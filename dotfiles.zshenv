# OpenClaw Global Environment Variables
# Loaded for all zsh sessions (interactive and non-interactive)

# OpenClaw Secrets - Auto-loaded for all shell sessions
if [ -f "$HOME/.openclaw/secrets.env" ]; then
    set -a
    source "$HOME/.openclaw/secrets.env"
    set +a
fi
