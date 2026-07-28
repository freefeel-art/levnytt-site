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

## Tokens and link policy

Design tokens are defined in `assets/css/levnytt-foundations.css`; shared
production rules are in `assets/css/levnytt-rebuild.css`. Generated pages do
not contain page CSS. Every hyperlink, including internal links and shell
links, uses `target="_blank"` and `rel="noopener noreferrer"`; sponsored
links preserve their sponsored relationship token.

Inline SVG presentation styles are converted to presentation attributes during
bootstrap so they remain part of the asset while page CSS stays centralized.

## Validation

`scripts/validate-rebuild.py` checks all sitemap routes, shared shell, one H1,
canonical styles, absence of inline page CSS, link safety, and source-token
preservation. `scripts/audit-production-links.py` and
`scripts/audit-production-ui.py` provide repository-wide reports.

The rebuild is prepared for review only. Deployment requires a separate Owner
approval that names the exact commit and keeps the previous deployed revision
as rollback reference.
