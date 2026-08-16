#!/usr/bin/env python3
"""Verify a one-property scene/resource patch preserves structural references."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def structural_tokens(text: str) -> dict[str, list[str]]:
    patterns = {
        "node_declarations": r"^\[node .*$",
        "node_paths": r"NodePath\([^\n]*\)",
        "resource_paths": r"res://[^\"\s]+",
        "ext_resources": r"^\[ext_resource .*$",
        "sub_resources": r"^\[sub_resource .*$",
        "connections": r"^\[connection .*$",
    }
    return {name: re.findall(pattern, text, flags=re.MULTILINE) for name, pattern in patterns.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("base", type=Path)
    ap.add_argument("actual", type=Path)
    ap.add_argument("--manifest", type=Path, default=None)
    ap.add_argument("--old-text", default=None)
    ap.add_argument("--new-text", default=None)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    if args.manifest is not None:
        mod = json.loads(args.manifest.read_text(encoding="utf-8"))
        if len(mod.get("patches", [])) != 1:
            raise SystemExit("ERROR: scene resource contract requires exactly one declared patch")
        patch = mod["patches"][0]
        old_text = patch["old_text"]
        new_text = patch["new_text"]
    elif args.old_text is not None and args.new_text is not None:
        old_text = args.old_text
        new_text = args.new_text
    else:
        raise SystemExit("ERROR: provide --manifest or both --old-text and --new-text")
    base_path = args.base.resolve()
    actual_path = args.actual.resolve()
    # Preserve CRLF exactly; the production patcher operates on bytes.
    base = base_path.read_bytes().decode("utf-8")
    actual = actual_path.read_bytes().decode("utf-8")
    errors: list[str] = []
    if base.count(old_text) != 1:
        errors.append(f"base old-text occurrence != 1: {base.count(old_text)}")
    if actual.count(new_text) != 1:
        errors.append(f"actual new-text occurrence != 1: {actual.count(new_text)}")
    if old_text not in base or new_text not in actual:
        errors.append("declared old/new text missing")
    normalized_base = base.replace(old_text, "<DECLARED_RESOURCE_PATCH>")
    normalized_actual = actual.replace(new_text, "<DECLARED_RESOURCE_PATCH>")
    if normalized_base != normalized_actual:
        errors.append("content differs outside declared resource property")
    base_tokens = structural_tokens(base)
    actual_tokens = structural_tokens(actual)
    token_diffs = {
        key: {"base": base_tokens[key], "actual": actual_tokens[key]}
        for key in base_tokens
        if base_tokens[key] != actual_tokens[key]
    }
    if token_diffs:
        errors.append("structural token collections changed")
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "base": str(base_path),
        "actual": str(actual_path),
        "base_sha256": sha(base_path.read_bytes()),
        "actual_sha256": sha(actual_path.read_bytes()),
        "declared_old_text": old_text,
        "declared_new_text": new_text,
        "structural_token_diffs": token_diffs,
        "errors": errors,
        "verdict": "PASS" if not errors else "FAIL",
        "proves": "the scene differs only in the declared property and structural node/resource references are unchanged",
        "not_proven": "runtime rendering, gameplay behavior, or visual quality beyond the targeted property",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"errors": errors, "structural_token_diff_count": len(token_diffs), "verdict": report["verdict"]}, ensure_ascii=False))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
