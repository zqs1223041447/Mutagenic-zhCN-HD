#!/usr/bin/env python3
"""Apply a manifest-defined, preimage-guarded text patch to a fresh worktree."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    base = args.base.resolve()
    mod = json.loads(args.manifest.read_text(encoding="utf-8"))
    out = args.out.resolve()
    if out.exists():
        raise SystemExit(f"ERROR: refusing to overwrite generated worktree: {out}")

    # Group patches by target before writing anything.  A manifest may
    # legitimately contain several exact text fields in one resource file;
    # checking the whole-file preimage once avoids treating the first patch's
    # intentional change as a second patch's preimage failure.
    grouped: OrderedDict[str, list[dict]] = OrderedDict()
    for patch in mod.get("patches", []):
        rel = Path(patch["path"])
        if rel.is_absolute() or ".." in rel.parts:
            raise SystemExit(f"ERROR: unsafe patch path: {rel}")
        grouped.setdefault(rel.as_posix(), []).append(patch)

    preflight: OrderedDict[str, dict] = OrderedDict()
    for rel_text, path_patches in grouped.items():
        rel = Path(rel_text)
        target = base / rel
        if not target.is_file():
            raise SystemExit(f"ERROR: patch target missing: {rel}")
        before = target.read_bytes()
        before_sha = sha256_bytes(before)
        for patch in path_patches:
            if before_sha.lower() != patch["preimage_sha256"].lower():
                raise SystemExit(f"ERROR: preimage mismatch for {rel}: expected {patch['preimage_sha256']}, got {before_sha}")
            if patch.get("classification") == "ASSET_PATCH":
                source_rel = Path(patch["source_path"])
                if source_rel.is_absolute() or ".." in source_rel.parts:
                    raise SystemExit(f"ERROR: unsafe asset source path: {source_rel}")
                source = base / source_rel
                if not source.is_file():
                    raise SystemExit(f"ERROR: asset replacement source missing: {source_rel}")
                replacement = source.read_bytes()
                replacement_sha = sha256_bytes(replacement)
                expected_replacement = patch.get("replacement_sha256")
                if expected_replacement and replacement_sha.lower() != expected_replacement.lower():
                    raise SystemExit(f"ERROR: replacement hash mismatch for {source_rel}: expected {expected_replacement}, got {replacement_sha}")
                if "replacement_size" in patch and len(replacement) != patch["replacement_size"]:
                    raise SystemExit(f"ERROR: replacement size mismatch for {source_rel}: expected {patch['replacement_size']}, got {len(replacement)}")
            else:
                old = patch["old_text"].encode("utf-8")
                count = before.count(old)
                if count != patch.get("expected_occurrences", 1):
                    raise SystemExit(f"ERROR: occurrence mismatch for {rel}: expected {patch.get('expected_occurrences', 1)}, got {count}")
        preflight[rel_text] = {"before": before, "before_sha256": before_sha, "patches": path_patches}

    # All guards passed; only now create the disposable generated worktree.
    shutil.copytree(base, out)
    applied = []
    for rel_text, info in preflight.items():
        rel = Path(rel_text)
        target = out / rel
        working = info["before"]
        for patch in info["patches"]:
            if patch.get("classification") == "ASSET_PATCH":
                source_rel = Path(patch["source_path"])
                replacement = (base / source_rel).read_bytes()
                working = replacement
                applied.append({
                    "path": rel.as_posix(),
                    "preimage_sha256": info["before_sha256"],
                    "postimage_sha256": sha256_bytes(working),
                    "source_path": source_rel.as_posix(),
                    "replacement_size": len(replacement),
                    "classification": "ASSET_PATCH",
                })
                continue
            old = patch["old_text"].encode("utf-8")
            new = patch["new_text"].encode("utf-8")
            count = working.count(old)
            expected = patch.get("expected_occurrences", 1)
            if count != expected:
                raise SystemExit(f"ERROR: occurrence changed while applying grouped patches for {rel}: expected {expected}, got {count}")
            working = working.replace(old, new)
            applied.append({
                "path": rel.as_posix(),
                "preimage_sha256": info["before_sha256"],
                "postimage_sha256": sha256_bytes(working),
                "occurrences": count,
                "old_text": patch["old_text"],
                "new_text": patch["new_text"],
            })
        target.write_bytes(working)
    files = []
    for path in sorted(p for p in out.rglob("*") if p.is_file()):
        files.append({"relpath": path.relative_to(out).as_posix(), "size": path.stat().st_size, "sha256": sha256_bytes(path.read_bytes())})
    report = {
        "experiment_id": mod["id"],
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "base": str(base),
        "out": str(out),
        "mod_manifest": str(args.manifest.resolve()),
        "patches": applied,
        "changed_paths": [x["path"] for x in applied],
        "changed_path_count": len(applied),
        "file_count": len(files),
        "files": files,
        "verdict": "PASS" if len(applied) == len(mod.get("patches", [])) else "FAIL",
        "proves": "declared patches applied only after exact preimage and occurrence guards",
        "not_proven": "compiler success, runtime effect, packaging integrity",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("changed_paths", "changed_path_count", "file_count", "verdict")}, ensure_ascii=False))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
