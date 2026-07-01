#!/usr/bin/env bash
#
# QA Article Validator V1
#
# Validates a content/articles/<slug>/<slug>.html file against the
# PAS V1.0 Publication Article Standard. 12 critical checks.
#
# Usage:
#   ./scripts/qa-article.sh <slug>
#   ./scripts/qa-article.sh vad-ar-lutein
#
# Exit codes:
#   0 — GREEN  (12/12 — all pass)
#   1 — AMBER  (10-11/12 — warnings)
#   2 — RED    (<10/12 — critical failures, must fix)
#   3 — ERROR  (file not found, invalid input)
#

set -euo pipefail

# ─── Colors ─────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
GOLD='\033[0;33m'
NC='\033[0m'

# ─── Validate input ─────────────────────────────────────────────────────
SLUG="${1:-}"

if [ -z "$SLUG" ]; then
    echo -e "${RED}ERROR: Missing slug.${NC}"
    echo "Usage: ./scripts/qa-article.sh <slug>"
    exit 3
fi

# ─── Repository root detection ──────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

ARTICLE="content/articles/$SLUG/$SLUG.html"

# ─── Header ─────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         QA Article Validator V1                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo "Article: $ARTICLE"
echo ""

# ─── Check file exists ──────────────────────────────────────────────────
if [ ! -f "$ARTICLE" ]; then
    echo -e "${RED}FAIL: File not found: $ARTICLE${NC}"
    exit 3
fi

PASS=0
FAIL=0

check() {
    local num="$1"
    local desc="$2"
    local result="$3"

    if [ "$result" -eq 0 ]; then
        echo -e "  ${GREEN}PASS${NC}   Q$num  $desc"
        PASS=$((PASS + 1))
    else
        echo -e "  ${RED}FAIL${NC}   Q$num  $desc"
        FAIL=$((FAIL + 1))
    fi
}

# ─── Helper: safe grep count (grep -c exits 1 on zero matches) ──────
grep_count() {
    local result
    result=$(grep -c "$1" "$2" 2>/dev/null || echo 0)
    echo "${result}" | head -1
}

# ─── Q1 — File exists ───────────────────────────────────────────────────
test -f "$ARTICLE"
check "1" "File exists" $?

# ─── Q2 — Non-empty (> 5000 bytes) ──────────────────────────────────────
SIZE=$(stat -c%s "$ARTICLE" 2>/dev/null || stat -f%z "$ARTICLE" 2>/dev/null || echo 0)
[ "$SIZE" -gt 5000 ]
check "2" "Non-empty (> 5000 bytes, actual: $SIZE)" $?

# ─── Q3 — Valid HTML shell ──────────────────────────────────────────────
HAS_HTML_OPEN=$(grep_count '<html' "$ARTICLE")
HAS_HTML_CLOSE=$(grep_count '</html>' "$ARTICLE")
HAS_HEAD=$(grep_count '<head>' "$ARTICLE")
HAS_BODY=$(grep_count '<body>' "$ARTICLE")
[ "$HAS_HTML_OPEN" -ge 1 ] && [ "$HAS_HTML_CLOSE" -ge 1 ] && [ "$HAS_HEAD" -ge 1 ] && [ "$HAS_BODY" -ge 1 ]
check "3" "Valid HTML shell (html/head/body)" $?

# ─── Q4 — PAS wrapper: <div class="ia-wrap"><article> ────────────────────
DIV_WRAP=$(grep_count '<div class="ia-wrap"><article>' "$ARTICLE")
MAIN_WRAP=$(grep_count '<main class="ia-wrap">' "$ARTICLE")
[ "$DIV_WRAP" -ge 1 ] && [ "$MAIN_WRAP" -eq 0 ]
check "4" "PAS wrapper (<div>, not <main>)" $?

# ─── Q5 — PAS CSS classes ───────────────────────────────────────────────
HAS_PUNCH=$(grep_count '\.ia-punchline' "$ARTICLE")
HAS_TAKE=$(grep_count '\.ia-takeaways' "$ARTICLE")
HAS_CTA=$(grep_count '\.ia-cta' "$ARTICLE")
HAS_FAQ=$(grep_count '\.ia-faq' "$ARTICLE")
[ "$HAS_PUNCH" -ge 1 ] && [ "$HAS_TAKE" -ge 1 ] && [ "$HAS_CTA" -ge 1 ] && [ "$HAS_FAQ" -ge 1 ]
check "5" "PAS CSS (.ia-punchline/.ia-takeaways/.ia-cta/.ia-faq)" $?

# ─── Q6 — Green/gold palette (NO legacy navy/coral) ─────────────────────
HAS_GREEN=$(grep_count '#1B4332' "$ARTICLE")
HAS_GOLD=$(grep_count '#E8C870' "$ARTICLE")
HAS_NAVY=$(grep_count '#0F1B3A' "$ARTICLE")
HAS_CORAL=$(grep_count '#F25F4C' "$ARTICLE")
[ "$HAS_GREEN" -ge 1 ] && [ "$HAS_GOLD" -ge 1 ] && [ "$HAS_NAVY" -eq 0 ] && [ "$HAS_CORAL" -eq 0 ]
check "6" "Green/gold palette (no navy/coral)" $?

# ─── Q7 — Dark evidence tiers ───────────────────────────────────────────
HAS_EVT1=$(grep_count '\.ia-ev-t1' "$ARTICLE")
HAS_EVT2=$(grep_count '\.ia-ev-t2' "$ARTICLE")
[ "$HAS_EVT1" -ge 1 ] && [ "$HAS_EVT2" -ge 1 ]
check "7" "Dark evidence tiers (.ia-ev-t1, .ia-ev-t2)" $?

# ─── Q8 — #site-nav div ─────────────────────────────────────────────────
HAS_SITENAV=$(grep_count '<div id="site-nav">' "$ARTICLE")
[ "$HAS_SITENAV" -ge 1 ]
check "8" "#site-nav div present" $?

# ─── Q9 — Shared scripts ────────────────────────────────────────────────
HAS_NAVJS=$(grep_count 'nav.js' "$ARTICLE")
HAS_FOOTERJS=$(grep_count 'footer.js' "$ARTICLE")
HAS_COMPJS=$(grep_count 'components.js' "$ARTICLE")
[ "$HAS_NAVJS" -ge 1 ] && [ "$HAS_FOOTERJS" -ge 1 ] && [ "$HAS_COMPJS" -ge 1 ]
check "9" "Shared scripts (nav.js/footer.js/components.js)" $?

# ─── Q10 — @graph schema ────────────────────────────────────────────────
HAS_FAQPG=$(grep_count 'FAQPage' "$ARTICLE")
HAS_ARTICLE=$(grep_count '"Article"' "$ARTICLE")
[ "$HAS_FAQPG" -ge 1 ] && [ "$HAS_ARTICLE" -ge 1 ]
check "10" "@graph JSON-LD (Article + FAQPage)" $?

# ─── Q11 — Title ≤ 60 chars ─────────────────────────────────────────────
TITLE=$(grep -oP '(?<=<title>).*?(?=</title>)' "$ARTICLE" | head -1 || echo "")
TITLE_LEN=${#TITLE}
[ "$TITLE_LEN" -le 60 ] && [ -n "$TITLE" ]
check "11" "Title ≤ 60 chars (actual: $TITLE_LEN)" $?

# ─── Q12 — Description ≤ 155 chars ──────────────────────────────────────
DESC=$(grep -oP '(?<=<meta name="description" content=").*?(?=")' "$ARTICLE" | head -1 || echo "")
DESC_LEN=${#DESC}
[ "$DESC_LEN" -le 155 ] && [ -n "$DESC" ]
check "12" "Description ≤ 155 chars (actual: $DESC_LEN)" $?

# ─── Report ─────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}───────────────────────────────────────────────────────${NC}"
echo ""
echo "QA RESULTS: $((PASS + FAIL))/12 checks run — $PASS passed, $FAIL failed"
echo ""

if [ "$PASS" -eq 12 ]; then
    echo -e "${GREEN}GATE: GREEN — 12/12 passed${NC}"
    echo "Proceed to publication."
    exit 0
elif [ "$PASS" -ge 10 ]; then
    echo -e "${GOLD}GATE: AMBER — $PASS/12 passed${NC}"
    echo "Operator override required before publication."
    echo "Review warnings above and type 'proceed' to continue or 'abort' to stop."
    exit 1
else
    echo -e "${RED}GATE: RED — $PASS/12 passed${NC}"
    echo "Critical failures detected. Pipeline BLOCKED."
    echo "Fix the article and re-run QA before attempting publication."
    exit 2
fi
