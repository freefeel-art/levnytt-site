# PROJECT-STATUS.md — LevNytt.se Executive Dashboard

*Last updated: 2026-06-30 | See `PROJECT-ENTRY.md` for reading order. See `DECISIONS.md` for engineering conventions.*

---

## Executive Summary

| | |
|---|---|
| **Project** | LevNytt.se |
| **Mission** | Sweden's evidence-based NeoLife knowledge platform |
| **Status** | 🟢 Production Stable |
| **Phase** | Maintenance + Feature Development |
| **Migration** | ✅ Complete |
| **Brand System** | ✅ Integrated and rolled out |
| **Deployment** | Cloudflare Pages (automatic deployment) |
| **Next Focus** | Content Expansion |

---

## Current State (post-Sprint 9)

| Status | Value |
|---|---|
| **Production** | ✅ Stable — live at https://levnytt.se/ |
| **Platform** | ✅ All root pages use shared components + brand system |
| **Design system** | ✅ `pillar.css` with CSS variables on all pages |
| **Brand System** | ✅ Integrated: `assets/brand/`, brand injectors, brand OG image |
| **Shared components** | ✅ `nav.js` + `footer.js` + `components.js` on all root pages |
| **Deployment** | Cloudflare Pages — automatic on `git push` |
| **Current phase** | Documentation baseline + Content Expansion |

---

## Project Objectives

- Build Sweden's most trustworthy NeoLife knowledge platform
- Help visitors make informed decisions using facts, research, and transparency
- Prioritize educational content over sales content
- Build topical authority through high-quality pillar pages and informational articles

---

## Vision

Become Sweden's most trusted independent NeoLife knowledge platform by publishing evidence-based, transparent, and decision-oriented content.

LevNytt exists to help people understand before they decide.

Every article, pillar page and decision tool should increase trust through facts, research and transparency rather than marketing claims.

---

## Engineering Principles

- **Repository is the source of truth** — all changes flow through git
- **Documentation reflects the repository** — keep docs in sync with the codebase
- **Skills are the implementation authority** — load required skills before implementation
- **Verify before implementing** — audit every page before making changes
- **Audit before and after every migration** — run `audit_pillar_page.py` on both sides
- **Prefer autonomous execution** — the AI should act on instructions without asking for permission on routine tasks
- **Ask only when business, branding, legal, SEO strategy or content strategy decisions are required** — the AI escalates these; everything else is routine

---

## Definition of Done

A page or sprint is considered complete only when:

- it passes the applicable production audit
- it follows the current design system
- all required project skills have been applied
- documentation has been updated
- changes have been committed and pushed
- deployment has completed successfully

---

## Site overview

**LevNytt.se** is a Swedish-language knowledge platform for NeoLife supplements and home care products. Its purpose is to drive organic search traffic and convert readers into NeoLife customers or distributors.

- **Language:** Swedish (sv-SE)
- **Sponsor ID:** 41-830928
- **Customer shop:** `https://se.neolifeshop.com/i/shop.html?sponsor=41-830928`
- **Distributor registration:** `https://se.neolifeshop.com/i/registration.html?type=reseller&sponsor=41-830928`

---

## Architecture

### Stack

| Layer | Technology |
|---|---|
| Pages | Vanilla HTML5 — hand-authored `.html` files |
| Styling | `pillar.css` (shared design system with CSS variables) + page-specific `<style>` blocks on select pages |
| Brand System | `assets/brand/` — LV Mark SVG, favicon, apple-touch-icon, hero-watermark, brand OG image |
| Shared components | `nav.js`, `footer.js`, `components.js` — self-injecting IIFEs, loaded with `defer` |
| Component injection | `components.js` injects brand meta, hero watermark, author avatar, scroll-to-top, sponsor-ID rewriting |
| Routing | Cloudflare Pages "Pretty URLs" + `_redirects` file |
| SEO | Hand-maintained `sitemap.xml`, JSON-LD schemas per page |
| Hosting | Cloudflare Pages — auto-deploys on `git push` |
| Repository | GitHub: `freefeel-art/levnytt-site` |
| Images | JPEG/PNG/WebP in `/images/`. Product images in `img/og/` and `neolife-*-subdir/`. |
| Fonts | Google Fonts CDN: Playfair Display (headings) + Inter (body) |

There is **no build step, no npm, no framework**. Files are deployed as-is.

### Design tokens (pillar.css)

| Token | Value | Usage |
|---|---|---|
| `--lv-green` | `#1B4332` | Primary brand — deep green |
| `--lv-gold` | `#E8C870` | Secondary brand — light gold |
| `--lv-green-dark` | `#0D2C1E` | Dark green accent |
| `--lv-green-light` | `#2D6A4F` | Light green accent |
| `--lv-cream` | `#F9F6EF` | Background cream |
| Max content width | `820px` | Article body width |

### Required page includes

Every production page must include:

```html
<meta name="google-site-verification" content="kAcoLDFGCpGh42gIFRgPeWlC253vTP3OLBs6wI8KDQ0">
<meta name="p:domain_verify" content="6a9e88f7014abe0735767f464c08f337"/>
```

```html
<link rel="stylesheet" href="/pillar.css">
<script src="/nav.js" defer></script>
<script src="/footer.js" defer></script>
<script src="/components.js" defer></script>
```

`components.js` provides:
- Brand meta injection (favicon, apple-touch-icon via `injectBrandMeta()`)
- Hero watermark injection (`.lv-watermark` SVG in `.hero` sections)
- Author avatar replacement (LV Mark SVG in `.ia-author-avatar` elements)
- Scroll-to-top button
- Sponsor-ID auto-rewriting for all `neolifeshop.com` links

### Brand assets

All brand assets live in `assets/brand/` and originate from the master LV Mark SVG:

| Asset | Path | Purpose |
|---|---|---|
| LV Mark (inline SVG) | Injected via `nav.js` / `footer.js` / `components.js` | Primary brand symbol |
| Favicon | `assets/brand/favicon.svg` | Browser tab icon |
| Apple Touch Icon | `assets/brand/apple-touch-icon.png` | iOS home screen icon |
| Hero Watermark | `assets/brand/hero-watermark.svg` | Background watermark on hero sections |
| Brand OG Image | `assets/brand/og-brand.png` | Default Open Graph social share image |

### Routing pattern

- Root-level `.html` files are served directly by Cloudflare Pages Pretty URLs (no rewrite needed).
- Pages in `content/articles/` are served via 200-rewrites in `_redirects`:

```
/slug  /content/articles/slug  200
```

---

## Current Platform Status

| Component | Status |
|---|---|
| **Design system** | ✅ Complete — `pillar.css` on all pages |
| **Brand System** | ✅ Complete — `assets/brand/` with LV Mark, favicon, apple-touch-icon, hero-watermark, brand OG |
| **Navigation system** | ✅ Complete — `nav.js` on all root pages |
| **Footer system** | ✅ Complete — `footer.js` on all root pages |
| **Shared components** | ✅ Complete — `components.js` with brand injectors, sponsor-ID rewriting, scroll-to-top |
| **Open Graph** | ✅ Complete — brand OG image on all root pages; product-specific OG on product subdirectories |
| **Audit system** | ✅ Operational — `audit_pillar_page.py` for pillar pages |
| **Documentation system** | ✅ Operational — `PROJECT-STATUS.md`, `CURRENT-SPRINT.md`, `docs/sprints/`, `docs/reports/` |
| **Sprint workflow** | ✅ Operational — sprint-based cadence |
| **Autonomous execution** | ✅ Operational — AI executes routine work without manual approval |
| **Deployment pipeline** | ✅ Operational — Cloudflare Pages auto-deploys on `git push` |

---

## AI Session Workflow

Every AI implementation session follows this workflow:

1. Read PROJECT-ENTRY.md
2. Read PROJECT-STATUS.md
3. Read CURRENT-SPRINT.md
4. Read DECISIONS.md
5. Load all required project skills
6. Verify before implementing
7. Complete the sprint
8. Update documentation
9. Commit
10. Push

Routine implementation decisions should be made autonomously.

Ask the user only when business, branding, legal, SEO strategy or content strategy decisions are required.

---

## Repository state

The repository is the authoritative source for current page counts.

### File structure

```
levnytt-site/
├── index.html                           ← Homepage (pillar)
├── *.html                               ← root-level pages
├── content/
│   ├── articles/                        ← informational articles (served via _redirects)
│   └── products/entities/                  ← Product Entity System (5 Wave 1 entities, Sprint 13)
├── neolife-kosttillskott/index.html     ← Hub page
├── neolife-fibre-tablets/index.html     ← Product subdir page
├── neolife-sustained-vitamin-c/index.html ← Product subdir page
├── images/                              ← product and editorial images
├── assets/
│   └── brand/                           ← Brand System assets (LV Mark, favicon, OG, watermark)
├── nav.js                               ← Site-wide navigation
├── footer.js                            ← Site-wide footer
├── components.js                        ← Brand injectors + sponsor-ID rewriting + scroll-to-top
├── pillar.css                           ← Shared design system
├── levnytt-se-master-template.html      ← Dev template (not a public page)
├── _redirects                           ← Cloudflare routing rules
├── robots.txt
├── sitemap.xml                          ← hand-maintained URL index
└── 404.html                             ← noindex, custom error page
```

### Content generation pipeline

1. **Search Gap Research** discovers keyword opportunities (via `search-gap-research` skill)
2. **Informational Article** generates publish-ready HTML (via `informational-article` skill)
3. **Publication Agent** deploys articles from `content/articles/` to root-level pages (via PA rules)
4. **Pillar Page Template** creates or migrates pillar/product pages (via `pillar-page-template` skill)

5. **Brand System** provides shared branding to both pillar pages and Publication Agent article outputs
---

## Completed milestones

| Milestone | Description | Date |
|---|---|---|
| Hosting migration | Netlify → Cloudflare Pages | 2026-06-20 |
| Audit A1–A3 | Critical fixes: canonicals, nutriance-organic 404 redirect, nav.js dedup | Jun 2026 |
| Wave B1–B9 | All pillar pages → 13/13 audit score | Jun 2026 |
| Nav migration | All pages migrated from hardcoded nav to `nav.js` + `footer.js` | Jun 2026 |
| Sitemap expansion | Sitemap expanded; all production pages covered | Jun 2026 |
| Author photo | Emoji avatar replaced with real photo across all linked pages | Jun 2026 |
| Wave 3A | A batch of vitamin product pages migrated to production standard | Jun 2026 |
| New articles | Batch of informational articles in new niches | Jun 2026 |
| Wave 3B / Sprint 6 | All informational articles migrated to production standard | Jun 2026 |
| Sprint 6.1 | Google Fonts links added; canonical URLs corrected | Jun 2026 |
| Sprint 7 | `neolife-formula-iv` pillar upgrade + Affärsmöjlighet 2.0 | Jun 2026 |
| Sprint 8 — Brand System | `neolife-tre-en-en` pillar, `assets/brand/` directory, brand injectors, pillar.css consolidation | Jun 2026 |
| Sprint 9 — Brand Rollout | Brand OG image deployed to all root pages + source articles; `#site-nav` on all root pages; subdirectory consistency | Jun 2026 |
| Sprint 10 — Documentation | Full documentation baseline: PROJECT-STATUS, CURRENT-SPRINT, DECISIONS, PROJECT-ENTRY, SPRINT-9 report | Jun 2026 |

---

## Next Development Priorities

### Priority 1 — New high-value content
- New pillar pages (e.g. `/neolife-sport/`)
- New informational articles in uncovered niches
- Expand the existing article clusters

### Priority 2 — Product Entity System
- Build out structured product data via `content/products/` schema
- Link product pages to their entity definitions

### Priority 3 — Interactive tools
- Comparison pages (e.g. Omega-3 sources comparison)
- Calculators (e.g. daily nutrient intake)
- Interactive decision guides

### Priority 4 — Performance & accessibility
- Image optimization and lazy loading audit
- Core Web Vitals tuning
- Accessibility improvements (contrast checks, ARIA labels, keyboard navigation)
- Trailing-slash canonical cleanup

---

## Current Milestone

Sprint 10 — Documentation & Baseline Update

Primary objective:

- Bring all project documentation in sync with the current repository state
- Document Sprint 8 and Sprint 9 architectural decisions in DECISIONS.md
- Create Sprint 9 summary report
- Validate documentation for outdated, duplicate, or obsolete files

The Brand System integration (Sprint 8) and Brand Rollout (Sprint 9) are complete.

All root pages now share:
- `pillar.css` (shared design system with brand CSS variables)
- `nav.js` / `footer.js` / `components.js` with `defer`
- Brand meta injection (favicon, apple-touch-icon)
- Brand OG image (`assets/brand/og-brand.png`)
- `#site-nav` placeholder
- Verification meta tags (Google + Pinterest)
- Google Fonts (Playfair Display + Inter)

---

See `CURRENT-SPRINT.md` for active sprint status.
