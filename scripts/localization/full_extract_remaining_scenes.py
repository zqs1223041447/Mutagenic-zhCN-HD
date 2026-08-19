import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "03_raw/Scenes"
OUT = Path(__file__).resolve().parents[2] / "10_logs/remaining_static_text.json"

# files already translated (exclude)
EXCLUDED = {
    "Scenes/Menu.tscn",
    "Scenes/Popups/Dialogs/CharacterSelect/CharacterSelect.tscn",
    "Scenes/Popups/Dialogs/CharacterSelect/CharacterChanger.tscn",
    "Scenes/Popups/Dialogs/CharacterSelect/CharacterCreator.tscn",
    "Scenes/Popups/Dialogs/CharacterSelect/CharacterSlot.tscn",
    "Scenes/Popups/Dialogs/CharacterSelect/CharacterClass.tscn",
    "Scenes/Popups/Dialogs/Settings/Settings.tscn",
    "Scenes/Popups/Dialogs/Keybinds/Keybinds.tscn",
    "Scenes/Popups/Dialogs/Keybinds/KeybindOption.tscn",
    "Scenes/Popups/EscapeMenu.tscn",
    "Scenes/Popups/DeathScreen.tscn",
    "Scenes/Popups/Dialogs/PassiveTree/PassiveTreePopup.tscn",
    "Scenes/Popups/Dialogs/PassiveTree/PassiveNode.tscn",
    "Scenes/GUI/GUI.tscn",
    "Scenes/GUI/StatusDisplay.tscn",
    "Scenes/GUI/BuffDisplay.tscn",
    "Scenes/GUI/Globes/Globe.tscn",
    "Scenes/Popups/Dialogs/SkillSelect/SkillSelect.tscn",
    "Scenes/Popups/Dialogs/SkillSelect/SkillList.tscn",
    "Scenes/Popups/Dialogs/SkillSelect/SkillListOption.tscn",
    "Scenes/Popups/Dialogs/SkillSelect/SupportList.tscn",
    "Scenes/Popups/Dialogs/SkillSelect/SupportListOption.tscn",
    "Scenes/Popups/Dialogs/SkillSelect/SkillButton.tscn",
    "Scenes/Popups/Dialogs/SkillSelect/SupportButton.tscn",
    "Scenes/Popups/Dialogs/SkillSelect/SkillSelectBackup.tscn",
    "Scenes/Levels/LevelLoader.tscn",
    "Scenes/Pickups/Portal/PortalPickup.tscn",
    "Scenes/Pickups/Pickup.tscn",
    "Scenes/Popups/LeaderboardPopup.tscn",
    "Scenes/Popups/EscapeMenuStat.tscn",
}

result = {}
all_lines = []
for f in sorted(ROOT.rglob("*.tscn")):
    rel = f.relative_to(ROOT.parent).as_posix()
    if rel in EXCLUDED:
        continue
    content = f.read_text(encoding="utf-8")
    lines = content.splitlines()
    hits = []
    for i, l in enumerate(lines, 1):
        for m in re.finditer(r'(text|label_text|bbcode_text)\s*=\s*"((?:[^"\\]|\\.)*)"', l):
            hits.append({"line": i, "line_text": l.strip(), "field": m.group(1), "value": m.group(2)})
    if hits:
        result[rel] = hits
        for h in hits:
            all_lines.append((rel, h["line"], h["field"], h["value"]))

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"files with text: {len(result)}")
total = sum(len(v) for v in result.values())
print(f"total text lines: {total}")
print("\n=== all remaining text lines ===")
for rel, ln, field, val in all_lines:
    print(f"{rel}:{ln} [{field}] {val}")
