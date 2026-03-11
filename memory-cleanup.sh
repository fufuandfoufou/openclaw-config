#!/bin/bash
# OpenClaw Memory Cleanup Script
# 添加到 crontab: 0 3 * * 0 /Users/openclaw/.openclaw/scripts/memory-cleanup.sh

MEMORY_DIR="$HOME/.openclaw/memory"
MAX_DAYS=30

echo "=== Memory Cleanup Started: $(date) ==="

# 1. VACUUM each SQLite database to reclaim space
echo ">>> Optimizing databases..."
for db in "$MEMORY_DIR"/*.sqlite; do
    if [ -f "$db" ]; then
        filename=$(basename "$db")
        size_before=$(du -m "$db" | cut -f1)

        # Run VACUUM to optimize database
        sqlite3 "$db" VACUUM 2>/dev/null

        size_after=$(du -m "$db" | cut -f1)
        saved=$((size_before - size_after))

        if [ "$saved" -gt 0 ]; then
            echo "  $filename: ${size_before}MB -> ${size_after}MB (saved ${saved}MB)"
        else
            echo "  $filename: ${size_before}MB (no change)"
        fi
    fi
done

# 2. Clean up old data (entries older than MAX_DAYS)
echo ""
echo ">>> Cleaning old entries (older than $MAX_DAYS days)..."

# Find and delete old sessions in agent directories
for agent_dir in "$HOME/.openclaw/agents"/*/sessions; do
    if [ -d "$agent_dir" ]; then
        agent_name=$(basename "$agent_dir")

        # Find .jsonl.deleted.* files older than MAX_DAYS
        deleted_count=$(find "$agent_dir" -name "*.jsonl.deleted.*" -mtime +$MAX_DAYS 2>/dev/null | wc -l)

        if [ "$deleted_count" -gt 0 ]; then
            find "$agent_dir" -name "*.jsonl.deleted.*" -mtime +$MAX_DAYS -delete 2>/dev/null
            echo "  $agent_name: deleted $deleted_count old session files"
        fi
    fi
done

# 3. Clean up old acpx sessions
if [ -d "$HOME/.acpx/sessions" ]; then
    old_acpx=$(find "$HOME/.acpx/sessions" -name "*.json" -mtime +$MAX_DAYS 2>/dev/null | wc -l)
    if [ "$old_acpx" -gt 0 ]; then
        find "$HOME/.acpx/sessions" -name "*.json" -mtime +$MAX_DAYS -delete 2>/dev/null
        find "$HOME/.acpx/sessions" -name "*.ndjson" -mtime +$MAX_DAYS -delete 2>/dev/null
        echo "  acpx: deleted $old_acpx old session files"
    fi
fi

echo ""
echo "=== Cleanup Complete: $(date) ==="
