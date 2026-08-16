#!/usr/bin/env python3
"""Create a pack tree from 03_raw plus only declared resource/script deltas."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--worktree", type=Path, required=True)
    ap.add_argument("--compiled", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    mod = json.loads(args.manifest.read_text(encoding="utf-8"))
    out = args.out.resolve()
    if out.exists():
        raise SystemExit(f"ERROR: refusing to overwrite pack tree: {out}")
    shutil.copytree(args.base.resolve(), out)
    changed = []
    for patch in mod.get("patches", []):
        rel = Path(patch["path"])
        source = args.worktree.resolve() / rel
        if patch.get("classification") == "ASSET_PATCH":
            source = args.worktree.resolve() / Path(patch["source_path"])
            target = out / rel
            if not source.is_file() or not target.is_file():
                raise SystemExit(f"ERROR: missing declared asset path/source: {rel} <- {patch['source_path']}")
            shutil.copy2(source, target)
            changed.append(rel.as_posix())
            continue
        if rel.suffix == ".gd":
            source = args.compiled.resolve() / rel.with_suffix(".gde")
            remap_source = args.compiled.resolve() / f"{rel}.remap"
            gde_target = out / rel.with_suffix(".gde")
            remap_target = out / f"{rel}.remap"
            if not source.is_file() or not remap_source.is_file():
                raise SystemExit(f"ERROR: missing compiled pair for {rel}")
            shutil.copy2(source, gde_target)
            shutil.copy2(remap_source, remap_target)
            plain = out / rel
            if plain.exists():
                plain.unlink()
            changed += [rel.with_suffix(".gde").as_posix(), (Path(f"{rel}.remap")).as_posix()]
        else:
            target = out / rel
            if not source.is_file() or not target.is_file():
                raise SystemExit(f"ERROR: missing declared resource path: {rel}")
            shutil.copy2(source, target)
            changed.append(rel.as_posix())
    for overlay in mod.get("asset_overlays", []):
        rel = Path(overlay["path"])
        source_rel = Path(overlay["source_path"])
        if rel.is_absolute() or ".." in rel.parts:
            raise SystemExit(f"ERROR: unsafe declared asset target: {rel}")
        if source_rel.is_absolute() or ".." in source_rel.parts:
            raise SystemExit(f"ERROR: unsafe declared asset source: {source_rel}")
        target = out / rel
        source = ROOT / source_rel
        if not target.is_file():
            raise SystemExit(f"ERROR: declared asset target missing: {rel}")
        if not source.is_file():
            raise SystemExit(f"ERROR: declared asset source missing: {source_rel}")
        target_before = sha(target)
        if target_before.lower() != overlay["preimage_sha256"].lower():
            raise SystemExit(f"ERROR: asset preimage mismatch for {rel}: expected {overlay['preimage_sha256']}, got {target_before}")
        source_sha = sha(source)
        if source_sha.lower() != overlay["replacement_sha256"].lower():
            raise SystemExit(f"ERROR: asset replacement hash mismatch for {source_rel}: expected {overlay['replacement_sha256']}, got {source_sha}")
        if "replacement_size" in overlay and source.stat().st_size != overlay["replacement_size"]:
            raise SystemExit(f"ERROR: asset replacement size mismatch for {source_rel}: expected {overlay['replacement_size']}, got {source.stat().st_size}")
        shutil.copy2(source, target)
        changed.append(rel.as_posix())
    files = sorted(p for p in out.rglob("*") if p.is_file())
    report = {"mod": mod["id"], "base": str(args.base.resolve()), "worktree": str(args.worktree.resolve()), "compiled": str(args.compiled.resolve()), "out": str(out), "count": len(files), "changed_paths": changed, "changed_path_count": len(changed), "files": [{"relpath": p.relative_to(out).as_posix(), "size": p.stat().st_size, "sha256": sha(p)} for p in files], "verdict": "PASS", "proves": "pack tree is copied from 03_raw and receives only manifest-declared overlays", "not_proven": "PCK/EXE structural validation or runtime behavior"}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"count": len(files), "changed_paths": changed, "verdict": "PASS"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
