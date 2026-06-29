# PROJECT-STATUS.md — LevNytt.se Executive Dashboard

*Last updated: 2026-06-29 | See `PROJECT-ENTRY.md` for reading order. See `DECISIONS.md` for engineering conventions.*

---

## Executive Summary

| | |
|---|---|
| **Project** | LevNytt.se |
| **Mission** | Sweden's evidence-based NeoLife knowledge platform |
| **Status** | 🟢 Production Stable |
| **Phase** | Maintenance + Feature Development |
| **Public Pages** | 55 |
| **Audit Compliance** | 55 / 55 pages pass the 13/13 production audit |
| **Migration** | ✅ Complete |
| **Deployment** | Cloudflare Pages (automatic deployment) |
| **Next Focus** | Content Expansion & Feature Development |

---

## Project Health

| Status | Value |
|---|---|
| **Production** | ✅ Stable — live at https://levnytt.se/ |
| **Migration** | ✅ Complete — all pages at Gen 3 |
| **Public pages** | 55 |
| **Audit compliance** | 55 / 55 pages pass the 13/13 production audit |
| **Deployment** | Cloudflare Pages — automatic on `git push` |
| **Current phase** | Maintenance + Feature Development |

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
- **Skills are the implementation authority** — use the pillar-page-template skill for migrations, informational-article skill for new content
- **Verify before implementing** — audit every page before making changes
- **One completed page = one commit** — clean, atomic git history
- **Audit before and after every migration** — run `audit_pillar_page.py` on both sides
- **Prefer autonomous execution** — the AI should act on instructions without asking for permission on routine tasks
- **Ask only when business, branding, legal, SEO strategy or content strategy decisions are required** — the AI escalates these; everything else is routine

---

## Definition of Done

A page is considered complete only when:

- it passes the 13/13 production audit
- it follows the Gen 3 design system
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
| Styling | `pillar.css` (shared design system) + page-specific `<style>` blocks on select pages |
| Shared components | `nav.js`, `footer.js`, `components.js` — self-injecting IIFEs, loaded with `defer` |
| Routing | Cloudflare Pages "Pretty URLs" + `_redirects` file |
| SEO | Hand-maintained `sitemap.xml`, JSON-LD schemas per page |
| Hosting | Cloudflare Pages — auto-deploys on `git push` |
| Repository | GitHub: `freefeel-art/levnytt-site` |
| Images | JPEG/PNG/WebP in `/images/`. Hero images generated via KIE.ai GPT Image 2 API. |
| Fonts | Google Fonts CDN: Playfair Display (headings) + Inter (body) |

There is **no build step, no npm, no framework**. Files are deployed as-is.

### Design tokens (pillar.css)

| Token | Value |
|---|---|
| `--green-dark` | `#1B4332` |
| `--green` | `#2D6A4F` |
| `--gold` | `#C9A84C` |
| `--cream` | `#F9F6EF` |
| Max content width | `820px` |

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

`components.js` rewrites all `neolifeshop.com` links to include the sponsor ID automatically.

### Routing pattern for content/articles/

Pages in `content/articles/` are served via 200-rewrites in `_redirects`:

```
/forsknings-faq  /content/articles/forsknings-faq  200
```

Root-level `.html` files are served directly by Cloudflare Pages Pretty URLs (no rewrite needed).

---

## Current Platform Status

| Component | Status |
|---|---|
| **Design system** | ✅ Complete — `pillar.css` on all 55 pages |
| **Navigation system** | ✅ Complete — `nav.js` with defer on all pages |
| **Shared components** | ✅ Complete — `footer.js` + `components.js` with defer on all pages |
| **Audit system** | ✅ Operational — `audit_pillar_page.py` for all pages |
| **Documentation system** | ✅ Operational — `PROJECT-STATUS.md`, `CURRENT-SPRINT.md`, `docs/reports/` |
| **Sprint workflow** | ✅ Operational — sprint-based migration cadence |
| **Autonomous execution** | ✅ Operational — AI executes routine migrations without manual approval |
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

The repository is the authoritative source for current page counts. Run `find . -name "*.html" -not -path "./.git/*"` to enumerate all HTML files.

### File structure

```
levnytt-site/
├── index.html                           ← Homepage (pillar)
├── *.html                               ← root-level pages
├── content/
│   ├── articles/                        ← informational articles (served via _redirects)
│   └── products/entity_formula_iv/sv.json  ← Nascent product entity system (one entry defined)
├── neolife-kosttillskott/index.html     ← Hub page
├── neolife-fibre-tablets/index.html     ← Product subdir page
├── neolife-sustained-vitamin-c/index.html ← Product subdir page
├── images/                              ← product and editorial images
├── nav.js                               ← Site-wide navigation
├── footer.js                            ← Site-wide footer
├── components.js                        ← Sponsor-ID link rewriting + scroll-to-top
├── pillar.css                           ← Shared design system
├── levnytt-se-master-template.html      ← Dev template (not a public page)
├── _redirects                           ← Cloudflare routing rules
├── robots.txt
├── sitemap.xml                          ← hand-maintained URL index
└── 404.html                             ← noindex, custom error page
```

---

## Page taxonomy

### Tier 1: Pillar pages

Highest-priority SEO pages. All pass the 13/13 audit checklist as of 2026-06-29.

| Page | URL |
|---|---|
| Homepage | `/` |
| Kosttillskott hub | `/neolife-kosttillskott` |
| Historia | `/neolife-historia` |
| Vetenskap | `/neolife-vetenskap` |
| Hållbarhet | `/neolife-hallbarhet/` |
| Pro Vitality | `/neolife-pro-vitality` |
| Carotenoid Complex | `/neolife-carotenoid-complex` |
| Omega-3 Plus | `/neolife-omega-3-plus` |
| Golden Home Care | `/golden-home-care/` |
| Affärsmöjlighet | `/neolife-affarsmojlighet` |
| Om oss | `/om-oss` |
| Den fundersamma mannen | `/den-fundersamma-mannen` |
| Vår metod | `/var-metod` |
| Forsknings-FAQ | `/forsknings-faq` |
| LevNytt Principer | `/levnytt-principer` |
| Formula IV | `/neolife-formula-iv` |
| Tre-en-en | `/neolife-tre-en-en` |
| Elevate | `/neolife-elevate/` |
| UpBeet | `/neolife-upbeet` |
| CoQ10 | `/neolife-coq10` |
| Personlig vård (Nutriance Organic) | `/personlig-vard/` |

### Tier 2: Informational articles

Format: "Vad är X / Varför X / X vs Y / Hur X". Product explainers, science articles, skincare cluster, nutrition cluster, direct sales cluster. All in `sitemap.xml`.

### Special pages (not indexed)

- `404.html` — noindex, utility error page
- `levnytt-se-master-template.html` — dev template, not publicly linked

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
| Wave 3A | A batch of vitamin product pages migrated to production standard | Jun 2026, `f45c9e5` |
| New articles | `vad-ar-vitamin-b12`, `hur-fungerar-natverksmarknadsforing-egentligen`, `vad-ar-probiotika`, `vad-ar-kostfiber` | Jun 2026 |
| Wave 3B / Sprint 6 | All informational articles migrated to production standard: `pillar.css`, no inline `:root`, 3 breakpoints, `og:image`, `components.js` with `defer` | Jun 2026 |
| Sprint 6.1 | Google Fonts links added to 9 pages; canonical URLs corrected on 3 `content/articles/` pages | Jun 2026 |
| Sprint 7 | `neolife-formula-iv` upgraded to pillar status: verification meta tags added, cost CTA violation removed | Jun 2026 |
| Sprint 8 | `neolife-tre-en-en` upgraded to pillar status: OG/Twitter meta added, JSON-LD author fixed, breadcrumb fixed, cost violations removed | Jun 2026 |
| Sprint 9–12 | `neolife-elevate`, `neolife-upbeet`, `neolife-coq10`, `personlig-vard` upgraded to pillar status | Jun 2026 |
| Sprint 13 | `index.html` (front page) migrated from Gen 1 to Gen 3: `pillar.css`, no inline `:root`, `components.js` with defer, verification meta, `og:image`, 3+ breakpoints. Pre: 9/13 → Post: 13/13 | Jun 2026, `7a3d7cb` |
| Sprint 14 | `neolife-kosttillskott/index.html` migrated to Gen 3: defer added to components.js | Jun 2026, `3cafa90` |
| Sprint 15 | `neolife-pro-vitality.html` migrated to Gen 3: verification meta + components.js | Jun 2026, `e97fdad` |
| Sprint 16 | `neolife-carotenoid-complex.html` migrated to Gen 3: verification meta + components.js | Jun 2026, `098139e` |
| Sprint 17 | `neolife-omega-3-plus.html` migrated to Gen 3: verification meta + components.js | Jun 2026, `46192b6` |
| Sprint 18 | `neolife-historia.html` migrated to Gen 3: removed inline `:root`, defer to components.js | Jun 2026, `6bcb3b3` |
| Sprint 19 | `neolife-vetenskap.html` migrated to Gen 3: removed inline `:root`, defer to components.js | Jun 2026, `fa8ce83` |
| Sprint 20 | `neolife-hallbarhet.html` migrated to Gen 3: added pillar.css, og:image, removed inline `:root`/duplicate CSS | Jun 2026, `f970916` |
| Sprint 21 | `neolife-affarsmojlighet.html` migrated to Gen 3: removed inline `:root`, defer, page-specific og:image | Jun 2026, `cbd21c1` |
| Sprint 22 | `om-oss.html` migrated to Gen 3: added components.js, verification meta, page-specific og:image | Jun 2026, `24d5eac` |
| Sprint 23 | `golden-home-care.html` migrated to Gen 3: removed inline `:root`, defer, page-specific og:image | Jun 2026, `656a050` |
| Sprint 24 | `den-fundersamma-mannen.html` migrated to Gen 3: defer, page-specific og:image | Jun 2026, `935cf30` |
| Sprint 25 | `neolife-fibre-tablets/` migrated to Gen 3 (8/13→13/13): pillar.css, og:image, removed inline :root/footer CSS | Jun 2026, `ab9e13f` |
| Sprint 26 | `neolife-sustained-vitamin-c/` migrated to Gen 3 (8/13→13/13): same pattern as Sprint 25 | Jun 2026, `b9d14c4` |
| Sprint 27 | `integritetspolicy.html` migrated to Gen 3 (10/13→13/13): last Gen 1 page | Jun 2026, `b5196cc` |
| Sprint 28 | 30 Gen 2 pages: batch-added verification meta tags (google-site-verification + p:domain_verify) | Jun 2026 |
| **Gen 3 Migration Complete** | All 55 public pages at Gen 3 (13/13 audit). No remaining migration backlog. Project moves to Maintenance + Feature Development. | Jun 2026 |

---

## Success Metrics

| Metric | Value |
|---|---|
| **Public pages** | 55 |
| **Pillar pages** | 20 |
| **Informational articles** | 29 |
| **13/13 audit compliance** | 55 / 55 (100%) |
| **Gen 3 migration** | Complete — all pages migrated |
| **Documentation status** | Current |
| **Production status** | ✅ Stable — live at https://levnytt.se/ |

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

Phase 2 — Content Expansion & Topical Authority

Primary objectives:

- Expand the pillar page network.
- Publish high-quality informational articles.
- Build the Product Entity System.
- Improve internal linking and topical authority.
- Develop interactive tools and comparison pages.
- Continue improving performance, accessibility and user experience.

The Gen 3 migration project is complete.

Future development focuses on expanding the platform rather than rebuilding existing pages.

---

See `CURRENT-SPRINT.md` for active sprint status. See `docs/reports/SITE-PAGE-INVENTORY.md` for the full page inventory.
