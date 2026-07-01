# LevNytt Brand Design System

## Mission

LevNytt's visual identity should communicate:

- Trust
- Scientific integrity
- Scandinavian simplicity
- Long-term consistency
- Editorial independence

The LV Mark is not merely a logo.

It is the primary visual element representing the LevNytt brand across every platform.

---

# Core Brand Element

Name:

LevNytt LV Mark

Style:

- Flat SVG
- Minimal
- Vector-based
- Timeless
- Scandinavian

Primary colors:

- Deep Green: #1B4332
- Light Gold: #E8C870

Supporting palette follows the LevNytt Design System.

---

# Brand Principles

The visual identity should always feel:

- Calm
- Credible
- Evidence-based
- Premium without being luxurious
- Human without becoming personal

The brand represents LevNytt as an editorial authority, not an individual author.

---

# Primary Usage

Use `lv-brand-mark.svg` as:

- Header logo (`header-logo.svg`)
- Footer logo (`header-logo.svg`)
- Author avatar (`author-avatar.svg`)
- Browser favicon (`favicon.svg`, `favicon-*.png`)
- Apple Touch Icon (`apple-touch-icon.png`)
- PWA application icon (`android-chrome-*.png`)
- Social media profile (`social-avatar.svg` / `.png`)
- Open Graph preview (`og-template.svg` / `.png`)

---

# Extended Usage

The LV Mark may also appear as:

- Section divider
- PDF reports
- Presentation material
- Video intro/outro

Use `editorial-watermark.svg` for:

- Hero backgrounds
- Section backgrounds
- PDF cover pages
- Editorial illustrations

---

# Watermark Policy

`editorial-watermark.svg` is a decorative background element, not a logo.

**Always:** hero backgrounds, section backgrounds, PDF covers, OG watermark.
**Never:** header, footer, author avatar, favicon, social avatar, brand signatures.

The watermark must never be presented as a logo or brand identifier. When used as a background, apply 10–15 % opacity.

---

# Safe Zones

| Asset | Minimum Clear Space |
|-------|-------------------|
| `lv-brand-mark.svg` | 25 % of icon diameter in all directions |
| `header-logo.svg` | 20 % of total height on all sides |
| `social-avatar.svg` | 10 % of canvas (built into 82 % fill spec) |

---

# Asset Registry

All brand assets live in `assets/brand/` and originate from the master SVG `lv-brand-mark.svg`.

Approved visual reference: `docs/brand/brand-system-reference.png`

## Master Asset

| File | Type | Purpose |
|------|------|---------|
| `lv-brand-mark.svg` | SVG master | Primary brand identifier. All other assets derive from this file. |

## Logo & Identity

| File | Type | Purpose |
|------|------|---------|
| `header-logo.svg` | SVG | Site header, sticky nav, mobile nav. Brand Mark + "LevNytt" wordmark. |
| `author-avatar.svg` | SVG | Editorial byline, article meta, author signature. |
| `social-avatar.svg` | SVG | Social media profiles (Facebook, Instagram, YouTube, LinkedIn, X). |
| `social-avatar-512.png` | PNG 512×512 | Social profile image. |
| `social-avatar-1024.png` | PNG 1024×1024 | High-res social image. |

## Open Graph

| File | Type | Purpose |
|------|------|---------|
| `og-template.svg` | SVG | OG previews. Replace [CATEGORY] and [HEADLINE] per article. |
| `og-template.png` | PNG 1200×630 | OG image export. |

## Favicon & System Icons

| File | Type | Purpose |
|------|------|---------|
| `favicon.svg` | SVG | Browser tab, bookmarks (modern browsers). |
| `favicon-16.png` | PNG 16×16 | Favicon legacy. |
| `favicon-32.png` | PNG 32×32 | Favicon legacy. |
| `favicon-48.png` | PNG 48×48 | Favicon legacy. |
| `apple-touch-icon.png` | PNG 180×180 | iOS home screen. |
| `android-chrome-192.png` | PNG 192×192 | Android home screen. |
| `android-chrome-512.png` | PNG 512×512 | Android splash screen. |
| `mstile-150.png` | PNG 150×150 | Microsoft tile. |
| `mask-icon.svg` | SVG | Safari pinned tab (monochrome). |

## Editorial

| File | Type | Purpose |
|------|------|---------|
| `editorial-watermark.svg` | SVG | Decorative background element. **Never used as logo.** See Watermark Policy. |

## Legacy Assets (deprecated — kept for backwards compatibility)

| File | Replaced By |
|------|-------------|
| `logo.svg` | `lv-brand-mark.svg` |
| `logo-dark.svg` | `lv-brand-mark.svg` |
| `logo-light.svg` | `lv-brand-mark.svg` |
| `hero-watermark.svg` | `editorial-watermark.svg` |
| `og-brand.svg` | `og-template.svg` |
| `og-brand.png` | `og-template.png` |

---

# Design Rules

Always:

- Preserve proportions.
- Use official colors.
- Maintain generous whitespace.
- Export from the master SVG.
- Keep the design simple and recognisable.

---

# Never

Never:

- Stretch
- Rotate
- Distort
- Add gradients unless officially approved
- Add shadows
- Apply 3D effects
- Replace the official colors
- Create alternative logo versions
- Use clipart or stock graphics

---

# Relationship to the Design System

The LV Mark complements the shared component system (pillar.css, nav.js, footer.js, components.js).

The shared component system defines:

- Layout
- Typography
- Components
- Spacing

The LV Mark defines:

- Visual identity
- Recognition
- Brand consistency

---

# Long-term Vision

Every visual touchpoint should immediately communicate LevNytt.

Whether a visitor sees:

- an informational article
- a pillar page
- a favicon
- an Open Graph image
- a PDF report
- a social media card
- a presentation
- a future application

the visual identity should remain instantly recognizable.

One brand.

One visual language.

One recognizable symbol.
