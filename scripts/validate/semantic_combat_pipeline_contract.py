#!/usr/bin/env python3
"""B1-X3 semantic contract check (runnable verification, no game exec).

Pins the combat pipeline contract discovered in the C0 audit:
  1. File SHA canaries (preimage drift detection).
  2. Anchor substrings at recorded line numbers (cast/cooldown/projectile/
     damage/event-dispatch chains).
  3. X1/X2 scope guard: no tracked mod patches Player.gd / Mob.gd.
  4. feat-tce-context manifest invariants (dependency, scope, target hash).
  5. No host absolute paths in new B1-X3 files.

Usage (from any repo path):
    python scripts/validate/semantic_combat_pipeline_contract.py
    python scripts/validate/semantic_combat_pipeline_contract.py --evidence docs/ai/audits/B1-X3-combat-pipeline-evidence.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def repo_root() -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return Path(out)
    except subprocess.CalledProcessError:
        return Path(__file__).resolve().parents[2]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", type=Path, default=Path("docs/ai/audits/B1-X3-combat-pipeline-evidence.json"))
    args = ap.parse_args()

    root = repo_root()
    evidence_path = args.evidence if args.evidence.is_absolute() else root / args.evidence
    fails: list[str] = []
    checks: list[tuple[str, bool]] = []

    def check(label: str, ok: bool) -> None:
        checks.append((label, ok))
        if not ok:
            fails.append(label)

    # --- 0. evidence file ---
    if not evidence_path.is_file():
        fails.append(f"evidence json missing: {evidence_path}")
        print("FAIL: evidence json missing")
        return 1
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    recovered = root / "04_recovered"
    check(f"04_recovered exists (junction) at {recovered}", recovered.is_dir())

    # --- 1. file SHA canaries ---
    for canary in evidence.get("file_canaries", []):
        rel = canary["relpath"]
        target = recovered / rel
        if not target.is_file():
            check(f"canary file missing: {rel}", False)
            continue
        live = sha256_path(target)
        check(f"sha canary {rel}", live == canary["sha256"])

    # --- 2. anchors ---
    for anchor in evidence.get("anchors", []):
        rel = anchor["relpath"]
        line = int(anchor["line"])
        needle = anchor["needle"]
        target = recovered / rel
        if not target.is_file():
            check(f"anchor file missing: {rel}", False)
            continue
        lines = target.read_text(encoding="utf-8").split("\n")
        ok = line <= len(lines) and needle in lines[line - 1]
        check(f"anchor {rel}:{line} {needle!r}", ok)

    # --- 3. scope guard: patch paths across tracked mods ---
    mods_root = root / "mods"
    banned = {"Scenes/Player/Player.gd", "Scenes/Mobs/Mob.gd"}
    violations: list[str] = []
    for mod_json in sorted(mods_root.rglob("mod.json")):
        try:
            data = json.loads(mod_json.read_text(encoding="utf-8"))
        except Exception as exc:
            check(f"mod json parse {mod_json}", False)
            continue
        for patch in data.get("patches", []):
            p = patch.get("path", "")
            if p in banned:
                violations.append(f"{mod_json.relative_to(root).as_posix()} patches {p}")
    check("X1/X2 scope guard (no patch touches Player.gd/Mob.gd)", not violations)
    for v in violations:
        print(f"    scope violation: {v}")

    # --- 4. feat-tce-context manifest invariants ---
    ctx_mod = mods_root / "feat-tce-context" / "mod.json"
    if ctx_mod.is_file():
        ctx = json.loads(ctx_mod.read_text(encoding="utf-8"))
        check("feat-tce-context depends on feat-tce", "feat-tce" in ctx.get("dependencies", []))
        check(
            "feat-tce-context target_original_sha256 == C7B5D5A5...",
            ctx.get("target_original_sha256", "").upper() == "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209",
        )
        ctx_paths = {p.get("path") for p in ctx.get("patches", [])}
        check(
            "feat-tce-context patches only X3-owned files",
            ctx_paths <= {"Scenes/Stats.gd", "Scenes/Skills/GenericSkill.gd"},
        )
        # per-file preimage: Stats.gd pristine + GenericSkill.gd pristine
        for patch in ctx.get("patches", []):
            rel = patch.get("path", "")
            expected = {
                "Scenes/Stats.gd": "C187245E4F475E0928252610BB9D6D27FCB4A23C68754B4409DF5A6EB9997234",
                "Scenes/Skills/GenericSkill.gd": "0ED26958CFCCA8C18EFFDA48E52C9978BB377522444A1C98712B29A14468BF6B",
            }.get(rel, "")
            check(f"feat-tce-context preimage {rel}", patch.get("preimage_sha256", "").lower() == expected.lower())
    else:
        check("feat-tce-context manifest exists", False)

    # --- 5. no host absolute paths in new B1-X3 files ---
    # Patterns are assembled with chr(92) so the scanner never matches itself.
    # In regex language a literal backslash needs escaping, hence doubled chars.
    # JSON escape lookahead excludes false positives from "\n"/"\t" escape bytes.
    bs = chr(92)
    json_escape = '["' + bs + 'bfnrtu/0-9]'
    abs_re = re.compile(
        "[" + "A-Za-z" + "]:" + bs + bs + "(?!" + json_escape + ")"  # drive letter + backslash
        + "|[" + "A-Za-z" + "]:" + "/"                                # drive letter + slash
        + "|" + bs + bs + bs + bs                                     # UNC prefix
    )
    scan_paths = [
        root / "mods" / "feat-tce-context",
        root / "docs" / "ai" / "audits" / "B1-X3-combat-pipeline.md",
        root / "docs" / "ai" / "audits" / "B1-X3-combat-pipeline-evidence.json",
        root / "scripts" / "validate" / "semantic_combat_pipeline_contract.py",
    ]
    for sp in scan_paths:
        if sp.is_file():
            text = sp.read_text(encoding="utf-8")
            bad = abs_re.findall(text)
            check(f"no absolute host path in {sp.relative_to(root).as_posix()}", not bad)
            for b in bad:
                print(f"    absolute path candidate: {b!r}")
        elif sp.is_dir():
            for f in sorted(sp.rglob("*")):
                if f.is_file():
                    text = f.read_text(encoding="utf-8", errors="replace")
                    bad = abs_re.findall(text)
                    check(f"no absolute host path in {f.relative_to(root).as_posix()}", not bad)
                    for b in bad:
                        print(f"    absolute path candidate: {b!r}")

    # --- verdict ---
    passed = len(checks) - len(fails)
    print(f"\ncontract checks: {passed}/{len(checks)} passed")
    if fails:
        for f in fails:
            print(f"FAIL: {f}")
        return 1
    print("verdict: PASS")
    print("proves: recovered sources match pinned canaries at recorded anchors; "
          "X1/X2 scope untouched; feat-tce-context declared invariants hold; no host paths in new files")
    print("not_proven: runtime cooldown floor, chain cost, FX density, TCE end-to-end (see audit §5)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())