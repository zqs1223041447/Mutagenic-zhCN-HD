#!/usr/bin/env python3
"""Overlay modified .gdc scripts into 08_pack as .gde files"""
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COMPILED_DIR = PROJECT_ROOT / "07_compiled"
PACK_DIR = PROJECT_ROOT / "08_pack"

MODIFIED_SCRIPTS = [
    "Globals/PlayableClasses.gde",
    "Globals/Skills.gde",
    "Scenes/Popups/DeathScreen.gde",
    "Scenes/Popups/EscapeMenu.gde",
    "Scenes/Popups/ItemTabContent.gde",
    "Scenes/Skills/GenericSkill.gde",
    "Scenes/Popups/Dialogs/UniqueHelp/UniqueItem.gde",
    "Scenes/Tooltips/GeneTooltip/GeneInfo.gde",
]


def main() -> int:
    overlay_count = 0
    
    for script_path in MODIFIED_SCRIPTS:
        # Source is .gdc, dest is .gde
        # Bug: compiled files are in subdirectories like "PlayableClasses.gdc/PlayableClasses.gdc"
        gdc_name = Path(script_path).name.replace(".gde", ".gdc")
        source_gdc = COMPILED_DIR / script_path.replace(".gde", ".gdc") / gdc_name
        dest_gde = PACK_DIR / script_path
        
        if not source_gdc.exists():
            print(f"  ✗ Missing source: {source_gdc}")
            continue
        
        # Remove dest if exists
        if dest_gde.exists():
            dest_gde.unlink()
        
        # Copy .gdc as .gde (unencrypted bytecode masquerading as encrypted)
        shutil.copy2(source_gdc, dest_gde)
        
        # Verify magic
        with open(dest_gde, "rb") as f:
            magic = f.read(4).decode("ascii", errors="ignore")
        
        if magic == "GDSC":
            print(f"  ✓ {script_path} (unencrypted .gdc renamed to .gde)")
            overlay_count += 1
        else:
            print(f"  ✗ {script_path} (wrong magic: {magic!r})")
            return 1
    
    print(f"\nSuccessfully overlaid: {overlay_count} / {len(MODIFIED_SCRIPTS)} files")
    
    if overlay_count != len(MODIFIED_SCRIPTS):
        print("✗ Overlay incomplete")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
