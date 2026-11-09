# Harness Seed

面向 AI 协作开发的轻量项目基础模板。它用精简入口、按需加载的成熟工作方法和可执行检查，让新项目逐步形成自己的文档与验证体系，统一文档骨架而不预设业务技术栈或代码目录树。

## 从这里开始

- 维护本模板：先读 [AGENTS.md](AGENTS.md)。本仓库已经是一个真实项目，不要在这里初始化示例业务。
- 创建新项目：复制模板到新的仓库，再要求 Agent：“读取 AGENTS.md 和 seed-initialize，按我的需求初始化这个项目，先确认必要方案。”
- 开发本模板：[开发说明](docs/development.md)。
- 了解固定名称与按需目录：[文档约定](docs/AGENTS.md)。
- 查看方法与边界：[设计说明](docs/architecture.md)。
- 查看检查方法与覆盖范围：[验证说明](docs/testing.md)。

初始化完成后，新项目应替换本 README 为真实项目说明，移除不再适用的模板教程和链接，并同步实际本地验证与 CI。保留适用改编内容时也要保留必要版权与许可。保留可复用 Skill 不等于保留初始化问卷。

## 组成

- 根 AGENTS：全局约束和阅读入口；子 AGENTS 仅为真实存在的局部约束创建。
- README 与项目文档：用途、边界、契约、操作方法等事实；不复制 Skill 的工作教程。
- `.agents/skills/`：通用开发与文档工作流，以及按场景加载的错误、测试、UI、性能、发布等专题；入口与触发条件见 AGENTS。
- `scripts/check_harness.py` 与测试：用 Python 标准库检查六个固定入口、Notes 格式与冻结、Skill 元数据和活跃 Markdown 文件链接，并测试检查器的失败路径。
- GitHub Actions：执行同一套检查。工作流不等于已配置分支保护，也不保证所有 Agent 自动读取规则。

## 本地检查

需要 Python 3.10 或以上，无第三方 Python 依赖。精确命令、覆盖边界和验证记录统一见 [测试说明](docs/testing.md)；开发环境与变更流程见 [开发说明](docs/development.md)。

## Agent 兼容性

使用 `.agents/skills/<名称>/SKILL.md` 作为唯一技能来源。支持项目 Skill 的宿主可以发现它们；其他宿主需要显式读取 AGENTS 指向的文件。没有宣称所有工具的自动发现、嵌套规则加载或调用行为一致。若需要工具专用入口，新增薄适配，不复制另一套规范正文。

## 来源与许可

本轮 Skill 依据 [DeepSeek Harness 固定版本](https://github.com/deepseek-ai/deepseek-harness/tree/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159) 做中文翻译和适配。保留通用判断细节，移除产品专属命令与强制技术假设，不是官方模板，也不声称完全等价。

独立 Skill 入口与全部 22 个上游 Skill 的对应去向见[迁移映射](docs/upstream-mapping.md)，版权和 MIT 原文见[第三方声明](THIRD_PARTY_NOTICES.md)。本仓库自行新增部分的统一开源许可尚待所有者决定，不能将公开可见理解为任意再分发许可。
