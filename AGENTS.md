# 开发约定

## 开始工作

先读 [README](README.md)，再沿改动路径读取适用的子目录 AGENTS.md 和模块说明；不要全仓加载无关文档。以用户当前目标为范围，不把建议当作实施授权。

## 不变的底线

- 先核实实现、配置和测试，再描述项目事实；发现规则与实现冲突时报告差异，不能以“代码如此”擅自改掉约束。
- 按改动风险验证行为，缺陷优先补回归检查。明确区分通过、失败、未运行及其原因，不用覆盖率替代业务验收。
- 同一变更同步维护受影响的长期知识；允许无需修改文档。不得把任务流水或临时调试过程追加到永久文档。
- 不为通过检查削弱测试、删掉失败证据或抬高预算。新增长期规则应解决已证实的重复风险，局部规则留在局部。
- 提交前检查差异、秘密信息和无关文件；提交说明用中文说明目的。推送、发布、权限变更遵循用户授权。

## 按需读取 Skill

以下是明确的文件入口；宿主未自动发现 Skill 时，直接读取对应文件，不假定加载成功。

- 从模板开始新项目：[seed-initialize](.agents/skills/seed-initialize/SKILL.md)。仅在用户要求初始化派生项目时使用；维护 Harness Seed 自身不触发。
- 实施功能、修复或重构：[seed-change](.agents/skills/seed-change/SKILL.md)。只读问答不进入改码流程。
- 长期知识发生变化：[seed-doc](.agents/skills/seed-doc/SKILL.md)。
- 需要编写或精简说明：[seed-prose](.agents/skills/seed-prose/SKILL.md)。
- 用户要求或发现具体治理问题：[seed-review](.agents/skills/seed-review/SKILL.md)。

## 本仓库验证

运行 `python3 scripts/check_harness.py`、`python3 -m unittest discover -s tests -v` 和 `git diff --check`。检查器只验证结构与本地链接，不证明事实、表达质量或 Agent 行为。适用于派生项目的命令由其实际技术栈决定。
