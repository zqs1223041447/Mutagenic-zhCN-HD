#!/usr/bin/env python3
"""Export private devkit for portable fresh-clone bootstrap.

Reads local private assets (00_original/Mutagenic.exe, manifests/script_key.txt,
02_tools/gdre/*) and packs them into an output directory (default .private_devkit/
or repo-outside) with manifest.json containing sha256, schema_version, created_at.

⚠️  PRIVATE / NOT FOR GIT — output directory is never auto git-added and must be
    covered by .gitignore (.private_devkit/, .devkit/, *.devkit.zip). Do NOT run
    `git add` on it. Content is copyright/secret; keep local only.

Usage:
  python scripts/bootstrap/export_private_devkit.py --out <dir>
  python scripts/bootstrap/export_private_devkit.py  # defaults to <repo_root>/.private_devkit
Env providers consumed on import side (bootstrap):
  MUTAGENIC_DEVKIT_ROOT, MUTAGENIC_ORIGINAL_EXE, MUTAGENIC_SCRIPT_KEY_FILE, MUTAGENIC_TOOL_ROOT

Never runs `git add`; output directory must be covered by .gitignore.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "env"))
from dev_environment import find_repo_root  # type: ignore

SCHEMA_VERSION = "1.0"
ORIGINAL_SHA = "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209"
ORIGINAL_SIZE = 103290320


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_ignored(repo_root: Path, out: Path) -> bool:
    """Check if out is gitignored (via git check-ignore). If git unavailable, fallback to name check."""
    try:
        r = subprocess.run(["git", "check-ignore", "-q", str(out)], cwd=str(repo_root), capture_output=True)
        return r.returncode == 0
    except OSError:
        pass
    rel = ""
    try:
        rel = out.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return True
    ignored_prefixes = (".private_devkit", ".devkit", ".cache")
    return any(rel.startswith(p) for p in ignored_prefixes) or rel.endswith(".devkit.zip")


def _get_host() -> str:
    try:
        return platform.node() or os.environ.get("COMPUTERNAME", "") or os.environ.get("HOSTNAME", "") or "unknown"
    except Exception:
        return "unknown"


def _get_repo_commit(repo_root: Path) -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo_root), capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode == 0:
            return r.stdout.strip()
    except OSError:
        pass
    return "unknown"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Export private devkit (PRIVATE / NOT FOR GIT — never git add).")
    ap.add_argument("--out", dest="out", type=str, default=None,
                    help="output directory (default <repo_root>/.private_devkit). Can be repo-outside; .private_devkit already gitignored.")
    ap.add_argument("--zip", action="store_true", help="also create .zip alongside dir (still gitignored via *.devkit.zip)")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    try:
        repo_root = find_repo_root()
    except Exception as e:
        print(f"[export] FAIL: {e}", file=sys.stderr)
        return 1

    out = Path(args.out) if args.out else (repo_root / ".private_devkit")
    if not out.is_absolute():
        out = (Path.cwd() / out).resolve()
    out = out.resolve()

    if out == repo_root.resolve():
        print(f"[export] FAIL: out cannot be repo_root itself: {out}", file=sys.stderr)
        return 1

    try:
        inside = out.is_relative_to(repo_root.resolve())  # py 3.9+
    except AttributeError:
        try:
            out.relative_to(repo_root.resolve())
            inside = True
        except ValueError:
            inside = False

    if inside and not is_ignored(repo_root, out):
        print(f"[export] WARN: output {out} may not be gitignored. Ensure .gitignore covers .private_devkit/ / .devkit/ / *.devkit.zip", file=sys.stderr)
        print(f"[export] WARN: PRIVATE / NOT FOR GIT — do not `git add` this directory", file=sys.stderr)

    # Collect sources
    exe = repo_root / "00_original/Mutagenic.exe"
    key = repo_root / "manifests/script_key.txt"
    gdre = repo_root / "02_tools/gdre/gdre_tools.exe"
    gdre_dir = repo_root / "02_tools/gdre"

    if not exe.is_file():
        print(f"[export] FAIL: missing {exe} - cannot export without owned exe", file=sys.stderr)
        print(f"  env hint: set MUTAGENIC_ORIGINAL_EXE=<path> or MUTAGENIC_DEVKIT_ROOT=<devkit> containing 00_original/Mutagenic.exe", file=sys.stderr)
        print(f"  expected SHA {ORIGINAL_SHA} size {ORIGINAL_SIZE}", file=sys.stderr)
        return 1
    if not key.is_file():
        print(f"[export] FAIL: missing {key} - cannot export without script_key", file=sys.stderr)
        print(f"  env hint: set MUTAGENIC_SCRIPT_KEY=64hex or MUTAGENIC_SCRIPT_KEY_FILE=<path> or MUTAGENIC_DEVKIT_ROOT=<devkit>/manifests/script_key.txt", file=sys.stderr)
        return 1

    exp_sha = ORIGINAL_SHA
    sz = exe.stat().st_size
    sha = sha256_file(exe).upper()
    if sha != exp_sha or sz != ORIGINAL_SIZE:
        print(f"[export] FAIL: exe sha/size mismatch sha={sha} size={sz} expected {exp_sha}/{ORIGINAL_SIZE}", file=sys.stderr)
        return 1

    txt = key.read_text(encoding="utf-8").strip()
    if len(txt) != 64 or any(c not in "0123456789abcdefABCDEF" for c in txt):
        print(f"[export] FAIL: key at {key} not 64 hex", file=sys.stderr)
        return 1

    out.mkdir(parents=True, exist_ok=True)

    manifest_entries = []
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    host = _get_host()
    repo_commit = _get_repo_commit(repo_root)

    # Copy exe
    dest_exe = out / "00_original" / "Mutagenic.exe"
    dest_exe.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(exe, dest_exe)
    manifest_entries.append({
        "id": "original_exe",
        "path": "00_original/Mutagenic.exe",
        "sha256": sha,
        "size": sz,
    })
    if args.verbose:
        print(f"[export] copied {exe} -> {dest_exe}")

    # Copy key
    dest_key = out / "manifests" / "script_key.txt"
    dest_key.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(key, dest_key)
    key_sha = sha256_file(dest_key)
    manifest_entries.append({
        "id": "script_key",
        "path": "manifests/script_key.txt",
        "sha256": key_sha,
        "size": dest_key.stat().st_size,
    })
    if args.verbose:
        print(f"[export] copied {key} -> {dest_key} (fingerprint {key_sha[:8]}...)")

    # Copy GDRE tools dir if present
    if gdre.is_file():
        dest_gdre_dir = out / "02_tools" / "gdre"
        dest_gdre_dir.mkdir(parents=True, exist_ok=True)
        for p in gdre_dir.rglob("*"):
            if p.is_file():
                rel = p.relative_to(gdre_dir)
                d = dest_gdre_dir / rel
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, d)
                manifest_entries.append({
                    "id": "gdre_tool",
                    "path": f"02_tools/gdre/{rel.as_posix()}",
                    "sha256": sha256_file(d).lower(),
                    "size": d.stat().st_size,
                })
        if args.verbose:
            print(f"[export] copied gdre dir {gdre_dir} -> {dest_gdre_dir}")
    else:
        if args.verbose:
            print(f"[export] gdre not found at {gdre}, skipping (set MUTAGENIC_TOOL_ROOT or download GDRE 2.6.4)")

    # Also copy tools.lock.json for reference (not secret)
    tl = repo_root / "tools.lock.json"
    if tl.is_file():
        dest_tl = out / "tools.lock.json"
        shutil.copy2(tl, dest_tl)
        manifest_entries.append({
            "id": "tools_lock",
            "path": "tools.lock.json",
            "sha256": sha256_file(dest_tl),
            "size": dest_tl.stat().st_size,
        })

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "created_at": created_at,
        "host": host,
        "repo_commit": repo_commit,
        "repo_root_hint": "<repo_root>",
        "exported_from": str(repo_root),
        "assets": manifest_entries,
        "usage": "Set MUTAGENIC_DEVKIT_ROOT to this directory and run python scripts/bootstrap/bootstrap_dev_env.py",
        "gitignored": True,
        "warning": "PRIVATE / NOT FOR GIT — Never git add this directory; it contains private copyright/secret assets.",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[export] PRIVATE devkit exported to {out}")
    print(f"[export] manifest: {out / 'manifest.json'} (schema {SCHEMA_VERSION})")
    print(f"[export] assets: {len(manifest_entries)} files — host={host} commit={repo_commit[:8]}")
    print(f"[export] ⚠️  PRIVATE / NOT FOR GIT — never `git add` this directory")
    print(f"[export] To use on fresh clone: set MUTAGENIC_DEVKIT_ROOT={out} then python scripts/bootstrap/bootstrap_dev_env.py")
    if args.verbose:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))

    if args.zip:
        # ensure zip name matches *.devkit.zip ignore pattern
        if out.suffix == ".devkit":
            base = str(out)  # e.g. Foo.devkit -> Foo.devkit.zip
            zip_base = base
        else:
            zip_base = str(out.parent / (out.name + ".devkit"))
        # shutil.make_archive expects base without extension
        # Remove possible .zip suffix already
        if zip_base.endswith(".zip"):
            zip_base = zip_base[:-4]
        # make archive
        created = shutil.make_archive(zip_base, "zip", root_dir=str(out.parent), base_dir=out.name)
        print(f"[export] zip archive: {created} (gitignored via *.devkit.zip)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
