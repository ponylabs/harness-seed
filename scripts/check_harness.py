#!/usr/bin/env python3
"""检查固定文档骨架、Agent Notes 路径、Skill 元数据和活跃 Markdown 文件链接，不访问网络。"""
import argparse
import os
from datetime import date
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

REQUIRED_DOCUMENTS = ('README.md', 'AGENTS.md', 'docs/AGENTS.md',
                      'docs/architecture.md', 'docs/development.md', 'docs/testing.md')
NOTE_LIFECYCLES = {'proposed', 'implemented', 'rejected', 'archived'}
NOTE_CLASSES = {'feature', 'bug-fix', 'simplification', 'architecture', 'process', 'testing'}

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

def check_note_path(relative: Path) -> list[str]:
    """仅约束记录的路径；控制文档不当作记录，不推断决策内容是否正确。"""
    parts = relative.parts
    if parts[:2] != ('.agents', 'notes'):
        return []
    note = parts[2:]
    if note == ('INDEX.md',):
        return [f'Agent Notes 不使用集中式 INDEX.md：{relative}']
    if (len(note) == 1 or (len(note) == 2 and note[0] in NOTE_LIFECYCLES)) and note[-1] in {'README.md', 'AGENTS.md'}:
        return []
    if len(note) != 3 or note[0] not in NOTE_LIFECYCLES or note[1] not in NOTE_CLASSES:
        return [f'Agent Note 路径应为合法状态/类别/日期主题.md：{relative}']
    match = re.fullmatch(r'(\d{4}-\d{2}-\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.md', note[2])
    if not match:
        return [f'Agent Note 文件名应为 yyyy-mm-dd-kebab-case-topic.md：{relative}']
    try:
        date.fromisoformat(match.group(1))
    except ValueError:
        return [f'Agent Note 首次提出日期无效：{relative}']
    return []

def check(root: Path) -> list[str]:
    """返回错误列表；不读取仓库之外的符号链接目标。"""
    root = root.resolve()
    errors = []
    for name in REQUIRED_DOCUMENTS:
        path = root / name
        if not path.is_file():
            errors.append(f'缺少必需入口：{name}')
    # 不递归符号链接目录，也不扫描依赖目录；先显式拒绝不支持的目录别名。
    markdown_paths = []
    for current, directories, files in os.walk(root, followlinks=False):
        current = Path(current)
        for name in list(directories):
            path = current / name
            if name in IGNORED:
                directories.remove(name)
            elif path.is_symlink():
                errors.append(f'不支持文档扫描范围内的目录符号链接：{path.relative_to(root)}')
                directories.remove(name)
            elif name.endswith('.md'):
                markdown_paths.append(path)
        markdown_paths.extend(current / name for name in files if name.endswith('.md'))
    for path in sorted(markdown_paths):
        relative = path.relative_to(root)
        if any(part in IGNORED for part in relative.parts):
            continue
        try:
            resolved = path.resolve()
        except (OSError, RuntimeError) as exc:
            errors.append(f'无法解析文档路径 {relative}：{exc}')
            continue
        if not resolved.is_relative_to(root):
            errors.append(f'文档符号链接越过仓库边界：{relative}')
            continue
        if not path.is_file():
            errors.append(f'文档路径不是可达的普通文件：{relative}')
            continue
        errors.extend(check_note_path(relative))
        # 冻结历史可保留过时出链；活跃文档指向归档的入链仍在通常检查内。
        if relative.parts[:3] == ('.agents', 'notes', 'archived') and len(relative.parts) >= 5:
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
                try:
                    destination = (path.parent / unquote(url.path)).resolve()
                except (OSError, RuntimeError) as exc:
                    errors.append(f'无法解析链接：{relative}:{number} → {target}：{exc}')
                    continue
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
    print('检查通过：固定文档骨架、Agent Notes 路径、Skill 元数据和活跃文件链接正常。')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
