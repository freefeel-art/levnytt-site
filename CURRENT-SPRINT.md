# CURRENT-SPRINT.md
# LevNytt.se — Project Phase

Last updated: 2026-06-30

---

## Phase: Maintenance + Feature Development

The Gen 3 migration is **complete**.
The Brand System integration (Sprint 8) and Brand Rollout (Sprint 9) are **complete**.
Sprint 10 (Documentation & Baseline Update) is **active**.

---

## Sprint Status

| | |
|---|---|
| **Status** | ✅ Completed |
| **Sprint** | 9 — Brand Rollout |
| **Completed** | 2026-06-30 |

### Tasks (Sprint 9)

- [x] Replace legacy branding on all existing pages
- [x] Update shared components for brand consistency
- [x] Split `/pillar.css` responsibilities
- [x] Resolve duplicated nav/footer/CSS loading
- [x] Verify the site-wide consistency

### What was implemented (Sprint 9)

- Brand OG image (`assets/brand/og-brand.png`) deployed to all 70 root pages + 37 content/articles source files
- `#site-nav` placeholder added to final 44 root pages + 3 subdirectory pages
- Final validation confirmed all 80 root pages have: `nav.js` + `footer.js` + `components.js` + `pillar.css` + `#site-nav`
- LV Brand Mark present in both `nav.js` and `footer.js`
- Hero watermark injector present in `components.js`
- Author avatar injector present in `components.js`

### Pages excluded from brand OG replacement

Pages with page-specific or product-specific OG images were preserved:

- `den-fundersamma-mannen.html` — editorial OG
- `fytosteroler-cellmembran.html` — editorial OG
- `integritetspolicy.html` — editorial OG
- `neolife-affarsmojlighet.html` — editorial OG
- `neolife-hallbarhet.html` — editorial OG
- `neolife-omega-3-plus.html` — product image OG
- `neolife-pro-vitality.html` — product image OG
- `neolife-tre-en-en-cellnaring.html` — product image OG
- `personlig-vard.html` — product image OG
- `404.html` — no OG (utility page)

---

## Active Sprint — 12

| | |
|---|---|
| **Status** | ✅ Completed |
| **Sprint** | 10 — Documentation & Baseline Update |
| **Completed** | 2026-06-30 |
| **Next** | Sprint 11 — Documentation Alignment |

### Sprint 10 completed

- PROJECT-STATUS.md, CURRENT-SPRINT.md, DECISIONS.md, PROJECT-ENTRY.md all updated
- SPRINT-9-BRAND-ROLLOUT.md created (archived in repo cleanup)
- Final validation complete: 58/75 .md files clean, 6 files reported for review

### Sprint 11 completed

- PUBLICATION-ARTICLE-STANDARD.md: OG image path updated, Sprint 7/8/9 drift resolved
- PHASE-2-ROADMAP.md: completely rewritten for current vanilla HTML architecture
- Validation: no Astro references, no obsolete OG paths, no DECISIONS.md contradictions

---

## Active Sprint — 12

| | |
|---|---|
| **Status** | 🟢 Active |
| **Sprint** | 12 — Product Entity System Foundation |
| **Started** | 2026-06-30 |

### Objective

Establish the architecture and specification for a Product Entity System — the canonical source for product identity, classification, and metadata across all LevNytt systems.

No production pages modified. Specification only.

### Tasks

- [x] Audit all places product information currently exists
- [x] Design Product Entity schema with field-level justification
- [x] Define repository structure (content/products/entities/)
- [x] Create category taxonomy (content/products/categories.json)
- [x] Document integration plan (PA, PB, Price DB, calculators, video)
- [x] Document migration strategy (incremental, 6 waves)
- [x] Validate: no Price DB duplication, no DECISIONS.md contradiction

### Completion criteria

- Product Entity architecture documented
- Canonical schema defined
- Repository structure proposed
- Integration plan completed
- Migration strategy documented
- No production pages modified
- No articles modified

### Next action

Start Wave 1 entity creation (Omega-3 Plus, Carotenoid Complex, Pro Vitality, Formula IV, Tre-en-en). Resolve multi-variant product modeling question first.

---

## Future work (backlog, unordered)

| Area | Description |
|---|---|
| **Product Entity System** | Structured product data via `content/products/` |
| **Content expansion** | New articles, internal linking |
| **Performance** | Image optimization, lazy loading, Core Web Vitals |
| **Accessibility** | Contrast checks, ARIA labels, keyboard navigation |
| **Interactive tools** | Comparison pages, calculators, decision guides |

---

## Sprint template

When opening a new sprint, use:

```
## Sprint status
Active.

## Sprint objective
[One sentence describing the goal.]

## Tasks
- [ ] Task 1
- [ ] Task 2

## Completion criteria
[Specific, verifiable conditions that define "done".]

## Next action
[Exactly what to do next.]
```
