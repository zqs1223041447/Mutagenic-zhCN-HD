#!/usr/bin/env python3
"""Repo-wide absolute-path scanner (portability gate).

Scans tracked source of truth files (AGENTS.md 9.4 extension set) for host
absolute paths and classifies every hit:

  production_hardcode  FAIL  - production code depends on one machine's path
  provenance_metadata  WARN  - historical record/evidence, must be preserved
  local_config         WARN  - machine-level lock/config fact, not a runtime default
  test_fixture         INFO  - deliberately placed fixture
  docs_example         INFO  - documentation placeholder such as C:\\path\\to\\...
  false_positive       INFO  - not a host path (URI scheme etc.)

Exit code is non-zero only for hits at or above --fail-on (default FAIL),
i.e. production_hardcode blocks, everything else reports.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from repo_util import RepoError, find_repo_root, git, tracked_files

SCAN_EXTS = {".py", ".ps1", ".bat", ".cmd", ".json", ".yaml", ".yml", ".toml",
             ".gd", ".tscn", ".tres"}

SCHEME_RE = re.compile(r"[A-Za-z][A-Za-z0-9+.\-]*://")
DRIVE_RE = re.compile(r"(?<![A-Za-z0-9_%])[A-Za-z]:[\\/]")
UNC_RE = re.compile(r"\\\\(?![\\/])[A-Za-z0-9_.\-]+(?:\\[A-Za-z0-9_.\-]+)+")
POSIX_USER_RE = re.compile(r"(?<![A-Za-z0-9_.\\/:])/(?:home|Users|mnt|opt|etc|var|tmp|usr)/(?:[A-Za-z0-9_.\-]+/)*[A-Za-z0-9_.\-]+")

SYSTEM_DIR_PREFIXES = (
    "C:/Windows", "C:\\Windows",
    "C:/Program Files", "C:\\Program Files",
    "C:/ProgramData", "C:\\ProgramData",
    "C:/Program Files (x86)", "C:\\Program Files (x86)",
)

PLACEHOLDER_MARKERS = ("\\path\\", "/path/", "\\path\\to\\", "/path/to/",
                       "\\example\\", "/example/", "\\your\\", "/your/")

PROVENANCE_FIELDS = {"source", "source_path", "workspace_root", "project_root",
                     "original_path", "evidence_path", "recorded_at",
                     "archive_root", "host", "host_path"}
PATCH_PAYLOAD_FIELDS = {"old_text", "new_text", "anchor", "context", "intent",
                        "scope", "expected_runtime_effect", "description",
                        "preimage", "unit_id"}

CLASS_SEVERITY = {
    "production_hardcode": "FAIL",
    "provenance_metadata": "WARN",
    "local_config": "WARN",
    "test_fixture": "INFO",
    "docs_example": "INFO",
    "false_positive": "INFO",
}

REMEDIATION = {
    "production_hardcode": "replace with Path(__file__).resolve()-derived root, MUTAGENIC_*_ROOT env/CLI/config injection or git submodule; do not commit host paths",
    "provenance_metadata": "historical evidence only - preserve verbatim, never auto-rewrite or delete",
    "local_config": "machine/lock fact - keep out of runtime defaults; move to local ignored config if consumed as a default",
    "test_fixture": "deliberate fixture - keep inside test/fixture scope",
    "docs_example": "doc placeholder - prefer <repo_root>/<archive_root> logical paths",
    "false_positive": "not a host absolute path - no action",
}


def _protect_schemes(text: str) -> str:
    return SCHEME_RE.sub("SCHEME://", text)


def _json_leaf_paths(data, value: str, prefix: str = "") -> list[str]:
    found: list[str] = []
    needles = {value, value.replace("\\\\", "\\")}
    if isinstance(data, dict):
        for k, v in data.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, (dict, list)):
                found.extend(_json_leaf_paths(v, value, key))
            elif isinstance(v, str) and any(n in v for n in needles):
                found.append(key)
    elif isinstance(data, list):
        for i, v in enumerate(data):
            key = f"{prefix}[{i}]"
            if isinstance(v, (dict, list)):
                found.extend(_json_leaf_paths(v, value, key))
            elif isinstance(v, str) and any(n in v for n in needles):
                found.append(key)
    return found


def _json_path_for(file_path: Path, needle: str) -> str | None:
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    paths = _json_leaf_paths(data, needle)
    return paths[0] if paths else None


def _is_system_dir(matched: str) -> bool:
    """True when the matched segment is (part of) an OS-level system directory.

    The scanner's own pattern table writes prefixes with doubled backslashes
    (for example ``C:\\Windows`` inside a Python string literal), and
    _full_segment may truncate at spaces (``C:\\Program`` from
    ``C:\\Program Files\\...``). Iteratively unescape backslash doublings and
    compare in both directions, so pattern definitions and truncated segments
    are not misclassified as hardcodes.
    """
    candidates = [matched]
    while True:
        nxt = candidates[-1].replace("\\\\", "\\")
        if nxt == candidates[-1]:
            break
        candidates.append(nxt)
    for raw in candidates:
        for prefix in SYSTEM_DIR_PREFIXES:
            if raw.startswith(prefix) or prefix.startswith(raw):
                return True
    return False


def classify(rel: str, matched: str, json_path: str | None = None) -> tuple[str, str]:
    parts = Path(rel).parts
    if rel.startswith("03_raw/") or rel.startswith("04_recovered/"):
        return "provenance_metadata", "immutable recovered provenance - never modify"
    if "docs" in parts:
        return "docs_example", "documentation/example scope"
    if rel == "status.json":
        return "provenance_metadata", "status.json is machine state/evidence records, not runtime default"
    if rel == "tools.lock.json":
        return "local_config", "toolchain lock records one machine's facts - not a runtime default"
    if json_path:
        leaf = json_path.rsplit(".", 1)[-1].split("[")[0]
        if leaf in PROVENANCE_FIELDS:
            return "provenance_metadata", f"provenance/evidence field '{leaf}' - preserve verbatim"
        if leaf in PATCH_PAYLOAD_FIELDS:
            return "provenance_metadata", f"patch payload field '{leaf}' mirrors recovered/historical content"
    if _is_system_dir(matched):
        return "local_config", "OS-level system directory (Windows) - not machine-specific user data"
    if any(m in matched for m in PLACEHOLDER_MARKERS):
        return "docs_example", "placeholder path (\\path\\to\\...) - documentation style"
    if rel.startswith(".opencode/"):
        return "local_config", "AI workbench local tooling bound to one machine (Hyper-V/VHDX facts) - portability debt, not product code"
    if rel.startswith("manifests/"):
        return "provenance_metadata", "manifest/evidence record of a past run - preserve verbatim"
    if any(("test" in p or "fixture" in p or p.startswith("test_")) for p in parts):
        return "test_fixture", "test/fixture scope"
    if not re.match(r"^[A-Za-z]:", matched):
        return "production_hardcode", "host absolute path in production source"
    return "production_hardcode", "host drive absolute path in production source"


def scan_text(rel: str, text: str, file_path: Path) -> list[dict]:
    hits: list[dict] = []
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = _protect_schemes(raw)
        if line.lstrip("\ufeff \t").startswith("#!"):
            continue
        for m in DRIVE_RE.finditer(line):
            matched = m.group(0)
            full = _full_segment(line, m.start(), m.end())
            json_path = _json_path_for(file_path, full) if file_path.suffix == ".json" and len(full) > 2 else None
            klass, why = classify(rel, full, json_path)
            hits.append(_hit(rel, line_no, full, klass, why, json_path))
        for m in UNC_RE.finditer(line):
            full = m.group(0)
            json_path = _json_path_for(file_path, full) if file_path.suffix == ".json" else None
            klass, why = classify(rel, full, json_path)
            hits.append(_hit(rel, line_no, full, klass, why, json_path))
        for m in POSIX_USER_RE.finditer(line):
            full = m.group(0)
            json_path = _json_path_for(file_path, full) if file_path.suffix == ".json" else None
            klass, why = classify(rel, full, json_path)
            hits.append(_hit(rel, line_no, full, klass, why, json_path))
    return hits


def _full_segment(line: str, start: int, end: int) -> str:
    seg = line[start:end]
    rest = line[end:]
    for i, ch in enumerate(rest):
        if ch in " \t\"'`()[],;{}":
            break
        seg += ch
    return seg[:160]


def _hit(rel: str, line_no: int, matched: str, klass: str, why: str, json_path: str | None) -> dict:
    return {
        "file": rel,
        "line": line_no,
        "json_path": json_path,
        "matched": matched,
        "classification": klass,
        "severity": CLASS_SEVERITY[klass],
        "remediation": REMEDIATION[klass],
        "why": why,
    }


def scan_files(root: Path, rel_files: list[str]) -> list[dict]:
    hits: list[dict] = []
    for rel in rel_files:
        if not rel.endswith(tuple(SCAN_EXTS)):
            continue
        if "script_key.txt" in rel or rel == "manifests/script_key.txt":
            continue
        p = root / rel
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        hits.extend(scan_text(rel, text, p))
    return hits


def scan_repo(root: Path, include_untracked: bool = False, changed_in: str | None = None) -> list[dict]:
    rel_files = tracked_files(root)
    if include_untracked:
        rel_files.extend(git("ls-files", "--others", "--exclude-standard", cwd=root).stdout.splitlines())
    if changed_in:
        base = git("rev-parse", changed_in, cwd=root).stdout.strip()
        head = git("rev-parse", "HEAD", cwd=root).stdout.strip()
        changed = set(git("diff", "--name-only", base, head, cwd=root).stdout.splitlines())
        dirty = set(git("diff", "--name-only", "HEAD", cwd=root).stdout.splitlines())
        untracked = set(git("ls-files", "--others", "--exclude-standard", cwd=root).stdout.splitlines()) if include_untracked else set()
        rel_files = [f for f in dict.fromkeys(rel_files) if f in changed | dirty | untracked]
    else:
        rel_files = list(dict.fromkeys(rel_files))
    return scan_files(root, rel_files)


def summarize(hits: list[dict]) -> dict:
    out = {c: 0 for c in CLASS_SEVERITY}
    for h in hits:
        out[h["classification"]] += 1
    return out


def fail_on_severity(severity: str, threshold: str) -> bool:
    order = {"INFO": 0, "WARN": 1, "FAIL": 2, "NEVER": 3}
    return order[severity] >= order[threshold]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="emit JSON report")
    ap.add_argument("--include-untracked", action="store_true")
    ap.add_argument("--changed-in", metavar="REF", help="only scan files changed since REF (tracked + dirty)")
    ap.add_argument("--fail-on", default="FAIL", choices=("FAIL", "WARN", "INFO", "NEVER"))
    args = ap.parse_args(argv)

    try:
        root = find_repo_root()
    except RepoError as e:
        print(f"abs_path_scan: {e}", file=sys.stderr)
        return 2

    hits = scan_repo(root, include_untracked=args.include_untracked, changed_in=args.changed_in)
    summary = summarize(hits)
    fails = [h for h in hits if fail_on_severity(h["severity"], args.fail_on)]

    if args.json:
        print(json.dumps({
            "repo_root": str(root),
            "fail_on": args.fail_on,
            "summary": summary,
            "hits": hits,
        }, ensure_ascii=False, indent=1))
    else:
        for h in hits:
            loc = f"{h['file']}:{h['line']}"
            if h["json_path"]:
                loc += f" ({h['json_path']})"
            print(f"[{h['severity']:4s}] {h['classification']:20s} {loc}  value={h['matched']}")
            print(f"        {h['why']} | {h['remediation']}")
        print("---")
        print(f"scanned repo root: {root}")
        print(f"hits: {sum(summary.values())}  " + "  ".join(f"{k}={v}" for k, v in summary.items()))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())