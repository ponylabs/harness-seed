# Harness Seed

面向 AI 协作开发的轻量项目基础模板。它用简短规则、按需加载的项目 Skill 和可执行检查，让新项目逐步形成自己的文档与验证体系，不预设业务技术栈或目录树。

## 从这里开始

- 维护本模板：先读 [AGENTS.md](AGENTS.md)。本仓库已经是一个真实项目，不要在这里初始化示例业务。
- 创建新项目：复制模板到新的仓库，再要求 Agent：“读取 AGENTS.md 和 seed-initialize，按我的需求初始化这个项目，先确认必要方案。”
- 查看方法与边界：[设计说明](docs/design.md)。
- 查看已执行和可复现的检查：[验证说明](docs/validation.md)。

初始化完成后，新项目应替换本 README 为真实项目说明，移除不再适用的模板教程和链接，并更新 AGENTS 中的验证命令。保留可复用 Skill 不等于保留初始化问卷。

## 组成

- 根 AGENTS：全局约束和阅读入口；子 AGENTS 仅为真实存在的局部约束创建。
- README 与项目文档：用途、边界、契约、操作方法等事实；不复制 Skill 的工作教程。
- `.agents/skills/`：初始化、变更、文档维护、表达标准和治理审查五个 Skill。
- `scripts/check_harness.py` 与测试：用 Python 标准库检查必需入口、Skill 元数据和本地 Markdown 文件链接，并测试检查器的失败路径。
- GitHub Actions：执行同一套检查。工作流不等于已配置分支保护，也不保证所有 Agent 自动读取规则。

## 本地检查

需要 Python 3.10 或以上，无第三方 Python 依赖。在仓库根目录运行：

```sh
python3 scripts/check_harness.py
python3 -m unittest discover -s tests -v
git diff --check
```

检查器默认扫描仓库中的 Markdown（忽略 Git、依赖和缓存目录），不访问外部链接、不检查锚点。它不会执行文档中的命令。大规模派生项目可调整忽略配置，并在 README 说明理由。

## Agent 兼容性

首版使用 `.agents/skills/<名称>/SKILL.md` 作为唯一技能来源。支持项目 Skill 的宿主可以发现它们；其他宿主需要显式读取 AGENTS 指向的文件。没有宣称所有工具的自动发现、嵌套规则加载或调用行为一致。若需要工具专用入口，新增薄适配，不复制另一套规范正文。

## 来源与许可

工程思路参考 [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)，本仓库为独立编写，并非其官方模板；没有复制其产品专属契约、双语规则或站点模板。当前未选定开源许可证，公开可见不代表获得额外的再分发许可；发布复用前由仓库所有者决定许可。
