"""验证检查器确实拒绝错误，不以文案匹配冒充业务验证。"""
import importlib.util
import tempfile
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

    def test_dependency_ignored(self):
        self.write('node_modules/a/README.md', '[错误](missing.md)\n')
        self.assertEqual(MODULE.check(self.root), [])

    def test_external_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            target = Path(other) / 'external.md'
            target.write_text('不应读取', encoding='utf-8')
            (self.root / 'external.md').symlink_to(target)
            self.assertTrue(MODULE.check(self.root))

if __name__ == '__main__':
    unittest.main()
