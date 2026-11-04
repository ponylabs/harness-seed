# 开发约定

## 开始工作

先读 [README](README.md)，再沿目标路径读取适用的子 AGENTS 和模块说明。遵守宿主指令优先级，不假定子目录规则会自动加载；不要全仓加载无关资料。范围以用户当前目标为准，建议不等于实施授权。

## 始终适用

- 核实实现、配置和测试再描述事实；发现实现与约束冲突时报告，不擅自改掉约束。
- 明确当前改动与验收条件；按风险验证真实行为，缺陷优先建立失败复现。通过、失败、未运行分别说明。
- 同一变更维护受影响的长期知识，允许零文档修改。已确认的未完成选择与阻塞要能从仓库入口找回；完成后收敛，不保存聊天流水。
- 不削弱测试、吞掉失败或放宽预算换取通过。局部规则留在局部，新增永久规则要有重复风险证据。
- 修改后重新评估验证证据；模板检查不替代业务检查，本地通过不等于远端 CI 通过。
- 提交前检查差异、秘密与无关文件，中文说明目的。推送、发布、历史重写、权限与生产操作按明确授权执行。

## 按任务读取 Skill

先读匹配的主文件，再只加载其要求的参考。宿主不自动发现时，使用下列路径；下列路由不是每次必须全量执行的流水线。

| 任务或风险 | 入口 |
| --- | --- |
| 新项目初始化；维护模板本身不触发 | [初始化](.agents/skills/seed-initialize/SKILL.md) |
| 项目事实、结构或文档生命周期 | [文档维护](.agents/skills/seed-doc/SKILL.md) |
| 文字、注释、提示词的完整性与精简 | [表达标准](.agents/skills/seed-prose/SKILL.md) |
| 长期提案、决策、取代与归档 | [Agent Notes](.agents/skills/seed-notes/SKILL.md) |
| 实现、接口、测试的正确性审查 | [代码审查](.agents/skills/seed-code-review/SKILL.md) |
| 开发验收、交付与推送前证据 | [验证](.agents/skills/seed-verify/SKILL.md) |
| 失败、副作用、重试、取消与降级 | [错误处理](.agents/skills/seed-error-handling/SKILL.md) |
| 并发、时序、资源与不稳定测试 | [测试可靠性](.agents/skills/seed-test-reliability/SKILL.md) |
| 界面、交互、响应式与视觉一致性 | [界面](.agents/skills/seed-ui/SKILL.md) |
| 路由、知识漂移、初始化退场与规则负担 | [治理审查](.agents/skills/seed-harness-review/SKILL.md) |

## 本仓库验证

命令与覆盖范围见 [测试说明](docs/testing.md)。基础检查、Skill 格式和真实 Agent 场景分别报告；不得把前两者通过说成模型始终正确。涉及上游改编时同步[来源与许可](THIRD_PARTY_NOTICES.md)及[迁移映射](docs/upstream-mapping.md)。

## 普通开发

确认仓库、分支、已有修改和可观察验收，沿实际接口与消费者实施最小必要变更。先复现缺陷，按风险读取上表方法；长期选择进入 Notes，当前事实原位更新。交付前检查最终差异，分别报告通过、失败、未运行和剩余责任。文档名称与创建条件以 [文档约定](docs/AGENTS.md) 为准。
