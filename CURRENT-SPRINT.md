# CURRENT-SPRINT.md
# LevNytt.se — Project Phase

Last updated: 2026-07-02

---

## Phase: Content Factory Transition

The Gen 3 migration is **complete**.
The Brand System (Sprint 8), Brand Rollout (Sprint 9), Repository Cleanup (Sprint 9b), and Post-Cleanup Baseline (Sprint 10) are **complete**.
The Production Orchestrator + Production Brief Architecture + Cost Telemetry (Sprint 11) is **complete**.
The Research Commander V2 + GSC Content Audit (Sprint 12) is **complete**.

---

## Sprint History

### Sprint 9 — Brand Rollout + Repository Cleanup

| | |
|---|---|
| **Status** | ✅ Completed |
| **Completed** | 2026-07-01 |
| **Commit** | `c61eebc` |

### Sprint 10 — Post-Cleanup Baseline

| | |
|---|---|
| **Status** | ✅ Completed |
| **Completed** | 2026-07-01 |
| **Commits** | `69c5359`, `a0ab42a` |

### Sprint 11 — Production Orchestrator + Brief Architecture + Telemetry

| | |
|---|---|
| **Status** | ✅ Completed |
| **Completed** | 2026-07-01 |
| **Commits** | `4fd38ac`, `2bd61c6`, `ba7079f` |

**Delivered:**
- `docs/PRODUCTION-PIPELINE.md` — V2: Brief→Package→Editorial chain (7 stages)
- `docs/PRODUCTION-ORCHESTRATOR.md` — V2: brief-first invocation, QA gating, abort/resume
- `docs/PRODUCTION-BRIEF-SPEC.md` — 14-field canonical spec (YAML)
- `docs/RESEARCH-PACKAGE-SPEC.md` — 12-file structured research output
- `docs/COST-TELEMETRY.md` — model pricing, log format, aggregation queries
- `scripts/run-production.sh` — V2: generates `.brief.yaml` from keyword, detects intent/topic/audience
- `scripts/qa-article.sh` — 12-check PAS V1.0 validator (GREEN/AMBER/RED)
- `scripts/cost-report.sh` — CLI cost aggregator (--today, --month, --per-article)
- `content/briefs/vad-ar-lutein.brief.yaml` — example brief (verified against 12/12 QA article)
- `production/logs/` — telemetry directory + sample log
- `.opencode/agents/production-orchestrator.md` — V2: brief-first agent chainer with telemetry

**Key architectural decision:** Keyword is now one field in the Production Brief, not the pipeline input. Brief → Research Commander → Research Package → Editorial Commander → Editorial Brief → Writer.

### Sprint 12 — Research Commander V2 + GSC Content Audit

| | |
|---|---|
| **Status** | ✅ Completed |
| **Completed** | 2026-07-02 |
| **Commit** | `436f7ed` |

**Delivered:**
- `.opencode/agents/research-commander.md` (V2) — brief-first input with keyword backward compatibility, Phase 0 input resolution, brief-field-driven research planning
- `docs/PRODUCTION-PIPELINE.md` (V2.2) — backward compatibility note, version history
- `docs/PRODUCTION-ORCHESTRATOR.md` (V2.2) — brief-first Stage 2 contract, resume detection table
- `docs/PRODUCTION-BRIEF-SPEC.md` (V1.1) — entity field backward compat note
- `docs/RESEARCH-PACKAGE-SPEC.md` (V1.1) — backward compatibility input mode
- `docs/specifications/AGENT-REGISTRY.md` (V1.2) — Research Commander registered as agent #7
- `docs/gsc/GSC-CONTENT-AUDIT.md` — comprehensive audit of 11 GSC "Crawled – not indexed" URLs with per-URL analysis, classifications (KEEP 2, IMPROVE 5, MERGE 2, REMOVE 2), and priority recommendations

**Key architectural decision:** Research Commander now accepts a `.brief.yaml` path as primary input OR a plain keyword string (backward compatible). Brief fields drive module selection, depth, and YMYL handling.

---

## Future work (backlog)

| Area | Description |
|---|---|
| Product Entity System | Structured product data via `content/products/` |
| Content expansion | New articles, internal linking |
| Research Commander modules | Implement authority, DataForSEO, reddit modules |
| Automated Editorial Review | Auto-approve routine QC gates |
| Performance | Image optimization, lazy loading, Core Web Vitals |
| GSC non-indexed URL remediation | Publish root files, sitemap fixes, deduplication (see `docs/SPRINT-13-PLAN.md`) |