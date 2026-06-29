# Phase 2 — Content Authority Pipeline

> **Status:** Active
> **Previous Phase:** Phase 1 (Site Build — complete)
> **Next Phase:** Phase 3 (Calculators & Interactivity)
> **First Completed Document:** `AFFARSMOJLIGHET-2.0-MASTERPLAN.md`

---

## Phase 2 Goal

Phase 1 delivered a complete, SEO-optimized Astro website with pillar pages, informational articles, and brand-correct styling. LevNytt exists as a site.

Phase 2 moves LevNytt from a *completed website* into an **authoritative knowledge platform**. The site stops being a collection of pages and starts being a connected, decision-support system for visitors evaluating NeoLife.

This phase has three objectives:

1. **Depth** — Replace shallow pages with thorough, transparent, decision-oriented content.
2. **Connectivity** — Link content into journeys, not dead ends.
3. **Infrastructure** — Build the data layer needed for future interactive tools.

Everything in Phase 2 serves the core philosophy: *Spara pengar. Använd produkterna. Dela vidare om du vill.*

---

## Project Pipeline

Projects are ordered by implementation sequence. Later projects depend on earlier ones.

---

### 1. Affärsmöjlighet 2.0

| Field | Value |
|-------|-------|
| **Status** | Planning Complete |
| **Priority** | Critical |
| **Dependencies** | None (standalone page rewrite) |
| **Estimated Complexity** | High (full page content, 10 sections) |
| **Purpose** | Replace existing MLM-style business page with a transparent decision-support page centered on savings, not recruitment. |
| **Key Deliverable** | New `/affarsmojlighet/` HTML page following the architecture in `AFFARSMOJLIGHET-2.0-MASTERPLAN.md` |

---

### 2. Product Entity System

| Field | Value |
|-------|-------|
| **Status** | Planned |
| **Priority** | High |
| **Dependencies** | None (greenfield infrastructure) |
| **Estimated Complexity** | Medium (data architecture + JSON/YAML definitions) |
| **Purpose** | Create a centralized product data source so every page references the same prices, descriptions, and categories. Eliminates copy-paste errors across pillar pages and articles. |
| **Key Deliverable** | `src/data/products.yaml` or `src/data/products.json` with all NeoLife products, prices (customer/distributor), categories, and metadata |

---

### 3. Dynamic Product Database

| Field | Value |
|-------|-------|
| **Status** | Planned |
| **Priority** | High |
| **Dependencies** | Product Entity System (needs data schema) |
| **Estimated Complexity** | Medium (Astro data layer + utility functions) |
| **Purpose** | Turn the static product definitions into a query-able data layer. Enables dynamic price lookups, category filtering, and automated price-per-use calculations across the site. |
| **Key Deliverable** | Importable TypeScript utilities: `getProduct()`, `getProductsByCategory()`, `getSavings()`, `getPricePerUse()` |

---

### 4. Besparingskalkylator

| Field | Value |
|-------|-------|
| **Status** | Planned |
| **Priority** | High |
| **Dependencies** | Dynamic Product Database (needs live prices) |
| **Estimated Complexity** | Medium (static table + JS-enhanced calculator) |
| **Purpose** | Let visitors select products they use and see exact annual savings at distributor pricing. This is the "soft close" of the Affärsmöjlighet page — the moment the visitor internalizes the value. |
| **Key Deliverable** | Working savings calculator on the Affärsmöjlighet page (static version first, interactive in Phase 3) |

---

### 5. Pris per användning

| Field | Value |
|-------|-------|
| **Status** | Planned |
| **Priority** | Medium |
| **Dependencies** | Dynamic Product Database (needs dosage/usage data) |
| **Estimated Complexity** | Low-Medium (comparison tables + narrative) |
| **Purpose** | Show visitors that NeoLife products are often cheaper per serving than store brands, even before distributor discounts. Addresses the "but isn't it expensive?" objection directly. |
| **Key Deliverable** | Price-per-use section on Affärsmöjlighet page + standalone comparison table component |

---

### 6. Produktjämförelser

| Field | Value |
|-------|-------|
| **Status** | Planned |
| **Priority** | Medium |
| **Dependencies** | Dynamic Product Database (needs full product catalog) |
| **Estimated Complexity** | Medium (sortable/filterable table + category views) |
| **Purpose** | Give visitors a single place to compare all NeoLife products by price, savings, category, and price-per-use. Replaces scattered pricing information across pillar pages. |
| **Key Deliverable** | Product comparison table (static page or Astro component with filtering) |

---

### 7. Interactive Decision Tools

| Field | Value |
|-------|-------|
| **Status** | Planned |
| **Priority** | Medium |
| **Dependencies** | Besparingskalkylator, Pris per användning, Produktjämförelser (all content must exist first) |
| **Estimated Complexity** | High (JavaScript interactivity, state management, responsive UX) |
| **Purpose** | Combine the three calculator/comparison features into an integrated decision-support experience. Visitors can flow naturally from "what do I use?" → "what do I save?" → "should I register?" |
| **Key Deliverable** | Interactive JavaScript widget suite on the Affärsmöjlighet page |

---

### 8. Video Integration

| Field | Value |
|-------|-------|
| **Status** | Planned |
| **Priority** | Low-Medium |
| **Dependencies** | Affärsmöjlighet 2.0 content (video script derived from page content) |
| **Estimated Complexity** | Medium (scriptwriting, recording, editing, embedding) |
| **Purpose** | Add a 2-4 minute explainer video to the Affärsmöjlighet page. A human voice explaining the same transparent message reinforces trust and caters to visitors who prefer watching over reading. |
| **Key Deliverable** | Embedded video in the Affärsmöjlighet page (hosted on YouTube/Vimeo) |

---

### 9. Internal Recommendation Engine

| Field | Value |
|-------|-------|
| **Status** | Planned |
| **Priority** | Low |
| **Dependencies** | Authority Content Expansion (needs breadth of content to recommend from) |
| **Estimated Complexity** | Medium (tagging system + related-content logic) |
| **Purpose** | Show relevant articles, pillar pages, and tools at the bottom of every page based on content tags. Keeps visitors on the site longer and naturally guides them toward informed decisions. |
| **Key Deliverable** | `src/components/RelatedContent.astro` with tag-based matching and configurable display count |

---

### 10. Authority Content Expansion

| Field | Value |
|-------|-------|
| **Status** | Planned |
| **Priority** | Medium (ongoing) |
| **Dependencies** | All above projects (establishes patterns to follow) |
| **Estimated Complexity** | Variable (depends on number of new articles) |
| **Purpose** | Expand LevNytt's content library with additional informational articles, comparison guides, and FAQ pages. Each new piece reinforces the site's authority and creates more entry points from search. |
| **Key Deliverable** | N new informational articles following the established tone and schema patterns |

---

## Dependencies

```
Affärsmöjlighet 2.0
  │
  ▼
Product Entity System ─────────────────────────────┐
  │                                                  │
  ▼                                                  │
Dynamic Product Database                             │
  │                                                  │
  ├────────────┬────────────┬────────────┐           │
  ▼            ▼            ▼            │           │
Besparings-   Pris per     Produkt-      │           │
kalkylator    användning   jämförelser   │           │
  │            │            │            │           │
  └────────────┴────────────┘            │           │
               ▼                         │           │
      Interactive Decision Tools ←───────┘           │
               │                                      │
               ▼                                      │
      Video Integration                               │
               │                                      │
               ▼                                      │
      Internal Recommendation Engine ←────────────────┘
               │                                      │
               ▼                                      ▼
      Authority Content Expansion (ongoing)
```

### Dependency Rules

- **Must block:** Dynamic Product Database cannot be built before Product Entity System exists. Calculators cannot work without the database.
- **Can run in parallel:** Video Integration and Product Entity System are independent. Authority Content Expansion can begin as soon as content patterns are established.
- **Soft dependency (content, not code):** Interactive Decision Tools needs calculator content to exist, but the JavaScript layer can be developed in parallel with the data layer using mock data.
- **Cumulative dependency:** Internal Recommendation Engine becomes more valuable as more content exists. Build it early (architecture) but it reaches full value late (content volume).

---

## Milestones

| # | Milestone | Criteria | Target Projects |
|---|-----------|----------|-----------------|
| M1 | **Affärsmöjlighet content complete** | All 10 IA sections written, reviewed, and published. No interactive features yet — just the narrative, tables, and FAQ. | Project 1 |
| M2 | **Product data centralized** | All NeoLife products entered into YAML/JSON with consistent fields. Prices verified against current NeoLife SE pricing. | Project 2 |
| M3 | **Data layer queryable** | `getProduct()`, `getSavings()`, `getPricePerUse()` working and used by at least one page. | Project 3 |
| M4 | **First calculator live** | Static or semi-interactive savings calculator visible on Affärsmöjlighet page. Visitors can see example savings. | Project 4 |
| M5 | **Full pricing transparency** | Price-per-use comparisons and product comparison table both published. Every product has a clear customer vs distributor price. | Projects 5, 6 |
| M6 | **Interactive decision tools ship** | Visitors can select products, see savings, compare options, and reach an informed decision — all within one page experience. | Project 7 |
| M7 | **Multimedia layer added** | Video embedded. Page supports reading, watching, and calculating. | Project 8 |
| M8 | **Site-wide content recommendations** | Related content appears on pillar pages and articles. Visitors naturally discover connected content. | Project 9 |
| M9 | **Content library expanded** | 5+ new informational articles published that link to and from the Affärsmöjlighet page. | Project 10 |

### Milestone Schedule (Target)

| Timeframe | Milestones |
|-----------|------------|
| Month 1 | M1 (Affärsmöjlighet content) |
| Month 2 | M2, M3 (Product data infrastructure) |
| Month 3 | M4, M5 (Calculators & comparisons) |
| Month 4 | M6, M7 (Interactive tools & video) |
| Month 5 | M8 (Recommendation engine) |
| Ongoing | M9 (Content expansion) |

---

## Success Criteria

Phase 2 is complete when all of the following are true:

### Content

- [ ] Affärsmöjlighet 2.0 page is live with all 10 IA sections from the master plan
- [ ] No income claims, hype language, or pressure CTAs exist on the page
- [ ] FAQ contains at least 8 questions with thorough answers
- [ ] Customer vs Distributor vs Business comparison is documented with neutral tone
- [ ] At least 5 product savings examples with real prices are shown

### Data Infrastructure

- [ ] Product Entity System contains all LevNytt-listed NeoLife products
- [ ] Dynamic Product Database exposes `getProduct()`, `getProductsByCategory()`, `getSavings()`, and `getPricePerUse()` utilities
- [ ] Product data is the single source of truth — no hardcoded prices remain on the Affärsmöjlighet page

### Tools

- [ ] Savings calculator shows customer vs distributor pricing with annual projection
- [ ] Price-per-use comparison exists for at least 5 products vs store alternatives
- [ ] Product comparison table is sortable or filterable

### Interactivity

- [ ] Visitors can select products and see personalized savings estimates
- [ ] Video is embedded and functional
- [ ] Internal recommendation engine displays relevant content on pillar pages and articles

### Platform Health

- [ ] All Phase 2 pages pass Lighthouse mobile score > 70 (Performance) and > 90 (Accessibility, SEO)
- [ ] All Phase 2 pages have Article or FAQPage schema
- [ ] Internal links flow naturally between Affärsmöjlighet and all pillar pages
- [ ] No dead ends — every page has at least one onward journey path
- [ ] Git history shows consistent commit messages matching repo style

### Definition of "Phase 2 Complete"

When the success criteria checklist above is fully green, Phase 2 ends and Phase 3 (Calculators & Advanced Interactivity) begins. The Affärsmöjlighet page at this point is a complete, transparent decision-support page with static calculators and embedded multimedia — ready for the dynamic JavaScript layer that Phase 3 will add.

---

## Appendix: Relationship to Existing Documents

| Document | Relationship |
|----------|-------------|
| `AFFARSMOJLIGHET-2.0-MASTERPLAN.md` | First completed Phase 2 deliverable. Defines the what. This roadmap defines the when and how. |
| Future Affärsmöjlighet HTML page | The concrete output of Project 1. Must match the IA in the master plan. |
| Future product data files | The concrete output of Project 2-3. Follows schema defined during implementation. |

---

*This roadmap is the implementation authority for Phase 2. No HTML pages have been modified in its creation.*
