#!/usr/bin/env bash
#
# LevNytt canonical article validator
#
# Validates a content/articles/<slug>/<slug>.html file against the shared
# editorial DOM, stylesheet and behavior contract. 12 critical checks.
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
echo -e "${GREEN}║         LevNytt Article Validator                ║${NC}"
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
HAS_BODY=$(grep_count '<body' "$ARTICLE")
[ "$HAS_HTML_OPEN" -ge 1 ] && [ "$HAS_HTML_CLOSE" -ge 1 ] && [ "$HAS_HEAD" -ge 1 ] && [ "$HAS_BODY" -ge 1 ]
check "3" "Valid HTML shell (html/head/body)" $?

# ─── Q4 — Canonical semantic article wrapper ─────────────────────────
MAIN_WRAP=$(grep_count '<main id="main-content"' "$ARTICLE")
ARTICLE_OPEN=$(grep_count '<article>' "$ARTICLE")
ARTICLE_CLOSE=$(grep_count '</article>' "$ARTICLE")
ARTICLE_BODY=$(grep_count 'class="ln-article-body ln-flow"' "$ARTICLE")
[ "$MAIN_WRAP" -eq 1 ] && [ "$ARTICLE_OPEN" -ge 1 ] && [ "$ARTICLE_CLOSE" -ge 1 ] && [ "$ARTICLE_BODY" -eq 1 ]
check "4" "Canonical main/article/content wrapper" $?

# ─── Q5 — Canonical editorial components ─────────────────────────────
HAS_PUNCH=$(grep_count 'ln-lede' "$ARTICLE")
HAS_TAKE=$(grep_count 'ln-takeaways' "$ARTICLE")
HAS_CTA=$(grep_count 'ln-cta' "$ARTICLE")
HAS_FAQ=$(grep_count 'ln-faq' "$ARTICLE")
[ "$HAS_PUNCH" -ge 1 ] && [ "$HAS_TAKE" -ge 1 ] && [ "$HAS_CTA" -ge 1 ] && [ "$HAS_FAQ" -ge 1 ]
check "5" "Canonical lede/takeaways/CTA/FAQ components" $?

# ─── Q6 — One canonical visual foundation ────────────────────────────
HAS_CANON_STYLE=$(grep_count '/assets/css/levnytt.css?v=' "$ARTICLE")
HAS_LEGACY_STYLE=$(grep_count 'pillar.css\|levnytt-foundations.css\|levnytt-components.css\|levnytt-rebuild.css\|editorial-components.css' "$ARTICLE")
[ "$HAS_CANON_STYLE" -eq 1 ] && [ "$HAS_LEGACY_STYLE" -eq 0 ]
check "6" "One canonical versioned stylesheet" $?

# ─── Q7 — Canonical evidence components ──────────────────────────────
HAS_EVIDENCE=$(grep_count 'ln-evidence-label' "$ARTICLE")
[ "$HAS_EVIDENCE" -ge 1 ]
check "7" "Canonical evidence labels" $?

# ─── Q8 — Canonical accessible shell ─────────────────────────────────
HAS_HEADER=$(grep_count 'class="ln-site-header"' "$ARTICLE")
HAS_MENU=$(grep_count 'aria-controls="ln-primary-nav"' "$ARTICLE")
[ "$HAS_HEADER" -eq 1 ] && [ "$HAS_MENU" -eq 1 ]
check "8" "Canonical header and accessible menu" $?

# ─── Q9 — One shared behavior runtime ────────────────────────────────
HAS_RUNTIME=$(grep_count '/assets/js/levnytt-rebuild.js?v=' "$ARTICLE")
HAS_LEGACY_RUNTIME=$(grep_count '/nav.js\|/footer.js\|/components.js' "$ARTICLE")
[ "$HAS_RUNTIME" -eq 1 ] && [ "$HAS_LEGACY_RUNTIME" -eq 0 ]
check "9" "One canonical shared runtime" $?

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
