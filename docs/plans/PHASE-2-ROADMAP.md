# Phase 2 — Platform Expansion

> **Status:** Active
> **Previous phase:** Phase 1 (Platform Build — complete)
> **Last updated:** 2026-06-30

---

## Current Architecture

LevNytt.se is a **vanilla HTML5/CSS3/ES5 static site** hosted on Cloudflare Pages. There is no build step, no framework, no npm, no transpilation. Files are deployed as-is on `git push`.

### Major Systems

#### Publication Agent
The Publication Agent (`.opencode/agents/publication-agent.md`) generates informational articles and deploys them from `content/articles/` to root-level production via `_redirects` 200-rewrites. Articles follow the Publication Article Standard (`docs/PUBLICATION-ARTICLE-STANDARD.md`) and are structurally uniform: `ia-wrap` content wrapper, `ia-*` CSS classes, JSON-LD `@graph` (Article + FAQPage), evidence tier labels, tiered internal linking, and CTA blocks.

#### Pillar Page Template
Pillar pages and product pages are hand-authored root-level `.html` files that follow the Gen 3 production standard. Each page passes the 13/13 audit checklist (nav.js, footer.js, components.js, pillar.css, no inline `:root`, Google Fonts, 3+ breakpoints, clean canonical, OG image, viewport meta). The `pillar-page-template` skill provides the migration workflow.

#### Brand Design System
`docs/BRAND-DESIGN-SYSTEM.md` defines the LV Mark, brand colors (`#1B4332` deep green, `#E8C870` light gold), and usage rules. All brand assets derive from a single master SVG.

#### Shared assets/brand/
All brand assets live in `assets/brand/`:
- `favicon.svg` — Browser tab icon
- `apple-touch-icon.png` — iOS home screen icon
- `hero-watermark.svg` — Background watermark for hero sections
- `og-brand.png` — Default Open Graph image (1200x630)
- `logo.svg`, `logo-dark.svg`, `logo-light.svg` — LV Mark variants
- `author-avatar.svg` — Author avatar source

Brand meta (favicon, apple-touch-icon) and visual enhancements (hero watermark, author avatar) are injected at runtime by `components.js`. No individual page hardcodes brand assets.

#### Navigation, Footer, and Components
Three shared JavaScript files loaded with `defer` on every root page:

| File | Purpose |
|---|---|
| `nav.js` | Self-injecting navigation IIFE. Renders the LV Mark, navigation links. |
| `footer.js` | Self-injecting footer IIFE. Renders brand mark, links, disclaimers. |
| `components.js` | Brand meta injector, hero watermark injector, author avatar injector, sponsor-ID rewriting for all `neolifeshop.com` links, scroll-to-top button. |

#### pillar.css (Design System)
`/pillar.css` is the single shared stylesheet. It defines brand CSS variables:

| Token | Value | Usage |
|---|---|---|
| `--lv-green` | `#1B4332` | Primary brand |
| `--lv-gold` | `#E8C870` | Secondary brand |
| `--lv-green-dark` | `#0D2C1E` | Dark accent |
| `--lv-green-light` | `#2D6A4F` | Light accent |
| `--lv-cream` | `#F9F6EF` | Background |

Every production page includes `pillar.css` via `<link>`. No inline `:root` blocks remain.

#### Documentation Hierarchy
Documentation is read in a fixed order before any implementation:

1. `PROJECT-ENTRY.md` — entry point, skills, workflow
2. `PROJECT-STATUS.md` — current state, milestones, priorities
3. `CURRENT-SPRINT.md` — active sprint
4. `DECISIONS.md` — permanent engineering decisions

Historical documents exist alongside operational ones but are explicitly classified as non-authoritative. Sprint reports are archived in `docs/sprints/`.

#### Repository File Structure
```
levnytt-site/
├── *.html                        ← Root-level pages (~80)
├── content/
│   ├── articles/                 ← Source articles (deployed via PA)
│   └── products/                 ← Nascent product entity system
├── assets/brand/                 ← Brand assets
├── nav.js, footer.js, components.js  ← Shared components
├── pillar.css                    ← Design system
├── _redirects                    ← Cloudflare routing
├── sitemap.xml                   ← Hand-maintained URL index
├── 404.html                      ← Custom error page
├── levnytt-se-master-template.html  ← Dev template (not public)
└── docs/                         ← All documentation
```

#### Design Tokens and Typography
- Fonts: Playfair Display (headings, weights 400/600/700), Inter (body, weights 300/400/500/600)
- Max content width: 820px (pillar pages), 760px (informational articles)
- Colors derive from brand CSS variables

#### Hosting and Deployment
- Hosting: Cloudflare Pages
- Deployment: Automatic on `git push`
- Routings: Pretty URLs (root files), `_redirects` rewrites for `content/articles/`, catch-all 404

---

## Completed Milestones

| Milestone | Description | Sprint |
|---|---|---|
| **Hosting Migration** | Netlify → Cloudflare Pages | Pre-Sprint |
| **Audit A1–A3** | Critical fixes: canonicals, redirects, nav dedup | Pre-Sprint |
| **Wave B1–B9** | All pillar pages → 13/13 audit | Pre-Sprint |
| **Nav Migration** | Hardcoded nav → shared nav.js/footer.js on all pages | Pre-Sprint |
| **Wave 3B / Sprint 6** | All informational articles migrated to production standard | Sprint 6 |
| **Affärsmöjlighet 2.0** | Sprint 7 — transparent decision-support page replacing MLM-style page | Sprint 7 |
| **Article/Page Separation** | Informational articles → `content/articles/` with PA standard; pillar pages → root-level hand-authored | Sprint 7 |
| **Publication Article Standard** | Frozen specification for all informational articles | Sprint 7 |
| **Legacy Migration** | All legacy Gen 1/Gen 2 pages migrated to Gen 3 production standard | Sprint 7 |
| **Brand Design System** | `docs/BRAND-DESIGN-SYSTEM.md`, `assets/brand/`, brand injectors in `components.js`, pillar.css consolidation | Sprint 8 |
| **Brand Rollout** | Brand OG image deployed to all root pages + source articles; `#site-nav` on all pages; site-wide component coverage verified | Sprint 9 |
| **Documentation Baseline** | All 4 core operational docs updated; Sprint 9 report created | Sprint 10 |
| **Documentation Alignment** | PA standard updated with brand OG; PHASE-2-ROADMAP rewritten for current architecture | Sprint 11 |

---

## Current Production Status

| Component | Status |
|---|---|
| All root pages use shared components (nav.js, footer.js, components.js) | ✅ Operational |
| All root pages link pillar.css with brand CSS variables | ✅ Operational |
| Brand assets in assets/brand/ injected by components.js | ✅ Operational |
| Brand OG image on all generic pages | ✅ Operational |
| Publication Agent generates PA-standard articles | ✅ Operational |
| Pillar Page Template creates 13/13 compliant pillar pages | ✅ Operational |
| 404 page, robots.txt, sitemap.xml | ✅ Operational |
| Cloudflare Pages auto-deployment | ✅ Operational |
| Documentation hierarchy and sprint workflow | ✅ Operational |
| Product Entity System | ⬜ Not started |
| Interactive tools (calculators, comparisons) | ⬜ Not started |
| Authority Research expansion | ⬜ Not started |

---

## Remaining Major Work

### Product Entity System
Create a centralized product data source so every page references the same prices, descriptions, and categories. Currently, product prices are hardcoded per page. A structured system (e.g., `content/products/*.json` or a JS data module) would eliminate copy-paste errors and enable automated price-per-use calculations.

**Deliverable:** Data file with all marketed NeoLife products, prices (customer/distributor), categories, and metadata. No build step — the file must be consumable directly by JavaScript at runtime or embedded during page authoring.

### Authority Research Expansion
The authority research system (`docs/authority-research/`) contains source material for direct sales, MLM regulation, and consumer protection topics. Expanding this to cover supplement science, ingredient profiles, and health condition research would strengthen the factual foundation for new articles.

**Deliverable:** Authority profiles for key supplement ingredients (omega-3, magnesium, vitamin D, probiotics, etc.) and health conditions (inflammation, sleep, stress, immune function). Each profile includes tiered sources (PubMed, EFSA, WHO, Livsmedelsverket) and key factual claims with evidence levels.

### Content Expansion
Add new pillar pages and informational articles in uncovered niches. Current gap analysis (see `docs/editorial-backlog/`) identifies opportunities in:

- Vitamin D cluster (depth)
- Magnesium cluster (depth)
- Probiotics cluster (depth)
- Fiber cluster (depth)
- New pillar pages (e.g., `/neolife-sport/`)
- New article topics outside existing clusters

**Deliverable:** New article HTML files in `content/articles/` deployed via the Publication Agent, and new pillar pages as root-level `.html` files.

### Video Automation
The Affärsmöjlighet page has dashed placeholder boxes for a savings calculator and an explainer video. Producing and embedding a short explainer video (2–4 min) would cater to visitors who prefer watching over reading.

**Deliverable:** Embedded video on the Affärsmöjlighet page (YouTube/Vimeo), with a documented article-to-video workflow for future content.

### QA Improvements
- **Performance:** Image optimization, lazy loading, Core Web Vitals tuning
- **Accessibility:** Contrast checks, ARIA labels, keyboard navigation
- **Consistency:** Trailing-slash canonical cleanup, remaining PA-standard variations in `content/articles/`
- **Validation:** Periodic schema.org validation, broken link checks

### Interactive Tools (Future)
- Savings calculator on the Affärsmöjlighet page
- Price-per-use comparison tables
- Product comparison pages
- Decision guides

These depend on the Product Entity System and are deferred until the data layer exists.

---

## Guiding Principles

### Single Source of Truth
The Git repository is the authoritative record. Documentation describes the repository. If they disagree, the repository is correct and documentation must be updated. Brand identity has a single source of truth in `docs/BRAND-DESIGN-SYSTEM.md`.

### Shared Components
Navigation, footer, and brand elements are injected by shared JavaScript files. No page may hardcode nav, footer, brand meta, or sponsor IDs. Centralized components mean site-wide changes require editing one file instead of every page.

### Documentation First
Every sprint updates documentation before it is considered complete. The four core operational documents (`PROJECT-ENTRY.md`, `PROJECT-STATUS.md`, `CURRENT-SPRINT.md`, `DECISIONS.md`) are read at the start of every session. Skills are loaded before implementation.

### Articles and Pages Are Separate Systems
Informational articles (`content/articles/`) use the Publication Agent pipeline and follow the Publication Article Standard. Pillar pages and product pages are hand-authored root-level `.html` files. They share the same components (`nav.js`, `footer.js`, `components.js`, `pillar.css`, `assets/brand/`) but have different structural templates.

### Reusable Brand Assets
All brand assets originate from a single master LV Mark SVG, stored in `assets/brand/`. Raster variants (favicon, apple-touch-icon, OG image) are exported from the master. No page hardcodes brand images or meta tags — `components.js` injects them at runtime.

### Sprint-Based Development
One active sprint at a time. `CURRENT-SPRINT.md` defines the active sprint. Work outside the active sprint is backlog. Each sprint has a clear objective, task list, and completion criteria. Sprints are numbered and documented in `docs/sprints/` upon completion.

### No Build Step
The site is and remains vanilla HTML5/CSS3/ES5. No build framework, no npm at the repo root, no transpilation. Deployment is a direct `git push` with zero build step. New tools that require a build pipeline must have a written justification and explicit approval.

### Static HTML — No Framework
All pages are hand-authored `.html` files. There is no React, Vue, Astro, Next.js, or any other framework. Routing is handled by Cloudflare Pages (Pretty URLs for root files, `_redirects` for `content/articles/`). This architecture is a permanent engineering decision (see `DECISIONS.md` B1).
