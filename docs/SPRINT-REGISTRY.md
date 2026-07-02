# Sprint Registry

**Canonical sprint inventory for LevNytt.se.**

This registry is the single source of truth for all project sprints. No other document defines sprint metadata independently. Future sprint plans, agents, and orchestrators read from this registry.

**Last updated:** 2026-07-02
**Status:** Completed — Sprint 14

---

## Status Values

| Status | Meaning |
|--------|---------|
| **Planned** | Sprint is scoped but not started |
| **Active** | Sprint is currently in progress |
| **Completed** | Sprint work is done, report archived |
| **Archived** | Sprint is historical, no longer referenced |

---

## Sprint List

---

### Sprint 1 — Platform Foundation

| Field | Value |
|-------|-------|
| **Status** | Archived |
| **Objective** | Create initial LevNytt.se platform. Establish hosting, domain, and first pillar pages (neolife-historia, neolife-pro-vitality, neolife-hallbarhet, neolife-vetenskap). |
| **Dependencies** | None |
| **Deliverables** | Root `.html` files for initial pillar pages, Cloudflare Pages hosting, Google Search Console setup, brand placeholder |
| **Completion Date** | 2026-05-12 |
| **Related Documents** | None |

---

### Sprint 2 — Pillar Page Expansion

| Field | Value |
|-------|-------|
| **Status** | Archived |
| **Objective** | Expand pillar page inventory to cover all major NeoLife product categories and brand pages. |
| **Dependencies** | Sprint 1 |
| **Deliverables** | neolife-affarsmojlighet, neolife-carotenoid-complex, neolife-omega-3-plus, neolife-kosttillskott hub, den-fundersamma-mannen |
| **Completion Date** | 2026-06-10 |
| **Related Documents** | None |

---

### Sprint 3 — Content Build-Out & Navigation

| Field | Value |
|-------|-------|
| **Status** | Archived |
| **Objective** | Build out informational article inventory. Establish navigation system across all pages. |
| **Dependencies** | Sprint 2 |
| **Deliverables** | First batch of informational articles, navigation system (nav.js), footer system (footer.js), sitemap.xml |
| **Completion Date** | 2026-06-20 |
| **Related Documents** | None |

---

### Sprint 4 — Hosting Migration & Critical Fixes

| Field | Value |
|-------|-------|
| **Status** | Archived |
| **Objective** | Migrate from Netlify to Cloudflare Pages. Fix critical SEO issues (canonicals, redirects). |
| **Dependencies** | Sprint 3 |
| **Deliverables** | Cloudflare Pages hosting, _redirects file, canonical URL corrections, nutriance-organic 404 redirect fix, nav.js deduplication |
| **Completion Date** | 2026-06-20 |
| **Related Documents** | None |

---

### Sprint 5 — Pillar Page Audit & Wave B Migration

| Field | Value |
|-------|-------|
| **Status** | Archived |
| **Objective** | Audit all pillar pages against 13/13 production standard. Migrate Wave B1-B9 pages to compliance. |
| **Dependencies** | Sprint 4 |
| **Deliverables** | 9 pillar pages at 13/13 audit score, pillar.css consolidation, audit_pillar_page.py script |
| **Completion Date** | 2026-06-22 |
| **Related Documents** | None |

---

### Sprint 6 — Wave 3B: Informational Article Standardization

| Field | Value |
|-------|-------|
| **Status** | Archived |
| **Objective** | Migrate all informational articles to the Publication Article Standard (PAS). Standardize ia-wrap, JSON-LD @graph, evidence tiers, CTA blocks. |
| **Dependencies** | Sprint 5 |
| **Deliverables** | All content/articles/ files converted to PAS, consistent ia-* class usage, Google Fonts integration, canonical URL corrections |
| **Completion Date** | 2026-06-28 |
| **Related Documents** | docs/PUBLICATION-ARTICLE-STANDARD.md (historical, superseded by Brief Spec) |

---

### Sprint 7 — Affärsmöjlighet 2.0 + Article/Page Separation + Legacy Migration

| Field | Value |
|-------|-------|
| **Status** | Archived |
| **Objective** | Replace MLM-style Affärsmöjlighet page with transparent decision-support page. Formalize Article/Page separation architecture. Migrate legacy Gen 1/Gen 2 pages to Gen 3 production standard. |
| **Dependencies** | Sprint 6 |
| **Deliverables** | Affärsmöjlighet 2.0 page, Article/Page Separation pattern, PAS frozen specification, all legacy pages migrated to Gen 3 |
| **Completion Date** | 2026-06-29 |
| **Related Documents** | docs/plans/AFFARSMOJLIGHET-2.0-MASTERPLAN.md |

---

### Sprint 8 — Brand Design System

| Field | Value |
|-------|-------|
| **Status** | Archived |
| **Objective** | Create centralized brand design system. Establish pillar.css as single shared stylesheet. Build assets/brand/ directory. |
| **Dependencies** | Sprint 7 |
| **Deliverables** | docs/BRAND-DESIGN-SYSTEM.md, assets/brand/ directory (LV Mark, favicon, apple-touch-icon, hero-watermark, OG image), brand injectors in components.js, pillar.css with CSS variables |
| **Completion Date** | 2026-06-29 |
| **Related Documents** | docs/BRAND-DESIGN-SYSTEM.md |

---

### Sprint 9 — Brand Rollout + Repository Cleanup

| Field | Value |
|-------|-------|
| **Status** | Completed |
| **Objective** | Deploy brand OG image to all root pages and source articles. Ensure #site-nav on all root pages. Verify site-wide component coverage. Clean up repository artifacts. |
| **Dependencies** | Sprint 8 |
| **Deliverables** | Brand OG image on all pages, #site-nav on all root pages, site-wide component coverage verified, repository cleanup |
| **Completion Date** | 2026-07-01 |
| **Related Documents** | docs/sprints/SPRINT-9-REPORT.md |

---

### Sprint 10 — Post-Cleanup Baseline

| Field | Value |
|-------|-------|
| **Status** | Completed |
| **Objective** | Establish full documentation baseline: PROJECT-STATUS, CURRENT-SPRINT, DECISIONS, PROJECT-ENTRY. Create Sprint 9 report. Align all documentation with current architecture. |
| **Dependencies** | Sprint 9 |
| **Deliverables** | All 4 core operational docs aligned, Sprint 9 report archived, PHASE-2-ROADMAP rewritten for current architecture |
| **Completion Date** | 2026-07-01 |
| **Related Documents** | PROJECT-ENTRY.md, PROJECT-STATUS.md, CURRENT-SPRINT.md, DECISIONS.md |

---

### Sprint 11 — Production Orchestrator + Brief Architecture + Telemetry

| Field | Value |
|-------|-------|
| **Status** | Completed |
| **Objective** | Build V2 production pipeline with Production Brief → Research Package → Editorial chain. Add QA gating and cost telemetry. |
| **Dependencies** | Sprint 10 |
| **Deliverables** | docs/PRODUCTION-PIPELINE.md (V2), docs/PRODUCTION-ORCHESTRATOR.md (V2), docs/PRODUCTION-BRIEF-SPEC.md, docs/RESEARCH-PACKAGE-SPEC.md, docs/COST-TELEMETRY.md, scripts/run-production.sh, scripts/qa-article.sh, scripts/cost-report.sh |
| **Completion Date** | 2026-07-01 |
| **Related Documents** | docs/sprints/SPRINT-11-REPORT.md |

---

### Sprint 12 — Research Commander V2 + GSC Content Audit

| Field | Value |
|-------|-------|
| **Status** | Completed |
| **Objective** | Refactor Research Commander agent to accept Production Brief as primary input (keyword backward compatible). Audit 11 GSC "Crawled – not indexed" URLs. Update all pipeline specs for V2. |
| **Dependencies** | Sprint 11 |
| **Deliverables** | Agent definition (research-commander.md), Agent Registry (#7), pipeline/orchestrator/brief/package specs updated, full GSC audit report (11 URLs, 9 criteria each), KEEP/IMPROVE/MERGE/REMOVE classifications |
| **Completion Date** | 2026-07-02 |
| **Related Documents** | docs/sprints/SPRINT-12-REPORT.md, docs/gsc/GSC-CONTENT-AUDIT.md, docs/specifications/AGENT-REGISTRY.md |

---

### Sprint 13 — GSC Non-Indexed URL Remediation

| Field | Value |
|-------|-------|
| **Status** | Completed |
| **Objective** | Maximize indexability of the highest-priority non-indexed URLs by resolving all repository-side issues identified in the GSC audit. |
| **Dependencies** | Sprint 12 |
| **Deliverables** | 4 root .html copies for orphaned pages with production includes, sitemap.xml updated, naringsbrist vs naringsbrist-symptom differentiated, 5 isolated pages received 5+ internal links each, titles shortened (neolife-tre-en-en 85→56, golden-home-care 88→59), neolife-pro-vitality title fixed, canonical resolution between tre-en-en pages |
| **Completion Date** | 2026-07-02 |
| **Related Documents** | docs/SPRINT-13-PLAN.md, docs/sprints/SPRINT-13-REPORT.md, docs/gsc/GSC-CONTENT-AUDIT.md |

---

### Sprint 14 — Sprint Registry System V1

| Field | Value |
|-------|-------|
| **Status** | Completed |
| **Objective** | Create centralized Sprint Registry as single source of truth for all project sprints. Build infrastructure so that future commands like "Run Sprint X", "Close Sprint X", "Open Sprint X" can be understood by any project agent by reading the registry. |
| **Dependencies** | Sprint 13 |
| **Deliverables** | docs/SPRINT-REGISTRY.md with sprints 1-20, CURRENT-SPRINT.md updated to reference registry, PROJECT-STATUS.md updated to reference registry, PHASE-2-ROADMAP.md updated to reference registry |
| **Completion Date** | 2026-07-02 |
| **Related Documents** | CURRENT-SPRINT.md, PROJECT-STATUS.md, PHASE-2-ROADMAP.md, docs/sprints/SPRINT-14-REPORT.md |

---

### Sprint 15 — Product Entity System V1

| Field | Value |
|-------|-------|
| **Status** | **Active** |
| **Objective** | Create centralized structured product data so every page references the same prices, descriptions, and categories. No build step. |
| **Dependencies** | Sprint 14 |
| **Deliverables** | content/products/prices.json (all 57 products), content/products/product-data.js (runtime module with price/entity lookups, sponsor link fixing, replacing components.js productMap), golden-home-care.html migrated as reference implementation |
| **Completion Date** | *(in progress)* |
| **Related Documents** | docs/plans/PHASE-2-ROADMAP.md, content/products/product-data.js, content/products/prices.json |

---

### Sprint 16 — Content Expansion Batch 1 (Planned)

| Field | Value |
|-------|-------|
| **Status** | Planned |
| **Objective** | Publish new pillar pages and informational articles in uncovered niches. Target clusters: Vitamin D depth, Magnesium depth, Probiotics depth, Fiber depth. New pillar page candidates: neolife-sport. |
| **Dependencies** | Sprint 14 |
| **Deliverables** | New article HTML files in content/articles/, new root-level pillar pages, cluster expansion |
| **Completion Date** | — |
| **Related Documents** | docs/plans/PHASE-2-ROADMAP.md, docs/editorial-backlog/ |

---

### Sprint 17 — Authority Research Expansion (Planned)

| Field | Value |
|-------|-------|
| **Status** | Planned |
| **Objective** | Expand authority research system with ingredient/condition profiles. Cover supplement ingredients (omega-3, magnesium, vitamin D, probiotics) and health conditions (inflammation, sleep, stress, immune function). Each profile includes tiered sources and key factual claims with evidence levels. |
| **Dependencies** | Sprint 14 |
| **Deliverables** | Authority profiles for key supplement ingredients and health conditions, tiered source libraries (PubMed, EFSA, WHO, Livsmedelsverket) |
| **Completion Date** | — |
| **Related Documents** | docs/authority-research/ |

---

### Sprint 18 — Performance & Accessibility Audit (Planned)

| Field | Value |
|-------|-------|
| **Status** | Planned |
| **Objective** | Audit and improve site performance and accessibility. Image optimization, lazy loading, Core Web Vitals tuning, contrast checks, ARIA labels, keyboard navigation, schema.org validation, broken link checks. |
| **Dependencies** | Sprint 14 |
| **Deliverables** | Optimized images, lazy loading implementation, Core Web Vitals report, accessibility improvements, trailing-slash canonical cleanup, validation fixes |
| **Completion Date** | — |
| **Related Documents** | docs/plans/PHASE-2-ROADMAP.md |

---

### Sprint 19 — Video & Interactive Tools (Planned)

| Field | Value |
|-------|-------|
| **Status** | Planned |
| **Objective** | Produce explainer video for Affärsmöjlighet page. Build initial interactive tools: comparison pages, decision guides. |
| **Dependencies** | Sprint 15 (Product Entity System) |
| **Deliverables** | Embedded video on Affärsmöjlighet page, article-to-video workflow documented, initial comparison pages, decision guides |
| **Completion Date** | — |
| **Related Documents** | docs/plans/PHASE-2-ROADMAP.md, docs/plans/AFFARSMOJLIGHET-2.0-MASTERPLAN.md |

---

### Sprint 20 — Site-Wide Consistency & Automation (Planned)

| Field | Value |
|-------|-------|
| **Status** | Planned |
| **Objective** | Final pass on site-wide consistency. Resolve remaining PAS variations in content/articles/. Automated QA improvements. Periodic validation scripts. |
| **Dependencies** | Sprint 18 |
| **Deliverables** | Consistent PAS compliance across all articles, automated validation scripts, site-wide consistency report |
| **Completion Date** | — |
| **Related Documents** | docs/plans/PHASE-2-ROADMAP.md |

---

## Agent Command Reference

The registry is designed so that project agents can execute these commands by reading the registry:

| Command | Agent Action |
|---------|-------------|
| `Run Sprint <N>` | Read registry for sprint objective, deliverables, dependencies. Execute. |
| `Continue Sprint <N>` | Read registry, check CURRENT-SPRINT.md for progress, resume unfinished work. |
| `Close Sprint <N>` | Create sprint report at docs/sprints/SPRINT-<N>-REPORT.md, update registry status to Completed, update CURRENT-SPRINT.md. |
| `Open Sprint <N>` | Update registry status to Active, update CURRENT-SPRINT.md with sprint details. |

---

## Engineering Rules

1. The Sprint Registry is the **canonical source** for sprint names, order, status, objectives, dependencies, deliverables, and documentation links.
2. No future document should redefine sprint metadata independently — always reference the registry.
3. When a sprint is completed, update its status to `Completed` and add the completion date and report path.
4. When a sprint is active, update its status to `Active` and ensure CURRENT-SPRINT.md reflects the same sprint.
5. Sprint reports are archived in `docs/sprints/SPRINT-<N>-REPORT.md`.
6. Future sprint plans should reference the Sprint Registry instead of duplicating sprint metadata.
