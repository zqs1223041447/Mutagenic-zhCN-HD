#!/usr/bin/env python3
"""查找可能导致崩溃的中文位置（字典键、NodePath、get_node 等）"""
import re
import pathlib

dangerous_patterns = [
    (r'get_node\(["\']([^"\']*[\u4e00-\u9fff][^"\']*)["\']', 'get_node with Chinese path'),
    (r'\$([^/\s"\']*[\u4e00-\u9fff][^/\s"\']*)', 'NodePath with Chinese'),
    (r'\{[^}]{0,100}["\']([^"\']*[\u4e00-\u9fff][^"\']*)["\'][\s]*:', 'Dictionary key with Chinese'),
    (r'\.has\(["\']([^"\']*[\u4e00-\u9fff][^"\']*)["\']', '.has() with Chinese key'),
    (r'\.get\(["\']([^"\']*[\u4e00-\u9fff][^"\']*)["\']', '.get() with Chinese key'),
]

worktree = pathlib.Path('06_worktree')
issues = []

for gd in worktree.rglob('*.gd'):
    try:
        content = gd.read_text(encoding='utf-8')
        for pattern, desc in dangerous_patterns:
            for match in re.finditer(pattern, content):
                chinese_part = match.group(1) if match.groups() else match.group(0)
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'file': str(gd.relative_to(worktree)),
                    'line': line_num,
                    'type': desc,
                    'match': chinese_part[:50]
                })
    except Exception as e:
        print(f"Error reading {gd}: {e}")

if issues:
    print(f'Found {len(issues)} dangerous Chinese placements:\n')
    # 按文件分组
    by_file = {}
    for issue in issues:
        f = issue['file']
        if f not in by_file:
            by_file[f] = []
        by_file[f].append(issue)
    
    for f, file_issues in sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)[:20]:
        print(f'\n{f} ({len(file_issues)} issues):')
        for issue in file_issues[:5]:
            print(f"  Line {issue['line']}: {issue['type']}")
            print(f"    '{issue['match']}'")
else:
    print('No dangerous Chinese patterns found')
