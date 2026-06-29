# CURRENT-SPRINT.md
# LevNytt.se — Project Phase

Last updated: 2026-06-29

---

## Phase: Maintenance + Feature Development

The Gen 3 migration project is **complete**.

- **55/55** public pages migrated to Gen 3
- **55/55** pages pass the 13/13 audit checklist
- **0** remaining migration backlog items

All pages now share:
- `pillar.css` (shared design system)
- `nav.js` / `footer.js` / `components.js` with `defer`
- Verification meta tags (Google + Pinterest)
- Page-specific `og:image`
- At least 3 responsive breakpoints
- Google Fonts (Playfair Display + Inter)

---

## Future work

No active sprint. When a new sprint opens, candidates include:

| Area | Description |
|---|---|
| **Content expansion** | New articles, product pages, informational guides |
| **Product entity system** | Structured product data via `content/products/` schema |
| **Canonical cleanup** | Align trailing-slash canonical URLs with sitemap entries |
| **Performance** | Image optimization, lazy loading, Core Web Vitals |
| **Accessibility** | Contrast checks, ARIA labels, keyboard navigation |

---

## Sprint template

When opening a new sprint, use:

```
## Sprint status
Active.

## Sprint objective
[One sentence describing the goal.]

## Tasks
- [ ] Task 1
- [ ] Task 2

## Completion criteria
[Specific, verifiable conditions that define "done".]

## Next action
[Exactly what to do next.]
```
