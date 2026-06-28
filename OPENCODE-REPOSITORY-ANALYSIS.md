## Architecture Summary

**LevNytt.se** is a hand-authored vanilla HTML/CSS/JS static site deployed to **Cloudflare Pages** via Git push — no build framework, no npm, no Astro, no transpilation.

| Layer | Technology |
|---|---|
| Pages | ~70 raw `.html` files |
| Styling | `pillar.css` (shared design system) + legacy inline `<style>` blocks |
| Components | `nav.js`, `footer.js`, `components.js` (self-injecting IIFEs) |
| Routing | Cloudflare Pages + `_redirects` file |
| SEO | Hand-maintained `sitemap.xml`, JSON-LD schemas per page |
| Language | Swedish (sv-SE), NeoLife supplement affiliate/distributor site |
| Images | JPEG/PNG/WebP in `/images/`, generated via KIE.ai GPT Image 2 API |

The site has **two page tiers**:
1. **Pillar pages** (13 named) — brand/product authority pages, highest SEO priority
2. **Informational articles** (~55 pages) — "Vad är X / Varför X / X vs Y" format articles for organic search

---

## Current Sprint Objective

The project has been executing a structured **pillar-page migration wave system**:

- **Wave B** (completed): All 13 named pillar pages brought to 13/13 audit score — migrated to `pillar.css`, removed inline `:root` token blocks, added OG images, added responsive breakpoints
- **Wave 3A** (completed, latest commit `f45c9e5`): 5 vitamin product pages migrated to production standard

The sprint objective implied by the roadmap is: **systematically migrate all remaining informational article pages to production standard, and build out the missing pillar pages** listed in `LEVNYTT-MUISTIO.md`.

---

## Highest-Priority Implementation Task

**Migrate the three `content/articles/` authority pages (`var-metod`, `forsknings-faq`, `levnytt-principer`) to full pillar.css standard — but this is already done** (commits B1–B3). The audit issues from June 23 have been resolved.

The single highest-priority remaining task is:

### Add the missing ~27 informational articles to `sitemap.xml`

**Why this is #1:**

From `AUDIT-REPORT.md §D5`, approximately 27 pages are live and indexed by Google but absent from `sitemap.xml`. This includes product informational articles like `neolife-coq10`, `neolife-vitamin-d`, `neolife-formula-iv`, `neolife-elevate`, `neolife-chelated-zinc`, and skincare cluster articles (`retinol-pa-sommaren`, `vad-ar-niacinamid`, `hudtecken-naringsbrist`, etc.).

- These pages **exist**, are **already linked from nav.js**, and receive traffic — but Google has no sitemap signal to prioritize crawling them
- The sitemap was updated from 38 → 67 URLs in a prior commit, but the audit explicitly notes that a large cohort of informational articles is still missing
- The `LEVNYTT-MUISTIO.md` roadmap's "future pages" (Tre-en-en pillar, Formula IV pillar, CoQ10, Elevate, UpBeet) cannot be prioritized until the current live pages are properly indexed
- This is a pure SEO leverage task with zero risk of regressions — no page content is touched, only `sitemap.xml` is updated

**Specific files to add**: the 21 root-level informational articles and 6 `content/articles/` files identified in Audit §D5 that are currently absent from `sitemap.xml`.
