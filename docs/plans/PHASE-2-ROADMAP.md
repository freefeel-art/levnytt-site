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

## Governance Model

### Project Lifecycle

Every project passes through these states:

| State | Criteria | Gate |
|-------|----------|------|
| **Backlog** | Idea identified, not yet planned | — |
| **Planned** | Dependencies mapped, complexity estimated, owner assigned | — |
| **In Progress** | Definition of Ready met (see below) | Gate: Ready check |
| **Review** | Deliverable submitted for validation | Gate: Quality review |
| **Done** | Definition of Done met (see below) | Gate: Sign-off |
| **Blocked** | Unresolved dependency or risk issue | Escalation required |
| **Cancelled** | Decision to not implement | Documented rationale |

### Definition of Ready (may start)

- [ ] Dependencies (projects) are all at Done or In Progress
- [ ] Purpose and key deliverable are defined
- [ ] Complexity estimate exists and resources are available
- [ ] Risk assessment completed (see risk register)
- [ ] Owner assigned

### Definition of Done (may close)

- [ ] Deliverable meets the purpose defined in project spec
- [ ] All success criteria for the milestone are met
- [ ] Documentation updated (see documentation workflow)
- [ ] No regressions introduced (backwards compatibility verified)
- [ ] Owner signs off

### Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| NeoLife SE changes pricing without notice | Medium | High | Product data includes `last_verified` field; quarterly audit cycle |
| Calculator logic errors produce wrong savings | Low | Critical | All calculator output must have known-value test cases before release |
| Content pipeline produces off-brand tone | Medium | Medium | Every AI-generated draft must pass human editorial review before staging |
| Data schema change breaks existing pages | Low | High | Versioned schema with backwards-compatible migrations |
| Key person dependency (single owner) | Medium | Medium | Each project must have a documented owner and a backup |
| Third-party dependencies (YouTube, analytics) change APIs | Low | Medium | APIs abstracted behind internal wrapper functions |

### Change Management

- This roadmap is the implementation authority. Changes to project scope, priority, or ordering require a documented amendment.
- Amendments are tracked in git alongside the roadmap.
- Any project that exceeds its estimated complexity by >50 % triggers a re-plan gate.
- Blocked projects are reviewed weekly. If blocked >2 weeks, a decision to unblock or cancel is required.
- Success criteria may only be modified by documented addendum (not by removing items).

---

## Architecture Decisions

### Single Source of Truth (SSOT)

| Domain | SSOT Location | Owner | Update Trigger |
|--------|--------------|-------|----------------|
| Product definitions | `src/data/products.yaml` | Editorial | Price change, product change, new product |
| Content metadata (tags, entities) | Frontmatter in `.md`/`.mdx` files | Editorial | Content publish or update |
| Schema definitions | `src/schemas/` (TypeScript types) | Technical | Data structure change |
| Site configuration | `src/config/` (Astro config + custom) | Technical | Site-wide change |

**Rule:** Every page derives product data from the SSOT. No hardcoded prices, no copy-paste from one page to another. If a page needs product data, it imports it.

### Technical Architecture Principles

1. **Data before UI.** Build the data layer (Projects 2-3) before any calculator or comparison tool. The UI is a consumer of data, never the source.
2. **Backwards compatibility.** The `getProduct()`, `getSavings()`, `getPricePerUse()` API signatures must remain stable once released. New parameters use optional arguments. Never remove a public function without a deprecation phase.
3. **Schema as contract.** The product data schema is a contract between content and presentation. Changes require both parties to approve.
4. **Component composability.** Calculators, tables, and comparison views are Astro/JS components that receive data as props, never fetch it themselves. This allows them to be embedded anywhere.
5. **Extensibility by addition.** New product lines, categories, or attributes are added to the schema — never require a schema migration that breaks existing data.

### Content Architecture

**Pillar strategy:**
- Each pillar page owns a topic cluster (e.g., Omega-3 → articles about inflammation, heart health, brain function).
- The Affärsmöjlighet page is a decision-support pillar, not a content cluster hub.
- All content links toward or from a pillar; no orphan content.

**Entity strategy:**
LevNytt tracks three entity types in content frontmatter:
| Entity Type | Examples | Purpose |
|-------------|----------|---------|
| Products | Omega-3 Plus, Carotenoid Complex | Link to product pages, price lookups |
| Health conditions | Inflammation, joint health, sleep | Topic clustering, search intent |
| Ingredients | EPA, DHA, lutein, zeaxanthin | Entity SEO, scientific authority |

Every page must tag at least one entity from each applicable type. The Internal Recommendation Engine (Project 9) uses entity tags for cross-linking.

**Content lifecycle:**

```
Create (draft) → Review (editor) → Stage (preview) → Publish (live) → Monitor (analytics)
                                                                              │
                                                         Update (if declining) ←┘
                                                         Archive (if obsolete) ←─ Archive (404 or redirect)
```

**Scientific review workflow:**
- Any page making health or nutritional claims must cite at least one primary source (PubMed, EFSA, WHO, or NeoLife research).
- Claims are flagged in content frontmatter as `needs-review: true` until verified.
- A quarterly scientific audit reviews all flagged claims against current research.
- If a claim is no longer supportable, the page is either updated or withdrawn.

**Price update workflow:**
- Product prices are verified quarterly against NeoLife SE official pricing.
- The `last_verified` field in the product entity records the date.
- If price discrepancy > 5 %, the page enters draft mode with a price alert flag.
- Discontinued products remain in the database with `status: discontinued` and a deprecation notice.

### AI Architecture

**Automation boundaries (what AI may never do unsupervised):**
- ❌ Publish content without human approval
- ❌ Make health claims without cited sources
- ❌ Generate income figures or earnings claims
- ❌ Modify existing published content
- ❌ Set or change internal link targets

**Human review checkpoints (mandatory before staging):**

| Stage | Check | By |
|-------|-------|----|
| Draft → Review | Factual accuracy, brand tone, claim sources | Editor |
| Review → Stage | Schema correctness, link validity, readability | Editor |
| Stage → Publish | Final read, preview check, frontmatter validation | Owner |

**Prompt governance:**
- All AI generation prompts are version-controlled in `docs/prompts/`.
- Each prompt has: purpose, model, temperature, max tokens, input spec, output spec.
- Prompt changes are reviewed and committed like code changes.
- A prompt library is maintained for each content type (article, FAQ, comparison).

**Fact verification protocol:**
- Source tiering: Tier 1 (PubMed, EFSA, WHO studies) > Tier 2 (NeoLife internal research) > Tier 3 (industry publications)
- Any claim sourced from Tier 3 must be flagged for editorial review.
- AI-drafted claims without an explicit source citation are rejected by the pipeline.

### SEO Architecture

**Topical authority model:**
```
NeoLife (brand authority)
  ├── Products (entity hub)
  │    ├── Omega-3 (pillar + cluster)
  │    ├── Carotenoids (pillar + cluster)
  │    └── ...
  ├── Health conditions (content clusters)
  │    ├── Heart health
  │    ├── Joint health
  │    └── ...
  ├── Affärsmöjlighet (decision support)
  └── Vetenskap (scientific authority)
```

**Content clusters:** Each pillar page is the hub. Informational articles are spokes that link to the hub and to each other where relevant. The Affärsmöjlighet page is a standalone hub with connections to product pillars and informational articles.

**Structured data evolution:**
- Phase 2 baseline: Article + FAQPage schema on all applicable pages.
- Phase 2 expansion: Product schema on product comparison pages, HowTo schema on registration steps.
- Phase 3: Review schema, BreadcrumbList, SiteNavigationElement, WebSite schema with SearchAction.
- All schema is generated programmatically (Project 11 — AI Content Pipeline), never hand-written.

**Search intent mapping:**

| Page Type | Primary Intent | Secondary Intent |
|-----------|---------------|------------------|
| Informational article | Informational | Commercial investigation |
| Product page | Commercial investigation | Transactional |
| Affärsmöjlighet | Commercial investigation | Informational |
| FAQ section | Informational | Navigational |
| Comparison table | Commercial investigation | Transactional |

---

## Operations

### Sprint Workflow

- 2-week sprints. Each sprint begins with a planning session where project tasks are selected from the pipeline.
- Each project in In Progress has at most one active sprint.
- Sprint review at end of week 2: demo, retro, next sprint planning.
- Blocked items are escalated within 24 hours, not carried across sprints.

### Documentation Workflow

- Every project produces documentation before moving from In Progress to Done.
- Documentation lives alongside code (docstrings for utilities, markdown in `docs/` for workflows).
- Each project's documentation checklist:
  - [ ] README or inline docs for any new component or utility
  - [ ] Schema changes documented in `docs/schemas/`
  - [ ] Prompt templates committed in `docs/prompts/` (Project 11)
  - [ ] Workflow documented if it changes editorial process

### Release Workflow

```
Feature branch → PR → Review → Staging → QA check → Merge to main → Deploy
```

- Commits to `main` trigger automatic staging deployment.
- Production deployment is manual, triggered after QA sign-off.
- No deployment on Fridays or before holidays.
- Each release includes a changelog entry in `docs/changelog/`.

### Rollback Strategy

- If a deployment causes errors, the immediate action is to revert the commit and redeploy.
- Rolled-back features are documented in a rollback log with root cause and resolution.
- Data changes (product prices, content updates) are always done via PR, never direct edit on production.
- The product data file is versioned in git — any price change can be reverted with `git revert`.

### Maintenance Workflow

Beyond project work, these recurring tasks are owned:
| Task | Cadence | Owner |
|------|---------|-------|
| Price verification | Quarterly | Editorial |
| Scientific claim audit | Quarterly | Editorial |
| Broken link check | Monthly | Technical |
| Analytics report | Monthly | Editorial |
| Lighthouse audit | Per release | Technical |
| Product data cleanup | Quarterly | Editorial |
| Schema.org validation | Per release | Technical |

---

## Future-Proofing

The Phase 2 architecture is designed so that the following future additions require minimal restructuring:

| Future Addition | Architectural Decision That Enables It |
|----------------|----------------------------------------|
| **More product lines** | Schema is additive. New categories, attributes, or product lines are added as new fields, not migrations. |
| **Multilingual content** | Content files use locale-based directories (`sv/`, `en/`). Product data supports `name_sv`, `name_en` fields. |
| **API access** | The `getProduct()` / `getSavings()` functions are already pure data queries. Wrapping them in an API endpoint (Astro API route or serverless function) requires no data restructuring. |
| **AI agents consuming site data** | Structured data (JSON-LD) is generated for every page. An agent can parse schema without scraping HTML. Entity frontmatter provides machine-readable content relationships. |
| **Dynamic/real-time calculators** | The component model (data passed as props) means calculators can be swapped from static → dynamic by changing only the data source, not the component. |
| **Recommendation engine expansion** | Entity tags in frontmatter are the foundation. A future ML-based engine replaces tag matching with vector similarity without changing the content. |
| **Personalization** | Analytics data (Project 12) feeds personalization rules. Segment-based content display can be added without touching the content layer. |
| **Memberships / gated content** | Content is already split by type (informational, comparison, decision-support). Member-only content can use the same frontmatter with an `access: member` field. |
| **Community features** | The Affärsmöjlighet page already facilitates decisions. A community layer (forums, shared savings) connects to the same entity system. |
| **Future automation** | The AI pipeline (Project 11) has explicit automation boundaries and prompt versioning. New automation stages extend the pipeline without redefining it. |

**Golden rule for future-proofing:** Every Phase 2 deliverable must be built as if it will eventually be consumed by an API, an AI agent, or a non-Swedish speaker — even if none of those exist today.

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

## Architecture Review Summary

### What was improved

The roadmap was missing governance, operational, and architectural scaffolding across 9 dimensions:

| Dimension | Gaps Found | Additions Made |
|-----------|-----------|----------------|
| **Project governance** | No Definition of Ready/Done, no risk register, no change management | Project lifecycle states with gates, DoR/DoD checklists, 5-item risk register, documented change management rules |
| **Technical architecture** | No SSOT ownership, no backwards compatibility rules, no schema contract | SSOT table with owners and update triggers, 5 technical principles (data before UI, backwards compatibility, schema as contract, component composability, extensibility by addition) |
| **Content architecture** | No pillar strategy, no entity strategy, no content lifecycle, no scientific review | Pillar + entity + content lifecycle + scientific review workflow + price update workflow |
| **AI architecture** | No automation boundaries, no prompt governance, no fact verification protocol | 5 prohibited AI actions, 3 human review checkpoints, prompt version-control rules, 3-tier source verification |
| **SEO architecture** | No topical authority model, no search intent mapping, no structured data evolution path | Topical authority tree, content cluster model, 3-phase schema evolution plan, search intent table by page type |
| **Product architecture** | No price update workflow, no product lifecycle, no regulatory update process | Price verification cadence, discontinued product handling, `last_verified` field |
| **Analytics architecture** | No baseline definition, no continuous improvement loop | Baselines established in M11, analytics feeds content update decisions via the content lifecycle |
| **Operational architecture** | Entirely missing (sprints, releases, rollback, maintenance) | 2-week sprint cadence, documentation checklist, release workflow with freeze rules, rollback revert strategy, 7 recurring maintenance tasks with owners and cadence |
| **Future-proofing** | No explicit extensibility patterns | 10 future additions mapped to the architectural decisions that enable them, plus a golden rule for all Phase 2 deliverables |

### Why it improves the roadmap

Before these additions, the roadmap described *what* to build and *when* — but not *how* to build it reliably, *who* decides, *what* to do when things go wrong, or *how* to ensure the foundation supports future growth. The architecture decisions turn a project schedule into an implementation authority that can survive owner changes, pricing shifts, and technology evolution.

### Is the roadmap now considered Phase 2 implementation authority?

**Yes.** The roadmap is architecturally complete and suitable as the permanent implementation authority for Phase 2. It covers all 9 architectural dimensions reviewed. No further structural additions are required before implementation begins.

### Remaining architectural concerns

None at the roadmap level. The following implementation-level concerns are acknowledged but do not block Phase 2 authority:

1. **Astro-specific data integration** — The exact mechanism for importing `products.yaml` into Astro content collections needs to be resolved during Project 2 (Product Entity System). This is an implementation detail, not a roadmap gap.
2. **Prompt model selection** — Which LLM backend powers the AI Content Pipeline is left undecided intentionally. The architecture supports any model; the decision is deferred to Project 11 implementation.
3. **Exact analytics dashboard tool** — Whether the dashboard is a markdown report, a HTML page, or a third-party tool (Looker Studio, etc.) is deferred to Project 12. The metrics and cadence are fixed; the implementation is flexible.
4. **Multi-language timing** — i18n is enabled architecturally but not scheduled. The decision to add a language is a business decision, not a technical constraint.

These are deferred decisions, not gaps. The roadmap provides enough constraint to start Phase 2 while preserving flexibility where it matters.

---

*This roadmap is the permanent implementation authority for Phase 2. No HTML pages have been modified in its creation.*
