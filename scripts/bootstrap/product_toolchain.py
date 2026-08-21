#!/usr/bin/env python3
"""P1-X2: Product Godot 4.7.1 discovery + optional headless import.

Resolves the engine via PATH, MUTAGENIC_GODOT_4 / GODOT4 / GODOT_BIN, or
repo-relative 02_tools/godot/* — never via host-drive literals in source.

Statuses (never PASS):
  SUCCESS           found binary, version is 4.7.1
  NOT_FOUND         no binary (alias: tool_missing=true)
  VERSION_MISMATCH  binary found, version is not 4.7.1
  TOOL_FAILED       binary found but --version / import failed to run
  MISSING_PRIVATE   used only for private-asset classification, not as a fake engine PASS
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

WANTED_VERSION = "4.7.1"
ENV_VARS = ("MUTAGENIC_GODOT_4", "GODOT4", "GODOT_BIN", "GODOT")
WHICH_NAMES = (
    "godot",
    "godot4",
    "Godot_v4.7.1-stable_win64.exe",
    "Godot_v4.7.1-stable_win64_console.exe",
    "Godot_v4.7.1-stable_linux.x86_64",
    "Godot_v4.7.1-stable_linux_headless.x86_64",
)
REPO_RELATIVE_CANDIDATES = (
    "02_tools/godot/Godot_v4.7.1-stable_win64.exe",
    "02_tools/godot/Godot_v4.7.1-stable_win64_console.exe",
    "02_tools/godot/godot.exe",
    "02_tools/godot/godot",
    "02_tools/godot/Godot_v4.7.1-stable_linux.x86_64",
    "02_tools/godot/Godot_v4.7.1-stable_linux_headless.x86_64",
)
VERSION_RE = re.compile(r"(?:Godot Engine v)?(\d+\.\d+\.\d+)", re.IGNORECASE)

IsFile = Callable[[Path], bool]
WhichFn = Callable[[str], str | None]
RunFn = Callable[[list[str]], subprocess.CompletedProcess]


def parse_godot_version(text: str) -> str | None:
    match = VERSION_RE.search(text or "")
    return match.group(1) if match else None


def version_is_wanted(version: str | None) -> bool:
    if not version:
        return False
    return version == WANTED_VERSION or version.startswith(WANTED_VERSION + ".")


def _default_run(cmd: list[str], cwd: Path | None = None, timeout: int | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def classify_private_assets(repo_root: Path, is_file: IsFile | None = None) -> dict[str, Any]:
    is_file = is_file or (lambda p: Path(p).is_file())
    original = Path(repo_root) / "00_original" / "Mutagenic.exe"
    key = Path(repo_root) / "manifests" / "script_key.txt"
    original_ok = is_file(original)
    key_ok = is_file(key)
    if original_ok and key_ok:
        status = "PRESENT"
    else:
        status = "MISSING_PRIVATE"
    return {
        "status": status,
        "original_exe": original_ok,
        "script_key": key_ok,
        "note": "Private assets are independent of Godot 4.7.1 discovery; missing private is not engine SUCCESS.",
    }


def _record_candidate(source: str, name: str | None, present: bool) -> dict[str, Any]:
    rec: dict[str, Any] = {"resolved_via": source, "present": present}
    if name:
        rec["name"] = name
    return rec


def probe_version(binary: Path, run: RunFn | None = None) -> dict[str, Any]:
    run = run or (lambda cmd: _default_run(cmd))
    try:
        proc = run([str(binary), "--version"])
    except OSError as exc:
        return {
            "status": "TOOL_FAILED",
            "version": None,
            "detail": str(exc),
            "stdout": "",
            "stderr": "",
            "returncode": None,
        }
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    version = parse_godot_version(combined)
    if proc.returncode not in (0, None) and not version:
        return {
            "status": "TOOL_FAILED",
            "version": None,
            "detail": f"--version exit {proc.returncode}",
            "stdout": proc.stdout or "",
            "stderr": proc.stderr or "",
            "returncode": proc.returncode,
        }
    if version_is_wanted(version):
        status = "SUCCESS"
        detail = ""
    elif version:
        status = "VERSION_MISMATCH"
        detail = f"found {version}, want {WANTED_VERSION}"
    else:
        status = "TOOL_FAILED"
        detail = "could not parse Godot version from --version output"
    return {
        "status": status,
        "version": version,
        "detail": detail,
        "stdout": proc.stdout or "",
        "stderr": proc.stderr or "",
        "returncode": proc.returncode,
    }


def discover_product_godot(
    repo_root: Path,
    environ: Mapping[str, str] | None = None,
    which: WhichFn | None = None,
    is_file: IsFile | None = None,
    run: RunFn | None = None,
) -> dict[str, Any]:
    """Return a machine-readable discovery result. Never uses status PASS."""
    repo_root = Path(repo_root)
    environ = dict(os.environ if environ is None else environ)
    which = which or shutil.which
    is_file = is_file or (lambda p: Path(p).is_file())
    tried: list[dict[str, Any]] = []
    binary: Path | None = None
    resolved_via: str | None = None

    for ev in ENV_VARS:
        raw = (environ.get(ev) or "").strip()
        if not raw:
            tried.append(_record_candidate("ENV", ev, False))
            continue
        cand = Path(raw)
        present = is_file(cand)
        tried.append(_record_candidate("ENV", ev, present))
        if present and binary is None:
            binary = cand
            resolved_via = f"ENV:{ev}"

    for rel in REPO_RELATIVE_CANDIDATES:
        cand = repo_root / rel
        present = is_file(cand)
        tried.append(_record_candidate("REPO_RELATIVE", rel, present))
        if present and binary is None:
            binary = cand
            resolved_via = "REPO_RELATIVE"

    for name in WHICH_NAMES:
        found = which(name)
        present = bool(found) and is_file(Path(found))
        tried.append(_record_candidate("PATH", name, present))
        if present and binary is None:
            binary = Path(found)  # type: ignore[arg-type]
            resolved_via = "PATH"

    private = classify_private_assets(repo_root, is_file=is_file)
    engine: dict[str, Any] = {
        "wanted": WANTED_VERSION,
        "status": "NOT_FOUND",
        "tool_missing": True,
        "binary_present": False,
        "binary": None,
        "binary_name": None,
        "resolved_via": None,
        "version": None,
        "detail": "Godot 4.7.1 not found on PATH, MUTAGENIC_GODOT_4/GODOT4/GODOT_BIN, or repo-relative 02_tools/godot/",
        "tried": tried,
    }

    if binary is None:
        overall = "NOT_FOUND"
        result = {
            "schema_version": 1,
            "task": "P1-X2",
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "engine": engine,
            "private_assets": private,
            "overall": overall,
        }
        return result

    # Record identity without baking a host drive into committed reports: callers
    # that persist into the repo should strip binary. Runtime JSON may include it.
    probed = probe_version(binary, run=run)
    engine.update({
        "tool_missing": False,
        "binary_present": True,
        "binary": str(binary),
        "binary_name": binary.name,
        "resolved_via": resolved_via,
        "version": probed.get("version"),
        "status": probed["status"],
        "detail": probed.get("detail") or "",
        "version_stdout": probed.get("stdout", "")[:500],
    })
    overall = probed["status"]
    if overall == "SUCCESS" and not engine["binary_present"]:
        overall = "TOOL_FAILED"
        engine["status"] = "TOOL_FAILED"
        engine["detail"] = "SUCCESS claimed without a binary"
    return {
        "schema_version": 1,
        "task": "P1-X2",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "engine": engine,
        "private_assets": private,
        "overall": overall,
    }


def sanitize_for_commit(result: dict[str, Any]) -> dict[str, Any]:
    """Drop host-absolute binary paths from a copy destined for the git tree."""
    clone = json.loads(json.dumps(result))
    engine = clone.get("engine") or {}
    binary = engine.get("binary")
    if binary:
        engine["binary"] = engine.get("binary_name")
        engine["binary_host_path_omitted"] = True
    clone["engine"] = engine
    return clone


def run_headless_import(
    binary: str | Path,
    product_dir: Path,
    run: RunFn | None = None,
) -> dict[str, Any]:
    run = run or (lambda cmd: _default_run(cmd, timeout=600))
    product_dir = Path(product_dir)
    cmd = [str(binary), "--headless", "--path", str(product_dir), "--import", "--quit"]
    try:
        proc = run(cmd)
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "TOOL_FAILED",
            "returncode": None,
            "stdout": (exc.stdout or "") if isinstance(exc.stdout, str) else "",
            "stderr": "timeout after 600s",
            "cmd_name": Path(str(binary)).name,
        }
    except OSError as exc:
        return {
            "status": "TOOL_FAILED",
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "cmd_name": Path(str(binary)).name,
        }
    return {
        "status": "RAN",
        "returncode": proc.returncode,
        "stdout": proc.stdout or "",
        "stderr": proc.stderr or "",
        "cmd_name": Path(str(binary)).name,
    }


def _repo_root_from_here() -> Path:
    here = Path(__file__).resolve()
    sys.path.insert(0, str(here.parent.parent / "env"))
    from dev_environment import find_repo_root  # type: ignore
    return find_repo_root(here)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--json", dest="json_out", nargs="?", const="-", metavar="PATH",
                    help="write JSON to PATH, or stdout if PATH omitted / '-'")
    ap.add_argument("--out", type=Path, default=None, help="write JSON report to PATH")
    ap.add_argument("--import-parse", action="store_true")
    ap.add_argument("--product", type=Path, default=None)
    ap.add_argument("--sanitize", action="store_true", help="omit host binary paths from JSON")
    args = ap.parse_args(argv)

    if args.root:
        root = args.root.resolve()
    else:
        try:
            root = _repo_root_from_here()
        except Exception:
            root = Path(__file__).resolve().parents[2]

    result = discover_product_godot(root)
    if args.import_parse:
        engine = result["engine"]
        product = (args.product or (root / "product")).resolve()
        if engine.get("status") == "SUCCESS" and engine.get("binary"):
            result["import_parse"] = run_headless_import(engine["binary"], product)
        else:
            result["import_parse"] = {
                "status": "NOT_RUN",
                "reason": engine.get("status") or "NOT_FOUND",
                "tool_missing": bool(engine.get("tool_missing")),
            }

    payload = sanitize_for_commit(result) if args.sanitize else result
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"

    out_path: Path | None = args.out
    if args.json_out and args.json_out not in {"-", ""}:
        out_path = Path(args.json_out)
    if out_path:
        if not out_path.is_absolute():
            out_path = (Path.cwd() / out_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")

    if args.json_out == "-" or (args.json_out is not None and not out_path) or (args.json_out is None and args.out is None):
        sys.stdout.write(text)

    overall = result.get("overall")
    # Honest NOT_FOUND is a successful discovery run. Fake PASS is a failure.
    if overall == "PASS":
        return 1
    if overall in {"SUCCESS", "NOT_FOUND", "MISSING_PRIVATE"}:
        return 0
    if overall in {"VERSION_MISMATCH", "TOOL_FAILED"}:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
