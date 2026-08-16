#!/usr/bin/env python3
"""Copy 04_recovered -> 06_worktree (canonical work tree), logging the overlay.

Usage:
    python scripts/setup_worktree.py [--src 04_recovered] [--dst 06_worktree]
"""

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, default=Path("04_recovered"))
    ap.add_argument("--dst", type=Path, default=Path("06_worktree"))
    ap.add_argument("--manifest", type=Path, default=Path("manifests/worktree_manifest.json"))
    ap.add_argument("--manifest-only", action="store_true")
    args = ap.parse_args()

    src, dst = args.src, args.dst
    if args.manifest_only:
        if not dst.is_dir():
            print(f"ERROR: {dst} does not exist for manifest-only mode")
            return 1
        files = [p for p in dst.rglob("*") if p.is_file()]
        manifest = []
        for p in files:
            rel = p.relative_to(dst)
            manifest.append({
                "relpath": str(rel).replace("\\", "/"),
                "size": p.stat().st_size,
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            })
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps({"source": str(src), "count": len(manifest),
                                             "files": manifest}, indent=1, ensure_ascii=False),
                                 encoding="utf-8")
        print(f"manifest: {len(manifest)} files recorded from {dst}")
        print(f"manifest: {args.manifest}")
        return 0
    if dst.exists():
        print(f"ERROR: {dst} already exists; refusing to clobber")
        return 1

    files = [p for p in src.rglob("*") if p.is_file()]
    dst.mkdir(parents=True)
    manifest = []
    for p in files:
        rel = p.relative_to(src)
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, out)
        manifest.append({
            "relpath": str(rel).replace("\\", "/"),
            "size": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        })

    mfile = args.manifest
    mfile.parent.mkdir(exist_ok=True)
    mfile.write_text(json.dumps({"source": str(src), "count": len(manifest),
                                 "files": manifest}, indent=1, ensure_ascii=False),
                     encoding="utf-8")
    print(f"worktree: {len(manifest)} files copied to {dst}")
    print(f"manifest: {mfile}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
