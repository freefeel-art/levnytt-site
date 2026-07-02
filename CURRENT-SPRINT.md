# CURRENT-SPRINT.md
# LevNytt.se — Project Phase

Last updated: 2026-07-02

---

## Phase: Infrastructure & Registry

The Sprint Registry (`docs/SPRINT-REGISTRY.md`) is now the **canonical source** for all sprint metadata. This file tracks the active sprint only; do not duplicate sprint details here.

---

## Sprint 15 — Product Entity System V1

| | |
|---|---|
| **Status** | ✅ Completed |
| **Completed** | 2026-07-02 |
| **Commit** | `03b4a82` |

**Delivered:**
- `content/products/prices.json` — all 57 products with prices
- `content/products/product-data.js` — runtime JS module
- `golden-home-care.html` — reference migration
- `components.js` — `fixLinks()` delegates to `LevNyttProductData`

See `docs/SPRINT-REGISTRY.md` for all sprint data.

---

## Sprint 16 — Content Expansion Batch 1

| | |
|---|---|
| **Status** | ✅ Completed |
| **Completed** | 2026-07-02 |
| **Commit** | `0c04c9c` |

**Delivered:**
- `d-vitaminbrist-sverige.html` — informational article (Sprint 16)
- `neolife-sport.html` — Gen 3 pillar page (Sprint 16)
- `magnesium-komplett-guide.html` — depth article (Sprint 9, retroactively attributed)
- `probiotika-komplett-guide.html` — depth article (Sprint 9, retroactively attributed)
- `kostfiber-komplett-guide.html` — depth article (Sprint 9, retroactively attributed)

See `docs/SPRINT-REGISTRY.md` for all sprint data.

---

## Sprint 17 — Authority Research Expansion

| | |
|---|---|
| **Status** | ✅ Completed |
| **Completed** | 2026-07-02 |

**Delivered:**
- 18 authority profiles in `docs/research/authority-profiles/`
- `research/manifests/authority-profiles-batch.json` — checkpoint file
- Research Commander V3 — resume-from-last-success command mode added

See `docs/SPRINT-REGISTRY.md` for full sprint data.

---

## Sprint 18 — Performance & Accessibility Audit

| | |
|---|---|
| **Status** | ✅ Completed |
| **Completed** | 2026-07-02 |

**Delivered:**
- pillar.css + nav.js + footer.js + og:image + @graph Article schema on 18 pages
- trailing-slash canonical cleanup (9 pages)
- `scripts/fix-sprint18-pages.py`

See `docs/SPRINT-REGISTRY.md` for full sprint data.

---

## Sprint 19 — Video & Interactive Tools

| | |
|---|---|
| **Status** | ✅ Completed |
| **Completed** | 2026-07-02 |

**Delivered:**
- `sparanalys.html` — interactive savings calculator
- Video placeholder + comparison table + FAQ on `direktforsaljning-fakta.html`
- Article-to-video workflow documented

See `docs/SPRINT-REGISTRY.md` for full sprint data.

---

## Sprint 20 — Site-Wide Consistency & Automation

| | |
|---|---|
| **Status** | ✅ Completed |
| **Completed** | 2026-07-02 |

**Delivered:**
- Consistent PAS compliance across all articles
- `scripts/fix-sprint20-consistency.py`
- Site-wide consistency report

See `docs/SPRINT-REGISTRY.md` for full sprint data.

---

## Sprint History

See `docs/SPRINT-REGISTRY.md` for the canonical list of all sprints (1–20), their status, objectives, deliverables, completion dates, and dependencies.

Sprint reports are archived at `docs/sprints/SPRINT-<N>-REPORT.md`.

---

## Sprint 21 — Markdown-First Publication Pipeline

| | |
|---|---|
| **Status** | ✅ Completed |
| **Completed** | 2026-07-02 |
| **Commit** | `c793f9e` |

**Delivered:**
- `scripts/md-to-article.py` — V2 → PAS V1.0 HTML converter (Python stdlib only)
- `docs/PUBLICATION-SOURCE-V2.md` — frozen V2 frontmatter spec
- `docs/MARKDOWN-FIRST-IMPLEMENTATION-PLAN.md` — implementation plan and constraints
- `docs/CONTRADICTION-RESOLUTION.md` — C1–C8 classification and resolution guide
- `content/articles/kalcium-brist-symtom/` — first article via new pipeline (QA GREEN 12/12)
- `_redirects` + `sitemap.xml` updated per B4/B5

See `docs/SPRINT-REGISTRY.md` for full sprint data.

---

## Future work (backlog)

| Area | Description |
|---|---|
| Performance & Accessibility | Image optimization, lazy loading, Core Web Vitals |
| Video & Interactive Tools | Explainer video, comparison pages, decision guides |
| Site-Wide Consistency | PAS compliance, automated validation |
