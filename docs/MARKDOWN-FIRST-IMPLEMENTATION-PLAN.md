# MARKDOWN-FIRST-IMPLEMENTATION-PLAN.md
# LevNytt.se — Smallest Viable Markdown-First Publication

**Date:** 2026-07-02  
**Author:** Senior Production Engineer  
**Status:** PLANNING — awaiting approval before implementation begins  
**Scope:** One successful Markdown-first publication end-to-end  

---

## 1. Goal

Enable a Markdown file (`content/articles/<slug>/<slug>.md`) to be converted into a PAS V1.0-compliant HTML article, pass the existing QA gate (`scripts/qa-article.sh` 12/12), and be deployed through the existing publication mechanism (`_redirects` + `sitemap.xml`).

**One article. One new script. No changes to production pages, design system, or pipeline.**

---

## 2. Current State

### What works

| Component | State |
|---|---|
| PAS V1.0 | FROZEN — complete HTML specification |
| `scripts/qa-article.sh` | Functional — 12 checks, GREEN/AMBER/RED gate |
| `_redirects` routing | Functional — 200-rewrites for `content/articles/` |
| `sitemap.xml` | Functional — hand-maintained |
| Publication Agent | Functional — copies to root, commits, pushes |
| Python 3.13 | Available — used by existing `scripts/*.py` files |
| Python stdlib | `re`, `json`, `html`, `textwrap`, `tomllib` all available |

### What does not work

| Component | State |
|---|---|
| `scripts/md-to-article.py` | Does not exist |
| `docs/PAGE-BUILDER-MARKDOWN-SPEC.md` | Incomplete — truncates mid-table; no component mapping |
| `content/articles/magnesium-och-stress/magnesium-och-stress.md` | Exists but unusable: frontmatter is commented-out (invalid), body has no PAS component conventions |

### Python environment constraint

`yaml` (PyYAML) and `markdown` are not installed. `pip` is not available. The conversion script must use Python stdlib only (`re`, `json`, `html.parser`, `tomllib`). YAML frontmatter can be parsed with `re` for the simple flat key:value structure used by PAS articles. No npm, no Node.js, no external parsers — per DECISIONS.md B1.

### Prototype document caveat

`docs/prototypes/PAGE-BUILDER-V2-PROTOTYPE.md` recommends `marked.js` and `npm install`. This recommendation violates DECISIONS.md B1 (no build step, no npm, no framework). The implementation will not follow that prototype. The prototype is retained as historical reference only.

---

## 3. Missing Components

Three components are missing. They must be created in order.

### 3.1 — Complete Markdown format specification

`docs/PAGE-BUILDER-MARKDOWN-SPEC.md` truncates mid-table-cell and contains no mapping from Markdown constructs to PAS components. It also shows incorrect commented-out frontmatter (`# title: "..."`) which is not parseable YAML.

The spec must define:
- Valid frontmatter structure (parseable without external libraries)
- Which PAS mandatory components come from frontmatter fields
- Which PAS mandatory components come from body section headings
- How prose sections map to `h2` / `h3` / `p` in PAS
- How FAQ entries are written in Markdown and how they become `<details>/<summary>`
- Which PAS components are generated from constants (disclosures, author box shell, verification metas)

### 3.2 — One correctly formatted test article

`content/articles/magnesium-och-stress/magnesium-och-stress.md` exists but is not usable:
- All frontmatter fields are commented out (e.g., `# title: "..."`) — not parseable
- Body has no PAS component structure: no punchline, no Key Takeaways block, no tier box, no CTA, no evidence labels, FAQ uses `###` headings not `<details>/<summary>`
- `@id:` in schema is invalid YAML

This file must be rewritten to match the completed spec, or a new test article must be created. The existing Markdown file may serve as content source material.

### 3.3 — Conversion script

`scripts/md-to-article.py` does not exist. This script is the Page Builder's conversion layer. It reads one `.md` file and writes one `.html` file matching PAS V1.0 exactly.

---

## 4. Dependencies

### Before writing the conversion script

| Dependency | Required for |
|---|---|
| 3.1 complete spec | Defines the contract the script implements |
| 3.2 test article | Provides the concrete input the script is tested against |

### Before writing the test article

| Dependency | Required for |
|---|---|
| 3.1 complete spec | Defines the format the test article must follow |

### Contradictions that do NOT block this work

The following contradictions from `docs/CONTRADICTION-RESOLUTION.md` are irrelevant to Markdown-first publication:

| Contradiction | Why it does not block |
|---|---|
| C2 — pillar.css ia-* values wrong | The converter writes inline CSS verbatim from PAS V1.0 Section 7. pillar.css ia-* values are irrelevant when inline CSS takes precedence. |
| C3 — duplicate ia-* definitions | Same reason as C2. |
| C1 / C8 — PAS "not yet extracted" note | PAS Section 7 inline CSS is the conversion source. The note is irrelevant. |

### Contradiction C7 is a low-risk blocker

C7 (`pillar.css` comment shows wrong path `/assets/pillar.css`) could mislead the conversion script author into generating the wrong `<link>` tag. The correct path (`/pillar.css`) is confirmed by PAS Section 7 and `PROJECT-STATUS.md`. The conversion script must hardcode `/pillar.css`, not follow the pillar.css comment.

---

## 5. Smallest Viable Implementation

### Approach

A Python 3 script using stdlib only. No new libraries, no npm, no build step. Consistent with how `scripts/fix-sprint20-consistency.py`, `scripts/generate-article-index.py`, and other scripts are implemented.

### Frontmatter design

The frontmatter will use a parseable flat YAML structure (simple `key: value` pairs and short lists), parsed by `re` in the conversion script. TOML (`tomllib`) is available as a fallback if YAML parsing proves ambiguous for nested fields.

Mandatory frontmatter fields (derived from PAS and PAGE-BUILDER-MARKDOWN-SPEC.md):

```
title           → <title>, og:title, twitter:title, JSON-LD headline
description     → <meta description>, og:description, twitter:description
slug            → canonical URL, og:url, JSON-LD url/@id
category        → category label <p> + ia-eyebrow
author_name     → JSON-LD author.name, byline <p>, author box
author_url      → JSON-LD author.url, byline link, author box link
author_initials → ia-author-avatar (2-letter initials, e.g. "JH")
author_bio      → ia-author-box bio text
date_published  → JSON-LD datePublished
date_modified   → JSON-LD dateModified, byline "Senast uppdaterad"
reading_time    → byline "X min läsning"
punchline       → ia-punchline content (single paragraph)
method_note     → ia-method-note content
```

Structured frontmatter fields:

```
takeaways[]     → ia-takeaways bullet list (items are plain strings; evidence labels are inline HTML)
tierbox[]       → ia-tierbox (4 items: label + url + title)
cta             → ia-cta (url, headline, body, link_text)
cta_secondary   → optional secondary CTA link (url, text)
faq[]           → ia-faq (question + answer pairs; maps to <details><summary>)
```

### Body mapping

The Markdown body contains only prose content sections. Mandatory PAS components with structured data (punchline, Key Takeaways, tier box, CTA, FAQ, method note, disclosures, author box) are driven by frontmatter — not body content.

| Markdown body element | PAS HTML output |
|---|---|
| `## Section heading` | `<h2>Section heading</h2>` |
| `### Sub-section` | `<h3>Sub-section</h3>` |
| Paragraph text | `<p>text</p>` |
| `| Table |` | `<table class="ia-method-table">` |
| `- bullet list` | `<ul><li>` |
| `**bold**` | `<strong>` |
| `[link](url)` | `<a href="url">` |

Evidence labels (`<span class="ia-evidence-label ia-ev-tN">`) are written as inline HTML in the Markdown body and pass through unchanged.

### Generated constants

The following PAS components are identical in every article and are generated by the script without frontmatter input:

- Verification meta tags (Google + Pinterest)
- OG image + dimensions (brand OG at `assets/brand/og-brand.png`)
- Font links (Playfair Display + Inter)
- Full inline ia-* CSS block (verbatim from PAS V1.0 Section 7)
- `#site-nav` div + `nav.js` defer
- Footer: `footer.js` + `components.js` defer
- Legal disclosure paragraph (verbatim from PAS Section 27)
- `og:site_name`, `og:locale`, `og:type`, `twitter:card`

### Script interface

```bash
python3 scripts/md-to-article.py <slug>
# Reads:  content/articles/<slug>/<slug>.md
# Writes: content/articles/<slug>/<slug>.html
# Exit 0: success
# Exit 1: file not found, missing required frontmatter field
```

After the script runs, the existing QA gate validates the output:

```bash
./scripts/qa-article.sh <slug>
# GREEN 12/12 → article is ready for publication
```

---

## 6. Files That Will Need Changes

| File | Change type | Notes |
|---|---|---|
| `docs/PAGE-BUILDER-MARKDOWN-SPEC.md` | Complete rewrite | Add component mapping, fix frontmatter format, add body conventions |
| `content/articles/magnesium-och-stress/magnesium-och-stress.md` | Rewrite | Fix frontmatter (remove `#` comments), restructure body to PAS conventions. OR use as a new test article with a different slug. |
| `scripts/md-to-article.py` | Create new | Python stdlib only; reads `.md`, writes `.html` |
| `_redirects` | Add one line | `/slug  /content/articles/slug/slug.html  200` |
| `sitemap.xml` | Add one entry | `<url><loc>https://levnytt.se/slug</loc>...</url>` |
| `CURRENT-SPRINT.md` | Update | Open new sprint for this work |

**Files that will NOT change:**
- `pillar.css` — not touched
- `nav.js` / `footer.js` / `components.js` — not touched
- Any existing `.html` article — not touched
- `scripts/qa-article.sh` — not touched
- `_redirects` existing lines — not touched

---

## 7. Estimated Implementation Order

### Step 1 — Documentation (no sprint required per DECISIONS.md A8)

1. Rewrite `docs/PAGE-BUILDER-MARKDOWN-SPEC.md`:
   - Define valid frontmatter format (all mandatory fields, correct YAML syntax)
   - Define component mapping (frontmatter → PAS components)
   - Define body mapping (Markdown → HTML prose)
   - Define FAQ conventions (how `faq[]` frontmatter entries become `<details>/<summary>`)
   - Define how evidence labels are written inline in the body

### Step 2 — Test article (requires sprint)

2. Create one correctly formatted test `.md` file in `content/articles/`:
   - Valid frontmatter (no commented-out fields)
   - All mandatory frontmatter fields present
   - Body with 4+ `h2` prose sections using evidence labels
   - No PAS-component sections in body (they come from frontmatter)

### Step 3 — Conversion script (requires sprint)

3. Write `scripts/md-to-article.py`:
   - Parse frontmatter with `re` (or `tomllib` if TOML format is chosen)
   - Validate: fail with clear error if any mandatory field is missing
   - Convert Markdown body to HTML prose using `re` (headings, paragraphs, bold, links, tables)
   - Build full PAS V1.0 HTML: insert frontmatter data into correct positions, build JSON-LD @graph, insert ia-* CSS verbatim, assemble all mandatory components in PAS order
   - Write output to `content/articles/<slug>/<slug>.html`

### Step 4 — Validate (no sprint required)

4. Run `python3 scripts/md-to-article.py <slug>`
5. Run `./scripts/qa-article.sh <slug>` — target: GREEN 12/12
6. Open the output HTML in a browser and verify visual match against an existing PA article

### Step 5 — Publish (requires sprint entry)

7. Add route to `_redirects`
8. Add entry to `sitemap.xml`
9. Commit: `Add first Markdown-first article: <slug>`
10. Push — Cloudflare Pages auto-deploys
11. Verify live at `https://levnytt.se/<slug>`

---

## 8. Risks

### R1 — Frontmatter YAML parsing without a YAML library

**Risk:** The existing `.md` file and `PAGE-BUILDER-MARKDOWN-SPEC.md` both use commented-out frontmatter (`# title: "..."`). This is not parseable YAML. The conversion script must use `re`-based parsing; complex nested YAML structures (e.g., the existing schema block with `@id:`) may cause edge cases.

**Mitigation:** Define the frontmatter format before writing the script. Keep the format flat (no deep nesting). If nested fields are required (e.g., `cta.url`, `cta.text`), use a simple dotted-key convention (`cta_url:`, `cta_text:`) that is easy to parse with `re`. Alternatively, switch the frontmatter format to TOML (Python 3.11+ `tomllib` is available).

**Decision required:** Choose the frontmatter format before implementation: simple flat YAML (parsed with `re`) or TOML (parsed with `tomllib`). This is an engineering decision with no content impact.

### R2 — Body Markdown edge cases

**Risk:** The Markdown-to-HTML body conversion is done with `re`, not a full parser. Edge cases like nested lists, inline code in table cells, or links inside bold text may not convert correctly.

**Mitigation:** Define supported Markdown constructs in the spec (Step 1) and keep them narrow: `##`, `###`, `p`, `**bold**`, `[link](url)`, `| table |`, `- list`, pass-through HTML. Evidence labels are raw HTML in the source — they pass through unchanged.

### R3 — QA gate Q11 (title ≤ 60 chars)

**Risk:** PAS Q11 checks that `<title>` is ≤ 60 characters. The `title` frontmatter field is the full article title, which is typically longer. The conversion script must truncate or transform the title for the `<title>` tag separately from `og:title`.

**Mitigation:** The conversion script constructs `<title>` as `<slug-title> | LevNytt` and validates the length. If over 60 characters, it truncates the first part. This is a known PAS constraint and must be handled in the script.

### R4 — QA gate Q12 (description ≤ 155 chars)

**Risk:** The `description` frontmatter field must be ≤ 155 characters. Authors writing Markdown may not know this constraint.

**Mitigation:** The conversion script validates description length and exits with an error if over 155 characters, rather than silently truncating. The spec must document this constraint.

### R5 — Test article content quality

**Risk:** The existing `magnesium-och-stress.md` content does not include evidence labels, PubMed links, or the factual depth that PAS mandates. It is thin draft content.

**Mitigation:** The QA gate checks HTML structure and brand palette, not content depth. A structurally valid article with placeholder evidence labels will pass 12/12. Content quality is separate from structural compliance for this first milestone.

### R6 — `magnesium-och-stress` slug conflict

**Risk:** `magnesium-och-stress.html` already exists as a root-level production page (Sprint 16 output). Using the same slug for the Markdown-first test article would overwrite the live page when the Publication Agent deploys.

**Mitigation:** Use a different slug for the test article. The existing `magnesium-och-stress.md` can be revised as source material but should be saved under a new slug (e.g., `magnesium-stressrespons`) or the test article can be an entirely new topic not already live.

---

## 9. Definition of Done

The Markdown-first implementation milestone is complete when all of the following are true:

| # | Criterion | How verified |
|---|---|---|
| 1 | `docs/PAGE-BUILDER-MARKDOWN-SPEC.md` is complete — no truncation, full component mapping | Read the document end-to-end |
| 2 | One `.md` file with valid frontmatter and PAS-structured body exists in `content/articles/<slug>/` | `cat content/articles/<slug>/<slug>.md` |
| 3 | `python3 scripts/md-to-article.py <slug>` exits 0 and creates `content/articles/<slug>/<slug>.html` | Run the script |
| 4 | `./scripts/qa-article.sh <slug>` returns GREEN 12/12 | Run the QA gate |
| 5 | The article HTML renders identically to an existing PA-generated article (visual inspection) | Open in browser |
| 6 | `_redirects` contains the correct 200-rewrite for the slug | `grep <slug> _redirects` |
| 7 | `sitemap.xml` contains the canonical URL | `grep <slug> sitemap.xml` |
| 8 | `git push` completes and Cloudflare Pages deploys | CF Pages deployment log |
| 9 | The article is live at `https://levnytt.se/<slug>` | Browser verification |
| 10 | No existing production pages were modified | `git diff HEAD~1 -- '*.html' '*.css' '*.js'` shows only new files |

---

## Appendix: What the "Existing Page Builder" Means in This Context

The Production Readiness Review referred to the Page Builder as the authoring-to-HTML conversion layer. In the current system this layer is the **LevNytt Writer agent** (`.opencode/agents/levnytt-writer.md`) which produces HTML directly. It does not accept Markdown input.

The Markdown-first implementation adds a **pre-processing step** (`scripts/md-to-article.py`) upstream of the existing agent. This script converts Markdown to PAS-compliant HTML, after which the existing QA gate and Publication Agent handle the output identically to any writer-generated article.

"Reuse the existing Page Builder" means:
- Reuse the same PAS V1.0 output format — the HTML the script produces is structurally identical to what the LevNytt Writer produces today
- Reuse the same QA gate (`scripts/qa-article.sh`) — no new validation layer
- Reuse the same publication mechanism (`_redirects`, `sitemap.xml`, Publication Agent)
- Reuse the same design system (`pillar.css`, `nav.js`, `footer.js`, `components.js`) — untouched

The only new component is the conversion script itself.

---

*No code was written or modified during the preparation of this document.*
