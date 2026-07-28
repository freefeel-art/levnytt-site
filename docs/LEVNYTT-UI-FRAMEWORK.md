# LevNytt UI Framework v1

This is the production reference for shared visual foundations and page-family contracts. Every sitemap-listed production page loads the same site shell and foundation/component styles; page purpose still determines which template contract applies.

## Foundations

`assets/css/levnytt-foundations.css` is the canonical token source. It defines brand, surface, caution, border and text colors, display/body fonts, eight spacing steps, radii, shell and reading widths, and editorial/social image ratios. Standardized templates consume named tokens; they do not repeat literal color values.

## Templates

| Family | Contract | Migration state |
| --- | --- | --- |
| Home / editorial hub | Site shell and editorial discovery | Shared-shell migrated |
| Article / information | `informational-article-v1` + `ia-wrap` | Default baseline; representative pages migrated |
| Authority / pillar / reference | `authority-editorial-trust-v1` | LevNytt Principles migrated; other authority pages share the shell pending their page-purpose migration |
| Product and product-category | Product disclosure and comparison contract | Shared-shell and card-contract migrated; preserve product-specific hierarchy |
| Library / category / search-index | Index and filtering contract | Shared-shell and editorial-card contract migrated |
| Utility and legal | Minimal, accessible utility shell | Shared-shell migrated |

## Shared components

The required common components are: site shell, navigation, footer, brand mark, breadcrumbs, editorial header, approved hero variants, metadata/byline/disclosure, semantic callouts, cards/grids, responsive tables, FAQ accordion, internal-link cluster, author block, CTA block, and image frame/caption.

`nav.js` and `footer.js` own global shell rendering. The footer uses the registered canonical `header-logo.svg`; `logo-light.svg` is legacy-only and must not be introduced into new shared work.

`assets/css/levnytt-components.css` supplies the only approved card variants: editorial, article/index, authority/trust, product, evidence/info, and warning/caution. Existing page classes are mapped in `config/ui-card-classification.json`; a new production card class must be added to that explicit registry and use the shared visual contract.

## Site-wide migration guarantees

The shell migrator places exactly one `#site-nav` mount immediately inside `body`, loads `nav.js` and `footer.js`, and loads the foundations and component styles for every sitemap-listed production page. The production UI audit verifies these contracts across the entire sitemap, including card classification and declared template requirements.

The link audit treats `levnytt.se`, relative and root-relative destinations as internal. Ordinary body links are canonicalized to same-tab root-relative links. The Owner-approved global navigation exception is explicit: every actual link emitted by `nav.js` or `footer.js`, including internal links and clickable logos, opens a new tab and carries `noopener noreferrer`; sponsored links preserve their relationship token. Menu buttons and other non-link controls are not affected.

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

1. Preserve the shared shell, canonical cards and link contracts as non-negotiable for every production page.
2. Keep Publication Agent articles as the reference baseline; migrate remaining legacy informational layouts only when page-level visual QA confirms no lost functionality.
3. Migrate authority-adjacent pages to the authority/trust template after their distinct trust contract is verified.
4. Keep product pages in their product family; remove page-local styling only when the product/disclosure behavior has an approved shared replacement.
5. Retire a legacy local override only after an equivalent shared component exists and has desktop, tablet and mobile visual QA coverage.
