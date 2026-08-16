#!/usr/bin/env python3
"""Resolve a declarative Mod dependency chain into one reproducible manifest.

The resolver does not edit game content.  It locates manifests by Mod ID,
checks the dependency graph, rejects conflicting declarations, and writes a
flattened manifest suitable for the existing fail-closed build stages.
Repeated declarations of the same unit or asset are allowed only when their
complete transformation is identical; the first declaration is retained.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def normalized_patch(value: dict[str, Any]) -> dict[str, Any]:
    """Compare declarations by their application semantics, not omissions."""
    result = dict(value)
    result.setdefault("expected_occurrences", 1)
    result.setdefault("classification", "TEXT_PATCH")
    result.setdefault("placeholders", [])
    result.setdefault("format_tokens", [])
    return result


def find_manifests(mods_root: Path) -> dict[str, Path]:
    by_id: dict[str, Path] = {}
    for path in sorted(mods_root.rglob("mod.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        mod_id = data.get("id")
        if not isinstance(mod_id, str) or not mod_id:
            raise SystemExit(f"ERROR: manifest has no non-empty id: {path}")
        if mod_id in by_id:
            raise SystemExit(f"ERROR: duplicate Mod ID {mod_id}: {by_id[mod_id]} and {path}")
        by_id[mod_id] = path
    return by_id


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--mods-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    root_manifest = args.manifest.resolve()
    mods_root = args.mods_root.resolve()
    if not root_manifest.is_file() or not mods_root.is_dir():
        raise SystemExit("ERROR: root manifest or mods root is missing")

    by_id = find_manifests(mods_root)
    root_data = json.loads(root_manifest.read_text(encoding="utf-8"))
    root_id = root_data.get("id")
    if by_id.get(root_id) != root_manifest:
        raise SystemExit(f"ERROR: root manifest is not the indexed manifest for id {root_id}: {root_manifest}")

    visiting: set[str] = set()
    visited: set[str] = set()
    ordered: list[tuple[str, Path, dict[str, Any]]] = []

    def visit(mod_id: str) -> None:
        if mod_id in visiting:
            raise SystemExit(f"ERROR: dependency cycle at {mod_id}")
        if mod_id in visited:
            return
        path = by_id.get(mod_id)
        if path is None:
            raise SystemExit(f"ERROR: dependency manifest not found for {mod_id}")
        visiting.add(mod_id)
        data = json.loads(path.read_text(encoding="utf-8"))
        for dependency in data.get("dependencies", []):
            if not isinstance(dependency, str) or not dependency:
                raise SystemExit(f"ERROR: invalid dependency in {path}: {dependency!r}")
            visit(dependency)
        visiting.remove(mod_id)
        visited.add(mod_id)
        ordered.append((mod_id, path, data))

    visit(root_id)

    target_hashes = {data.get("target_original_sha256") for _, _, data in ordered}
    if len(target_hashes) != 1 or None in target_hashes:
        raise SystemExit(f"ERROR: dependency chain has inconsistent target_original_sha256 values: {target_hashes}")

    patches: list[dict[str, Any]] = []
    patch_by_unit: dict[str, dict[str, Any]] = {}
    patch_source: dict[str, str] = {}
    assets: list[dict[str, Any]] = []
    asset_by_path: dict[str, dict[str, Any]] = {}
    asset_source: dict[str, str] = {}
    tests: list[str] = []
    for mod_id, path, data in ordered:
        for patch in data.get("patches", []):
            unit_id = patch.get("unit_id")
            key = str(unit_id) if unit_id else f"path:{patch.get('path')}:{len(patches)}"
            if key in patch_by_unit:
                if canonical(normalized_patch(patch_by_unit[key])) != canonical(normalized_patch(patch)):
                    raise SystemExit(
                        f"ERROR: conflicting declaration for {key}: "
                        f"{patch_source[key]} vs {path}"
                    )
                continue
            patch_by_unit[key] = normalized_patch(patch)
            patch_source[key] = str(path)
            patches.append(patch_by_unit[key])
        for asset in data.get("asset_overlays", []):
            key = str(asset.get("path"))
            if key in asset_by_path:
                if canonical(asset_by_path[key]) != canonical(asset):
                    raise SystemExit(
                        f"ERROR: conflicting asset declaration for {key}: "
                        f"{asset_source[key]} vs {path}"
                    )
                continue
            asset_by_path[key] = asset
            asset_source[key] = str(path)
            assets.append(asset)
        for test in data.get("tests", []):
            if test not in tests:
                tests.append(test)

    source_manifests = [
        {
            "id": mod_id,
            "path": path.relative_to(mods_root.parent).as_posix(),
            "sha256": sha256_path(path),
        }
        for mod_id, path, _ in ordered
    ]
    resolved = {
        "id": root_id,
        "version": root_data.get("version", "0.0.0"),
        "resolved": True,
        "resolution_order": [mod_id for mod_id, _, _ in ordered],
        "source_manifests": source_manifests,
        "patch_type": "RESOLVED_MOD_CHAIN",
        "target_original_sha256": next(iter(target_hashes)),
        "dependencies": [],
        "conflicts": root_data.get("conflicts", []),
        "scope": root_data.get("scope", root_id),
        "patches": patches,
        "asset_overlays": assets,
        "tests": tests,
        "proves": "the dependency chain was resolved from indexed manifests with identical duplicate declarations and no conflicts",
        "not_proven": "patch application, pack/EXE structure, runtime behavior, translation quality, or release readiness",
    }
    report = {
        "root_manifest": str(root_manifest),
        "mods_root": str(mods_root),
        "resolution_order": resolved["resolution_order"],
        "source_manifests": source_manifests,
        "patch_count": len(patches),
        "asset_overlay_count": len(assets),
        "duplicate_patch_declarations_collapsed": sum(
            len(data.get("patches", [])) for _, _, data in ordered
        ) - len(patches),
        "duplicate_asset_declarations_collapsed": sum(
            len(data.get("asset_overlays", [])) for _, _, data in ordered
        ) - len(assets),
        "verdict": "PASS",
        "proves": resolved["proves"],
        "not_proven": resolved["not_proven"],
    }
    output = args.output.resolve()
    report_path = args.report.resolve()
    if output.exists() or report_path.exists():
        raise SystemExit("ERROR: refusing to overwrite resolved manifest or report")
    output.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(resolved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"resolution_order": resolved["resolution_order"], "patch_count": len(patches), "asset_overlay_count": len(assets), "verdict": "PASS"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
