# Sprint 12 — Research Commander V2 + GSC Content Audit

**Status:** ✅ Completed
**Period:** 2026-07-01 — 2026-07-02
**Commit:** `436f7ed`

---

## Objective

1. Refactor Research Commander agent to accept Production Brief as primary input (keyword backward compatible).
2. Audit 11 GSC "Crawled – currently not indexed" URLs and produce a content quality report.
3. Update all pipeline/orchestrator/brief/package specs for Research Commander V2.

---

## Deliverables

### Research Commander V2

| Deliverable | Location | Notes |
|---|---|---|
| Agent definition | `.opencode/agents/research-commander.md` | Local only (`.opencode/` gitignored). V2: brief-first input, Phase 0 resolution, brief-field-driven planning |
| Agent Registry | `docs/specifications/AGENT-REGISTRY.md` | Research Commander registered as agent #7 (V2.0) with responsibilities, permissions, version history |
| Pipeline spec | `docs/PRODUCTION-PIPELINE.md` (V2.2) | Backward compatibility note, version history |
| Orchestrator spec | `docs/PRODUCTION-ORCHESTRATOR.md` (V2.2) | Brief-first Stage 2 contract, resume detection table, version history |
| Brief spec | `docs/PRODUCTION-BRIEF-SPEC.md` (V1.1) | Entity field backward compat note |
| Package spec | `docs/RESEARCH-PACKAGE-SPEC.md` (V1.1) | Backward compatibility input mode |

### GSC Content Audit

| Deliverable | Location | Notes |
|---|---|---|
| Full audit report | `docs/gsc/GSC-CONTENT-AUDIT.md` | 11 URLs analyzed across 9 criteria each |
| Classification summary | Within report | KEEP (2), IMPROVE (5), MERGE (2), REMOVE (2) |
| Priority recommendations | Within report | P1–P3 with expected SEO impact |

---

## Key Findings

- **4 orphaned pages** exist only in `content/articles/` with no root `.html` — also absent from sitemap. These are the highest-quality articles in the audit and the strongest non-indexing signal.
- **3 thin FAQ-only pages** (#8, #10, #11) at <125 lines struggle to demonstrate sufficient value.
- **2 duplicate clusters** (#2/#5 on naringsbrist, #10 overlapping with indexed omega-3 guides).
- **Root file existence** is the single strongest correlation with non-indexing in this dataset.

---

## Decisions

1. Research Commander V2 accepts `.brief.yaml` path OR keyword string (backward compat).
2. `.opencode/` gitignore confirmed intentional — agent implementation is local; specs in `docs/` are canonical.
3. GSC audit is analysis-only — no code changes, redirects, or sitemap edits made during Sprint 12.

---

## Commits

```
436f7ed Sprint 12: Research Commander V2 + GSC Content Audit
```

---

## Next

Sprint 13 proposed — GSC Non-Indexed URL Remediation. See `docs/SPRINT-13-PLAN.md`.
