#!/usr/bin/env python3
"""Portable dev environment helpers - single source of truth for path/env resolution.

All repo-internal paths are derived from repo_root; no hard-coded drive/user/UNC.
External assets are injected via MUTAGENIC_* env vars (see dev_environment_requirements.json).

Provides: find_repo_root(), load_requirements(), resolve_asset(), get_readiness_level(), check_portability()
Intended for reuse by bootstrap/doctor/pipeline.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_MARKER = "AGENTS.md"
REQUIREMENTS_REL = Path("manifests/dev_environment_requirements.json")


def find_repo_root(start: Path | str | None = None) -> Path:
    """Resolve repo root: git rev-parse --show-toplevel first, fallback to marker walk."""
    start_path = Path(start) if start is not None else Path.cwd()
    # git preferred (works from any subdir and inside worktree)
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(start_path),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if r.returncode == 0:
            out = r.stdout.strip()
            if out:
                p = Path(out).resolve()
                if p.is_dir():
                    return p
    except OSError:
        pass
    # fallback: walk parents looking for AGENTS.md
    cur = Path(__file__).resolve()
    # also walk from start_path
    for base in (cur, start_path.resolve()):
        c = base if base.is_dir() else base.parent
        while True:
            if (c / REPO_MARKER).is_file():
                return c
            if c.parent == c:
                break
            c = c.parent
    raise RuntimeError(f"not inside Mutagenic repo clone (no git toplevel or {REPO_MARKER}): {start_path}")


def get_repo_root() -> Path:
    return find_repo_root()


def load_requirements(repo_root: Path | None = None) -> dict:
    root = repo_root or find_repo_root()
    p = root / REQUIREMENTS_REL
    if not p.is_file():
        raise FileNotFoundError(f"requirements manifest missing: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_asset(asset_id: str, repo_root: Path | None = None) -> dict:
    """Resolve asset location/status without leaking secret plaintext.

    Returns dict with keys: asset_id, repo_path, exists, sha256 (if applicable), fingerprint (for SECRET), providers_tried, env_sources
    """
    root = repo_root or find_repo_root()
    req = load_requirements(root)
    asset = next((a for a in req.get("required_assets", []) if a.get("id") == asset_id), None)
    if asset is None:
        raise KeyError(f"unknown asset id: {asset_id}")

    # primary repo-relative path
    rel = asset.get("path") or (asset.get("paths") or [None])[0]
    repo_path = (root / rel) if rel else root
    result: dict = {
        "asset_id": asset_id,
        "classification": asset.get("classification"),
        "repo_path": str(repo_path),
        "rel": rel,
        "exists": False,
        "providers": asset.get("bootstrap_provider", []),
        "env_sources": {},
    }

    # Record env var presence (not values for secrets)
    for ev in asset.get("env_vars", []):
        v = os.environ.get(ev)
        if v is not None:
            if asset.get("classification") == "SECRET":
                result["env_sources"][ev] = f"<present:{len(v)}chars>"
            else:
                result["env_sources"][ev] = v

    # Existence check
    if rel and (root / rel).exists():
        # for file
        p = root / rel
        if p.is_file():
            result["exists"] = True
            # fingerprint only for SECRET
            if asset.get("classification") == "SECRET":
                try:
                    data = p.read_bytes()
                    result["fingerprint"] = hashlib.sha256(data).hexdigest()
                    result["size"] = len(data)
                except OSError:
                    pass
            else:
                # for non-secret, optionally hash but not required here
                try:
                    if asset_id == "original_exe":
                        result["sha256"] = _sha256_file(p).upper()
                        result["size"] = p.stat().st_size
                    elif asset_id == "gdre_tool":
                        result["sha256"] = _sha256_file(p).lower()
                        result["size"] = p.stat().st_size
                except OSError:
                    pass
        elif p.is_dir():
            result["exists"] = True

    # For recovered_provenance: check both dirs
    if asset_id == "recovered_provenance":
        paths = asset.get("paths", [])
        result["checks"] = {}
        for rp in paths:
            pp = root / rp
            result["checks"][rp] = pp.is_dir() and any(pp.iterdir()) if pp.is_dir() else False
        result["exists"] = all(result["checks"].values())

    return result


def check_portability(repo_root: Path | None = None) -> dict:
    """Run lightweight portability checks: abs_path_scan + secret_scan presence.

    Returns dict with summary; does not fail on missing tools, just reports.
    """
    root = repo_root or find_repo_root()
    out = {"repo_root": str(root), "checks": {}}
    # try import scans
    try:
        sys.path.insert(0, str(root / "scripts" / "ai"))
        from abs_path_scan import scan_repo as abs_scan  # type: ignore
        hits = abs_scan(root)
        fails = [h for h in hits if h.get("severity") == "FAIL"]
        out["checks"]["abs_path_scan"] = {
            "status": "FAIL" if fails else "PASS",
            "hits_total": len(hits),
            "fail_hits": len(fails),
        }
    except Exception as e:
        out["checks"]["abs_path_scan"] = {"status": "WARN", "error": str(e)}
    try:
        from secret_scan import scan_repo as sec_scan  # type: ignore
        findings = sec_scan(root)
        out["checks"]["secret_scan"] = {
            "status": "FAIL" if findings else "PASS",
            "findings": len(findings),
        }
    except Exception as e:
        out["checks"]["secret_scan"] = {"status": "WARN", "error": str(e)}
    return out


def get_readiness_level(repo_root: Path | None = None) -> dict:
    """Compute readiness levels per dev_doctor semantics (lightweight)."""
    root = repo_root or find_repo_root()
    levels = {
        "LEVEL_0_REPO_READY": False,
        "LEVEL_1_BUILD_READY": False,
        "LEVEL_2_RUNTIME_READY": False,
        "LEVEL_3_FULL_VALIDATION_READY": False,
    }
    reasons: dict[str, str] = {}

    # LEVEL 0: git repo + AGENTS.md + status.json parseable + provenance dirs present
    try:
        # git
        r = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=str(root), capture_output=True, text=True)
        git_ok = r.returncode == 0 and r.stdout.strip() == "true"
        ag_ok = (root / "AGENTS.md").is_file()
        status_ok = False
        try:
            json.loads((root / "status.json").read_text(encoding="utf-8"))
            status_ok = True
        except Exception:
            pass
        prov_ok = (root / "03_raw").is_dir() and (root / "04_recovered").is_dir()
        levels["LEVEL_0_REPO_READY"] = bool(git_ok and ag_ok and status_ok and prov_ok)
        if not levels["LEVEL_0_REPO_READY"]:
            reasons["LEVEL_0_REPO_READY"] = f"git={git_ok} agents={ag_ok} status={status_ok} provenance={prov_ok}"
    except Exception as e:
        reasons["LEVEL_0_REPO_READY"] = str(e)

    # LEVEL 1: + original_exe correct sha + script_key present + gdre exists + python ok
    try:
        exe = root / "00_original/Mutagenic.exe"
        key = root / "manifests/script_key.txt"
        gdre = root / "02_tools/gdre/gdre_tools.exe"
        exe_ok = False
        if exe.is_file():
            try:
                exe_ok = _sha256_file(exe).upper() == "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209" and exe.stat().st_size == 103290320
            except OSError:
                pass
        key_ok = key.is_file() and len(key.read_text(encoding="utf-8").strip()) == 64 if key.is_file() else False
        gdre_ok = gdre.is_file()
        py_ok = sys.version_info >= (3, 11)
        levels["LEVEL_1_BUILD_READY"] = bool(levels["LEVEL_0_REPO_READY"] and exe_ok and key_ok and gdre_ok and py_ok)
        if not levels["LEVEL_1_BUILD_READY"]:
            reasons["LEVEL_1_BUILD_READY"] = f"exe={exe_ok} key={key_ok} gdre={gdre_ok} python={py_ok}"
    except Exception as e:
        reasons["LEVEL_1_BUILD_READY"] = str(e)

    # LEVEL 2: + cache dir writable + pipeline files present
    try:
        cache = Path(os.environ.get("MUTAGENIC_CACHE_ROOT", str(root / ".cache")))
        try:
            cache.mkdir(parents=True, exist_ok=True)
            cache_ok = cache.is_dir()
        except OSError:
            cache_ok = False
        pipeline_ok = (root / "scripts" / "build").is_dir() or (root / "scripts" / "pipeline").is_dir() or (root / "scripts" / "extract_pck.py").is_file()
        levels["LEVEL_2_RUNTIME_READY"] = bool(levels["LEVEL_1_BUILD_READY"] and cache_ok and pipeline_ok)
        if not levels["LEVEL_2_RUNTIME_READY"]:
            reasons["LEVEL_2_RUNTIME_READY"] = f"cache={cache_ok} pipeline={pipeline_ok}"
    except Exception as e:
        reasons["LEVEL_2_RUNTIME_READY"] = str(e)

    # LEVEL 3: + abs_path no FAIL + secret no findings + check_all would pass (approx)
    try:
        port = check_portability(root)
        abs_ok = port.get("checks", {}).get("abs_path_scan", {}).get("status") == "PASS"
        sec_ok = port.get("checks", {}).get("secret_scan", {}).get("status") == "PASS"
        levels["LEVEL_3_FULL_VALIDATION_READY"] = bool(levels["LEVEL_2_RUNTIME_READY"] and abs_ok and sec_ok)
        if not levels["LEVEL_3_FULL_VALIDATION_READY"]:
            reasons["LEVEL_3_FULL_VALIDATION_READY"] = f"abs={abs_ok} secret={sec_ok}"
    except Exception as e:
        reasons["LEVEL_3_FULL_VALIDATION_READY"] = str(e)

    return {"levels": levels, "reasons": reasons}


__all__ = ["find_repo_root", "get_repo_root", "load_requirements", "resolve_asset", "get_readiness_level", "check_portability"]
