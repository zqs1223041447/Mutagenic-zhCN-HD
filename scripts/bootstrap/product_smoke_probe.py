#!/usr/bin/env python3
"""P2-A2: Product smoke-scene hop probe (headless LoadGame -> Menu -> TestLevel).

Each hop performs ONE real engine launch using Godot 4's positional scene
argument (autoloads register exactly like a normal boot; no --script harness):

    <godot> --headless --path <product> "res://scenes/X.tscn"

The probe lets the process dwell for --dwell-seconds, then terminates it via
the subprocess timeout kill. Surviving the full dwell window is the EXPECTED
outcome for a healthy scene (games idle forever), so that outcome is reported
as TIMEOUT = "arrived, needs manual confirmation" and is NOT a tool failure.

Reach rules (no in-game markers; judged from lifecycle + error features):
  REACHED      exited on its own within the dwell window with rc==0 and no
               fatal error signature in stdout/stderr
  TIMEOUT      survived until the dwell window elapsed and was killed as
               planned; counted as arrived but flagged needs_manual_confirm
  NOT_REACHED  early exit with rc != 0, or rc == 0 with a fatal signature
               (SCRIPT ERROR / failed scene-or-resource load / crash words)
  SPAWN_FAILED engine could not be launched (OSError)

Every hop collects the SCRIPT ERROR lines of its own process; a line already
produced by an earlier hop does not count as "new" (new = delta against all
previous hops of this run). Scene-load evidence lines (.tscn references,
loading-resource chatter, occurrences of the hop scene path) are recorded per
hop under "scene_evidence"; "loaded_scene" echoes the hop scene only when its
path literally appears in the engine output.

Hop statuses: REACHED / NOT_REACHED / TIMEOUT / SPAWN_FAILED.
Overall statuses (never PASS-tool-failure mix):
  SMOKE_PASS    every hop reached its target scene (TIMEOUT arrivals included)
  SMOKE_PARTIAL some (but not all) hops reached their target scene
  SMOKE_FAIL    engine ran but no hop reached its target scene
  NOT_FOUND     engine binary missing (alias: engine.tool_missing=true)
  TOOL_FAILED   probe infrastructure failure only: spawn OSError or empty
                scene chain

Exit codes: SMOKE_PASS / NOT_FOUND -> 0, everything else -> 1.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

try:
    from product_boot_probe import resolve_engine, sanitize_cmd  # type: ignore
    from product_boot_probe import SCRIPT_ERROR_RE  # type: ignore
except Exception:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from product_boot_probe import resolve_engine, sanitize_cmd, SCRIPT_ERROR_RE  # type: ignore

TASK_ID = "P2-A2"
SCHEMA_VERSION = 1
DEFAULT_SCENES: tuple[str, ...] = (
    "res://scenes/LoadGame.tscn",
    "res://scenes/Menu.tscn",
    "res://scenes/Levels/TestLevel/TestLevel.tscn",
)
DEFAULT_TIMEOUT_PER_HOP_S = 20
DEFAULT_DWELL_SECONDS = 5.0
MAX_SAMPLE_LINES = 10
MAX_EVIDENCE_LINES = 20

HOP_REACHED = "REACHED"
HOP_NOT_REACHED = "NOT_REACHED"
HOP_TIMEOUT = "TIMEOUT"
HOP_SPAWN_FAILED = "SPAWN_FAILED"

OVERALL_PASS = "SMOKE_PASS"
OVERALL_PARTIAL = "SMOKE_PARTIAL"
OVERALL_FAIL = "SMOKE_FAIL"
OVERALL_NOT_FOUND = "NOT_FOUND"
OVERALL_TOOL_FAILED = "TOOL_FAILED"

EXIT_CODES: dict[str, int] = {
    OVERALL_PASS: 0,
    OVERALL_NOT_FOUND: 0,
    OVERALL_PARTIAL: 1,
    OVERALL_FAIL: 1,
    OVERALL_TOOL_FAILED: 1,
}

FATAL_SIGNATURE_RES: tuple[re.Pattern[str], ...] = (
    SCRIPT_ERROR_RE,
    re.compile(r"\bfatal\b", re.IGNORECASE),
    re.compile(r"segmentation fault|access violation|general protection fault", re.IGNORECASE),
    re.compile(r"assertion failed|handle[_ ]crash", re.IGNORECASE),
    re.compile(
        r"no loader found|failed (?:loading|to load) (?:scene|resource)"
        r"|can'?t (?:load|open)|couldn'?t (?:load|open)",
        re.IGNORECASE,
    ),
    re.compile(r"cannot open file|file not found", re.IGNORECASE),
)

SCENE_EVIDENCE_RE = re.compile(
    r"\.tscn|loading (?:scene|resource)|loaded (?:scene|resource)"
    r"|scene_file_path|current scene|main scene",
    re.IGNORECASE,
)

RunFn = Callable[..., Any]
ClockFn = Callable[[], float]


def _repo_root_from_here() -> Path:
    try:
        here = Path(__file__).resolve()
        sys.path.insert(0, str(here.parent.parent / "env"))
        from dev_environment import find_repo_root  # type: ignore
        return find_repo_root(here)
    except Exception:
        return Path(__file__).resolve().parents[2]


def _default_run(cmd: list[str], timeout: int | None = None) -> Any:
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


def expand_scenes(values: Iterable[str] | None) -> list[str]:
    """Accept repeated flags and/or comma-separated scene lists; drop empties."""
    out: list[str] = []
    for item in values or ():
        for piece in str(item).split(","):
            piece = piece.strip()
            if piece:
                out.append(piece)
    return out


def extract_script_error_lines(stdout: str, stderr: str) -> list[str]:
    lines = list(stdout.splitlines()) + list(stderr.splitlines())
    return [ln for ln in lines if SCRIPT_ERROR_RE.search(ln)]


def normalize_error_line(line: str) -> str:
    return " ".join(line.split())


def diff_new_error_lines(lines: list[str], seen: set[str]) -> list[str]:
    """Return lines not seen in earlier hops; register every occurrence."""
    new: list[str] = []
    for ln in lines:
        if normalize_error_line(ln) in seen:
            continue
        new.append(ln)
    for ln in lines:
        seen.add(normalize_error_line(ln))
    return new


BENIGN_ERROR_RES: tuple[re.Pattern[str], ...] = (
    re.compile(r"Preload file .*does not exist|has no resource loaders", re.IGNORECASE),
    re.compile(r"Failed loading resource|Resource file not found", re.IGNORECASE),
    re.compile(r"cannot open file|file not found", re.IGNORECASE),
    re.compile(r"Could not resolve (?:class|super class|external class member)", re.IGNORECASE),
    re.compile(r"Failed to load script|Failed to create an autoload", re.IGNORECASE),
    re.compile(r"\.aseprite", re.IGNORECASE),
)


def has_fatal_signature(stdout: str, stderr: str) -> bool:
    lines = list(stdout.splitlines()) + list(stderr.splitlines())
    hard_res = FATAL_SIGNATURE_RES[1:]
    for ln in lines:
        if any(p.search(ln) for p in BENIGN_ERROR_RES):
            continue
        if any(p.search(ln) for p in hard_res) or SCRIPT_ERROR_RE.search(ln):
            return True
    return False


def collect_scene_evidence(
    stdout: str,
    stderr: str,
    scene: str,
    limit: int = MAX_EVIDENCE_LINES,
) -> list[str]:
    lines = [ln.strip() for ln in list(stdout.splitlines()) + list(stderr.splitlines())]
    picked = [ln for ln in lines if ln and (SCENE_EVIDENCE_RE.search(ln) or scene in ln)]
    return picked[: max(0, int(limit))]


def derive_loaded_scene(stdout: str, stderr: str, scene: str) -> str | None:
    combined = stdout + "\n" + stderr
    return scene if scene in combined else None


def effective_run_timeout_s(dwell_seconds: float, timeout_per_hop_s: int) -> float:
    """Kill point per hop: dwell seconds, clamped to the hard cap (min 1s)."""
    return max(1.0, min(float(dwell_seconds), float(int(timeout_per_hop_s))))


def run_hop(
    binary: str | Path,
    product_dir: Path,
    scene: str,
    *,
    timeout_per_hop_s: int = DEFAULT_TIMEOUT_PER_HOP_S,
    dwell_seconds: float = DEFAULT_DWELL_SECONDS,
    run: RunFn | None = None,
    clock: ClockFn | None = None,
) -> dict[str, Any]:
    run = run or _default_run
    clock = clock or time.monotonic
    cmd = [
        str(binary),
        "--headless",
        "--path",
        str(product_dir),
        scene,
    ]
    run_timeout = effective_run_timeout_s(dwell_seconds, timeout_per_hop_s)
    started = clock()
    timed_out = False
    detail = ""
    returncode: int | None = None
    reached: bool | None = None
    try:
        proc = run(cmd, timeout=run_timeout)
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout_text = _as_text(exc.stdout)
        stderr_text = _as_text(exc.stderr)
        if has_fatal_signature(stdout_text, stderr_text):
            status = HOP_NOT_REACHED
            reached = False
            detail = "dwell window elapsed but fatal signature in output; arrival denied"
        else:
            status = HOP_TIMEOUT
            reached = True
            detail = (
                "dwell %.1fs elapsed; process terminated as planned; "
                "arrival presumed - manual confirmation advised" % run_timeout
            )
    except OSError as exc:
        status = HOP_SPAWN_FAILED
        detail = str(exc)
        stdout_text = ""
        stderr_text = str(exc)
    else:
        stdout_text = _as_text(getattr(proc, "stdout", ""))
        stderr_text = _as_text(getattr(proc, "stderr", ""))
        returncode = getattr(proc, "returncode", None)
        if has_fatal_signature(stdout_text, stderr_text):
            status = HOP_NOT_REACHED
            reached = False
            detail = "fatal signature in output (rc=%s)" % returncode
        elif returncode == 0:
            status = HOP_REACHED
            reached = True
            detail = "clean exit within dwell window"
        else:
            status = HOP_NOT_REACHED
            reached = False
            detail = "early exit rc=%s; fatal crash suspected" % returncode
    duration_ms = int((clock() - started) * 1000)
    return {
        "scene": scene,
        "status": status,
        "detail": detail,
        "timed_out": timed_out,
        "reached": reached,
        "returncode": returncode,
        "stdout": stdout_text,
        "stderr": stderr_text,
        "duration_ms": duration_ms,
        "cmd": cmd,
        "script_error_lines": extract_script_error_lines(stdout_text, stderr_text),
        "scene_evidence": collect_scene_evidence(stdout_text, stderr_text, scene),
        "loaded_scene": derive_loaded_scene(stdout_text, stderr_text, scene),
    }


def classify_overall(hops: list[dict[str, Any]]) -> str:
    if not hops:
        return OVERALL_TOOL_FAILED
    if any(h.get("status") == HOP_SPAWN_FAILED for h in hops):
        return OVERALL_TOOL_FAILED
    reached = [bool(h.get("reached")) for h in hops]
    if all(reached):
        return OVERALL_PASS
    if any(reached):
        return OVERALL_PARTIAL
    return OVERALL_FAIL


def gather_report(
    root: Path,
    product_dir: Path | None = None,
    scenes: Iterable[str] | None = None,
    *,
    timeout_per_hop_s: int = DEFAULT_TIMEOUT_PER_HOP_S,
    dwell_seconds: float = DEFAULT_DWELL_SECONDS,
    max_sample_lines: int = MAX_SAMPLE_LINES,
    environ: Mapping[str, str] | None = None,
    which: Callable[[str], str | None] | None = None,
    is_file: Callable[[Path], bool] | None = None,
    run: RunFn | None = None,
    clock: ClockFn | None = None,
) -> dict[str, Any]:
    root = Path(root)
    product = Path(product_dir) if product_dir else root / "product"
    chain = expand_scenes(DEFAULT_SCENES if scenes is None else scenes)
    engine = resolve_engine(root, environ=environ, which=which, is_file=is_file, run=run)
    engine_block = {
        "binary_name": engine["binary_name"],
        "resolved_via": engine["resolved_via"],
        "version": engine["version"],
        "status": engine["tool_status"],
        "tool_missing": not engine["found"],
        "discovery_note": engine.get("fallback_note") or "",
    }
    hops: list[dict[str, Any]] = []
    note = ""
    overall: str | None = None
    if not engine["found"]:
        overall = OVERALL_NOT_FOUND
        note = "Godot binary not found; smoke hops not attempted"
    elif not chain:
        overall = OVERALL_TOOL_FAILED
        note = "empty scene chain; nothing to probe"
    else:
        seen: set[str] = set()
        for index, scene in enumerate(chain):
            raw = run_hop(
                engine["binary"],
                product,
                scene,
                timeout_per_hop_s=timeout_per_hop_s,
                dwell_seconds=dwell_seconds,
                run=run,
                clock=clock,
            )
            new_lines = diff_new_error_lines(
                raw.get("script_error_lines") or [], seen
            )
            limit = max(0, int(max_sample_lines))
            hops.append({
                "index": index,
                "scene": raw["scene"],
                "status": raw["status"],
                "detail": raw.get("detail", ""),
                "reached": raw["reached"],
                "change_rc": None,
                "loaded_scene": raw.get("loaded_scene"),
                "new_script_errors": len(new_lines),
                "script_errors_total": len(raw.get("script_error_lines") or []),
                "sample_lines": [ln.strip() for ln in new_lines][:limit],
                "returncode": raw["returncode"],
                "timed_out": raw["timed_out"],
                "needs_manual_confirm": raw["status"] == HOP_TIMEOUT,
                "duration_ms": raw["duration_ms"],
                "cmd": sanitize_cmd(raw["cmd"], root),
                "stdout_head": (raw.get("stdout") or "")[:2000],
                "stderr_head": (raw.get("stderr") or "")[:2000],
                "scene_evidence": raw.get("scene_evidence") or [],
            })
    if overall is None:
        overall = classify_overall(hops)
    kills = sum(1 for h in hops if h.get("timed_out"))
    if kills and not note:
        note = (
            "%d/%d hop(s) ended by dwell kill (planned); arrival presumed - "
            "manual confirmation advised" % (kills, len(hops))
        )
    report = {
        "schema_version": SCHEMA_VERSION,
        "task": TASK_ID,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "engine": engine_block,
        "config": {
            "scenes": chain,
            "timeout_per_hop_s": int(timeout_per_hop_s),
            "dwell_seconds": float(dwell_seconds),
            "max_sample_lines": int(max_sample_lines),
            "product_dir": "<repo>/product" if product == root / "product" else product.name,
        },
        "hops": hops,
        "reached_count": sum(1 for h in hops if h.get("reached") is True),
        "total_hops": len(chain),
        "overall": overall,
    }
    if note:
        report["note"] = note
    return report


def summarize(report: dict[str, Any]) -> str:
    engine = report["engine"]
    hops = report["hops"]
    new_total = sum(h.get("new_script_errors", 0) for h in hops)
    kills = sum(1 for h in hops if h.get("timed_out"))
    return (
        f"P2-A2 smoke={report['overall']}"
        f" reached={report['reached_count']}/{report['total_hops']}"
        f" dwell_kills={kills}"
        f" new_script_errors={new_total}"
        f" binary={engine['binary_name']}"
        f" via={engine['resolved_via']}"
        f" note={report.get('note') or '-'}"
    )


def exit_code_for(report: dict[str, Any]) -> int:
    return EXIT_CODES.get(report.get("overall"), 1)


def main(
    argv: list[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    which: Callable[[str], str | None] | None = None,
    is_file: Callable[[Path], bool] | None = None,
    run: RunFn | None = None,
    clock: ClockFn | None = None,
) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None, help="repo root (default: auto-detect)")
    ap.add_argument("--product", type=Path, default=None, help="product dir (default: <root>/product)")
    ap.add_argument(
        "--scenes",
        nargs="+",
        metavar="SCENE",
        default=None,
        help="scene chain in visit order; repeatable and/or comma-separated "
             "(default: %s)" % ",".join(DEFAULT_SCENES),
    )
    ap.add_argument(
        "--timeout-per-hop",
        dest="timeout_per_hop",
        type=int,
        default=DEFAULT_TIMEOUT_PER_HOP_S,
        help="hard cap per hop in seconds; the engine is killed at "
             "min(--dwell-seconds, this)",
    )
    ap.add_argument(
        "--dwell-seconds",
        dest="dwell_seconds",
        type=float,
        default=DEFAULT_DWELL_SECONDS,
        help="seconds to let each real launch run before terminating it",
    )
    ap.add_argument("--max-sample-lines", dest="max_sample_lines", type=int, default=MAX_SAMPLE_LINES)
    ap.add_argument("--out", type=Path, default=None, help="write JSON report to PATH")
    ap.add_argument("--json", action="store_true", help="also print full JSON to stdout")
    args = ap.parse_args(argv)

    root = args.root.resolve() if args.root else _repo_root_from_here()
    product = args.product.resolve() if args.product else None
    report = gather_report(
        root,
        product_dir=product,
        scenes=args.scenes,
        timeout_per_hop_s=args.timeout_per_hop,
        dwell_seconds=args.dwell_seconds,
        max_sample_lines=args.max_sample_lines,
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
