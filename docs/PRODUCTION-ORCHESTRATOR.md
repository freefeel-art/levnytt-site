# Production Orchestrator V2

**Date:** 2026-07-01
**Status:** ACTIVE
**Supersedes:** PRODUCTION-ORCHESTRATOR.md V1

---

## Purpose

The Production Orchestrator is the single entry point that transforms a Production Brief into a published article. It chains agents through the pipeline, enforcing gates between each stage.

**Key change from V1:** The pipeline input is now a **Production Brief** (YAML), not a raw keyword. The keyword is one field inside the brief.

---

## How to Invoke

### Primary method — opencode agent

```
Kör produktionen för vad-ar-lutein
```

The Production Orchestrator reads `content/briefs/vad-ar-lutein.brief.yaml`, validates it, and runs the pipeline.

**Trigger phrases:** `run production`, `kör produktion`, `production run`, `producera artikel`, `full pipeline`

### Shell script method

```bash
# Generate a brief from a keyword (basic auto-fill)
./scripts/run-production.sh "vad är lutein"

# OR write the brief manually in YAML, then invoke the orchestrator
```

---

## Pipeline Flow (V2)

```
1. VALIDATE    → Read & validate Production Brief
2. RESEARCH    → Research Commander: brief → research package
3. EDITORIAL   → Editorial Commander: package → editorial decisions
4. WRITE       → Writer: brief + package + editorial → article
5. QA          → 12-check PAS V1.0 validator
6. PUBLISH     → Publication Agent: copy to root, commit, push
7. REPORT      → Production Report (terminal)
```

---

## Stage-by-Stage Execution

### STAGE 1 — Validate Production Brief

**What you do:**
1. Read `content/briefs/<slug>.brief.yaml`
2. If it doesn't exist, offer to create one from a keyword
3. Validate all 14 required fields are present
4. Validate enum values are valid
5. Check entity-keyword coherence

**Gate:** Brief is valid and complete.
**If fail:** Report missing/invalid fields. Offer to fix or abort.

### STAGE 2 — Research Commander

**Input:** `content/briefs/<slug>.brief.yaml`

Invoke Research Commander:
```
Task subagent: research-commander
Prompt: "Build Research Package for Production Brief at
         content/briefs/<slug>.brief.yaml.
         Output to research/packages/<slug>/.
         Generate manifest, summary, sources, studies, entities,
         internal-links, faq, competitor-analysis, evidence,
         keywords, product-notes, and audit log."
```

**Check:**
- `research/packages/<slug>/manifest.json` exists, lifecycle = `completed`
- For health/science: `sources.json` has ≥3 Tier 1-2 sources

**Gate:** Complete Research Package with valid manifest.
**If fail:** Report partial status. Operator may waive or retry.

### STAGE 3 — Editorial Commander

**Input:** `research/packages/<slug>/`

Invoke Editorial Commander:
```
Task subagent: editorial-commander
Prompt: "Review Research Package at research/packages/<slug>/.
         Confirm article angle, select verified claims, finalize
         evidence tiers, set internal link priorities, define CTA
         strategy, and confirm H2 outline from required_outputs.
         Do NOT perform new research — use only the package data."
```

**Check:**
- Editorial decisions are recorded
- No: authority BLOCKED (should have been caught by research)

**Gate:** Editorial decisions confirmed.
**If fail:** Report what's missing. May request research refresh.

### STAGE 4 — Writer

**Input:**
- `content/briefs/<slug>.brief.yaml`
- `research/packages/<slug>/`

Invoke Writer:
```
Task subagent: levnytt-writer
Prompt: "Write LevNytt informational article.
         Use Production Brief: content/briefs/<slug>.brief.yaml.
         Use Research Package: research/packages/<slug>/.
         Follow PUBLICATION-ARTICLE-STANDARD.md V1.0.
         Use BRAND-DESIGN-SYSTEM.md (green/gold).
         Output to: content/articles/<slug>/<slug>.html"
```

**Check:**
- File exists and > 5000 bytes
- Contains `<div class="ia-wrap">` + `<article>` structure
- Contains all `required_outputs` from the brief

**Gate:** Valid PAS article at correct path.
**If fail:** Report failure. Save partial output.

### STAGE 5 — QA Gate

Run `bash scripts/qa-article.sh <slug>`.

**12 checks:** File exists, non-empty, HTML shell, PAS wrapper, PAS CSS, brand palette, evidence tiers, site-nav, scripts, schema, title ≤60, description ≤155.

**Gate:** GREEN → proceed. AMBER → operator override. RED → blocked.

### STAGE 6 — Publication Agent

QA must be GREEN (or AMBER overridden).

```
Task subagent: publication-agent
Prompt: "Publish article: content/articles/<slug>/<slug>.html.
         QA passed. Copy to root, verify, regenerate index,
         commit, push."
```

**Gate:** Published at root, committed, pushed.

### STAGE 7 — Production Report + Cost Telemetry

Print terminal summary. Then capture cost telemetry to `production/logs/`.

See `docs/COST-TELEMETRY.md` for the full telemetry specification.

After every run:
1. Write `production/logs/<run_id>.json` — full per-agent breakdown
2. Append to `production/logs/history.json` — aggregated summary

Cost aggregation: `./scripts/cost-report.sh [--today|--month YYYY-MM|--per-article|--article <slug>]`

---

## File Passing Between Stages

| From | To | Passed Via |
|---|---|---|
| Orchestrator | Research Commander | `content/briefs/<slug>.brief.yaml` path |
| Research Commander | Editorial Commander | `research/packages/<slug>/` directory |
| Editorial Commander | Writer | Package + editorial decisions (same dir) |
| Orchestrator | Writer | Brief + package paths |
| Writer | QA | `content/articles/<slug>/<slug>.html` |
| QA | Publication Agent | Same HTML (QA passed flag) |
| Publication Agent | Report | Commit hash |

---

## Resume / Partial Runs

The orchestrator detects completed stages by checking files:

| Stage | Detection |
|---|---|
| 1. Brief | `content/briefs/<slug>.brief.yaml` exists |
| 2. Research | `research/packages/<slug>/manifest.json` with lifecycle `completed` |
| 4. Write | `content/articles/<slug>/<slug>.html` exists |
| 5. QA | Last QA run passed (flag in context) |
| 6. Publish | `/<slug>.html` at root |

---

## QA Gate Details

Same 12 checks as V1 (see `scripts/qa-article.sh`). V2 adds one optional check:

| # | Check | How |
|---|---|---|
| 13 | Required outputs present | Read brief, check each `required_output` has a corresponding section |

---

## Version History

| Version | Date | Change |
|---|---|---|
| V1 | 2026-07-01 | Initial orchestrator: keyword-based, 12 QA checks |
| V2 | 2026-07-01 | Production Brief architecture: brief→package→editorial, stage 0 validation |
| V2.1 | 2026-07-01 | Cost telemetry: per-agent token/cost tracking, production/logs/, cost-report.sh |