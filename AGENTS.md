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
| 用户要求从模板开始新项目；维护本模板不触发 | [初始化](.agents/skills/seed-initialize/SKILL.md) |
| 已授权功能、修复、重构 | [开发变更](.agents/skills/seed-change/SKILL.md) |
| 交付或推送前选择、核实验证证据 | [验证](.agents/skills/seed-verify/SKILL.md) |
| 审查实现及测试是否满足需求 | [代码审查](.agents/skills/seed-code-review/SKILL.md) |
| 文档分类、事实更新、迁移或整理 | [文档维护](.agents/skills/seed-doc/SKILL.md) |
| 编写或精简文字、注释和指令 | [表达标准](.agents/skills/seed-prose/SKILL.md) |
| Harness 路由、规则或知识漂移 | [治理审查](.agents/skills/seed-review/SKILL.md) |
| 失败、副作用、重试、取消和降级 | [错误处理](.agents/skills/seed-error-handling/SKILL.md) |
| 不稳定测试、并发资源或新测试门禁 | [测试可靠性](.agents/skills/seed-test-reliability/SKILL.md) |
| 注册、后台任务与销毁次序 | [资源生命周期](.agents/skills/seed-resource-lifecycle/SKILL.md) |
| 工具、提示词和 Agent 工作流设计 | [Agent 使用体验](.agents/skills/seed-agent-experience/SKILL.md) |
| 复杂度与维护负担简化 | [简化设计](.agents/skills/seed-find-simplifications/SKILL.md) |
| 已确认性能问题或性能改动 | [性能](.agents/skills/seed-performance/SKILL.md) |
| UI 交互、布局、响应式 | [界面](.agents/skills/seed-ui/SKILL.md) |
| 需要真实 UI 操作证据 | [界面证据](.agents/skills/seed-ui-evidence/SKILL.md) |
| 修改已有日志派生的 projection/reducer 或其恢复契约 | [状态投影](.agents/skills/seed-state-projection/SKILL.md) |
| 编写或更新 PR 说明 | [PR 说明](.agents/skills/seed-pr-description/SKILL.md) |
| 明确涉及依赖 PR 链 | [依赖 PR](.agents/skills/seed-stacked-prs/SKILL.md) |
| 对外破坏性变化，或修改/撤回未发布指南涵盖的变化 | [升级指南](.agents/skills/seed-upgrade-guide/SKILL.md) |
| 整理已存在的决策记录 | [决策归档](.agents/skills/seed-archive-decisions/SKILL.md) |
| 指定范围清理过时过程叙事 | [过程残留](.agents/skills/seed-trim-session-residue/SKILL.md) |
| 用户明确要求翻译或调用翻译 Skill | [翻译](.agents/skills/seed-translate/SKILL.md) |

## 本仓库验证

命令与覆盖范围见 [README 的本地检查](README.md#本地检查)。基础检查、Skill 格式和真实 Agent 场景分别报告；不得把前两者通过说成模型始终正确。涉及上游改编时同步[来源与许可](THIRD_PARTY_NOTICES.md)及[迁移映射](docs/upstream-mapping.md)。
