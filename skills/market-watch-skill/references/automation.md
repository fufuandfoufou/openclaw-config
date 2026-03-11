# Automation

This skill is designed to work well with OpenClaw cron jobs.

## Recommended use

- Morning cron: read both A股 and 港股 scripts, produce watchlists and position rules
- Post-close cron: read both scripts again, combine with market summary and public news, then suggest next-day adjustments

## Scripts

- `scripts/ashare_watchlist_report.py`
- `scripts/hk_watchlist_report.py`

Both scripts output structured JSON so the agent can summarize without re-deriving every rule from scratch.
