# DECISIONS.md
# LevNytt.se — Permanent Engineering Decisions

This document records decisions that are settled. Do not contradict them without first updating this file and getting explicit confirmation from the project owner.

See `PROJECT-ENTRY.md` for the reading order and workflow. See `PROJECT-STATUS.md` for current project state.

---

## A. Process decisions

### A1. Repository is the Source of Truth

The Git repository is the authoritative record of the project. Documentation describes the repository.

If documentation and repository disagree, the repository is correct and the documentation must be updated. The repository is never modified to match outdated documentation.

**Implication:** Always read actual files before acting on documentation. Verify before changing anything.

---

### A2. Documentation hierarchy

Always read documentation in this order before starting work:

1. `PROJECT-ENTRY.md`
2. `PROJECT-STATUS.md`
3. `CURRENT-SPRINT.md`
4. `DECISIONS.md`
5. Repository files
6. Historical documents (context only)

Historical documents (`AUDIT-REPORT.md`, `LEVNYTT-MUISTIO.md`, etc.) are reference material. They are not authoritative.

---

### A3. AI session startup rule

Every new AI session begins by reading `PROJECT-ENTRY.md`, `PROJECT-STATUS.md`, `CURRENT-SPRINT.md`, and `DECISIONS.md` — in that order — before any implementation begins.

Do not perform a full repository analysis unless explicitly requested.

Do not redefine priorities when an active sprint already exists.

---

### A4. Sprint discipline

One active sprint at a time. One implementation goal per sprint. `CURRENT-SPRINT.md` defines the active sprint.

Finish the active sprint before introducing unrelated work, unless the project owner explicitly instructs otherwise.

Work that is not in the active sprint is backlog.

---

### A5. Verification before recommendation

Never recommend implementation work based only on historical audits or documentation.

Always verify that:
- the issue still exists in the current repository
- it has not already been solved
- the recommendation reflects the current repository state

---

### A6. Documentation maintenance rules

| Document | Contains |
|---|---|
| `PROJECT-STATUS.md` | Current project state only. No historical sprint narratives. |
| `CURRENT-SPRINT.md` | One active sprint only. Goal, tasks, criteria, blockers, next action. |
| `DECISIONS.md` | Permanent engineering decisions only. |

Historical reports remain archived. They are never modified to remove their original content.

---

### A7. Engineering principle

Implement before redesign.

Verify before changing.

Document before assuming.

Repository first. Documentation second. Conversation memory last.

---

### A8. Do not modify production pages without a sprint

HTML, CSS, JavaScript, and `sitemap.xml` are not modified outside of an active sprint task.

Documentation files (`*.md`) may be updated at any time.

**Implication:** Analysis, auditing, and documentation work can happen freely. Code changes require an active sprint entry in `CURRENT-SPRINT.md`.

---

### A9. Documentation must not contain hard-coded repository statistics

Documentation must not hard-code counts that are properties of the repository and will become stale as the project grows — for example: total number of HTML pages, number of pillar pages, number of informational articles, number of images.

These counts change with every new page or file. Hard-coded counts in documentation create false confidence and contradict the repository.

**Rule:** Describe the system. Do not duplicate repository statistics.

**Correct:** "All production pages are in `sitemap.xml`."
**Incorrect:** "73 production pages are in `sitemap.xml`."

**Correct:** "The site has two page tiers: pillar pages and informational articles."
**Incorrect:** "The site has 15 pillar pages and 55 informational articles."

**To get current counts:** query the repository directly.

```bash
# All HTML files (excluding .git)
find . -name "*.html" -not -path "./.git/*" | wc -l

# Production pages only (excluding 404)
find . -name "*.html" -not -path "./.git/*" \
  -not -name "404.html" | wc -l

# Sitemap entry count
grep -c '<loc>' sitemap.xml
```

**Implication:** When reviewing or updating documentation, remove any counts that refer to the number of files, pages, images, or sitemap entries. Replace with system descriptions.

---

## B. Architecture decisions

### B1. Static HTML architecture — no framework

The site is and remains vanilla HTML5/CSS3/ES5. No build framework (Astro, Next.js, Vite, React, etc.), no npm at the repo root, no transpilation.

Deployment is a direct `git push` with zero build step.

**Implication:** Never propose migrating to a framework without a written justification and explicit owner approval.

---

### B2. Shared components via injected JS — no hardcoded nav or footer

Navigation and footer are injected by `nav.js` and `footer.js` via self-invoking IIFEs. No page may have a hardcoded `<nav>` or `<footer>` element.

**Rationale:** Central maintenance. Changing navigation requires editing one file instead of every page.

**Implication:** Every new page must load `nav.js` and `footer.js` with `defer`. Any page found with a hardcoded nav must be migrated before other work on that page is done.

---

### B3. pillar.css is the single design system

All current and future pages use `pillar.css` for styling. Inline `<style>` blocks with `:root` token definitions are a legacy pattern being phased out.

`pillar.css` defines brand-aware CSS variables:
- `--lv-green` (`#1B4332`) — Deep Green, primary brand
- `--lv-gold` (`#E8C870`) — Light Gold, secondary brand
- `--lv-green-dark` (`#0D2C1E`) — Dark green accent
- `--lv-green-light` (`#2D6A4F`) — Light green accent
- `--lv-cream` (`#F9F6EF`) — Background cream

**Implication:** New pages must link `pillar.css`. Do not add new inline `:root` blocks. Existing pages with inline `:root` blocks are migration candidates.

---

### B4. sitemap.xml is hand-maintained

`sitemap.xml` is edited manually. There is no automated sitemap generator.

**Implication:** Every new page must be added to `sitemap.xml` in the same commit it is created. Every deleted or redirected page must be removed or updated. The sitemap must never be left inconsistent with the repository.

---

### B5. _redirects handles content/articles/ routing

Pages in `content/articles/` are served via 200-rewrites in `_redirects`:

```
/slug  /content/articles/slug  200
```

The catch-all `/* /404.html 404` must always be the last line in `_redirects`.

**Implication:** Every new article in `content/articles/` needs a corresponding rewrite line in `_redirects`. The catch-all must remain last.

---

### B6. Sponsor ID is injected by components.js — never hardcoded

All links to `neolifeshop.com` must include `?sponsor=41-830928`. This is handled automatically by `components.js` at page load.

**Implication:** `components.js` must be loaded on every page. Do not hardcode sponsor IDs in HTML.

---

### B7. URL form convention

The canonical URL for a root-level `.html` file is the clean slug: `/slug` (no extension, no trailing slash).

Exception: pages served from a subdirectory use a trailing slash: `/neolife-kosttillskott/`.

Known legacy exceptions (intentional trailing-slash canonicals on root-level files): `/golden-home-care/`, `/neolife-hallbarhet/`, `/neolife-acidophilus-plus/`, `/neolife-elevate/`, `/neolife-shake-bar-tea/`, `/personlig-vard/`, `/finns-det-billigare-alternativ/`. These are documented and must not be "corrected" without verifying the canonical tag in the file.

**Implication:** New root-level pages: use clean-slug canonical. New subdir pages: use trailing-slash canonical.

---

### B8. BRAND-DESIGN-SYSTEM.md is the Single Source of Truth for brand identity

`docs/BRAND-DESIGN-SYSTEM.md` defines the LV Mark, brand colors, usage rules, and visual identity. It is the authoritative specification. All brand assets must be derived from its rules.

`pillar.css` CSS variables (`--lv-green`, `--lv-gold`, etc.) are the technical implementation of the brand spec. They must never contradict `BRAND-DESIGN-SYSTEM.md`.

**Implication:** Before adding or changing brand assets, read `docs/BRAND-DESIGN-SYSTEM.md` first. Do not create brand assets that are not specified or implied by the brand document.

---

### B9. Brand assets are stored in assets/brand/

All brand image assets live in `assets/brand/`:

| Asset | Purpose |
|---|---|
| favicon.svg | Browser tab icon |
| apple-touch-icon.png | iOS home screen icon |
| hero-watermark.svg | Background watermark on hero sections |
| og-brand.png | Default Open Graph social share image |
| logo.svg | LV Mark (light background variant) |
| logo-dark.svg | LV Mark (dark background variant) |
| logo-light.svg | LV Mark (optional variant) |

All raster assets originate from the master SVG. The `og-brand.png` (1200x630) is the only rasted OG asset required.

**Implication:** New brand image files must be placed in `assets/brand/`. Do not scatter brand assets across `images/` or `img/` directories.

---

### B10. Shared branding is injected through components.js

Brand meta elements (favicon, apple-touch-icon, hero watermark, author avatar) are injected at runtime by `components.js` via self-invoking IIFEs.

No page may hardcode brand meta tags or brand images unless the page requires a page-specific override (e.g. product-specific OG image).

**Implication:** New pages include `components.js` with `defer`. The brand injectors (`injectBrandMeta`, `injectHeroWatermark`, `injectBrandAvatar`) run automatically on `DOMContentLoaded`. Do not hardcode favicon or apple-touch-icon links in individual pages.

---

### B11. LevNytt Writer and pillar-page-template consume the same shared brand assets

Both the LevNytt Writer (which generates informational articles) and the `pillar-page-template` skill (which migrates pillar pages) use the same shared components: `nav.js`, `footer.js`, `components.js`, `pillar.css`, and `assets/brand/`.

There is no separate brand pipeline for articles vs. pillar pages. Both are vanilla HTML files at root level and use the same shared infrastructure.

**Implication:** New content generation skills (informational-article, pillar-page-template, etc.) must reference the same shared components. Do not create a second brand system for any output type.

## C. Content and SEO decisions

### C1. Google and Pinterest verification meta tags

Every page must include these two meta tags as the first lines inside `<head>`:

```html
<meta name="google-site-verification" content="kAcoLDFGCpGh42gIFRgPeWlC253vTP3OLBs6wI8KDQ0">
<meta name="p:domain_verify" content="6a9e88f7014abe0735767f464c08f337"/>
```

---

### C2. Image naming and alt text convention

Image filenames: descriptive, keyword-rich, lowercase, hyphenated (e.g., `ldc-golden-home-care.jpg`).

Alt text: always in Swedish, always descriptive.

---

### C3. Pillar page audit checklist (13 checks)

Every named pillar page must pass all 13 checks from the audit script at `~/.claude/skills/pillar-page-template/scripts/audit_pillar_page.py`:

1. `nav_js_with_defer` — `<script src="/nav.js" defer>` present
2. `footer_js_with_defer` — `<script src="/footer.js" defer>` present
3. `no_hardcoded_nav_element` — no hardcoded `<nav>` in HTML
4. `links_pillar_css` — `<link rel="stylesheet" href="/pillar.css">` present
5. `no_inline_root_token_block` — no `:root { --token: ... }` block in inline `<style>`
6. `playfair_display_loaded` — Playfair Display loaded from Google Fonts
7. `inter_loaded` — Inter loaded from Google Fonts
8. `at_least_3_breakpoints` — 3 or more `@media` breakpoints in the page
9. `img_width100_has_height_auto` — responsive images use `width: 100%; height: auto`
10. `canonical_is_clean_slug` — `<link rel="canonical">` present and correct
11. `og_image_present` — `<meta property="og:image">` present
12. `viewport_meta_present` — `<meta name="viewport">` present
13. (Composite — a page passes 13/13 when all 12 named checks above pass)

**Implication:** Any new pillar page must pass 13/13 before it is considered production-ready. Run the audit script to verify.
