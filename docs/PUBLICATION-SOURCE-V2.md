# PUBLICATION-SOURCE-V2.md
# LevNytt.se — Publication Source Format V2

**Date:** 2026-07-02  
**Status:** FROZEN — source format for Sprint 21 Markdown-first implementation  
**Scope:** Informational articles published via `content/articles/<slug>/<slug>.md`  
**Supersedes:** `docs/PUBLICATION-SOURCE-SPEC.md` (V1) and `docs/PAGE-BUILDER-MARKDOWN-SPEC.md` (incomplete)  

---

## Design Principle

The Publication Source is the minimum set of fields an author must write to produce a PAS V1.0-compliant article.

**Author-owned:** fields that are unique to this article and cannot be derived elsewhere.  
**System-generated:** fields that are constant, derivable from author fields, or set by the Publication Agent at deploy time. These fields are not in the source file.

An author should never write a field the system can generate. A system should never require a field the author cannot know.

---

## What Changed from V1

V1 (`PUBLICATION-SOURCE-SPEC.md`) mixed author fields with system fields in the same frontmatter block, used commented-out YAML (`# title: "..."`), and included a full `schema:` block that duplicated data already present in other fields.

V2 removes all of that:

| Removed from V2 | Reason |
|---|---|
| `# field: value` syntax | Not valid YAML. All fields use standard `key: value`. |
| `date_published` | Set by Publication Agent at first deploy. Not author-owned. |
| `date_modified` | Set by Publication Agent at each deploy. Not author-owned. |
| `template` | Always `article` for informational articles. Constant, not author-owned. |
| `schema:` block | Entirely derived from other fields + system constants + deploy dates. Not author-owned. |
| `hero:` block | Informational articles do not have hero sections (PAS V1.0 — hero components are forbidden). |

V2 adds fields that PAS V1.0 requires but V1 had no provision for:

| Added in V2 | Reason |
|---|---|
| `eyebrow` | PAS Section 11 — ia-eyebrow display tag |
| `author.initials` | PAS Section 26 — ia-author-avatar 2-letter initial |
| `author.bio` | PAS Section 26 — ia-author-box bio text |
| `reading_time` | PAS Section 13 — byline reading time |
| `punchline` | PAS Section 14 — ia-punchline paragraph |
| `takeaways` | PAS Section 15 — ia-takeaways bullet list |
| `method_note` | PAS Section 21 — ia-method-note text |
| `tierbox` | PAS Section 22 — ia-tierbox 4 internal links |
| `cta` | PAS Section 23 — ia-cta product block |
| `disclosure` | PAS Section 25 — ia-disclosure methodology note |
| `faq` | PAS Section 24 — ia-faq question/answer pairs |

---

## V2 Frontmatter Format

All fields use standard YAML. No comments on field keys. No schema block. No hero block.

```yaml
---
title: "Article title — descriptive subtitle"
description: "SEO description, maximum 155 characters. One sentence."
slug: "article-slug"
category: "Mineraler"
eyebrow: "Kosttillskott · Forskning"

author:
  name: "Jarmo Halonen"
  url: "https://levnytt.se/den-fundersamma-mannen"
  initials: "JH"
  bio: "Jarmo Halonen är grundaren av LevNytt och en oberoende NeoLife-distributör med fokus på evidensbaserad hälsoinformation."

updated: "2026-07-02"
reading_time: 7

punchline: >
  One-paragraph value proposition. The central claim of the article. May contain
  <strong>bold text</strong> on the key assertion.

takeaways:
  - "First takeaway. <span class=\"ia-evidence-label ia-ev-t1\">Tier 1</span>"
  - "Second takeaway with source: (<a href=\"https://pubmed.ncbi.nlm.nih.gov/12345678/\">Author et al., 2024</a>). <span class=\"ia-evidence-label ia-ev-t2\">Tier 2</span>"
  - "Third takeaway — standalone fact. <span class=\"ia-evidence-label ia-ev-t3\">Tier 3</span>"
  - "Fourth takeaway with practical guidance."

method_note: >
  Denna artikel bygger på systematiska översikter och kliniska studier från PubMed.
  Granskning genomförd juli 2026. Artikeln ersätter inte medicinsk rådgivning.

tierbox:
  - label: "Tier 1"
    url: "https://levnytt.se/neolife-historia"
    title: "Historia & Vetenskap"
  - label: "Tier 2"
    url: "https://levnytt.se/magnesium-komplett-guide"
    title: "Komplett guide om magnesium"
  - label: "Tier 3"
    url: "https://levnytt.se/neolife-tre-en-en"
    title: "NeoLife Tre-en-en"
  - label: "Tier 4"
    url: "https://levnytt.se/den-fundersamma-mannen"
    title: "Om skribenten"

cta:
  headline: "Vill du förbättra din stresshantering?"
  body: "NeoLife Magnesium är formulerat för optimal biotillgänglighet med magnesiumbisglycinat."
  url: "https://levnytt.se/neolife-kosttillskott/"
  link_text: "Se NeoLife Magnesium →"

cta_secondary:
  url: "https://levnytt.se/magnesium-komplett-guide"
  text: "eller läs den kompletta guiden om magnesium"

disclosure: >
  <strong>Metodnotering:</strong> YMYL-klassificerad artikel om kosttillskott och hälsa.
  Alla påståenden är kopplade till evidensnivå (Tier 1–4). Källor inkluderar PubMed,
  EFSA och Livsmedelsverket. Se <a href="https://levnytt.se/var-metod">Vår Metod</a>
  för information om hur vi bedömer evidens.

faq:
  - q: "Hur påverkar magnesium stressnivåerna?"
    a: "Magnesium reglerar HPA-axeln och kortisolproduktionen, vilket dämpar kroppens stressrespons."
  - q: "Vilken dos magnesium rekommenderas mot stress?"
    a: "Vuxna behöver 310–420 mg per dag. Vid stress kan 200–300 mg extra vara aktuellt."
  - q: "Vilken form av magnesium är bäst?"
    a: "Magnesiumbisglycinat rekommenderas ofta för stresshantering — god biotillgänglighet och skonsamt för magen."
  - q: "Hur lång tid tar det att märka effekt?"
    a: "Många märker förbättring inom några dagar till en vecka vid kontinuerligt intag."
  - q: "Kan jag ta magnesium utan brist?"
    a: "Ja. Magnesiumtillskott kan vara fördelaktigt vid stress även utan påvisad brist."
  - q: "Finns det biverkningar?"
    a: "Höga doser kan ge diarré. Håll dig till rekommenderade doser och rådfråga läkare vid medicinska tillstånd."
---
```

---

## Field Reference

### Core metadata

| Field | Type | Required | Constraint |
|---|---|---|---|
| `title` | string | Yes | Full article title. Used in `<title>` (truncated if needed), `og:title`, JSON-LD headline. |
| `description` | string | Yes | Maximum 155 characters. Used in `<meta name="description">`, `og:description`, `twitter:description`. |
| `slug` | string | Yes | URL-friendly identifier. Lowercase, hyphenated. Determines canonical URL, `og:url`, JSON-LD `url` and `@id`. |
| `category` | string | Yes | Content category. Displayed as the category label `<p>` at the top of the article body. Example: `Mineraler`, `Vitaminer`, `Hälsa`. |
| `eyebrow` | string | Yes | Short category tag for `ia-eyebrow`. 2–3 words, separated by ` · `. Example: `Kosttillskott · Forskning`. |

### Author

| Field | Type | Required | Constraint |
|---|---|---|---|
| `author.name` | string | Yes | Author full name. Used in byline, ia-author-box, JSON-LD `author.name`. |
| `author.url` | string | Yes | Author page URL. Used in byline link, ia-author-box link, JSON-LD `author.url`. |
| `author.initials` | string | Yes | Exactly 2 uppercase letters. Used in `ia-author-avatar`. Example: `JH` for Jarmo Halonen. |
| `author.bio` | string | Yes | 1–2 sentences. Used in `ia-author-box` bio paragraph with link to `author.url`. |

### Timing and reading

| Field | Type | Required | Constraint |
|---|---|---|---|
| `updated` | string | Yes | ISO 8601 date: `YYYY-MM-DD`. Displayed in byline as "Senast uppdaterad: [month] [year]" (e.g., `2026-07-02` → "juli 2026"). Also used as `datePublished` and `dateModified` in JSON-LD on first publication. |
| `reading_time` | integer | Yes | Estimated reading time in minutes. Displayed in byline as "X min läsning". |

### Article components

| Field | Type | Required | Constraint |
|---|---|---|---|
| `punchline` | string | Yes | Single paragraph. The article's value proposition. May contain inline HTML (`<strong>`, `<a>`). Rendered as `ia-punchline`. |
| `takeaways` | list of strings | Yes | 4–7 items. Each item is a self-contained insight. Inline HTML is permitted for evidence labels and source links. Rendered as `ia-takeaways` bullet list. |
| `method_note` | string | Yes | 1–3 sentences describing research methodology, review date, and disclaimer. Rendered as `ia-method-note` before the tier box. |
| `tierbox` | list of objects | Yes | Exactly 4 items. Each item: `label` (string: "Tier 1"–"Tier 4"), `url` (string), `title` (string). Rendered as `ia-tierbox`. |
| `cta` | object | Yes | Fields: `headline` (string), `body` (string, 1–2 sentences), `url` (string), `link_text` (string). Rendered as `ia-cta`. |
| `cta_secondary` | object | **No** | Optional. Fields: `url` (string), `text` (string). Rendered as `ia-cta-secondary` paragraph inside the CTA block. Omit the field entirely if not needed. |
| `disclosure` | string | Yes | Methodology disclosure paragraph. HTML is permitted. Begins with `<strong>Metodnotering:</strong>`. Links to 1–3 related pages. Rendered as first `ia-disclosure` (before author box). |
| `faq` | list of objects | Yes | 6–10 items. Each item: `q` (string, question text), `a` (string, answer text, 2–4 sentences). Rendered as `ia-faq` with native `<details>/<summary>` accordion. Questions are also included in JSON-LD FAQPage schema. |

---

## Body format

The Markdown body follows the YAML frontmatter block. It contains only prose sections. All mandatory PAS components with structured data are driven by frontmatter fields — not body content.

### Permitted body elements

| Markdown | HTML output |
|---|---|
| `## Section heading` | `<h2>Section heading</h2>` |
| `### Sub-section` | `<h3>Sub-section</h3>` |
| Paragraph text | `<p>text</p>` |
| `**bold**` | `<strong>bold</strong>` |
| `[text](url)` | `<a href="url">text</a>` |
| `- item` | `<li>item</li>` inside `<ul>` |
| `\| Table \|` | `<table class="ia-method-table">` |
| Raw inline HTML | Passed through unchanged |

Evidence labels are written as raw inline HTML directly in the body:

```markdown
Magnesium reglerar HPA-axeln. <span class="ia-evidence-label ia-ev-t2">Tier 2</span>
```

### Body constraints

- Do not include the punchline, Key Takeaways, method note, tier box, CTA, FAQ, disclosure, or author box in the body — these are generated from frontmatter fields.
- Do not include `<h1>` — the title is generated from `title`.
- Minimum 3 `h2` sections with substantive paragraph content.
- No `<h4>` or deeper nesting.
- Internal links use absolute URLs (`https://levnytt.se/slug`).
- PubMed links use full absolute URLs.

---

## What the system generates

These elements are produced by the conversion script from author fields or from system constants. The author never writes them.

### From author fields

| Generated element | Source fields |
|---|---|
| `<title>Article title | LevNytt</title>` | `title` (truncated to ≤57 chars before ` \| LevNytt`) |
| `<meta name="description">` | `description` |
| `<link rel="canonical">` | `slug` |
| `og:title`, `twitter:title` | `title` |
| `og:description`, `twitter:description` | `description` |
| `og:url` | `slug` |
| JSON-LD `Article.headline` | `title` |
| JSON-LD `Article.url` | `slug` |
| JSON-LD `Article.author` | `author.name`, `author.url` |
| JSON-LD `FAQPage.mainEntity` | `faq[].q`, `faq[].a` |
| Category label `<p>` | `category` |
| `<div class="ia-eyebrow">` | `eyebrow` |
| `<h1>` | `title` |
| Author byline `<p>` | `author.name`, `author.url`, `updated`, `reading_time` |
| `<p class="ia-punchline">` | `punchline` |
| `<div class="ia-takeaways">` | `takeaways` |
| `<div class="ia-method-note">` | `method_note` |
| `<div class="ia-tierbox">` | `tierbox` |
| `<div class="ia-cta">` | `cta`, `cta_secondary` |
| `<div class="ia-faq">` | `faq` |
| First `<p class="ia-disclosure">` | `disclosure` |
| `<div class="ia-author-box">` | `author.name`, `author.url`, `author.initials`, `author.bio` |

### System constants (never in source file)

| Generated element | Value |
|---|---|
| `date_published` in JSON-LD | Set by Publication Agent at first deploy |
| `date_modified` in JSON-LD | Set by Publication Agent at each deploy |
| Google verification meta | `kAcoLDFGCpGh42gIFRgPeWlC253vTP3OLBs6wI8KDQ0` |
| Pinterest verification meta | `6a9e88f7014abe0735767f464c08f337` |
| `og:type` | `article` |
| `og:site_name` | `LevNytt` |
| `og:locale` | `sv_SE` |
| `og:image` | `https://levnytt.se/assets/brand/og-brand.png` |
| `og:image:width` | `1200` |
| `og:image:height` | `630` |
| `og:image:alt` | `LevNytt — En oberoende NeoLife-distributör` |
| `twitter:card` | `summary_large_image` |
| JSON-LD `Article.publisher` | `{name: "LevNytt", url: "https://levnytt.se"}` |
| JSON-LD `mainEntityOfPage` | `{"@type": "WebPage", "@id": "https://levnytt.se/<slug>"}` |
| Font preconnects + link | Google Fonts (Playfair Display + Inter) |
| `<link rel="stylesheet">` | `/pillar.css` |
| Full `<style>` ia-* CSS block | Verbatim from PAS V1.0 Section 7 |
| `<div id="site-nav">` + nav.js | PAS Section 8 |
| `<div class="ia-wrap"><article>` | PAS Section 9 |
| `<script src="/footer.js">` | PAS Section 28 |
| `<script src="/components.js">` | PAS Section 28 |
| Second `ia-disclosure` (legal) | Verbatim: "LevNytt.se är en oberoende NeoLife-distributörswebbplats (Sponsor-ID: 41-830928)..." |

---

## Field constraints summary

| Field | Constraint |
|---|---|
| `title` | No hard limit in source. Conversion script truncates `<title>` tag to ≤57 characters before appending ` \| LevNytt` (QA gate Q11 requires ≤60 total). `og:title` uses the full title. |
| `description` | Maximum 155 characters. Conversion script rejects values over limit. (QA gate Q12.) |
| `slug` | Lowercase, hyphenated, no special characters, no Swedish letters in slug. Example: `magnesium-och-stress`. |
| `author.initials` | Exactly 2 characters, uppercase. |
| `updated` | ISO 8601 format: `YYYY-MM-DD`. |
| `reading_time` | Integer only. No unit string. Conversion script appends "min läsning". |
| `takeaways` | 4–7 items. Fewer than 4 fails QA semantically; more than 7 is editorial overload. |
| `tierbox` | Exactly 4 items. PAS Section 22 is strict on count. |
| `faq` | Minimum 6 items. Maximum 10. (QA gate Q10 checks FAQPage schema presence; fewer than 6 is a PAS violation.) |
| `punchline` | Single paragraph only. No `<h2>` or block elements. |
| `cta_secondary` | Omit the field entirely when not used. Do not use `null` or empty string. |

---

## Compatibility with the existing Page Builder

The conversion script (`scripts/md-to-article.py`, to be written in Sprint 21) reads a V2 source file and produces a `.html` file that is structurally identical to an article produced by the LevNytt Writer agent. The output passes `scripts/qa-article.sh` 12/12 and is deployed by the Publication Agent without modification.

No changes are made to:
- `pillar.css`
- `nav.js` / `footer.js` / `components.js`
- `scripts/qa-article.sh`
- The Publication Agent
- Any existing production articles

V2 source files are stored at `content/articles/<slug>/<slug>.md`. The conversion script writes the HTML to `content/articles/<slug>/<slug>.html` in the same directory, matching the path convention established by the existing pipeline.

---

## Migration note for existing source files

`content/articles/magnesium-och-stress/magnesium-och-stress.md` was created under the old V1 commented-YAML format. It is not a V2-compliant file and must be rewritten before it can be used as input to the conversion script. The prose content in the body may be reused but the frontmatter must be replaced entirely. The existing `magnesium-och-stress.html` root page is live and must not be overwritten by the first V2 test article — use a different slug.

---

*This document is the frozen source format specification for the Sprint 21 Markdown-first implementation. No code was written during its preparation.*
