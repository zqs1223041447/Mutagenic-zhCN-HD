#!/usr/bin/env python3
"""Portable dev environment bootstrapper - FAIL-CLOSED, IDEMPOTENT.

Flow:
  repo preflight -> load manifest -> ensure .cache etc -> restore original_exe
  -> restore secret -> check GDRE/tools -> python env -> fingerprint -> doctor summary

Supports: --check-only, --json [path], --verbose
Runs from any subdir (self-discovers repo_root). Never hard-codes drive/user/UNC.
On missing private asset: prints BLOCKED_BY_PRIVATE_ASSET + remediation, no traceback.
On wrong SHA: FAIL.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Ensure scripts/env is importable regardless of cwd
_THIS = Path(__file__).resolve()
_REPO_FALLBACK = _THIS.parents[2]  # scripts/bootstrap -> repo_root fallback
sys.path.insert(0, str(_REPO_FALLBACK / "scripts" / "env"))
sys.path.insert(0, str(_REPO_FALLBACK / "scripts" / "ai"))

from dev_environment import find_repo_root, load_requirements  # type: ignore

ORIGINAL_SHA = "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209"
ORIGINAL_SIZE = 103290320
RED = "\x1b[31m" if sys.stdout.isatty() else ""
RESET = "\x1b[0m" if sys.stdout.isatty() else ""


def log(msg: str, verbose: bool = False, is_verbose: bool = False) -> None:
    if is_verbose and not verbose:
        return
    print(msg)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_cache_dirs(repo_root: Path, verbose: bool) -> None:
    cache_root = Path(os.environ.get("MUTAGENIC_CACHE_ROOT", str(repo_root / ".cache")))
    dirs = [
        cache_root,
        cache_root / "gdre",
        cache_root / "pack_stage",
        cache_root / "base_index",
        repo_root / ".cache",
    ]
    for d in dirs:
        try:
            d.mkdir(parents=True, exist_ok=True)
            log(f"[bootstrap] ensure dir: {d}", verbose, True)
        except OSError as e:
            log(f"[bootstrap] WARN cannot create {d}: {e}")


def try_restore_original(repo_root: Path, verbose: bool) -> dict:
    """Restore 00_original/Mutagenic.exe with priority: existing correct SHA > DEVKIT_ROOT > ORIGINAL_EXE > BLOCKED."""
    dest = repo_root / "00_original/Mutagenic.exe"
    result: dict = {"id": "original_exe", "dest": str(dest), "status": "BLOCKED", "remediation": ""}
    # 1. existing and correct
    if dest.is_file():
        try:
            sz = dest.stat().st_size
            sha = sha256_file(dest).upper()
            if sha == ORIGINAL_SHA and sz == ORIGINAL_SIZE:
                log(f"[bootstrap] original_exe: existing correct at {dest}")
                result.update({"status": "PASS", "source": "existing_correct_sha", "sha256": sha, "size": sz})
                return result
            else:
                log(f"[bootstrap] FAIL: original EXE wrong SHA/size at {dest} sha={sha} size={sz} expected {ORIGINAL_SHA} / {ORIGINAL_SIZE}")
                result.update({"status": "FAIL", "sha256": sha, "size": sz, "expected_sha256": ORIGINAL_SHA, "expected_size": ORIGINAL_SIZE,
                               "remediation": "Replace with pristine owned copy; verify SHA256."})
                return result
        except OSError as e:
            log(f"[bootstrap] FAIL reading existing exe: {e}")
            result.update({"status": "FAIL", "error": str(e)})
            return result

    # 2. MUTAGENIC_DEVKIT_ROOT
    devkit = os.environ.get("MUTAGENIC_DEVKIT_ROOT")
    if devkit:
        cand = Path(devkit) / "00_original" / "Mutagenic.exe"
        # also allow flat devkit/Mutagenic.exe
        cands = [cand, Path(devkit) / "Mutagenic.exe"]
        for c in cands:
            if c.is_file():
                try:
                    sha = sha256_file(c).upper()
                    sz = c.stat().st_size
                    if sha != ORIGINAL_SHA or sz != ORIGINAL_SIZE:
                        log(f"[bootstrap] FAIL: candidate {c} wrong SHA/size sha={sha} size={sz}")
                        result.update({"status": "FAIL", "source": str(c), "sha256": sha, "size": sz})
                        return result
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(c, dest)
                    log(f"[bootstrap] original_exe: restored from MUTAGENIC_DEVKIT_ROOT {c} -> {dest}")
                    result.update({"status": "PASS", "source": str(c), "sha256": sha, "size": sz})
                    return result
                except OSError as e:
                    log(f"[bootstrap] WARN copy from {c}: {e}")

    # 3. MUTAGENIC_ORIGINAL_EXE
    orig_env = os.environ.get("MUTAGENIC_ORIGINAL_EXE")
    if orig_env:
        c = Path(orig_env)
        if c.is_file():
            try:
                sha = sha256_file(c).upper()
                sz = c.stat().st_size
                if sha != ORIGINAL_SHA or sz != ORIGINAL_SIZE:
                    log(f"[bootstrap] FAIL: MUTAGENIC_ORIGINAL_EXE {c} wrong SHA/size sha={sha} size={sz}")
                    result.update({"status": "FAIL", "source": str(c), "sha256": sha, "size": sz})
                    return result
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(c, dest)
                log(f"[bootstrap] original_exe: restored from MUTAGENIC_ORIGINAL_EXE {c} -> {dest}")
                result.update({"status": "PASS", "source": str(c), "sha256": sha, "size": sz})
                return result
            except OSError as e:
                log(f"[bootstrap] WARN copy from MUTAGENIC_ORIGINAL_EXE: {e}")
        else:
            log(f"[bootstrap] MUTAGENIC_ORIGINAL_EXE points to missing file: {c}")

    # 4. BLOCKED
    log(f"[bootstrap] BLOCKED_BY_PRIVATE_ASSET: original_exe missing at {dest}")
    log(f"  remediation: place owned pristine Mutagenic.exe at 00_original/Mutagenic.exe (SHA {ORIGINAL_SHA}, size {ORIGINAL_SIZE})")
    log(f"  or set MUTAGENIC_DEVKIT_ROOT to a devkit containing 00_original/Mutagenic.exe")
    log(f"  or set MUTAGENIC_ORIGINAL_EXE to absolute path of owned exe")
    log(f"  obtain via: python scripts/bootstrap/export_private_devkit.py --out <devkit_dir> on a machine that has it")
    result.update({
        "status": "BLOCKED_BY_PRIVATE_ASSET",
        "remediation": f"Provide owned pristine exe SHA {ORIGINAL_SHA} via 00_original/Mutagenic.exe or env MUTAGENIC_DEVKIT_ROOT / MUTAGENIC_ORIGINAL_EXE. Export from source machine: python scripts/bootstrap/export_private_devkit.py --out <dir>",
    })
    return result


def try_restore_secret(repo_root: Path, verbose: bool) -> dict:
    """Priority: MUTAGENIC_SCRIPT_KEY > MUTAGENIC_SCRIPT_KEY_FILE > MUTAGENIC_DEVKIT_ROOT > BLOCKED. Writes 64-hex single line."""
    dest = repo_root / "manifests/script_key.txt"
    result: dict = {"id": "script_key", "dest": str(dest), "status": "BLOCKED"}

    def write_key(hex_str: str, src_desc: str) -> dict:
        hex_str = hex_str.strip()
        if len(hex_str) != 64 or any(c not in "0123456789abcdefABCDEF" for c in hex_str):
            log(f"[bootstrap] FAIL: key from {src_desc} not 64 hex chars (len={len(hex_str)})")
            return {"status": "FAIL", "source": src_desc, "remediation": "Provide 64 hex chars (32 bytes). Check source file has single line hex."}
        dest.parent.mkdir(parents=True, exist_ok=True)
        # write normalized lower
        dest.write_text(hex_str.lower() + "\n", encoding="utf-8")
        fp = hashlib.sha256(dest.read_bytes()).hexdigest()
        log(f"[bootstrap] script_key: restored from {src_desc} -> {dest} (fingerprint sha256={fp})")
        return {"status": "PASS", "source": src_desc, "fingerprint": fp}

    # existing already valid?
    if dest.is_file():
        try:
            txt = dest.read_text(encoding="utf-8").strip()
            if len(txt) == 64 and all(c in "0123456789abcdefABCDEF" for c in txt):
                fp = hashlib.sha256(dest.read_bytes()).hexdigest()
                log(f"[bootstrap] script_key: existing valid at {dest} (fingerprint sha256={fp})", verbose, True)
                # Return PASS but note existing; no overwrite needed unless env overrides? keep existing.
                result.update({"status": "PASS", "source": "existing", "fingerprint": fp})
                return result
            else:
                log(f"[bootstrap] WARN: existing key at {dest} not 64 hex, will try env providers")
        except OSError as e:
            log(f"[bootstrap] WARN reading existing key: {e}")

    # 1. MUTAGENIC_SCRIPT_KEY inline
    env_key = os.environ.get("MUTAGENIC_SCRIPT_KEY")
    if env_key:
        r = write_key(env_key, "MUTAGENIC_SCRIPT_KEY")
        if r.get("status") == "PASS":
            result.update(r)
            return result
        else:
            result.update(r)
            return result

    # 2. MUTAGENIC_SCRIPT_KEY_FILE
    env_key_file = os.environ.get("MUTAGENIC_SCRIPT_KEY_FILE")
    if env_key_file:
        p = Path(env_key_file)
        if p.is_file():
            try:
                txt = p.read_text(encoding="utf-8").strip().split()[0]
                r = write_key(txt, f"MUTAGENIC_SCRIPT_KEY_FILE={p}")
                if r.get("status") == "PASS":
                    result.update(r)
                    return result
                result.update(r)
                return result
            except OSError as e:
                log(f"[bootstrap] WARN reading MUTAGENIC_SCRIPT_KEY_FILE {p}: {e}")
        else:
            log(f"[bootstrap] MUTAGENIC_SCRIPT_KEY_FILE missing: {p}")

    # 3. MUTAGENIC_DEVKIT_ROOT
    devkit = os.environ.get("MUTAGENIC_DEVKIT_ROOT")
    if devkit:
        cand = Path(devkit) / "manifests" / "script_key.txt"
        cands = [cand, Path(devkit) / "script_key.txt"]
        for c in cands:
            if c.is_file():
                try:
                    txt = c.read_text(encoding="utf-8").strip().split()[0]
                    r = write_key(txt, f"MUTAGENIC_DEVKIT_ROOT/{c.name}")
                    if r.get("status") == "PASS":
                        result.update(r)
                        return result
                except OSError as e:
                    log(f"[bootstrap] WARN reading devkit key {c}: {e}")

    # BLOCKED
    if dest.is_file() and result.get("status") == "BLOCKED":
        # we already checked existing valid above; if still blocked, existing invalid
        pass
    log(f"[bootstrap] BLOCKED_BY_PRIVATE_ASSET: script_key missing at {dest}")
    log(f"  remediation: set MUTAGENIC_SCRIPT_KEY=64hex or MUTAGENIC_SCRIPT_KEY_FILE=<path> or MUTAGENIC_DEVKIT_ROOT=<devkit>")
    log(f"  obtain via export: python scripts/bootstrap/export_private_devkit.py --out <devkit_dir>")
    result.update({
        "status": "BLOCKED_BY_PRIVATE_ASSET",
        "remediation": "Provide script key via MUTAGENIC_SCRIPT_KEY (64 hex) or MUTAGENIC_SCRIPT_KEY_FILE or MUTAGENIC_DEVKIT_ROOT/manifests/script_key.txt. Export: python scripts/bootstrap/export_private_devkit.py --out <dir>",
    })
    return result


def check_gdre(repo_root: Path) -> dict:
    gdre = repo_root / "02_tools/gdre/gdre_tools.exe"
    env_tool_root = os.environ.get("MUTAGENIC_TOOL_ROOT")
    env_devkit = os.environ.get("MUTAGENIC_DEVKIT_ROOT")
    # Also try to copy from env if missing locally
    if not gdre.is_file():
        for base in [env_tool_root, env_devkit]:
            if not base:
                continue
            for cand in [Path(base) / "02_tools/gdre/gdre_tools.exe", Path(base) / "gdre/gdre_tools.exe", Path(base) / "gdre_tools.exe"]:
                if cand.is_file():
                    try:
                        gdre.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(cand, gdre)
                        break
                    except OSError:
                        pass
            if gdre.is_file():
                break
    if gdre.is_file():
        try:
            sha = sha256_file(gdre).lower()
            # expected from tools.lock.json
            exp = "88d6fbccfb7e5bacca7d248c5171fe66bbef15d78e0d7f6287c2f44e78aa9eaf"
            status = "PASS" if sha == exp else "WARN"
            return {"id": "gdre_tool", "path": str(gdre), "status": status, "sha256": sha, "expected_sha256": exp, "version": "2.6.4"}
        except OSError as e:
            return {"id": "gdre_tool", "path": str(gdre), "status": "WARN", "error": str(e)}
    return {"id": "gdre_tool", "path": str(gdre), "status": "WARN", "remediation": "Download GDRE v2.6.4 to 02_tools/gdre/gdre_tools.exe or set MUTAGENIC_TOOL_ROOT/MUTAGENIC_DEVKIT_ROOT"}


def check_python_env(verbose: bool) -> dict:
    py_ok = sys.version_info >= (3, 11)
    pip_ok = shutil.which("pip") is not None
    reqs = ["pycryptodome", "pillow", "fonttools", "frida"]
    installed: dict = {}
    for pkg in reqs:
        try:
            __import__(pkg if pkg != "pycryptodome" else "Crypto")
            installed[pkg] = True
        except ImportError:
            try:
                # pillow is PIL
                if pkg == "pillow":
                    import PIL  # noqa
                    installed[pkg] = True
                else:
                    installed[pkg] = False
            except ImportError:
                installed[pkg] = False
    return {"python_version": sys.version.split()[0], "python_ok": py_ok, "pip_ok": pip_ok, "deps": installed}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Bootstrap portable Mutagenic dev environment (FAIL-CLOSED, idempotent).")
    ap.add_argument("--check-only", action="store_true", help="only check, do not write/restore")
    ap.add_argument("--json", dest="json_out", nargs="?", const="-", metavar="PATH", help="emit JSON report to PATH or stdout if no PATH")
    ap.add_argument("--verbose", action="store_true", help="verbose logging")
    args = ap.parse_args(argv)

    verbose = args.verbose

    try:
        repo_root = find_repo_root()
    except Exception as e:
        print(f"[bootstrap] FAIL: not inside repo: {e}", file=sys.stderr)
        return 1

    log(f"[bootstrap] repo_root: {repo_root}", verbose, False)
    # preflight: repo marker
    if not (repo_root / "AGENTS.md").is_file():
        print("[bootstrap] FAIL: AGENTS.md missing - not a valid clone", file=sys.stderr)
        return 1
    if not (repo_root / "status.json").is_file():
        print("[bootstrap] FAIL: status.json missing", file=sys.stderr)
        return 1

    try:
        req = load_requirements(repo_root)
        log(f"[bootstrap] manifest: {repo_root / 'manifests/dev_environment_requirements.json'} schema={req.get('schema_version')}", verbose, True)
    except Exception as e:
        print(f"[bootstrap] FAIL: cannot load requirements: {e}", file=sys.stderr)
        return 1

    report: dict = {"repo_root": str(repo_root), "steps": {}, "blocked": [], "failed": []}

    # ensure cache dirs unless check-only
    if not args.check_only:
        ensure_cache_dirs(repo_root, verbose)
        report["steps"]["cache_dirs"] = {"status": "PASS", "cache_root": str(Path(os.environ.get("MUTAGENIC_CACHE_ROOT", str(repo_root / ".cache"))))}
    else:
        report["steps"]["cache_dirs"] = {"status": "CHECK_ONLY"}

    # original exe
    if args.check_only:
        dest = repo_root / "00_original/Mutagenic.exe"
        if dest.is_file():
            try:
                sha = sha256_file(dest).upper()
                sz = dest.stat().st_size
                ok = sha == ORIGINAL_SHA and sz == ORIGINAL_SIZE
                report["steps"]["original_exe"] = {"status": "PASS" if ok else "FAIL", "sha256": sha, "size": sz}
                if not ok:
                    report["failed"].append("original_exe")
            except OSError as e:
                report["steps"]["original_exe"] = {"status": "FAIL", "error": str(e)}
                report["failed"].append("original_exe")
        else:
            report["steps"]["original_exe"] = {"status": "BLOCKED_BY_PRIVATE_ASSET", "remediation": "Provide owned exe via env or file"}
            report["blocked"].append("original_exe")
    else:
        r = try_restore_original(repo_root, verbose)
        report["steps"]["original_exe"] = r
        if r["status"] == "FAIL":
            report["failed"].append("original_exe")
        elif "BLOCKED" in r["status"]:
            report["blocked"].append("original_exe")

    # script key
    if args.check_only:
        dest = repo_root / "manifests/script_key.txt"
        if dest.is_file():
            try:
                txt = dest.read_text(encoding="utf-8").strip()
                ok = len(txt) == 64 and all(c in "0123456789abcdefABCDEF" for c in txt)
                fp = hashlib.sha256(dest.read_bytes()).hexdigest() if ok else None
                report["steps"]["script_key"] = {"status": "PASS" if ok else "FAIL", "fingerprint": fp}
                if not ok:
                    report["failed"].append("script_key")
            except OSError as e:
                report["steps"]["script_key"] = {"status": "FAIL", "error": str(e)}
                report["failed"].append("script_key")
        else:
            # check env would provide
            has_env = bool(os.environ.get("MUTAGENIC_SCRIPT_KEY") or os.environ.get("MUTAGENIC_SCRIPT_KEY_FILE") or os.environ.get("MUTAGENIC_DEVKIT_ROOT"))
            if has_env:
                report["steps"]["script_key"] = {"status": "PASS_VIA_ENV", "note": "env provider available (check-only, not restored)"}
            else:
                report["steps"]["script_key"] = {"status": "BLOCKED_BY_PRIVATE_ASSET"}
                report["blocked"].append("script_key")
    else:
        r = try_restore_secret(repo_root, verbose)
        report["steps"]["script_key"] = r
        if r["status"] == "FAIL":
            report["failed"].append("script_key")
        elif "BLOCKED" in r["status"]:
            report["blocked"].append("script_key")

    # gdre
    gdre_info = check_gdre(repo_root)
    report["steps"]["gdre_tool"] = gdre_info
    # not blocked, just WARN

    # python env
    py_info = check_python_env(verbose)
    report["steps"]["python_env"] = py_info
    if not py_info["python_ok"]:
        report["failed"].append("python_version")

    # recovered provenance
    prov_ok = (repo_root / "03_raw").is_dir() and (repo_root / "04_recovered").is_dir()
    report["steps"]["recovered_provenance"] = {"status": "PASS" if prov_ok else "FAIL", "03_raw": (repo_root / "03_raw").is_dir(), "04_recovered": (repo_root / "04_recovered").is_dir()}
    if not prov_ok:
        report["failed"].append("recovered_provenance")

    # fingerprint report
    try:
        fp_path = repo_root / "01_baseline/game_fingerprint.json"
        if fp_path.is_file():
            fp_data = json.loads(fp_path.read_text(encoding="utf-8"))
            report["steps"]["fingerprint"] = {"status": "PASS", "path": str(fp_path)}
        else:
            report["steps"]["fingerprint"] = {"status": "WARN", "path": str(fp_path), "note": "not present (optional)"}
    except Exception as e:
        report["steps"]["fingerprint"] = {"status": "WARN", "error": str(e)}

    # final doctor summary via dev_environment helper
    try:
        sys.path.insert(0, str(repo_root / "scripts" / "env"))
        from dev_environment import get_readiness_level  # type: ignore
        lvl = get_readiness_level(repo_root)
        report["readiness"] = lvl
        # elevate blocked to overall
        blocked = len(report["blocked"]) > 0
        failed = len(report["failed"]) > 0
        if failed:
            report["overall"] = "FAIL"
        elif blocked:
            report["overall"] = "BLOCKED_BY_PRIVATE_ASSET"
        else:
            # map readiness
            levels = lvl.get("levels", {})
            if levels.get("LEVEL_3_FULL_VALIDATION_READY"):
                report["overall"] = "DEV_ENV_READY"
            elif levels.get("LEVEL_1_BUILD_READY"):
                report["overall"] = "DEV_ENV_READY"
            else:
                report["overall"] = "PARTIAL"
    except Exception as e:
        report["readiness"] = {"error": str(e)}
        report["overall"] = "FAIL" if report["failed"] else ("BLOCKED_BY_PRIVATE_ASSET" if report["blocked"] else "UNKNOWN")

    # alias for doctor compatibility: final_status == overall
    report["final_status"] = report.get("overall")

    # human summary
    print("--- bootstrap summary ---")
    for k, v in report["steps"].items():
        st = v.get("status", "UNKNOWN")
        print(f"  {k:22s} {st}")
        if v.get("fingerprint"):
            print(f"    fingerprint: sha256={v['fingerprint']}")
        if v.get("sha256"):
            print(f"    sha256: {v['sha256']}")
        if v.get("remediation"):
            print(f"    remediation: {v['remediation']}")
    if report.get("readiness", {}).get("levels"):
        print("  readiness:")
        for lvl, ok in report["readiness"]["levels"].items():
            print(f"    {lvl}: {'PASS' if ok else 'NOT_READY'}")
    print(f"overall: {report.get('overall')}")
    if report["blocked"]:
        print(f"BLOCKED_BY_PRIVATE_ASSET: {', '.join(report['blocked'])}")
        print("  -> Fresh clone needs private assets. Run on source machine: python scripts/bootstrap/export_private_devkit.py --out <dir>")
        print("     Then on this machine set MUTAGENIC_DEVKIT_ROOT=<dir> and re-run bootstrap.")
    if report["failed"]:
        print(f"FAIL: {', '.join(report['failed'])}")

    # json output
    if args.json_out is not None:
        js = json.dumps(report, ensure_ascii=False, indent=2)
        if args.json_out == "-" or args.json_out == "":
            print(js)
        else:
            # resolve relative to repo_root or cwd? treat as given path
            out = Path(args.json_out)
            if not out.is_absolute():
                out = Path.cwd() / out
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(js, encoding="utf-8")
            print(f"[bootstrap] JSON report: {out}")

    # exit code: 0 if PASS or BLOCKED (blocked is expected for fresh clone), 1 only on FAIL
    if report["failed"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
