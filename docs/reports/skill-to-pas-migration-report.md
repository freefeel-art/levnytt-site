# Skill-to-PAS Migration Report — Component Adaptation Map

**Date:** 2026-07-01
**Scope:** All divergences between the original Informational Article Skill CSS/HTML/components and the current LevNytt PUBLICATION-ARTICLE-STANDARD.md
**Purpose:** Prescriptive reference for LevNytt Writer adapters — not a recommendation, not a suggestion

---

## 1. Color Palette Migration

Every color value that appears in the original skill's inline CSS must be replaced with the LevNytt brand color. The original uses a navy/coral palette; the Publication Standard uses a green/gold palette.

| Original Hex | Original Use | Replaced By | LevNytt Use |
|---|---|---|---|
| `#0F1B3A` | Hero bg, SVG container bg, section bg | `#1B4332` | Hero/header bg, dark section bg |
| `#18274b` | `.ia-takeaways` background | `#1B4332` | `.ia-takeaways` background |
| `#faf6f0` | `.ia-punchline` background | `#F9F6EF` | `.ia-punchline` background |
| `#faf4e6` | `.ia-takeaways` text, stat bg | `#F9F6EF` | `.ia-takeaways` text, stat-card bg, callout bg |
| `#F25F4C` | Punchline border, SVG title, accent line | `#C9A84C` | Punchline border, all accent elements |
| `#ff3020` | `.ia-punchline` border-left | `#C9A84C` | `.ia-punchline` border-left |
| `#e4b257` | `.ia-takeaways h3` color | `#C9A84C` | `.ia-takeaways h3` color, `.ia-cta h3` color |
| `#0f0f12` | `.ia-punchline` text color | `#1B4332` | `.ia-punchline` text color |
| `#FAF4E6` | Stat infographic numbers, SVG text | `#F9F6EF` | Stat infographic numbers, light text |
| `#6FA8FF` | Stat infographic labels, SVG notes | (unchanged) | (infographic-specific, not CSS) |
| `#9fc4ff` | SVG `.r-note` fill | (unchanged) | (SVG-specific, not in PAS) |

---

## 2. CSS Rule Migrations — Exact Value Changes

### 2.1 `.ia-wrap` — Content Wrapper

| Property | Original Skill | Publication Standard |
|---|---|---|
| `max-width` | _not defined in original_ | `760px` |
| `margin` | _not defined_ | `0 auto` |
| `padding` | _not defined_ | `0 20px` |
| `font-family` | _not defined_ | `Inter, system-ui, sans-serif` |
| `color` | _not defined_ | `#1a1a1a` |
| `line-height` | _not defined_ | `1.65` |

**Action:** Add all declarations from PAS. Original skill delegates wrapper styling to host pages; LevNytt must inline it.

### 2.2 `.ia-wrap h1` — Primary Heading

| Property | Original Skill | Publication Standard |
|---|---|---|
| `font-family` | _not defined_ | `"Playfair Display", Georgia, serif` |
| `font-size` | _not defined_ | `2.1em` |
| `line-height` | _not defined_ | `1.2` |
| `color` | _not defined_ | `#1B4332` |
| `margin` | _not defined_ | `0.6em 0 0.4em` |

**Action:** Add entire rule block. Original skill has no H1 styling — it relies on WordPress theme.

### 2.3 `.ia-wrap h2` — Section Heading

| Property | Original Skill | Publication Standard |
|---|---|---|
| `font-family` | _not defined_ | `"Playfair Display", Georgia, serif` |
| `font-size` | _not defined_ | `1.5em` |
| `color` | _not defined_ | `#1B4332` |
| `margin` | _not defined_ | `1.6em 0 0.6em` |

**Action:** Add entire rule block.

### 2.4 `.ia-wrap h3` — Subsection Heading

| Property | Original Skill | Publication Standard |
|---|---|---|
| `font-size` | _not defined_ | `1.15em` |
| `color` | _not defined_ | `#1B4332` |
| `margin` | _not defined_ | `1.2em 0 0.5em` |

**Action:** Add entire rule block. Critical for cascade: `.ia-wrap h3` (0,1,1) affects all H3s inside the article wrap, including those in dark-background blocks — specificity rules below.

### 2.5 `.ia-punchline` — Value Proposition Block

| Property | Original Skill | Publication Standard |
|---|---|---|
| `font-size` | `1.35em` | `1.3em` |
| `font-weight` | `600` | `600` _(unchanged)_ |
| `border-left` | `4px solid #ff3020` | `4px solid #C9A84C` |
| `padding` | `18px 22px` | `18px 22px` _(unchanged)_ |
| `background` | `#faf6f0` | `#F9F6EF` |
| `margin` | `24px 0` | `24px 0` _(unchanged)_ |
| `border-radius` | `0 6px 6px 0` | `0 6px 6px 0` _(unchanged)_ |
| `color` | `#0f0f12` | `#1B4332` |

**Action:** Replace 4 values: `font-size`, `border-left-color`, `background`, `color`.

### 2.6 `.ia-takeaways` — Key Takeaways Block

| Property | Original Skill | Publication Standard |
|---|---|---|
| `background` | `#18274b` | `#1B4332` |
| `color` | `#faf4e6` | `#F9F6EF` |
| `border-radius` | `10px` | `10px` _(unchanged)_ |
| `padding` | `22px 26px` | `22px 26px` _(unchanged)_ |
| `margin` | `26px 0` | `26px 0` _(unchanged)_ |

**Action:** Replace `background` and `color`.

### 2.7 `.ia-wrap .ia-takeaways h3` — Takeaways Heading

| Property | Original Skill | Publication Standard |
|---|---|---|
| `margin` | `0 0 14px` | `0 0 14px` _(unchanged)_ |
| `color` | `#e4b257` | `#C9A84C` |
| `font-size` | `1.05em` | `1.05em` _(unchanged)_ |
| `letter-spacing` | `0.04em` | `0.04em` _(unchanged)_ |
| `text-transform` | `uppercase` | `uppercase` _(unchanged)_ |
| `font-weight` | `700` | `700` _(unchanged)_ |

**Action:** Replace `color`. Specificity must stay at `.ia-wrap .ia-takeaways h3` (0,2,1).

### 2.8 `.ia-takeaways li` — Takeaways List Items

| Property | Original Skill | Publication Standard |
|---|---|---|
| `margin` | `8px 0` | `9px 0` |
| `color` | `#faf4e6` | `#F9F6EF` |

**Action:** Replace both values. Margin changes from 8px to 9px.

### 2.9 `.ia-takeaways ul` — Takeaways List

| Property | Original Skill | Publication Standard |
|---|---|---|
| `color` | `#faf4e6` | `#F9F6EF` |

**Action:** Replace color.

### 2.10 `.ia-takeaways a` — Takeaways Links

| Property | Original Skill | Publication Standard |
|---|---|---|
| `color` | `#ffd47a` | `#ffd47a` _(unchanged)_ |
| `text-decoration-color` | `#ffd47a` | `#ffd47a` _(unchanged)_ |

**Action:** None — unchanged. Note: `#ffd47a` is the one color from original skill that persists.

### 2.11 Evidence Tier Labels — `.ia-evidence-label`, `.ia-ev-t1`–`t4`

**NO CHANGES.** The original skill's evidence tier colors match PAS exactly:

| Class | Original | PAS | Match? |
|---|---|---|---|
| `.ia-ev-t1` | `#1a3a2a` / `#4ade80` | `#1a3a2a` / `#4ade80` | ✅ |
| `.ia-ev-t2` | `#1a2e3a` / `#60a5fa` | `#1a2e3a` / `#60a5fa` | ✅ |
| `.ia-ev-t3` | `#2e2a1a` / `#fbbf24` | `#2e2a1a` / `#fbbf24` | ✅ |
| `.ia-ev-t4` | `#2a1a1a` / `#f87171` | `#2a1a1a` / `#f87171` | ✅ |

### 2.12 `.ia-stat-grid` + `.ia-stat-card` — Stat Cards

| Property | Publication Standard | Note |
|---|---|---|
| `.ia-stat-grid` `display:grid;...gap:14px;margin:26px 0` | Defined in PAS | **New** — not in original skill |
| `.ia-stat-card` `background:#F9F6EF;border:1px solid #e3dcc9...` | Defined in PAS | **New** |
| `.ia-stat-card .num` `color:#1B4332;font-size:1.7em...` | Defined in PAS | **New** |
| `.ia-stat-card .lbl` `font-size:0.85em;color:#444` | Defined in PAS | **New** |
| `.ia-stat-card .src` `font-size:0.75em;color:#888` | Defined in PAS | **New** |

**Action:** Add 5 new CSS rule blocks. Original skill only describes stat cards conceptually.

### 2.13 `.ia-method-table` — Comparison Tables

| Property | Publication Standard | Note |
|---|---|---|
| `width:100%;border-collapse:collapse;margin:24px 0;font-size:0.92em` | Defined in PAS | **New** |
| `th,td{border:1px solid #e3dcc9;padding:10px 12px...}` | Defined in PAS | **New** |
| `th{background:#1B4332;color:#F9F6EF}` | Defined in PAS | **New** |
| `tr:nth-child(even){background:#F9F6EF}` | Defined in PAS | **New** |

**Action:** Add 4 new CSS rule blocks.

### 2.14 `.ia-callout` — Info Callout Box

| Property | Publication Standard | Note |
|---|---|---|
| `background:#F9F6EF;border:1px solid #e3dcc9;border-radius:8px;padding:16px 20px;margin:22px 0` | Defined in PAS | **New** |
| `.ia-callout h4{margin:0 0 8px;color:#1B4332;font-size:1em}` | Defined in PAS | **New** |

**Action:** Add 2 new CSS rule blocks.

### 2.15 `.ia-faq` + `details`/`summary`

| Property | Publication Standard | Note |
|---|---|---|
| `.ia-faq details{border-bottom:1px solid #e3dcc9;padding:14px 0}` | Defined in PAS | **New** |
| `.ia-faq summary{font-weight:600;cursor:pointer;color:#1B4332}` | Defined in PAS | **New** |
| `.ia-faq p{margin:10px 0 0}` | Defined in PAS | **New** |

**Action:** Add 3 new CSS rule blocks. Original skill describes FAQ conceptually but provides no CSS.

### 2.16 `.ia-tierbox` + `.ia-tier` — Tier Callout Box

| Property | Publication Standard | Note |
|---|---|---|
| `.ia-tierbox{display:flex;gap:12px;flex-wrap:wrap;margin:30px 0}` | Defined in PAS | **New** |
| `.ia-tier{flex:1 1 150px;background:#1B4332;color:#F9F6EF;border-radius:8px;padding:14px 16px;text-decoration:none;font-size:0.9em}` | Defined in PAS | **New** |
| `.ia-tier b{color:#C9A84C;display:block;font-size:0.8em;letter-spacing:0.05em;margin-bottom:4px}` | Defined in PAS | **New** |

**Action:** Add 3 new CSS rule blocks. Original skill has no tier box CSS.

### 2.17 `.ia-cta` — CTA Block

| Property | Publication Standard | Note |
|---|---|---|
| `.ia-cta{background:#1B4332;color:#F9F6EF;border-radius:10px;padding:24px 26px;margin:30px 0;text-align:center}` | Defined in PAS | **New** |
| `.ia-wrap .ia-cta h3{color:#C9A84C;margin-top:0}` | Defined in PAS | **New** |
| `.ia-cta a{color:#F9F6EF;background:#C9A84C;padding:10px 20px;border-radius:6px;text-decoration:none;display:inline-block;margin-top:10px;font-weight:600}` | Defined in PAS | **New** |

**Action:** Add 3 new CSS rule blocks.

### 2.18 `.ia-author-box` + `.ia-author-avatar`

| Property | Publication Standard | Note |
|---|---|---|
| `.ia-author-box{display:flex;gap:16px;align-items:flex-start;background:#F9F6EF;border-radius:10px;padding:20px;margin:34px 0}` | Defined in PAS | **New** |
| `.ia-author-avatar{width:48px;height:48px;border-radius:50%;background:#1B4332;color:#C9A84C;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0}` | Defined in PAS | **New** |

**Action:** Add 2 new CSS rule blocks.

### 2.19 `.ia-disclosure` — Disclosure Paragraphs

| Property | Publication Standard | Note |
|---|---|---|
| `font-size:0.82em;color:#666;border-top:1px solid #e3dcc9;padding-top:16px;margin-top:30px` | Defined in PAS | **New** |

**Action:** Add 1 new CSS rule block.

### 2.20 Inline-SVG Container — `.ia-risk-svg`

| Property | Original Skill | Publication Standard |
|---|---|---|
| `background` | `#0F1B3A` | `#1B4332` |

**Action:** Replace background color. PAS doesn't explicitly define this class — it should use the brand green.

---

## 3. New Mandatory Components (Not In Original Skill)

These components exist in PAS but are entirely absent from the original skill. Every one must be added to every LevNytt article output.

### 3.1 HTML Shell — Document Head

| Component | Original Skill | PAS Required |
|---|---|---|
| `lang="sv"` on `<html>` | No (generic) | Yes — always |
| `google-site-verification` meta | No | Yes — verbatim content |
| `p:domain_verify` meta (Pinterest) | No | Yes — verbatim content |
| `<meta name="robots">` | No | Yes — `index, follow, max-snippet:-1...` |

### 3.2 Open Graph Metas

| Meta | Original Skill | PAS Required |
|---|---|---|
| `og:type` | Described but generic | `"article"` — specific value required |
| `og:locale` | Not mentioned | `"sv_SE"` — always |
| `og:site_name` | Not mentioned | `"LevNytt"` — always |
| `og:image` | API URL, needs publish-time swap | `https://levnytt.se/assets/brand/og-brand.png` |
| `og:image:width` | Not mentioned | `"1200"` |
| `og:image:height` | Not mentioned | `"630"` |
| `og:image:alt` | Not mentioned | `"LevNytt — En oberoende NeoLife-distributör"` |

### 3.3 Twitter Card Metas

| Meta | Original Skill | PAS Required |
|---|---|---|
| `twitter:card` | Generic | `"summary_large_image"` |
| `twitter:title` | Generic | Present |
| `twitter:description` | Generic | Present |

### 3.4 Fonts

| Component | Original Skill | PAS Required |
|---|---|---|
| Google Fonts preconnect | Not included | 2 `<link rel="preconnect">` tags |
| Playfair Display | Not included | 400, 600, 700 |
| Inter | Not included | 300, 400, 500, 600 |
| Font weights | Not specified | Exact weights (no 800 Playfair, no 700/800 Inter) |

### 3.5 Shared Site Infrastructure

| Component | Original Skill | PAS Required |
|---|---|---|
| `pillar.css` link | No (self-contained) | `<link rel="stylesheet" href="/pillar.css">` before inline `<style>` |
| `#site-nav` div | No | `<div id="site-nav"></div>` first in body |
| `nav.js` script | No | `<script src="/nav.js" defer>` right after #site-nav |
| `footer.js` script | No | `<script src="/footer.js" defer>` before `</body>` |
| `components.js` script | No | `<script src="/components.js" defer>` before `</body>` |

**Critical:** The original skill produces fully self-contained HTML. The PAS expects shared site infrastructure. The Writer must inject these 6 elements into every output.

### 3.6 Content Structure Additions

| Component | Original Skill | PAS Required |
|---|---|---|
| Category label `<p>` | No | `<p style="font-size:0.85em;color:#888;text-transform:uppercase;letter-spacing:0.05em">CATEGORY</p>` — first in article body |
| `.ia-eyebrow` | No | `<div class="ia-eyebrow">Kosttillskott · Forskning</div>` — after category label |
| Author byline format | Generic: "Author byline + reviewer byline" | Exact: `<p>Av <a ...>Name</a> · Senast uppdaterad: MONTH YEAR · X min läsning</p>` |
| Method note | Generic "methodology note" | `<div class="ia-method-note"><strong>Metod:</strong> ...</div>` |
| Tier box (4 links) | No | `<div class="ia-tierbox">` with exactly 4 `<a class="ia-tier">` |
| CTA block | Generic "single conversion box" | `<div class="ia-cta">` with `<h3>`, `<p>`, `<a>`, optional `.ia-cta-secondary` |
| Author box | Not specified | `<div class="ia-author-box"><div class="ia-author-avatar">XX</div>...` |
| Disclosure (methodology) | Generic | `<p class="ia-disclosure"><strong>Metodnotering:</strong> ...</p>` |
| Disclosure (legal) | No | `<p class="ia-disclosure">LevNytt.se är en oberoende NeoLife...</p>` — verbatim text |

### 3.7 JSON-LD Schema Differences

| Field | Original Skill | PAS Required |
|---|---|---|
| `publisher` | Generic `SITE_NAME` | `"name": "LevNytt", "url": "https://levnytt.se"` |
| `mainEntityOfPage` | Not included | `{"@type":"WebPage","@id":"https://levnytt.se/slug"}` |
| Single `<script>` block | Mentioned but not enforced | Single `<script>` containing one `@graph` array |

---

## 4. Forbidden Components (Remove From Output)

These appear in the original skill's patterns but must NEVER appear in LevNytt output. PAS sections "Legacy Components (Do Not Use)" and "Forbidden CSS Classes" list them exhaustively.

### 4.1 Element-Level Forbiddens

| Pattern | Original Skill Context | PAS Status |
|---|---|---|
| `<footer>` element | "No `<footer>` element inside the article body" (original also forbids) | ✅ Already forbidden |
| Mid-article popup / JS gate | Original also forbids | ✅ Already forbidden |
| "Related Articles" link dump | Original also forbids | ✅ Already forbidden |
| Calculator widget | Original also forbids (review-article pattern) | ✅ Already forbidden |

### 4.2 Class-Level Forbiddens (Must Be Stripped)

From PAS Section "Forbidden CSS Classes":

`.freshness-banner`, `.hero`, `.hero-overlay`, `.hero-content`, `.hero-stats`, `.hero-stat`, `.back-link-wrapper`, `.back-link`, `.breadcrumbs`, `.authority-nav`, `.authority-nav-label`, `.journey-block`, `.journey-steps`, `.tier-section`, `.tier-label`, `.tier-grid`, `.tier-box`, `.tier-box-label`, `.tier-box-title`, `.callout-gold`, `.cta-block`, `.cta-btn`, `.article-wrap`, `.article-body`, `.article-content`, `.article-inner`, `.container`, `.stats-row`, `.stats-grid`, `.stat-number`, `.stat-label`, `.stat-source`, `.author-box`, `.author-avatar`, `.author-label`, `.author-info`, `.method-note`, `.last-updated`, `.faq-section`, `.faq-answer`, `.faq-body`, `.toc`

### 4.3 Non-`ia-*` Class Forbiddens (Test-Run Discovery)

These class names were used by the V1.0 test run and must be rejected:

| Wrong (V1.0) | Correct (PAS) |
|---|---|
| `punchline` | `ia-punchline` |
| `takeaway-box` | `ia-takeaways` |
| `cta-box`, `cta-button` | `ia-cta` |
| `disclosure-box`, `final-disclosure` | `ia-disclosure` |
| `author-box`, `author-avatar`, `author-info` | `ia-author-box`, `ia-author-avatar` |
| `faq-item`, `faq-answer` | `ia-faq` (wrapper) + `<details><summary>` |
| `callout` | `ia-callout` |
| `stat-card`, `number`, `stat-label`, `stat-source` | `ia-stat-card`, `.num`, `.lbl`, `.src` |
| `tierbox`, `tierbox-item`, `tier-label` | `ia-tierbox`, `ia-tier` |
| `eyebrow`, `category-label` | `ia-eyebrow` |
| `method-note` | `ia-method-note` |
| `evidence-tier tier-t1` | `ia-evidence-label ia-ev-t1` |
| `credentials`, `author-link` | `ia-author-box` child content (no separate classes needed) |
| `category-label` (as class) | Plain `<p>` inline style (no class) |

---

## 5. Image/Visual Asset Changes

### 5.1 Hero Image

| Parameter | Original Skill | PAS/Brand |
|---|---|---|
| Background | Dark navy `#0F1B3A` | Deep green `#1B4332` |
| Accent line | Coral `#F25F4C` | Gold `#C9A84C` |
| Headline color | Coral serif | Gold or cream serif |

**Action:** Update GPT Image 2 prompt to use `#1B4332` background, `#C9A84C` accent.

### 5.2 Stats Infographic

| Parameter | Original Skill | PAS/Brand |
|---|---|---|
| Background | Dark navy `#0F1B3A` | Deep green `#1B4332` |
| Number color | Cream `#FAF4E6` | Cream `#F9F6EF` |
| Label color | Light blue `#6FA8FF` | Light blue `#6FA8FF` (unchanged) |

### 5.3 Image Policy

| Rule | Original Skill | LevNytt |
|---|---|---|
| AI product images | Not addressed | **Forbidden** — use official NeoLife images only |
| Hero image minimum | 3 images (hero + stats + comparison) | 2 minimum (hero + infographic) for health articles |
| Product visual preference | Not addressed | Official NeoLife product images > AI-generated |

---

## 6. Output Path Migration

| Aspect | Original Skill | LevNytt |
|---|---|---|
| Base directory | `[OUTPUT_DIR]/[slug]/` | `content/articles/[slug]/` |
| HTML file | `[slug].html` | `[slug].html` (same) |
| Images dir | `[slug]/images/` | `[slug]/images/` (same) |
| Config file | `[slug]/run-config.json` | `[slug]/run-config.json` (same) |
| Root writes | Permitted (self-contained) | **Forbidden** — Publication Agent only |

---

## 7. H1 Handling

| Aspect | Original Skill | LevNytt |
|---|---|---|
| H1 in output | Mandatory (v1.1) | Mandatory |
| WordPress strip | H1 stripped at WP publish | **No WP publish step** — H1 stays in production HTML |

---

## 8. Summary: Change Count

| Category | Count | Severity |
|---|---|---|
| CSS hex value changes | 14 | Blocking — wrong colors render |
| New CSS rule blocks to add | 29 | Blocking — unstyled components |
| Forbidden class names to reject | 44 | Blocking — pillar.css won't match |
| New mandatory HTML elements | 17 | Blocking — missing infrastructure (nav, footer, fonts) |
| New mandatory meta tags | 12 | High — missing OG/social/verification |
| Image prompt color changes | 4 | Medium — visual mismatch |
| Output path change | 1 | Medium — wrong directory |
| Evidence tier labels | 0 | ✅ No changes needed |
| FAQ structural concept | 0 | ✅ Pattern matches |
| Question H2s concept | 0 | ✅ Pattern matches |
| Schema concept | 0 | ✅ Pattern matches (with publisher additions) |

**Total adaptations required: ~121 individual changes across 8 categories.**
