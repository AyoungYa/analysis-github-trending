# Data Source Strategy

GitHub Trending 没有稳定官方 API。执行分析时，优先使用用户提供的数据；如果没有，则根据当前平台能力选择可用数据源。

## 数据源优先级

1. 用户提供的仓库列表、Trending 页面内容、截图转文本或 CSV  
   这是最可靠输入。保留用户给出的排序、时间范围和语言筛选条件。

2. 平台内置联网搜索或浏览器  
   访问 `https://github.com/trending`，根据用户要求选择语言和时间范围，例如 daily、weekly、monthly。

3. 本项目脚本  
   如果当前平台允许运行本地脚本和联网，优先使用 `scripts/fetch_trending.py` 获取结构化候选列表。该脚本只依赖 Python 标准库，也支持 `--input-html` 解析用户提供的 Trending HTML。

4. GitHub 仓库页面和 README  
   对入选仓库逐个补充 README、stars、forks、issues、releases、commit 活跃度、license、主要贡献者等信息。

5. 第三方趋势源  
   可参考 Trendshift、HelloGitHub、GitHub Explore、Hacker News、Reddit、X、Product Hunt 等，但必须标注为辅助信号。

6. 估算或缺失处理  
   如果无法联网或信息不足，明确写出“数据不足”，不要编造 star 增量、发布时间、融资、用户量或 benchmark。

## 推荐采集字段

对每个仓库尽量收集：

- 仓库名和 URL
- 一句话描述
- 主要语言和关键技术栈
- stars、forks、今日/本周 star 增长
- 创建时间和最近更新时间
- README 成熟度
- issue / PR 活跃度
- release / tag 情况
- license
- 安装和上手成本
- 目标用户和典型场景
- 与同类项目的差异
- 潜在风险

## 数据可信度分级

- A: 来自 GitHub 仓库页面、README、release、issue、commit 等一手来源
- B: 来自官方文档、作者博客、项目官网
- C: 来自第三方榜单、媒体、社区讨论
- D: 来自模型推断或不完整输入

报告中涉及关键判断时，优先使用 A/B 级证据。C/D 级只能作为辅助，不应作为强结论。

## 时间范围处理

用户没有指定时间范围时，默认分析 daily trending。若用户问“趋势”“周报”“最近”，优先使用 weekly，并在报告开头说明假设。

常见范围：

- daily: 适合捕捉新热点，但噪声最大
- weekly: 适合判断真实关注度
- monthly: 适合观察中期技术方向

## 联网不可用时的降级策略

如果平台不能联网：

1. 请用户提供 GitHub Trending 页面内容或仓库列表
2. 基于已有输入做结构化分析
3. 明确列出无法验证的字段
4. 不输出“今日”“最新”等强时效性结论
