# Strategy Notes

This skill does not pretend to run a full institutional quant stack. It uses practical, lightweight heuristics that are robust enough for daily watchlists and position management.

## Core ideas

### 1. Trend first
Use short and medium moving averages (MA5 / MA10 / MA20) to judge whether price is trending, stalling, or weakening.

### 2. Breakout confirmation
Do not add just because a name is down from cost. Prefer adding only after price reclaims a short-term high or key moving average.

### 3. Relative activity matters
Use turnover, volume expansion, and money-flow style proxies to separate dead names from active names.

### 4. Bucket the universe
For A股, split candidates into:
- 核心池
- 弹性池
- 题材池

For 港股, split candidates into:
- 核心大票池
- 核心观察池
- 弹性机会池
- 主题/ETF池

This makes the daily output more stable than ranking the whole market with one score.

### 5. Position plans need triggers
For trapped positions, always define:
- wait zone
- add trigger
- reduce trigger
- fail / defense trigger

## What this is good for
- Morning watchlists
- End-of-day review
- Next-day planning
- Managing swing-style positions

## What this is not good for
- Tick-level scalping
- Intraday execution quality
- True high-frequency or market-making logic
