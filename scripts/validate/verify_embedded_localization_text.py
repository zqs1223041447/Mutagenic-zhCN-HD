#!/usr/bin/env python3
"""Verify exact localized scene text in a fully extracted runtime tree.

This validator deliberately matches serialized Godot ``text = "..."`` fields,
not arbitrary substrings. Node names and resource paths may legitimately keep
their English identifiers after a display label is translated.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED: dict[str, dict[str, list[str]]] = {
    "Scenes/Menu.tscn": {
        "expected": ['text = "开始游戏"'],
        "old": ['text = "Play"'],
    },
    "Scenes/Popups/Dialogs/CharacterSelect/CharacterSelect.tscn": {
        "expected": [
            'text = "选择你的角色"',
            'text = "创建新角色"',
            'text = "关闭"',
        ],
        "old": [
            'text = "Choose your Character"',
            'text = "Create New Character"',
            'text = "Close"',
        ],
    },
    "Scenes/Popups/Dialogs/CharacterSelect/CharacterChanger.tscn": {
        "expected": ['text = "取消"', 'text = "选择你的职业"'],
        "old": ['text = "Cancel"', 'text = "Choose your Class"'],
    },
    "Scenes/Popups/Dialogs/CharacterSelect/CharacterCreator.tscn": {
        "expected": ['text = "取消"', 'text = "选择你的职业"'],
        "old": ['text = "Cancel"', 'text = "Choose your Class"'],
    },
    "Scenes/Popups/Dialogs/Settings/Settings.tscn": {
        "expected": [
            'text = "设置"',
            'text = "关闭设置"',
            'text = "按键设置"',
        ],
        "old": [
            'text = "Settings"',
            'text = "Close Settings"',
            'text = "Keybindings"',
        ],
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    candidate = args.candidate.resolve()
    if not root.is_dir():
        raise SystemExit(f"ERROR: extracted runtime root does not exist: {root}")
    if not candidate.is_file():
        raise SystemExit(f"ERROR: candidate EXE does not exist: {candidate}")

    checks: list[dict[str, object]] = []
    for relative, declaration in EXPECTED.items():
        path = root / relative
        if not path.is_file():
            checks.append({"path": relative, "missing_file": True})
            continue
        content = path.read_text(encoding="utf-8")
        expected_counts = {
            line: content.count(line) for line in declaration["expected"]
        }
        old_counts = {line: content.count(line) for line in declaration["old"]}
        checks.append(
            {
                "path": relative,
                "expected_field_counts": expected_counts,
                "old_field_counts": old_counts,
                "expected_exactly_once": all(
                    count == 1 for count in expected_counts.values()
                ),
                "old_fields_absent": all(count == 0 for count in old_counts.values()),
                "sha256": sha256(path),
            }
        )

    passed = all(
        check.get("missing_file") is not True
        and check.get("expected_exactly_once") is True
        and check.get("old_fields_absent") is True
        for check in checks
    )
    report = {
        "evidence_id": "C5-L4-embedded-text-20260814-v2",
        "candidate": str(candidate),
        "candidate_sha256": sha256(candidate),
        "checks": checks,
        "status": "PASS" if passed else "FAIL",
        "proves": (
            "the extracted runtime contains each cumulative C5-L1 through C5-L4 "
            "localized display field exactly once and the targeted English text "
            "fields are absent"
        ),
        "not_proven": (
            "visual rendering, dynamic values, interaction, persistence, broad "
            "localization, or release readiness"
        ),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "candidate_sha256": report["candidate_sha256"]}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
