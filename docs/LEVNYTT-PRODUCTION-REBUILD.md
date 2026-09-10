# LevNytt canonical production rebuild

LevNytt production pages are generated from `content/data/production-pages.json`
through `scripts/rebuild-production.py`. The generator applies one of six page
families and the shared shell, components and tokens:

`content data → family template → shared shell/components → token CSS → HTML`

The bootstrap command intentionally reads the current sitemap once to preserve
titles, metadata, canonical URLs, JSON-LD, images and body content. Subsequent
builds are deterministic from the content registry. `--build` writes only the
sitemap-listed production routes; unlisted source files are not deployed.

## Canonical components

The generated shell provides `SiteHeader`, `PrimaryNavigation`, `SiteFooter`,
`Breadcrumbs`, `ArticleHeader`, `ArticleBody`, and the shared semantic styling
for key takeaways, information cards, related links, CTA blocks, source lists
and author/disclosure blocks retained in page content.

## Canonical presentation contract

Design tokens, layout primitives and all shared production components are
defined in the single canonical stylesheet `assets/css/levnytt.css`.
`scripts/site_renderer.py` owns the shared shell and maps retained source
markup to the stable `ln-*` component vocabulary at the build boundary.
Generated pages do not contain page CSS or load page-family override sheets.

Internal links retain normal same-tab navigation. External links that open a
new tab retain `noopener noreferrer`; sponsored links also preserve their
commercial relationship tokens and destination parameters.

Inline SVG presentation styles are converted to presentation attributes during
bootstrap so they remain part of the asset while page CSS stays centralized.

## Validation

`scripts/validate-rebuild.py` checks all sitemap routes, shared shell, one H1,
canonical styles, absence of inline page CSS, link safety, and source-token
preservation. `scripts/audit-production-links.py` and
`scripts/audit-production-ui.py` provide repository-wide reports.

Deployment follows the repository's established Cloudflare Pages Git workflow.
The previous deployed revision remains available in Git and Cloudflare as the
rollback reference.
