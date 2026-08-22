#!/usr/bin/env python3
"""P1-V0: Product Godot 4.7.1 headless boot probe.

Resolves the engine exactly like product_toolchain.discover_product_godot
(PATH, MUTAGENIC_GODOT_4 / GODOT4 / GODOT_BIN, repo-relative 02_tools/godot/*
— never host-drive literals in source), then runs:

    <godot> --headless --path product --quit-after N

Statuses (never PASS):
  BOOTED              returncode==0 and no "SCRIPT ERROR" in output
  BOOTED_WITH_ERRORS  returncode==0 but "SCRIPT ERROR" present in output
  CRASHED             returncode != 0
  NOT_FOUND           engine binary missing (alias: tool_missing=true)
  TOOL_FAILED         probe could not run; includes TIMEOUT (detail=TIMEOUT)

Exit codes: BOOTED / NOT_FOUND -> 0, everything else -> 1.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

DEFAULT_QUIT_AFTER = 600
DEFAULT_TIMEOUT_S = 120
MAX_ERROR_LINES = 500
ERROR_CLASSES = ("missing_asset", "class_resolve", "load_fail", "api_member")
SCRIPT_ERROR_RE = re.compile(r"SCRIPT\s+ERROR", re.IGNORECASE)
ERROR_LINE_RE = re.compile(r"(?:script\s+error|error|parse\s+error)", re.IGNORECASE)
ERROR_CLASS_RES: dict[str, re.Pattern[str]] = {
    "missing_asset": re.compile(
        r"preload|failed loading resource|cannot open file|file not found", re.IGNORECASE
    ),
    "class_resolve": re.compile(r"could not resolve class", re.IGNORECASE),
    "load_fail": re.compile(r"failed to load script", re.IGNORECASE),
    "api_member": re.compile(r"cannot find member|not declared", re.IGNORECASE),
}

ENV_VARS = ("MUTAGENIC_GODOT_4", "GODOT4", "GODOT_BIN")
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

EXIT_CODES: dict[str, int] = {
    "BOOTED": 0,
    "NOT_FOUND": 0,
    "BOOTED_WITH_ERRORS": 1,
    "CRASHED": 1,
    "TOOL_FAILED": 1,
}

RunFn = Callable[..., subprocess.CompletedProcess]
ClockFn = Callable[[], float]
IsFile = Callable[[Path], bool]
WhichFn = Callable[[str], str | None]

try:
    from product_toolchain import discover_product_godot as _toolchain_discover  # type: ignore
except Exception:
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from product_toolchain import discover_product_godot as _toolchain_discover  # type: ignore
    except Exception:
        _toolchain_discover = None  # type: ignore[assignment]


def _default_run(cmd: list[str], timeout: int | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def sanitize_cmd(cmd: list[str], repo_root: Path) -> list[str]:
    """Mask host paths: repo paths -> <repo>/rel, foreign absolutes -> basename.

    Non-path args (flags like --headless, numbers) pass through untouched.
    """
    repo = Path(repo_root).resolve()
    out: list[str] = []
    for raw in cmd:
        arg = str(raw)
        p = Path(arg)
        if not p.is_absolute():
            out.append(arg)
            continue
        try:
            rel = p.resolve().relative_to(repo)
            out.append("<repo>/" + rel.as_posix())
        except Exception:
            out.append(p.name)
    return out


def empty_error_class_counts() -> dict[str, int]:
    return {**{cls: 0 for cls in ERROR_CLASSES}, "other": 0}


def classify_error_line(line: str) -> str:
    for cls, pattern in ERROR_CLASS_RES.items():
        if pattern.search(line):
            return cls
    return "other"


def classify_error_lines(lines: list[str]) -> dict[str, int]:
    counts = empty_error_class_counts()
    for ln in lines:
        counts[classify_error_line(ln)] += 1
    return counts


def analyze_output(
    stdout: str, stderr: str, max_error_lines: int = MAX_ERROR_LINES
) -> dict[str, Any]:
    lines = [ln for ln in stdout.splitlines()] + [ln for ln in stderr.splitlines()]
    script_error_count = sum(1 for ln in lines if SCRIPT_ERROR_RE.search(ln))
    error_lines = [ln.strip() for ln in lines if ERROR_LINE_RE.search(ln)]
    limit = max(0, int(max_error_lines))
    return {
        "script_error_count": script_error_count,
        "script_errors_by_class": classify_error_lines(error_lines),
        "error_lines": error_lines[:limit],
        "error_lines_truncated": len(error_lines) > limit,
    }


def classify_boot(returncode: int | None, script_error_count: int) -> str:
    if returncode == 0 and script_error_count == 0:
        return "BOOTED"
    if returncode == 0:
        return "BOOTED_WITH_ERRORS"
    return "CRASHED"


def run_boot_probe(
    binary: str | Path,
    product_dir: Path,
    quit_after: int = DEFAULT_QUIT_AFTER,
    timeout_s: int = DEFAULT_TIMEOUT_S,
    max_error_lines: int = MAX_ERROR_LINES,
    run: RunFn | None = None,
    clock: ClockFn | None = None,
) -> dict[str, Any]:
    """Run `<godot> --headless --path product --quit-after N` once, classified."""
    run = run or _default_run
    clock = clock or time.monotonic
    cmd = [
        str(binary),
        "--headless",
        "--path",
        str(product_dir),
        "--quit-after",
        str(int(quit_after)),
    ]
    started = clock()
    try:
        proc = run(cmd, timeout=timeout_s)
    except subprocess.TimeoutExpired as exc:
        duration_ms = int((clock() - started) * 1000)
        return {
            "status": "TOOL_FAILED",
            "detail": f"TIMEOUT after {timeout_s}s",
            "timed_out": True,
            "returncode": None,
            "stdout": _as_text(exc.stdout),
            "stderr": _as_text(exc.stderr) or "timeout",
            "duration_ms": duration_ms,
            "cmd": cmd,
        }
    except OSError as exc:
        duration_ms = int((clock() - started) * 1000)
        return {
            "status": "TOOL_FAILED",
            "detail": str(exc),
            "timed_out": False,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "duration_ms": duration_ms,
            "cmd": cmd,
        }
    duration_ms = int((clock() - started) * 1000)
    stdout = _as_text(proc.stdout)
    stderr = _as_text(proc.stderr)
    analysis = analyze_output(stdout, stderr, max_error_lines=max_error_lines)
    status = classify_boot(proc.returncode, analysis["script_error_count"])
    return {
        "status": status,
        "detail": "",
        "timed_out": False,
        "returncode": proc.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "duration_ms": duration_ms,
        "cmd": cmd,
        **analysis,
    }


def _discover_fallback(
    repo_root: Path,
    environ: Mapping[str, str],
    which: WhichFn,
    is_file: IsFile,
) -> dict[str, Any]:
    """Minimal discovery used only when product_toolchain is not importable.

    Order: PATH -> MUTAGENIC_GODOT_4/GODOT4/GODOT_BIN -> repo-relative
    02_tools/godot/*.
    """
    tried: list[dict[str, Any]] = []
    checks: list[tuple[str, str, Path | None]] = []
    for name in WHICH_NAMES:
        found = which(name)
        checks.append(("PATH", name, Path(found) if found else None))
    for ev in ENV_VARS:
        raw = (environ.get(ev) or "").strip()
        checks.append(("ENV", ev, Path(raw) if raw else None))
    for rel in REPO_RELATIVE_CANDIDATES:
        checks.append(("REPO_RELATIVE", rel, Path(repo_root) / rel))

    for source, name, cand in checks:
        present = cand is not None and is_file(cand)
        rec: dict[str, Any] = {"resolved_via": source, "name": name, "present": present}
        tried.append(rec)
        if present:
            return {
                "found": True,
                "binary": str(cand),
                "binary_name": cand.name,
                "resolved_via": f"{source}:{name}" if source != "REPO_RELATIVE" else "REPO_RELATIVE",
                "version": None,
                "tool_status": "UNKNOWN",
                "tried": tried,
            }
    return {
        "found": False,
        "binary": None,
        "binary_name": None,
        "resolved_via": None,
        "version": None,
        "tool_status": "NOT_FOUND",
        "tried": tried,
    }


def resolve_engine(
    repo_root: Path,
    environ: Mapping[str, str] | None = None,
    which: WhichFn | None = None,
    is_file: IsFile | None = None,
    run: RunFn | None = None,
) -> dict[str, Any]:
    """Normalized engine discovery; delegates to product_toolchain when importable."""
    repo_root = Path(repo_root)
    environ = dict(os.environ if environ is None else environ)
    which = which or shutil.which
    is_file = is_file or (lambda p: Path(p).is_file())
    if _toolchain_discover is not None:
        try:
            result = _toolchain_discover(repo_root, environ=environ, which=which, is_file=is_file, run=run)
            engine = result.get("engine") or {}
            binary = engine.get("binary")
            return {
                "found": bool(engine.get("binary_present")) and bool(binary),
                "binary": str(binary) if binary else None,
                "binary_name": engine.get("binary_name"),
                "resolved_via": engine.get("resolved_via"),
                "version": engine.get("version"),
                "tool_status": engine.get("status"),
                "tried": engine.get("tried"),
            }
        except Exception as exc:
            fallback_note = f"product_toolchain delegation failed: {exc}"
    else:
        fallback_note = "product_toolchain not importable; using minimal fallback"
    discovered = _discover_fallback(repo_root, environ, which, is_file)
    discovered["fallback_note"] = fallback_note
    return discovered


def gather_report(
    root: Path,
    product_dir: Path | None = None,
    quit_after: int = DEFAULT_QUIT_AFTER,
    timeout_s: int = DEFAULT_TIMEOUT_S,
    max_error_lines: int = MAX_ERROR_LINES,
    environ: Mapping[str, str] | None = None,
    which: WhichFn | None = None,
    is_file: IsFile | None = None,
    run: RunFn | None = None,
    clock: ClockFn | None = None,
) -> dict[str, Any]:
    root = Path(root)
    product = Path(product_dir) if product_dir else root / "product"
    engine = resolve_engine(root, environ=environ, which=which, is_file=is_file, run=run)
    if not engine["found"]:
        boot: dict[str, Any] = {
            "status": "NOT_FOUND",
            "detail": "Godot binary not found; boot not attempted",
            "timed_out": False,
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "duration_ms": None,
            "cmd": [],
            "script_error_count": 0,
            "script_errors_by_class": empty_error_class_counts(),
            "error_lines": [],
            "error_lines_truncated": False,
        }
    else:
        boot = run_boot_probe(
            engine["binary"],
            product,
            quit_after=quit_after,
            timeout_s=timeout_s,
            max_error_lines=max_error_lines,
            run=run,
            clock=clock,
        )
    report = {
        "schema_version": 1,
        "task": "P1-V0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "engine": {
            "binary_name": engine["binary_name"],
            "resolved_via": engine["resolved_via"],
            "version": engine["version"],
            "status": engine["tool_status"],
            "tool_missing": not engine["found"],
            "discovery_note": engine.get("fallback_note") or "",
        },
        "boot": {
            "status": boot["status"],
            "detail": boot.get("detail") or "",
            "returncode": boot["returncode"],
            "timed_out": boot["timed_out"],
            "script_error_count": boot.get("script_error_count", 0),
            "script_errors_by_class": boot.get("script_errors_by_class") or empty_error_class_counts(),
            "error_lines": boot.get("error_lines", []),
            "error_lines_truncated": boot.get("error_lines_truncated", False),
            "max_error_lines": int(max_error_lines),
            "duration_ms": boot["duration_ms"],
            "quit_after": int(quit_after),
            "timeout_s": int(timeout_s),
            "product_dir": "<repo>/product" if product == root / "product" else product.name,
            "cmd": sanitize_cmd(boot["cmd"], root),
        },
        "overall": boot["status"],
    }
    for key in ("stdout", "stderr"):
        text = boot.get(key) or ""
        report["boot"][key + "_head"] = text[:2000]
    return report


def summarize(report: dict[str, Any]) -> str:
    boot = report["boot"]
    engine = report["engine"]
    return (
        f"P1-V0 boot={boot['status']}"
        f" rc={boot['returncode']}"
        f" script_errors={boot['script_error_count']}"
        f" duration_ms={boot['duration_ms']}"
        f" binary={engine['binary_name']}"
        f" via={engine['resolved_via']}"
        f" detail={boot['detail'] or '-'}"
    )


def exit_code_for(report: dict[str, Any]) -> int:
    return EXIT_CODES.get(report.get("overall"), 1)


def _repo_root_from_here() -> Path:
    try:
        here = Path(__file__).resolve()
        sys.path.insert(0, str(here.parent.parent / "env"))
        from dev_environment import find_repo_root  # type: ignore
        return find_repo_root(here)
    except Exception:
        return Path(__file__).resolve().parents[2]


def main(
    argv: list[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    which: WhichFn | None = None,
    is_file: IsFile | None = None,
    run: RunFn | None = None,
    clock: ClockFn | None = None,
) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None, help="repo root (default: auto-detect)")
    ap.add_argument("--product", type=Path, default=None, help="product dir (default: <root>/product)")
    ap.add_argument("--quit-after", dest="quit_after", type=int, default=DEFAULT_QUIT_AFTER)
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S, help="subprocess timeout seconds")
    ap.add_argument(
        "--max-error-lines",
        dest="max_error_lines",
        type=int,
        default=MAX_ERROR_LINES,
        help="max captured error lines kept in report (default: %(default)s)",
    )
    ap.add_argument("--out", type=Path, default=None, help="write JSON report to PATH")
    ap.add_argument("--json", action="store_true", help="also print full JSON to stdout")
    args = ap.parse_args(argv)

    root = args.root.resolve() if args.root else _repo_root_from_here()
    product = args.product.resolve() if args.product else None
    report = gather_report(
        root,
        product_dir=product,
        quit_after=args.quit_after,
        timeout_s=args.timeout,
        max_error_lines=args.max_error_lines,
        environ=environ,
        which=which,
        is_file=is_file,
        run=run,
        clock=clock,
    )
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"

    if args.out:
        out_path = args.out if args.out.is_absolute() else (Path.cwd() / args.out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")

    if args.json:
        sys.stdout.write(text)
    print(summarize(report))
    return exit_code_for(report)


if __name__ == "__main__":
    raise SystemExit(main())
