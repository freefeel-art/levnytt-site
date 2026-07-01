# Article Template Family Analysis — Sprint 7 Phase 2

**Date:** 2026-06-30
**Baseline:** Publication Agent (PA) ia-wrap template
**Objective:** Document every template family, compare against PA standard, recommend migration order

---

## Summary Table

| # | Template Family | Articles | PA Match | Complexity | Migration Priority |
|---|---|---|---|---|---|
| 0 | **Publication Agent (PA)** | 26 | 100% | Reference | Baseline |
| 1 | S1 — ia-wrap Compact | 8 | 55% | Low | **Phase 1** |
| 2 | S4 — naringsbrist-symptom | 1 | 35% | Medium | **Phase 2** |
| 3 | R2 — ia-wrap Legacy | 4 | 40% | Medium | **Phase 2** |
| 4 | R3 — PA-Close / Old Master | 2 | 50% | Medium | **Phase 3** |
| 5 | S2 — ia-wrap Large / Authority | 5 | 30% | Medium-High | **Phase 4** |
| 6 | R1 — Pillar Authority | 11 | 25% | High | **Phase 5** |
| 7 | S3 — Trust Architecture | 3 | 30% | High | **Phase 5** |
| 8 | R4 — Calculator Tool | 1 | 5% | Special | **Phase 6** |
| 9 | P1 — Historia/Vetenskap | 2 | 30% | Out of scope* | Separate sprint |
| 10 | P2 — Hallbarhet/Golden Home | 2 | 25% | Out of scope* | Separate sprint |
| 11 | P3 — Affarsmojlighet | 1 | 15% | Out of scope* | Separate sprint |
| 12 | P4 — Custom Isolated | 2 | 5% | Out of scope* | Separate sprint |
| 13 | PROD-A — Pillar Product | 20 | 15% | Separate family* | Separate sprint |
| 14 | PROD-B — Old-style Product | 5 | 20% | Separate family* | Separate sprint |

\* **Pillar and product pages** serve different purposes than informational articles. They use distinct template families and should be migrated in a separate sprint after article migration is complete. They are included here for completeness.

**Articles in migration scope: 35 informational articles** (families 1-8)
**Articles in separate template families: 32** (families 9-14 — pillar + product pages)

---

## Family 0: Publication Agent (PA) — Baseline

**Articles:** 26 (already compliant, not being migrated)
**PA match:** 100%

### Component inventory (reference standard)

#### Head
```
<!DOCTYPE html><html lang="sv">
<meta charset/>, <meta viewport/>, <title>Topic | LevNytt</title>
<meta description> (155 char)
<link canonical>
<meta og:type, og:title, og:description, og:url, og:site_name, og:image+dimensions>
<meta twitter:card, twitter:title, twitter:description>
<script> @graph { Article + FAQPage } JSON-LD
<link> Playfair Display 400/600/700 + Inter 300/400/500/600
<link href="/pillar.css">
<style> (inline ia-* CSS)
```

#### Body
```
<div id="site-nav"></div><script src="/nav.js" defer></script>
<div class="ia-wrap"><article>
  <p category-label> (grey, small, uppercase)
  <div class="ia-eyebrow">
  <h1>
  <p author byline> (Av Author · uppdaterad month year · X min)
  <p class="ia-punchline"> (bold claim, gold left border)
  <div class="ia-takeaways"><h3>Key Takeaways</h3><ul> (dark green box)
  <h2>, <h3>, <p>, <ul>, <ol> content sections
  <span class="ia-evidence-label ia-ev-t1|t2|t3|t4"> (evidence tier badges)
  <table class="ia-method-table"> (comparison tables)
  <div class="ia-stat-grid"><div class="ia-stat-card"> (2-col stats)
  <div class="ia-callout"><h4><p> (info callouts)
  <div class="ia-tierbox"><a class="ia-tier"> (4-tier internal links)
  <div class="ia-cta"><h3><p><a> (product CTA)
  <div class="ia-faq"><h2>Vanliga frågor</h2>
    <details><summary>Q</summary><p>A</p></details> (accordion FAQ)
  <div class="ia-method-note"> (methodology)
  <div class="ia-author-box"><div class="ia-author-avatar">XX</div> (author bio)
  <p class="ia-disclosure"> (LevNytt.se är en oberoende... border-top)
</article></div>
<script src="/footer.js" defer></script>
<script src="/components.js" defer></script>
```

#### CSS patterns (inline, extracted to pillar.css would eliminate ~80 lines per article)
```
.ia-wrap{max-width:760px;margin:0 auto;padding:0 20px}
.ia-wrap h1{font-family:"Playfair Display";font-size:2.1em;color:#1B4332}
.ia-wrap h2{font-size:1.5em;color:#1B4332;margin:1.6em 0 0.6em}
.ia-punchline{font-size:1.3em;border-left:4px solid #C9A84C;padding:18px 22px;background:#F9F6EF}
.ia-takeaways{background:#1B4332;color:#F9F6EF;border-radius:10px;padding:22px 26px}
.ia-takeaways h3{color:#C9A84C;text-transform:uppercase}
.ia-stat-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
.ia-stat-card{background:#F9F6EF;border:1px solid #e3dcc9;border-radius:8px;padding:16px}
.ia-method-table{width:100%;border-collapse:collapse}
.ia-method-table th{background:#1B4332;color:#F9F6EF}
.ia-method-table tr:nth-child(even){background:#F9F6EF}
.ia-callout{background:#F9F6EF;border:1px solid #e3dcc9;border-radius:8px;padding:16px 20px}
.ia-evidence-label{display:inline-block;font-size:0.72em;font-weight:700}
.ia-ev-t1{background:#1a3a2a;color:#4ade80}
.ia-ev-t2{background:#1a2e3a;color:#60a5fa}
.ia-ev-t3{background:#2e2a1a;color:#fbbf24}
.ia-ev-t4{background:#2a1a1a;color:#f87171}
.ia-faq details{border-bottom:1px solid #e3dcc9;padding:14px 0}
.ia-faq summary{font-weight:600;cursor:pointer;color:#1B4332}
.ia-tierbox{display:flex;gap:12px;flex-wrap:wrap;margin:30px 0}
.ia-tier{flex:1 1 150px;background:#1B4332;color:#F9F6EF;border-radius:8px;padding:14px}
.ia-cta{background:#1B4332;color:#F9F6EF;border-radius:10px;padding:24px 26px;text-align:center}
.ia-cta a{color:#F9F6EF;background:#C9A84C;padding:10px 20px;border-radius:6px}
.ia-author-box{display:flex;gap:16px;background:#F9F6EF;border-radius:10px;padding:20px}
.ia-author-avatar{width:48px;height:48px;border-radius:50%;background:#1B4332;color:#C9A84C}
.ia-disclosure{font-size:0.82em;color:#666;border-top:1px solid #e3dcc9;padding-top:16px}
@media(max-width:900px){}@media(max-width:768px){}@media(max-width:600px){}
```

#### JavaScript patterns
```
<div id="site-nav"></div>
<script src="/nav.js" defer></script>
... ia-wrap content ...
<script src="/footer.js" defer></script>
<script src="/components.js" defer></script>
```

#### Schema patterns
- Single `@graph` JSON-LD block containing `Article` + `FAQPage`
- No BreadcrumbList (PA articles do not include BreadcrumbList schema)
- Author: `{"@type": "Person", "name": "..."}`
- Publisher: `{"@type": "Organization", "name": "LevNytt"}`

#### CSS approach
- `<link href="/pillar.css">` for base design system
- `<style>` with inline ia-* classes (~60-90 lines)
- No inline :root tokens (uses pillar.css variables)
- Fonts: Playfair Display 400/600/700 + Inter 300/400/500/600

#### Key differences from legacy `levnytt-se-master-template.html` (now removed)
- **No freshness banner**
- **No gradient hero** (flat header)
- **No back-link**
- **No article-content/article-inner** (uses ia-wrap)
- **No TOC**
- **No gold conclusion callout**
- **No itemscope FAQ** (uses details/summary accordion)
- **No smooth scroll script** (CSS only)
- **No inline footer CSS** (footer.js only)
- **No BreadcrumbList schema**
- **No inline Google verification metas**
- Additions: author box, CTA block, tierbox, evidence labels, disclosure

---

## Family 1: S1 — ia-wrap Compact

**Articles:** 8
**Location:** `content/articles/` (not yet published to root)
**PA match:** 55%
**Complexity:** Low

### Articles
1. `ar-miljovanliga-rengoringsmedel-lika-effektiva.html` (188 lines)
2. `c-vitamin-tillskott-vs-serum-huden.html` (217 lines)
3. `hudtecken-naringsbrist.html` (227 lines)
4. `lutein-zeaxantin-huden.html` (217 lines)
5. `nya-kostrad-65-plus-d-vitamin-magnesium.html` (166 lines)
6. `retinol-pa-sommaren.html` (230 lines)
7. `vad-ar-niacinamid.html` (226 lines)
8. `vilken-magnesiumform-ar-bast.html` (283 lines)

### Hero implementation
- **Flat header** — no gradient, no overlay, no stats
- Pattern: `.ia-eyebrow` + `<h1>` + `.ia-meta` (author · date · reading time)
- Optional SVG image: `<img src="data:image/webp;base64,...">` after meta
- No breadcrumb HTML in body (breadcrumbs in JSON-LD schema only)

### Article header
```
<main class="ia-wrap">
<article>
<p class="ia-eyebrow">Topic · Category</p>
<h1>Article Title</h1>
<div class="ia-meta">
  <span>Author Name</span><span class="dot"></span>
  <span>Uppdaterad: month year</span><span class="dot"></span>
  <span>X min läsning</span>
</div>
```

### Metadata layout
- Title, description, canonical (standard)
- og:type=article, og:title, og:description, og:url, og:site_name, og:image+dimensions
- twitter:card=summary_large_image, twitter:title, twitter:description
- **Missing:** Google verification metas, BreadcrumbList schema, `og:locale`

### Breadcrumb implementation
- **No HTML breadcrumbs** in body
- **No BreadcrumbList schema** in JSON-LD
- **Category label available** in `<p class="ia-eyebrow">` which can map to breadcrumb position

### Author Box
- Present but incomplete compared to PA template
- Pattern: `<div class="ia-author-box"><div><p class="name">Author</p><p class="cred">Bio</p><a>Link</a></div></div>`
- **Missing:** `.ia-author-avatar` div with initials — PA template has `XX` avatar
- Author box is simpler (no avatar circle, just text block)

### CTA
- **Missing** — no `.ia-cta` product call-to-action block
- PA template: dark green box with product pitch and gold button

### Related Articles
- **Missing** — no `.ia-tierbox` (4-tier internal link grid)
- Some articles have inline links to other LevNytt pages within content
- PA template: `.ia-tierbox` with 4 `.ia-tier` links to history, science, FAQ, author

### Footer
- `footer.js` + `components.js` (deferred) — matches PA template
- No inline footer CSS

### Custom components
- `.ia-svg-card` — dark green SVG card (article-specific)
- `.ia-prompt` — italic prompt with left border (used for official quotes)
- `.ia-warning` — orange warning box with left border
- Fonts: Playfair Display 700 only (not 400/600) + Inter 400/500/600/700
- Font loading order: single `<link>` (not two separate preconnect + link)

### CSS patterns
- Links to `pillar.css` + inline `<style>` (~40 lines)
- No :root tokens declared
- Body background: `var(--cream)` (from pillar.css)
- `.ia-wrap` uses `max-width:var(--max-w)` (wider than PA's 760px)
- `.ia-eyebrow` specific to this family
- `.ia-meta` with dot separators
- `.ia-hero-img` for SVG image
- `.ia-method-note` for methodology (matches PA)
- `.ia-svg-card`, `.ia-prompt`, `.ia-warning` (family-specific)

### JavaScript patterns
```
<script src="/nav.js" defer></script>    ← at top (no #site-nav div)
<main class="ia-wrap"> ... </main>
<script src="/footer.js" defer></script>
<script src="/components.js" defer></script>
```

### Schema
- Single `@graph` block: `Article` + `FAQPage`
- No BreadcrumbList
- No Google verification metas in head
- Matches PA schema pattern

### Components already matching PA
- `pillar.css` link ✓
- `ia-wrap` wrapper ✓
- `article` element ✓
- `ia-punchline` ✓
- `ia-takeaways` (Key Takeaways) ✓
- `ia-method-table` ✓
- `ia-stat-grid` / `ia-stat-card` ✓
- `ia-callout` ✓
- `ia-evidence-label` / `ia-ev-t1–t4` ✓
- `ia-faq` (details/summary) ✓
- `ia-method-note` ✓
- `ia-author-box` (partial) ✓
- Schema: @graph Article+FAQPage ✓
- `footer.js` + `components.js` at bottom ✓
- `nav.js` at top ✓
- Fonts: Playfair Display + Inter ✓

### Components to be replaced
- `.ia-meta` → PA byline format (`<p>Av <a>Author</a> · date · X min</p>`)
- `.ia-hero-img` → move after punchline (PA puts SVG after punchline)
- `.ia-svg-card` → keep or convert to `ia-callout` as needed
- Font weight subset (700 only) → 400/600/700 for Playfair

### Components to be added
- `#site-nav` div placeholder (currently just script)
- `ia-author-avatar` div inside author box
- `ia-cta` product CTA block
- `ia-tierbox` 4-tier internal links
- `ia-disclosure` (LevNytt.se är en oberoende...)
- Google verification metas
- `og:locale` meta

### Components to be removed
- `.ia-prompt` (can fold into ia-callout)
- `.ia-warning` (can use ia-callout variant)
- `.ia-svg-card` (article-specific, may keep per-article)
- `.dot` separator spans (replaced by PA byline format)

### Migration effort
- **Low** — closest to PA template of any legacy family
- ~30 min per article
- Add 6 missing components per article
- Replace 2 component patterns
- Remove 2-3 legacy class patterns
- Standardize fonts, nav div, author box structure

---

## Family 2: S4 — naringsbrist-symptom

**Articles:** 1
**Location:** `content/articles/naringsbrist-symptom.html` (445 lines)
**PA match:** 35%
**Complexity:** Medium

### Article
- `naringsbrist-symptom.html` — standalone, larger than S1 compact files

### Hero implementation
- Flat ia-wrap header (similar to S1 but larger)
- Eyebrow + h1 + meta (author, date, reading time)
- Has SVG hero image after header

### Article header
- Same ia-eyebrow/h1/ia-meta pattern as S1 family
- Has byline with author link

### Metadata layout
- Standard OG + Twitter metas present
- Has Google verification metas ✓ (unlike S1)
- Canonical URL uses `www.levnytt.se` domain (inconsistent)

### Breadcrumbs
- No HTML breadcrumbs
- No BreadcrumbList schema

### Author Box
- Missing — no `.ia-author-box`
- Has inline product CTA at end instead (different from PA)

### CTA
- Has product CTA but uses custom inline format, not PA `.ia-cta`

### Related Articles
- Has inline tier boxes but not PA `.ia-tierbox` format

### FAQ
- Details/summary accordion ✓
- FAQPage schema in JSON-LD ✓

### CSS patterns
- `pillar.css` + inline CSS
- Uses `Georgia` font family as fallback (not `Inter`)
- Larger article: 445 lines (includes substantial inline CSS)
- Has product-specific CSS not in PA template

### Components already matching
- `pillar.css` link ✓
- `ia-wrap` wrapper ✓
- `ia-punchline` ✓
- `ia-takeaways` ✓
- FAQ accordion + FAQPage schema ✓
- OG + Twitter metas ✓

### Components to be replaced
- Georgia font → Inter (PA standard)
- Custom product CTA → PA `.ia-cta` format
- Custom tier boxes → PA `.ia-tierbox`
- Body CSS overrides → align with PA standard

### Components to be added
- `ia-author-box`
- `ia-disclosure`
- `ia-tierbox` (standard 4-tier)
- `ia-cta` (standard format)
- Standardized PA byline format
- BreadcrumbList schema

### Components to be removed
- Georgia font references
- Custom product CSS (use shared ia-cta from pillar.css)
- Inline tier box CSS (use shared ia-tierbox)
- `www.levnytt.se` canonical → `levnytt.se`

### Migration effort
- **Medium** — one file but 445 lines
- ~45 min
- Similar challenges to S1 plus font standardization
- Estimated as Phase 2 alongside R2

---

## Family 3: R2 — ia-wrap Legacy

**Articles:** 4
**Location:** Root `/`
**PA match:** 40%
**Complexity:** Medium

### Articles
1. `hur-fungerar-natverksmarknadsforing-egentligen.html` (349 lines)
2. `magnesiumglycinat-och-somn.html` (317 lines)
3. `multivitamin-kvinnor-over-40.html` (406 lines)
4. `vad-ar-vitamin-b12.html` (430 lines)

### Hero implementation
- **Flat header** — no gradient, no overlay
- SVG image as hero graphic (inline base64)
- Pattern: `<h1>` → `<div class="ia-byline">` → SVG image → `ia-punchline`
- No `.ia-eyebrow` (category label)
- No stats row

### Article header
```
<article class="ia-wrap">
<h1>Article Title</h1>
<div class="ia-byline">
  Av <a href="/om-oss/">Author</a> — Role, levnytt.se · Uppdaterad: month year
</div>
<img src="data:image/webp;base64,..." />  (SVG hero)
<p class="ia-punchline">...</p>
```

### Metadata layout
- Full OG + Twitter metas ✓
- Google verification metas ✓
- Playfair 400/600/700 + Inter 300/400/500/600 ✓
- Canonical ✓
- `og:locale` ✓

### Breadcrumb implementation
- No HTML breadcrumbs
- No BreadcrumbList schema in JSON-LD

### Author Box
- Present with avatar ✓ (closer to PA than S1)
- Pattern: `<div class="ia-author-box"><div class="avatar">JH</div><div class="meta"><strong>Author</strong><br>Bio</div></div>`
- Class names differ from PA: `.avatar` (PA: `.ia-author-avatar`), `.meta` (PA: no class)
- PA author box uses `ia-author-avatar` and `flex` layout directly
- Avatar circle is `#2D6A4F` (PA uses `#1B4332`)

### CTA
- Present on most articles ✓ (3 of 4 have it)
- Uses custom button classes (`.btn`, `.btn-sec`) — PA uses inline `<a>` styling
- PA: gold background button, dark green background CTA
- R2: green background CTA with gold buttons + secondary outline button

### Related Articles
- Missing — no `.ia-tierbox`
- PA: 4-tier grid with history, science, FAQ, author links

### Footer
- `footer.js` + `components.js` at bottom ✓
- `nav.js` at top ✓ (but inline, not `#site-nav` div)

### Custom components
- `.ia-warning-box` — orange warning with border (article-specific)
- `.ia-methodology` — green-bordered methodology note (PA: inline paragraph)
- `.ia-byline` — unique byline format with border-bottom
- SVG hero image (inline base64, differs from S1's `.ia-hero-img`)
- Font sizes slightly different from PA: h1 2.05em (PA: 2.1em)

### CSS patterns
- `pillar.css` + inline `<style>` (~100 lines)
- **Fully self-contained CSS** — includes `*{box-sizing;margin:0;padding:0}`, body styles, all ia-* classes
- No dependency on pillar.css for any ia-* classes (declares everything)
- Classes like `.ia-wrap` use `max-width:780px` (PA: 760px)
- `.ia-wrap` uses `padding:32px 20px 60px` (PA: `padding:0 20px`)
- **No `#site-nav` div** — just `<script src="/nav.js" defer></script>` directly

### JavaScript patterns
```
<div id="site-nav"></div>           ← sometimes present (#6, #9)
<script src="/nav.js" defer></script>  ← sometimes at top only (NOT at bottom)
... ia-wrap content ...
<script src="/footer.js" defer></script>
<script src="/components.js" defer></script>
                                ← nav.js MISSING at bottom on 4/4 files
```

**Critical bug:** `nav.js` is loaded at top but not at bottom. On 2 of 4 files, `nav.js` appears at top inside `#site-nav` div but is never loaded at end of body. On the other 2, it's loaded at top only without `#site-nav` wrapper. PA template puts `nav.js` at top with `#site-nav` and does not duplicate at bottom.

### Schema
- `@graph`: Article + FAQPage ✓
- No BreadcrumbList
- Matches PA schema pattern

### Components already matching
- `pillar.css` link ✓
- `ia-wrap` + `article` ✓
- `ia-punchline` ✓
- `ia-takeaways` (Key Takeaways) ✓
- `ia-stat-grid` + `ia-stat-card` ✓
- `ia-method-table` ✓
- `ia-evidence-label` + `ia-ev-t1–t4` ✓
- `ia-faq` (details/summary) ✓
- `ia-author-box` (with avatar) ✓
- `ia-cta` (present, different classes) ✓ (partial)
- Schema @graph Article+FAQPage ✓
- OG + Twitter + Google metas ✓
- `og:locale` ✓

### Components to be replaced
- `.ia-byline` → PA byline format (paragraph, no border-bottom)
- `ia-cta` button classes (`.btn`, `.btn-sec`) → PA inline styled links
- `.ia-methodology` → PA inline method note format
- `.ia-wrap` padding/max-width → align with PA (760px, 0 20px)
- `.avatar` → `.ia-author-avatar` class name
- CSS: remove standalone reset/body styles (pillar.css provides these)
- SVG image placement → after punchline (PA standard)

### Components to be added
- `ia-tierbox` (4-tier internal links)
- `ia-disclosure` (LevNytt.se är en oberoende...)
- `#site-nav` div wrapper (currently just script on some)
- Category label at top (`<p style="font-size:0.85em;color:#888">`)

### Components to be removed
- `.ia-warning-box` → fold into ia-callout or keep as article-specific
- `.ia-byline` border-bottom → not in PA standard
- CSS reset block (already in pillar.css)
- body font override (pillar.css sets it)
- `.btn`, `.btn-sec` button classes → use PA inline link formatting

### Migration effort
- **Medium** — need to fix CSS self-sufficiency, standardize CTA, add missing components
- ~45 min per article
- Closest to PA of any root-level family

---

## Family 4: R3 — PA-Close / Old Master

**Articles:** 2
**Location:** Root `/`
**PA match:** 50%
**Complexity:** Medium

### Articles
1. `varfor-fiskolja-inte-ar-likvardigt.html` (113 lines)
2. `viktuppgang-klimakteriet.html` (106 lines)

### Hero implementation
- **Gradient hero with overlay** — matches old master template, NOT PA standard
- `section.hero` with `.hero-overlay` + `.hero-content`
- Breadcrumb inside hero: `Hem / Current Page`
- h1 in hero
- Hero stats: `.hero-stats` with `.hero-stat` (num + lbl)
- **PA standard:** no hero section → flat header

### Article header
```
<div class="freshness-banner">Uppdaterad maj 2026</div>
<section class="hero"><div class="hero-overlay"></div>
  <div class="hero-content">
    <div class="breadcrumb"><a href="/">Hem</a><span>/</span><span>Page</span></div>
    <h1>Title</h1>
    <div class="hero-stats">
      <div class="hero-stat"><span class="num">70%</span><span class="lbl">Label</span></div>
    </div>
  </div>
</section>
<div class="back-link-wrapper"><a href="/" class="back-link">&larr; Tillbaka</a></div>
<div class="article-content"><div class="article-inner">
```

### Metadata layout
- Title, description, canonical ✓
- Google verification metas ✓
- og:image added via `<meta property>` tag (not grouped with others)
- **Missing:** og:type, og:url, og:site_name, og:locale, twitter:card, twitter:title/description
- **Missing:** og:image dimensions (width/height/alt)
- Fonts: Inter 400/500/600/700/800 + Playfair 600/700 (heavier weight range)

### Breadcrumb implementation
- HTML breadcrumbs in hero (visible) ✓
- Breadcrumb data: `Hem / Page` (flat, no intermediate category)
- **No BreadcrumbList schema** in JSON-LD

### Author Box
- Missing — no author information anywhere in the article

### CTA
- Missing — no product CTA block

### Related Articles
- Present as `.internal-links-section` ✓
- Pattern: `<section class="internal-links-section"><div class="container"><h3>Relaterade artiklar</h3><ul><li><a>...</a></li></ul></div></section>`
- **PA standard:** `.ia-tierbox` (4-tier grid, not ul list)
- This is old master template format — needs replacement

### FAQ
- **Missing** — no FAQ section at all
- No FAQPage schema
- No Article schema (no schema of any kind!)

### Sources
- Present as inline styled paragraph ✓
- Pattern: `<p style="font-size:0.85em;color:#888;border-top..."><strong>Källor:</strong><br>...</p>`
- PA standard: references inline in content + `.ia-disclosure` at end

### Gold conclusion
- Present as `.callout.callout-gold` ✓
- PA standard: no gold conclusion callout

### CSS patterns
- **Fully inline CSS** (~50 lines) — no dependency on ia-* classes
- **Uses :root tokens** from pillar.css (--gold, --green, --cream, --ink, etc.)
- **Links to pillar.css** as fallback ✓
- CSS copied directly from old master template:
  - `nav`, `.nav-inner`, `.nav-brand`, `.nav-links`, `.nav-cta`, `.nav-hamburger`
  - `.freshness-banner`
  - `.hero`, `.hero-overlay`, `.hero-content`, `.breadcrumb`, `.hero-stats`
  - `.article-content`, `.article-inner`, `.callout`, `.callout-gold`
  - `.back-link-wrapper`, `.internal-links-section`
  - `footer` (full inline footer CSS — no footer.js dependency for styles)
  - `@media` breakpoints for responsive

### JavaScript patterns
```
<script> (smooth scroll — inline)
<script src="/nav.js" defer></script>
<script src="/footer.js" defer></script>
<script src="/components.js" defer></script>
```

### Schema
- **NONE** — no Article, no FAQPage, no BreadcrumbList, no @graph
- Critical SEO gap

### Components already matching
- `pillar.css` link ✓
- `footer.js` + `components.js` at bottom ✓
- `nav.js` + `footer.js` ✓
- Responsive media queries ✓

### Components to be replaced
- Entire hero section → flat ia-wrap header
- Freshness banner → remove (not in PA)
- Back-link → remove (not in PA)
- `.article-content` / `.article-inner` → `.ia-wrap` / `<article>`
- `.internal-links-section` ul → `.ia-tierbox` grid
- `.callout` Sammanfattning → `.ia-punchline`
- `.callout.callout-gold` Slutsats → fold into content or remove
- Sources paragraph → inline refs in content + `.ia-disclosure`
- Smooth scroll script → CSS only (already in pillar.css)
- `.breadcrumb` → move to schema only, remove from HTML
- Inline nav CSS → remove (nav.js handles it)
- Inline footer CSS → remove (footer.js handles it)

### Components to be added
- `ia-wrap` wrapper structure
- `ia-punchline`
- `ia-takeaways` (Key Takeaways)
- `ia-stat-grid` + `ia-stat-card`
- `ia-faq` (details/summary accordion)
- `ia-author-box`
- `ia-cta`
- `ia-tierbox`
- `ia-disclosure`
- `ia-evidence-label` (tier badges)
- Schema: @graph Article + FAQPage
- OG + Twitter full metas
- `#site-nav` div
- Category label
- Author byline
- Evidence labels in content

### Components to be removed
- `.freshness-banner` (not in PA)
- `.back-link-wrapper` (not in PA)
- `.hero`, `.hero-overlay`, `.hero-content`, `.hero-stats` (not in PA)
- `.callout.callout-gold` (Gold conclusion — not in PA)
- Inline nav CSS (~15 lines)
- Inline footer CSS (~15 lines)
- Inline smooth scroll script

### Migration effort
- **Medium** — only 2 files, but needs complete structural rewrite
- ~45 min per article
- These articles match the OLD master template, not the PA ia-wrap standard
- Need full conversion: hero → flat, add FAQ, add schema, restructure content

---

## Family 5: S2 — ia-wrap Large / Authority

**Articles:** 5
**Location:** `content/articles/`
**PA match:** 30%
**Complexity:** Medium-High

### Articles
1. `ar-dyra-kosttillskott-verkligen-battre.html` (465 lines)
2. `cellmembran-funktion.html` (985 lines)
3. `naringsbrist.html` (796 lines)
4. `vad-ar-vaxtsteroler.html` (857 lines)
5. `varfor-ar-jag-trott-hela-tiden.html` (1037 lines)

### Hero implementation
- **Gradient hero** — `.hero` with `::before`/`::after` decorative circles
- Pattern: `.hero-eyebrow` → `h1` → `.hero-intro` → `.hero-meta` (author/date/evidence)
- Has breadcrumbs bar: `<div class="breadcrumbs"><div class="container"><a>LevNytt</a><span>›</span><a>Category</a><span>›</span>Current</div></div>`
- Has stats row: `<section class="stats-row"><div class="stats-grid"><div><span class="stat-number">...</span><span class="stat-label">...</span><span class="stat-source">...</span></div></div></section>`
- Has authority nav: `<div class="authority-nav"><div class="container"><span class="authority-nav-label">Om LevNytt</span><a>5 links</a></div></div>`
- **PA standard:** flat header — no gradient, no overlay, no breadcrumbs bar, no stats row, no authority nav

### Article header
Full pillar authority header pattern:
```
<div class="breadcrumbs"><div class="container">Breadcrumb links</div></div>
<header class="hero"><div class="container">
  <p class="hero-eyebrow">Topic tags</p>
  <h1>Title</h1>
  <p class="hero-intro">Intro paragraph</p>
  <div class="hero-meta">Author | Date | Evidence type</div>
</div></header>
<section class="stats-row"><div class="container"><div class="stats-grid">4 stats</div></div></section>
<div class="authority-nav"><div class="container">5 authority links</div></div>
```

### Metadata layout
- Standard OG metas (title, description, type, url, site_name, image+dimensions)
- No Google verification metas (unlike R2)
- No `og:locale` (unlike R2)
- Plays 400/600/700 + Inter 300/400/500/600 ✓

### Breadcrumb implementation
- Full HTML breadcrumbs bar ✓ (separate from hero, above it)
- BreadcrumbList schema in JSON-LD ✓ (matches R1 pattern)
- Breadcrumbs are visible, styled, and useful

### Author Box
- Present but in R1/prod-A format:
  - `<div class="author-box"><div class="author-avatar"><img></div><div class="author-info"><span class="author-label">Skribent</span><strong>Name</strong><span>Bio</span><div class="method-note">Methodology</div></div></div>`
  - Uses image avatar (not initials)
  - Has `.method-note` inline
  - PA: uses `.ia-author-box` with `.ia-author-avatar` (initials, no image)

### CTA
- Present as `.cta-block` (different from PA's `.ia-cta`)
- Pattern: `<div class="cta-block"><h3>Title</h3><p>Text</p><a href="..." class="cta-btn">CTA →</a></div>`
- PA standard: `.ia-cta` (dark green bg, gold button)

### Related Articles
- Present as `.tier-section` (different from PA's `.ia-tierbox`)
- Pattern: `<div class="tier-section"><p class="tier-label">Utforska vidare</p><div class="tier-grid"><a class="tier-box">Tier 1 | Title</a>...</div></div>`
- 8 links (4 authority + 4 topical) vs PA's 4 links
- PA: `.ia-tierbox` (4-cell flex grid)

### Footer
- `footer.js` + `components.js` at bottom ✓
- `nav.js` at bottom ✓
- Also has `.journey-block` at very end: breadcrumb-style navigation chain

### Custom components
- `.breadcrumbs` bar (separate from hero)
- `.hero` with decorative circles
- `.stats-row` + `.stats-grid` (separate section, sourced stats)
- `.authority-nav` (5 trust links)
- `.article-wrap` / `.article-body` (different from `.ia-wrap` / `<article>`)
- `.callout-amber`, `.callout-standard` (callout variants)
- `.cta-block` (different from `.ia-cta`)
- `.tier-section` + `.tier-grid` (8-link grid)
- `.tier-box` (individual tier link card, different class from PA's `.ia-tier`)
- `.author-box` with `.author-avatar img` (image, not initials)
- `.method-note` (inline in author box)
- `.last-updated` paragraph
- `.journey-block` + `.journey-steps`

### CSS patterns
- `pillar.css` + inline `<style>` (~100-120 lines)
- Full custom CSS for all structural components
- Body: `font-family:'Inter',sans-serif; background:var(--cream); color:var(--ink)`
- Uses `var(--max-width)` from pillar.css
- Hero gradient: `linear-gradient(145deg, #0f2d1f 0%, var(--green-dark) 60%, #1e4d35 100%)`
- Stats row: `background:var(--white); border-bottom:3px solid var(--gold)`
- Authority nav: small text, centered in container
- `.article-wrap` uses `.container` pattern

### JavaScript patterns
```
<header class="hero">...</header>
<section class="stats-row">...</section>
<div class="authority-nav">...</div>
<main class="article-wrap"><div class="container">
  ...
  <div class="journey-block">...</div>
</div></main>
<script src="/nav.js" defer></script>
<script src="/footer.js" defer></script>
<script src="/components.js" defer></script>
```

### Schema
- Sometimes present, sometimes not (inconsistency within family)
- When present: `@graph` with Article + FAQPage + BreadcrumbList ✓
- 2 of 5 have NO schema at all (critical gap)

### Components already matching
- `pillar.css` link ✓
- `ia-punchline` ✓ (inside `.article-wrap`)
- `ia-takeaways` ✓ (inside `.article-wrap`)
- `ia-method-table` ✓
- `ia-stat-grid` + `ia-stat-card` ✓
- `ia-faq` (details/summary) ✓
- Some have @graph Article+FAQPage ✓
- `footer.js` + `components.js` ✓
- `nav.js` ✓
- Evidence labels (tier badges in FAQ) ✓
- OG + Twitter metas ✓

### Components to be replaced
- `.breadcrumbs` bar → remove (PA has no HTML breadcrumbs)
- `.hero` gradient section → flat ia-wrap header
- `.stats-row` → inline `ia-stat-grid` (PA puts stats in content)
- `.authority-nav` → remove (PA has no authority nav)
- `.article-wrap` / `.article-body` → `.ia-wrap` / `<article>`
- `.cta-block` → `.ia-cta`
- `.tier-section` / `.tier-grid` → `.ia-tierbox`
- `.author-box` with image → `.ia-author-box` with initials
- `.callout-amber` → `.ia-callout`
- `.journey-block` → remove (PA has no journey navigation)

### Components to be added
- Flat header: `.ia-eyebrow` + `h1` + byline (no hero section)
- `.ia-disclosure`
- `.ia-evidence-label` inline in content (family has them in FAQ only)
- Schema where missing (2 files)
- `#site-nav` div

### Components to be removed
- `.breadcrumbs` bar
- `.hero` section (entire gradient hero)
- `.stats-row` section
- `.authority-nav` div
- `.journey-block`
- `.last-updated` (fold into byline or disclosure)

### Migration effort
- **Medium-High** — 5 large files (465-1037 lines each), needs complete structural conversion
- ~60 min per article
- Most impacted: replacing the entire pillar authority header (breadcrumbs bar + hero + stats + authority nav) with flat ia-wrap header

---

## Family 6: R1 — Pillar Authority

**Articles:** 11
**Location:** Root `/`
**PA match:** 25%
**Complexity:** High

### Articles
1. `ala-vs-epa-vs-dha.html` (119 lines)
2. `direktforsaljning-fakta.html` (125 lines)
3. `ekologisk-stadning-greenwashing.html` (127 lines)
4. `fytosteroler-cellmembran.html` (467 lines)
5. `karotenoid-tillskott-vs-mat.html` (123 lines)
6. `personlig-vard.html` (422 lines)
7. `super-10.html` (115 lines)
8. `vad-ar-kostfiber.html` (138 lines)
9. `vad-ar-probiotika.html` (141 lines)
10. `vaxtbaserade-steroler-dagligen.html` (121 lines)
11. `zeaxantin-immunforsvar-2025.html` (660 lines)

### Hero implementation
- **Identical to S2 family** — gradient hero with decorative elements
- `header.hero` with `.hero-eyebrow` → `h1` → `.hero-intro` → `.hero-meta`
- Breadcrumbs bar above hero (separate section): `<div class="breadcrumbs" role="navigation">`
- Stats row below hero: `<section class="stats-row">`
- Authority nav below stats: `<div class="authority-nav">`

### Article header
**Exact same pattern as S2** (likely S2 was copied from R1 pattern):
```
<div class="breadcrumbs"><div class="container">LevNytt › Category › Page</div></div>
<header class="hero"><div class="container">
  <p class="hero-eyebrow">Tags</p>
  <h1>Title</h1>
  <p class="hero-intro">...</p>
  <div class="hero-meta"><span>Av <strong>Name</strong></span><span>Publicerad <strong>date</strong></span><span>Evidenstyp: <strong>type</strong></span></div>
</div></header>
<section class="stats-row"><div class="container"><div class="stats-grid">4 stats with sources</div></div></section>
<div class="authority-nav"><div class="container"><span class="authority-nav-label">Om LevNytt</span><a href="...">Om oss</a><a href="...">Den Fundersamma Mannen</a>...</div></div>
```

### Metadata layout
- Full OG + Twitter metas ✓
- Google verification metas ✓
- Playfair 400/600/700 + Inter 300/400/500/600 ✓
- `og:locale` ✓

### Breadcrumbs
- HTML breadcrumbs bar ✓
- BreadcrumbList in @graph schema ✓

### Content structure
```
<main class="article-wrap"><div class="container">
  <div class="ia-punchline"><p>...</p></div>
  <div class="ia-takeaways"><h2>Det viktigaste att veta</h2><ul>...</ul></div>
  <div class="article-body">
    ...content...
    <div class="cta-block">...</div>
    <div class="tier-section">...</div>
    <div class="faq-section">...</div>
    <div class="author-box">...</div>
    <p class="last-updated">...</p>
    <div class="journey-block">...</div>
  </div>
</div></main>
```

### All other components
- **Identical to S2 family** in every respect:
  - Same CTA format (`.cta-block`)
  - Same related articles (`.tier-section` with 8 links)
  - Same author box (image avatar, `.method-note` inline)
  - Same journey block
  - Same FAQ (details/summary)
  - Same CSS patterns
  - Same JS patterns

### Differences from S2
- R1 articles are at root (published), S2 are in `content/articles/` (source)
- R1 articles are smaller on average (115-660 lines vs S2's 465-1037)
- R1 has BreadcrumbList schema in all files; S2 is inconsistent
- R1 has Google verification metas in all files; S2 does not
- `personlig-vard.html` uses `CollectionPage` schema instead of `Article` (unique)

### Components already matching PA
- `pillar.css` ✓
- `ia-punchline` ✓
- `ia-takeaways` ✓
- `ia-faq` (details/summary) ✓
- `ia-method-table` ✓
- `ia-stat-grid` + `ia-stat-card` ✓ (in stats-row section)
- `ia-evidence-label` ✓ (in FAQ)
- Schema @graph Article+FAQPage+BreadcrumbList ✓
- OG + Twitter + Google metas ✓
- `footer.js` + `components.js` ✓
- `nav.js` ✓

### Components to be replaced
- All S2 components listed above PLUS:
- Entire breadcrumbs bar
- Entire gradient hero section
- Entire stats-row section
- Entire authority-nav div
- `.article-wrap` → `.ia-wrap`
- `.article-body` → remove wrapper
- `.cta-block` → `.ia-cta`
- `.tier-section` → `.ia-tierbox` (reduce 8 links → 4)
- `.author-box` (with img) → `.ia-author-box` (with initials)
- `.journey-block` → remove

### Components to be added
- Flat ia-wrap header
- `.ia-disclosure`
- `.ia-evidence-label` inline in content body
- `#site-nav` div

### Components to be removed
- Same 9+ structural sections as S2

### Migration effort
- **High** — 11 files, complete structural rewrite from pillar authority to ia-wrap
- ~90 min per file
- Largest family in migration scope

---

## Family 7: S3 — Trust Architecture

**Articles:** 3
**Location:** `content/articles/`
**PA match:** 30%
**Complexity:** High

### Articles
1. `forsknings-faq.html` (892 lines)
2. `levnytt-principer.html` (824 lines)
3. `var-metod.html` (791 lines)

### Hero implementation
- **Gradient hero** (similar to S2/R1)
- Breadcrumbs in hero (inline)
- No stats row
- No authority nav

### Critical difference: Schema type
- **Uses `WebPage` schema** — NOT `Article`
- These pages are concept references (FAQ, principles, methodology), not articles
- `og:type: "website"` instead of `og:type: "article"`
- This is semantically correct for their purpose but differs from PA standard

### Custom components
- `.section-label` system — custom labeling for content sections
- `.journey-block` — reader journey navigation
- `.tier-boxes` — inline tier navigation (different from `.tier-section`)
- `.authority-cta` — custom CTA format
- `.editorial-signal` — editorial quality indicator
- **No `components.js`** — unique among all families

### Components to note
- These pages serve a trust/architecture purpose
- Schema should remain `WebPage` (not Article) — changing would be semantically wrong
- Journey + tier navigation is their core value proposition

### Migration effort
- **High** — schema decision needed, custom components, missing scripts
- These may not need full ia-wrap conversion — they serve a separate purpose

---

## Family 8: R4 — Calculator Tool

**Articles:** 1
**Location:** Root `/`
**PA match:** 5%
**Complexity:** Special

### Article
- `finns-det-billigare-alternativ.html` (1091 lines)

### Unique characteristics
- **Interactive JavaScript calculators** (savings calculator, cost comparison)
- Video embed section
- FAQ accordion (no schema)
- Savings grid display
- Custom gradient hero (`.hero` class, different CSS)
- Container-based layout (not ia-wrap or article-wrap)
- 980+ lines of custom CSS
- No schema of any kind
- No author box

### Purpose
- This is a tool/utility page, not an informational article
- Primary value is the interactive calculator
- Different user intent (calculate, not read)

### Migration strategy
- **Decision needed:** Either:
  A. Rebuild as PA ia-wrap article with embedded calculator widget
  B. Split into two: an informational article + a separate calculator tool page
  C. Keep as-is with schema/metadata improvements

---

## Family 9: P1 — Historia/Vetenskap (Pillar Pages)

**Articles:** 2
**Location:** Root `/`
**PA match:** 30%
**Complexity:** Out of scope for this sprint

### Articles
- `neolife-historia.html` (393 lines)
- `neolife-vetenskap.html` (399 lines)

### Key characteristics
- Gradient hero (`.historia-hero`) — named variant, not `.hero`
- Freshness banner ✓ (unlike PA)
- Back-link ✓ (unlike PA)
- TOC ✓ (unlike PA)
- Summary callout ✓ (unlike PA, uses IA format)
- Gold conclusion ✓ (present in historia, missing in vetenskap)
- FAQ with itemscope microdata ✓ (in body + schema)
- Sources section ✓
- Internal-links-section ✓
- Smooth scroll script ✓
- Timeline component (historia only)
- Separate Article + FAQPage + BreadcrumbList JSON-LD blocks (not @graph)

---

## Family 10: P2 — Hallbarhet/Golden Home Care

**Articles:** 2
- `neolife-hallbarhet.html` (305 lines)
- `golden-home-care.html` (394 lines)

Similar to P1 but lighter: no TOC, FAQ without microdata, no smooth scroll.

---

## Family 11: P3 — Affarsmojlighet

**Articles:** 1
- `neolife-affarsmojlighet.html` (584 lines)

Heavily customized: custom hero, comparison cards, savings highlights, video cards.

---

## Family 12: P4 — Custom Isolated

**Articles:** 2
- `den-fundersamma-mannen.html` (294 lines) — completely custom design system
- `om-oss.html` (1065 lines) — custom masthead, missing nav.js

---

## Family 13: PROD-A — Pillar Product

**Articles:** 20
**PA match:** 15%

Product informational pages with pillar.css + authority-nav + stats-row pattern.
Separate product template family.

---

## Family 14: PROD-B — Old-style Product

**Articles:** 5
**PA match:** 20%

Old master-template derivative product pages with freshness banner, gradient hero, back-link.
Separate product template family.

---

## Recommended Migration Order

### Prerequisite: Standardize ia-* CSS in pillar.css

Before ANY article migration, extract the 12 shared ia-* CSS class groups into `pillar.css`:

| Class group | Lines saved per article |
|---|---|
| `.ia-wrap` base | 8 |
| `.ia-punchline` | 6 |
| `.ia-takeaways` | 10 |
| `.ia-stat-grid` + `.ia-stat-card` | 12 |
| `.ia-method-table` | 12 |
| `.ia-callout` | 5 |
| `.ia-evidence-label` + `ia-ev-t1–t4` | 8 |
| `.ia-faq` + details/summary | 10 |
| `.ia-tierbox` + `.ia-tier` | 8 |
| `.ia-cta` | 10 |
| `.ia-author-box` + `.ia-author-avatar` | 10 |
| `.ia-disclosure` | 5 |
| **Total per article** | **~104 lines saved** |

This reduces inline CSS from ~100 lines to ~10 lines per article. Total savings across 26 PA articles + 35 migrated articles = ~6,300 lines of duplicated CSS eliminated.

### Phase 1 — S1: ia-wrap Compact (8 articles)
- **Reason:** Closest to PA template (55% match). Adds author box, CTA, tierbox, disclosure.
- **Risk:** Low — same ia-wrap base, already in content/articles/ (not live)
- **Estimated effort:** 4 hours
- **Opportunity:** These are also the newest source articles (June 2026 dates). Standardize fonts, add `#site-nav` div.

### Phase 2 — S4 + R2 (5 articles)
- **Reason:** Second-closest families. R2 has author box + CTA already. S4 is one file.
- **Risk:** Medium — R2 articles are live at root
- **Estimated effort:** 4 hours
- **Opportunity:** Fix R2's self-contained CSS (no longer needed after pillar.css extraction)

### Phase 3 — R3: PA-Close (2 articles)
- **Reason:** Smallest family. Closest to old master template. Needs complete restructure but content is short.
- **Risk:** Medium — live at root, but only 2 small files (113, 106 lines)
- **Estimated effort:** 1.5 hours
- **Opportunity:** Largest number of components to REMOVE (freshness banner, back-link, hero, gold conclusion, inline nav/footer CSS, smooth scroll script) — most cleanup per article

### Phase 4 — S2: ia-wrap Large/Authority (5 articles)
- **Reason:** Larger articles but already have ia-punchline/takeaways/FAQ. Need to strip pillar authority header.
- **Risk:** Medium — in content/articles/ (not live)
- **Estimated effort:** 5 hours
- **Opportunity:** Remove breadcrumbs bar, hero, stats row, authority nav, journey block — 5 structural sections per file

### Phase 5 — R1: Pillar Authority + S3: Trust (14 articles)
- **Reason:** Largest family (R1, 11 files) + trust pages (S3, 3 files). Most complex conversion.
- **Risk:** High — R1 articles are live at root, heavily trafficked
- **Estimated effort:** 21 hours (11 × 90min + 3 × 90min)
- **Opportunity:** Highest per-article reduction in structural complexity
- **Note:** S3 trust pages may need schema approach decision before conversion

### Phase 6 — R4: Calculator Tool (1 article)
- **Reason:** Unique — needs architectural decision first
- **Risk:** High — interactive calculators depend on custom JS
- **Estimated effort:** Decision required before estimating

### Separate Sprint: Pillar + Product Pages (32 articles)
- **Reason:** Different purpose, different template families
- **Families:** P1, P2, P3, P4, PROD-A, PROD-B
- **Effort:** Estimated separately after article migration audit is complete

### Total Estimated Migration Effort

| Phase | Articles | Effort |
|---|---|---|
| Prerequisite (pillar.css) | N/A | 2 hours |
| Phase 1 (S1) | 8 | 4 hours |
| Phase 2 (S4+R2) | 5 | 4 hours |
| Phase 3 (R3) | 2 | 1.5 hours |
| Phase 4 (S2) | 5 | 5 hours |
| Phase 5 (R1+S3) | 14 | 21 hours |
| Phase 6 (R4) | 1 | TBD |
| **Total** | **35** | **37.5 hours + R4** |

### Safest Sequence Rationale

1. **S1 first** — these are in content/articles/ (not live), highest match, lowest risk. Validates the pillar.css extraction approach.

2. **S4+R2 next** — R2 is live but small (4 files), with similar ia-wrap base. Any issues discovered in Phase 1 can be fixed before touching live files.

3. **R3** — only 2 small files, but complete structural rewrite. Good learning opportunity before tackling larger families.

4. **S2** — larger files, but in content/articles/ (safe). Practice stripping pillar authority headers before hitting the live R1 family.

5. **R1+S3** — the big one. By this point, the migration process is proven. All earlier phases have validated the approach. R1 articles are the most visible/important legacy articles (topics: omega-3, direct sales, greenwashing, carotenoids, etc.).

6. **R4** — handled last because it needs a separate architectural decision that may influence whether it even gets converted.

---

*Analysis prepared by OpenCode Editorial System. No articles were modified. This is a read-only analysis.*