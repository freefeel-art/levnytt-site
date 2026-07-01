# LevNytt Production Pipeline V2

**Date:** 2026-07-01
**Status:** ACTIVE — single source of truth for the end-to-end content production flow
**Supersedes:** PRODUCTION-PIPELINE.md V1

---

## Architecture Overview

The pipeline transforms a **Production Brief** into a published, QA-verified article. The keyword is one field in the brief — never the pipeline's primary input.

```
Production Brief        content/briefs/<slug>.brief.yaml
    ↓
Research Commander      Reads brief → builds research mission
    ↓
Research Package        research/packages/<slug>/ (12 structured files)
    ↓
Editorial Commander     Reads package → produces editorial brief
    ↓
Editorial Brief         Writer-ready instructions
    ↓
Writer                  LevNytt Writer V1.0
    ↓
QA Gate                 12-check PAS V1.0 validator
    ↓
Publication Agent       Deploy to root, commit, push
    ↓
Production Report       Terminal summary
```

---

## Stage 1: Production Brief

**Input:** Editorial decision (topic selection, content gap analysis)

**Output:** `content/briefs/<slug>.brief.yaml`

A human (or Editorial Commander) creates a Production Brief. This is the single source of truth for the entire production run. See `docs/PRODUCTION-BRIEF-SPEC.md` for the full field specification.

**Key principle:** The brief describes an **editorial assignment**, not an SEO keyword.

**Example fields:**
```yaml
title: Vad är lutein? — karotenoiden för ögon, hud och hjärna
entity: [lutein]
primary_keyword: vad är lutein
content_type: informational_article
intent: definition
topic: antioxidants
cluster: carotenoids
audience: consumers
authority_mode: health
goal: Explain what lutein is...
required_outputs: [definition, evidence, food_sources, ...]
```

**Gate:** All 14 required fields present and valid. Brief file exists at correct path.
**Error:** Missing or invalid brief → pipeline cannot start.

---

## Stage 2: Research Commander

**Input:** `content/briefs/<slug>.brief.yaml`

**Output:** `research/packages/<slug>/` (12 structured files)

The Research Commander reads the Production Brief and builds a **research mission** from it. It uses the entity list for PubMed/authority queries, the cluster for content-gap analysis, the related_entities for entity co-occurrence, and the goal for scoping.

**Module selection is driven by the brief:**
- `authority_mode: health` → all modules including authority research
- `entity` → entity disambiguation + synonym expansion
- `cluster` → content-gap analysis against existing cluster content
- `related_entities` → co-occurrence for LSI clustering
- `goal` → scopes research depth (broad explainer vs narrow evidence dive)

**Package contents:**
| File | Required | Content |
|------|----------|---------|
| `manifest.json` | Yes | Provenance, module status, lifecycle |
| `research-summary.md` | Yes | Human-readable synthesis |
| `sources.json` | Yes | All sources with evidence tiers (T1-T4) |
| `studies.json` | Health mode | Extracted study data |
| `entities.json` | Yes | Named entities + relationships |
| `internal-links.json` | Yes | Link targets with placement context |
| `faq.json` | Yes | 6-10 FAQ candidates |
| `competitor-analysis.md` | Yes | Top 3-5 SERP competitors |
| `evidence.md` | Health mode | Claim-to-evidence mapping |
| `product-notes.json` | Optional | Relevant NeoLife products |
| `keywords.json` | Optional | LSI + co-occurring terms |
| `audit.json` | Yes | Execution log |

**Gate:** `manifest.json lifecycle = completed`. For health/science: ≥3 Tier 1-2 sources in `sources.json`.
**Error:** Package incomplete → Editorial Commander decides whether to proceed with partial data.

---

## Stage 3: Editorial Commander

**Input:** `research/packages/<slug>/` (full Research Package)

**Output:** Editorial Brief (integrated into the package as editorial decisions)

The Editorial Commander reads the Research Package and **does no research of its own**. It makes editorial decisions based on the research data.

**Decisions made:**
1. **Angle confirmation:** Does the recommended angle match the original goal?
2. **Claim selection:** Which verified facts go into the article?
3. **Evidence tier assignment:** Confirm or adjust tier labels
4. **Source prioritization:** Which sources are primary vs supporting?
5. **Internal link priority:** Finalize link targets and placement
6. **CTA strategy:** Which product link? Where?
7. **Structure confirmation:** H2 outline based on `required_outputs`

**Gate:** Package is complete and all required decisions are made.
**Error:** If the package is insufficient (e.g., no Tier 1 sources for a health claim), the Editorial Commander requests a research refresh or waives the requirement.

---

## Stage 4: Writer

**Input:**
- Production Brief (`content/briefs/<slug>.brief.yaml`)
- Research Package (`research/packages/<slug>/`) + editorial decisions
- `PUBLICATION-ARTICLE-STANDARD.md` V1.0

**Output:** `content/articles/<slug>/<slug>.html`

The Writer produces a PAS V1.0-compliant HTML article. It does not research. It does not decide structure. It follows the editorial brief, the required_outputs from the Production Brief, and the evidence map from the Research Package.

**Writer's constraints:**
- Must use PAS V1.0 Section 6.0 page shell verbatim
- Must use green/gold brand palette (`#1B4332` / `#E8C870` / `#F9F6EF`)
- Must use dark evidence tier labels
- Must use `<div class="ia-wrap"><article>` structure
- Must include all `required_outputs` specified in the brief

**Gate:** Valid HTML file written to `content/articles/<slug>/`.
**Error:** Writer fails → save partial output, report failure.

---

## Stage 5: QA Gate

**Input:** `content/articles/<slug>/<slug>.html`

**Output:** QA report (GREEN / AMBER / RED)

12 automated checks via `scripts/qa-article.sh`. See `docs/PRODUCTION-ORCHESTRATOR.md` for full check list.

**Gate behavior:**
- 12/12 → GREEN — proceed
- 10-11/12 → AMBER — operator override required
- <10/12 → RED — pipeline blocked

---

## Stage 6: Publication Agent

**Input:** `content/articles/<slug>/<slug>.html` (QA passed)

**Output:** Published root page, git commit

Copy to root, verify, regenerate article index, commit, push.

---

## Stage 7: Production Report + Cost Telemetry

Terminal summary of the entire run — all stages, statuses, commit hash, duration, and per-agent cost breakdown.

**Cost telemetry** is captured automatically:
- Per-agent token/cost/duration estimates → `production/logs/<run_id>.json`
- Aggregated run summary → appended to `production/logs/history.json`
- Cost report script: `./scripts/cost-report.sh`

See `docs/COST-TELEMETRY.md` for the full telemetry specification.

---

## Complete File Map

After a successful production run:

```
content/briefs/<slug>.brief.yaml            ← Stage 1: Production Brief
research/packages/<slug>/                   ← Stage 2: Research Package
├── manifest.json
├── research-summary.md
├── sources.json
├── studies.json
├── entities.json
├── internal-links.json
├── faq.json
├── competitor-analysis.md
├── evidence.md
├── keywords.json
├── product-notes.json
└── audit.json
content/articles/<slug>/<slug>.html         ← Stage 4: Article
/<slug>.html                                 ← Stage 6: Published
production/logs/<run_id>.json               ← Stage 7: Cost telemetry
production/logs/history.json                ← Stage 7: Aggregated (appended)
```

---

## Key Architectural Decisions

1. **Keyword is a field, not the input.** The Production Brief is the input. Keyword is one of 14 fields.
2. **Research Commander takes a brief, not a keyword.** The brief's entity, cluster, and goal drive the research mission.
3. **Editorial Commander does no research.** It reads the Research Package and makes decisions.
4. **Writer does no research.** It follows the editorial brief.
5. **Every stage has a defined input and output contract.** No stage invents its own input.

---

## Version History

| Version | Date | Change |
|---|---|---|
| V1 | 2026-07-01 | Initial pipeline: keyword-based, 7 stages |
| V2 | 2026-07-01 | Production Brief architecture: brief→package→editorial chain, Research Package spec |
| V2.1 | 2026-07-01 | Cost telemetry: per-run JSON logs, history.json aggregation, cost-report.sh |