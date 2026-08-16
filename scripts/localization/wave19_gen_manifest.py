#!/usr/bin/env python3
"""Generate C5-L19: unique item names and flavor texts
(Globals/Genes/UniquePools/UniquePoolGeneric.gd + UniquePoolSOTA.gd).

Each unit old_text/new_text = the full stripped serialized source line.
Translations follow docs/zh_CN_glossary.md; flavor lines are literary but
concise, matching game-translation style. Internal identifiers (pool keys,
mod_id strings, texture vars) stay English; only player-visible name/flavor
values are translated.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(r"G:\opencode-Mutageni")
SRC = ROOT / "04_recovered"
OUT = ROOT / "mods/c5-l19-unique-items-zhcn/mod.json"
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
    "phase_checkpoint_unique_items_zhcn",
]

# (rel_path, line_no, old_line, new_line, source_text, translation, occurrences)
ENTRIES = [
    # ============ Globals/Genes/UniquePools/UniquePoolGeneric.gd ============
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 32, '"name": "Expansion Charm", ', '"name": "扩张护符", ', "Expansion Charm", "扩张护符", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 33, '"flavor": "Increase your reach.", ', '"flavor": "扩大你的范围。", ', "Increase your reach.", "扩大你的范围。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 48, '"name": "Harrowing Cold", ', '"name": "酷寒", ', "Harrowing Cold", "酷寒", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 49, '"flavor": "It\'s cold outside...", ', '"flavor": "外面真冷……", ', "It's cold outside...", "外面真冷……", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 70, '"name": "Balanced Oppression", ', '"name": "平衡压迫", ', "Balanced Oppression", "平衡压迫", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 71, '"flavor": "Some love the heat, some love the cold. Why not both?", ', '"flavor": "有人爱热，有人爱冷。为何不能兼得？", ', "Some love the heat, some love the cold. Why not both?", "有人爱热，有人爱冷。为何不能兼得？", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 91, '"name": "Ice Crown", ', '"name": "冰冠", ', "Ice Crown", "冰冠", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 92, '"flavor": "From the cold comes darkness.", ', '"flavor": "寒冷孕育黑暗。", ', "From the cold comes darkness.", "寒冷孕育黑暗。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 109, '"name": "Echoes of Sin", ', '"name": "罪恶回响", ', "Echoes of Sin", "罪恶回响", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 110, '"flavor": "Fires of the past continue to burn with a malignant taste.", ', '"flavor": "往日的火焰仍带着恶意持续燃烧。", ', "Fires of the past continue to burn with a malignant taste.", "往日的火焰仍带着恶意持续燃烧。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 136, '"name": "Strength from Strength", ', '"name": "愈战愈强", ', "Strength from Strength", "愈战愈强", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 137, '"flavor": "The best offense is a good defense.", ', '"flavor": "最好的进攻就是出色的防守。", ', "The best offense is a good defense.", "最好的进攻就是出色的防守。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 155, '"name": "Gladiators Resolve", ', '"name": "角斗士的决心", ', "Gladiators Resolve", "角斗士的决心", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 156, '"flavor": "Sometimes one must take a hit to make it through to the end.", ', '"flavor": "有时必须挨上一击，才能坚持到最后。", ', "Sometimes one must take a hit to make it through to the end.", "有时必须挨上一击，才能坚持到最后。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 180, '"name": "Fishing Rod", ', '"name": "钓鱼竿", ', "Fishing Rod", "钓鱼竿", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 181, '"flavor": "It\'s not much, but it\'ll do for now.", ', '"flavor": "算不上什么好东西，但暂时够用了。", ', "It's not much, but it'll do for now.", "算不上什么好东西，但暂时够用了。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 199, '"name": "Mercurial Venom", ', '"name": "水银剧毒", ', "Mercurial Venom", "水银剧毒", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 200, '"flavor": "The toxin had a metallic shimmer.", ', '"flavor": "毒素泛着金属般的微光。", ', "The toxin had a metallic shimmer.", "毒素泛着金属般的微光。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 227, '"name": "Skull Crusher", ', '"name": "碎颅锤", ', "Skull Crusher", "碎颅锤", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 228, '"flavor": "It\'s big. Big and heavy.", ', '"flavor": "它很大。又大又重。", ', "It's big. Big and heavy.", "它很大。又大又重。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 248, '"name": "Spreading Flames", ', '"name": "蔓延之火", ', "Spreading Flames", "蔓延之火", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 249, '"flavor": "When the wind catches a small flame, a forest is needed to put it out.", ', '"flavor": "当风助长一点小火苗，就需要一片森林才能扑灭。", ', "When the wind catches a small flame, a forest is needed to put it out.", "当风助长一点小火苗，就需要一片森林才能扑灭。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 272, '"name": "Ogre Talisman", ', '"name": "食人魔护符", ', "Ogre Talisman", "食人魔护符", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 273, '"flavor": "Fire burns hotter in a bigger heart.", ', '"flavor": "更大的心脏燃起更旺的火焰。", ', "Fire burns hotter in a bigger heart.", "更大的心脏燃起更旺的火焰。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 290, '"name": "Cheat-ahs", ', '"name": "猎豹之靴", ', "Cheat-ahs", "猎豹之靴", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 291, '"flavor": "A little pep in your step.", ', '"flavor": "脚步轻盈，活力十足。", ', "A little pep in your step.", "脚步轻盈，活力十足。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 308, '"name": "Tinkerer\'s Toy", ', '"name": "工匠的玩具", ', "Tinkerer's Toy", "工匠的玩具", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 309, '"flavor": "Sometimes, just sometimes, tinkering with a bomb isn\'t dangerous.", ', '"flavor": "有时候，仅仅是有时候，捣鼓炸弹并不危险。", ', "Sometimes, just sometimes, tinkering with a bomb isn't dangerous.", "有时候，仅仅是有时候，捣鼓炸弹并不危险。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 324, '"name": "Frozen Sludge", ', '"name": "冰冻泥沼", ', "Frozen Sludge", "冰冻泥沼", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 325, '"flavor": "A feverish cold comes over your foes.", ', '"flavor": "一阵狂热的寒冷席卷你的敌人。", ', "A feverish cold comes over your foes.", "一阵狂热的寒冷席卷你的敌人。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 340, '"name": "Goblin\'s Girdle", ', '"name": "哥布林腰带", ', "Goblin's Girdle", "哥布林腰带", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 341, '"flavor": "A goblin is alone without a tribe. A tribe of Buff-Boons.", ', '"flavor": "哥布林离不开部落。一个由增益小丑组成的部落。", ', "A goblin is alone without a tribe. A tribe of Buff-Boons.", "哥布林离不开部落。一个由增益小丑组成的部落。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 360, '"name": "Chillburn", ', '"name": "寒灼", ', "Chillburn", "寒灼", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 361, '"flavor": "Burning sensations are replaced by numbness to the pain.", ', '"flavor": "灼烧感被麻木取代，痛楚不再明显。", ', "Burning sensations are replaced by numbness to the pain.", "灼烧感被麻木取代，痛楚不再明显。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 378, '"name": "Echoing Fury", ', '"name": "回响之怒", ', "Echoing Fury", "回响之怒", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 379, '"flavor": "Memories of trauma linger amongst the survivors.", ', '"flavor": "创伤的记忆在幸存者中萦绕不散。", ', "Memories of trauma linger amongst the survivors.", "创伤的记忆在幸存者中萦绕不散。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 396, '"name": "Prismatic Bow", ', '"name": "棱彩之弓", ', "Prismatic Bow", "棱彩之弓", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 397, '"flavor": "Elemental dread at the pull of a string.", ', '"flavor": "拉弦之间，元素之惧涌来。", ', "Elemental dread at the pull of a string.", "拉弦之间，元素之惧涌来。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 422, '"name": "Bloody Knuckles", ', '"name": "染血指节", ', "Bloody Knuckles", "染血指节", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 423, '"flavor": "Reminders of the skill you possess.", ', '"flavor": "你身怀绝技的证明。", ', "Reminders of the skill you possess.", "你身怀绝技的证明。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 438, '"name": "Elder Ward", ', '"name": "长者守护", ', "Elder Ward", "长者守护", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 439, '"flavor": "Become a stalwart defender in critical times.", ', '"flavor": "在危急时刻成为坚定的守护者。", ', "Become a stalwart defender in critical times.", "在危急时刻成为坚定的守护者。", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 462, '"name": "Balance of Power", ', '"name": "力量平衡", ', "Balance of Power", "力量平衡", 1),
    ("Globals/Genes/UniquePools/UniquePoolGeneric.gd", 463, '"flavor": "A steady stream of rotational power.", ', '"flavor": "源源不断的旋转之力。", ', "A steady stream of rotational power.", "源源不断的旋转之力。", 1),

    # ============ Globals/Genes/UniquePools/UniquePoolSOTA.gd ============
    ("Globals/Genes/UniquePools/UniquePoolSOTA.gd", 10, '"name": "Ancient\'s Charm", ', '"name": "古灵护符", ', "Ancient's Charm", "古灵护符", 1),
    ("Globals/Genes/UniquePools/UniquePoolSOTA.gd", 11, '"flavor": "A token of the Ancient Spirit.", ', '"flavor": "远古之灵的凭证。", ', "A token of the Ancient Spirit.", "远古之灵的凭证。", 1),
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
        src_path = SRC / rel
        content = src_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        if line_no - 1 >= len(lines):
            raise SystemExit(f"line out of range: {rel}:{line_no}")
        actual = lines[line_no - 1].strip()
        old_s = old.strip()
        new_s = new.strip()
        if old_s != actual:
            raise SystemExit(f"line mismatch {rel}:{line_no}\n expected: {old_s!r}\n actual:   {actual!r}")
        count = content.count(old_s)
        if count != occurrences:
            raise SystemExit(f"occurrence {count} != {occurrences} for {old_s!r} at {rel}:{line_no}")
        preimage = sha256_file(src_path).upper()
        col = actual.find('"') + 2
        unit_id = f"{rel}:{line_no}:{col}"
        patches.append({
            "path": rel,
            "field": "text",
            "classification": "TEXT_PATCH",
            "unit_id": unit_id,
            "old_text": old_s,
            "new_text": new_s,
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
        "id": "c5-l19-unique-items-zhcn",
        "version": "0.1.0",
        "patch_type": "TEXT_PATCH",
        "target_original_sha256": TARGET_SHA,
        "dependencies": [],
        "conflicts": [],
        "scope": f"C5-L19: unique item display names and flavor texts across {len(files)} UniquePools scripts (UniquePoolGeneric.gd 23 items, UniquePoolSOTA.gd 1 item); internal identifiers (pool keys, mod_id strings, texture vars) untouched",
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