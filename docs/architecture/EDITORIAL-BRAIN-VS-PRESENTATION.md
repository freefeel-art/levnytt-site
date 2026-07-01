# Editorial Brain vs Presentation Layer

## Purpose

Analyze the current Informational Article Skill (`/home/yampa/.claude/skills/informational-article/SKILL.md`) and separate it into two distinct concerns:

1. **Editorial Brain** — content logic, writing rules, SEO/GEO strategy, source requirements, voice guidelines, verification logic. These are **site-independent** rules that any presentation layer must follow.
2. **Presentation Layer** — CSS, HTML structure, image embedding, navigation, color values, visual components. These are **site-specific** and can be extracted to external stylesheets and HTML templates.

The goal is NOT to restructure SKILL.md. The goal is to document exactly what belongs where so that future changes to one layer never touch the other.

## File Status

| File | Lines | Role |
|------|-------|------|
| `SKILL.md` | 1257 | **Active skill.** The Writer-modified version with LevNytt-specific additions (Default Author Profile, §6.0 Page Shell, §5.5 writing rules). OpenCode loads this file when the `informational-article` skill is invoked. |
| `SKILL-v2.md` | 1238 | Pre-refactor version. Always asks for author info. Contains same §6.0 Page Shell and editorial content as SKILL.md. |
| `SKILL-v2.before-refactor.md` | 1214 | Backup before `SKILL-v2.md` → `SKILL.md` refactor that added Default Author Profile. |

## Section-by-Section Mapping

Each row maps one section/rule in SKILL.md to either the Editorial Brain, Presentation Layer, or MIXED. Line numbers refer to SKILL.md.

### Design Principles (lines 14-21)

| # | Principle | Layer | Why |
|---|-----------|-------|-----|
| 1 | H1 mandatory in HTML, stripped for WP | **Brain** | Content logic: what heading to use and when to strip it |
| 2 | Two stacked checks (SEO + LLM) | **Brain** | Editorial strategy — what to verify, not how to render |
| 3 | YMYL Reddit-skip rule | **Brain** | Editorial policy for sourcing |
| 4 | Inline-SVG fallback for tier visuals | **Brain** | *Decision logic*: when to use SVG vs image; the SVG template itself is Presentation |
| 5 | Q-A punchline pattern | **Brain** | Content structure — what to write, not how to style |
| 6 | Authority Content Mode always on | **Brain** | Editorial policy |

### Section 0: Authority Content Mode — LevNytt Rules (lines 25-82)

**Layer: PURE EDITORIAL BRAIN**

Everything here is editorial policy: health claim requirements, source hierarchy, evidence labeling, language restrictions. Zero CSS or HTML.

### Required Inputs (lines 86-141)

**Layer: PURE EDITORIAL BRAIN**

Keyword, target site, author params, article type detection — all editorial input logic. The Default Author Profile (lines 98-114) is editorial configuration.

### Pipeline (lines 145-158)

**Layer: PURE EDITORIAL BRAIN**

Flow description — the sequence of operations. No presentation logic.

### Step 1: Research (lines 162-208)

**Layer: PURE EDITORIAL BRAIN**

Research methodology, search angles, source extraction, citation rules. No presentation logic.

### Step 2: Sitemap — Internal Link Mining (lines 212-282)

**Layer: PURE EDITORIAL BRAIN**

Internal link strategy, destination pages, anchor text rules, link placement logic. No presentation logic.

### Step 3: LSI Keywords & Entity Clustering (lines 285-300)

**Layer: PURE EDITORIAL BRAIN**

Keyword clustering logic. No presentation logic.

### Step 4: Playwright Screenshots (lines 303-358)

**Layer: PRESENTATION LAYER** (the tooling/implementation)

The concept of "capture SERP previews" is borderline, but the Playwright script, screenshot parameters, image processing pipeline, and file naming are implementation details of the presentation. The *decision to include SERP previews* could be Editorial Brain, but the implementation is Presentation.

### Step 5: Generate Images (lines 361-510)

**Layer: MIXED**

| Subsection | Layer | Why |
|-----------|-------|-----|
| GPT Image 2 integration | **Brain** | Tool choice — editorial decision |
| Image policy rules (non-promotional, evidence, etc.) | **Brain** | Content policy |
| Hero image guidance | **Brain** | Content description |
| Infographic text requirements (5+ numbers, sample sizes) | **Brain** | Content requirements |
| Text path verification | **Brain** | Editorial quality check |
| Full prompt table with image descriptions | **Brain** | Content descriptions |
| Color hex values in prompts (#1B4332, #C9A84C) | **Presentation** | Brand colors — visual identity |
| SVG fallback template | **Presentation** | Markup template |
| SVG hex colors, font stacks, dimensions | **Presentation** | Visual styling |

### Step 6: Build HTML (lines 512-983)

**Layer: MOSTLY MIXED** — this is where the entanglement is worst.

#### §6.0 — Page Shell (lines 512-700)

**Layer: PRESENTATION LAYER**

The entire page shell is a verbatim HTML template:
- DOCTYPE, `<html>`, `<head>`, `<meta>`, `<title>`, `<link>`, `<style>`, `<body>`
- Font stacks (`Inter`, `Georgia`, `JetBrains Mono`)
- Color values (`#1B4332`, `#C9A84C`, `#2D6A4F`, `#111827`, etc.)
- Dimension values (`900px`, `28px`)
- `nav.js` include
- Google Fonts preconnect
- CSS reset and base styles
- The entire inline `<style>` block (lines 528-590)

All of this is presentation markup. It depends on Editorial Brain for:
- Which classes exist (`.ia-wrap`, `.ia-punchline`, etc.)
- What content goes in each block

But the *structure and styling* are pure Presentation.

#### §6.1 — Punchline (lines 703-711)

**Layer: EDITORIAL BRAIN** (writing rules + pattern)
**Dependency: Presentation Layer** for the `.ia-punchline` CSS class

The writing rules (open with verbatim question, em-dash, etc.) are Editorial Brain. The HTML structure (`<div class="ia-punchline">`) is a Presentation Layer concern, but it's defined here.

#### §6.2 — Key Takeaways (lines 713-719)

Same pattern as §6.1. Writing rules = Editorial Brain, CSS class = Presentation Layer dependency.

#### §6.3 — Question-Format H2s (lines 721-735)

**Layer: PURE EDITORIAL BRAIN**

Guidelines for phrasing H2s as questions. No presentation logic.

#### §6.4 — Section Templates (lines 737-779)

**Layer: EDITORIAL BRAIN**

Content structure logic: how to organize sections, what to include in each, definition blocks, mechanism explanations, comparison tables. No presentation markup.

#### §6.5 — On-Page Elements (lines 781-816)

**Layer: EDITORIAL BRAIN**

SEO/GEO rules: stat card inclusion, punchline position (<500 chars), external/internal citations, CTA required, author box, FAQ, methodology note. All content requirements.

#### §6.6 — Schema (lines 818-870)

**Layer: MIXED**

| Component | Layer | Why |
|-----------|-------|-----|
| Schema inclusion rules (what to include, what type) | **Brain** | Editorial/SEO decision |
| JSON-LD Article template with variables | **Brain** | Structured data — the *content* is Brain |
| JSON-LD FAQPage template | **Brain** | Same — Brain |
| `@id` URL patterns, author URLs | **Brain** | Editorial configuration |
| The `<script type="application/ld+json">` wrapper | **Presentation** | Markup structure |
| The file location / injection point | **Presentation** | Where in the HTML it goes |

Schema straddles the boundary but leans Brain — the schema markup conveys editorial meaning, not visual appearance.

#### §6.7 — Writing Voice / Structure (lines 872-912)

**Layer: PURE EDITORIAL BRAIN**

Voice guidelines: scannability, credibility, evidence-first, question sections, evidence labeling, methodology notes, practical application, nutrition practicality. Zero presentation.

#### §6.7.1 — CTA Rules (lines 914-980)

**Layer: MIXED**

| Component | Layer | Why |
|-----------|-------|-----|
| CTA content rules (no health claims, no pricing, link to product page) | **Brain** | What to say |
| `.ia-cta` CSS class reference | **Presentation** | Visual component |
| CTA placement (near bottom, before FAQ) | **Brain** | Content structure |
| Recommended CTA text (whether generic or varied) | **Brain** | Content strategy |

The CTA *content rules* are Editorial Brain. The `.ia-cta` styling (which is in the §6.8 CSS block) is Presentation Layer.

#### §6.8 — CSS (lines 982-1110)

**Layer: PRESENTATION LAYER**

This entire section is CSS. Every line. Colors, fonts, spacing, borders, grid layouts, hover states, specificity selectors. There is zero editorial logic here.

**Conflict note:** The CSS in SKILL.md §6.8 (lines 982-1110) is the SAME CSS that appears in the §6.0 Page Shell `<style>` block (lines 528-590). It is also duplicated in levnytt.se's actual `articles.css` file. **Triple-defined.**

#### §6.9 — Image Embedding (lines 1118-1143)

**Layer: PRESENTATION LAYER**

Base64 embedding code, WebP conversion, `style` attributes for images. All implementation detail. The *rule* ("embed images as base64") could be considered Presentation Layer policy.

#### §6.10 — Skip These (lines 1147-1155)

**Layer: EDITORIAL BRAIN**

Content rules: no `<footer>`, no popup, no related articles dump, no calculator, no marketing sources. Pure editorial.

#### §6.11 — WordPress Post-Processing (lines 1157-1182)

**Layer: EDITORIAL BRAIN** (process logic)

The Python sanitization script and WP REST API payload construction. This is content processing, not presentation.

#### §6.12 — LevNytt Navigation (lines 1183-1198)

**Layer: PRESENTATION LAYER**

`nav.js` include, HTML element structure, script path. This is how the article is wrapped in navigation — pure presentation.

#### §6.13 — External Link Behavior (lines 1126-1144)

**Layer: EDITORIAL BRAIN**

Security/UX rule: `target="_blank" rel="noopener noreferrer"` on external links. This is a behavior rule, not presentation.

#### §6.14 — Internal Recommendation Links (lines 1148-1168)

**Layer: EDITORIAL BRAIN**

Link behavior rules for recommendation sections vs inline contextual links. Editorial/UX decision.

### Step 7: Verification (lines 986-1089)

**Layer: EDITORIAL BRAIN**

Two verification checklists (Basic SEO, LLM-optimization, Authority Content Mode) and the Python verification script. This is quality assurance logic, not presentation.

### Output Structure (lines 1094-1103)

**Layer: PRESENTATION LAYER**

File naming convention and directory structure. Presentation Layer logistics.

### LevNytt Core Link List (lines 1191-1212)

**Layer: EDITORIAL BRAIN**

Internal link priority tiers. Content strategy.

### SVG Hero Fallback Template (lines 1216-1242)

**Layer: PRESENTATION LAYER**

Verbatim SVG markup with brand colors, font stacks, dimensions. Pure presentation.

### LevNytt Page Type Division (lines 1107-1122)

**Layer: EDITORIAL BRAIN**

URL patterns, page type intent, linking roles. Content strategy.

## Layer Summaries

### Summary: What Belongs to the Editorial Brain

Everything in Editorial Brain is **site-independent logic** — it applies whether the article renders on LevNytt, a generic WordPress site, a static Astro site, or a JSON API.

- §0 Authority Content Mode (all health/sourcing rules)
- §Design Principles (Q-A punchline, H1 logic, YMYL rule, stacked checks)
- Required Inputs (keyword, site, author config)
- Pipeline flow
- Step 1 Research (search methodology, source extraction)
- Step 2 Sitemap (internal link strategy)
- Step 3 LSI clustering
- Step 5 Image *rules* (what images to create, text requirements)
- §6.1 Punchline writing rules
- §6.2 Key Takeaways writing rules
- §6.3 Question H2 guidelines
- §6.4 Section templates (content structure)
- §6.5 On-page element rules (stat cards, citations, CTA, author box, FAQ, methodology)
- §6.6 Schema *inclusion logic* (what to mark up)
- §6.7 Writing voice / evidence labeling / methodology / practicality rules
- §6.7.1 CTA content rules (what to say, not how to style)
- §6.10 Skip rules
- §6.11 WordPress post-processing
- §6.13 External link behavior
- §6.14 Internal recommendation link behavior
- Step 7 Verification checklists + script
- LevNytt Core Link List
- LevNytt Page Type Division

**Total: ~60% of SKILL.md**

### Summary: What Belongs to the Presentation Layer

Everything in Presentation Layer is **site-specific** — it changes when the visual identity or platform changes.

- Step 4 Playwright screenshot script (implementation)
- Step 5 Image *prompts* and *color values* (brand-specific)
- §6.0 Page Shell (verbatim DOCTYPE, HTML, <head>, <style>, <body> shell)
- §6.6 Schema *HTML wrapper* (the `<script type="application/ld+json">` tag)
- §6.8 CSS (entire style block — colors, fonts, spacing, grid, layout)
- §6.9 Image embedding code
- §6.12 nav.js include
- Output file structure
- SVG Hero Fallback template

**Total: ~30% of SKILL.md**

### Summary: Mixed Sections (straddle the boundary)

| Section | Brain Content | Presentation Content | Recommendation |
|---------|--------------|---------------------|----------------|
| §6.1 Punchline | Writing rules | `.ia-punchline` class reference | Keep writing rules in Brain; move class definition to Presentation CSS |
| §6.2 Takeaways | Writing rules | `.ia-takeaways` class reference | Same |
| §6.6 Schema | What schema to include, field values | `<script>` wrapper, `@id` URL construction | Schema content is Brain; injection point is Presentation |
| §6.7.1 CTA | Content rules | `.ia-cta` class reference | Content rules stay in Brain; class styling in Presentation CSS |
| §6.0 Page Shell (concept) | *That* a page shell exists | *What* the page shell contains | Brain defines the editorial structure; Presentation provides the template |

**Total: ~10% of SKILL.md**

## Conflict Inventory

### C1 — CSS Triple-Defined

The EXACT same CSS appears in three places:

| Location | Lines | Content |
|----------|-------|---------|
| `SKILL.md` §6.0 (inside `<style>`) | 528-590 | Full article CSS: `ia-wrap`, `.ia-punchline`, `.ia-takeaways`, `.ia-stat-card`, `.ia-method-table`, `.ia-faq`, `.ia-cta`, `.ia-author-box`, colors `#1B4332`/`#C9A84C`, font stacks |
| `SKILL.md` §6.8 | 982-1110 | **Same CSS** with minor additions: `.ia-evidence-label`, `.ia-ev-t1`-`t4`, specificity rules for dark-background blocks |
| `levnytt.se` actual `articles.css` | N/A | The production CSS file on the live site |

The §6.0 block and §6.8 block are nearly identical. The §6.8 block is more complete (adds evidence-tier labels). The §6.0 block would override §6.8 in the live HTML since it appears first in the `<head>`.

**Impact:** Any change to article styling must be made in 3 places. The §6.0 inline `<style>` and §6.8 `<style>` contradict each other when both rules have identical selectors — the §6.0 block always wins.

**Fix:** Merge all CSS into one external `articles.css`. Remove the §6.0 inline `<style>`. Remove §6.8 from the skill. Reference `articles.css` by URL.

### C2 — Duplicate Page Shell Logic

§6.0 (lines 512-700) defines a full HTML page template. But §6.8 also defines CSS that belongs inside that template. The split forces readers to cross-reference two sections to understand the full page shell.

### C3 — Styling Rules in Editorial Sections

Many editorial sections reference CSS class names as if they were editorial concepts:

| Location | Class Reference | Should Be |
|----------|----------------|-----------|
| §6.1 | `.ia-punchline` | "the punchline block" (abstract concept) |
| §6.2 | `.ia-takeaways` | "the key takeaways block" (abstract concept) |
| §6.5 | `.ia-stat-card`, `.ia-stat-grid` | "stat cards" (abstract concept) |
| §6.7.1 | `.ia-cta` | "the CTA block" (abstract concept) |
| Step 7 verification | `.ia-punchline`, `.ia-takeaways`, etc. | "punchline exists", "takeaways exist" (behavioral check) |

The verification script (Step 7) actually checks for the CSS class strings — which means changing a class name in the Presentation Layer breaks the editorial verification. This is the tightest coupling point.

**Coupling severity:** HIGH. Renaming `.ia-punchline` to `.punchline` would cause Step 7 to fail all punchline checks silently.

### C4 — No Clear Separation of Brand Identity

Brand colors (`#1B4332`, `#C9A84C`, `#2D6A4F`) appear in:
- §6.0 Page Shell CSS (lines 528-590)
- §6.8 CSS (lines 982-1110)
- Step 5 image prompts (as color instructions to GPT Image 2)
- SVG Hero Fallback template

Changing a brand color requires searching the entire SKILL.md for hex values.

## Dependency Analysis

### Presentation Layer Depends on Editorial Brain For:

| Dependency | Details |
|-----------|---------|
| Class names | Presentation CSS defines `.ia-punchline`, etc. — but Editorial Brain (Step 7) checks for these exact class names. They must stay in sync. |
| Content structure | Presentation HTML knows where to inject punchline, takeaways, stat cards, FAQ — but the *order* is defined by Editorial Brain. |
| Schema fields | The JSON-LD template references editorial content (article title, description, date, author). |
| Image placement | The Presentation Layer's `<img>` elements depend on Editorial Brain deciding that an image is needed. |

### Editorial Brain Depends on Presentation Layer For:

| Dependency | Details |
|-----------|---------|
| Class names for verification | Step 7 `.ia-punchline`, `.ia-takeaways` string checks depend on Presentation Layer class naming convention. **This is the critical coupling.** |
| Output file format | The Output section assumes HTML. If Presentation Layer ever outputs JSON or MD, Editorial Brain's verification logic needs updating. |

### Fundamental Insight

**The class-name dependency (C3) is the single point of coupling.** If the verification script checked for *structural* patterns (e.g., "is there a block before the first H2 that starts with a question?") instead of *class names*, the two layers would be fully independent.

## Separation Strategy

### Phase 1: Extract CSS (Low Risk, High Value)

1. Create `/home/yampa/levnytt-site/public/css/ia-articles.css` containing ALL CSS from §6.8 (the more complete version).
2. In §6.0 Page Shell, replace the inline `<style>` block with a `<link rel="stylesheet" href="/css/ia-articles.css">`.
3. Remove §6.8 entirely from SKILL.md.
4. In §6.0, keep only the structural HTML (doctype, head, body, divs) without CSS.

**Verification:** Generated articles render identically when the CSS is loaded externally vs inline. The Step 7 verification passes because class names haven't changed.

### Phase 2: Abstract Class References in Editorial Brain

Replace CSS class name references in editorial text with conceptual names:

| Current | Replacement |
|---------|-------------|
| `.ia-punchline` | "punchline section" |
| `.ia-takeaways` | "key takeaways block" |
| `.ia-stat-card .ia-stat-grid` | "stat card grid" |
| `.ia-cta` | "CTA block" |

In Step 7, change the verification to check *behavioral* patterns instead of class names:
- `class="ia-punchline"` exists → Check: "Is there a block in the first 500 chars that opens with the verbatim keyword question?"
- `class="ia-takeaways"` exists → Check: "Is there a `<ul>` or `<ol>` with 5-7 items near the top?"

**Result:** Presentation Layer can rename classes without breaking Editorial Brain verification.

### Phase 3: Extract HTML Templates

Move §6.0 Page Shell to `/home/yampa/levnytt-site/docs/templates/article-shell.html`. SKILL.md references it as "use the template at `/docs/templates/article-shell.html`."

The SVG Hero Fallback moves to `/home/yampa/levnytt-site/docs/templates/svg-hero.svg` or similar.

### Phase 4: Single Source of Truth for Brand Values

Create `/home/yampa/levnytt-site/docs/architecture/BRAND-VALUES.md`:

```yaml
colors:
  primary: "#1B4332"    # forest green
  accent: "#C9A84C"     # gold
  secondary: "#2D6A4F"  # medium green
  text: "#111827"       # near-black
  background: "#F9FAFB" # light gray
fonts:
  headings: "Georgia, serif"
  body: "Inter, sans-serif"
  code: "JetBrains Mono, monospace"
```

All other files (CSS, image prompts, SVG templates) reference this file instead of hardcoding values. CSS generation pulls colors from here.

### Phase 5: Decouple Step 7 Verification

The verification script in Step 7 currently mixes class-name string checks with semantic checks. Split it:

1. **Structural verification** (Editorial Brain): Checks content semantics — "punchline exists", "question H2s ≥ 4", "external citations ≥ 5". These are stable regardless of Presentation Layer.
2. **Style verification** (Presentation Layer): Checks visual requirements — "CSS loads without 404", "fonts render", "colors match brand spec". These belong in the Presentation Layer's own QA.

## Design Principles for Separation

1. **The Editorial Brain never references CSS class names, hex colors, or HTML element structure.** It talks about editorial concepts: "the punchline", "the takeaways block", "stat cards", "the CTA".
2. **The Presentation Layer never makes editorial decisions.** It provides the visual container for whatever content the Editorial Brain produces.
3. **Configuration files are the bridge.** BRAND-VALUES.yaml feeds both image prompts and CSS. ARTICLE-TEMPLATE.html provides the shell that Editorial Brain fills.
4. **Verification checks editorial behavior, not presentation strings.** "Does a punchline section exist at the right position?" — not "Does `class="ia-punchline"` exist?"

## Current Entanglement Score

| Metric | Value |
|--------|-------|
| Editorial Brain | ~60% |
| Presentation Layer | ~30% |
| Mixed/Boundary | ~10% |
| CSS defined inline in §6.0 | ~62 lines |
| CSS defined in §6.8 | ~128 lines |
| Presentation-layer hex colors hardcoded in Brain sections | 6+ (image prompts) |
| Editorial checks that depend on class names | 10+ (Step 7) |
| CSS duplicate locations | 3 (inline §6.0, block §6.8, production articles.css) |

## Related Skills Note

The `informational-article` skill exists independently of Editor and Writer. The original `SKILL.md` is loaded by OpenCode when the skill is invoked. The Writer (`levnytt-writer.md`) was a temporary cursor-based modification. The Editorial Brain should live in the skill file; the Presentation Layer should be extracted to the project repository.
