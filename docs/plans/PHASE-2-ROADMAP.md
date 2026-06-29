# Phase 2 — Content Authority Pipeline

> **Status:** Active
> **Previous Phase:** Phase 1 (Site Build — complete)
> **Next Phase:** Phase 3 (Automation & Intelligence)
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
| **Key Deliverable** | Working savings calculator on the Affärsmöjlighet page (static version first, full interactivity in Phase 3) |

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

### 11. AI Content Pipeline

| Field | Value |
|-------|-------|
| **Status** | Planned |
| **Priority** | Medium |
| **Dependencies** | Affärsmöjlighet 2.0 content (establishes tone and structure), Product Entity System (needs product data for generation) |
| **Estimated Complexity** | Medium (workflow definition + prompt templates + automation scripts) |
| **Purpose** | Build a repeatable, AI-assisted content production workflow so LevNytt can scale authority content without sacrificing quality or transparency. Removes manual bottlenecks while keeping editorial control. |
| **Key Deliverable** | Documented pipeline with prompt templates, fact-check workflow, editorial checklist, and automation scripts for internal linking, schema generation, and publishing. |

**Pipeline stages:**

| Stage | Description | AI Role |
|-------|-------------|---------|
| Research | Gather source material, competitor analysis, SERP data | Assist (gathering, summarising) |
| Fact verification | Cross-check claims against NeoLife sources, scientific studies, and regulatory data | Assist (flagging inconsistencies) |
| Draft generation | Produce first draft following LevNytt tone and IA patterns | Generate |
| Editorial review | Human editor reviews, rewrites, approves | Human (final say) |
| Internal linking automation | Scan new content against existing pages, suggest natural link placements | Assist |
| Schema generation | Generate Article, FAQPage, HowTo, Product JSON-LD structured data | Automate |
| Publishing workflow | Push to staging, review, schedule, deploy | Automate |

**How this supports future authority content:**

- Enables rapid production of informational articles without content debt
- Keeps tone consistent across every page (no drift)
- Automates the tedious parts (schema, internal links) so editors focus on substance
- Creates a template system that new writers (or future team members) can follow
- Ensures every piece of content meets Phase 2's transparency standards before it ships

---

### 12. Analytics & Authority Dashboard

| Field | Value |
|-------|-------|
| **Status** | Planned |
| **Priority** | Medium |
| **Dependencies** | Affärsmöjlighet 2.0 live (needs baseline data), Authority Content Expansion (needs content to measure) |
| **Estimated Complexity** | Low-Medium (GA4 + GSC setup + simple dashboard) |
| **Purpose** | Measure whether Phase 2 actually improves authority and search visibility. Replace guesswork with data. |
| **Key Deliverable** | Internal dashboard (markdown or lightweight HTML) showing key SEO and engagement metrics. |

**Metrics tracked:**

| Metric | Source | Purpose |
|--------|--------|---------|
| Search Impressions | Google Search Console | Are pages being discovered? |
| Search CTR | Google Search Console | Are titles/meta descriptions working? |
| Top Queries | Google Search Console | What is LevNytt ranking for? |
| Top Pages | Google Search Console | Which pages drive traffic? |
| Average Position | Google Search Console | Is authority improving over time? |
| Page Views | Google Analytics | Are visitors engaging? |
| Time on Page | Google Analytics | Is content holding attention? |
| Bounce Rate | Google Analytics | Are visitors finding what they need? |
| Scroll Depth | Google Analytics (enhanced) | Are visitors reading full pages? |
| Internal Link Clicks | Google Analytics | Are content journeys working? |
| Outlink Clicks (registrations) | Google Analytics | Are visitors taking action? |

**Dashboard outputs:**
- Monthly content performance report (auto-generated from GSC + GA data)
- Authority score trend (composite of position, CTR, and engagement)
- Top opportunity queries (pages ranking 11-20 that could reach top 10)
- Content gap alerts (high-volume queries LevNytt doesn't target)

---

### 13. Video Authority Pipeline

| Field | Value |
|-------|-------|
| **Status** | Planned |
| **Priority** | Medium |
| **Dependencies** | Affärsmöjlighet 2.0 content (primary source material), Authority Content Expansion (articles to adapt from) |
| **Estimated Complexity** | Medium (script adaptation + recording + publishing workflow) |
| **Purpose** | Expand written authority content into video assets that reach audiences on YouTube, Pinterest, and short-form platforms. Every article becomes a potential video. |
| **Key Deliverable** | Documented article-to-video workflow + first batch of companion videos for key pages. |

**Platforms:**

| Platform | Content Type | Format | Purpose |
|----------|-------------|--------|---------|
| YouTube | Full companion videos | 4-10 min | Embed on article pages, long-form SEO |
| Pinterest | Infographic pins, idea pins | Static + short video | Drive referral traffic, visual discovery |
| Short-form (Shorts/Reels) | Key takeaways, quick tips | 30-60 sec | Brand awareness, younger audiences |

**Article-to-video workflow:**

```
Article published
  │
  ▼
Script adaptation (condense article into spoken script)
  │
  ▼
Fact-check script against article source
  │
  ▼
Record (talking head + screen share + B-roll)
  │
  ▼
Edit + captions + thumbnail
  │
  ▼
Publish to YouTube → embed on article page
  │
  ▼
Repurpose clips for Shorts / Reels / Pinterest
```

**Future expansion (Phase 3+):**
- AI-assisted narration (synthetic voiceovers for rapid video production)
- Automated caption generation and translation
- Dynamic video thumbnails with A/B testing
- YouTube channel SEO optimisation

---

## Dependencies

```
Affärsmöjlighet 2.0
  │
  ├─────────────────────────────────────────────────────┐
  ▼                                                     │
Product Entity System                                   │
  │                                                     │
  ▼                                                     │
Dynamic Product Database                                │
  │                                                     │
  ├────────────┬────────────┬────────────┐              │
  ▼            ▼            ▼            │              │
Besparings-   Pris per     Produkt-      │              │
kalkylator    användning   jämförelser   │              │
  │            │            │            │              │
  └────────────┴────────────┘            │              │
               ▼                         │              │
      Interactive Decision Tools ←───────┘              │
               │                                        │
               ▼                                        │
      Video Integration                                 │
               │                                        │
               ▼                                        │
      Internal Recommendation Engine ←──────────────────┘
               │                                        │
               ├────────────────────┐                   │
               ▼                    ▼                   │
      Authority Content    AI Content Pipeline          │
      Expansion (ongoing)  (feeds expansion)            │
               │                    │                   │
               └────────┬───────────┘                   │
                        ▼                               │
               Video Authority Pipeline                 │
               (article → video)                        │
                                                        │
      Analytics & Authority Dashboard ←─────────────────┘
      (measures everything, runs in parallel)
```

### Dependency Rules

- **Must block:** Dynamic Product Database cannot be built before Product Entity System exists. Calculators cannot work without the database.
- **Can run in parallel:** Video Integration and Product Entity System are independent. Authority Content Expansion can begin as soon as content patterns are established. Analytics & Authority Dashboard runs alongside all other projects.
- **Soft dependency (content, not code):** Interactive Decision Tools needs calculator content to exist, but the JavaScript layer can be developed in parallel with the data layer using mock data.
- **Cumulative dependency:** Internal Recommendation Engine becomes more valuable as more content exists. Build it early (architecture) but it reaches full value late (content volume).
- **Feeder dependency:** AI Content Pipeline feeds Authority Content Expansion — it produces the articles that expand the library. Video Authority Pipeline consumes articles and turns them into video assets.
- **Measurement dependency:** Analytics & Authority Dashboard has full value only after other projects ship, but data collection (GA/GSC) should begin on day one to establish baselines.

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
| M10 | **AI content pipeline operational** | Research, draft generation, fact-check, editorial review, internal linking, schema generation, and publishing workflow documented and tested with at least 2 articles. | Project 11 |
| M11 | **Analytics dashboard live** | GSC + GA data flowing. Monthly report template created. Baseline metrics recorded for authority score, impressions, CTR, and top queries. | Project 12 |
| M12 | **First video companion published** | Article-to-video workflow documented. At least one companion video published and embedded on its corresponding article page. | Project 13 |

### Milestone Schedule (Target)

| Timeframe | Milestones |
|-----------|------------|
| Month 1 | M1 (Affärsmöjlighet content) |
| Month 2 | M2, M3 (Product data infrastructure) |
| Month 3 | M4, M5 (Calculators & comparisons) |
| Month 4 | M6, M7 (Interactive tools & video) |
| Month 5 | M8, M10 (Recommendation engine + AI pipeline) |
| Month 6 | M9, M11, M12 (Content expansion + analytics + video authority) |
| Ongoing | M9 continued, M11 reporting cadence |

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

### AI & Automation

- [ ] AI content pipeline documented with all 7 stages defined and tested
- [ ] At least 2 articles produced through the AI pipeline end-to-end
- [ ] Schema generation automated in the publishing workflow
- [ ] Internal linking suggestions integrated into the editorial workflow

### Analytics & Measurement

- [ ] Google Search Console + Google Analytics tracking active on all Phase 2 pages
- [ ] Monthly content performance report template exists
- [ ] Baseline authority score recorded (composite of position, CTR, engagement)
- [ ] Top opportunity queries identified (pages ranking 11-20)

### Video Authority

- [ ] Article-to-video workflow documented
- [ ] At least 1 companion video published and embedded on its article page
- [ ] Video hosted on YouTube and integrated into the page

### Platform Health

- [ ] All Phase 2 pages pass Lighthouse mobile score > 70 (Performance) and > 90 (Accessibility, SEO)
- [ ] All Phase 2 pages have Article or FAQPage schema
- [ ] Internal links flow naturally between Affärsmöjlighet and all pillar pages
- [ ] No dead ends — every page has at least one onward journey path
- [ ] Git history shows consistent commit messages matching repo style

### Definition of "Phase 2 Complete"

When the success criteria checklist above is fully green, Phase 2 ends and Phase 3 (Automation & Intelligence) begins. The Affärsmöjlighet page at this point is a complete, transparent decision-support page with static calculators and embedded multimedia. The AI content pipeline, analytics dashboard, and video authority workflow are operational. Phase 3 will layer on interactive tools, automation, AI-assisted workflows, advanced recommendation systems, personalization, and future intelligent features.

---

## Appendix: Relationship to Existing Documents

| Document | Relationship |
|----------|-------------|
| `AFFARSMOJLIGHET-2.0-MASTERPLAN.md` | First completed Phase 2 deliverable. Defines the what. This roadmap defines the when and how. |
| Future Affärsmöjlighet HTML page | The concrete output of Project 1. Must match the IA in the master plan. |
| Future product data files | The concrete output of Projects 2-3. Follows schema defined during implementation. |
| Future pipeline documentation | The concrete output of Project 11. Defines the AI content workflow. |
| Future analytics dashboard | The concrete output of Project 12. Tracks Phase 2 success metrics. |
| Future video workflow documentation | The concrete output of Project 13. Defines the article-to-video pipeline. |

---

*This roadmap is the implementation authority for Phase 2. No HTML pages have been modified in its creation.*
