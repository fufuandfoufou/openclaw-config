#!/bin/bash
# OpenClaw Log Rotation Script
# 添加到 crontab: 0 0 * * * /Users/openclaw/.openclaw/scripts/log-rotate.sh

LOG_DIR="$HOME/.openclaw/logs"
MAX_SIZE_MB=10
MAX_DAYS=7

# 限制日志文件大小
rotate_if_needed() {
    local logfile="$1"
    local basename=$(basename "$logfile")

    if [ -f "$logfile" ]; then
        local size_mb=$(du -m "$logfile" | cut -f1)

        if [ "$size_mb" -gt "$MAX_SIZE_MB" ]; then
            echo "Rotating $basename (size: ${size_mb}MB)"

            # 压缩并归档
            timestamp=$(date +%Y%m%d-%H%M%S)
            gzip -c "$logfile" > "$LOG_DIR/archive/${basename}.${timestamp}.gz"

            # 清空当前日志
            : > "$logfile"

            echo "  -> Archived to ${basename}.${timestamp}.gz"
        fi
    fi
}

# 清理过期归档
cleanup_old() {
    find "$LOG_DIR/archive" -name "*.gz" -mtime +$MAX_DAYS -delete
    echo "Cleaned up archives older than $MAX_DAYS days"
}

# 确保归档目录存在
mkdir -p "$LOG_DIR/archive"

# 执行日志轮转
rotate_if_needed "$LOG_DIR/gateway.log"
rotate_if_needed "$LOG_DIR/gateway.err.log"

# 清理过期归档
cleanup_old

echo "Log rotation completed at $(date)"
