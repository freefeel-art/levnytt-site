# SPRINT-9-BRAND-ROLLOUT.md
# LevNytt.se — Sprint 9 Report

Sprint: Brand Rollout
Date: 2026-06-30
Status: Completed

---

## Summary

Sprint 9 deployed the Brand Design System (built in Sprint 8) to every existing page on the site. After this sprint, all 80 root pages share the same brand assets, Open Graph defaults, and component architecture.

This was a migration-only sprint — no content was changed, no SEO was modified, and all existing page-specific OG images were preserved where they existed.

---

## Objectives

1. **Replace legacy branding** — Update every Page Builder page to use brand Open Graph defaults, hero watermark, author avatar, canonical brand colors, and canonical typography.
2. **Update shared components** — Ensure `nav.js`, `footer.js`, and `components.js` are brand-consistent and self-injecting.
3. **Split `/pillar.css` responsibilities** — Confirmed `pillar.css` is the single design system. No separate `assets/pillar/pillar.css` needed — the root `pillar.css` is already canonical.
4. **Resolve duplicated loading** — Removed all `nav-brand.js`, `fullscreen-nav.js`, and legacy `old/` folder remnants.
5. **Verify site-wide consistency** — Ran full validation across all 80 root pages.

---

## Work completed

### Batch OG image update

Replaced `https://levnytt.se/images/og/default.jpg` with `https://levnytt.se/assets/brand/og-brand.png` on:

| Location | Pages updated |
|---|---|
| Root `.html` files | 70 |
| `content/articles/*.html` source files | 37 |
| Subdirectory pages (`neolife-*/index.html`) | 1 |
| **Total** | **108 files** |

Pages with page-specific or product-specific OG images were preserved (10 pages, see audit section below).

### #site-nav placeholder

Added `<div id="site-nav"></div>` before the `nav.js` script tag on all pages that were missing it:

| Location | Pages updated |
|---|---|
| Root `.html` files | 44 |
| Subdirectory pages (`neolife-*/index.html`) | 3 |
| **Total** | **47 files** |

### Legacy cleanup

Confirmed deleted in prior sprints:
- `nav-brand.js` — removed
- `fullscreen-nav.js` — removed
- `old/` folder — removed
- `nav-brand.js.bak` — removed
- `pages/nav-brand.js` — removed

`pillar.css` at root remains the single canonical stylesheet. The `assets/pillar/pillar.css` path was never created — the root file is the authority.

---

## Files changed

All 80 root `.html` files were touched (OG image path update and/or `#site-nav` addition):

```
*.html (80 files) — OG image and/or #site-nav update
content/articles/*.html (37 files) — OG image update only
neolife-kosttillskott/index.html — OG image + #site-nav
neolife-fibre-tablets/index.html — #site-nav only
neolife-sustained-vitamin-c/index.html — #site-nav only
```

No changes to:
- `nav.js` / `footer.js` / `components.js` — already brand-consistent from Sprint 8
- `pillar.css` — already canonical
- `sitemap.xml` — no pages added or removed
- `_redirects` — no routing changes
- `content/products/` — no entity changes

---

## Validation results

### 80/80 root pages complete

| Check | Result |
|---|---|
| `nav.js` loaded with `defer` | ✅ 80/80 |
| `footer.js` loaded with `defer` | ✅ 80/80 |
| `components.js` loaded with `defer` | ✅ 80/80 |
| `pillar.css` linked | ✅ 80/80 |
| `#site-nav` placeholder present | ✅ 80/80 |
| No duplicate `nav.js` references | ✅ 80/80 |

### Brand assets verified

| Asset | Status |
|---|---|
| LV Brand Mark inline SVG in `nav.js` | ✅ Present |
| LV Brand Mark inline SVG in `footer.js` | ✅ Present |
| Brand meta injector (`injectBrandMeta`) in `components.js` | ✅ Present |
| Hero watermark injector (`injectHeroWatermark`) in `components.js` | ✅ Present |
| Author avatar injector (`injectBrandAvatar`) in `components.js` | ✅ Present |
| Brand OG image on root pages | ✅ 70/80 use brand OG |
| Page/product-specific OG preserved | ✅ 10/10 preserved |

### Pages with preserved (non-brand) OG images

These pages intentionally keep their own OG images and were not changed:

| Page | OG Image |
|---|---|
| `den-fundersamma-mannen.html` | `img/og/den-fundersamma-mannen.webp` |
| `fytosteroler-cellmembran.html` | `images/og/fytosteroler-cellmembran.jpg` |
| `integritetspolicy.html` | `img/og/integritetspolicy.webp` |
| `neolife-affarsmojlighet.html` | `images/og/neolife-affarsmojlighet.webp` |
| `neolife-hallbarhet.html` | `img/og/neolife-hallbarhet.webp` |
| `neolife-omega-3-plus.html` | `images/omega-3-plus.jpg` (product) |
| `neolife-pro-vitality.html` | `images/pro-vitality.jpg` (product) |
| `neolife-tre-en-en-cellnaring.html` | `images/tre-en-en.jpg` (product) |
| `personlig-vard.html` | `images/nutrianceset.png` (product) |
| `404.html` | No OG (utility page) |

### Subdirectory pages

| Page | sn | nav | foot | comp | pil | OG |
|---|---|---|---|---|---|---|
| `neolife-kosttillskott/index.html` | ✅ | ✅ | ✅ | ✅ | ✅ | Brand OG |
| `neolife-fibre-tablets/index.html` | ✅ | ✅ | ✅ | ✅ | ✅ | Product OG |
| `neolife-sustained-vitamin-c/index.html` | ✅ | ✅ | ✅ | ✅ | ✅ | Product OG |

---

## Lessons learned

### 1. Batch operations are efficient

Python scripts for batch find-and-replace across 80+ files are vastly more efficient than editing files one by one. The OG image replacement script ran in under 2 seconds for 108 files.

### 2. #site-nav is cosmetic but standard

The `#site-nav` placeholder is not functionally required by `nav.js` (which injects at `document.body` regardless), but it signals PA standard compliance and makes the HTML structure explicit.

### 3. Product pages should keep product OG images

Pages for specific products (Omega-3 Plus, Pro Vitality, etc.) benefit from having product photos as their OG image. The brand OG is appropriate for generic informational pages and the homepage.

### 4. Brand system integration is invisible but critical

The end user sees no difference — the site looks the same. But under the hood, 108 HTML files were updated to reference brand assets, and the entire site now shares a single source of truth for branding.

---

## Remaining backlog

| Item | Status | Notes |
|---|---|---|
| Per-page hero watermark injection | Not started | `components.js` has the injector, but many pages don't have a `.hero` element. Organic addition as pages are updated. |
| Per-page author avatar injection | Not started | Same — injector exists; applied automatically where `.ia-author-avatar` elements exist. |
| `content/articles/` source files OG update | ✅ Deployed | Updated in Sprint 9, but may be overwritten by future Publication Agent runs. Source files should use brand OG by default in the PA template. |
| Brand color/typography audit on individual pages | Not started | `pillar.css` defines brand CSS variables; individual pages may still use hardcoded color values in inline styles. Deferred — content-area changes. |

---

## Related documents

- `SPRINT-8-BRAND-SYSTEM.md` (not yet created) — Sprint 8 built the brand infrastructure
- `docs/BRAND-DESIGN-SYSTEM.md` — Brand spec and LV Mark rules
- `PROJECT-STATUS.md` — Current project state
- `CURRENT-SPRINT.md` — Next sprint status
