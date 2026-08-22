#!/usr/bin/env python3
"""Download Godot 4.7.1 stable into repo-relative 02_tools/godot/.

URLs are official GitHub godot-builds releases. Destination is always
repo-relative. Never embeds a host drive letter.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path
from typing import Callable
from urllib.request import Request, urlopen

WANTED = "4.7.1"
RELEASE_TAG = "4.7.1-stable"
BASE = f"https://github.com/godotengine/godot-builds/releases/download/{RELEASE_TAG}"
ASSETS = {
    "windows": "Godot_v4.7.1-stable_win64.exe.zip",
    "linux": "Godot_v4.7.1-stable_linux.x86_64.zip",
}
REL_DEST = "02_tools/godot"


def asset_for_platform(platform: str | None = None) -> tuple[str, str]:
    plat = (platform or sys.platform).lower()
    if plat.startswith("win"):
        key = "windows"
    elif plat.startswith("linux"):
        key = "linux"
    else:
        raise ValueError(f"unsupported platform {plat}; Godot fetch supports windows/linux")
    name = ASSETS[key]
    return key, f"{BASE}/{name}"


def official_url(platform: str | None = None) -> str:
    return asset_for_platform(platform)[1]


def dest_dir(repo_root: Path) -> Path:
    return Path(repo_root) / REL_DEST


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_zip(payload: bytes, dest: Path) -> list[str]:
    dest.mkdir(parents=True, exist_ok=True)
    names: list[str] = []
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            target = dest / Path(info.filename).name
            target.write_bytes(zf.read(info))
            names.append(target.name)
            if sys.platform.startswith("linux") and not target.name.endswith(".zip"):
                target.chmod(target.stat().st_mode | 0o111)
    return names


Downloader = Callable[[str], bytes]


def _default_download(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "mutagenic-fetch-godot/1.0"})
    with urlopen(req, timeout=120) as resp:  # nosec B310 - official Godot HTTPS
        return resp.read()


def fetch_godot(
    repo_root: Path,
    *,
    platform: str | None = None,
    download: Downloader | None = None,
) -> dict:
    key, url = asset_for_platform(platform)
    if WANTED not in url or RELEASE_TAG not in url:
        raise ValueError("refusing to fetch a URL that is not Godot 4.7.1-stable")
    dest = dest_dir(repo_root)
    payload = (download or _default_download)(url)
    names = extract_zip(payload, dest)
    (dest / "VERSION.txt").write_text(f"{WANTED}\n{url}\n", encoding="utf-8")
    return {
        "status": "FETCHED",
        "wanted": WANTED,
        "platform": key,
        "url": url,
        "dest": REL_DEST,
        "files": names,
        "bytes": len(payload),
        "sha256": sha256_bytes(payload),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--platform", default=None)
    ap.add_argument("--print-url", action="store_true")
    args = ap.parse_args(argv)
    root = (args.root or Path(__file__).resolve().parents[2]).resolve()
    if args.print_url:
        print(official_url(args.platform))
        return 0
    result = fetch_godot(root, platform=args.platform)
    print(json.dumps({k: result[k] for k in ("status", "wanted", "platform", "url", "dest", "files", "bytes")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
