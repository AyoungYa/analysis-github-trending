---
name: gh-trend
description: Analyze GitHub Trending and popular open-source repositories. Use when users ask about hot repos, open-source trends, repo value, or trend reports.
---

# GitHub Trending Analysis

This Codex skill turns GitHub Trending data into a structured technical judgment: what is actually valuable, what is noisy, what to study, and what to track.

## References

Load only the files needed for the user request:

- `../../../core/analysis-framework.md` for workflow
- `../../../core/data-source-strategy.md` for data collection and uncertainty handling
- `../../../core/scoring-rubric.md` for project scoring
- `../../../core/report-templates.md` for output templates

If this skill is installed standalone, use the bundled copies instead:

- `references/analysis-framework.md`
- `references/data-source-strategy.md`
- `references/scoring-rubric.md`
- `references/report-templates.md`

## Operating procedure

1. Determine the requested scope: time window, language, topic, and audience.
2. Use available tools to collect current data if the user expects latest/trending information.
3. If live data is unavailable, ask for repository URLs or pasted Trending content.
4. Evaluate candidate repositories with the scoring rubric.
5. Produce the closest matching report template.
6. Keep the answer actionable: learn, try, watch, skip.

## Defaults

- Language: Chinese
- Time window: daily
- Audience: developer
- Output: concise structured Markdown
- Evidence: prefer GitHub README, releases, issues, PRs, commits, license, and official docs

## Required safeguards

- Do not fabricate current Trending entries or metrics.
- Mark unverifiable facts as assumptions.
- Explain why a project is trending, not just what it does.
- Include risk, maturity, and next-step recommendations.
