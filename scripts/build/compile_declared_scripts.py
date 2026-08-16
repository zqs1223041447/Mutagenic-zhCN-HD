#!/usr/bin/env python3
"""Compile and encrypt only scripts declared by a Mod manifest.

Fast-path compile:
- deduplicates declared .gd paths (a manifest may reference the same file from
  many patches; each unique file is compiled exactly once),
- batches all files in the same directory into a single GDRE invocation
  (--compile is repeatable; output is flattened into the per-dir stage dir,
  so grouping by parent dir is collision-free),
- runs directory groups in parallel (GDRE instances are independent),
- optional --cache reuses the encrypted .gde for sources whose sha256 is
  unchanged, so an iteration that touches one file launches GDRE only for it.

Output layout is unchanged: out/<rel.parent>/<stem>.gde + out/<rel.name>.remap,
which is exactly what build_declared_pack.py consumes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GDRE = ROOT / "02_tools/gdre/gdre_tools.exe"
KEY_FILE = ROOT / "manifests/script_key.txt"
BYTECODE = "3.5.3.stable"

sys.path.insert(0, str(ROOT / "scripts"))
from compile_encrypt_scripts import make_gde, remap_text  # noqa: E402


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def compile_group(rel_files: list[Path], worktree: Path, stage: Path, gdre: Path) -> None:
    """Launch one GDRE process to compile all rel_files (same parent dir)
    into stage. Raises on failure with per-file attribution."""
    stage.mkdir(parents=True, exist_ok=True)
    cmd = [str(gdre), "--headless"]
    cmd += [f"--compile={worktree / rel}" for rel in rel_files]
    cmd += [f"--bytecode={BYTECODE}", f"--output={stage}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        missing = [rel.as_posix() for rel in rel_files if not (stage / f"{rel.stem}.gdc").is_file()]
        detail = result.stderr[-1500:] if result.stderr else result.stdout[-1500:]
        raise SystemExit(
            f"ERROR: compile failed (rc={result.returncode}) for: {missing or rel_files[0].as_posix()}\n{detail}"
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worktree", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=4, help="max parallel GDRE instances (default 4)")
    ap.add_argument("--cache", type=Path, default=None, help="persistent .gde cache dir; reuse unchanged sources")
    args = ap.parse_args()
    mod = json.loads(args.manifest.read_text(encoding="utf-8"))
    key = bytes.fromhex(KEY_FILE.read_text(encoding="utf-8").strip())
    out = args.out.resolve()
    if out.exists():
        raise SystemExit(f"ERROR: refusing to overwrite compiled directory: {out}")
    out.mkdir(parents=True)
    gdre = GDRE.resolve()

    # 1. Collect unique declared .gd paths, preserving declaration order.
    seen: set[str] = set()
    rel_files: list[Path] = []
    for patch in mod.get("patches", []):
        rel = Path(patch["path"])
        if rel.suffix != ".gd" or rel.as_posix() in seen:
            continue
        source = (args.worktree.resolve() / rel)
        if not source.is_file():
            raise SystemExit(f"ERROR: declared script missing: {rel}")
        seen.add(rel.as_posix())
        rel_files.append(rel)

    # 2. Group by parent dir -> one stage dir, one GDRE invocation, no collisions.
    groups: dict[str, list[Path]] = {}
    for rel in rel_files:
        groups.setdefault(rel.parent.as_posix(), []).append(rel)

    cache_root = (args.cache.resolve() / BYTECODE) if args.cache else None
    if cache_root:
        cache_root.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    cache_hits = 0
    compiled_count = 0
    invocations = 0
    failures: list[str] = []
    gdre_lock_holder = {"invocations": 0}  # plain dict as cheap cross-thread counter

    def run_group(parent: str, group: list[Path]) -> None:
        nonlocal cache_hits, compiled_count
        stage = out / parent
        stage.mkdir(parents=True, exist_ok=True)
        todo: list[Path] = []
        for rel in group:
            source = args.worktree.resolve() / rel
            src_hash = sha256_bytes(source.read_bytes())
            cached = (cache_root / f"{src_hash}.gde") if cache_root else None
            gde = stage / f"{rel.stem}.gde"
            if cached and cached.is_file():
                shutil.copy2(cached, gde)
                cache_hits += 1
            else:
                todo.append(rel)
        if todo:
            # Batch-compile only the files not satisfied from cache.
            gdre_lock_holder["invocations"] += 1
            compile_group(todo, args.worktree.resolve(), stage, gdre)
            compiled_count += len(todo)
            for rel in todo:
                source = args.worktree.resolve() / rel
                gdc = stage / f"{rel.stem}.gdc"
                if not gdc.is_file():
                    raise SystemExit(f"ERROR: compile produced no .gdc for {rel.as_posix()}")
                gde_bytes = make_gde(gdc.read_bytes(), key)
                gdc.unlink()
                (stage / f"{rel.stem}.gde").write_bytes(gde_bytes)
                if cache_root:
                    (cache_root / f"{sha256_bytes(source.read_bytes())}.gde").write_bytes(gde_bytes)

    if groups:
        workers = max(1, min(args.workers, len(groups)))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(run_group, parent, g): parent for parent, g in groups.items()}
            for fut in as_completed(futures):
                try:
                    fut.result()
                except SystemExit as e:
                    failures.append(str(e))
    invocations = gdre_lock_holder["invocations"]

    if failures:
        raise SystemExit("\n".join(failures[:5]))

    # 3. Build the report (same schema as before) from resolved order.
    for rel in rel_files:
        gde = out / rel.with_suffix(".gde")
        remap = out / f"{rel}.remap"
        if not gde.is_file():
            raise SystemExit(f"ERROR: missing gde for {rel.as_posix()}")
        remap.write_text(remap_text(rel), encoding="utf-8")
        rows.append({
            "source": rel.as_posix(),
            "gde": gde.relative_to(out).as_posix(),
            "remap": remap.relative_to(out).as_posix(),
            "gde_sha256": sha256_bytes(gde.read_bytes()),
            "remap_sha256": sha256_bytes(remap.read_bytes()),
        })

    declared_gd = [p["path"] for p in mod.get("patches", []) if Path(p["path"]).suffix == ".gd"]
    empty_ok = not declared_gd
    ok = bool(rows) or empty_ok
    report = {
        "mod": mod["id"], "worktree": str(args.worktree.resolve()), "output": str(out),
        "bytecode": BYTECODE, "compiled": rows, "count": len(rows),
        "declared_gd_entries": len(declared_gd), "unique_gd_paths": len(rel_files),
        "gdre_invocations": invocations, "cache_hits": cache_hits,
        "empty_ok": empty_ok, "verdict": "PASS" if ok else "FAIL",
        "proves": "each unique declared script path was compiled exactly once and encrypted; unchanged cached sources were reused",
        "not_proven": "runtime semantic effect or PCK/EXE structural validation",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "compiled": len(rows), "unique_gd": len(rel_files), "declared_gd_entries": len(declared_gd),
        "gdre_invocations": invocations, "cache_hits": cache_hits, "verdict": report["verdict"],
    }))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())