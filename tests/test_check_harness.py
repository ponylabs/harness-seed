"""验证检查器确实拒绝错误，不以文案匹配冒充业务验证。"""
import importlib.util
import tempfile
import subprocess
import sys
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('check_harness', Path(__file__).resolve().parents[1] / 'scripts/check_harness.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class HarnessChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write('AGENTS.md', '# 规则\n')
        self.write('README.md', '# 项目\n')
        for name in MODULE.REQUIRED_DOCUMENTS:
            if not (self.root / name).exists():
                self.write(name, '# 项目事实\n')

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
        return target

    def test_minimal_project(self):
        self.assertEqual(MODULE.check(self.root), [])

    def test_missing_entry(self):
        (self.root / 'AGENTS.md').unlink()
        self.assertTrue(MODULE.check(self.root))

    def test_each_fixed_document_is_required(self):
        for name in MODULE.REQUIRED_DOCUMENTS:
            with self.subTest(name=name):
                path = self.root / name
                content = path.read_text(encoding='utf-8')
                path.unlink()
                self.assertTrue(any(name in error for error in MODULE.check(self.root)))
                self.write(name, content)

    def test_optional_documents_and_notes_need_not_exist(self):
        self.assertFalse((self.root / '.agents/notes').exists())
        self.assertFalse((self.root / 'docs/web-styling.md').exists())
        self.assertEqual(MODULE.check(self.root), [])

    def test_all_note_lifecycles_and_classes(self):
        for lifecycle in MODULE.NOTE_LIFECYCLES:
            for kind in MODULE.NOTE_CLASSES:
                self.write(f'.agents/notes/{lifecycle}/{kind}/2026-11-04-example.md', '# 决策\n')
        self.assertEqual(MODULE.check(self.root), [])

    def test_notes_control_documents(self):
        for scope in ('', 'proposed/', 'implemented/', 'rejected/', 'archived/'):
            for name in ('README.md', 'AGENTS.md'):
                self.write(f'.agents/notes/{scope}{name}', '# 规则\n')
        self.assertEqual(MODULE.check(self.root), [])

    def test_invalid_note_paths_and_names(self):
        cases = (
            'INDEX.md',
            'draft/feature/2026-11-04-example.md',
            'implemented/refactor/2026-11-04-example.md',
            'implemented/feature/nested/2026-11-04-example.md',
            'implemented/2026-11-04-example.md',
            'implemented/feature/2026-02-30-example.md',
            'implemented/feature/2026-1-04-example.md',
            'implemented/feature/2026-11-04-Example.md',
            'implemented/feature/2026-11-04-two_words.md',
        )
        for name in cases:
            with self.subTest(name=name):
                path = self.write(f'.agents/notes/{name}', '# 决策\n')
                self.assertTrue(MODULE.check(self.root))
                path.unlink()

    def test_notes_move_and_inbound_links_follow_lifecycle(self):
        old = '.agents/notes/proposed/architecture/2026-11-04-boundary.md'
        new = '.agents/notes/implemented/architecture/2026-11-04-boundary.md'
        self.write(old, '# 决策\n')
        self.write('README.md', f'[决策]({old})\n')
        self.assertEqual(MODULE.check(self.root), [])
        target = self.root / new
        target.parent.mkdir(parents=True, exist_ok=True)
        (self.root / old).rename(target)
        self.assertTrue(MODULE.check(self.root))
        self.write('README.md', f'[决策]({new})\n')
        self.assertEqual(MODULE.check(self.root), [])

    def test_archive_preserves_historical_outbound_links(self):
        name = '.agents/notes/archived/architecture/2026-11-04-boundary.md'
        self.write(name, '# 冻结决策\n[历史路径](removed.md)\n')
        self.write('README.md', f'[历史决策]({name})\n')
        self.assertEqual(MODULE.check(self.root), [])
        (self.root / name).unlink()
        self.assertTrue(MODULE.check(self.root))

    def test_archive_instructions_still_check_links(self):
        self.write('.agents/notes/archived/AGENTS.md', '[错误](missing.md)\n')
        self.assertTrue(MODULE.check(self.root))

    def test_active_note_outbound_links_are_checked(self):
        self.write('.agents/notes/implemented/process/2026-11-04-checks.md', '[失效](missing.md)\n')
        self.assertTrue(MODULE.check(self.root))

    def test_valid_skill(self):
        self.write('.agents/skills/example/SKILL.md', '---\nname: example\ndescription: 测试明确职责\n---\n# 示例\n')
        self.assertEqual(MODULE.check(self.root), [])

    def test_mismatched_skill(self):
        self.write('.agents/skills/example/SKILL.md', '---\nname: other\ndescription: 示例\n---\n')
        self.assertTrue(MODULE.check(self.root))

    def test_missing_description(self):
        self.write('.agents/skills/example/SKILL.md', '---\nname: example\n---\n')
        self.assertTrue(MODULE.check(self.root))

    def test_missing_frontmatter(self):
        self.write('.agents/skills/example/SKILL.md', '# 缺少元数据\n')
        self.assertTrue(MODULE.check(self.root))

    def test_broken_link(self):
        self.write('README.md', '[不存在](missing.md)\n')
        self.assertTrue(MODULE.check(self.root))

    def test_relative_link(self):
        self.write('docs/read.md', '[入口](../README.md)\n')
        self.assertEqual(MODULE.check(self.root), [])

    def test_encoded_path_and_anchor(self):
        self.write('说明.md', '# 说明\n')
        self.write('README.md', '[中文](%E8%AF%B4%E6%98%8E.md#标题)\n')
        self.assertEqual(MODULE.check(self.root), [])

    def test_external_and_anchor_ignored(self):
        self.write('README.md', '[外部](https://example.com/a) [锚点](#标题)\n')
        self.assertEqual(MODULE.check(self.root), [])

    def test_code_fence_ignored(self):
        self.write('README.md', '```md\n[例子](not-real.md)\n```\n')
        self.assertEqual(MODULE.check(self.root), [])

    def test_long_fence_contains_short_fence(self):
        self.write('README.md', '````md\n```\n[例子](missing.md)\n````\n')
        self.assertEqual(MODULE.check(self.root), [])

    def test_closing_fence_cannot_have_text(self):
        self.write('README.md', '```md\n```not-close\n[例子](missing.md)\n```\n')
        self.assertEqual(MODULE.check(self.root), [])

    def test_link_after_long_fence_is_checked(self):
        self.write('README.md', '````md\n```\n````\n[失效](missing.md)\n')
        self.assertTrue(MODULE.check(self.root))

    def test_parentheses_in_target(self):
        self.write('guide(v1).md', '# 指南\n')
        self.write('README.md', '[指南](guide(v1).md)\n')
        self.assertEqual(MODULE.check(self.root), [])

    def test_angle_target_with_spaces(self):
        self.write('my guide.md', '# 指南\n')
        self.write('README.md', '[指南](<my guide.md>)\n')
        self.assertEqual(MODULE.check(self.root), [])

    def test_inline_code_ignored(self):
        self.write('README.md', '`[例子](missing.md)` 与 ``[例子](also-missing.md)``\n')
        self.assertEqual(MODULE.check(self.root), [])

    def test_quoted_empty_description(self):
        self.write('.agents/skills/example/SKILL.md', '---\nname: example\ndescription: ""\n---\n')
        self.assertTrue(MODULE.check(self.root))

    def test_outside_link_rejected(self):
        self.write('README.md', '[越界](../outside.md)\n')
        self.assertTrue(MODULE.check(self.root))

    def test_moving_document_requires_inbound_link_update(self):
        self.write('docs/old.md', '# 当前说明\n')
        self.write('README.md', '[说明](docs/old.md)\n')
        self.assertEqual(MODULE.check(self.root), [])
        (self.root / 'docs/old.md').rename(self.root / 'docs/new.md')
        self.assertTrue(MODULE.check(self.root))
        self.write('README.md', '[说明](docs/new.md)\n')
        self.assertEqual(MODULE.check(self.root), [])

    def test_cli_failure_is_nonzero(self):
        self.write('README.md', '[缺失参考](missing.md)\n')
        result = subprocess.run(
            [sys.executable, str(Path(MODULE.__file__)), '--root', str(self.root)],
            text=True, capture_output=True, check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('missing.md', result.stdout + result.stderr)

    def test_structure_pass_does_not_validate_business_code(self):
        # 明确锁定覆盖边界：结构绿灯不能证明业务语义或可执行性。
        self.write('broken.py', 'this is not valid Python!\n')
        self.assertEqual(MODULE.check(self.root), [])

    def test_dependency_ignored(self):
        self.write('node_modules/a/README.md', '[错误](missing.md)\n')
        self.assertEqual(MODULE.check(self.root), [])

    def test_external_required_directory_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other)
            for path in (self.root / 'docs').iterdir():
                self.write(path.relative_to(self.root).as_posix(), '# 当前文档\n')
                (outside / path.name).write_text('# 外部文档\n', encoding='utf-8')
                path.unlink()
            (self.root / 'docs').rmdir()
            (self.root / 'docs').symlink_to(outside, target_is_directory=True)
            errors = MODULE.check(self.root)
            self.assertTrue(any('目录符号链接' in error for error in errors))

    def test_internal_directory_symlink_rejected(self):
        (self.root / 'alias').symlink_to(self.root / 'docs', target_is_directory=True)
        self.assertTrue(any('目录符号链接' in error for error in MODULE.check(self.root)))

    def test_ignored_directory_symlink_allowed(self):
        with tempfile.TemporaryDirectory() as other:
            (self.root / 'node_modules').symlink_to(other, target_is_directory=True)
            self.assertEqual(MODULE.check(self.root), [])

    def test_dangling_archived_note_symlink_rejected(self):
        path = self.root / '.agents/notes/archived/process/2026-11-04-test.md'
        path.parent.mkdir(parents=True)
        path.symlink_to(self.root / 'missing.md')
        self.assertTrue(any('不是可达的普通文件' in error for error in MODULE.check(self.root)))

    def test_archived_note_directory_rejected(self):
        path = self.root / '.agents/notes/archived/process/2026-11-04-test.md'
        path.mkdir(parents=True)
        self.assertTrue(any('不是可达的普通文件' in error for error in MODULE.check(self.root)))

    def test_document_symlink_loop_reports_error(self):
        (self.root / 'loop.md').symlink_to('loop.md')
        self.assertTrue(any('无法解析文档路径' in error for error in MODULE.check(self.root)))

    def test_link_symlink_loop_reports_error(self):
        (self.root / 'loop').symlink_to('loop')
        self.write('README.md', '[循环](loop)\n')
        self.assertTrue(any('无法解析链接' in error for error in MODULE.check(self.root)))

    def test_external_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            target = Path(other) / 'external.md'
            target.write_text('不应读取', encoding='utf-8')
            (self.root / 'external.md').symlink_to(target)
            self.assertTrue(MODULE.check(self.root))

if __name__ == '__main__':
    unittest.main()
