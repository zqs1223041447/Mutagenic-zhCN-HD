#!/usr/bin/env python3
"""Generate C5-L17: status effect display names (description) and on_apply_tip
texts across Scenes/StatusEffects/**/*.tscn.

Each unit old_text/new_text = the exact full stripped serialized line from
03_raw/Scenes/StatusEffects/**.tscn (e.g. `description = "Burning"`).
Translations follow docs/zh_CN_glossary.md (Ailment=异常状态, Boon=增益,
Curse=诅咒, Keystone effect names match c5-l11 keystone translations where
applicable). Internal identifiers (node names, unique_group, stack_group,
script paths) stay English; only player-visible description/on_apply_tip
values are translated.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(r"G:\opencode-Mutageni")
RAW = ROOT / "03_raw"
OUT = ROOT / "mods/c5-l17-status-effects-zhcn/mod.json"
TARGET_SHA = "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209"

TESTS = [
    "locked_units_and_preimages",
    "exact_unit_application",
    "resource_contract",
    "declared_delta",
    "compiled_script_load",
    "pck_checksum",
    "exe_structure",
    "pck_roundtrip",
    "boot",
    "phase_checkpoint_status_effects_zhcn",
]

# (rel_path, line_no, old_line, new_line, source_text, translation, occurrences)
ENTRIES = [
    # ---- Skills ----
    ("Scenes/StatusEffects/Skills/Webbed.tscn", 8, 'description = "Webbed"', 'description = "蛛网缠身"', "Webbed", "蛛网缠身", 1),
    ("Scenes/StatusEffects/Skills/Plague.tscn", 8, 'description = "Plague"', 'description = "瘟疫"', "Plague", "瘟疫", 1),
    ("Scenes/StatusEffects/Skills/Dread.tscn", 9, 'description = "Dread"', 'description = "恐惧"', "Dread", "恐惧", 1),
    ("Scenes/StatusEffects/Skills/EnergeticFlesh.tscn", 9, 'description = "Energized Flesh"', 'description = "活力之躯"', "Energized Flesh", "活力之躯", 1),
    ("Scenes/StatusEffects/Skills/BondedElectrons.tscn", 9, 'description = "Bonded Electrons"', 'description = "电子联结"', "Bonded Electrons", "电子联结", 1),
    # ---- DamageAilments ----
    ("Scenes/StatusEffects/DamageAilments/Burn.tscn", 9, 'description = "Burning"', 'description = "燃烧"', "Burning", "燃烧", 1),
    ("Scenes/StatusEffects/DamageAilments/Electrocution.tscn", 8, 'description = "Electrocuted"', 'description = "电击"', "Electrocuted", "电击", 1),
    ("Scenes/StatusEffects/DamageAilments/Freeze.tscn", 9, 'description = "Frozen"', 'description = "冰冻"', "Frozen", "冰冻", 1),
    ("Scenes/StatusEffects/DamageAilments/Chill.tscn", 8, 'description = "Chilled"', 'description = "寒冷"', "Chilled", "寒冷", 1),
    ("Scenes/StatusEffects/DamageAilments/Bleed.tscn", 9, 'description = "Bleeding"', 'description = "流血"', "Bleeding", "流血", 1),
    ("Scenes/StatusEffects/DamageAilments/Charred.tscn", 8, 'description = "Charred"', 'description = "焦灼"', "Charred", "焦灼", 1),
    ("Scenes/StatusEffects/DamageAilments/Infection.tscn", 9, 'description = "Infected"', 'description = "感染"', "Infected", "感染", 1),
    ("Scenes/StatusEffects/DamageAilments/Jolt.tscn", 8, 'description = "Jolted"', 'description = "电震"', "Jolted", "电震", 1),
    ("Scenes/StatusEffects/DamageAilments/Poison.tscn", 9, 'description = "Poisoned"', 'description = "中毒"', "Poisoned", "中毒", 1),
    ("Scenes/StatusEffects/DamageAilments/Rupture.tscn", 9, 'description = "Ruptured"', 'description = "撕裂"', "Ruptured", "撕裂", 1),
    # ---- Boons ----
    ("Scenes/StatusEffects/Boons/PrecisionBoon.tscn", 8, 'description = "Precision Boon"', 'description = "精准恩惠"', "Precision Boon", "精准恩惠", 1),
    ("Scenes/StatusEffects/Boons/ToughnessBoon.tscn", 8, 'description = "Toughness Boon"', 'description = "坚韧恩惠"', "Toughness Boon", "坚韧恩惠", 1),
    ("Scenes/StatusEffects/Boons/SwiftnessBoon.tscn", 8, 'description = "Swiftness Boon"', 'description = "迅捷恩惠"', "Swiftness Boon", "迅捷恩惠", 1),
    # ---- Pickups ----
    ("Scenes/StatusEffects/Pickups/Magnifier.tscn", 8, 'description = "Magnifier"', 'description = "放大镜"', "Magnifier", "放大镜", 1),
    ("Scenes/StatusEffects/Pickups/Magnifier.tscn", 9, 'on_apply_tip = "Projectile Frenzy"', 'on_apply_tip = "投射物狂热"', "Projectile Frenzy", "投射物狂热", 1),
    ("Scenes/StatusEffects/Pickups/Frenzy.tscn", 8, 'description = "Frenzy"', 'description = "狂热"', "Frenzy", "狂热", 1),
    ("Scenes/StatusEffects/Pickups/Frenzy.tscn", 9, 'on_apply_tip = "Speed Buff"', 'on_apply_tip = "速度增益"', "Speed Buff", "速度增益", 1),
    # ---- Curses ----
    ("Scenes/StatusEffects/Curses/Bane.tscn", 8, 'description = "Bane"', 'description = "灾厄"', "Bane", "灾厄", 1),
    ("Scenes/StatusEffects/Curses/Brittle.tscn", 8, 'description = "Brittle"', 'description = "脆弱"', "Brittle", "脆弱", 1),
    ("Scenes/StatusEffects/Curses/Debilitate.tscn", 8, 'description = "Debilitate"', 'description = "虚弱"', "Debilitate", "虚弱", 1),
    ("Scenes/StatusEffects/Curses/Dread.tscn", 14, 'description = "Dread"', 'description = "恐惧"', "Dread", "恐惧", 1),
    ("Scenes/StatusEffects/Curses/Hinder.tscn", 8, 'description = "Hinder"', 'description = "阻碍"', "Hinder", "阻碍", 1),
    ("Scenes/StatusEffects/Curses/Hypothermia.tscn", 7, 'description = "Hypothermia"', 'description = "低温症"', "Hypothermia", "低温症", 1),
    ("Scenes/StatusEffects/Curses/Polarize.tscn", 8, 'description = "Polarize"', 'description = "极化"', "Polarize", "极化", 1),
    ("Scenes/StatusEffects/Curses/Protract.tscn", 8, 'description = "Protract"', 'description = "延长"', "Protract", "延长", 1),
    ("Scenes/StatusEffects/Curses/Scorch.tscn", 8, 'description = "Scorch"', 'description = "灼烧"', "Scorch", "灼烧", 1),
    # ---- Generic ----
    ("Scenes/StatusEffects/Generic/Echoing.tscn", 8, 'description = "Echoing"', 'description = "回响"', "Echoing", "回响", 1),
    ("Scenes/StatusEffects/Generic/Exposed.tscn", 8, 'description = "Exposure"', 'description = "暴露"', "Exposure", "暴露", 1),
    ("Scenes/StatusEffects/Generic/Hamstrung.tscn", 8, 'description = "Hamstrung"', 'description = "跛足"', "Hamstrung", "跛足", 1),
    ("Scenes/StatusEffects/Generic/RecentlyHit.tscn", 8, 'description = "Recently Hit"', 'description = "最近受击"', "Recently Hit", "最近受击", 1),
    ("Scenes/StatusEffects/Generic/Vulnerable.tscn", 8, 'description = "Vulnerable"', 'description = "易伤"', "Vulnerable", "易伤", 1),
    # ---- Keystones ----
    ("Scenes/StatusEffects/Keystones/Adrenaline.tscn", 8, 'description = "Adrenaline"', 'description = "肾上腺素"', "Adrenaline", "肾上腺素", 1),
    ("Scenes/StatusEffects/Keystones/BloodBoil.tscn", 8, 'description = "Blood Boil"', 'description = "热血沸腾"', "Blood Boil", "热血沸腾", 1),
    ("Scenes/StatusEffects/Keystones/CycleOfDestructionEffect.tscn", 8, 'description = "Cycle of Destruction"', 'description = "毁灭循环"', "Cycle of Destruction", "毁灭循环", 1),
    ("Scenes/StatusEffects/Keystones/Endurance.tscn", 8, 'description = "Endurance"', 'description = "耐力"', "Endurance", "耐力", 1),
    ("Scenes/StatusEffects/Keystones/GrowingPain.tscn", 8, 'description = "Growing Pain"', 'description = "成长之痛"', "Growing Pain", "成长之痛", 1),
    ("Scenes/StatusEffects/Keystones/HardenedFlesh.tscn", 8, 'description = "Hardened Flesh"', 'description = "硬化之躯"', "Hardened Flesh", "硬化之躯", 1),
    ("Scenes/StatusEffects/Keystones/KillMomentum.tscn", 8, 'description = "Raging Momentum"', 'description = "狂暴势头"', "Raging Momentum", "狂暴势头", 1),
    ("Scenes/StatusEffects/Keystones/PhantomShield.tscn", 9, 'description = "Phantom Shield"', 'description = "幻影护盾"', "Phantom Shield", "幻影护盾", 1),
    ("Scenes/StatusEffects/Keystones/RegenerativeFleshEffect.tscn", 8, 'description = "Regenerative Flesh"', 'description = "再生之躯"', "Regenerative Flesh", "再生之躯", 1),
    ("Scenes/StatusEffects/Keystones/SpikeArmor.tscn", 8, 'description = "Spike Armor"', 'description = "尖刺护甲"', "Spike Armor", "尖刺护甲", 1),
    ("Scenes/StatusEffects/Keystones/ToxicRunner.tscn", 8, 'description = "Plague Runner"', 'description = "瘟疫行者"', "Plague Runner", "瘟疫行者", 1),
    ("Scenes/StatusEffects/Keystones/Transfusion.tscn", 8, 'description = "Transfusion"', 'description = "输血"', "Transfusion", "输血", 1),
    ("Scenes/StatusEffects/Keystones/UnleashEffect.tscn", 8, 'description = "Unleash"', 'description = "释放"', "Unleash", "释放", 1),
    ("Scenes/StatusEffects/Keystones/VampiricSkin.tscn", 8, 'description = "Vampiric Skin"', 'description = "吸血鬼之肤"', "Vampiric Skin", "吸血鬼之肤", 1),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_patches(entries):
    patches = []
    for rel, line_no, old, new, src, tr, occurrences in entries:
        src_path = RAW / rel
        content = src_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        if line_no - 1 >= len(lines):
            raise SystemExit(f"line out of range: {rel}:{line_no}")
        actual = lines[line_no - 1].strip()
        if old != actual:
            raise SystemExit(f"line mismatch {rel}:{line_no}\n expected: {old!r}\n actual:   {actual!r}")
        count = content.count(old)
        if count != occurrences:
            raise SystemExit(f"occurrence {count} != {occurrences} for {old!r} at {rel}:{line_no}")
        preimage = sha256_file(src_path).upper()
        col = actual.find('"') + 2
        unit_id = f"{rel}:{line_no}:{col}"
        patches.append({
            "path": rel,
            "field": "text",
            "classification": "TEXT_PATCH",
            "unit_id": unit_id,
            "old_text": old,
            "new_text": new,
            "preimage_sha256": preimage,
            "expected_occurrences": occurrences,
            "source_text": src,
            "translation": tr,
            "placeholders": [],
            "format_tokens": [],
            "tests": [
                "unit_id_exact_match",
                "placeholder_conservation",
                "token_conservation",
                "resource_contract",
                "declared_delta",
                "compiled_script_load",
            ],
        })
    return patches


def main():
    patches = build_patches(ENTRIES)
    files = sorted({p["path"] for p in patches})
    manifest = {
        "id": "c5-l17-status-effects-zhcn",
        "version": "0.1.0",
        "patch_type": "TEXT_PATCH",
        "target_original_sha256": TARGET_SHA,
        "dependencies": [],
        "conflicts": [],
        "scope": f"C5-L17: status effect display names (description) and on_apply_tip texts across {len(files)} StatusEffects .tscn scenes (Skills, DamageAilments, Boons, Pickups, Curses, Generic, Keystones); internal identifiers (node names, unique_group, stack_group, script paths) untouched",
        "entities": [
            {"kind": "localization_unit", "id": p["unit_id"], "classification": "DISPLAY_SAFE",
             "confidence": "INFERENCE_HIGH",
             "expected_runtime_effect": f"displays {p['translation']}"}
            for p in patches
        ],
        "patches": patches,
        "asset_overlays": [],
        "tests": TESTS,
        "not_proven": "visual layout quality, persistence, gameplay, broad localization, or release readiness",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest written: {OUT}")
    print(f"patches: {len(patches)}")
    print(f"files: {len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())