#!/usr/bin/env python3
"""Build 08_pack from 03_raw with controlled overlays from 06_worktree.

Rules:
  - 08_pack starts as a full copy of 03_raw (canonical derived tree).
  - Overlay from 06_worktree:
      *.gd        -> replaces encrypted .gde (deletes .gde and .gd.remap)
      *.tscn,*.tres,*.json -> overwrite in place
  - Never overlays addons/ or .autoconverted/ (editor-only artifacts).
  - project.binary kept as-is from 03_raw.
Outputs 08_pack/ with manifest manifests/pack_manifest.json.

Usage:
    python scripts/build_pack.py [--base 03_raw] [--overlay 06_worktree] [--dst 08_pack]
"""

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

OVERLAY_EXTS = {".gd", ".tscn", ".tres", ".json"}
SKIP_DIRS = {"addons", ".autoconverted"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, default=Path("03_raw"))
    ap.add_argument("--overlay", type=Path, default=Path("06_worktree"))
    ap.add_argument("--scripts", type=Path, default=Path("07_compiled"),
                    help="compiled+encrypted scripts (.gde + .gd.remap)")
    ap.add_argument("--plain-scripts", action="store_true",
                    help="ship unencrypted .gd instead of .gde (debug only)")
    ap.add_argument("--dst", type=Path, default=Path("08_pack"))
    args = ap.parse_args()

    base, overlay, dst = args.base, args.overlay, args.dst
    scripts = args.scripts
    if dst.exists():
        print(f"ERROR: {dst} exists; refusing to clobber")
        return 1
    if not args.plain_scripts:
        if not scripts.exists():
            print(f"ERROR: {scripts} not found. Run "
                  f"scripts/compile_encrypt_scripts.py first, or pass "
                  f"--plain-scripts.")
            return 1
        print(f"script mode: ENCRYPTED (.gde from {scripts})")
    else:
        print("script mode: PLAIN .gd (debug)")

    # 1. copy base
    base_files = [p for p in base.rglob("*") if p.is_file()]
    dst.mkdir(parents=True)
    for p in base_files:
        out = dst / p.relative_to(base)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, out)
    print(f"copied base: {len(base_files)} files")

    # 2. overlay
    overlaid = []
    deleted = []
    missing_scripts = []
    plain_kept = []
    for p in overlay.rglob("*"):
        if not p.is_file():
            continue
        if any(sk in p.parts for sk in SKIP_DIRS):
            continue
        rel = p.relative_to(overlay)
        ext = p.suffix.lower()
        target = dst / rel
        if ext == ".gd":
            if args.plain_scripts:
                # Debug path: ship unencrypted source, drop the encrypted pair.
                gde = dst / rel.with_suffix(".gde")
                remap = dst / rel.with_suffix(".gd.remap")
                if gde.exists():
                    gde.unlink()
                    deleted.append(str(rel.with_suffix(".gde")).replace("\\", "/"))
                if remap.exists():
                    remap.unlink()
                    deleted.append(str(rel.with_suffix(".gd.remap")).replace("\\", "/"))
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, target)
                overlaid.append(str(rel).replace("\\", "/"))
                continue

            # Preserve the original shipping form per script.  A handful of
            # scripts shipped as plain .gd in the original PCK (no .gde, no
            # remap); re-encrypting those would add files the original never
            # had.  Keep them plain so the pack layout stays 1:1 with 03_raw.
            base_had_gde = (base / rel.with_suffix(".gde")).exists()
            if not base_had_gde:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, target)
                overlaid.append(str(rel).replace("\\", "/"))
                plain_kept.append(str(rel).replace("\\", "/"))
                continue

            # Default path: ship the compiled+encrypted form, matching the
            # original PCK layout (.gde + .gd.remap, no plain .gd).
            src_gde = scripts / rel.with_suffix(".gde")
            src_remap = scripts / f"{rel}.remap"
            if not src_gde.exists() or not src_remap.exists():
                missing_scripts.append(str(rel).replace("\\", "/"))
                continue
            dst_gde = dst / rel.with_suffix(".gde")
            dst_remap = dst / rel.with_suffix(".gd.remap")
            dst_gde.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_gde, dst_gde)
            shutil.copy2(src_remap, dst_remap)
            # A plain .gd must NOT coexist with the remap; base may have one.
            if target.exists():
                target.unlink()
                deleted.append(str(rel).replace("\\", "/"))
            overlaid.append(str(rel.with_suffix(".gde")).replace("\\", "/"))
        elif ext in OVERLAY_EXTS:
            if not target.exists():
                continue  # only overwrite files that exist in base
            shutil.copy2(p, target)
            overlaid.append(str(rel).replace("\\", "/"))

    # 2b. every overlaid .gd must have a compiled counterpart -- FAIL CLOSED.
    if missing_scripts:
        print(f"ERROR: {len(missing_scripts)} scripts have no .gde/.gd.remap in "
              f"{scripts} (FAIL CLOSED). Re-run compile_encrypt_scripts.py.")
        for m in missing_scripts[:20]:
            print(f"  - {m}")
        return 1

    # 3. integrity check on remaining encrypted scripts -- FAIL CLOSED.
    #
    # Scripts NOT overlaid from 06_worktree keep their original encrypted form
    # (.gde) plus the .gd.remap that points at it.  That pair is self-consistent
    # and is what the original PCK shipped, so it is PRESERVED.
    #
    # A previous version of this script deleted every leftover .gde/.remap
    # unconditionally.  That silently dropped the addons/ scripts entirely
    # (skipped by the overlay -> no .gd, and .gde deleted -> script gone),
    # shrinking the pack from 3744 to 3206 files.  Any such inconsistency is
    # now a hard error instead of a silent drop.
    kept_gde = sorted(p.relative_to(dst) for p in dst.rglob("*.gde"))
    problems = []
    for gde_rel in kept_gde:
        remap = dst / gde_rel.with_suffix(".gd.remap")
        if not remap.exists():
            problems.append(f"orphan .gde without .gd.remap: {gde_rel}")
    for remap_p in dst.rglob("*.gd.remap"):
        remap_rel = remap_p.relative_to(dst)
        # "Foo.gd.remap" -> "Foo.gde"
        gde = dst / remap_rel.with_suffix("").with_suffix(".gde")
        if not gde.exists():
            problems.append(f"remap target missing: {remap_rel} -> {gde.name}")
    if problems:
        print(f"ERROR: {len(problems)} script-path inconsistencies (FAIL CLOSED):")
        for pr in problems[:20]:
            print(f"  - {pr}")
        return 1
    print(f"preserved encrypted scripts: {len(kept_gde)} .gde (+ matching .remap)")
    if plain_kept:
        print(f"kept plain (original shipped no .gde): {len(plain_kept)}")
        for pk in plain_kept[:5]:
            print(f"  - {pk}")

    # 4. manifest
    final_files = [p for p in dst.rglob("*") if p.is_file()]
    manifest = []
    for p in final_files:
        rel = str(p.relative_to(dst)).replace("\\", "/")
        manifest.append({
            "relpath": rel,
            "size": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        })

    mfile = Path("manifests/pack_manifest.json")
    mfile.parent.mkdir(exist_ok=True)
    mfile.write_text(json.dumps({
        "base": str(base), "overlay": str(overlay),
        "count": len(manifest),
        "overlaid": overlaid, "deleted": deleted, "files": manifest,
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"overlaid: {len(overlaid)} deleted: {len(deleted)} final: {len(manifest)}")
    print(f"manifest: {mfile}")
    return 0


if __name__ == "__main__":
    sys.exit(main())