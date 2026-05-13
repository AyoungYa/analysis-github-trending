# GitHub Trending Analysis Skill

一套跨 AI 平台的 GitHub Trending 分析 skill，用于帮助 Claude Code、Codex、Gemini、Trae、Clawbot 等 agent 从热门仓库中识别真实技术趋势、项目价值和可行动机会。

当前版本先实现平台无关核心框架，以及 Claude Code / Codex 双适配。

## 适用场景

- 生成每日、每周或每月 GitHub Trending 技术简报
- 分析某个语言或方向的热门仓库，例如 Python、TypeScript、Rust、AI Agent、LLM Infra、DevTools
- 判断单个仓库是否值得学习、跟进、fork、集成或商业化研究
- 从 GitHub Trending 中提炼技术趋势、产品机会和学习路线
- 对热门项目做风险识别，避免只被短期 star 增长误导

## 设计原则

1. 平台无关核心优先  
   核心分析框架、评分标准和报告模板不依赖任何单一 AI 平台。

2. 平台适配层保持薄  
   Claude Code 和 Codex 的 `SKILL.md` 只负责触发、工作流和资源指向，避免重复维护分析逻辑。

3. 数据源可替换  
   GitHub Trending 没有官方 API。skill 应该支持网页搜索、GitHub 页面、第三方趋势源、用户粘贴列表、脚本抓取等多种数据来源。

4. 输出必须可行动  
   不只复述 README，而要给出项目价值、风险、适合人群和下一步建议。

## 项目结构

```text
analysis-github-trending/
├── README.md
├── core/
│   ├── analysis-framework.md
│   ├── data-source-strategy.md
│   ├── report-templates.md
│   └── scoring-rubric.md
├── skills/
│   ├── claude-code/
│   │   └── gh-trend/
│   │       ├── SKILL.md
│   │       └── references/
│   └── codex/
│       └── gh-trend/
│           ├── SKILL.md
│           └── references/
├── examples/
│   ├── daily-report.md
│   └── repo-deep-dive.md
└── evals/
    └── evals.json
```

## 使用方式

### Claude Code

将 `skills/claude-code/gh-trend/` 作为 Claude Code skill 安装或引用。该目录已包含 `references/`，可以独立复制到 Claude Code 的 skill 目录。触发请求示例：

```text
/gh-trend 分析今天 GitHub Trending 上 AI Agent 相关项目，给我一份中文简报。
```

### Codex

将 `skills/codex/gh-trend/` 作为 Codex skill 安装或引用。该目录已包含 `references/`，可以独立复制到 Codex 的 skill 目录。触发请求示例：

```text
/gh-trend 看一下本周 TypeScript 热门项目，有哪些值得学习？
```

## 第一版边界

- 不内置强依赖脚本
- 不假设所有平台都有联网能力
- 不保证 GitHub Trending 页面抓取稳定
- 支持用户直接提供仓库列表或 trending 页面内容
- 报告默认中文输出，可按用户要求切换英文或中英双语

## 后续扩展

- 增加 `scripts/fetch_trending.py`
- 增加 Gemini、Trae、Clawbot 适配入口
- 增加自动化周报模板
- 增加可执行 eval，用于比较有无 skill 时的分析质量
