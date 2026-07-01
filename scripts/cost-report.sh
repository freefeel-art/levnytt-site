#!/usr/bin/env bash
#
# Cost Report V1 — LevNytt Production Telemetry
#
# Aggregates production/logs/history.json for cost analysis.
# No database, no dashboard — just JSON and jq.
#
# Usage:
#   ./scripts/cost-report.sh                    # all-time summary
#   ./scripts/cost-report.sh --today            # today's runs
#   ./scripts/cost-report.sh --month 2026-07    # specific month
#   ./scripts/cost-report.sh --article vad-ar-lutein  # per-article detail
#   ./scripts/cost-report.sh --per-article      # cost per article list
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

HISTORY="production/logs/history.json"

if [ ! -f "$HISTORY" ]; then
    echo "No telemetry data yet. Run a production to generate history.json."
    exit 0
fi

GREEN='\033[0;32m'
GOLD='\033[0;33m'
NC='\033[0m'

# ─── All-time summary (default) ─────────────────────────────────────────
summary() {
    local count total_cost total_tokens total_duration avg_cost
    count=$(jq 'length' "$HISTORY")
    total_cost=$(jq '[.[].estimated_cost_usd] | add // 0' "$HISTORY")
    total_tokens=$(jq '[.[].total_tokens] | add // 0' "$HISTORY")
    total_duration=$(jq '[.[].duration_ms] | add // 0' "$HISTORY")
    avg_cost=$(echo "scale=4; $total_cost / $count" | bc 2>/dev/null || echo "0")

    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════${NC}"
    echo -e "${GREEN}  LevNytt Production Cost Report${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════${NC}"
    echo ""
    echo "  Total runs:        $count"
    echo "  Total tokens:      $(printf "%'d" $total_tokens)"
    echo "  Total cost:        \$$(printf "%.3f" $total_cost)"
    echo "  Total duration:    $(echo "scale=1; $total_duration / 1000" | bc)s"
    echo "  Avg cost/article:  \$$(printf "%.4f" $avg_cost)"
    echo ""
}

# ─── Today ──────────────────────────────────────────────────────────────
today() {
    local today
    today=$(date +%Y-%m-%d)
    jq --arg d "$today" '[.[] | select(.timestamp | startswith($d))]' "$HISTORY" | \
        jq '{count: length, cost: [.[].estimated_cost_usd] | add // 0, tokens: [.[].total_tokens] | add // 0}'
}

# ─── Month ──────────────────────────────────────────────────────────────
month() {
    local ym="${1:-}"
    if [ -z "$ym" ]; then
        ym=$(date +%Y-%m)
    fi
    jq --arg ym "$ym" '[.[] | select(.timestamp | startswith($ym))]' "$HISTORY" | \
        jq '{month: $ym, count: length, cost: [.[].estimated_cost_usd] | add // 0, tokens: [.[].total_tokens] | add // 0}'
}

# ─── Per article ────────────────────────────────────────────────────────
per_article() {
    jq -r '.[] | "\(.article)\t\(.timestamp)\t\(.estimated_cost_usd)\t\(.status)"' "$HISTORY" | \
        column -t -s $'\t' -N "ARTICLE,TIMESTAMP,COST,STATUS"
}

# ─── Single article detail ──────────────────────────────────────────────
article_detail() {
    local slug="${1:-}"
    if [ -z "$slug" ]; then
        echo "Usage: ./scripts/cost-report.sh --article <slug>"
        exit 1
    fi
    local log_file="production/logs/"*"-$slug.json"
    if ls $log_file 1>/dev/null 2>&1; then
        jq '.' $log_file
    else
        echo "No detailed log found for: $slug"
        echo "Checking history..."
        jq --arg s "$slug" '.[] | select(.article == $s)' "$HISTORY"
    fi
}

# ─── Parse flags ────────────────────────────────────────────────────────
case "${1:-}" in
    --today)
        today
        ;;
    --month)
        month "${2:-}"
        ;;
    --per-article)
        per_article
        ;;
    --article)
        article_detail "${2:-}"
        ;;
    *)
        summary
        ;;
esac