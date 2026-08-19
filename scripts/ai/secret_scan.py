#!/usr/bin/env python3
"""Repo-wide secret scanner (pre-commit / integration gate).

Detects key/credential/token/.env material in the scanned file set and
REPORTS REDACTED FINDINGS ONLY - the raw secret value is never printed.

Two hard rules (AGENTS.md 5.8 / 8):
  * manifests/script_key.txt is the local AES script key (gitignored); its
    content must never be emitted in any mode. Key files are reported as
    presence + SHA-256 fingerprint only.
  * any matched credential value is replaced by <redacted:len>.

Scope: git-tracked files by default; --include-untracked adds untracked
non-ignored files; --scan-ignored adds gitignored files (for a deliberate
local sweep - key files still remain content-safe).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from repo_util import RepoError, find_repo_root, git, tracked_files

KEY_NAMES = (r"api[_-]?key|apikey|secret|token|passwd|password|pwd|credential"
             r"|client[_-]?secret|access[_-]?key|auth[_-]?key|encryption[_-]?key"
             r"|private[_-]?key|script[_-]?key|session[_-]?key|refresh[_-]?token"
             r"|steam[_-]?web[_-]?api[_-]?key|db[_-]?pass|user[_-]?pass")

RULES = [
    ("private_key_block", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----")),
    ("key_value", re.compile(rf"(?i)\b({KEY_NAMES})\b\s*[:=]\s*(?:['\"]?)([^\s'\"]{{8,}})")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github_pat", re.compile(r"\bghp_[A-Za-z0-9]{36}\b")),
    ("openai_sk", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
]

KEY_FILE_BASENAMES = {
    "script_key.txt", "script_key", "script_encryption_key", "encryption_key",
    "godot_script_key", "godot_script_key.txt", "script_key.key",
}

ENV_PATTERN = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*(.*)$")
ENV_NAME_OK = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
ENV_REDACT_NAME = re.compile(r"(?i)(key|secret|token|pass|pwd|credential)")


def is_key_file(rel: str) -> bool:
    if rel == "manifests/script_key.txt":
        return True
    return Path(rel).name in KEY_FILE_BASENAMES


def is_env_file(rel: str) -> bool:
    return Path(rel).name == ".env" or Path(rel).name.startswith(".env.")


def _redact(name_hint: str, value: str) -> str:
    return f"{name_hint}=<redacted:{len(value)}>"


def scan_text(rel: str, text: str) -> list[dict]:
    findings: list[dict] = []
    for line_no, raw in enumerate(text.splitlines(), 1):
        stripped = raw.strip()
        if is_env_file(rel):
            m = ENV_PATTERN.match(raw)
            if m and m.group(1).strip() and ENV_NAME_OK.match(raw.split("=", 1)[0].strip()):
                name = raw.split("=", 1)[0].strip()
                value = m.group(1).strip().strip("\"'")
                if len(value) >= 8 and ENV_REDACT_NAME.search(name):
                    findings.append({
                        "file": rel, "line": line_no, "rule": "env_line",
                        "key": _redact(name, value), "secret_length": len(value),
                    })
                    continue
        for rule_name, rx in RULES:
            for m in rx.finditer(raw):
                if rule_name == "key_value":
                    name, value = m.group(1), m.group(2)
                    hint = _redact(name, value)
                elif rule_name == "private_key_block":
                    hint = f"private_key_block=<redacted:lines>"
                else:
                    hint = f"{rule_name}=<redacted:{len(m.group(0))}>"
                findings.append({
                    "file": rel, "line": line_no, "rule": rule_name,
                    "key": hint, "secret_length": len(m.group(0) if rule_name != "key_value" else value),
                })
    return findings


def scan_files(root: Path, rel_files: list[str], scan_ignored: bool = False) -> list[dict]:
    findings: list[dict] = []
    for rel in rel_files:
        if is_key_file(rel):
            continue
        if "tests/fixtures" in rel:
            continue
        p = root / rel
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        findings.extend(scan_text(rel, text))
    if scan_ignored:
        findings.extend(_scan_ignored_key_files(root))
    return findings


def _scan_ignored_key_files(root: Path) -> list[dict]:
    reports: list[dict] = []
    try:
        rels = tracked_files(root) + git("ls-files", "--others", "--ignored", "--exclude-standard",
                                         cwd=root).stdout.splitlines()
    except RepoError:
        rels = [p.relative_to(root).as_posix() for p in root.rglob("*")
                if p.is_file() and ".git" not in p.relative_to(root).parts]
    for rel in rels:
        if not is_key_file(rel):
            continue
        p = root / rel
        if not p.is_file():
            continue
        try:
            data = p.read_bytes()
        except OSError:
            continue
        reports.append({
            "file": rel, "line": None, "rule": "key_file_presence",
            "key": f"key_file=<redacted:content_preserved>", "secret_length": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    return reports


def scan_repo(root: Path, include_untracked: bool = False, scan_ignored: bool = False,
              changed_in: str | None = None) -> list[dict]:
    rel_files = tracked_files(root)
    if include_untracked or scan_ignored:
        rel_files.extend(git("ls-files", "--others", "--exclude-standard", cwd=root).stdout.splitlines())
    rel_files = list(dict.fromkeys(rel_files))
    if changed_in:
        base = git("rev-parse", changed_in, cwd=root).stdout.strip()
        changed = set(git("diff", "--name-only", base, "HEAD", cwd=root).stdout.splitlines())
        dirty = set(git("diff", "--name-only", "HEAD", cwd=root).stdout.splitlines())
        untracked = set(git("ls-files", "--others", "--exclude-standard", cwd=root).stdout.splitlines())
        rel_files = [f for f in rel_files if f in changed | dirty | untracked]
    return scan_files(root, rel_files, scan_ignored=scan_ignored)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="emit JSON report")
    ap.add_argument("--include-untracked", action="store_true", help="also scan untracked non-ignored files")
    ap.add_argument("--scan-ignored", action="store_true", help="also scan gitignored files (local sweep only)")
    ap.add_argument("--changed-in", metavar="REF", help="only scan files changed since REF")
    args = ap.parse_args(argv)

    try:
        root = find_repo_root()
    except RepoError as e:
        print(f"secret_scan: {e}", file=sys.stderr)
        return 2

    findings = scan_repo(root, include_untracked=args.include_untracked,
                         scan_ignored=args.scan_ignored, changed_in=args.changed_in)
    if args.json:
        print(json.dumps({"repo_root": str(root), "findings": findings}, ensure_ascii=False, indent=1))
    else:
        if findings:
            print("secret_scan: findings (values redacted):")
        for f in findings:
            loc = f"{f['file']}:{f['line']}" if f["line"] else f"{f['file']}"
            extra = f" sha256={f['sha256']}" if "sha256" in f else ""
            print(f"  {loc} [{f['rule']}] {f['key']}{extra}")
        print(f"secret_scan: scanned root {root}; findings={len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())