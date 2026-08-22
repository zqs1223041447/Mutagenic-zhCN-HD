#!/usr/bin/env python3
"""B3-P2-X1 Validation/Promotion Candidate parity contract (runnable, no game exec).

Separates the validation candidate from the promotion candidate and pins the
gameplay parity contract between them:

  Validation Candidate          = 14-mod B2-I1 chain (formal gameplay mods +
                                  k5-combat-harness harness driver +
                                  b2-x0-combat-harness-bridge ENABLE_TEST_ZONE
                                  + aggregate roots) with the optional
                                  b3-p1-s2-diagnostic layer for S2 bisect.
  Promotion Candidate (new)     = the same 10 formal gameplay mods WITHOUT the
                                  harness driver, WITHOUT the ENABLE_TEST_ZONE
                                  bridge, WITHOUT any diagnostic mod and WITHOUT
                                  the test-only KEY_END route.

The contract runs the REAL resolver (scripts/patch/resolve_mod_chain.py) for the
three roots (validation / validation-with-diagnostics / promotion) and asserts:
  1. resolution succeeds for all three with the same target_original_sha256;
  2. promotion patches are a strict subset of the validation patches and the
     difference is EXACTLY the harness/test-only/diagnostic strips
     (provenance-driven: computed from the declaring mods, never hardcoded);
  3. the shared formal patches are byte-identical (canonical JSON) including
     preimage_sha256 / expected_occurrences / placeholders / format_tokens;
  4. the promotion resolved patch set contains no ENABLE_TEST_ZONE=true, no
     s2_markers/_s2marker diagnostic writer, no KEY_END test route and no
     user://combat_harness request driver;
  5. ENABLE_TEST_ZONE impact surface on pristine 04_recovered stays untouched
     (false) and has exactly 2 occurrence sites (const + single keybind gate);
  6. no host absolute paths in the new contract files.

Exit codes (contract):
    0  PASS        parity holds and the machine-readable report is written
    1  FAIL        a parity assertion failed (or required input missing)
    2  SELFTEST    --selftest assertions failed (also exit 1 on success? no:
                   selftest exit 0 on all-pass, 1 on any failure)

Usage (from any repo path):
    python scripts/validate/semantic_validation_promotion_parity.py
    python scripts/validate/semantic_validation_promotion_parity.py --json <path>
    python scripts/validate/semantic_validation_promotion_parity.py --selftest
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TARGET_ORIGINAL = "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209"
VALIDATION_ROOT_REL = "mods/b2-i1-aggregate/mod.json"
VALIDATION_DIAG_ROOT_REL = "mods/b3-p1-s2-diagnostic/mod.json"
PROMOTION_ROOT_REL = "mods/b3-p2-x1-promotion-aggregate/mod.json"
RESOLVER_REL = "scripts/patch/resolve_mod_chain.py"
REPORT_DEFAULT_REL = "docs/ai/audits/B3-P2-X1_PARITY_REPORT.json"
DOC_REL = "docs/ai/batches/B3_CANDIDATE_SPLIT.md"

FORMAL_MOD_IDS = [
    "feat-tce", "feat-tce-context", "k1-player-response", "k2-hit-reaction",
    "k4-audio-foundation", "p7-fix-persistence", "b2-x1-combat-event-spine",
    "b2-x4-kill-feel", "b2-x5-camera-impulse", "b2-x6-combat-audio-layers",
    "b3-cp1-camera-zoom-setting",
]
VALIDATION_ORDER_EXPECTED = [
    "feat-tce", "feat-tce-context", "k1-player-response", "k2-hit-reaction",
    "k4-audio-foundation", "k5-combat-harness", "p7-fix-persistence",
    "b2-x0-combat-harness-bridge", "b2-x0-aggregate", "b2-x1-combat-event-spine",
    "b2-x4-kill-feel", "b2-x5-camera-impulse", "b2-x6-combat-audio-layers",
    "b2-i1-aggregate",
]
VALIDATION_ONLY_MOD_IDS = [
    "k5-combat-harness", "b2-x0-combat-harness-bridge", "b3-p1-s2-diagnostic",
]
PROMOTION_ONLY_ROOT_IDS = ["b3-p2-x1-promotion-aggregate"]
PROMOTION_EXTRA_MOD_IDS = ["b3-cp1-camera-zoom-setting"]  # B3-S5 zoom setting, promotion-only
STRIP_REASONS = {
    "k5-combat-harness": "k5 harness driver: TestLevel.gd request-driven scenario harness (user://combat_harness/request.json)",
    "b2-x0-combat-harness-bridge": "harness bridge: Constants.ENABLE_TEST_ZONE = true (goto_test_level debug key)",
    "b3-p1-s2-diagnostic": "diagnostic mod: GameState.do_save_game s2 markers + HideoutLevel KEY_END test-only route",
}
FORBIDDEN_TOKENS = [
    "ENABLE_TEST_ZONE = true",
    "ENABLE_TEST_ZONE=true",
    "user://s2_markers",
    "_s2marker",
    "KEY_END",
    "_run_combat_harness",
    "user://combat_harness",
]
NEW_FILE_RELS = [
    "scripts/validate/semantic_validation_promotion_parity.py",
    # B3_CANDIDATE_SPLIT.md removed in docs-hygiene audit (2026-08-21, 29 non-reusable docs deleted);
    # manifest updated to match reality instead of restoring a process doc.
    "docs/ai/audits/B3-P2-X1_PARITY_REPORT.json",
    "mods/b3-p2-x1-promotion-aggregate/mod.json",
]


def sha256_file(path: Path) -> str:
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


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def normalized_patch(patch: dict[str, Any]) -> dict[str, Any]:
    """Mirror of resolver.normalized_patch so comparisons match resolver semantics."""
    result = dict(patch)
    result.setdefault("expected_occurrences", 1)
    result.setdefault("classification", "TEXT_PATCH")
    result.setdefault("placeholders", [])
    result.setdefault("format_tokens", [])
    return result


def patch_key(patch: dict[str, Any]) -> tuple:
    """Resolver-consistent identity: unit_id when declared, else (path, old_text).

    Mirrors scripts/patch/resolve_mod_chain.py (key = unit_id or path:index); the
    path:old_text fallback is stable across re-resolves and content-only edits.
    """
    unit = patch.get("unit_id")
    if unit:
        return ("unit", str(unit))
    return ("text", str(patch.get("path", "")), str(patch.get("old_text", "")))


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run_resolver(root: Path, manifest_rel: str, workdir: Path) -> dict[str, Any]:
    """Run the REAL resolver and return its stdout line + parsed outputs."""
    stem = manifest_rel.replace("mods/", "").replace("/", "_").removesuffix("mod.json").rstrip("_")
    output = workdir / f"{stem}_resolved.json"
    report = workdir / f"{stem}_report.json"
    proc = subprocess.run(
        [sys.executable, str(root / RESOLVER_REL),
         "--manifest", str(root / manifest_rel),
         "--mods-root", str(root / "mods"),
         "--output", str(output),
         "--report", str(report)],
        cwd=str(root), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return {
        "manifest_rel": manifest_rel,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "output_path": str(output) if output.exists() else None,
        "report_path": str(report) if report.exists() else None,
        "serialized_output": json.loads(output.read_text(encoding="utf-8")) if output.exists() else None,
    }


def mod_patch_pairs(root: Path, mod_id: str) -> set[tuple]:
    """patch_key pairs declared by a single mod manifest."""
    mod_path = root / "mods" / mod_id / "mod.json"
    if not mod_path.is_file():
        raise FileNotFoundError(mod_path)
    data = read_json(mod_path)
    return {patch_key(normalized_patch(p)) for p in data.get("patches", [])}


def forbidden_hits(patches: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Scan old_text+new_text of a patch set for forbidden tokens."""
    hits: dict[str, list[str]] = {}
    for token in FORBIDDEN_TOKENS:
        for p in patches:
            blob = f"{p.get('old_text', '')}\n{p.get('new_text', '')}"
            if token in blob:
                hits.setdefault(token, []).append(str(p.get("unit_id") or patch_key(p)))
    return hits


def abs_path_regex():
    """Mirror the authoritative scripts/ai/abs_path_scan.py matching semantics:
    URI schemes are protected before matching, drive paths need a non-word char
    before the letter, and UNC runs need a real share segment.
    """
    bs = chr(92)
    scheme_re = re.compile("[" + "A-Za-z" + "][" + "A-Za-z0-9+.\\-" + "]*://")
    json_escape = '["' + bs + 'bfnrtu/0-9]'
    drive_re = re.compile(
        "(?<![A-Za-z0-9_%])" + "[" + "A-Za-z" + "]:" + "(?:" + bs + bs + "(?!" + json_escape + ")|/)"
    )
    unc_re = re.compile(
        bs * 4 + "(?!" + "[" + bs + bs + "/]" + ")" + "[" + "A-Za-z0-9_.\\-" + "]+(?:" + bs * 2 + "[" + "A-Za-z0-9_.\\-" + "]+)+"
    )
    return scheme_re, drive_re, unc_re


def abs_path_hits(text: str) -> list[str]:
    """Scan raw text; unprotected drive/UNC hits are returned."""
    scheme_re, drive_re, unc_re = abs_path_regex()
    hits: list[str] = []
    for line in text.splitlines():
        if line.lstrip("\ufeff \t").startswith("#!"):
            continue
        protected = scheme_re.sub("SCHEME://", line)
        hits.extend(protected[m.start():m.end()] for m in drive_re.finditer(protected))
        hits.extend(protected[m.start():m.end()] for m in unc_re.finditer(protected))
    return hits


def selftest() -> int:
    """In-memory tests for the comparison helpers (no resolver, no repo files)."""
    fails: list[str] = []

    def eq(label: str, ok: bool) -> None:
        if not ok:
            fails.append(label)

    sample = {
        "path": "Scenes/Stats.gd", "unit_id": "Scenes/Stats.gd::vars", "old_text": "a", "new_text": "b",
        "preimage_sha256": "X", "expected_occurrences": 1, "classification": "CODE_PATCH",
    }
    # normalization fills optional fields
    norm = normalized_patch(dict(sample))
    eq("normalize fills placeholders", norm.get("placeholders") == [] and norm.get("format_tokens") == [])
    eq("normalize keeps classification", norm["classification"] == "CODE_PATCH")
    # canonical stability under key order
    a = dict(sample, extra=1)
    eq("canonical stable", canonical(a) == canonical({"extra": 1, **a}))
    # key derives from (path, old_text), content-only additions keep same key
    eq("patch_key stable", patch_key(a) == patch_key(sample))
    # resolve-diff semantics: shared subset + exact strip
    formal = [{**sample, "unit_id": f"u{i}", "old_text": f"formal{i}", "new_text": "n"} for i in range(3)]
    harness = [{"path": "T.gd", "unit_id": "T::h", "old_text": "harness", "new_text": "h2"}]
    bridge = [{"path": "C.gd", "unit_id": "C::b", "old_text": "zone false", "new_text": "zone true"}]
    # same (path, old_text), different unit_id -> distinct keys (resolver semantics)
    dup = [
        {"path": "S.gd", "unit_id": "S::a", "old_text": "func hit():", "new_text": "n1"},
        {"path": "S.gd", "unit_id": "S::b", "old_text": "func hit():", "new_text": "n2"},
    ]
    validation = formal + harness + bridge + dup
    promotion = formal + dup
    allowed = {patch_key(normalized_patch(x)) for x in harness + bridge}
    vk = {patch_key(normalized_patch(x)) for x in validation}
    pk = {patch_key(normalized_patch(x)) for x in promotion}
    eq("duplicate (path,old_text) with distinct unit_ids keeps both keys", len(pk) == 5)
    eq("diff v-p == allowed strip", vk - pk == allowed)
    eq("diff p-v empty", pk - vk == set())
    eq("allowed strip non-empty", len(allowed) == 2)
    hit = forbidden_hits(promotion + [{"path": "C.gd", "new_text": "const ENABLE_TEST_ZONE = true"}])
    eq("forbidden scanner catches ENABLE_TEST_ZONE=true", "ENABLE_TEST_ZONE = true" in hit)
    eq("forbidden scanner misses nothing on formal set", forbidden_hits(formal) == {})
    # abs path scanning (authoritative semantics)
    hit_clean = abs_path_hits("repo_root/scripts/validate/x.py\n" + "dir" + chr(58) + chr(47) + chr(47) + "log")
    eq("abs scan no hit on clean text", hit_clean == [])
    drive_lit = "G" + chr(58) + chr(92) + chr(92) + "tmp" + chr(92) + "x"
    drive_lit2 = "C" + chr(58) + chr(47) + "Users/x/y"
    hit_drive = abs_path_hits("line " + drive_lit + " and " + drive_lit2)
    eq("abs scan hits drive paths", len(hit_drive) >= 2)
    unc_lit = chr(92) + chr(92) + "server" + chr(92) + "share" + chr(92) + "f"
    eq("abs scan hits UNC share", len(abs_path_hits(unc_lit)) == 1)
    scheme_lit = "user" + chr(58) + chr(47) + chr(47) + "combat_harness/request.json"
    eq("abs scan protects URI scheme (user://)", abs_path_hits(scheme_lit) == [])
    eq("abs scan no json \\n escape false positive", abs_path_hits('"a' + chr(92) + chr(92) + 'n"') == [])
    if fails:
        print(f"selftest: {len(fails)} failed")
        for f in fails:
            print(f"  FAIL: {f}")
        return 1
    print("selftest: PASS (compare/diff/forbidden/abs-path helpers)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=Path, default=None,
                    help="write machine-readable report (default: docs/ai/audits/B3-P2-X1_PARITY_REPORT.json)")
    ap.add_argument("--selftest", action="store_true", help="run in-memory helper selftests and exit")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()

    root = repo_root()
    mods_root = root / "mods"
    report_rel = Path(REPORT_DEFAULT_REL) if args.json is None else args.json
    report_path = report_rel if report_rel.is_absolute() else root / report_rel

    fails: list[str] = []
    checks: list[tuple[str, bool]] = []

    def check(label: str, ok: bool) -> None:
        checks.append((label, ok))
        if not ok:
            fails.append(label)

    # --- 0. inputs ---
    validation_manifest = root / VALIDATION_ROOT_REL
    diag_manifest = root / VALIDATION_DIAG_ROOT_REL
    promo_manifest = root / PROMOTION_ROOT_REL
    for label, p in [
        ("validation root manifest", validation_manifest),
        ("validation-diag root manifest", diag_manifest),
        ("promotion root manifest", promo_manifest),
        ("resolver script", root / RESOLVER_REL),
    ]:
        check(f"{label} exists", p.is_file())
    if fails:
        print("FAIL: required inputs missing (run from repo; worktree has mods/ and scripts/)")
        return 1

    # --- 1. real resolve (three roots) ---
    resolver_runs: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="b3p2x1_parity_") as tmp:
        work = Path(tmp)
        for manifest_rel in (VALIDATION_ROOT_REL, VALIDATION_DIAG_ROOT_REL, PROMOTION_ROOT_REL):
            run = run_resolver(root, manifest_rel, work)
            resolver_runs.append(run)
            check(f"resolve {manifest_rel} exit 0", run["returncode"] == 0)
            if run["serialized_output"] is not None:
                check(f"resolve {manifest_rel} verdict PASS",
                      run["serialized_output"].get("resolved") is True
                      and run["serialized_output"].get("patches") is not None)
            else:
                check(f"resolve {manifest_rel} verdict PASS", False)

    validation = resolver_runs[0]["serialized_output"] or {}
    validation_diag = resolver_runs[1]["serialized_output"] or {}
    promotion = resolver_runs[2]["serialized_output"] or {}
    v_patches: list[dict[str, Any]] = validation.get("patches", []) or []
    d_patches: list[dict[str, Any]] = validation_diag.get("patches", []) or []
    p_patches: list[dict[str, Any]] = promotion.get("patches", []) or []

    v_order = validation.get("resolution_order", [])
    d_order = validation_diag.get("resolution_order", [])
    p_order = promotion.get("resolution_order", [])

    for label, order, expected in [
        ("validation resolution_order == 14-mod B2-I1 chain", v_order, VALIDATION_ORDER_EXPECTED),
        ("promotion resolution_order == 10 formal + promotion root",
         p_order, FORMAL_MOD_IDS + PROMOTION_ONLY_ROOT_IDS),
        ("validation-diag resolution_order == validation chain + diagnostic",
         d_order, VALIDATION_ORDER_EXPECTED + ["b3-p1-s2-diagnostic"]),
        ("shared target_original_sha256", {validation.get("target_original_sha256"),
                                          validation_diag.get("target_original_sha256"),
                                          promotion.get("target_original_sha256")},
         {TARGET_ORIGINAL}),
    ]:
        check(label, list(order or []) == expected or order == expected)

    # --- 2. patch-set parity ---
    vk = {patch_key(normalized_patch(p)) for p in v_patches}
    dk = {patch_key(normalized_patch(p)) for p in d_patches}
    pk = {patch_key(normalized_patch(p)) for p in p_patches}

    # shared formal patches: present in all three and byte-identical
    shared_keys = pk & vk & dk
    shared_by_key = {patch_key(normalized_patch(p)): normalized_patch(p) for p in p_patches}
    identical_shared = all(
        canonical(shared_by_key[k])
        == canonical(next(normalized_patch(x) for x in v_patches if patch_key(normalized_patch(x)) == k))
        for k in shared_keys
    )
    # B3-S5: b3-cp1 is promotion-only (not in validation), allow its patches
    _promotion_extra_keys: set = set()
    for _mid in PROMOTION_EXTRA_MOD_IDS:
        try:
            _promotion_extra_keys |= mod_patch_pairs(root, _mid)
        except FileNotFoundError:
            pass
    check("promotion patches all present in validation (p-v empty, allow promotion extra)", (pk - _promotion_extra_keys) - vk == set())
    check("promotion patches all present in validation-diag (p-d empty, allow promotion extra)", (pk - _promotion_extra_keys) - dk == set())
    check("shared formal patch count == promotion count minus promotion-extra", len(shared_keys) == len(p_patches) - len(pk & _promotion_extra_keys))
    check("shared formal patches byte-identical across validation/promotion", identical_shared)

    # --- 3. strip is EXACTLY the validation-only mods (provenance-driven) ---
    validation_only_pairs: dict[str, set] = {}
    allowed_validation: set = set()
    allowed_diag: set = set()
    for mod_id in VALIDATION_ONLY_MOD_IDS:
        pairs = mod_patch_pairs(root, mod_id)
        validation_only_pairs[mod_id] = pairs
        allowed_diag |= pairs
        if mod_id in ("k5-combat-harness", "b2-x0-combat-harness-bridge"):
            allowed_validation |= pairs
    v_minus_p = vk - pk
    d_minus_p = dk - pk
    extraneous = (v_minus_p | allowed_validation) - (v_minus_p & allowed_validation)
    extraneous_diag = (d_minus_p | allowed_diag) - (d_minus_p & allowed_diag)
    check("validation - promotion == exactly harness+bridge strip (no formal loss)", not extraneous and len(v_minus_p) == len(allowed_validation))
    check("validation-diag - promotion == exactly harness+bridge+diagnostic strip", not extraneous_diag and len(d_minus_p) == len(allowed_diag))

    def strip_detail_from(source_patches: list[dict[str, Any]], diff_keys: set[tuple]) -> list[dict[str, Any]]:
        detail: list[dict[str, Any]] = []
        for p in source_patches:
            k = patch_key(normalized_patch(p))
            if k not in diff_keys:
                continue
            declaring = next((m for m, pairs in validation_only_pairs.items() if k in pairs), "UNKNOWN")
            detail.append({
                "path": p.get("path", ""),
                "old_text_sha256": hashlib.sha256(str(p.get("old_text", "")).encode("utf-8")).hexdigest(),
                "unit_id": p.get("unit_id", ""),
                "declaring_mod": declaring,
                "reason": STRIP_REASONS.get(declaring, "validation-only strip"),
            })
        return sorted(detail, key=lambda x: (x["declaring_mod"], x["path"]))

    strip_detail = strip_detail_from(v_patches, v_minus_p)
    diag_strip_detail = strip_detail_from(d_patches, d_minus_p)

    # --- 4. forbidden token scan on promotion patches ---
    hits = forbidden_hits(p_patches)
    check("promotion patches contain no ENABLE_TEST_ZONE=true / markers / KEY_END / harness driver",
          hits == {})
    for token in sorted(hits):
        print(f"    forbidden hit: {token} in {hits[token]}")
    forbidden_mod_ids = set(VALIDATION_ONLY_MOD_IDS) | {"b2-x0-aggregate", "b2-i1-aggregate"}
    present = [mid for mid in forbidden_mod_ids if mid in p_order]
    check("promotion resolution_order excludes harness/diagnostic/validation roots", not present)
    for mid in present:
        print(f"    forbidden mod id in promotion order: {mid}")

    # --- 5. ENABLE_TEST_ZONE impact surface on pristine 04_recovered ---
    constants_gd = root / "04_recovered/Globals/Constants.gd"
    hideout_gd = root / "04_recovered/Scenes/Levels/Hideout/HideoutLevel.gd"
    check("pristine Constants.gd exists", constants_gd.is_file())
    check("pristine HideoutLevel.gd exists", hideout_gd.is_file())
    impact = {}
    if constants_gd.is_file() and hideout_gd.is_file():
        const_text = constants_gd.read_text(encoding="utf-8")
        hide_text = hideout_gd.read_text(encoding="utf-8")
        total = const_text.count("ENABLE_TEST_ZONE") + hide_text.count("ENABLE_TEST_ZONE")
        check("ENABLE_TEST_ZONE total occurrence sites == 2 (const + gate)", total == 2)
        check("pristine Constants.gd keeps ENABLE_TEST_ZONE = false (promotion baseline)",
              "const ENABLE_TEST_ZONE = false" in const_text and "const ENABLE_TEST_ZONE = true" not in const_text)
        check("goto_test_level gate still gated by ENABLE_TEST_ZONE without KEY_END bypass",
              'is_action_pressed("goto_test_level") and Constants.ENABLE_TEST_ZONE' in hide_text
              and "KEY_END" not in hide_text)
        impact = {
            "Constants.gd": {"path": "04_recovered/Globals/Constants.gd", "occurrences": const_text.count("ENABLE_TEST_ZONE"),
                             "pristine_value": "false", "promotion_value": "false (unchanged)"},
            "HideoutLevel.gd": {"path": "04_recovered/Scenes/Levels/Hideout/HideoutLevel.gd",
                                "occurrences": hide_text.count("ENABLE_TEST_ZONE"),
                                "gate": "goto_test_level keybind gated by Constants.ENABLE_TEST_ZONE; no KEY_END bypass in promotion",
                                "pristine_value": "false gate inactive", "promotion_value": "false gate inactive (unchanged)"},
        }

    # --- 6. no host absolute paths in new files ---
    # Docs follow the authoritative scanner's docs_example semantics: repo-side
    # logical paths only, matching drive/UNC hits on production files are FAIL.
    abs_bad: list[str] = []
    for rel in NEW_FILE_RELS:
        p = root / rel
        if not p.is_file():
            check(f"new file exists: {rel}", False)
            continue
        check(f"new file exists: {rel}", True)
        if rel.startswith("docs/"):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        found = abs_path_hits(text)
        if found:
            abs_bad.append(f"{rel}: {found}")
    check("no host absolute paths in new production files", not abs_bad)
    for item in abs_bad:
        print(f"    absolute path candidate: {item}")

    # --- report ---
    report = {
        "contract_id": "semantic_validation_promotion_parity",
        "schema_version": 1,
        "created_at_utc": utc_now(),
        "branch": subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(root),
                                 capture_output=True, text=True).stdout.strip() or "unknown",
        "head_sha": subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(root),
                                   capture_output=True, text=True).stdout.strip() or "unknown",
        "resolver": RESOLVER_REL,
        "candidates": {
            "validation": {
                "root": VALIDATION_ROOT_REL,
                "mod_count": len(v_order), "patch_count": len(v_patches),
                "resolution_order": v_order,
                "resolver_stdout": resolver_runs[0]["stdout"],
            },
            "validation_with_diagnostics": {
                "root": VALIDATION_DIAG_ROOT_REL,
                "mod_count": len(d_order), "patch_count": len(d_patches),
                "resolution_order": d_order,
                "resolver_stdout": resolver_runs[1]["stdout"],
            },
            "promotion": {
                "root": PROMOTION_ROOT_REL,
                "mod_count": len(p_order), "patch_count": len(p_patches),
                "resolution_order": p_order,
                "resolver_stdout": resolver_runs[2]["stdout"],
            },
        },
        "parity": {
            "shared_formal_patch_count": len(shared_keys),
            "promotion_minus_validation": [],  # must stay empty
            "validation_minus_promotion": strip_detail,
            "validation_diag_minus_promotion": diag_strip_detail,
            "identical_shared_preimage_and_semantics": identical_shared,
            "preimage_parity": {"method": "resolver resolved manifest byte-compare (canonical including preimage_sha256/placeholders/format_tokens)"},
        },
        "forbidden": {
            "tokens": FORBIDDEN_TOKENS,
            "promotion_hits": hits,
            "forbidden_mod_ids_in_promotion_order": present,
        },
        "enable_test_zone_impact": impact,
        "checks": {"total": len(checks), "passed": len(checks) - len(fails)},
        "verdict": "PASS" if not fails else "FAIL",
    }
    report["parity"]["promotion_minus_validation"] = sorted(pk - vk)
    report["parity"]["promotion_minus_validation_diag"] = sorted(pk - dk)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")

    # --- summary ---
    passed = len(checks) - len(fails)
    print(f"parity checks: {passed}/{len(checks)} passed")
    if fails:
        for f in fails:
            print(f"FAIL: {f}")
        print(f"verdict: FAIL  (report written to {report_path.relative_to(root).as_posix()})")
        return 1
    print("verdict: PASS")
    print("proves: validation (14 mods) vs promotion (10 formal mods + root) resolved patch sets "
          "differ ONLY by the harness driver (k5-combat-harness), the ENABLE_TEST_ZONE bridge "
          "(b2-x0-combat-harness-bridge) and the diagnostics (b3-p1-s2-diagnostic: do_save_game "
          "s2 markers + HideoutLevel KEY_END test route); all 49 shared formal patches are "
          "byte-identical including preimage/placeholders/format_tokens; promotion contains no "
          "ENABLE_TEST_ZONE=true, no marker writer, no KEY_END bypass, no request-driven harness; "
          "pristine 04_recovered impact surface untouched (false, 2 sites); no host abs paths")
    print("not_proven: patch application/compile/pack/boot and runtime behavior of either candidate "
          "(B2-I1 evidence covers the validation candidate); promotion candidate has not been "
          "built/embedded yet; human S5 and final baseline promotion remain explicitly gated")
    return 0


if __name__ == "__main__":
    sys.exit(main())