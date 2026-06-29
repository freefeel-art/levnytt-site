# CURRENT-SPRINT.md
# LevNytt.se — Project Phase

Last updated: 2026-06-29

---

## Phase: Maintenance + Feature Development

The Gen 3 migration project is **complete**.

- **All public pages** migrated to Gen 3
- **All public pages** pass the 13/13 audit checklist
- **0** remaining migration backlog items

All pages now share:
- `pillar.css` (shared design system)
- `nav.js` / `footer.js` / `components.js` with `defer`
- Verification meta tags (Google + Pinterest)
- Page-specific `og:image`
- At least 3 responsive breakpoints
- Google Fonts (Playfair Display + Inter)

---

## Sprint Status

| | |
|---|---|
| **Status** | ✅ Completed |
| **Sprint** | 7 — Affärsmöjlighet 2.0 |
| **Completed** | 2026-06-29 |

### Tasks

- [x] Read all core project documents (PROJECT-ENTRY, STATUS, SPRINT, DECISIONS, MASTERPLAN, ROADMAP)
- [x] Explore existing page architecture, components, and design patterns
- [x] Build Affärsmöjlighet 2.0 page following masterplan IA
- [x] Build succeeds — 13/13 audit passed
- [x] Committed and pushed

### What was implemented

Complete replacement of `neolife-affarsmojlighet.html` with the new Affärsmöjlighet 2.0 page. The old MLM-style business page with income claims, compensation plan tables, and Director earnings illustrations was replaced with a transparent decision-support page centered on savings.

All 10 IA sections from the masterplan are built:

1. **Hero** — H1 "Hur mycket kan du faktiskt spara som NeoLife återförsäljare?" with ingress and stat row (21% savings, 57 products, 0 kr registration, 0 sales requirements)
2. **"De flesta börjar inte för att sälja"** — narrative section explaining most register for the discount
3. **Video placeholder** — dashed placeholder box for future video
4. **Calculator placeholder** — dashed placeholder box for future savings calculator
5. **Product savings examples** — table with 7 real products, prices from LEVNYTT-PRICE-DATABASE.md
6. **Pris per användning** — cost-per-use table across 6 products
7. **Kund / Återförsäljare / Verksamhet** — three-column comparison using `component-grid` + custom cards
8. **FAQ** — 8 questions using `details/summary` accordion with FAQPage schema
9. **Registration** — step-by-step registration info + CTA block
10. **Closing** — core message repeated, no hard sell

Additional:
- JSON-LD schema: Article + FAQPage + BreadcrumbList
- Internal linking section (`tier-section`) with 6 outgoing links
- 13/13 audit compliance
- Uses existing design system — no new components added to pillar.css

### What was left for later sprints

- **Besparingskalkylator** (interactive) — placeholder only. Logic deferred to Phase 2, Project 4.
- **Video integration** — placeholder only. Deferred to Phase 2, Project 8.
- **Product Entity System** — not built. Deferred to Phase 2, Project 2.
- **Dynamic Product Database** — not built. Deferred to Phase 2, Project 3.
- **OG image** — meta tags point to `images/og/neolife-affarsmojlighet.webp` (needs to be created separately)

### Architectural observations

- The `component-grid`/`component-card` pattern in pillar.css works well for three-column comparisons with minor page-specific overrides. The comparison cards introduced minimal page-specific CSS (`.comparison-card`) that could be promoted to pillar.css if this pattern repeats on other pages.
- The placeholder box pattern (`.placeholder-box`) is intentionally page-specific since it's a temporary pattern. Once calculators and video land, these dashed boxes are replaced entirely.
- No changes to project architecture, shared components, or pillar.css were required.

---

## Future work

Candidates for next sprint include:

| Area | Description |
|---|---|
| **Product Entity System** | Structured product data via `src/data/products.yaml` |
| **Content expansion** | New articles, internal linking from Affärsmöjlighet |
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
