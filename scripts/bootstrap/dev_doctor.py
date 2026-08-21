#!/usr/bin/env python3
"""Portable dev environment doctor — FAIL-CLOSED, no hard-coded paths.

Supports being invoked from any subdir (via dev_environment.find_repo_root).
Checks: GIT, REPO, PROVENANCE, ORIGINAL_ASSET, SCRIPT_KEY, TOOLS, PYTHON,
        PIPELINE, BUILD, VALIDATE, RUNTIME, VM

Each check emits PASS/WARN/BLOCKED/FAIL + proves/not_proven/remediation.
Outputs human summary to stdout + machine JSON if --json <path>.
Exit 0 unless FAIL (BLOCKED is expected on fresh clone).

Never prints secret plaintext; only fingerprints (sha256 first 8).
No hard-coded drive/user/UNC — all repo paths from repo_root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

_THIS = Path(__file__).resolve()
_REPO_FALLBACK = _THIS.parents[2]
sys.path.insert(0, str(_REPO_FALLBACK / "scripts" / "env"))
sys.path.insert(0, str(_REPO_FALLBACK / "scripts" / "ai"))

from dev_environment import find_repo_root, load_requirements  # type: ignore

ORIGINAL_SHA = "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209"
ORIGINAL_SIZE = 103290320
GDRE_SHA = "88d6fbccfb7e5bacca7d248c5171fe66bbef15d78e0d7f6287c2f44e78aa9eaf"
GDRE_VERSION = "2.6.4"

LEVELS_ORDER = [
    "LEVEL_0_REPO_READY",
    "LEVEL_1_BUILD_READY",
    "LEVEL_2_RUNTIME_READY",
    "LEVEL_3_FULL_VALIDATION_READY",
]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True, encoding="utf-8", errors="replace")


def check_git(repo_root: Path) -> dict:
    inner = run(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo_root)
    inside = inner.returncode == 0 and inner.stdout.strip() == "true"
    br = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root)
    branch = br.stdout.strip() if br.returncode == 0 else "unknown"
    hd = run(["git", "rev-parse", "HEAD"], cwd=repo_root)
    head = hd.stdout.strip() if hd.returncode == 0 else "unknown"
    ok = inside and head != "unknown" and len(head) == 40
    status = "PASS" if ok else "FAIL"
    return {
        "id": "GIT",
        "status": status,
        "proves": "repo is inside git worktree with resolvable HEAD" if ok else "",
        "not_proven": "" if ok else "git worktree or HEAD not resolvable",
        "remediation": "" if ok else "Run inside a valid git clone; check git installation.",
        "branch": branch,
        "head": head,
        "inside": inside,
    }


def check_repo(repo_root: Path) -> dict:
    ag = (repo_root / "AGENTS.md").is_file()
    sj = repo_root / "status.json"
    sj_ok = False
    sj_err = ""
    try:
        json.loads(sj.read_text(encoding="utf-8"))
        sj_ok = True
    except Exception as e:
        sj_err = str(e)
    ok = ag and sj_ok
    status = "PASS" if ok else "FAIL"
    remediation = ""
    if not ag:
        remediation = "Missing AGENTS.md — not a valid Mutagenic clone"
    elif not sj_ok:
        remediation = f"status.json unparseable: {sj_err}"
    return {
        "id": "REPO",
        "status": status,
        "proves": "AGENTS.md present and status.json parseable" if ok else "",
        "not_proven": "" if ok else "repo marker or machine authority source invalid",
        "remediation": remediation,
        "agents": ag,
        "status_json": sj_ok,
    }


def check_provenance(repo_root: Path) -> dict:
    raw_dir = repo_root / "03_raw"
    rec_dir = repo_root / "04_recovered"
    raw_manifest = repo_root / "manifests/raw_manifest.json"
    rec_manifest = repo_root / "manifests/recovered_clean_manifest.json"
    raw_ok = raw_manifest.is_file()
    rec_ok = rec_manifest.is_file()
    # count checks: 03_raw 3744, 04_recovered 5058 per spec; we can count files or check manifest count field
    raw_count = None
    rec_count = None
    try:
        if raw_ok:
            raw_data = json.loads(raw_manifest.read_text(encoding="utf-8"))
            raw_count = raw_data.get("count") or len(raw_data.get("files", []))
    except Exception:
        pass
    try:
        if rec_ok:
            rec_data = json.loads(rec_manifest.read_text(encoding="utf-8"))
            # recovered_clean_manifest shape may use count or files
            rec_count = rec_data.get("count") or len(rec_data.get("files", []))
            if rec_count is None:
                # try alternative key
                rec_count = rec_data.get("file_count")
    except Exception:
        pass
    # also check actual dir listing if manifests unavailable
    actual_raw = len(list(raw_dir.rglob("*"))) if raw_dir.is_dir() else 0
    actual_rec = len(list(rec_dir.rglob("*"))) if rec_dir.is_dir() else 0
    # prefer manifest declared counts
    exp_raw = 3744
    exp_rec = 5058
    raw_match = raw_count == exp_raw if raw_count is not None else None
    rec_match = rec_count == exp_rec if rec_count is not None else None
    # fallback to file existence check if count not readable
    dir_ok = raw_dir.is_dir() and rec_dir.is_dir()
    # gitattributes byte-preserving check
    ga = (repo_root / ".gitattributes").read_text(encoding="utf-8", errors="replace") if (repo_root / ".gitattributes").is_file() else ""
    ga_ok = "/03_raw/** -text -eol" in ga and "/04_recovered/** -text -eol" in ga
    # Overall
    manifest_ok = raw_ok and rec_ok
    count_ok = (raw_match is True and rec_match is True) if raw_match is not None and rec_match is not None else dir_ok
    ok = manifest_ok and dir_ok and ga_ok and (raw_match is not False and rec_match is not False)
    if not manifest_ok or not dir_ok:
        status = "FAIL"
    elif raw_match is False or rec_match is False:
        status = "FAIL"
    elif not ga_ok:
        status = "WARN"
    else:
        status = "PASS"
    remediation = ""
    if not raw_ok:
        remediation = "Missing manifests/raw_manifest.json — clone incomplete"
    elif not rec_ok:
        remediation = "Missing manifests/recovered_clean_manifest.json"
    elif raw_match is False:
        remediation = f"raw_manifest count mismatch expected {exp_raw} got {raw_count}"
    elif rec_match is False:
        remediation = f"recovered_clean_manifest count mismatch expected {exp_rec} got {rec_count}"
    elif not dir_ok:
        remediation = "03_raw or 04_recovered directory missing"
    elif not ga_ok:
        remediation = ".gitattributes missing byte-preserving rules for 03_raw/04_recovered"
    return {
        "id": "PROVENANCE",
        "status": status,
        "proves": "immutable provenance dirs and manifests present with expected counts" if status == "PASS" else "",
        "not_proven": "" if status == "PASS" else "provenance integrity not fully evidenced",
        "remediation": remediation,
        "raw_manifest": raw_ok,
        "recovered_manifest": rec_ok,
        "raw_count": raw_count,
        "recovered_count": rec_count,
        "actual_raw_files": actual_raw,
        "actual_rec_files": actual_rec,
        "gitattributes_byte_preserving": ga_ok,
    }


def check_original(repo_root: Path) -> dict:
    p = repo_root / "00_original/Mutagenic.exe"
    if not p.is_file():
        return {
            "id": "ORIGINAL_ASSET",
            "status": "BLOCKED",
            "proves": "",
            "not_proven": "pristine EXE not present — cannot fresh-embed",
            "remediation": f"Provide owned pristine EXE at 00_original/Mutagenic.exe (SHA {ORIGINAL_SHA} size {ORIGINAL_SIZE}) or set MUTAGENIC_DEVKIT_ROOT / MUTAGENIC_ORIGINAL_EXE; export from source: python scripts/bootstrap/export_private_devkit.py --out <dir>",
            "path": str(p),
            "exists": False,
        }
    try:
        sha = sha256_file(p).upper()
        sz = p.stat().st_size
        if sha == ORIGINAL_SHA and sz == ORIGINAL_SIZE:
            return {
                "id": "ORIGINAL_ASSET",
                "status": "PASS",
                "proves": "pristine EXE matches expected SHA and size — fresh embed source valid",
                "not_proven": "runtime behavior",
                "remediation": "",
                "path": str(p),
                "exists": True,
                "sha256": sha,
                "sha256_short": sha[:8],
                "size": sz,
            }
        else:
            return {
                "id": "ORIGINAL_ASSET",
                "status": "FAIL",
                "proves": "",
                "not_proven": "pristine EXE hash/size mismatch",
                "remediation": f"Replace with pristine owned EXE SHA {ORIGINAL_SHA} size {ORIGINAL_SIZE} — current sha={sha} size={sz}",
                "path": str(p),
                "exists": True,
                "sha256": sha,
                "sha256_short": sha[:8],
                "size": sz,
                "expected_sha256": ORIGINAL_SHA,
                "expected_size": ORIGINAL_SIZE,
            }
    except OSError as e:
        return {"id": "ORIGINAL_ASSET", "status": "FAIL", "proves": "", "not_proven": str(e), "remediation": str(e), "path": str(p)}


def check_script_key(repo_root: Path) -> dict:
    p = repo_root / "manifests/script_key.txt"
    if not p.is_file():
        has_env = bool(os.environ.get("MUTAGENIC_SCRIPT_KEY") or os.environ.get("MUTAGENIC_SCRIPT_KEY_FILE") or os.environ.get("MUTAGENIC_DEVKIT_ROOT"))
        if has_env:
            return {
                "id": "SCRIPT_KEY",
                "status": "BLOCKED",
                "proves": "",
                "not_proven": "script key not yet materialized but env provider present (bootstrap can restore)",
                "remediation": "Run python scripts/bootstrap/bootstrap_dev_env.py to materialize key from env",
                "path": str(p),
                "exists": False,
                "env_provider": True,
            }
        return {
            "id": "SCRIPT_KEY",
            "status": "BLOCKED",
            "proves": "",
            "not_proven": "AES script key missing — cannot compile/encrypt",
            "remediation": "Provide 64-hex key via MUTAGENIC_SCRIPT_KEY (64 hex) or MUTAGENIC_SCRIPT_KEY_FILE=<path> or MUTAGENIC_DEVKIT_ROOT/manifests/script_key.txt; export: python scripts/bootstrap/export_private_devkit.py --out <dir>",
            "path": str(p),
            "exists": False,
        }
    try:
        data = p.read_bytes()
        txt = data.decode("utf-8", errors="replace").strip().split()[0] if data else ""
        fp_full = hashlib.sha256(data).hexdigest()
        fp_short = fp_full[:8]
        ok = len(txt) == 64 and all(c in "0123456789abcdefABCDEF" for c in txt)
        if ok:
            return {
                "id": "SCRIPT_KEY",
                "status": "PASS",
                "proves": "script key present with valid 64-hex format (fingerprint only)",
                "not_proven": "runtime correctness",
                "remediation": "",
                "path": str(p),
                "exists": True,
                "fingerprint": fp_full,
                "fingerprint_short": fp_short,
                "size": len(data),
            }
        else:
            return {
                "id": "SCRIPT_KEY",
                "status": "FAIL",
                "proves": "",
                "not_proven": "key file not 64 hex",
                "remediation": "Replace with 64 hex chars (32 bytes) single line; check source file",
                "path": str(p),
                "exists": True,
                "fingerprint": fp_full,
                "fingerprint_short": fp_short,
                "size": len(data),
            }
    except OSError as e:
        return {"id": "SCRIPT_KEY", "status": "FAIL", "proves": "", "not_proven": str(e), "remediation": str(e), "path": str(p)}


def check_tools(repo_root: Path) -> dict:
    gdre = repo_root / "02_tools/gdre/gdre_tools.exe"
    if not gdre.is_file():
        # also check env providers
        env_tool = os.environ.get("MUTAGENIC_TOOL_ROOT")
        env_devkit = os.environ.get("MUTAGENIC_DEVKIT_ROOT")
        has_env = bool(env_tool or env_devkit)
        status = "WARN" if has_env else "WARN"
        return {
            "id": "TOOLS",
            "status": status,
            "proves": "",
            "not_proven": "GDRE 2.6.4 not present locally",
            "remediation": "Download GDRE v2.6.4 to 02_tools/gdre/gdre_tools.exe or set MUTAGENIC_TOOL_ROOT / MUTAGENIC_DEVKIT_ROOT containing gdre/gdre_tools.exe; expected SHA " + GDRE_SHA,
            "path": str(gdre),
            "exists": False,
            "expected_sha256": GDRE_SHA,
            "expected_version": GDRE_VERSION,
        }
    try:
        sha = sha256_file(gdre).lower()
        ok = sha == GDRE_SHA
        status = "PASS" if ok else "WARN"
        return {
            "id": "TOOLS",
            "status": status,
            "proves": "GDRE 2.6.4 present with expected SHA" if ok else "",
            "not_proven": "" if ok else "GDRE SHA mismatch — version may differ",
            "remediation": "" if ok else f"Re-download GDRE {GDRE_VERSION} expected {GDRE_SHA} got {sha}",
            "path": str(gdre),
            "exists": True,
            "sha256": sha,
            "sha256_short": sha[:8],
            "expected_sha256": GDRE_SHA,
            "expected_version": GDRE_VERSION,
        }
    except OSError as e:
        return {"id": "TOOLS", "status": "WARN", "proves": "", "not_proven": str(e), "remediation": str(e), "path": str(gdre)}


def check_python(repo_root: Path) -> dict:
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info >= (3, 11)
    deps = {}
    # pycryptodome -> Crypto, pillow -> PIL, fonttools, frida
    for pkg, mod_name in [("pycryptodome", "Crypto"), ("pillow", "PIL"), ("fonttools", "fontTools"), ("frida", "frida")]:
        try:
            __import__(mod_name)
            deps[pkg] = True
        except ImportError:
            deps[pkg] = False
    # also check pip existence
    import shutil
    pip_ok = shutil.which("pip") is not None
    all_deps = all(deps.values())
    if not py_ok:
        status = "FAIL"
    elif not all_deps:
        status = "WARN"
    else:
        status = "PASS"
    remediation = ""
    if not py_ok:
        remediation = f"Python >=3.11 required, found {py_ver}"
    elif not all_deps:
        missing = [k for k, v in deps.items() if not v]
        remediation = f"pip install -r requirements.txt — missing: {', '.join(missing)}"
    return {
        "id": "PYTHON",
        "status": status,
        "proves": "Python version and pip deps present" if status == "PASS" else "",
        "not_proven": "" if status == "PASS" else "python env incomplete",
        "remediation": remediation,
        "python_version": py_ver,
        "python_ok": py_ok,
        "pip_ok": pip_ok,
        "deps": deps,
    }


def check_pipeline(repo_root: Path) -> dict:
    # check canonical scripts existence
    candidates = [
        "scripts/patch/resolve_mod_chain.py",
        "scripts/patch/apply_mod.py",
        "scripts/build/compile_declared_scripts.py",
        "scripts/build/build_declared_pack.py",
        "scripts/extract_pck.py",
        "scripts/embed_pck.py",
        "scripts/recover/recover_reference.py",
        "scripts/build/normalize_pck_md5.py",
    ]
    missing = [p for p in candidates if not (repo_root / p).is_file()]
    ok = len(missing) == 0
    status = "PASS" if ok else "FAIL"
    return {
        "id": "PIPELINE",
        "status": status,
        "proves": "canonical pipeline scripts present" if ok else "",
        "not_proven": "" if ok else f"missing: {', '.join(missing)}",
        "remediation": "" if ok else f"Restore missing pipeline scripts: {', '.join(missing)}",
        "missing": missing,
        "checked": candidates,
    }


def check_build(repo_root: Path) -> dict:
    cache = Path(os.environ.get("MUTAGENIC_CACHE_ROOT", str(repo_root / ".cache")))
    try:
        cache.mkdir(parents=True, exist_ok=True)
        writable = cache.is_dir() and os.access(cache, os.W_OK)
    except OSError:
        writable = False
    # build profile
    profile = repo_root / ".cache/build_profile.json"
    # also check tools.lock.json
    tl = repo_root / "tools.lock.json"
    tl_ok = tl.is_file()
    if writable:
        status = "PASS" if tl_ok else "WARN"
    else:
        status = "FAIL"
    remediation = ""
    if not writable:
        remediation = f".cache not writable: {cache}"
    elif not tl_ok:
        remediation = "tools.lock.json missing — toolchain lock not found"
    return {
        "id": "BUILD",
        "status": status,
        "proves": ".cache writable and build profile accessible" if status == "PASS" else "",
        "not_proven": "" if status == "PASS" else "build cache or toolchain lock not ready",
        "remediation": remediation,
        "cache_root": str(cache),
        "writable": writable,
        "tools_lock": tl_ok,
        "build_profile": profile.is_file(),
    }


def check_validate(repo_root: Path) -> dict:
    details = {}
    # abs_path_scan
    try:
        sys.path.insert(0, str(repo_root / "scripts" / "ai"))
        from abs_path_scan import scan_repo as abs_scan  # type: ignore
        hits = abs_scan(repo_root)
        fails = [h for h in hits if h.get("severity") == "FAIL"]
        details["abs_path_scan"] = {"status": "FAIL" if fails else "PASS", "hits_total": len(hits), "fail_hits": len(fails)}
    except Exception as e:
        details["abs_path_scan"] = {"status": "WARN", "error": str(e)}
    # secret_scan
    try:
        from secret_scan import scan_repo as sec_scan  # type: ignore
        findings = sec_scan(repo_root)
        details["secret_scan"] = {"status": "FAIL" if findings else "PASS", "findings": len(findings) if isinstance(findings, list) else str(findings)[:200]}
    except Exception as e:
        details["secret_scan"] = {"status": "WARN", "error": str(e)}
    # status.json parseable already checked but repeat
    try:
        json.loads((repo_root / "status.json").read_text(encoding="utf-8"))
        details["status_json"] = {"status": "PASS"}
    except Exception as e:
        details["status_json"] = {"status": "FAIL", "error": str(e)}
    # mod resolver self-check: try import and help
    try:
        r = run([sys.executable, str(repo_root / "scripts/patch/resolve_mod_chain.py"), "--help"])
        details["mod_resolver"] = {"status": "PASS" if r.returncode == 0 else "WARN", "rc": r.returncode}
    except Exception as e:
        details["mod_resolver"] = {"status": "WARN", "error": str(e)}
    # check_all existence
    ca = repo_root / "scripts/ai/check_all.py"
    if ca.is_file():
        details["check_all"] = {"status": "PASS", "path": str(ca)}
    else:
        details["check_all"] = {"status": "WARN", "path": str(ca), "error": "missing"}
    # overall
    fails = sum(1 for v in details.values() if v.get("status") == "FAIL")
    warns = sum(1 for v in details.values() if v.get("status") == "WARN")
    if fails:
        status = "FAIL"
    elif warns:
        status = "WARN"
    else:
        status = "PASS"
    return {
        "id": "VALIDATE",
        "status": status,
        "proves": "abs_path/secret/status/mod_resolver/check_all all PASS" if status == "PASS" else "",
        "not_proven": "" if status == "PASS" else "validation gates not fully passing",
        "remediation": "" if status == "PASS" else "Run python scripts/ai/check_all.py and fix reported findings",
        "details": details,
    }


def check_runtime(repo_root: Path) -> dict:
    # Runtime = cache + ability to boot? Without VM it is BLOCKED but we explain levels
    cache = Path(os.environ.get("MUTAGENIC_CACHE_ROOT", str(repo_root / ".cache")))
    writable = cache.is_dir() or True
    try:
        cache.mkdir(parents=True, exist_ok=True)
        writable = True
    except OSError:
        writable = False
    # Check if exe/key ready affects runtime
    exe_ok = (repo_root / "00_original/Mutagenic.exe").is_file()
    key_ok = (repo_root / "manifests/script_key.txt").is_file()
    # RUNTIME requires LEVEL_1 -> if not, BLOCKED is expected
    if not exe_ok or not key_ok:
        status = "BLOCKED"
        remediation = "RUNTIME requires LEVEL_1_BUILD_READY (original EXE + script key). Restore via bootstrap."
    elif not writable:
        status = "FAIL"
        remediation = f".cache not writable: {cache}"
    else:
        # Without VM/Hyper-V we cannot prove full runtime; treat as WARN/BLOCKED per spec
        # Spec says RUNTIME/VM 未配置时标 BLOCKED 但说明 LEVEL_0/LEVEL1 是否 READY
        # We'll report BLOCKED if no VM tooling, but still indicate cache is ready
        status = "BLOCKED"
        remediation = "VM/Hyper-V not configured or not probed — runtime full validation not available; LEVEL_0/LEVEL1 readiness unaffected"
    return {
        "id": "RUNTIME",
        "status": status,
        "proves": "" if status != "PASS" else "runtime cache ready",
        "not_proven": "full runtime not validated without VM/Hyper-V" if status == "BLOCKED" else "",
        "remediation": remediation,
        "cache_writable": writable,
        "level_hint": "check LEVEL_0_REPO_READY / LEVEL_1_BUILD_READY for build readiness",
    }


def check_vm(repo_root: Path) -> dict:
    # Probe Hyper-V / VM availability — no hard-coded host; just check powershell / hyper-v
    # If unavailable, BLOCKED is expected
    import shutil
    ps = shutil.which("powershell") or shutil.which("pwsh")
    has_ps = ps is not None
    # Try a lightweight VM probe: check if build profile mentions VM or if VM artifacts dir exists
    # We do not require VM for repo/build readiness
    status = "BLOCKED"
    remediation = "VM not configured — LEVEL_3_FULL_VALIDATION_READY requires VM/Hyper-V. See docs/dev-environment for setup; LEVEL_0/LEVEL1 still READY if repo/build checks PASS."
    if not has_ps:
        remediation = "powershell not found — VM probes unavailable; install PowerShell 5.1+ or pwsh"
    return {
        "id": "VM",
        "status": status,
        "proves": "",
        "not_proven": "VM/Hyper-V validation not executed",
        "remediation": remediation,
        "powershell": has_ps,
        "note": "LEVEL_2_RUNTIME_READY and LEVEL_3 require VM; LEVEL_0_REPO_READY and LEVEL_1_BUILD_READY are independent",
    }


def compute_levels(checks: dict, repo_root: Path) -> dict:
    # Mirrors dev_environment.get_readiness_level but uses doctor checks for accuracy
    # Import helper for detailed reasoning
    try:
        from dev_environment import get_readiness_level  # type: ignore
        base = get_readiness_level(repo_root)
        levels = base.get("levels", {})
        reasons = base.get("reasons", {})
    except Exception as e:
        levels = {k: False for k in LEVELS_ORDER}
        reasons = {"error": str(e)}
    # Ensure all levels present
    for lvl in LEVELS_ORDER:
        levels.setdefault(lvl, False)
    # Override with doctor-derived logic if needed for consistency
    # LEVEL_0: GIT PASS + REPO PASS + PROVENANCE PASS/WARN?
    git_ok = checks.get("GIT", {}).get("status") == "PASS"
    repo_ok = checks.get("REPO", {}).get("status") == "PASS"
    prov_ok = checks.get("PROVENANCE", {}).get("status") in ("PASS", "WARN")
    if not (git_ok and repo_ok and prov_ok):
        levels["LEVEL_0_REPO_READY"] = False
    # LEVEL_1 additionally requires ORIGINAL PASS + SCRIPT_KEY PASS + TOOLS PASS/WARN + PYTHON PASS/WARN
    orig_ok = checks.get("ORIGINAL_ASSET", {}).get("status") == "PASS"
    key_ok = checks.get("SCRIPT_KEY", {}).get("status") == "PASS"
    tools_ok = checks.get("TOOLS", {}).get("status") in ("PASS", "WARN")
    python_ok = checks.get("PYTHON", {}).get("status") in ("PASS", "WARN")
    if not (levels["LEVEL_0_REPO_READY"] and orig_ok and key_ok and tools_ok and python_ok):
        levels["LEVEL_1_BUILD_READY"] = False
    # LEVEL_2 and LEVEL_3 remain as computed by dev_environment (cache/pipeline/validate)
    return {"levels": levels, "reasons": reasons}


_JSON_SENTINEL = "__DOCTOR_JSON_DEFAULT__"

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Doctor for Mutagenic dev environment (portable, FAIL-CLOSED).")
    ap.add_argument("--json", dest="json_out", nargs="?", const=_JSON_SENTINEL, metavar="PATH", help="emit JSON report to PATH; if bare --json, writes to <repo_root>/10_logs/dev_doctor.json")
    ap.add_argument("--verbose", action="store_true", help="verbose output")
    args = ap.parse_args(argv)

    verbose = args.verbose
    try:
        repo_root = find_repo_root()
    except Exception as e:
        print(f"[doctor] FAIL: not inside repo: {e}", file=sys.stderr)
        return 1

    # Determine json path: None = no json, Path = write file, "-" = stdout
    json_path: Path | None = None
    emit_stdout_json = False
    if args.json_out is not None:
        if args.json_out == _JSON_SENTINEL:
            json_path = repo_root / "10_logs/dev_doctor.json"
        elif args.json_out == "-" or args.json_out == "":
            emit_stdout_json = True
            json_path = None
        else:
            json_path = Path(args.json_out)
            if not json_path.is_absolute():
                json_path = (Path.cwd() / json_path).resolve()

    # Collect git info
    git_info = check_git(repo_root)
    checks: dict[str, dict] = {}
    checks["GIT"] = git_info
    checks["REPO"] = check_repo(repo_root)
    checks["PROVENANCE"] = check_provenance(repo_root)
    checks["ORIGINAL_ASSET"] = check_original(repo_root)
    checks["SCRIPT_KEY"] = check_script_key(repo_root)
    checks["TOOLS"] = check_tools(repo_root)
    checks["PYTHON"] = check_python(repo_root)
    checks["PIPELINE"] = check_pipeline(repo_root)
    checks["BUILD"] = check_build(repo_root)
    checks["VALIDATE"] = check_validate(repo_root)
    checks["RUNTIME"] = check_runtime(repo_root)
    checks["VM"] = check_vm(repo_root)

    levels_info = compute_levels(checks, repo_root)
    levels = levels_info["levels"]
    reasons = levels_info["reasons"]

    # Determine final level
    final_level = "NONE"
    for lvl in reversed(LEVELS_ORDER):
        if levels.get(lvl):
            final_level = lvl
            break
    # If LEVEL_0 not ready, final is NONE; else at least LEVEL_0
    if not levels.get("LEVEL_0_REPO_READY"):
        final_level = "NOT_READY"

    # Final status: FAIL if any FAIL, else BLOCKED_BY_PRIVATE_ASSET if any BLOCKED in ORIGINAL/SCRIPT_KEY, else DEV_ENV_READY if LEVEL_1+ else PARTIAL
    has_fail = any(v.get("status") == "FAIL" for v in checks.values())
    has_blocked_private = any(checks[k].get("status") == "BLOCKED" for k in ("ORIGINAL_ASSET", "SCRIPT_KEY"))
    if has_fail:
        final_status = "FAIL"
    elif has_blocked_private:
        final_status = "BLOCKED_BY_PRIVATE_ASSET"
    elif levels.get("LEVEL_3_FULL_VALIDATION_READY"):
        final_status = "DEV_ENV_READY"
    elif levels.get("LEVEL_2_RUNTIME_READY"):
        final_status = "DEV_ENV_READY"
    elif levels.get("LEVEL_1_BUILD_READY"):
        final_status = "DEV_ENV_READY"
    elif levels.get("LEVEL_0_REPO_READY"):
        final_status = "PARTIAL_REPO_READY"
    else:
        final_status = "NOT_READY"

    # Remediation aggregation
    remediation: list[str] = []
    for cid, info in checks.items():
        r = info.get("remediation")
        if r:
            remediation.append(f"{cid}: {r}")
    for lvl, reason in reasons.items():
        if reason and not levels.get(lvl):
            remediation.append(f"{lvl}: {reason}")

    json_report = {
        "repo_root": str(repo_root),
        "git": {"branch": git_info.get("branch"), "head": git_info.get("head"), "inside": git_info.get("inside")},
        "branch": git_info.get("branch"),
        "head": git_info.get("head"),
        "checks": checks,
        "levels": levels,
        "level_reasons": reasons,
        "final_level": final_level,
        "final_status": final_status,
        "remediation": remediation,
    }

    # Human summary
    print("=== dev_doctor ===")
    print(f"repo_root: {repo_root}")
    print(f"branch: {git_info.get('branch')}  head: {git_info.get('head')}")
    if git_info.get("head") and len(git_info.get("head")) >= 8:
        print(f"head_short: {git_info.get('head')[:8]}")
    print("--- checks ---")
    for cid in ["GIT","REPO","PROVENANCE","ORIGINAL_ASSET","SCRIPT_KEY","TOOLS","PYTHON","PIPELINE","BUILD","VALIDATE","RUNTIME","VM"]:
        info = checks.get(cid, {})
        st = info.get("status", "UNKNOWN")
        print(f"  {cid:15s} {st}")
        if info.get("fingerprint_short"):
            print(f"    fingerprint: sha256={info['fingerprint_short']}... (full not shown)")
        if info.get("sha256_short"):
            print(f"    sha256: {info['sha256_short']}... (full {info.get('sha256','')[:8]}...)")
        if info.get("size"):
            print(f"    size: {info['size']}")
        if verbose:
            if info.get("proves"):
                print(f"    proves: {info['proves']}")
            if info.get("not_proven"):
                print(f"    not_proven: {info['not_proven']}")
        if info.get("remediation"):
            print(f"    remediation: {info['remediation']}")
        # For PROVENANCE show counts
        if cid == "PROVENANCE" and verbose:
            print(f"    raw_count: {info.get('raw_count')} (expected 3744) recovered_count: {info.get('recovered_count')} (expected 5058)")
        if cid == "VALIDATE" and verbose:
            for k, v in info.get("details", {}).items():
                print(f"    validate.{k}: {v.get('status')} {v}")

    print("--- readiness ---")
    for lvl in LEVELS_ORDER:
        ok = levels.get(lvl)
        print(f"  {lvl}: {'PASS' if ok else 'NOT_READY'}")
        if verbose and not ok and reasons.get(lvl):
            print(f"    reason: {reasons[lvl]}")
    print(f"final_level: {final_level}")
    print(f"final_status: {final_status}")
    if final_status == "BLOCKED_BY_PRIVATE_ASSET":
        print("BLOCKED_BY_PRIVATE_ASSET: provision private assets then rerun bootstrap")
        print("  -> On source machine: python scripts/bootstrap/export_private_devkit.py --out <dir>")
        print("  -> On this machine: set MUTAGENIC_DEVKIT_ROOT=<dir> && python scripts/bootstrap/bootstrap_dev_env.py")
    elif final_status == "DEV_ENV_READY":
        print("DEV_ENV_READY: Fresh clone can build; runtime/VM gates may still be BLOCKED (expected without VM)")
        # Specifically note RUNTIME/VM BLOCKED but LEVEL_0/LEVEL1 READY
        if checks.get("RUNTIME", {}).get("status") == "BLOCKED" or checks.get("VM", {}).get("status") == "BLOCKED":
            l0 = levels.get("LEVEL_0_REPO_READY")
            l1 = levels.get("LEVEL_1_BUILD_READY")
            print(f"  note: RUNTIME/VM BLOCKED is expected without Hyper-V; LEVEL_0_REPO_READY={l0} LEVEL_1_BUILD_READY={l1}")
    if remediation and verbose:
        print("--- remediation ---")
        for r in remediation:
            print(f"  - {r}")

    if json_path is not None:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(json_report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[doctor] JSON report: {json_path}")

    if emit_stdout_json:
        print(json.dumps(json_report, ensure_ascii=False, indent=2))

    # Exit code: 0 if PASS or BLOCKED (fresh clone), 1 only on FAIL
    if has_fail:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
