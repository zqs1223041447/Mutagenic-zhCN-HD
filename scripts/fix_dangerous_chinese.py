#!/usr/bin/env python3
"""修复被错误翻译的字典键、节点名、属性名"""
import pathlib

fixes = [
    ('Globals/PlayableClasses.gd', '"战士": "战士"', '"WARRIOR": "WARRIOR"'),
    ('Globals/Skills.gd', '"霰弹枪":', '"Shotgun":'),
    ('Scenes/Popups/DeathScreen.gd', 'get_node("属性")', 'get_node("Stats")'),
    ('Scenes/Popups/EscapeMenu.gd', 'get_node("属性")', 'get_node("Stats")'),
    ('Scenes/Popups/ItemTabContent.gd', 'get_node("属性")', 'get_node("Stats")'),
    ('Scenes/Skills/GenericSkill.gd', 'get_node("属性")', 'get_node("Stats")'),
    ('Scenes/Popups/Dialogs/UniqueHelp/UniqueItem.gd', '.has("风味")', '.has("flavor")'),
    ('Scenes/Tooltips/GeneTooltip/GeneInfo.gd', '.has("风味")', '.has("flavor")'),
]

worktree = pathlib.Path('06_worktree')
fixed_count = 0
not_found = []

for rel_path, old, new in fixes:
    fpath = worktree / rel_path
    if fpath.exists():
        content = fpath.read_text(encoding='utf-8')
        if old in content:
            new_content = content.replace(old, new)
            fpath.write_text(new_content, encoding='utf-8')
            fixed_count += 1
            print(f'✓ Fixed {rel_path}')
        else:
            not_found.append((rel_path, old))
            print(f'⚠ Pattern not found in {rel_path}: {repr(old[:30])}')
    else:
        print(f'✗ File not found: {rel_path}')

print(f'\nTotal fixed: {fixed_count}/{len(fixes)} files')

if not_found:
    print(f'\nNot found ({len(not_found)}):')
    for f, pattern in not_found:
        print(f'  {f}: {repr(pattern[:40])}')
