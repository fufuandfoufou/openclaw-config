# OpenClaw Configuration

My personal OpenClaw configuration backup.

## 📁 Repository Structure

```
.
├── README.md                 # This file
├── .gitignore               # Git ignore rules
├── openclaw.json            # Main configuration (sanitized)
├── scripts/                 # Maintenance scripts
│   ├── backup-manager.sh
│   ├── health-monitor.sh
│   ├── log-rotate.sh
│   └── memory-cleanup.sh
├── agents/                  # Agent configurations
│   └── [agent-id]/
│       └── agent/
│           └── models.json  # Agent-specific model configs
└── dotfiles/                # Shell configuration
    └── .zshenv              # Environment variable loader
```

## 🔐 Secrets Management

**Never commit `secrets.env`!**

This repository uses environment variables for secrets. See `secrets.env.example` for required variables.

### Required Environment Variables

| Variable | Purpose |
|----------|---------|
| `OPENCLAW_GATEWAY_TOKEN` | Gateway authentication |
| `OPENCLAW_MINIMAX_API_KEY` | MiniMax API access |
| `OPENCLAW_MINIMAX_CN_API_KEY` | MiniMax CN API access |
| `OPENCLAW_ARK_API_KEY` | Ark/Volces API access |
| `OPENCLAW_OPENAI_API_KEY` | OpenAI-compatible API access |
| `OPENCLAW_TELEGRAM_BOT_TOKEN` | Telegram bot integration |
| `OPENCLAW_FEISHU_APP_SECRET` | Feishu integration |
| `OPENCLAW_MEMORYSEARCH_REMOTE_API_KEY` | Memory search service |

## 🚀 Setup Instructions

### First Time Setup

```bash
# Clone the repository
git clone <your-repo-url> ~/openclaw-config

# Copy config files to OpenClaw directory
cp -r ~/openclaw-config/* ~/.openclaw/

# Create secrets.env file
cp ~/.openclaw/secrets.env.example ~/.openclaw/secrets.env
# Edit secrets.env with your actual API keys

# Setup zshenv (optional but recommended)
cp ~/.openclaw/dotfiles/.zshenv ~/.zshenv
```

### Daily Usage

After setup, all OpenClaw commands will automatically load environment variables from `secrets.env`.

```bash
openclaw status
openclaw agent list
```

## 📝 Maintenance

### Backup (Automated via Cron)

The `backup-manager.sh` script runs daily at 2 AM to backup configuration:

```bash
# Manual backup
~/.openclaw/scripts/backup-manager.sh
```

### Log Rotation (Automated)

Logs are rotated when they exceed 10MB, archived for 7 days.

### Memory Cleanup (Automated)

SQLite databases are optimized weekly (Sundays at 3 AM).

## 🔧 Customization

### Adding New Models

Edit `openclaw.json`:

```json
{
  "models": {
    "providers": {
      "your-provider": {
        "baseUrl": "https://api.example.com",
        "apiKey": {
          "source": "env",
          "provider": "default",
          "id": "YOUR_API_KEY_ENV_VAR"
        },
        "models": [...]
      }
    }
  }
}
```

### Adding New Agents

Edit `agents.list` in `openclaw.json`:

```json
{
  "id": "my-agent",
  "name": "My Agent",
  "workspace": "~/.openclaw/workspace-my-agent",
  "agentDir": "~/.openclaw/agents/my-agent/agent",
  "model": "openai/gpt-5.4"
}
```


## 📈 Stock Automation

This setup now includes a lightweight market watch workflow for A-shares and Hong Kong stocks.

### Scheduled Jobs

- **08:30 daily** — Morning brief
  - A-share watchlist from fixed buckets: core / momentum / theme
  - HK watchlist from fixed buckets: large-cap core / core watch / opportunity / theme-ETF
  - Position tracking for:
    - `07226.HK` (2x Long HSTECH ETF)
    - `03896.HK` (Kingsoft Cloud)

- **16:30 daily** — Post-close review
  - Market recap for A-shares and HK stocks
  - Candidate bucket changes
  - Position review and next-day action rules

### Market Watch Skill

The repo also stores a reusable skill:

- `skills/market-watch-skill/`

It contains:
- `SKILL.md`
- `scripts/ashare_watchlist_report.py`
- `scripts/hk_watchlist_report.py`
- `references/` for strategy notes, bucket definitions, position rules, and automation guidance

### Current Data Sources

- **A-shares**: TuShare (daily/after-close data)
- **HK stocks**: AKShare (daily historical data + public info)

### Important Limitation

This workflow is designed for daily watchlists, post-close review, and next-day planning.
It is **not** a tick-level or high-frequency trading system.

## 📊 Provider Summary

| Provider | Base URL | Models |
|----------|----------|--------|
| minimax | https://api.minimax.chat/v1/text | MiniMax |
| ark | https://ark.cn-beijing.volces.com/api/coding/v3 | minimax-2.5 |
| minimax-cn | https://api.minimaxi.com/anthropic | MiniMax-M2.5 |
| openai | https://gmncode.cn/v1 | gpt-5-codex, gpt-5.1-codex, gpt-5.2, gpt-5.4 |

## ⚠️ Important Notes

1. **Never commit `secrets.env`** - It contains sensitive API keys
2. **Test before pushing** - Run `openclaw status` to verify config
3. **Keep backups** - The backup-manager keeps last 10 backups
4. **Monitor logs** - Check `~/.openclaw/logs/` if issues occur

## 🔄 Sync with GitHub

```bash
# After making changes
cd ~/.openclaw
git add .
git commit -m "Update config: [description]"
git push origin main

# On a new machine
git pull origin main
```

### Verified from OpenClaw Runtime

On 2026-03-11, the GitHub path was verified end-to-end from the OpenClaw runtime:
- clone repository
- edit file
- commit locally
- authenticate git via `gh auth setup-git`
- push to `main`

This means future small config updates can be pushed directly from the running OpenClaw environment.
