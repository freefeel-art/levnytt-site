# PROJECT-STATUS.md
# LevNytt.se — Current Project Status

Last updated: 2026-06-28

See `PROJECT-ENTRY.md` for the reading order and workflow. See `DECISIONS.md` for engineering conventions.

---

## Site overview

**LevNytt.se** is a Swedish-language knowledge platform for NeoLife supplements and home care products. Its purpose is to drive organic search traffic and convert readers into NeoLife customers or distributors.

- **Live site:** https://levnytt.se/
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
| Styling | `pillar.css` (shared design system) + legacy inline `<style>` blocks on older pages |
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

Highest-priority SEO pages. All pass the 13/13 audit checklist as of 2026-06-28.

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

---

## Open backlog (no active sprint)

These items are documented but unscheduled. They become sprint candidates when the project owner opens a new sprint.

### 1. Future pillar pages

Pages that currently exist only as informational articles and are candidates for full pillar treatment:

| Current file | Target URL |
|---|---|
| `neolife-tre-en-en.html` | `/neolife-tre-en-en/` |
| `neolife-formula-iv.html` | `/formula-iv/` |
| `neolife-elevate.html` | `/neolife-elevate/` |
| `neolife-upbeet.html` | `/neolife-upbeet/` |
| `neolife-coq10.html` | `/neolife-coq10/` |
| `personlig-vard.html` | `/nutriance-organic/` (expansion pending) |
| *(does not exist)* | `/neolife-sport/` |

### 3. Trailing-slash canonical inconsistencies

Several root-level pages have a trailing-slash canonical but a non-trailing-slash sitemap entry (and vice versa). Functionally served correctly by Cloudflare Pretty URLs but technically inconsistent. Low urgency.

### 4. Product entity system

Only one product entity is defined (`content/products/entity_formula_iv/sv.json`). The system is nascent with no active development.

---

## Active sprint

See `CURRENT-SPRINT.md`.
