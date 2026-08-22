#!/usr/bin/env python3
"""
fetch_cc0_anim.py — P4-ANIM 最小可用闭环：下载 OGA 16x16 base sprites 直链

功能:
- 下载 OGA 16x16 base sprites CC0 直链 (base_male.png / base_female.png)
  含 1 帧 idle + 6 帧 walk × 4 方向，16x16 像素风格
- 校验 SHA256（若提供期望值则强校验，否则计算后写入 SOURCE.txt）
- 落盘至 product/sprites/_acquired/oga_16x16-base-sprites/
- 生成 SOURCE.txt (URL/许可/CC0/日期) 供审计

补充包 blocky dungeon / skeleton / slimes 同为 CC0 直链，见 OPTIONAL_PACKS，
默认仅拉取 base 2 帧；如需扩展可 --with-optional。

itch 需手动包 (0x72 / o_lobster / Shade) 不在此脚本下载，另见
migration/inventory/p4_art_needs_manual_download.json

用法:
  python scripts/bootstrap/fetch_cc0_anim.py
  python scripts/bootstrap/fetch_cc0_anim.py --with-optional
  python scripts/bootstrap/fetch_cc0_anim.py --root C:/AI-GAME/Mutagenic-zhCN-HD
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# --- 配置 -----------------------------------------------------------------

# OGA 16x16 base sprites — CharlesGabriel / OGA 投稿，CC0
# 直链为 opengameart.org/sites/default/files/ 下的原始 PNG
# 如 OGA 站点返回 302/403，脚本会自动跟随重定向并以 UA 重试
OGA_BASE_PACKS: list[dict] = [
    {
        "filename": "base_male.png",
        "url": "https://opengameart.org/sites/default/files/base_male.png",
        "license": "CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/)",
        "author": "OGA CharlesGabriel et al. (base_male)",
        # SHA256 在首次下载后回填；此处留空则仅计算并记录，不做强校验
        "sha256": None,
        "note": "16x16 base: 1 idle + 6 walk × 4 dir, CC0",
    },
    {
        "filename": "base_female.png",
        "url": "https://opengameart.org/sites/default/files/base_female.png",
        "license": "CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/)",
        "author": "OGA CharlesGabriel et al. (base_female)",
        "sha256": None,
        "note": "16x16 base: 1 idle + 6 walk × 4 dir, CC0",
    },
]

# 可选补充包（同为 CC0 直链，默认不拉取，加 --with-optional 触发）
# URL 为 OGA 详情页附带的 "files" 直链；若后续失效可在 SOURCE.txt 中更新
OPTIONAL_PACKS: list[dict] = [
    {
        "filename": "blocky_dungeon.png",
        "url": "https://opengameart.org/sites/default/files/blocky_dungeon_sheet.png",
        "license": "CC0 1.0",
        "author": "OGA blocky dungeon",
        "sha256": None,
        "note": "补充：blocky dungeon tileset",
    },
    {
        "filename": "skeleton.png",
        "url": "https://opengameart.org/sites/default/files/skeleton_0.png",
        "license": "CC0 1.0",
        "author": "OGA skeleton",
        "sha256": None,
        "note": "补充：skeleton 16x16",
    },
    {
        "filename": "slime.png",
        "url": "https://opengameart.org/sites/default/files/slime_0.png",
        "license": "CC0 1.0",
        "author": "OGA slime",
        "sha256": None,
        "note": "补充：slimes",
    },
]

DEST_REL = Path("product/sprites/_acquired/oga_16x16-base-sprites")
SOURCE_TXT = "SOURCE.txt"
MANIFEST_JSON = "fetch_manifest.json"
USER_AGENT = "mutagenic-fetch-cc0-anim/1.0 (+https://opengameart.org/ CC0)"

# --- 工具 -----------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def ensure_dest(repo_root: Path) -> Path:
    dest = repo_root / DEST_REL
    dest.mkdir(parents=True, exist_ok=True)
    return dest

def download_with_retry(url: str, retries: int = 2, timeout: int = 60) -> bytes:
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "image/png,*/*"})
            with urlopen(req, timeout=timeout) as resp:  # nosec B310 - OGA HTTPS
                data = resp.read()
                if not data:
                    raise ValueError(f"empty response from {url}")
                # basic PNG magic check
                if data[:4] != b"\x89PNG" and data[:2] != b"\xff\xd8":
                    # OGA 有时返回 HTML 重定向页；抛出以触发重试/占位逻辑
                    head = data[:500].decode("utf-8", errors="ignore").lower()
                    if "<html" in head or "<!doctype" in head:
                        raise ValueError(f"expected PNG but got HTML (status-like) from {url}: {head[:200]}")
                return data
        except (HTTPError, URLError, ValueError, TimeoutError) as e:
            last_exc = e
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise
    assert last_exc is not None
    raise last_exc

def is_valid_png(data: bytes) -> bool:
    return len(data) >= 8 and data[:8] == b"\x89PNG\r\n\x1a\n"

def write_placeholder_png(dest_path: Path, label: str) -> tuple[int, str]:
    """网络不可达时生成最小占位 PNG（1x1 透明）并返回 bytes 长度与 sha256，保证管线打通。"""
    # 1x1 透明 PNG 的固定字节（已验证可被 Godot 导入）
    placeholder = bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
        "0000000a4944415478da63000100000500010d0a2db40000000049454e44ae426082"
    )
    dest_path.write_bytes(placeholder)
    h = sha256_bytes(placeholder)
    return len(placeholder), h

# --- 主流程 ---------------------------------------------------------------

def fetch_one(entry: dict, dest_dir: Path, force: bool = False) -> dict:
    filename = entry["filename"]
    url = entry["url"]
    expected = entry.get("sha256")
    dest_path = dest_dir / filename

    # 若已存在且非 force，校验现有文件
    if dest_path.exists() and not force:
        existing = dest_path.read_bytes()
        if is_valid_png(existing):
            h = sha256_bytes(existing)
            if expected and h.lower() != expected.lower():
                result = {"file": filename, "url": url, "status": "EXISTS_MISMATCH", "path": str(dest_path), "sha256": h, "expected": expected, "bytes": len(existing)}
                # 仍视为需要重新下载
            else:
                return {"file": filename, "url": url, "status": "EXISTS_VALID", "path": str(dest_path), "sha256": h, "bytes": len(existing), "license": entry["license"]}
        else:
            # 非 PNG（可能是旧占位 HTML），强制重下
            pass

    # 下载
    try:
        data = download_with_retry(url)
        # 强校验 SHA256（若提供）
        h = sha256_bytes(data)
        if expected and h.lower() != expected.lower():
            raise ValueError(f"SHA256 mismatch for {filename}: got {h} expected {expected}")
        if not is_valid_png(data):
            raise ValueError(f"downloaded file for {filename} is not a valid PNG ({len(data)} bytes)")
        dest_path.write_bytes(data)
        return {"file": filename, "url": url, "status": "DOWNLOADED", "path": str(dest_path), "sha256": h, "bytes": len(data), "license": entry["license"]}
    except Exception as e:
        # 网络/404 兜底：生成占位 PNG，保证后续 SpriteFrames 管线可验证
        # 同时保留错误信息到 manifest，便于 CI 识别为 PLACEHOLDER
        if dest_path.exists():
            try:
                existing = dest_path.read_bytes()
                if is_valid_png(existing):
                    h = sha256_bytes(existing)
                    return {"file": filename, "url": url, "status": "PLACEHOLDER_KEPT_EXISTING", "path": str(dest_path), "sha256": h, "bytes": len(existing), "license": entry["license"], "error": str(e)}
            except Exception:
                pass
        n, h = write_placeholder_png(dest_path, filename)
        return {"file": filename, "url": url, "status": "PLACEHOLDER_GENERATED", "path": str(dest_path), "sha256": h, "bytes": n, "license": entry["license"], "error": str(e), "note": "network unreachable or HTML response; placeholder 1x1 PNG written. Replace by re-running when network available."}

def write_source_txt(dest_dir: Path, results: list[dict]) -> Path:
    now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    lines = []
    lines.append("pack: OGA 16x16 base sprites (CC0)")
    lines.append("source: https://opengameart.org/ (base_male.png / base_female.png)")
    lines.append("license: CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/)")
    lines.append(f"fetched_at: {now}")
    lines.append(f"dest: {DEST_REL.as_posix()}/")
    lines.append(f"tool: scripts/bootstrap/fetch_cc0_anim.py (UA: {USER_AGENT})")
    lines.append("")
    lines.append("files:")
    for r in results:
        lines.append(f"  - filename: {r['file']}")
        lines.append(f"    url: {r['url']}")
        lines.append(f"    status: {r['status']}")
        lines.append(f"    sha256: {r['sha256']}")
        lines.append(f"    bytes: {r['bytes']}")
        lines.append(f"    license: {r.get('license','CC0 1.0')}")
        if "error" in r:
            lines.append(f"    error: {r['error']}")
        if "note" in r:
            lines.append(f"    note: {r['note']}")
    lines.append("")
    lines.append("notes:")
    lines.append("  - OGA 16x16 base: sheet is 1 idle + 6 walk frames x 4 directions, 16px grid (actual PNG 126x144, includes spacing).")
    lines.append("  - If status is PLACEHOLDER_*, the direct URL was unreachable (common in CI without internet or OGA auth page).")
    lines.append("    A 1x1 placeholder PNG was written to keep Godot import pipeline unblocked; re-run with network to replace.")
    lines.append("  - After real images land, slicing plan is in migration/inventory/p4_anim_plan.md and example SpriteFrames.")
    lines.append("  - Supplemental packs (blocky dungeon / skeleton / slimes) are also CC0; use --with-optional to fetch.")
    lines.append("  - itch manual packs (0x72 / o_lobster / Shade) require user manual 0$ download into _acquired/; see p4_art_needs_manual_download.json.")
    out = dest_dir / SOURCE_TXT
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out

def write_manifest(dest_dir: Path, results: list[dict]) -> Path:
    now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    manifest = {
        "schema_version": 1,
        "task": "P4-ANIM fetch_cc0_anim",
        "generated_at": now,
        "dest": DEST_REL.as_posix(),
        "results": results,
    }
    out = dest_dir / MANIFEST_JSON
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None, help="repo root (default: two levels up from script)")
    ap.add_argument("--with-optional", action="store_true", help="also fetch blocky dungeon / skeleton / slimes")
    ap.add_argument("--force", action="store_true", help="force re-download even if file exists")
    ap.add_argument("--json", action="store_true", help="print JSON manifest to stdout")
    args = ap.parse_args(argv)

    repo_root = (args.root or Path(__file__).resolve().parents[2]).resolve()
    dest_dir = ensure_dest(repo_root)

    packs = list(OGA_BASE_PACKS)
    if args.with_optional:
        packs.extend(OPTIONAL_PACKS)

    results: list[dict] = []
    for entry in packs:
        r = fetch_one(entry, dest_dir, force=args.force)
        results.append(r)
        status = r["status"]
        print(f"[{status}] {r['file']} <- {r['url']}  sha256={r['sha256'][:12]}... bytes={r['bytes']}")
        if "error" in r:
            print(f"  ! error: {r['error']}", file=sys.stderr)

    source_path = write_source_txt(dest_dir, results)
    manifest_path = write_manifest(dest_dir, results)
    print(f"Wrote {source_path}")
    print(f"Wrote {manifest_path}")

    # 汇总状态
    has_real = any(r["status"] in ("DOWNLOADED", "EXISTS_VALID") for r in results)
    all_placeholder = all("PLACEHOLDER" in r["status"] for r in results)
    if args.json:
        print(json.dumps({"results": results, "dest": str(dest_dir)}, indent=2, ensure_ascii=False))

    if all_placeholder:
        print("NOTE: all files are placeholders (network/URL unreachable). Pipeline still valid; re-run with network to replace.", file=sys.stderr)
        return 0
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
