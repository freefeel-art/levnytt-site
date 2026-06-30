# Legacy Article Migration Audit — Sprint 7

**Date:** 2026-06-30
**Auditor:** OpenCode Editorial System
**Scope:** All legacy HTML pages vs current Publication Agent article template

---

## Critical Finding: Template Discrepancy

The file `levnytt-se-master-template.html` (357 lines, labeled "MASTER TEMPLATE v1.0 — Maj 2026") does **not** match the actual template used by Publication Agent articles. The PA template has since evolved to the **ia-wrap format**. This audit compares against the **actual PA article template** (as seen in `magnesiumformer-vilken-valja.html`, `varfor-tar-d-vitamin-slut-pa-ditt-magnesium.html`, and 24 other batch articles).

| Feature | master-template.html | Actual PA Template (ia-wrap) |
|---|---|---|
| CSS | Full inline `<style>` block | `<link href="/pillar.css">` + inline ia-\* CSS |
| Freshness banner | Yes | **No** |
| Hero | Gradient + overlay + breadcrumb + stats | Flat: ia-eyebrow + h1 + author byline |
| Back-link | Yes (`.back-link-wrapper`) | **No** |
| Content wrapper | `.article-content` > `.article-inner` | `.ia-wrap` > `<article>` |
| Summary | `.callout` with `Sammanfattning` | `.ia-punchline` (bold claim) |
| Takeaways | None | `.ia-takeaways` (dark green box with bullet list) |
| TOC | `.toc` with `<ol>` | **No TOC** |
| Conclusion | `.callout.callout-gold` with `Slutsats` | **No gold conclusion** |
| FAQ | `itemscope` microdata inline | `<details>/<summary>` accordion (no itemscope) |
| Sources | Inline styled paragraph | `.ia-disclosure` + inline references |
| Internal links | `.internal-links-section` with `<ul>` | `.ia-tierbox` (4-cell grid) |
| CTA | None | `.ia-cta` (dark green block with gold button) |
| Author box | **No** | `.ia-author-box` (avatar + bio) |
| Schema | Article + BreadcrumbList (separate) | `@graph` (Article + FAQPage), no BreadcrumbList |
| Smooth scroll | Inline script | **No** (CSS only) |
| Nav | Inline `<nav>` element + nav.js | `<div id="site-nav">` + nav.js deferred |
| Google verification | Inline metas | **No** |

**Recommendation:** Archive or update `levnytt-se-master-template.html` to reflect the current ia-wrap standard. It no longer represents the canonical template.

---

## Scope

| Category | Count | Description |
|---|---|---|
| **Publication Agent articles (baseline)** | 26 | Already ia-wrap compliant. Not in migration scope. |
| **Root-level legacy articles** | 18 | Informational articles at `/`. Pre-date PA pipeline. |
| **content/articles/ source files** | 17 | Source articles not yet published via PA. |
| **Pillar/authority pages** | 7 | Authority/hub pages (historia, vetenskap, etc.) |
| **Product pages** | 25 | NeoLife product pages (separate template family) |
| **Total legacy pages** | **67** | |

---

## 1. Publication Agent Template — Canonical Component Map

The current standard. Every migrated legacy article must adopt this structure.

### Component inventory

| # | Component | HTML Pattern | Required |
|---|---|---|---|
| 1 | **Doctype + lang** | `<!DOCTYPE html><html lang="sv">` | Yes |
| 2 | **Meta charset + viewport** | `<meta charset="UTF-8"><meta name="viewport"...>` | Yes |
| 3 | **Title** | `<title>Topic | LevNytt</title>` | Yes |
| 4 | **Meta description** | `<meta name="description" content="...">` (155 char) | Yes |
| 5 | **Canonical** | `<link rel="canonical" href="https://levnytt.se/slug">` | Yes |
| 6 | **OG tags** | og:type, og:title, og:description, og:url, og:site_name, og:image, og:image:width/height/alt | Yes |
| 7 | **Twitter card** | twitter:card, twitter:title, twitter:description | Yes |
| 8 | **Schema @graph** | Article + FAQPage in single JSON-LD `@graph` block | Yes |
| 9 | **Fonts** | Playfair Display 400/600/700 + Inter 300/400/500/600 | Yes |
| 10 | **pillar.css** | `<link rel="stylesheet" href="/pillar.css">` | Yes |
| 11 | **Inline ia-* CSS** | `<style>` with .ia-wrap, .ia-punchline, .ia-takeaways, .ia-stat-grid, .ia-stat-card, .ia-method-table, .ia-callout, .ia-faq, .ia-tierbox, .ia-cta, .ia-author-box, .ia-disclosure, .ia-evidence-label | Yes |
| 12 | **Nav placeholder** | `<div id="site-nav"></div><script src="/nav.js" defer></script>` | Yes |
| 13 | **Content wrapper** | `<div class="ia-wrap"><article>` | Yes |
| 14 | **Category label** | `<p style="font-size:0.85em;color:#888;text-transform:uppercase">` | Yes |
| 15 | **Eyebrow** | `<div class="ia-eyebrow">` | Yes |
| 16 | **H1** | `<h1>Article Title</h1>` | Yes |
| 17 | **Author byline** | `<p>Av <a>Author</a> · Senast uppdaterad: month year · X min läsning</p>` | Yes |
| 18 | **Punchline** | `<p class="ia-punchline">` — bold key claim with left gold border | Yes |
| 19 | **Key Takeaways** | `<div class="ia-takeaways"><h3>Key Takeaways</h3><ul>` — dark green box | Yes |
| 20 | **Content sections** | `<h2>`, `<h3>`, `<p>`, `<ul>`, `<ol>`, `<table>` | Yes |
| 21 | **Stat grid** | `<div class="ia-stat-grid"><div class="ia-stat-card">` — 2-col grid | Optional |
| 22 | **Evidence labels** | `<span class="ia-evidence-label ia-ev-t1">Tier 1</span>` | Yes (inline on claims) |
| 23 | **Info callout** | `<div class="ia-callout"><h4>Title</h4><p>Content</p></div>` | Optional |
| 24 | **Method table** | `<table class="ia-method-table">` — comparison tables | Optional |
| 25 | **Tier box** | `<div class="ia-tierbox"><a class="ia-tier">` — 4 internal links | Yes |
| 26 | **CTA block** | `<div class="ia-cta"><h3>Question?</h3><p>Text</p><a>Link →</a></div>` | Yes |
| 27 | **FAQ accordion** | `<div class="ia-faq"><h2>Vanliga frågor</h2><details><summary>Q</summary><p>A</p></details></div>` | Yes |
| 28 | **Method note** | `.ia-method-note` or inline `<p>` | Yes |
| 29 | **Author box** | `<div class="ia-author-box"><div class="ia-author-avatar">XX</div><div>Bio</div></div>` | Yes |
| 30 | **Disclosure** | `<p class="ia-disclosure">LevNytt.se är en oberoende NeoLife-distributör...</p>` | Yes |
| 31 | **Footer scripts** | `<script src="/footer.js" defer></script><script src="/components.js" defer></script>` | Yes |

---

## 2. Root-Level Legacy Articles — 18 Files

These are published informational articles at `/` that predate the PA pipeline.

### 2.1 Template Families

#### Family R1 — "Pillar Authority" (11 files)
**Signature:** `pillar.css` + article-wrap/container/article-body, hero header, breadcrumbs bar, stats-row, authority-nav, tier-section, `<details>` FAQ with FAQPage schema, journey-block.

Files: `ala-vs-epa-vs-dha.html`, `direktforsaljning-fakta.html`, `ekologisk-stadning-greenwashing.html`, `fytosteroler-cellmembran.html`, `karotenoid-tillskott-vs-mat.html`, `personlig-vard.html`, `super-10.html`, `vad-ar-kostfiber.html`, `vad-ar-probiotika.html`, `vaxtbaserade-steroler-dagligen.html`, `zeaxantin-immunforsvar-2025.html`

**PA template match: ~25%** — fundamentally different layout.

#### Family R2 — "ia-wrap Legacy" (4 files)
**Signature:** `ia-wrap` wrapper class, SVG hero image (no gradient), ia-punchline + ia-takeaways, ia-stat-grid, ia-method-table, `<details>` FAQ, NO nav.js at bottom, NO BreadcrumbList schema.

Files: `hur-fungerar-natverksmarknadsforing-egentligen.html`, `magnesiumglycinat-och-somn.html`, `multivitamin-kvinnor-over-40.html`, `vad-ar-vitamin-b12.html`

**PA template match: ~40%** — closest family but missing author box, CTA block, tierbox, disclosure, footer scripts order.

#### Family R3 — "PA-Close" (2 files)
**Signature:** INLINE CSS with :root tokens + pillar.css fallback, freshness banner, PA-style gradient hero (hero section+overlay+breadcrumb+stats), back-link, article-content/article-inner, Sammanfattning callout, italic disclaimer, gold Slutsats callout, Sources section, internal-links-section. **Critically missing:** NO Schema at all, NO FAQ section, NO TOC.

Files: `varfor-fiskolja-inte-ar-likvardigt.html` (113 lines), `viktuppgang-klimakteriet.html` (106 lines)

**PA template match: ~50%** — they match the OLD master template but not the ia-wrap standard.

#### Family R4 — "Calculator Tool" (1 file)
**Signature:** Custom 1000+ line CSS, interactive JavaScript calculators, video section, FAQ accordion (no schema), savings grid. Unique tool page, not an article.

File: `finns-det-billigare-alternativ.html` (1091 lines)

**PA template match: ~5%** — completely different purpose.

### 2.2 Per-File Audit — Family R1 (Pillar Authority)

| File | Lines | Hero | Summary | TOC | FAQ | CTA | Author Box | Tier Box | Schema | Key Diffs from PA Template |
|---|---|---|---|---|---|---|---|---|---|---|
| ala-vs-epa-vs-dha | 118 | pillar hero hdr | ia-punchline+takeaways | No | details+FAQPage | No | No | tier-section | Article+FAQ+Breadcrumb | No ia-wrap, no CTA, no author, old hero |
| direktforsaljning-fakta | 125 | pillar hero hdr | ia-punchline+takeaways | No | details+FAQPage | No | No | tier-section | Article+FAQ+Breadcrumb | Same as above |
| ekologisk-stadning-greenwashing | 127 | pillar hero hdr | ia-punchline+takeaways | No | details+FAQPage | No | No | tier-section | Article+FAQ+Breadcrumb | Same |
| fytosteroler-cellmembran | 467 | pillar hero hdr | ia-punchline+takeaways | No | details+FAQPage | No | No | tier-section | Article+FAQ+Breadcrumb | +research-box, +evidence-tag |
| karotenoid-tillskott-vs-mat | 123 | pillar hero hdr | ia-punchline+takeaways | No | details+FAQPage | No | No | tier-section | Article+FAQ+Breadcrumb | Standard pillar |
| personlig-vard | 422 | pillar hero hdr | ia-punchline+takeaways | No | details+FAQPage | No | No | tier-section | CollectionPage+FAQ+Breadcrumb | Wrong schema type |
| super-10 | 115 | pillar hero hdr | ia-punchline+takeaways | No | details+FAQPage | No | No | tier-section | Article+FAQ+Breadcrumb | Standard pillar |
| vad-ar-kostfiber | 138 | pillar hero hdr | ia-punchline+takeaways | No | details+FAQPage | No | No | tier-section | Article+FAQ+Breadcrumb | Standard pillar |
| vad-ar-probiotika | 141 | pillar hero hdr | ia-punchline+takeaways | No | details+FAQPage | No | No | tier-section | Article+FAQ+Breadcrumb | Standard pillar |
| vaxtbaserade-steroler-dagligen | 121 | pillar hero hdr | ia-punchline+takeaways | No | details+FAQPage | No | No | tier-section | Article+FAQ+Breadcrumb | Standard pillar |
| zeaxantin-immunforsvar-2025 | 660 | pillar hero hdr | ia-punchline+takeaways | No | details+FAQPage | No | No | tier-section | Article+FAQ+Breadcrumb | Largest pillar article |

### 2.3 Per-File Audit — Family R2 (ia-wrap Legacy)

| File | Lines | Hero | Nav.js bottom | CTA | Author Box | Tier Box | Schema | Key Diffs |
|---|---|---|---|---|---|---|---|---|
| hur-fungerar-natverksmarknadsforing | 349 | SVG image | **Missing** | ia-cta present | No | No | Article+FAQ (no Breadcrumb) | Missing nav.js at bottom, missing author box, missing tierbox |
| magnesiumglycinat-och-somn | 317 | SVG image | **Missing** | ia-cta present | No | No | Article+FAQ (no Breadcrumb) | Same gaps |
| multivitamin-kvinnor-over-40 | 406 | SVG image | **Missing** | ia-cta present | No | No | Article+FAQ (no Breadcrumb) | Same gaps |
| vad-ar-vitamin-b12 | 430 | SVG image | **Missing** | No | No | No | Article+FAQ (no Breadcrumb) | Largest gap — missing CTA, author, tierbox |

### 2.4 Per-File Audit — Families R3 & R4

| File | Lines | Summary | FAQ | Schema | CTA | Author Box | Tier Box | Key Issues |
|---|---|---|---|---|---|---|---|---|
| varfor-fiskolja-inte-ar-likvardigt | 113 | Sammanfattning callout ✓ | **Missing** | **None** | No | No | No | No Schema, no FAQ, no ia-wrap classes |
| viktuppgang-klimakteriet | 106 | Sammanfattning callout ✓ | **Missing** | **None** | No | No | No | No Schema, no FAQ, no ia-wrap classes |
| finns-det-billigare-alternativ | 1091 | Calc tool page | Custom accordion | **None** | No | No | No | Unique calculator tool — separate migration strategy needed |

---

## 3. content/articles/ Source Files — 17 Files

Source articles in `content/articles/` not yet deployed via Publication Agent.

### 3.1 Template Families

#### Family S1 — "ia-wrap Compact" (8 files)
**Signature:** `pillar.css` + inline CSS, `.ia-wrap` wrapper, flat header (ia-eyebrow + h1 + ia-meta), ia-punchline + ia-takeaways, `<details>` FAQ, nav.js + footer.js + components.js. Schema: Article + FAQPage in @graph (no BreadcrumbList). Inline SVG stat cards.

**PA template match: ~55%** — same ia-wrap base but missing author box, CTA block, tierbox, disclosure.

Files: `ar-miljovanliga-rengoringsmedel-lika-effektiva.html`, `c-vitamin-tillskott-vs-serum-huden.html`, `hudtecken-naringsbrist.html`, `lutein-zeaxantin-huden.html`, `nya-kostrad-65-plus-d-vitamin-magnesium.html`, `retinol-pa-sommaren.html`, `vad-ar-niacinamid.html`, `vilken-magnesiumform-ar-bast.html`

#### Family S2 — "ia-wrap Large / Authority" (5 files)
**Signature:** Same CSS approach but with gradient hero (`.hero`), breadcrumbs, `.stats-row`, `.article-wrap` > `.article-body` structure. Gold callout. `<details>` FAQ. NO Article/Breadcrumb/FAQPage schema in head (some have it). Larger articles with more content depth.

**PA template match: ~30%** — mixes pillar authority and ia-wrap patterns.

Files: `ar-dyra-kosttillskott-verkligen-battre.html`, `cellmembran-funktion.html`, `naringsbrist.html`, `vad-ar-vaxtsteroler.html`, `varfor-ar-jag-trott-hela-tiden.html`

#### Family S3 — "Trust Architecture" (3 files)
**Signature:** `WebPage` schema type (not Article), custom section-label system, Journey Block + Tier Boxes, Authority CTA, Editorial Signal. NO components.js.

**PA template match: ~30%** — wrong schema type, custom navigation layer.

Files: `forsknings-faq.html`, `levnytt-principer.html`, `var-metod.html`

#### Family S4 — "naringsbrist-symptom" (1 file)
**Signature:** Like Family S1 but uses Georgia font, has Tier boxes inline, product CTA. 445 lines.

**PA template match: ~35%**

File: `naringsbrist-symptom.html`

### 3.2 Per-File Audit

| # | File | Lines | Family | Hero | CTA | Author Box | Tier Box | Schema | Match % |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ar-dyra-kosttillskott-verkligen-battre | 465 | S2 | Gradient+bread+stats | No | No | No | None | 30% |
| 2 | ar-miljovanliga-rengoringsmedel | 188 | S1 | Flat ia-wrap | No | No | No | Art+FAQ (no BC) | 55% |
| 3 | cellmembran-funktion | 985 | S2 | Gradient+bread+stats | No | No | No | None | 30% |
| 4 | c-vitamin-tillskott-vs-serum | 217 | S1 | Flat ia-wrap | No | No | No | Art+FAQ (no BC) | 55% |
| 5 | forsknings-faq | 892 | S3 | Gradient+bread | No | No | Journey/tier | Web+BC+FAQ | 30% |
| 6 | hudtecken-naringsbrist | 227 | S1 | Flat ia-wrap | No | No | No | Art+FAQ (no BC) | 55% |
| 7 | levnytt-principer | 824 | S3 | Gradient+bread | No | No | Journey/tier | Web+BC+FAQ | 30% |
| 8 | lutein-zeaxantin-huden | 217 | S1 | Flat ia-wrap | No | No | No | Art+FAQ (no BC) | 55% |
| 9 | naringsbrist | 796 | S2 | Gradient+bread+stats | No | No | No | None | 30% |
| 10 | naringsbrist-symptom | 445 | S4 | Flat ia-wrap | Product CTA | No | Inline tiers | Art+FAQ (no BC) | 35% |
| 11 | nya-kostrad-65-plus | 166 | S1 | Flat ia-wrap | No | No | No | Art+FAQ (no BC) | 55% |
| 12 | retinol-pa-sommaren | 230 | S1 | Flat ia-wrap | No | No | No | Art+FAQ (no BC) | 55% |
| 13 | vad-ar-niacinamid | 226 | S1 | Flat ia-wrap | No | No | No | Art+FAQ (no BC) | 55% |
| 14 | vad-ar-vaxtsteroler | 857 | S2 | Gradient+bread+stats | No | No | No | None | 30% |
| 15 | varfor-ar-jag-trott | 1037 | S2 | Gradient+bread+stats | No | No | No | None | 30% |
| 16 | var-metod | 791 | S3 | Gradient+bread | No | No | Journey/tier | Web+BC+FAQ | 30% |
| 17 | vilken-magnesiumform-ar-bast | 283 | S1 | Flat ia-wrap | No | No | No | Art+FAQ (no BC) | 55% |

### 3.3 Universal Gaps — All 17 Source Files

| Component | Present |
|---|---|
| Freshness banner | 0/17 |
| ia-author-box | 0/17 |
| ia-cta block | 1/17 (naringsbrist-symptom only) |
| ia-tierbox | 3/17 (S3 trust pages, different pattern) |
| ia-disclosure (border-top) | 0/17 |
| BreadcrumbList schema | 3/17 |
| Smooth scroll | 0/17 |
| Google verification metas | 0/17 |
| components.js | 14/17 (missing in S3 trust pages) |

---

## 4. Pillar/Authority Pages — 7 Files

These serve a different purpose (brand authority, history, about) but benefit from template cataloging.

### 4.1 Template Families

#### Family P1 — "Historia/Vetenskap" (2 files)
**PA template match: ~30%** — gradient hero, breadcrumbs, stats, TOC, sources, internal-links-section. Uses pillar.css.

Files: `neolife-historia.html` (90% match to old master template), `neolife-vetenskap.html` (85% match to old master template)

#### Family P2 — "Hallbarhet/Golden Home Care" (2 files)
**PA template match: ~25%** — Similar to P1 but missing TOC, missing hero stats, FAQ lacks microdata.

Files: `neolife-hallbarhet.html`, `golden-home-care.html`

#### Family P3 — "Affarsmojlighet" (1 file)
**PA template match: ~15%** — Heavily customized, no freshness banner, no back-link, tier-section instead of internal-links, no smooth scroll.

File: `neolife-affarsmojlighet.html`

#### Family P4 — "Custom Isolated" (2 files)
**PA template match: ~5%** — Completely custom designs. `den-fundersamma-mannen.html` uses ia-prefix classes with custom design system. `om-oss.html` uses WebPage schema, custom masthead, missing nav.js.

Files: `den-fundersamma-mannen.html`, `om-oss.html`

---

## 5. Product Pages — 25 Files

Product pages serve a different purpose and use distinct templates. They are out of scope for article migration but cataloged for completeness.

### Template Families

#### Family PROD-A — "Pillar Informational" (20 files)
**Signature:** `pillar.css`, authority-nav, hero-eyebrow+h1+hero-meta, stats-row, ia-punchline+ia-takeaways, `<details>` FAQ accordion, tier-section, author-box, journey-block. Dated June 2026.

Files: `neolife-all-c.html`, `betaguard`, `botanical-balance`, `carotenoid-complex` (526L), `chelated-zinc`, `coq10`, `cruciferous-plus`, `flavonoid-complex`, `formula-iv` (296L), `garlic-allium`, `kalmag-plus-d` (168L), `magnesium-complex` (322L), `omega-3-plus` (333L), `pro-vitality` (318L), `resp-x`, `tre-en-en-cellnaring` (300L), `upbeet`, `vitamin-d` (306L), `vitamin-e`, `vita-squares`

**PA template match: ~15%** — fundamentally different layout.

#### Family PROD-B — "Old-style Master-derived" (5 files)
**Signature:** Inline CSS, freshness banner, master-template nav, gradient hero with overlay+stats, back-link, itemscope FAQ, sources block, internal-links-section. Dated May 2026.

Files: `neolife-acidophilus-plus.html` (186L), `elevate` (264L), `shake-bar-tea` (203L), `tre-en-en` (559L), `viktkontroll` (468L)

**PA template match: ~20%** — closer to the old master template than to ia-wrap.

---

## 6. Migration Complexity Assessment

| Template Family | Count | Match to PA Template | Complexity | Migration Strategy |
|---|---|---|---|---|
| **PA Articles (baseline)** | 26 | 100% | **None** | Already compliant |
| **S1 — ia-wrap Compact** | 8 | 55% | **Low** | Add author box, CTA, tierbox, disclosure. Closest to target. |
| **S4 — naringsbrist-symptom** | 1 | 35% | **Medium** | Standardize classes, add missing components |
| **R2 — ia-wrap Legacy** | 4 | 40% | **Medium** | Fix nav.js at bottom, add author box, CTA, tierbox, disclosure, BreadcrumbList schema |
| **S2 — ia-wrap Large/Authority** | 5 | 30% | **Medium-High** | Needs hero conversion, add schema, standardize wrapper classes |
| **R1 — Pillar Authority** | 11 | 25% | **High** | Complete restructure: hero → flat ia-wrap, replace article-wrap with ia-wrap, add all PA components |
| **R3 — PA-Close** | 2 | 50% | **Medium** | Closest to OLD master template. Needs FAQ, Schema, ia-wrap conversion |
| **S3 — Trust Architecture** | 3 | 30% | **High** | Schema change (WebPage→Article), remove journey/tier navigation layer, standardize |
| **R4 — Calculator Tool** | 1 | 5% | **Special** | Unique interactive tool. Keep separate or rebuild as embedded widget. |
| **P1-P4 — Pillar Pages** | 7 | 15-30% | **High** | Different purpose. Consider keeping as separate template family. |
| **PROD-A/B — Product Pages** | 25 | 15-20% | **Special** | Different purpose. Separate template family. |

### Complexity Summary

| Complexity | Count | Articles |
|---|---|---|
| **Low** (55%+ match) | 8 | S1 family — needs only author box, CTA, tierbox, disclosure |
| **Medium** (35-55% match) | 7 | S4 + R2 + R3 families |
| **Medium-High** (25-35% match) | 5 | S2 family |
| **High** (<25% match) | 14 | R1 family + S3 family |
| **Special** | 1 | R4 — calculator tool |
| **Out of scope** | 32 | Pillar pages (7) + Product pages (25) — separate template families |

---

## 7. Components That Differ from PA Template

### Components present in legacy articles but ABSENT from PA template

| Legacy Component | PA Template Equivalent | Action |
|---|---|---|
| Freshness banner (`<div class="freshness-banner">`) | None | **Remove** — PA template doesn't use it |
| Gradient hero (`<section class="hero">` with overlay) | Flat ia-eyebrow + h1 header | **Replace** with flat header |
| Back-link (`<div class="back-link-wrapper">`) | None | **Remove** |
| Gold conclusion callout (`.callout.callout-gold`) | None explicitly | Fold into ia-callout or remove |
| Sammanfattning summary callout | ia-punchline | **Replace** with ia-punchline |
| TOC (`.toc` with `<ol>`) | None | **Remove** — PA template doesn't use TOC |
| Internal-links-section (`<section class="internal-links-section">`) | ia-tierbox | **Replace** with ia-tierbox |
| Sources block (inline border-top paragraph) | ia-disclosure + inline refs | **Replace** |
| Journey block (breadcrumb-style nav) | None | **Remove** |
| Authority-nav (`.authority-nav` div) | None | **Remove** |
| Inline `<nav>` element | `<div id="site-nav">` placeholder | **Replace** |
| Itemscope FAQ microdata in body | `<details>/<summary>` accordion | **Replace** — schema only in JSON-LD head |
| Stats-row (`.stats-row` separate section) | ia-stat-grid inline | **Replace** |
| Tier-section (`.tier-section` grid) | ia-tierbox | **Replace** |
| Smooth scroll inline script | CSS `scroll-behavior: smooth` | **Remove** inline script |

### Components in PA template but ABSENT from most legacy articles

| PA Component | Present in Legacy | Migration Action |
|---|---|---|
| ia-author-box (avatar + bio) | Near 0% | **Add** to all |
| ia-cta (product CTA block) | ~10% | **Add** to all |
| ia-tierbox (4-link grid) | ~15% (different pattern) | **Add** to all |
| ia-disclosure (border-top disclaimer) | ~0% | **Add** to all |
| ia-evidence-label (Tier badges) | ~15% | **Add** to all health articles |
| OG image + Twitter card metas | ~60% | **Add** where missing |
| Google verification metas | ~0% | **Add** to all |
| BreadcrumbList schema | ~20% | **Add** to all |
| components.js script | ~80% | **Add** where missing |

---

## 8. Components That Can Be Standardized

### Shared CSS classes (move to pillar.css)

These ia-* class patterns are duplicated inline across 26 PA articles and 8 S1 source files:

| CSS Class | Used By | Standardize? |
|---|---|---|
| `.ia-wrap` | PA + S1 + R2 families | **Yes** — 60+ articles use identical CSS |
| `.ia-punchline` | PA + S1 + R2 | **Yes** |
| `.ia-takeaways` | PA + S1 + R2 | **Yes** |
| `.ia-stat-grid`, `.ia-stat-card` | PA + S1 + R2 | **Yes** |
| `.ia-method-table` | PA + S1 + R2 | **Yes** |
| `.ia-callout` | PA + S1 + R2 | **Yes** |
| `.ia-evidence-label`, `.ia-ev-t1–t4` | PA articles | **Yes** |
| `.ia-faq`, `.ia-faq details/summary` | PA + S1 + R2 | **Yes** |
| `.ia-tierbox`, `.ia-tier` | PA articles | **Yes** |
| `.ia-cta` | PA + some legacy | **Yes** |
| `.ia-author-box`, `.ia-author-avatar` | PA articles | **Yes** |
| `.ia-disclosure` | PA articles | **Yes** |

**Recommendation:** Extract these 12 class groups into `pillar.css` before migration begins. This reduces per-article inline CSS from ~80 lines to ~10 lines of page-specific overrides.

### Shared JS patterns

| Pattern | Standardize? |
|---|---|
| `nav.js` defer placement | **Yes** — standardize `<div id="site-nav">` + `<script src="/nav.js" defer></script>` at top of body |
| `footer.js` + `components.js` at bottom | **Yes** — always defer both |
| FAQ accordion behavior | Already handled by native `<details>` |

---

## 9. Components That Can Be Removed After Migration

Once all legacy articles are migrated to the PA ia-wrap template:

| Component | Files Affected | Notes |
|---|---|---|
| Freshness banner | R3 family (2), PROD-B (5), pillar pages (4) | PA template doesn't use it |
| `.back-link-wrapper` | R3 family (2), PROD-B (5) | Not in PA template |
| `.toc` with `<ol>` | neolife-historia, neolife-vetenskap, PROD-B (2) | PA template doesn't use TOC |
| `.callout.callout-gold` (Slutsats) | R3 family (2), pillar pages (3) | Fold into content or remove |
| `.internal-links-section` | R3 family (2), pillar pages (4), PROD-B (5) | Replace with ia-tierbox |
| `.authority-nav` | All R1 family (11), pillar pages (5) | PA template has no authority-nav |
| `.journey-block` | R1 family (11), trust pages (3) | Not in PA template |
| `.tier-section` | R1 family (11), PROD-A (20) | Replace with ia-tierbox |
| `itemscope` FAQ microdata in body | Old master-template pages | PA puts FAQ schema in JSON-LD head only |
| Inline smooth scroll script | R3 family (2), pillar pages (3) | Use CSS `scroll-behavior` |
| `levnytt-se-master-template.html` | N/A | Archive — no longer canonical |

---

## 10. Migration Priority & Sequencing

### Phase 1 — Low Complexity (8 files)
**Family S1 — ia-wrap Compact.** These already use ia-wrap base. Migration = add author box, CTA, tierbox, disclosure, og metas, verification metas.

1. ar-miljovanliga-rengoringsmedel-lika-effektiva.html
2. c-vitamin-tillskott-vs-serum-huden.html
3. hudtecken-naringsbrist.html
4. lutein-zeaxantin-huden.html
5. nya-kostrad-65-plus-d-vitamin-magnesium.html
6. retinol-pa-sommaren.html
7. vad-ar-niacinamid.html
8. vilken-magnesiumform-ar-bast.html

**Estimated effort:** ~30 min per file. Total: 4 hours.

### Phase 2 — Medium Complexity (7 files)
**Families S4 + R2 + R3.** Already close to ia-wrap or master template. Need moderate restructuring.

1. naringsbrist-symptom.html (S4)
2. hur-fungerar-natverksmarknadsforing-egentligen.html (R2)
3. magnesiumglycinat-och-somn.html (R2)
4. multivitamin-kvinnor-over-40.html (R2)
5. vad-ar-vitamin-b12.html (R2)
6. varfor-fiskolja-inte-ar-likvardigt.html (R3)
7. viktuppgang-klimakteriet.html (R3)

**Estimated effort:** ~45 min per file. Total: 5.25 hours.

### Phase 3 — Medium-High Complexity (5 files)
**Family S2 — ia-wrap Large/Authority.** Need hero conversion, schema addition, wrapper standardization.

1. ar-dyra-kosttillskott-verkligen-battre.html
2. cellmembran-funktion.html
3. naringsbrist.html
4. vad-ar-vaxtsteroler.html
5. varfor-ar-jag-trott-hela-tiden.html

**Estimated effort:** ~60 min per file. Total: 5 hours.

### Phase 4 — High Complexity (14 files)
**Families R1 + S3.** Complete restructure from pillar authority to ia-wrap.

R1 (11): ala-vs-epa-vs-dha, direktforsaljning-fakta, ekologisk-stadning-greenwashing, fytosteroler-cellmembran, karotenoid-tillskott-vs-mat, personlig-vard, super-10, vad-ar-kostfiber, vad-ar-probiotika, vaxtbaserade-steroler-dagligen, zeaxantin-immunforsvar-2025

S3 (3): forsknings-faq, levnytt-principer, var-metod

**Estimated effort:** ~90 min per file. Total: 21 hours.

### Phase 5 — Special (1 file)
**Family R4.** Calculator tool. Needs architectural decision: rebuild as ia-wrap with embedded calculator, or keep as separate interactive tool.

1. finns-det-billigare-alternativ.html

**Estimated effort:** Decision needed before estimating.

---

## 11. Recommendations

1. **Update the canonical template.** Archive `levnytt-se-master-template.html` or rewrite it to reflect the actual ia-wrap standard. It currently describes a layout that no PA article uses.

2. **Extract ia-* CSS to pillar.css first.** Before migrating any article, add the 12 shared ia-* class groups to `pillar.css`. This eliminates ~80 lines of duplicated inline CSS from every article.

3. **Create an ia-wrap article template file.** A new reference template matching the actual PA output (e.g., `ia-wrap-article-template.html`) that can be used as the migration target for all legacy articles.

4. **Standardize schema generation.** All PA articles use @graph (Article + FAQPage). Legacy articles use various combinations. Pick one format and apply consistently.

5. **Consider pillar page migration separately.** The 7 pillar/authority pages serve a different purpose. They may not need full ia-wrap conversion. A pillar-specific template may be more appropriate.

6. **Product pages are a separate concern.** The 25 product pages (20 Pillar Informational + 5 Old-style) use their own templates. They should be audited and migrated in a separate sprint.

---

## 12. Summary

| Metric | Value |
|---|---|
| **Total legacy pages audited** | 67 |
| **Publication Agent articles (baseline)** | 26 |
| **Template/layout families identified** | 14 distinct families |
| **PA template components defined** | 31 |
| **Average match to PA template (article pages)** | ~30% |
| **Articles requiring Low migration effort** | 8 |
| **Articles requiring Medium effort** | 7 |
| **Articles requiring Medium-High effort** | 5 |
| **Articles requiring High effort** | 14 |
| **Special cases** | 1 (calculator tool) |
| **Pages in separate template families** | 32 (pillar + product) |
| **Components that can be standardized** | 12 CSS class groups + 2 JS patterns |
| **Components that can be removed** | 11 legacy component types |
| **Estimated total migration effort** | ~35 hours (excluding Phase 5) |
| **Prerequisite** | Extract ia-* CSS to pillar.css |

---

*Audit prepared by OpenCode Editorial System. No articles were modified. This is a read-only analysis.*
