---
name: market-watch-skill
description: A股/港股观察与持仓跟踪 skill。用于晨报候选池、收盘复盘、持仓出入场条件、A股核心池/弹性池/题材池、港股核心池/弹性池/主题池、以及对指定持仓给出更明确的加仓/减仓/观望条件。触发场景：用户要求推荐明天关注的股票、做盘后复盘、分析某只A股或港股、跟踪已有持仓、优化次日持仓计划。
---

# Market Watch Skill

Manage a practical A/H stock watch workflow for OpenClaw: morning watchlists, post-close review, fixed candidate buckets, and position-specific action rules.

## When to Use

Use this skill when the user asks to:
- Recommend A股 or 港股 for next-day attention
- Produce a morning stock brief or post-close review
- Track existing positions and define add / reduce / wait conditions
- Turn an ad-hoc stock workflow into a repeatable system

## Routing

- **A股 watchlist / candidate buckets** → run `scripts/ashare_watchlist_report.py`
- **港股 watchlist / position tracking** → run `scripts/hk_watchlist_report.py`
- **Need the logic behind the buckets or rules** → read `references/strategy-notes.md`
- **Need the bucket definitions** → read `references/buckets.md`
- **Need clearer position action rules** → read `references/position-rules.md`
- **Need to wire into cron / automation** → read `references/automation.md`

## Working Rules

- Be explicit about data limits: current setup is mostly daily/after-close, not tick-level execution
- Distinguish confirmed data from inference
- Prefer clear action rules over vague opinions
- For positions, always separate: add condition / reduce condition / wait condition / fail condition
- For candidate lists, diversify by bucket or industry when possible instead of recommending three near-identical names

## Output Pattern

Default structure:
1. What the market watchlist says
2. Top candidates
3. Position rules
4. Risks / what would invalidate the plan

## References
- `references/strategy-notes.md` — Practical quant-style heuristics used in this workflow.
- `references/buckets.md` — What each watchlist bucket means.
- `references/position-rules.md` — How to state add / reduce / wait / fail conditions.
- `references/automation.md` — How to connect the skill to cron-based morning / closing workflows.
