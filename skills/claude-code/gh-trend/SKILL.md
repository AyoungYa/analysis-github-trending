---
name: gh-trend
description: Analyze GitHub Trending, hot repos, open-source trends, and whether a repo is worth learning, adopting, forking, or tracking.
---

# GitHub Trending Analysis

Use this skill to analyze GitHub Trending and popular open-source repositories. The goal is to identify real technical value, trend signals, risks, and actionable recommendations.

## Core references

Read these files as needed:

- `../../../core/analysis-framework.md`: main workflow and judgment principles
- `../../../core/data-source-strategy.md`: how to get or validate trending data
- `../../../core/scoring-rubric.md`: 100-point evaluation rubric
- `../../../core/report-templates.md`: report formats

If this skill is installed standalone, use the bundled copies instead:

- `references/analysis-framework.md`
- `references/data-source-strategy.md`
- `references/scoring-rubric.md`
- `references/report-templates.md`

## Default behavior

When the user asks for GitHub Trending analysis:

1. Infer scope from the request:
   - Time range: daily by default, weekly for "trend" or "recent" requests
   - Language/topic: use the user's requested filter if present
   - Output language: Chinese by default unless the user asks otherwise
   - Persona: developer by default
2. Gather data from user input or available browsing/search tools.
3. If current data cannot be verified, state the limitation and ask for a repo list or page content.
4. Analyze using the core framework.
5. Output a structured report with conclusion, evidence, risks, and next actions.

## Data handling

GitHub Trending has no stable official API. Do not invent current trending data. If browsing is unavailable, ask the user to provide:

- GitHub Trending page text
- A list of repo URLs
- A screenshot converted to text
- A CSV or Markdown table of candidate repositories

## Report selection

- Use Daily Trending Brief for "today", "daily", "GitHub Trending"
- Use Weekly Trend Report for "trend", "this week", "recent", "方向"
- Use Repo Deep Dive for a single repository
- If the user wants a decision, lead with "建议" and "理由"

## Quality bar

Always distinguish popularity from value. Include at least one risk or uncertainty section. Do not merely summarize README files.
