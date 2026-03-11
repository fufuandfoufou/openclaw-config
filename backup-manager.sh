#!/bin/bash
# OpenClaw Backup Management Script
# 添加到 crontab: 0 2 * * * /Users/openclaw/.openclaw/scripts/backup-manager.sh

OPENCLAW_DIR="$HOME/.openclaw"
BACKUP_DIR="$OPENCLAW_DIR/backups"
MAX_BACKUPS=10

echo "=== Backup Manager Started: $(date) ==="

# Create timestamped backup
timestamp=$(date +%Y%m%d-%H%M%S)
backup_file="$BACKUP_DIR/openclaw-$timestamp.json"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Create backup of openclaw.json
cp "$OPENCLAW_DIR/openclaw.json" "$backup_file"
echo "Created backup: openclaw-$timestamp.json"

# Also backup secrets.env if exists
if [ -f "$OPENCLAW_DIR/secrets.env" ]; then
    cp "$OPENCLAW_DIR/secrets.env" "$BACKUP_DIR/secrets-$timestamp.env"
    echo "Created backup: secrets-$timestamp.env"
fi

# Clean up old backups (keep only MAX_BACKUPS)
echo ""
echo ">>> Cleaning old backups (keeping last $MAX_BACKUPS)..."

# Count JSON backups
json_backups=$(ls -1t "$BACKUP_DIR"/openclaw-*.json 2>/dev/null | wc -l)
echo "  Total JSON backups: $json_backups"

if [ "$json_backups" -gt "$MAX_BACKUPS" ]; then
    delete_count=$((json_backups - MAX_BACKUPS))
    # Delete oldest backups (last in sorted list)
    ls -1t "$BACKUP_DIR"/openclaw-*.json 2>/dev/null | tail -$delete_count | while read -r file; do
        rm -f "$file"
        echo "  Deleted: $(basename "$file")"
    done
    echo "  Removed $delete_count old backup(s)"
fi

# Clean up old secrets backups (keep same count)
secrets_backups=$(ls -1t "$BACKUP_DIR"/secrets-*.env 2>/dev/null | wc -l)
if [ "$secrets_backups" -gt "$MAX_BACKUPS" ]; then
    delete_count=$((secrets_backups - MAX_BACKUPS))
    ls -1t "$BACKUP_DIR"/secrets-*.env 2>/dev/null | tail -$delete_count | while read -r file; do
        rm -f "$file"
    done
fi

# Show remaining backups
echo ""
echo ">>> Current backups:"
ls -1t "$BACKUP_DIR"/openclaw-*.json 2>/dev/null | head -5 | while read -r file; do
    echo "  $(basename "$file")"
done

echo ""
echo "=== Backup Manager Complete: $(date) ==="
