# Baseline V1 — LevNytt Production Pipeline

**Date:** 2026-07-01
**Status:** Accepted & Frozen
**Commit:** e43a551 (latest)

> This document captures the state of the production pipeline at the Baseline V1 milestone.
> **Do not modify** the Writer, Publication Agent, Brand Asset Pack, Publication Standard, or HTML templates without explicit approval.
> This is the rollback point for all future development.

---

## 1. Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│                 Editorial Commander V1.3                 │
│  Orchestration layer — scans, analyses, routes, reports │
└──────────┬──────────────────────────────────┬───────────┘
           │ routes to                        │ routes to
           ▼                                  ▼
┌──────────────────────┐       ┌──────────────────────────┐
│  LevNytt Writer V1.7 │       │   MLM Editorial Agent    │
│  Informational       │       │   (separate, not frozen) │
│  articles only       │       │                          │
└──────────┬───────────┘       └──────────────────────────┘
           │ outputs to
           ▼
┌─────────────────────────────────────────────────────────┐
│              Publication Agent V1.0                      │
│  Reads Editorial Brief → validates → copies → verifies   │
│  → regenerates index → updates status → commits → pushes│
└─────────────────────────────────────────────────────────┘
```

### Component Lines of Code

| Component | File | Lines |
|-----------|------|-------|
| Editorial Commander | `.opencode/agents/editorial-commander.md` | 347 |
| LevNytt Writer | `.opencode/agents/levnytt-writer.md` | 1,218 |
| Publication Agent | `.opencode/agents/publication-agent.md` | 223 |
| Article Index Generator | `scripts/generate-article-index.py` | 595 |
| Editorial Sync Engine | `scripts/sync-editorial-state.py` | 1,162 |
| **Total** | | **3,545** |

### Content Inventory

| Metric | Count |
|--------|-------|
| Published articles (root `/*.html`, valid JSON-LD) | 96 |
| Source articles (`content/articles/*.html`) | 41 |
| Unique source articles not yet published | 19 |
| Index categories | 6 |
| Portalguides (komplett guide format) | 8 |
| Brand assets (`assets/brand/`) | 25 files |
| Product entities | 61 |
| Gap report clusters tracked | 94 |

---

## 2. Pipeline Overview

### 2.1 — Trigger Sequence

The pipeline is triggered via the Editorial Commander, which must always run first. It produces:

1. **Repository Health Report** — scans published vs source files, checks drift
2. **Editorial Brief** — saved to `docs/editorial-briefs/` with date stamp, lists READY TO PUBLISH items, recommends next action
3. **Production Status** — updated in `docs/editorial-backlog/production-status.md`

### 2.2 — Agent Roles

| Agent | Responsibility |
|-------|---------------|
| **Editorial Commander V1.3** | Orchestration, scanning, routing, drift detection. Never writes articles. |
| **LevNytt Writer V1.7** | Generates informational articles only. Uses §6.0 page shell (Golden Reference structure). Authority Content Mode always active. |
| **Publication Agent V1.0** | Deploys source articles to root. Copy-only, never modifies content. |

### 2.3 — Production Rules

- **Published production** = root `/*.html` files only
- **Source articles** = `content/articles/*.html` — completed but not yet deployed
- **Publishing** = copy operation only, no content modification
- **No overwrites** — root files are never overwritten without explicit instruction
- **No index.html edits** — navigation pages are not touched by the pipeline
- **One commit per article** — never batch multiple articles into one commit

---

## 3. Production Workflow

### Step 1 — Generate Article (Writer)

The Writer produces a standalone HTML file with:

- **§6.0 Page Shell** — exact copy of the Golden Reference structure (D-vitamin komplett guide)
- **Brand-correct CSS** — inline, `#1B4332` / `#E8C870` / `#F9F6EF` / `#111827` palette
- **Editorial watermark** — `editorial-watermark.svg`, opacity 0.10 (desktop) / 0.08 (mobile)
- **Schema** — `@graph` with `Article` (includes `@id`, publisher with `logo`, `image`, `author`) + `FAQPage`
- **Structure** — H1 → punchline → Key Takeaways → stat grid (optional) → H2 sections → mid-CTA → FAQ accordion (6–10 pairs) → Author Box → Method Note → end CTA
- **Two CTAs** — exactly two `.ia-cta` blocks with `.btn` class
- **Evidence labels** — `.ia-evidence-label` with `.ia-ev-t1` through `.ia-ev-t4`
- **No tierbox, no category label, no methodology/final disclosure** — removed per Golden Reference alignment

Output: `content/articles/<slug>.html`

### Step 2 — Validate Product References (Publication Agent)

```bash
python3 content/products/scripts/validate_product_references.py content/articles/<slug>.html
```

Phase 1 behavior: Warnings logged, does not block publication.

### Step 3 — Confirm Source Exists

Verify `content/articles/<slug>.html` exists and `/<slug>.html` does not exist at root.

### Step 4 — Copy to Root

```bash
cp content/articles/<slug>.html <slug>.html
```

### Step 5 — Verify Publication

- Root file exists
- `diff` confirms byte-for-byte identical
- `<html` tag present
- All 8 required brand assets present:

```
assets/brand/logo.svg
assets/brand/logo-light.svg
assets/brand/logo-dark.svg
assets/brand/favicon.svg
assets/brand/apple-touch-icon.png
assets/brand/author-avatar.svg
assets/brand/hero-watermark.svg
assets/brand/og-brand.png
```

### Step 5B — Regenerate Article Index

```bash
python3 scripts/generate-article-index.py
```

Scans all root HTML files, extracts metadata from JSON-LD, classifies into 6 categories, rebuilds `artiklar.html`.

### Step 6 — Update Production Status

Update `docs/editorial-backlog/production-status.md` — change status to **Published**, add date if applicable.

### Step 7 — Commit

Stage: new root HTML + `production-status.md` + `artiklar.html` only.  
Never stage: `content/articles/` source files, `.opencode/` runtime files.

### Step 8 — Push

```bash
git push origin main
```

### Step 9 — Publication Report

Standard format:

```
✅ PUBLISHED: /<slug>
   Source: content/articles/<slug>.html
   Commit: <hash>
   Brand: v1 — LevNytt LV Mark (assets/brand/)
   Entities: validated — Product Entity System v1
   Index: artiklar.html auto-updated — <total> articles across <cats> categories
```

---

## 4. Category System

Articles are classified by `generate-article-index.py` using keyword matching on slug + title + meta description. Categories are defined in `CATEGORY_MAP`:

| Category ID | Label | Keywords | Articles |
|-------------|-------|----------|----------|
| `vitaminer` | Vitaminer & mineraler | (catch-all) | 52 |
| `fettsyror` | Fettsyror & antioxidanter | omega-3, fiskolja, epa, dha, hjärthälsa, ledvärk, fettsyra, ... | 13 |
| `tarmhalsa` | Tarmhälsa & kostfiber | kostfiber, probiotika, prebiotika, ibs, förstoppning, fiber, ... | 13 |
| `halsa` | Hälsa & livsstil | kollagen, kreatin, melatonin, sömn, trött, retinol, hudtecken, ... | 6 |
| `goldenhomecare` | Golden Home Care | golden.home.care, rengör, städ, diskmedel, kemikalie, ... | 5 |
| `direktforsaljning` | Direktförsäljning | mlm, pyramidspel, nätverksmarknadsföring, konsumenträtt, ... | 7 |

Unmatched articles fall to `vitaminer` (catch-all).

---

## 5. Brand System (V1)

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| Forest Green | `#1B4332` | Headings, punchline bg, CTA bg, table headers, watermark |
| Gold | `#E8C870` | Accents, borders, hover, eyebrow, checkmarks, CTA buttons |
| Warm White | `#F9F6EF` | Card backgrounds, blockquote bg, author box bg, gold text on dark |
| Dark Text | `#111827` | Body text |
| Medium Gray | `#475569` | Meta text, secondary labels |
| Light Gray | `#9CA3AF` | Method note, source text |

### Font Stack

- **Headings:** `'Playfair Display', Georgia, serif` (weight 600–700)
- **Body:** `'Inter', system-ui, -apple-system, sans-serif` (weight 400–700)

### Key Assets

- `logo.svg` / `logo-light.svg` / `logo-dark.svg` — site logos
- `lv-brand-mark.svg` — used as JSON-LD publisher `logo`
- `og-template.png` — default OG image (1200×630)
- `og-brand.png` / `og-brand.svg` — branded OG image
- `author-avatar.svg` — default author image in article bylines
- `editorial-watermark.svg` — decorative article watermark (opacity 0.10/0.08)
- `hero-watermark.svg` — decorative hero watermark
- `favicon.svg` + PNG fallbacks — favicon set
- `social-avatar-*.png/svg` — social media avatars

---

## 6. Current Limitations

1. **No phase 2 product validation** — Phase 1 is advisory only; validation warnings do not block publication.
2. **No automated drift resolution** — `sync-editorial-state.py` detects undocumented pages (AMBER drifts) but does not auto-heal.
3. **Index regeneration is destructive** — `artiklar.html` is fully rebuilt each run; custom edits outside marker comments are overwritten.
4. **No article-level SEO score** — no built-in check for keyword density, heading distribution, or meta description length.
5. **No batch commit safety** — the pipeline enforces one commit per article, but no guardrail prevents accidental batch commits if the user bypasses the agent.
6. **No canonical chain validation** — no automated check that all internal links resolve to existing pages.
7. **No schema validation** — JSON-LD is not validated against schema.org schemas before publishing.
8. **Author box is static** — all articles use Jarmo Halonen as default; no per-topic author routing.
9. **No scheduled runs** — all pipeline steps are manually triggered; no cron or CI integration.

---

## 7. Known Future Improvements

### High Priority

- [ ] **Product Entity Phase 2** — validation failures block publication (exit code 1 = halt)
- [ ] **Canonical check** — verify all internal `href` links exist before publishing
- [ ] **SEO scorecard** — automated check before publication (title length, meta desc, H1 presence, keyword in first 50 words)

### Medium Priority

- [ ] **Author routing** — per-topic author selection based on keyword cluster
- [ ] **Schema validation** — `jsonschema`-based validation of JSON-LD against schema.org
- [ ] **Drift auto-heal** — auto-generate gap report entries for undocumented pages
- [ ] **Image generation** — integrate GPT Image 2 into the Writer pipeline for hero images and infographics

### Low Priority

- [ ] **Scheduled sync** — daily cron job for `sync-editorial-state.py`
- [ ] **CI/CD integration** — GitHub Actions for publish-on-push to `content/articles/`
- [ ] **Article preview** — `content/articles/` source files rendered on `levnytt.se/dev/` subdomain before publishing
- [ ] **Batch publication** — multi-article queue with dependency ordering
- [ ] **SEO monitoring** — track article rank positions and update production-status with ranking data

---

## 8. Rollback Instructions

To restore Baseline V1 state:

```bash
# Restore Writer template
git checkout e43a551 -- .opencode/agents/levnytt-writer.md

# Restore Publication Agent
git checkout e43a551 -- .opencode/agents/publication-agent.md

# Restore Brand Asset Pack
git checkout e43a551 -- assets/brand/

# Restore Article Index Generator
git checkout e43a551 -- scripts/generate-article-index.py

# Restore Editorial Sync Engine
git checkout e43a551 -- scripts/sync-editorial-state.py

# Restore Publication Standard
git checkout e43a551 -- docs/PUBLICATION-ARTICLE-STANDARD.md
git checkout e43a551 -- docs/BRAND-DESIGN-SYSTEM.md

# Restore page shell CSS (embedded in §6.0, restored via Writer template above)
```

After restore, regenerate the article index:

```bash
python3 scripts/generate-article-index.py
```

---

## 9. Sign-off

Baseline V1 represents the accepted production pipeline as of 2026-07-01.

- **Writer:** levnytt-writer.md v1.7 (frozen)
- **Publication Agent:** publication-agent.md v1.0 (frozen)
- **Brand Asset Pack:** V1 (frozen, 25 assets)
- **Golden Reference:** `content/articles/d-vitamin-allt-du-behover-veta.html` (accepted)
- **Verification Article:** `content/articles/antioxidanter-komplett-guide.html` (passes structural comparison)
- **Confirmed Structural Match:** WRITER-VERIFICATION.md (16 positions, 25+ classes, schema, CTA placement)

---

*End of Baseline V1 documentation.*
