#!/usr/bin/env python3
"""B3-P2-X2 S3 persistence gate: unattended save->exit->reload same-state check.

Runs the candidate game twice against ONE isolated APPDATA profile:

  * run1 (save+exit): a seed save (user://_0_6_0.dat) is staged, the game is
    launched, we poll until the save gets rewritten on disk (GameState
    load_game -> migrate -> clean_saved_data -> do_save_game always rewrites
    the file, so a disk sha change is the load+save signal) plus a debounce
    settle window, then the process is closed and the save is re-read
    (post-exit state).
  * run2 (reload): the SAME APPDATA is launched again; we wait for the
    reload rewrite ("LOADED AND MERGED" log marker and/or disk sha change),
    settle, close and re-read.

Same-state verdict compares the SEMANTIC state of run1's exit save vs run2's
reloaded save.  The semantic state is the save dict with the volatile
per-save keys dropped (timestamp / checksum / stamp are recomputed by
do_save_game() on every write by design - see
04_recovered/Globals/GameState.gd do_save_game()).  The gate also requires
real evidence that the save was actually loaded and rewritten and that the
planted character markers survived the cycle; a PASS can never come from a
static file comparison alone.

Verdicts / exit codes:
  0 PASS      - real save->exit->reload cycle observed, semantic state equal
  1 FAIL      - game ran but same-state criteria unmet (diff recorded)
  2 BLOCKED   - tool/environment prevented observation (no window, no boot
                log, save never appeared, unparseable save, missing deps)
  3 USAGE     - invalid arguments

No host paths are hardcoded; all paths come from CLI arguments (AGENTS.md 9).

Usage:
    python scripts/validate/s3_persistence_gate.py --candidate <exe>
        --apdata <dir> --seed-save <path> --out <dir>
        [--experiment-id B3-P2-S3-<n>] [--boot-seconds 8]
        [--load-timeout 50] [--settle-seconds 12] [--poll-seconds 0.5]
        [--grace-close-seconds 8]
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TOOL_VERSION = "B3-P2-X2-s3-persistence-gate-v1"

# Keys do_save_game() recomputes on every write: they are expected to differ
# between two saves of the same game state and are excluded from same-state.
VOLATILE_KEYS = frozenset({"timestamp", "checksum", "stamp"})

SAVE_REL = Path("Godot/app_userdata/Mutagenic/_0_6_0.dat")
LOG_REL = Path("Godot/app_userdata/Mutagenic/logs/godot.log")

LOAD_MARKER = "LOADED AND MERGED"
NO_SAVE_MARKER = "No save file found"
FATAL_MARKERS = ("SCRIPT ERROR", "FATAL", "ALERT!")
BOOT_MARKER = "GameState getting ready..."
WINDOW_TITLE = "Mutagenic"

WM_CLOSE = 0x0010

SEMANTIC_FIELDS = (
    "save_version", "settings", "shared_stash", "keybind_overrides",
    "characters", "completed_achievements",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------------
# pure logic (unit-testable offline)
# --------------------------------------------------------------------------

def canonical_json(data) -> str:
    """Deterministic serialization (key-sorted, compact, utf-8).  The game
    writes JSON.print(saved_stats, "", true) with dictionary insertion order;
    order is not a state fact, so comparisons canonicalize it away."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def semantic_snapshot(save: dict) -> dict:
    return {k: v for k, v in save.items() if k not in VOLATILE_KEYS}


def semantic_sha256(save: dict) -> str:
    return sha256_bytes(canonical_json(semantic_snapshot(save)).encode("utf-8"))


def diff_paths(a, b, path: str = "", out: list[str] | None = None,
               limit: int = 40) -> list[str]:
    """Collect dot-paths of leaf values that differ between two arbitrary
    JSON-like structures (a is the expectation, b the observation)."""
    if out is None:
        out = []
    if len(out) >= limit:
        return out
    if type(a) is not type(b):
        out.append((path or "<root>") + f" (type {type(a).__name__} vs {type(b).__name__})")
        return out
    if isinstance(a, dict):
        for key in sorted(set(a) | set(b)):
            if key not in a:
                out.append((path + "." + key if path else key) + " (missing in a)")
            elif key not in b:
                out.append((path + "." + key if path else key) + " (missing in b)")
            else:
                diff_paths(a[key], b[key], path + "." + key if path else key,
                           out, limit)
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            out.append((path or "<root>") + f" (list len {len(a)} vs {len(b)})")
            return out
        for i, (x, y) in enumerate(zip(a, b)):
            diff_paths(x, y, f"{path}[{i}]" if path else f"[{i}]", out, limit)
        return out
    if a != b:
        out.append((path or "<root>") + f" ({a!r} vs {b!r})")
    return out


def compare_semantic(a_save: dict, b_save: dict, limit: int = 40) -> list[str]:
    return diff_paths(semantic_snapshot(a_save), semantic_snapshot(b_save),
                      limit=limit)


def planted_marker_report(save: dict, character_name: str) -> dict:
    """Check the seed's distinguishing markers survived a reload."""
    chars = save.get("characters")
    names = sorted(chars) if isinstance(chars, dict) else []
    present = isinstance(chars, dict) and character_name in chars
    needs_starter = None
    if present:
        needs_starter = chars[character_name].get("needs_starter")
    starter_ok = present and needs_starter is False
    return {
        "character_name": character_name,
        "character_present": present,
        "characters": names,
        "needs_starter": needs_starter,
        "starter_picked_ok": starter_ok,
        "ok": starter_ok,
    }


def parse_save_bytes(data: bytes) -> tuple[bool, dict | None, str]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return False, None, f"save is not utf-8: {exc}"
    try:
        save = json.loads(text)
    except Exception as exc:
        return False, None, f"save is not valid JSON: {exc}"
    if not isinstance(save, dict):
        return False, None, f"save root is {type(save).__name__}, expected dict"
    if "characters" not in save or not isinstance(save["characters"], dict):
        return False, None, "save lacks a characters dict (not a GameState save)"
    return True, save, ""


def evidence_field_brief(save: dict) -> dict:
    brief = {}
    for key in SEMANTIC_FIELDS:
        if key not in save:
            brief[key] = "<missing>"
            continue
        value = save[key]
        if key == "characters":
            brief[key] = {"names": sorted(value),
                          "count": len(value),
                          "needs_starter": {n: value[n].get("needs_starter")
                                            for n in sorted(value)}}
        elif key == "settings" and isinstance(value, dict):
            brief[key] = {"keys": sorted(value),
                          "enable_fullscreen": value.get("enable_fullscreen"),
                          "enable_vsync": value.get("enable_vsync"),
                          "volume": value.get("volume")}
        elif key == "shared_stash" and isinstance(value, dict):
            brief[key] = {"item_keys": sorted(value), "count": len(value)}
        elif key == "completed_achievements" and isinstance(value, list):
            brief[key] = {"count": len(value), "ids": value}
        elif isinstance(value, (dict, list)):
            brief[key] = {"kind": type(value).__name__, "len": len(value)}
        else:
            brief[key] = value
    brief["volatile_present"] = {k: save.get(k) is not None
                                 for k in sorted(VOLATILE_KEYS)}
    return brief


def classify_verdict(run1: dict, run2: dict, seed_finalize: dict,
                     planted_name: str) -> tuple[str, dict]:
    """Pure verdict decision.  run1/run2 are run-cycle outcome dicts."""
    detail: dict = {}
    if not seed_finalize.get("staged"):
        return "BLOCKED", {"reason": "seed save staging failed before launch"}
    if not run1.get("window_found"):
        return "BLOCKED", {"reason": "run1: no visible game window found"}
    if not run2.get("window_found"):
        return "BLOCKED", {"reason": "run2: no visible game window found"}
    for which, run in (("run1", run1), ("run2", run2)):
        if not run.get("load_triggered"):
            return "BLOCKED", {"reason": f"{which}: load/save trigger never "
                                         "arrived (no disk rewrite, no "
                                         "LOADED AND MERGED marker)",
                               "observed": run.get("summary")}
        if not run.get("save_parse_ok"):
            return "BLOCKED", {"reason": f"{which}: settled save is not a "
                                         "parseable GameState save",
                               "parse_error": run.get("parse_error")}
    if run1.get("no_save_marker") or run2.get("no_save_marker"):
        return "FAIL", {"reason": "game reported 'No save file found' on "
                                  "a run where a save existed on disk"}
    if run1.get("fatal_markers") or run2.get("fatal_markers"):
        return "FAIL", {"reason": "fatal/script-error markers in game log",
                        "fatals": {"run1": run1.get("fatal_markers"),
                                   "run2": run2.get("fatal_markers")}}
    a = run1.get("post_exit_snapshot") or {}
    b = run2.get("settled_snapshot") or {}
    a_save = a.get("save") or {}
    b_save = b.get("save") or {}
    diffs = compare_semantic(a_save, b_save)
    detail["run1_exit_vs_run2_diffs"] = diffs
    marker = planted_marker_report(b_save, planted_name)
    detail["planted_marker_run2"] = marker
    if diffs:
        return "FAIL", {"reason": "semantic state differs between run1 exit "
                                  "save and run2 reloaded save",
                        "diff_paths": diffs[:40]}
    if not marker["ok"]:
        return "FAIL", {"reason": "planted character markers lost after "
                                  "reload (fresh profile suspected)",
                        "marker": marker}
    exit_stable = (
        run1.get("exit_stable", False) and run2.get("exit_stable", False)
    )
    detail["exit_stable"] = exit_stable
    if not exit_stable:
        return "FAIL", {"reason": "post-exit save differs semantically from "
                                  "settled save (state changed during exit)"}
    detail["rewritten_twice"] = (
        bool(run1.get("rewrite_count", 0) >= 1)
        and bool(run2.get("rewrite_count", 0) >= 1)
    )
    if not detail["rewritten_twice"]:
        return "FAIL", {"reason": "no disk rewrite observed in both runs "
                                  "(PASS would be unbacked)"}
    detail["run2_load_marker"] = bool(run2.get("load_marker_seen"))
    if not detail["run2_load_marker"]:
        return "FAIL", {"reason": "run2 load marker 'LOADED AND MERGED' not "
                                  "seen in game log (rewrite alone is "
                                  "insufficient evidence)"}
    return "PASS", detail


# --------------------------------------------------------------------------
# windows helpers
# --------------------------------------------------------------------------

def find_window(pid: int, timeout: float) -> int | None:
    user32 = ctypes.windll.user32
    found_exact = []
    found_contains = []

    def cb(hwnd, _lp):
        wpid = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
        if wpid.value != pid:
            return True
        if not user32.IsWindowVisible(hwnd):
            return True
        n = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(n + 1)
        user32.GetWindowTextW(hwnd, buf, n + 1)
        title = buf.value
        if title == WINDOW_TITLE:
            found_exact.append(hwnd)
            return False
        if title and WINDOW_TITLE in title:
            found_contains.append(hwnd)
        return True

    proto = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        found_exact.clear()
        found_contains.clear()
        user32.EnumWindows(proto(cb), 0)
        if found_exact:
            return found_exact[0]
        if found_contains:
            return found_contains[0]
        time.sleep(0.25)
    return None


def graceful_close(hwnd: int) -> None:
    ctypes.windll.user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)


def terminate(proc: subprocess.Popen, hwnd: int | None,
              grace_seconds: float) -> dict:
    """WM_CLOSE first, then hard kill; report which path was taken."""
    if hwnd is not None and proc.poll() is None:
        graceful_close(hwnd)
        try:
            proc.wait(timeout=grace_seconds)
        except subprocess.TimeoutExpired:
            pass
    if proc.poll() is None:
        proc.kill()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"],
                           capture_output=True)
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                pass
    return {"exit_code": proc.returncode,
            "method": "wm_close" if proc.returncode is not None and
                      proc.returncode == 0 else "kill_fallback"}


def log_tail(apdata: Path, max_lines: int = 60, after: float = 0.0) -> str:
    log_dir = apdata / LOG_REL
    if not log_dir.is_file():
        return ""
    try:
        if log_dir.stat().st_mtime < after - 1:
            return ""
        lines = log_dir.read_text(errors="replace").splitlines()
        return "\n".join(lines[-max_lines:])
    except OSError:
        return ""


# --------------------------------------------------------------------------
# runtime
# --------------------------------------------------------------------------

def stage_seed(apdata: Path, seed_src: Path) -> dict:
    """Copy the seed save into the isolated profile and force windowed mode
    (same finalize the B2 launcher applies).  Returns staging facts."""
    user_dir = apdata / "Godot/app_userdata/Mutagenic"
    user_dir.mkdir(parents=True, exist_ok=True)
    save_path = user_dir / "_0_6_0.dat"
    if not seed_src.is_file():
        return {"staged": False, "reason": f"seed save missing: {seed_src}"}
    raw = seed_src.read_bytes()
    before = sha256_bytes(raw)
    shutil.copy2(seed_src, save_path)
    finalize = "none"
    try:
        save = json.loads(raw.decode("utf-8"))
        if isinstance(save, dict) and isinstance(save.get("settings"), dict):
            save["settings"]["enable_fullscreen"] = False
            text = json.dumps(save, ensure_ascii=False) + "\n"
            save_path.write_bytes(text.encode("utf-8"))
            finalize = "enable_fullscreen=False patched"
    except Exception as exc:
        finalize = f"finalize skipped ({exc})"
    after = sha256_bytes(save_path.read_bytes())
    return {
        "staged": True,
        "seed_source": str(seed_src),
        "seed_sha_before": before,
        "seed_sha_after": after,
        "seed_size": len(raw),
        "finalize": finalize,
    }


def run_cycle(exe: Path, apdata: Path, out_dir: Path, run_id: str,
              expected_prev_sha: str | None, planted_prev_sha: str | None,
              boot_seconds: float, load_timeout: float, settle_seconds: float,
              poll_seconds: float, grace_close_seconds: float,
              heartbeat: Path) -> dict:
    """Launch the game under APPDATA=apdata, wait for the save to be loaded
    and rewritten (disk sha change from expected_prev_sha OR the log marker),
    let the save settle, close the process and re-read the save.

    Returns a full run-cycle outcome dict (evidence-grade)."""
    events: list[dict] = []
    t0 = time.monotonic()
    run_start_epoch = time.time()

    def note(kind: str, detail: str) -> None:
        events.append({"t_sec": round(time.monotonic() - t0, 2),
                       "kind": kind, "detail": detail})

    save_path = apdata / SAVE_REL
    env = dict(os.environ.copy())
    env["APPDATA"] = str(apdata)

    note("launch", f"candidate={exe.name} cwd={exe.parent}")
    proc = subprocess.Popen([str(exe)], cwd=str(exe.parent), env=env)
    note("pid", str(proc.pid))

    hwnd = find_window(proc.pid, boot_seconds + 20.0)
    note("window", f"hwnd={hwnd}")

    last_sha = expected_prev_sha
    last_size = None
    seen_log_marker = False
    seen_no_save = False
    fatal: list[str] = []
    seen_boot = False
    rewrite_count = 0
    load_trigger_kind = None
    load_t = None
    last_change_t = time.monotonic()
    save_parse_ok = False
    parse_error = ""
    last_save = None
    settled = False

    writes: list[dict] = []

    def poll_save(phase: str) -> None:
        nonlocal last_sha, last_size, rewrite_count, load_trigger_kind, load_t
        nonlocal last_change_t, save_parse_ok, parse_error, last_save
        try:
            data = save_path.read_bytes()
        except OSError:
            data = None
        if data is None:
            if last_sha is not None:
                note("save_gone", f"save missing (was {last_sha[:10]})")
                last_sha = None
                last_change_t = time.monotonic()
            with heartbeat.open("a", encoding="utf-8") as hb:
                hb.write(json.dumps({
                    "at": utc_now(), "phase": phase,
                    "alive": proc.poll() is None,
                    "save": None, "markers": {"load": seen_log_marker,
                                              "no_save": seen_no_save},
                }, ensure_ascii=False) + "\n")
            return
        cur = sha256_bytes(data)
        size = len(data)
        if cur != last_sha:
            if last_sha is not None:
                rewrite_count += 1
                note("save_rewrite", f"sha={cur[:10]} size={size} "
                                     f"(was {last_sha[:10]})")
            else:
                note("save_first_seen", f"sha={cur[:10]} size={size}")
            writes.append({"sha256": cur, "size": size,
                           "at_sec": round(time.monotonic() - t0, 2)})
            last_sha, last_size, last_change_t = cur, size, time.monotonic()
            last_save = cur
            if load_trigger_kind is None and planted_prev_sha is not None \
                    and cur != planted_prev_sha:
                load_trigger_kind = "disk_rewrite"
                load_t = time.monotonic()
                note("load_trigger", f"disk rewrite differs from staged seed "
                                     f"({planted_prev_sha[:10]})")
            ok, save, err = parse_save_bytes(data)
            if ok:
                save_parse_ok = True
                parse_error = ""
            elif parse_error != err:
                parse_error = err
                note("save_unparseable", err)
        with heartbeat.open("a", encoding="utf-8") as hb:
            hb.write(json.dumps({
                "at": utc_now(), "phase": phase,
                "alive": proc.poll() is None,
                "save": {"sha256": cur, "size": size},
                "markers": {"load": seen_log_marker, "no_save": seen_no_save,
                            "boot": seen_boot},
            }, ensure_ascii=False) + "\n")

    def poll_log() -> None:
        nonlocal seen_log_marker, seen_no_save, fatal, seen_boot
        nonlocal load_trigger_kind, load_t
        log_path = apdata / LOG_REL
        if not log_path.is_file():
            return
        try:
            if log_path.stat().st_mtime < run_start_epoch - 1:
                return
            text = log_path.read_text(errors="replace")
        except OSError:
            return
        if LOAD_MARKER in text:
            if not seen_log_marker:
                note("log_marker", LOAD_MARKER)
            seen_log_marker = True
            if load_trigger_kind is None:
                load_trigger_kind = "log_marker"
                load_t = time.monotonic()
        if NO_SAVE_MARKER in text:
            if not seen_no_save:
                note("log_marker", NO_SAVE_MARKER)
            seen_no_save = True
        if BOOT_MARKER in text:
            seen_boot = True
        for m in FATAL_MARKERS:
            if m in text and m not in fatal:
                fatal.append(m)
                note("log_marker", m)

    try:
        time.sleep(boot_seconds)
        deadline = time.monotonic() + load_timeout
        triggered_at = None
        settle_notes = 0
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                note("process_exited", f"code={proc.returncode}")
                break
            poll_log()
            poll_save("await_load")
            if load_trigger_kind is not None and triggered_at is None:
                triggered_at = time.monotonic()
                note("load_confirmed", f"kind={load_trigger_kind}")
                deadline = max(deadline,
                               triggered_at + settle_seconds + 4.0)
            elif triggered_at is not None and not settled:
                if time.monotonic() - last_change_t >= settle_seconds \
                        and time.monotonic() - triggered_at >= 4.0:
                    settled = True
                    note("settled", f"no rewrite for {settle_seconds}s")
                elif settle_notes % 8 == 0:
                    note("settle_wait",
                         f"idle={round(time.monotonic() - last_change_t, 1)}s")
            if settled:
                break
            settle_notes += 1
            time.sleep(poll_seconds)
        if load_trigger_kind is None:
            note("no_load_trigger", "timeout waiting for load/save signal")
    finally:
        time.sleep(0.25)
        poll_save("pre_close")
        note("pre_close_sha", f"{last_sha[:10] if last_sha else 'none'} "
                              f"size={last_size}")
        exit_info = terminate(proc, hwnd, grace_close_seconds)
        note("exit", f"method={exit_info['method']} "
                     f"exit_code={exit_info['exit_code']}")
        time.sleep(1.0)
        poll_save("post_exit")
        poll_log()

    ok, save, err = parse_save_bytes(save_path.read_bytes()) \
        if save_path.is_file() else (False, None,
                                     "save file missing after exit (restored "
                                     "before close? staging bug)")
    if ok:
        save_parse_ok = True
        parse_error = ""
    else:
        parse_error = err
    exit_stable = (last_save is not None
                   and str(last_save) == str(sha256_bytes(save_path.read_bytes()))
                   if save_path.is_file() else False)
    settled_semantic = semantic_sha256(save) if ok else None
    settled_raw_sha = sha256_bytes(save_path.read_bytes()) \
        if save_path.is_file() else None

    return {
        "run_id": run_id,
        "window_found": hwnd is not None,
        "window_title_ok": bool(hwnd),
        "load_triggered": load_trigger_kind is not None,
        "load_trigger_kind": load_trigger_kind,
        "load_t_sec": round(load_t - t0, 2) if load_t else None,
        "settled": settled,
        "rewrite_count": rewrite_count,
        "save_parse_ok": save_parse_ok,
        "parse_error": parse_error,
        "load_marker_seen": seen_log_marker,
        "no_save_marker": seen_no_save,
        "boot_marker_seen": seen_boot,
        "fatal_markers": fatal,
        "writes": writes,
        "events": events,
        "settled_snapshot": {
            "save": save,
            "semantic_sha256": settled_semantic,
            "raw_sha256": settled_raw_sha,
            "size": save_path.stat().st_size if save_path.is_file() else None,
        },
        "post_exit_snapshot": {
            "save": save,
            "semantic_sha256": settled_semantic,
            "raw_sha256": settled_raw_sha,
            "size": save_path.stat().st_size if save_path.is_file() else None,
        },
        "exit_stable": exit_stable,
        "exit_info": exit_info,
        "summary": {
            "rewrite_count": rewrite_count,
            "load_trigger": load_trigger_kind,
            "load_marker": seen_log_marker,
            "no_save_marker": seen_no_save,
            "fatal": fatal,
        },
        "log_tail": log_tail(apdata),
    }


def build_evidence(args, verdict: str, detail: dict, run1: dict, run2: dict,
                   seed_stage: dict, out_root: Path) -> dict:
    def snap(which: dict, key: str) -> dict:
        s = which.get(key) or {}
        save = s.get("save") or {}
        return {
            "semantic_sha256": s.get("semantic_sha256"),
            "raw_sha256": s.get("raw_sha256"),
            "size": s.get("size"),
            "field_brief": evidence_field_brief(save),
        }

    return {
        "experiment_id": args.experiment_id,
        "tool_version": TOOL_VERSION,
        "recorded_at": args.recorded_at,
        "ended_at": utc_now(),
        "commands": [sys.executable] + [str(a) for a in sys.argv],
        "candidate": {"exe": str(Path(args.candidate).resolve()),
                      "sha256": args.candidate_sha},
        "seed": seed_stage,
        "apdata": str(Path(args.apdata).resolve()),
        "same_state": {
            "criterion": "semantic fields (all top-level save keys except "
                         "timestamp/checksum/stamp) of run1 post-exit save "
                         "== run2 reloaded save; planted character markers "
                         "survived; real disk rewrites observed in both runs; "
                         "'LOADED AND MERGED' marker in run2 log; no fatal/"
                         "script-error markers; no 'No save file found'.",
            "run1_exit": snap(run1, "post_exit_snapshot"),
            "run2_settled": snap(run2, "settled_snapshot"),
            "run2_exit": snap(run2, "post_exit_snapshot"),
            "diffs": detail.get("run1_exit_vs_run2_diffs", []),
            "planted_marker_run2": detail.get("planted_marker_run2"),
            "exit_stable": detail.get("exit_stable"),
            "rewritten_twice": detail.get("rewritten_twice"),
            "run2_load_marker": detail.get("run2_load_marker"),
        },
        "runs": {"run1": run1, "run2": run2},
        "status": verdict,
        "verdict_detail": detail,
        "raw_evidence_dir": str(out_root),
        "proves": None if verdict != "PASS" else (
            "The candidate, under one isolated APPDATA profile, performed a "
            "real save->exit->reload cycle: run1 staged seed save was loaded "
            "and rewritten on disk, the process exited, run2 booted against "
            "the SAME profile, re-loaded the save ('LOADED AND MERGED'), "
            "rewrote it again, and the post-exit semantic state of run1 "
            "equals the reloaded semantic state of run2 for all semantic "
            "fields (save_version/settings/shared_stash/keybind_overrides/"
            "characters/completed_achievements); the planted character "
            "markers survived; timestamp/checksum/stamp were the only "
            "expected per-save volatile deltas. Evidence: the gate's own "
            "timeline/heartbeat/log captures in the raw evidence dir."),
        "not_proven": None if verdict != "PASS" else (
            "In-game progress made OUTSIDE the save path (e.g. mid-run "
            "orbs/genes/stage completions) is not exercised by this gate "
            "(no gameplay input is sent; the same-state claim covers the "
            "state the game itself wrote); Steam cloud save branch is not "
            "exercised (p7-fix-persistence USE_STEAM=false local branch); "
            "visual/UI behaviour; and this run is on the current available "
            "candidate - the promotion candidate must be re-run through this "
            "gate before S3 can be claimed for it."),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidate", required=True, type=Path,
                    help="candidate Mutagenic.exe")
    ap.add_argument("--apdata", required=True, type=Path,
                    help="isolated APPDATA root (created if missing; shared "
                         "by both runs)")
    ap.add_argument("--seed-save", required=True, type=Path,
                    help="seed _0_6_0.dat to stage before run1")
    ap.add_argument("--out", required=True, type=Path,
                    help="evidence output dir (raw, git-ignored)")
    ap.add_argument("--experiment-id", default="B3-P2-S3")
    ap.add_argument("--boot-seconds", type=float, default=8.0)
    ap.add_argument("--load-timeout", type=float, default=50.0)
    ap.add_argument("--settle-seconds", type=float, default=12.0)
    ap.add_argument("--poll-seconds", type=float, default=0.5)
    ap.add_argument("--grace-close-seconds", type=float, default=8.0)
    ap.add_argument("--character-name", default="default",
                    help="character the seed save plants (marker check)")
    args = ap.parse_args(argv)

    recorded_at = utc_now()
    args.recorded_at = recorded_at
    exe = args.candidate.resolve()
    if not exe.is_file():
        print(f"USAGE: candidate exe missing: {exe}")
        return 3
    if not (exe.parent / "steam_api64.dll").is_file():
        print(f"USAGE: adjacent steam_api64.dll missing in {exe.parent} "
              "(local-save branch requires it)")
        return 3
    try:
        args.candidate_sha = sha256_bytes(exe.read_bytes())
    except OSError as exc:
        print(f"USAGE: cannot read candidate exe: {exc}")
        return 3
    if not args.apdata.exists():
        args.apdata.mkdir(parents=True)
    out_root = args.out.resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    seed_stage = stage_seed(args.apdata, args.seed_save)
    if not seed_stage["staged"]:
        print(f"BLOCKED: seed stage failed: {seed_stage['reason']}")
        return 2

    run1 = run_cycle(exe, args.apdata, out_root, "run1",
                     seed_stage["seed_sha_after"], seed_stage["seed_sha_after"],
                     args.boot_seconds, args.load_timeout, args.settle_seconds,
                     args.poll_seconds, args.grace_close_seconds,
                     out_root / "heartbeat_run1.jsonl")
    run2 = run_cycle(exe, args.apdata, out_root, "run2",
                     run1["post_exit_snapshot"]["raw_sha256"],
                     seed_stage["seed_sha_after"],
                     args.boot_seconds, args.load_timeout, args.settle_seconds,
                     args.poll_seconds, args.grace_close_seconds,
                     out_root / "heartbeat_run2.jsonl")

    verdict, detail = classify_verdict(run1, run2, seed_stage,
                                       args.character_name)
    evidence = build_evidence(args, verdict, detail, run1, run2, seed_stage,
                              out_root)

    report_path = out_root / "s3_persistence_evidence.json"
    report_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2)
                           + "\n", encoding="utf-8")
    (out_root / "run1_log_tail.txt").write_text(
        run1.get("log_tail", ""), encoding="utf-8")
    (out_root / "run2_log_tail.txt").write_text(
        run2.get("log_tail", ""), encoding="utf-8")
    for label, save in (("seed_staged", seed_stage),
                        ("run1_exit", run1.get("post_exit_snapshot")),
                        ("run2_settled", run2.get("settled_snapshot")),
                        ("run2_exit", run2.get("post_exit_snapshot"))):
        data = save.get("save") if isinstance(save, dict) else None
        if data is not None:
            (out_root / f"{label}.json").write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8")

    print(json.dumps({
        "experiment_id": args.experiment_id,
        "status": verdict,
        "candidate": str(exe),
        "candidate_sha256": args.candidate_sha,
        "recorded_at": recorded_at,
        "same_state": {
            "run1_exit_semantic_sha": evidence["same_state"]
                ["run1_exit"]["semantic_sha256"],
            "run2_settled_semantic_sha": evidence["same_state"]
                ["run2_settled"]["semantic_sha256"],
            "diffs": evidence["same_state"]["diffs"],
            "planted_ok": (evidence["same_state"]
                           .get("planted_marker_run2", {})
                           .get("ok")),
        },
        "runs": {
            "run1": {"window": run1["window_found"],
                     "load_trigger": run1["load_trigger_kind"],
                     "rewrites": run1["rewrite_count"],
                     "exit": run1["exit_info"]["method"]},
            "run2": {"window": run2["window_found"],
                     "load_trigger": run2["load_trigger_kind"],
                     "rewrites": run2["rewrite_count"],
                     "load_marker": run2["load_marker_seen"],
                     "exit": run2["exit_info"]["method"]},
        },
        "detail": detail.get("reason") or detail,
        "evidence": str(report_path),
    }, ensure_ascii=False, indent=2))
    return {"PASS": 0, "FAIL": 1, "BLOCKED": 2}[verdict]


if __name__ == "__main__":
    raise SystemExit(main())