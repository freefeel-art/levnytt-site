# LevNytt Brand Usage Guide

**Status:** Brand Asset Pack V1 — APPROVED
**Location:** `assets/brand/`
**Visual reference:** `docs/brand/brand-system-reference.png`

This document is the permanent Single Source of Truth for every visual asset in the LevNytt platform.

---

## Mission

LevNytt is an editorial publication.

The visual identity must communicate:

- independent thinking
- scientific credibility
- calm authority
- Scandinavian clarity

The brand should never resemble an MLM company, an ecommerce store, or a startup.

---

## Master Assets

### 1. LV Brand Mark

**File:** `lv-brand-mark.svg`

Primary identity. Used for:

- Header (`header-logo.svg`)
- Footer
- Author Avatar (`author-avatar.svg`)
- Social Avatar (`social-avatar.svg`)
- Favicon (`favicon.svg`)
- Open Graph (`og-template.svg`)
- PDF
- Brand Signatures

Never modified. Never redesigned. Never replaced.

### 2. Editorial Watermark

**File:** `editorial-watermark.svg`

Decorative editorial illustration. Used for:

- Hero backgrounds
- Section backgrounds
- Report covers

Never used as a logo.

---

## Derived Assets

All derived directly from `lv-brand-mark.svg`. No independent redesigns are permitted.

| Asset | Format | Purpose |
|-------|--------|---------|
| `header-logo.svg` | SVG | Site header, sticky nav, mobile nav. Brand Mark + "LevNytt" wordmark. |
| `author-avatar.svg` | SVG | Editorial byline, article meta, author signature. Identical to master. |
| `social-avatar.svg` | SVG 120×120 | Social media profiles. 82 % canvas fill. |
| `social-avatar-512.png` | PNG 512×512 | Social profile image export. |
| `social-avatar-1024.png` | PNG 1024×1024 | High-res social image export. |
| `og-template.svg` | SVG 1200×630 | OG previews. Replace [CATEGORY] and [HEADLINE] per article. |
| `og-template.png` | PNG 1200×630 | OG image export. |
| `favicon.svg` | SVG | Browser tab, bookmarks (modern browsers). |
| `favicon-16.png` | PNG 16×16 | Favicon legacy. |
| `favicon-32.png` | PNG 32×32 | Favicon legacy. |
| `favicon-48.png` | PNG 48×48 | Favicon legacy. |
| `apple-touch-icon.png` | PNG 180×180 | iOS home screen. |
| `android-chrome-192.png` | PNG 192×192 | Android home screen. |
| `android-chrome-512.png` | PNG 512×512 | Android splash screen. |
| `mstile-150.png` | PNG 150×150 | Microsoft tile. |
| `mask-icon.svg` | SVG | Safari pinned tab (monochrome). |

### Legacy assets (deprecated — kept for backwards compatibility)

| File | Replaced By |
|------|-------------|
| `logo.svg` | `lv-brand-mark.svg` |
| `logo-dark.svg` | `lv-brand-mark.svg` |
| `logo-light.svg` | `lv-brand-mark.svg` |
| `hero-watermark.svg` | `editorial-watermark.svg` |
| `og-brand.svg` | `og-template.svg` |
| `og-brand.png` | `og-template.png` |

---

## Official Colors

| Name | Hex | Usage |
|------|-----|-------|
| Deep Green | `#1B4332` | LV mark fill, wordmark "Lev", headline text, continent shapes |
| Gold | `#E8C870` | LV mark border, LV monogram, wordmark "Nytt", category label, accent lines |
| Cream | `#FAF7F0` | OG background, accent card backgrounds |
| White | `#FFFFFF` | Page backgrounds, text on dark blocks |
| Ink | `#1A1A1A` | Body text (pillar.css `--ink`) |

---

## Typography

| Role | Typeface | Fallback |
|------|----------|----------|
| Headlines | Playfair Display | Georgia, 'Times New Roman', serif |
| Body | Inter | Arial, system-ui, sans-serif |

No substitutions without updating this document.

---

## Safe Zones

| Asset | Minimum Clear Space |
|-------|-------------------|
| LV Brand Mark | 25 % of icon diameter in all directions |
| Header Logo | 20 % of total height on all sides |
| Social Avatar | 10 % of canvas (82 % fill spec) |

---

## Watermark Policy

`editorial-watermark.svg` is a decorative editorial element, not a logo.

- **Always:** hero backgrounds, section backgrounds, PDF covers, OG watermark.
- **Never:** header, footer, author avatar, favicon, social avatar, brand signatures.
- **Opacity:** 10–15 % when used as background. Full opacity only in documentation.

---

## Design Principles

- Editorial before commercial.
- Clarity before decoration.
- Trust before marketing.
- Consistency before creativity.
- Premium without luxury.
- Scientific without clinical.
- Warm without being casual.

---

## Do

✓ Use generous whitespace.
✓ Keep layouts calm.
✓ Use the Brand Mark consistently.
✓ Use the Watermark subtly.
✓ Maintain visual hierarchy.

## Don't

✗ Don't redesign the logo.
✗ Don't create alternate icons.
✗ Don't add gradients.
✗ Don't use drop shadows.
✗ Don't distort the Brand Mark.
✗ Don't use the Watermark as a logo.
✗ Don't create competing visual identities.

---

## Engineering Rule

Every future asset must originate from the approved Brand Assets.

No new brand graphics may be introduced without updating this document first.
