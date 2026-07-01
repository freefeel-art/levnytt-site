#!/usr/bin/env bash
#
# LevNytt Production Runner V1
#
# Single-command launcher for the full content production pipeline.
# Creates run-config.json and sets up the environment, then invokes the
# Production Orchestrator agent via opencode.
#
# Usage:
#   ./scripts/run-production.sh "vad är lutein"
#   ./scripts/run-production.sh "omega-3 dosering per dag"
#
# What this script does:
#   1. Validates the keyword
#   2. Converts to a URL-safe slug
#   3. Creates content/articles/<slug>/ directory
#   4. Writes run-config.json
#   5. Prints a launch command for opencode
#
# The actual agent chaining is done by the Production Orchestrator
# (.opencode/agents/production-orchestrator.md) via opencode's Task tool.
#

set -euo pipefail

# ─── Colors ─────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
GOLD='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─── Banner ─────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       LevNytt Production Runner V1                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# ─── Validate input ─────────────────────────────────────────────────────
KEYWORD="${1:-}"

if [ -z "$KEYWORD" ]; then
    echo -e "${RED}ERROR: Missing keyword.${NC}"
    echo ""
    echo "Usage:"
    echo "  ./scripts/run-production.sh \"vad är lutein\""
    echo ""
    exit 1
fi

echo -e "${BLUE}Keyword:${NC}  $KEYWORD"

# ─── Slugify ─────────────────────────────────────────────────────────────
slugify() {
    echo "$1" | tr '[:upper:]' '[:lower:]' \
        | sed 's/[^a-zåäö0-9 -]//g' \
        | sed 's/ /-/g' \
        | sed 's/-\+/-/g' \
        | sed 's/^-//;s/-$//'
}

SLUG=$(slugify "$KEYWORD")

if [ -z "$SLUG" ]; then
    echo -e "${RED}ERROR: Could not generate slug from keyword.${NC}"
    exit 1
fi

echo -e "${BLUE}Slug:${NC}     $SLUG"

# ─── Detect intent ───────────────────────────────────────────────────────
detect_intent() {
    local kw_lower
    kw_lower=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    if echo "$kw_lower" | grep -qE '^(vad är|vad ar|definition|betydelse)'; then
        echo "definition"
    elif echo "$kw_lower" | grep -qE '^(hur|hur fungerar|hur gör|steg för steg)'; then
        echo "how-to"
    elif echo "$kw_lower" | grep -qE '^(bästa|topp|lista|rankning)'; then
        echo "listicle"
    elif echo "$kw_lower" | grep -qE '( vs | eller | jämför|skillnad|alternativ)'; then
        echo "comparison"
    else
        echo "explainer"
    fi
}

INTENT=$(detect_intent "$KEYWORD")
echo -e "${BLUE}Intent:${NC}    $INTENT"

# ─── Detect YMYL ─────────────────────────────────────────────────────────
YMYL_KEYWORDS="hälsa|kosttillskott|vitamin|mineral|medicin|sjukdom|symptom|
behandling|dosering|brist|farligt|gravid|barn|äldre|diabetes|högt blodtryck|
kolesterol|inflammation|immunförsvar|sömn|stress|vikt|tarm|mage|probiotika|
omega-3|magnesium|kalcium|järn|zink|selen|d-vitamin|folsyra|b12|antioxidant|
näring|nutrition|kost|allergi|ögon|hud|led|hår|träning|prestation|läkemedel|
protein|aminosyra|kolhydrat|fett|kalori|ämnesomsättning|hormon|tillskott|dos|
biverkning|interaktion|upptag|biotillgänglighet|kostråd|livsmedelsverket"

if echo "$KEYWORD" | grep -qiE "$YMYL_KEYWORDS"; then
    YMYL=true
else
    YMYL=false
fi
echo -e "${BLUE}YMYL:${NC}      $YMYL"

# ─── Repository root detection ───────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$REPO_ROOT"

# ─── Check for duplicate slug ────────────────────────────────────────────
if [ -d "content/articles/$SLUG" ]; then
    echo ""
    echo -e "${GOLD}WARNING: content/articles/$SLUG/ already exists.${NC}"
    echo -e "${GOLD}This slug has been used before.${NC}"
    echo ""
    echo -e -n "Overwrite existing config? (y/n) "
    read -r REPLY
    if [ "$REPLY" != "y" ] && [ "$REPLY" != "Y" ]; then
        echo "Aborted."
        exit 0
    fi
fi

if [ -f "$SLUG.html" ]; then
    echo ""
    echo -e "${RED}WARNING: /$SLUG.html already exists at root (PUBLISHED).${NC}"
    echo -e "${GOLD}This article is already published.${NC}"
    echo ""
    echo -e -n "Continue anyway? (y/n) "
    read -r REPLY
    if [ "$REPLY" != "y" ] && [ "$REPLY" != "Y" ]; then
        echo "Aborted."
        exit 0
    fi
fi

# ─── Create directory ────────────────────────────────────────────────────
mkdir -p "content/articles/$SLUG"
echo -e "${GREEN}Created:${NC}  content/articles/$SLUG/"

# ─── Write run-config.json ───────────────────────────────────────────────
TODAY=$(date +%Y-%m-%d)

cat > "content/articles/$SLUG/run-config.json" << EOF
{
  "keyword": "$KEYWORD",
  "slug": "$SLUG",
  "target_site": "levnytt.se",
  "language": "sv",
  "intent": "$INTENT",
  "ymyl": $YMYL,
  "generated": "$TODAY"
}
EOF

echo -e "${GREEN}Written:${NC}  content/articles/$SLUG/run-config.json"

# ─── Summary ─────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}───────────────────────────────────────────────────────${NC}"
echo -e "${GREEN}Run config ready.${NC}"
echo ""
echo "Files created:"
echo "  content/articles/$SLUG/run-config.json"
echo "  content/articles/$SLUG/           (directory)"
echo ""
echo -e "${GOLD}Next step — start the pipeline:${NC}"
echo ""
echo -e "  ${GREEN}Run production: '$SLUG'${NC}"
echo ""
echo "Or manually invoke individual stages:"
echo "  1. Research:        opencode → 'research $KEYWORD for $SLUG'"
echo "  2. Write:           opencode → 'write article for $SLUG'"
echo "  3. QA:              ./scripts/qa-article.sh $SLUG"
echo "  4. Publish:         opencode → 'publish $SLUG'"
echo ""
echo -e "${GREEN}───────────────────────────────────────────────────────${NC}"
echo ""
