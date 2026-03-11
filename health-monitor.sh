#!/bin/bash
# OpenClaw Health Monitor Script
# 添加到 crontab: */15 * * * * /Users/openclaw/.openclaw/scripts/health-monitor.sh

OPENCLAW_DIR="$HOME/.openclaw"
LOG_DIR="$OPENCLAW_DIR/logs"
ALERT_THRESHOLD_ERRORS=5
ALERT_THRESHOLD_LATENCY_MS=30000

echo "=== Health Check: $(date) ==="

ERRORS=0
WARNINGS=0

# 1. Check Gateway Status
echo ">>> Checking Gateway..."
if pgrep -f "openclaw.*gateway" > /dev/null || pgrep -f "openclaw/dist/index.js" > /dev/null; then
    echo "  Gateway: RUNNING"

    # Check gateway log for recent errors
    recent_errors=$(tail -500 "$LOG_DIR/gateway.log" 2>/dev/null | grep -c "ERROR\|error\|fatal" || echo "0")
    if [ "$recent_errors" -gt "$ALERT_THRESHOLD_ERRORS" ]; then
        echo "  ⚠️  Recent errors found: $recent_errors"
        ERRORS=$((ERRORS + 1))
    else
        echo "  Errors: $recent_errors (ok)"
    fi
else
    echo "  Gateway: NOT RUNNING"
    ERRORS=$((ERRORS + 1))
fi

# 2. Check Disk Space
echo ""
echo ">>> Checking Disk Space..."
disk_usage=$(df -h "$HOME" | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$disk_usage" -gt 90 ]; then
    echo "  ⚠️  Disk usage: ${disk_usage}%"
    ERRORS=$((ERRORS + 1))
elif [ "$disk_usage" -gt 80 ]; then
    echo "  ⚠️  Disk usage: ${disk_usage}% (warning)"
    WARNINGS=$((WARNINGS + 1))
else
    echo "  Disk usage: ${disk_usage}% (ok)"
fi

# 3. Check Log File Sizes
echo ""
echo ">>> Checking Log Files..."
total_log_size=$(du -sm "$LOG_DIR" 2>/dev/null | cut -f1)
if [ "$total_log_size" -gt 500 ]; then
    echo "  ⚠️  Total log size: ${total_log_size}MB (consider rotating)"
    WARNINGS=$((WARNINGS + 1))
else
    echo "  Total log size: ${total_log_size}MB (ok)"
fi

# 4. Check Memory Databases
echo ""
echo ">>> Checking Memory Databases..."
for db in "$OPENCLAW_DIR/memory"/*.sqlite; do
    if [ -f "$db" ]; then
        size=$(du -m "$db" | cut -f1)
        dbname=$(basename "$db")
        if [ "$size" -gt 10 ]; then
            echo "  ⚠️  $dbname: ${size}MB (large)"
            WARNINGS=$((WARNINGS + 1))
        else
            echo "  $dbname: ${size}MB (ok)"
        fi
    fi
done

# 5. Check Cron Jobs Status
echo ""
echo ">>> Checking Cron Jobs..."
# Check if cron jobs ran recently
last_heartbeat=$(find "$OPENCLAW_DIR/cron" -name "*.json" -mmin -20 2>/dev/null | wc -l)
if [ "$last_heartbeat" -gt 0 ]; then
    echo "  Recent cron activity: found"
else
    echo "  ⚠️  No recent cron activity"
    WARNINGS=$((WARNINGS + 1))
fi

# 6. Check ACPX Sessions
echo ""
echo ">>> Checking ACPX..."
if [ -d "$HOME/.acpx/sessions" ]; then
    acpx_sessions=$(ls -1 "$HOME/.acpx/sessions"/*.json 2>/dev/null | wc -l)
    echo "  Active sessions: $acpx_sessions"
else
    echo "  ACPX sessions directory not found"
fi

# Summary
echo ""
echo "=== Summary ==="
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"

if [ "$ERRORS" -gt 0 ]; then
    echo "Status: ❌ CRITICAL"
    exit 1
elif [ "$WARNINGS" -gt 0 ]; then
    echo "Status: ⚠️  WARNING"
    exit 0
else
    echo "Status: ✅ HEALTHY"
    exit 0
fi
