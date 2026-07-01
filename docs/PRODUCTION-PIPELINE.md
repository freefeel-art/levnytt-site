# LevNytt Production Pipeline V1

**Date:** 2026-07-01
**Status:** ACTIVE — single source of truth for the end-to-end content production flow

---

## Overview

The LevNytt Production Pipeline transforms a keyword into a published, QA-verified informational article. It chains six stages through five registered agents, with a strict gate between each stage.

```
KEYWORD ──→ RESEARCH ──→ BRIEF ──→ WRITE ──→ QA ──→ PUBLISH ──→ REPORT
  │           │            │          │        │         │           │
  │     Research       Editorial     Writer   QA       Publication   Production
  │     Commander      Commander             Gate     Agent         Orchestrator
  │                                                                    │
  └──── Production Orchestrator (orchestrates all stages) ────────────┘
```

---

## Stage 1: Keyword → Run Config

**Responsible:** Production Orchestrator

**Input:** Raw keyword string (e.g. `"vad är lutein"`)

**Actions:**
1. Validate keyword is not empty
2. Convert to slug: lowercase, strip special chars, replace spaces/hyphens
3. Detect intent: `definition` / `how-to` / `listicle` / `comparison` / `explainer`
4. Detect YMYL: true if health/medical/nutrition/supplement/financial/legal
5. Create output directory: `content/articles/<slug>/`
6. Write `run-config.json`

**Output:** `content/articles/<slug>/run-config.json`

**Schema (run-config.json):**
```json
{
  "keyword": "<original keyword>",
  "slug": "<url-slug>",
  "target_site": "levnytt.se",
  "language": "sv",
  "intent": "explainer|definition|how-to|listicle|comparison",
  "ymyl": true|false,
  "generated": "YYYY-MM-DD"
}
```

**Error handling:**
- Empty keyword → abort with ERROR: missing keyword
- Duplicate slug (existing `content/articles/<slug>/`) → warn, ask to overwrite or pick new slug
- Invalid slug characters → abort with ERROR: invalid slug

---

## Stage 2: Research

**Responsible:** Research Commander (`.opencode/agents/research-commander.md`)

**Input:** `run-config.json` + keyword context from Editorial Commander routing

**Actions:**
1. Build research plan (infer required modules from topic)
2. Check two-level cache (topic package + per-module)
3. Execute missing modules: authority, dataforseo, reddit, content-gap, gsc, news-radar, product-db
4. Generate Research Package (`research/briefs/<slug>-approved.md`)
5. Generate Research Manifest (`research/manifests/<slug>.json`)
6. Editorial Review gate (human approval)
7. Produce Approved Research Brief

**Output files:**
| File | Required | Description |
|------|----------|-------------|
| `research/briefs/<slug>-approved.md` | Yes | Approved Research Brief (Writer input) |
| `research/manifests/<slug>.json` | Yes | Manifest with `final_brief = approved` |
| `research/authority/<slug>.json` | Optional | Authority research module output |
| `research/reddit/<slug>.json` | Optional | Reddit research (YMYL topics skip this) |

**Gate:** `research/manifests/<slug>.json` must have `final_brief = approved`

**Error handling:**
- All modules fail → abort: RESEARCH FAILED
- Partial failure → deliver partial package, Editorial Review decides
- Manifest missing or `final_brief = pending` → block writer, wait for approval
- Cache hit on all modules → return existing approved brief, skip to Stage 3

---

## Stage 3: Editorial Briefing

**Responsible:** Editorial Commander (`.opencode/agents/editorial-commander.md`)

**Input:** Approved Research Brief from Stage 2

**Actions:**
1. Verify authority clearance
2. Assign article type (defines H2 structure)
3. Select internal link targets from published sitemap pages
4. Set CTA destination (cluster hub + product page)
5. Write editorial briefing into the Approved Brief

**Output:** `research/briefs/<slug>-approved.md` (updated with editorial layer)

**Gate:** Authority check CLEARED. If BLOCKED, pipeline halts — must run authority research first.

**Error handling:**
- Authority not cleared → abort: AUTHORITY BLOCKED
- No approved brief found → abort: BRIEF MISSING
- Brief `final_brief != approved` → abort: BRIEF NOT APPROVED

---

## Stage 4: Write Article

**Responsible:** LevNytt Writer (`.opencode/agents/levnytt-writer.md`)

**Input:**
- `run-config.json` from Stage 1
- Approved Research Brief from Stage 3
- `PUBLICATION-ARTICLE-STANDARD.md` V1.0 (canonical template)
- `BRAND-DESIGN-SYSTEM.md` (green/gold palette)

**Actions:**
1. Read run-config.json for keyword, slug, intent
2. Read approved brief for verified facts, sources, writer instructions
3. Follow PAS V1.0 Section 6.0 page shell verbatim
4. Write complete HTML article with all 28 mandatory components
5. Save to `content/articles/<slug>/<slug>.html`

**Output:** `content/articles/<slug>/<slug>.html`

**Mandatory components (PAS V1.0):**
- `<div class="ia-wrap"><article>` structure (NOT `<main>`)
- Full PAS inline CSS (green/gold, dark evidence tiers)
- `<p class="ia-punchline">` — Q-A pattern, keyword in first 8 words
- `.ia-takeaways` — 4-7 bulleted claims with evidence labels
- `.ia-stat-grid` — 3-6 sourced stat cards
- `.ia-comp-table` — comparison table (if applicable)
- Question-format H2s (min 4 of 6-10)
- `.ia-cta` blocks (mid-article + bottom)
- `.ia-faq` — 6-10 question/answer pairs
- `.ia-author-box`
- `.ia-method-note`
- `@graph` JSON-LD (Article + FAQPage)
- `<title>` ≤60 chars, `<meta description>` ≤155 chars
- `#site-nav` div
- `nav.js` + `footer.js` + `components.js` scripts
- External links: `target="_blank" rel="noopener noreferrer"`

**Error handling:**
- Brief missing or not approved → abort: NO APPROVED BRIEF
- PAS V1.0 file missing → abort: TEMPLATE MISSING
- Write failure → save partial, mark as DRAFT, abort

---

## Stage 5: QA Gate

**Responsible:** Production Orchestrator (scripts/qa-article.sh or inline validation)

**Input:** `content/articles/<slug>/<slug>.html`

**Checks (V1 — 12 critical checks):**

| # | Check | Type | Pass Condition |
|---|-------|------|---------------|
| 1 | File exists | existence | `content/articles/<slug>/<slug>.html` is a regular file |
| 2 | Non-empty | existence | file size > 5000 bytes |
| 3 | Valid HTML | structure | contains `<html`, `</html>`, `<head>`, `<body>` |
| 4 | Correct wrapper | structure | `<div class="ia-wrap"><article>` present (NOT `<main>`) |
| 5 | PAS CSS present | style | contains `.ia-punchline`, `.ia-takeaways`, `.ia-cta`, `.ia-faq` |
| 6 | Green/gold palette | brand | `#1B4332` and `#E8C870` present, `#F25F4C` and `#0F1B3A` absent |
| 7 | Dark evidence tiers | style | `.ia-ev-t1`, `.ia-ev-t2` present with dark backgrounds |
| 8 | #site-nav div | structure | `<div id="site-nav"></div>` present |
| 9 | Shared scripts | structure | `nav.js`, `footer.js`, `components.js` all loaded |
| 10 | @graph schema | seo | JSON-LD script with `Article` and `FAQPage` types |
| 11 | Title length | seo | `<title>` ≤ 60 characters |
| 12 | Description length | seo | `<meta name="description">` ≤ 155 characters |

**Gate behavior:**
- 12/12 pass → GREEN, proceed to Stage 6
- 10-11/12 pass → AMBER, report warnings, operator can override
- 1-9/12 pass → RED, HALT — article must be fixed
- Any RED → pipeline stops, error reported

**Output:** QA report printed to terminal

**Error handling:**
- RED gate → write `content/articles/<slug>/qa-failures.txt` with failure details
- AMBER gate → write warnings to QA report, prompt operator override

---

## Stage 6: Publication

**Responsible:** Publication Agent (`.opencode/agents/publication-agent.md`)

**Input:**
- `content/articles/<slug>/<slug>.html` (QA passed)
- `docs/editorial-backlog/production-status.md`
- Brand assets under `assets/brand/`

**Actions:**
1. Confirm source file exists
2. Confirm root file does NOT already exist
3. Copy to root: `cp content/articles/<slug>/<slug>.html <slug>.html`
4. Verify copy (byte-identical diff check)
5. Validate brand assets exist
6. Regenerate article index: `python3 scripts/generate-article-index.py`
7. Update production status
8. Git commit + push

**Output:**
- `/<slug>.html` — published root page
- Updated `docs/editorial-backlog/production-status.md`
- Updated `artiklar.html`
- Git commit on `main` branch

**Error handling:**
- Source file missing → abort: SOURCE MISSING
- Root file already exists → skip, log ALREADY PUBLISHED
- Diff check fails → remove root copy, abort: COPY VERIFICATION FAILED
- Brand assets missing → abort: BRAND ASSET MISSING
- Index generation fails → abort: INDEX FAILED

---

## Stage 7: Production Report

**Responsible:** Production Orchestrator

**Input:** Results from all stages

**Output (terminal):**
```
╔══════════════════════════════════════════════════════╗
║         PRODUCTION COMPLETE                          ║
║         <keyword> — <date>                           ║
╚══════════════════════════════════════════════════════╝

STAGE           STATUS    DETAIL
─────           ──────    ──────
Run Config      ✅       content/articles/<slug>/run-config.json
Research        ✅       Approved brief: research/briefs/<slug>-approved.md
Write           ✅       content/articles/<slug>/<slug>.html
QA              ✅       12/12 checks passed
Publish         ✅       https://levnytt.se/<slug> (commit <hash>)

Duration: Xm Ys
```

---

## Full File Map

After a complete production run:

```
content/articles/<slug>/
├── run-config.json              ← Stage 1
└── <slug>.html                  ← Stage 4

research/
├── briefs/<slug>-approved.md    ← Stage 2
├── manifests/<slug>.json        ← Stage 2
├── authority/<slug>.json        ← Stage 2 (optional)
└── ...

/<slug>.html                     ← Stage 6 (published root)

docs/
└── editorial-backlog/
    └── production-status.md     ← Stage 6 (updated)
```

---

## Abort Conditions

The pipeline halts at these gates. No stage beyond the gate executes.

| Gate | Condition | What is blocked |
|------|-----------|----------------|
| **Keyword** | Empty or duplicate slug | Entire pipeline |
| **Research** | All modules failed | Writer, QA, Publish |
| **Brief** | `final_brief != approved` | Writer, QA, Publish |
| **Brief** | Authority not cleared | Writer, QA, Publish |
| **QA RED** | <10/12 checks pass | Publication |
| **Publish** | Source missing or copy fails | Commit, push |

---

## Invocation

### Via Production Orchestrator (recommended)

```
opencode → "run production 'vad är lutein'"
```

The Production Orchestrator agent (`production-orchestrator`) chains all stages, enforcing gates.

### Via shell script

```bash
./scripts/run-production.sh "vad är lutein"
```

Creates run-config.json, prints pipeline instructions, optionally invokes opencode.

### Manual (stage by stage)

Each stage can also be invoked independently via opencode agents:
```
opencode → "research commander: vad är lutein"
opencode → "write article for vad-ar-lutein"
opencode → "qa vad-ar-lutein"
opencode → "publish vad-ar-lutein"
```

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| V1 | 2026-07-01 | Initial pipeline specification. 7 stages, 5 agents, 12 QA checks. |
