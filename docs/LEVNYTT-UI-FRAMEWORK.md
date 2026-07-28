# LevNytt UI Framework v1

This is the production reference for shared visual foundations. It standardizes the system without requiring a site-wide redesign.

## Foundations

`assets/css/levnytt-foundations.css` is the canonical token source. It defines brand colors, display/body fonts, eight spacing steps, radii, shell and reading widths, and editorial/social image ratios. Standardized templates consume named tokens; they do not repeat brand-color literals.

## Templates

| Family | Contract | Migration state |
| --- | --- | --- |
| Home / editorial hub | Site shell and editorial discovery | Existing; not changed in v1 |
| Article / information | `informational-article-v1` + `ia-wrap` | Default baseline |
| Authority / pillar / reference | Pillar shell and research components | Later migration |
| Product and product-category | Product disclosure and comparison contract | Later migration |
| Library / category / search-index | Index and filtering contract | Later migration |
| Utility and legal | Minimal, accessible utility shell | Later migration |

## Shared components

The required common components are: site shell, navigation, footer, brand mark, breadcrumbs, editorial header, approved hero variants, metadata/byline/disclosure, semantic callouts, cards/grids, responsive tables, FAQ accordion, internal-link cluster, author block, CTA block, and image frame/caption.

`nav.js` and `footer.js` own global shell rendering. The footer uses the registered canonical `header-logo.svg`; `logo-light.svg` is legacy-only and must not be introduced into new shared work.

## Informational Article v1

`assets/css/informational-article.css` owns the reusable `ia-*` shell: editorial header, headings, takeaways, callouts, tables, FAQ, internal-link cluster, author block, disclosure, and CTA variants. Informational pages use the `ia-wrap` family as their baseline and declare:

```html
<meta name="levnytt-template" content="informational-article-v1">
<meta name="levnytt-cta" content="none|internal|product-referral|affiliate-referral">
```

Referral variants also require `levnytt-disclosure` metadata and a visible `.ia-disclosure` block. `none` is valid for consumer-information pages.

## Accessibility and responsive rules

Use semantic heading order, visible focus, sufficient color contrast, descriptive image alt text, native `details/summary` FAQ interaction, tables that remain readable on small screens, and a single reading column at narrow widths. Images use explicit editorial or social aspect-ratio contracts and must not convey essential information only through color.

## Guard

Run `python3 scripts/validate-informational-page.py <page.html>` for every new or migrated informational page. It rejects missing shared navigation/footer, an unapproved article template, literal brand colors in the standardized template, unclassified CTA behavior, and missing referral disclosure metadata.

## Progressive migration

1. Keep Publication Agent articles as the reference baseline; migrate compact `ia-wrap` articles where shell extraction is mechanical.
2. Migrate S4/R2 legacy article families after page-by-page visual QA.
3. Migrate R3/S2 authority-adjacent articles after their content contracts are confirmed.
4. Address R1/S3 pillars and all product families separately; they require distinct page-purpose and disclosure review.
5. Retire legacy one-off styling only after an equivalent shared component exists and has visual QA coverage.
