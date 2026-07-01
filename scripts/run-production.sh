#!/usr/bin/env bash
#
# LevNytt Production Runner V2
#
# Single-command launcher for the full content production pipeline.
# Generates a Production Brief (YAML) from a keyword, auto-filling all
# fields from keyword analysis.
#
# Usage:
#   ./scripts/run-production.sh "vad är lutein"
#   ./scripts/run-production.sh --brief content/briefs/vad-ar-lutein.brief.yaml
#
# With --brief flag, skips generation and uses an existing brief directly.
#

set -euo pipefail

# ─── Colors ─────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
GOLD='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ─── Banner ─────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       LevNytt Production Runner V2                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# ─── Paths ──────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

BRIEFS_DIR="content/briefs"

# ─── Parse flags ────────────────────────────────────────────────────────
EXISTING_BRIEF=""
KEYWORD=""

if [ "${1:-}" = "--brief" ]; then
    EXISTING_BRIEF="${2:-}"
    if [ -z "$EXISTING_BRIEF" ]; then
        echo -e "${RED}ERROR: --brief requires a file path.${NC}"
        exit 1
    fi
    if [ ! -f "$EXISTING_BRIEF" ]; then
        echo -e "${RED}ERROR: Brief not found: $EXISTING_BRIEF${NC}"
        exit 1
    fi
    echo -e "${BLUE}Using existing brief:${NC} $EXISTING_BRIEF"
    KEYWORD=$(grep 'primary_keyword:' "$EXISTING_BRIEF" | head -1 | sed 's/.*primary_keyword:\s*//' | xargs)
    if [ -z "$KEYWORD" ]; then
        echo -e "${RED}ERROR: Could not extract keyword from brief.${NC}"
        exit 1
    fi
else
    KEYWORD="${1:-}"
fi

# ─── Validate keyword ───────────────────────────────────────────────────
if [ -z "$KEYWORD" ]; then
    echo -e "${RED}ERROR: Missing keyword.${NC}"
    echo ""
    echo "Usage:"
    echo "  ./scripts/run-production.sh \"vad är lutein\""
    echo "  ./scripts/run-production.sh --brief content/briefs/vad-ar-lutein.brief.yaml"
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
echo -e "${BLUE}Slug:${NC}     $SLUG"

# ─── Detect fields from keyword ─────────────────────────────────────────
detect_intent() {
    local kw_lower
    kw_lower=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    case "$kw_lower" in
        vad\ är*|vad\ ar*|definition*|betydelse*) echo "definition" ;;
        hur\ fungerar*|hur\ gör*|steg\ för*)       echo "how_to" ;;
        bästa*|topp*|lista*|rankning*)             echo "listicle" ;;
        *\ vs\ *|*\ eller\ *|*jämför*|*skillnad*) echo "comparison" ;;
        *)                                          echo "explainer" ;;
    esac
}

detect_primary_entity() {
    local kw_lower
    kw_lower=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    # Strip question words and common prefixes
    kw_lower=$(echo "$kw_lower" | sed 's/^vad är //;s/^vad ar //;s/^hur fungerar //;s/^hur //')
    # Take first meaningful word as primary entity
    echo "$kw_lower" | awk '{print $1}'
}

detect_topic() {
    local kw_lower
    kw_lower=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    case "$kw_lower" in
        *omega-3*|*fiskolja*|*fettsyra*)    echo "fatty_acids" ;;
        *d-vitamin*|*vitamin\ d*)           echo "vitamins" ;;
        *magnesium*)                         echo "minerals" ;;
        *zink*)                              echo "minerals" ;;
        *järn*|*jarn*)                       echo "minerals" ;;
        *selen*)                             echo "minerals" ;;
        *antioxidant*|*karotenoid*)          echo "antioxidants" ;;
        *probiotika*|*tarm*|*mage*)          echo "gut_health" ;;
        *fiber*|*kostfiber*)                 echo "gut_health" ;;
        *protein*)                           echo "protein" ;;
        *sömn*|*melatonin*)                  echo "sleep" ;;
        *stress*)                            echo "stress" ;;
        *kollagen*|*hud*)                    echo "skincare" ;;
        *träning*|*prestation*)              echo "sports" ;;
        *kosttillskott*|*tillskott*)         echo "supplements" ;;
        *)                                   echo "nutrition" ;;
    esac
}

detect_cluster() {
    local kw_lower
    kw_lower=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    case "$kw_lower" in
        *omega-3*|*fiskolja*|*epa*|*dha*)   echo "omega_3" ;;
        *d-vitamin*|*vitamin\ d*)           echo "vitamin_d" ;;
        *magnesium*)                         echo "magnesium" ;;
        *zink*)                              echo "zinc" ;;
        *järn*|*jarn*)                       echo "iron" ;;
        *selen*)                             echo "selenium" ;;
        *antioxidant*|*karotenoid*|*lutein*) echo "carotenoids" ;;
        *probiotika*|*tarmflora*)            echo "probiotics" ;;
        *fiber*|*kostfiber*)                 echo "fiber" ;;
        *kollagen*)                          echo "collagen" ;;
        *kreatin*)                           echo "creatine" ;;
        *melatonin*)                         echo "melatonin" ;;
        *protein*)                           echo "protein" ;;
        *multivitamin*)                      echo "multivitamins" ;;
        *)                                   echo "general" ;;
    esac
}

detect_ymyl() {
    local kw_lower
    kw_lower=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    if echo "$kw_lower" | grep -qiE 'hälsa|kosttillskott|vitamin|mineral|medicin|sjukdom|symptom|behandling|dosering|brist|farligt|gravid|barn|äldre|diabetes|högt blodtryck|kolesterol|inflammation|immunförsvar|sömn|stress|vikt|tarm|mage|probiotika|omega-3|magnesium|kalcium|järn|zink|selen|d-vitamin|folsyra|b12|antioxidant|näring|nutrition|kost|allergi|ögon|hud|led|hår|träning|prestation|läkemedel|protein|aminosyra|kolhydrat|fett|kalori|ämnesomsättning|hormon|tillskott|dos|biverkning|interaktion|upptag|biotillgänglighet|kostråd|livsmedelsverket'; then
        echo "true"
    else
        echo "false"
    fi
}

detect_audience() {
    local kw_lower
    kw_lower=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    case "$kw_lower" in
        *barn*|*gravid*|*ammande*) echo "parents" ;;
        *träning*|*prestation*|*muskel*) echo "athletes" ;;
        *kvinnor*|*klimakteriet*) echo "women" ;;
        *män*|*testosteron*)      echo "men" ;;
        *äldre*|*65*)             echo "seniors" ;;
        *)                        echo "consumers" ;;
    esac
}

INTENT=$(detect_intent "$KEYWORD")
ENTITY=$(detect_primary_entity "$KEYWORD")
TOPIC=$(detect_topic "$KEYWORD")
CLUSTER=$(detect_cluster "$KEYWORD")
YMYL=$(detect_ymyl "$KEYWORD")
AUDIENCE=$(detect_audience "$KEYWORD")
AUTHORITY_MODE="health"
TODAY=$(date +%Y-%m-%d)

# health → health, everything else → general
if [ "$YMYL" = "false" ]; then
    AUTHORITY_MODE="general"
fi

echo -e "${BLUE}Entity:${NC}    $ENTITY"
echo -e "${BLUE}Intent:${NC}    $INTENT"
echo -e "${BLUE}Topic:${NC}     $TOPIC"
echo -e "${BLUE}Cluster:${NC}   $CLUSTER"
echo -e "${BLUE}Audience:${NC}  $AUDIENCE"
echo -e "${BLUE}Mode:${NC}      $AUTHORITY_MODE"

# ─── Check existing brief ────────────────────────────────────────────────
if [ -n "$EXISTING_BRIEF" ]; then
    echo ""
    echo -e "${GREEN}Using existing brief. Pipeline ready.${NC}"
    echo ""
    echo -e "${GOLD}Next step:${NC}"
    echo -e "  ${GREEN}Run production: '$SLUG'${NC}"
    echo ""
    exit 0
fi

if [ -f "$BRIEFS_DIR/$SLUG.brief.yaml" ]; then
    echo ""
    echo -e "${GOLD}Brief already exists: $BRIEFS_DIR/$SLUG.brief.yaml${NC}"
else
    # ─── Generate title ─────────────────────────────────────────────────
    generate_title() {
        local capitalized
        capitalized=$(echo "$KEYWORD" | sed 's/\b\([a-zåäö]\)/\u\1/g')
        case "$INTENT" in
            definition) echo "$capitalized — en komplett evidensbaserad guide" ;;
            how_to)     echo "Hur du använder $ENTITY — steg för steg-guide" ;;
            comparison) echo "$capitalized — vilket alternativ passar dig?" ;;
            explainer)  echo "$capitalized — allt du behöver veta" ;;
            listicle)   echo "$capitalized — de bästa alternativen" ;;
            *)          echo "$capitalized — komplett guide" ;;
        esac
    }
    TITLE=$(generate_title)

    # ─── Generate required_outputs ──────────────────────────────────────
    generate_outputs() {
        local outputs="definition evidence food_sources safety faq internal_links cta stat_cards"
        case "$INTENT" in
            definition) outputs="$outputs mechanism myth_busting" ;;
            how_to)     outputs="$outputs practical_guide" ;;
            comparison) outputs="$outputs comparison" ;;
            explainer)  outputs="$outputs mechanism practical_guide" ;;
        esac
        if [ "$YMYL" = "true" ]; then
            outputs="$outputs evidence safety"
        fi
        echo "$outputs"
    }
    OUTPUTS=$(generate_outputs | tr ' ' '\n' | sort -u | tr '\n' ' ' | xargs)

    # ─── Write Production Brief ─────────────────────────────────────────
    mkdir -p "$BRIEFS_DIR"

    cat > "$BRIEFS_DIR/$SLUG.brief.yaml" << YAMLEOF
# LevNytt Production Brief — auto-generated $(date +%Y-%m-%d)
# Review and edit before production run.

title: $TITLE

entity:
  - $ENTITY

primary_keyword:
  $KEYWORD

content_type:
  informational_article

intent:
  $INTENT

topic:
  $TOPIC

cluster:
  $CLUSTER

audience:
  $AUDIENCE

language:
  sv

authority_mode:
  $AUTHORITY_MODE

goal: >
  ${TITLE}. Explain what ${ENTITY} is, its role in the body, where it
  is found in food, what current research says, and when
  supplementation may be relevant. Help the reader make informed
  decisions about ${ENTITY} intake.

publication:
  levnytt.se

related_entities: []

required_outputs:
$(echo "$OUTPUTS" | tr ' ' '\n' | sed 's/^/  - /')
YAMLEOF

    echo -e "${GREEN}Written:${NC}  $BRIEFS_DIR/$SLUG.brief.yaml"
fi

# ─── Also create legacy run-config for Writer compatibility ──────────────
mkdir -p "content/articles/$SLUG"
cat > "content/articles/$SLUG/run-config.json" << EOF
{
  "keyword": "$KEYWORD",
  "slug": "$SLUG",
  "target_site": "levnytt.se",
  "language": "sv",
  "intent": "$INTENT",
  "ymyl": $YMYL,
  "generated": "$TODAY",
  "brief_source": "$BRIEFS_DIR/$SLUG.brief.yaml"
}
EOF
echo -e "${GREEN}Written:${NC}  content/articles/$SLUG/run-config.json"

# ─── Summary ─────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}───────────────────────────────────────────────────────${NC}"
echo -e "${GREEN}Production Brief ready.${NC}"
echo ""
echo "Files created:"
echo "  $BRIEFS_DIR/$SLUG.brief.yaml       (Production Brief)"
echo "  content/articles/$SLUG/run-config.json"
echo ""
echo -e "${GOLD}Next step — start the pipeline:${NC}"
echo ""
echo -e "  ${GREEN}Run production: '$SLUG'${NC}"
echo ""
echo "Or review and edit the brief first:"
echo "  $BRIEFS_DIR/$SLUG.brief.yaml"
echo ""
echo -e "${GREEN}───────────────────────────────────────────────────────${NC}"
echo ""