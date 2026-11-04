#!/usr/bin/env python3
"""检查 Harness 入口、Skill 元数据和本地 Markdown 文件链接，不访问网络。"""
import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

IGNORED = {'.git', 'node_modules', '.venv', '__pycache__', '.cache', 'vendor'}
def inline_targets(line: str) -> list[str]:
    """读取同一行内联链接目标，支持转义、括号和尖括号目标。"""
    # 屏蔽同一行成对反引号代码段，避免把代码示例当链接。
    pieces = list(line)
    index = 0
    while index < len(line):
        if line[index] != '`':
            index += 1
            continue
        end = index
        while end < len(line) and line[end] == '`':
            end += 1
        marker = line[index:end]
        close = line.find(marker, end)
        while close >= 0 and ((close > 0 and line[close - 1] == '`') or
                              (close + len(marker) < len(line) and line[close + len(marker)] == '`')):
            close = line.find(marker, close + 1)
        if close >= 0:
            pieces[index:close + len(marker)] = ' ' * (close + len(marker) - index)
            index = close + len(marker)
        else:
            index = end
    line = ''.join(pieces)
    targets = []
    for match in re.finditer(r'(?<!!)\[[^\]\n]*\]\(|!\[[^\]\n]*\]\(', line):
        start = match.end()
        if start < len(line) and line[start] == '<':
            end = line.find('>', start + 1)
            if end >= 0:
                targets.append(line[start + 1:end])
            continue
        depth, value, escaped = 0, [], False
        for char in line[start:]:
            if escaped:
                value.append(char)
                escaped = False
            elif char == chr(92):
                escaped = True
            elif char == '(':
                depth += 1
                value.append(char)
            elif char == ')':
                if depth == 0:
                    break
                depth -= 1
                value.append(char)
            elif char.isspace() and depth == 0:
                break
            else:
                value.append(char)
        if value:
            targets.append(''.join(value))
    return targets

def check(root: Path) -> list[str]:
    """返回错误列表；不读取仓库之外的符号链接目标。"""
    root = root.resolve()
    errors = []
    for name in ('AGENTS.md', 'README.md'):
        path = root / name
        if not path.is_file():
            errors.append(f'缺少必需入口：{name}')
    for path in sorted(root.rglob('*.md')):
        relative = path.relative_to(root)
        if any(part in IGNORED for part in relative.parts):
            continue
        if not path.resolve().is_relative_to(root):
            errors.append(f'文档符号链接越过仓库边界：{relative}')
            continue
        try:
            content = path.read_text(encoding='utf-8')
        except (OSError, UnicodeError) as exc:
            errors.append(f'无法读取 {relative}：{exc}')
            continue
        if path.name == 'SKILL.md' and relative.parts[:2] == ('.agents', 'skills'):
            header = re.match(r'\A---\n(.*?)\n---(?:\n|$)', content, re.S)
            fields = {}
            if header:
                for line in header.group(1).splitlines():
                    key, sep, value = line.partition(':')
                    if sep:
                        fields[key.strip()] = value.strip().strip('\"\'').strip()
            name = fields.get('name', '')
            if name != path.parent.name or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
                errors.append(f'Skill 名称缺失、无效或与目录不一致：{relative}')
            if not fields.get('description'):
                errors.append(f'Skill 缺少 description：{relative}')
        # 仅检查围栏外的内联文件链接。参考式链接与锚点不在本检查器覆盖范围内。
        in_fence = False
        fence_char = ''
        fence_length = 0
        for number, line in enumerate(content.splitlines(), 1):
            marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
            if marker:
                char = marker.group(1)[0]
                if not in_fence:
                    in_fence, fence_char = True, char
                    fence_length = len(marker.group(1))
                elif char == fence_char and len(marker.group(1)) >= fence_length and not marker.group(2).strip():
                    in_fence = False
                continue
            if in_fence:
                continue
            for target in inline_targets(line):
                target = target.strip('<>')
                try:
                    url = urlsplit(target)
                except ValueError:
                    errors.append(f'无效链接：{relative}:{number} → {target}')
                    continue
                if url.scheme or url.netloc or not url.path:
                    continue
                destination = (path.parent / unquote(url.path)).resolve()
                if not destination.is_relative_to(root):
                    errors.append(f'链接越过仓库边界：{relative}:{number} → {target}')
                elif not destination.exists():
                    errors.append(f'失效文件链接：{relative}:{number} → {target}')
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1], help='待检查的仓库根目录')
    args = parser.parse_args()
    if not args.root.is_dir():
        print(f'检查失败：目录不存在：{args.root}')
        return 1
    errors = check(args.root)
    if errors:
        print('\n'.join(errors))
        print(f'检查失败：共 {len(errors)} 项问题。')
        return 1
    print('检查通过：入口、Skill 元数据和支持范围内的本地文件链接正常。')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
