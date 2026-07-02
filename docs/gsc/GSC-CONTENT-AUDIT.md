# GSC Content Audit — Crawled Not Indexed

**Date:** 2026-07-02
**Source:** Google Search Console — "Crawled – currently not indexed"
**Scope:** 11 URLs
**Method:** Manual audit per URL — 9 criteria + repository validation + production review
**Constraint:** Audit only — no HTML modifications, no redirects, no sitemap changes

---

## URL Inventory

| # | GSC URL | Source File | Root `.html`? | Sitemap? | Canonical |
|---|---------|------------|:---:|:---:|---|
| 1 | `https://levnytt.se/levnytt-principer` | `content/articles/levnytt-principer.html` | ❌ | ❌ | `https://levnytt.se/levnytt-principer` |
| 2 | `https://levnytt.se/content/articles/naringsbrist.html` | `content/articles/naringsbrist.html` | ❌ | ❌ | `https://levnytt.se/naringsbrist` |
| 3 | `https://levnytt.se/content/articles/varfor-ar-jag-trott-hela-tiden.html` | `content/articles/varfor-ar-jag-trott-hela-tiden.html` | ❌ | ❌ | `https://levnytt.se/varfor-ar-jag-trott-hela-tiden` |
| 4 | `https://levnytt.se/den-fundersamma-mannen` | `den-fundersamma-mannen.html` | ✅ | ✅ | `https://levnytt.se/den-fundersamma-mannen` |
| 5 | `https://levnytt.se/content/articles/naringsbrist-symptom.html` | `content/articles/naringsbrist-symptom.html` | ❌ | ❌ | `https://levnytt.se/naringsbrist-symptom/` |
| 6 | `https://levnytt.se/neolife-pro-vitality` | `neolife-pro-vitality.html` | ✅ | ✅ | `https://levnytt.se/neolife-pro-vitality` |
| 7 | `https://levnytt.se/neolife-tre-en-en` | `neolife-tre-en-en.html` | ✅ | ✅ | `https://levnytt.se/neolife-tre-en-en` |
| 8 | `https://levnytt.se/karotenoid-tillskott-vs-mat` | `karotenoid-tillskott-vs-mat.html` | ✅ | ✅ | `https://levnytt.se/karotenoid-tillskott-vs-mat` |
| 9 | `https://levnytt.se/golden-home-care` | `golden-home-care.html` | ✅ | ✅ | `https://levnytt.se/golden-home-care/` |
| 10 | `https://levnytt.se/ala-vs-epa-vs-dha` | `ala-vs-epa-vs-dha.html` | ✅ | ✅ | `https://levnytt.se/ala-vs-epa-vs-dha` |
| 11 | `https://levnytt.se/ekologisk-stadning-greenwashing` | `ekologisk-stadning-greenwashing.html` | ✅ | ✅ | `https://levnytt.se/ekologisk-stadning-greenwashing` |

**Key finding:** 4 of 11 URLs have NO root `.html` file (only `content/articles/` copies). These 4 are also absent from the sitemap. They are the highest-quality informational pages in the audit.

---

## Per-URL Analysis

---

### 1. `https://levnytt.se/levnytt-principer`

**Article Type:** Authority Page — editorial principles & methodology
**Search Intent:** Unclear primary keyword. Navigational/informational hybrid — serves as trust signal, not search target.
**SEO Structure:**
- Title: `LevNytt Principer – De fem redaktionella principerna | LevNytt` — brand-forward, low search volume
- Meta description: Present, well-written, ~155 chars
- H1: Single H1 matching title. H2s per principle. Sound structure
- URL: `/levnytt-principer` — matches H1
**Content Quality:** 824 lines. Comprehensive explanation of 5 principles with concrete examples, tables, FAQ accordion, journey block. Good editorial quality but internal-facing content, not search-optimised
**Internal Linking:** ~46 incoming links from 25+ files (authority-nav + tier-box pattern across product pages). Strong integration
**Duplicate Risk:** Low — unique content, no other page covers editorial principles
**E-E-A-T Review:** Author: Jarmo Halonen. Date: 2026-06-09. Schema: `WebPage` + `FAQPage` (NOT `Article`). No scientific references needed (non-YMYL). Trust elements: disclosure, about link, editorial signal
**Technical Review:** Canonical ✅. No `noindex`. Schema: `WebPage` (not `Article`). Sitemap: ❌ NOT included. Robots: clean
**Production Review:** Predates PAS V1.0. Uses custom pillar.css inline styles. Appears to be pre-pipeline hand-built page. Not compliant with current production standards
**Repository Validation:** Source at `content/articles/levnytt-principer.html`. No root `levnytt-principer.html`. Canonical URL `https://levnytt.se/levnytt-principer` has no physical file. Sitemap excluded

| Problem | Reason | Recommended Action | Expected SEO Impact |
|---------|--------|--------------------|--------------------|
| No root `.html` file | Source file lives in `content/articles/` — only the physical crawl path | Create root `levnytt-principer.html` with same content | HIGH — may be primary non-indexing cause |
| No `Article` schema | Uses `WebPage` schema — weaker E-E-A-T signal | Add `Article` schema type | LOW |
| Not in sitemap | Missing from sitemap.xml entirely | Add to sitemap | MEDIUM |

**Classification:** IMPROVE

---

### 2. `https://levnytt.se/content/articles/naringsbrist.html`

**Article Type:** Informational (explainer)
**Search Intent:** Clear definition intent — `naringsbrist`. Keyword matches exactly. Strong intent clarity
**SEO Structure:**
- Title: `Näringsbrist – vad det är, varför det uppstår och vad du kan göra` — ~70 chars, keyword-first, excellent
- Meta description: Present, ~155 chars, includes call to action
- H1: Single "Näringsbrist". Clean H2 structure. Well-organized
- URL: Crawled at `content/articles/naringsbrist.html` — physical file path
**Content Quality:** 627 lines. Punchline, key takeaways, cause cards, risk grid, SVG diagram, comparison table, CTA block, FAQ accordion. Estimated ~3500 words. Comprehensive for the topic
**Internal Linking:** ~27 incoming links from ~19 unique source files. Strong linking from supplement cluster articles
**Duplicate Risk:** HIGH with `/naringsbrist-symptom` (both cover causes, types, symptoms of nutritional deficiency)
**E-E-A-T Review:** Author: Jarmo Halonen. Date: 2026-06-08. Schema: `Article` + `FAQPage`. References to PubMed, Livsmedelsverket, 1177. Evidence labels present. Author bio box. Methodology note. Strong E-E-A-T
**Technical Review:** Canonical ✅ points to `https://levnytt.se/naringsbrist`. No `noindex`. Schema: `Article`. Sitemap: ❌ NOT included. Robots: clean
**Production Review:** Follows PAS V1.0 conventions (hero, punchline, takeaways, method note, author box, CTA, FAQ, tier boxes). Post-pipeline quality. No root `.html` file

| Problem | Reason | Recommended Action | Expected SEO Impact |
|---------|--------|--------------------|--------------------|
| Crawled at `content/articles/` path | Google found source file at physical path — canonical points to `/naringsbrist` but no root file exists there | Publish root `/naringsbrist.html` file | HIGH — most likely primary cause |
| Not in sitemap | Missing from sitemap even though content is high-quality | Add to sitemap | MEDIUM |
| Duplicate topic with #5 | Both cover nutritional deficiency — Google may pick one | Differentiate: make #2 broad overview, #5 symptom-to-nutrient diagnostic table | MEDIUM |

**Classification:** IMPROVE

---

### 3. `https://levnytt.se/content/articles/varfor-ar-jag-trott-hela-tiden.html`

**Article Type:** Informational (listicle/explainer hybrid)
**Search Intent:** VERY clear — `varför är jag trött hela tiden` is a common Swedish query. Strongest intent match in audit
**SEO Structure:**
- Title: `Varför är jag trött hela tiden? 8 vanliga orsaker förklarade` — ~60 chars, question-form, number, keyword-first. Excellent
- Meta description: Present, ~155 chars, well-written
- H1: Single "Varför är jag trött hela tiden?". H2s per cause. Clear structure
- URL: Crawled at `content/articles/varfor-ar-jag-trott-hela-tiden.html` — physical file path
**Content Quality:** 723 lines. Punchline, takeaways, card grid (6 causes), nutrient table, lifestyle table, SVG diagram, CTA block, FAQ accordion, author box, methodology note. Estimated ~4000 words. Highest content depth in audit
**Internal Linking:** ~12 incoming links from ~10 files. Moderate. Could benefit from more from fatigue/nutrition cluster
**Duplicate Risk:** Low-Moderate — overlaps slightly with naringsbrist (fatigue as symptom) but angle is all causes of fatigue, not just nutrition
**E-E-A-T Review:** Author: Jarmo Halonen. Date: 2026-06-08. Schema: `Article` + `FAQPage`. References to BMC Public Health, Livsmedelsverket, Internetmedicin.se, PubMed. Evidence notes present. Author bio + methodology note. Strong E-E-A-T
**Technical Review:** Canonical ✅ points to `/varfor-ar-jag-trott-hela-tiden`. No `noindex`. Schema: `Article`. Sitemap: ❌ NOT included. Robots: clean
**Production Review:** Follows PAS V1.0 conventions. Post-pipeline quality. No root `.html` file

| Problem | Reason | Recommended Action | Expected SEO Impact |
|---------|--------|--------------------|--------------------|
| Crawled at `content/articles/` path | Google found source file at physical path — no root file for canonical URL | Publish root `/varfor-ar-jag-trott-hela-tiden.html` file | HIGH — strongest index candidate |
| Not in sitemap | Missing from sitemap | Add to sitemap | MEDIUM |
| Only 12 incoming links | Lower than similar content pages | Add contextual links from fatigue/nutrition/sleep articles | LOW |

**Classification:** KEEP

---

### 4. `https://levnytt.se/den-fundersamma-mannen`

**Article Type:** About Page / personal narrative / author profile
**Search Intent:** Weak — no clear primary keyword. Brand navigational intent. Low standalone search value
**SEO Structure:**
- Title: `Den fundersamma mannen – LevNytt` — ~45 chars, brand-focused, not search-optimised
- Meta description: Present, narrative tone. Could target specific phrases
- H1: Single H1. H2s by life-story sections
- URL: `/den-fundersamma-mannen` — matches title
**Content Quality:** 295 lines. Personal narrative — Finland childhood, trucking years, network marketing experience, sobriety since 2020, NeoLife origin story. Well-written but not search-targeted content. Low informational value for someone without brand awareness
**Internal Linking:** ~141 incoming links from ~99 unique files. HIGHEST on site — used as author link from virtually every article
**Duplicate Risk:** Low — unique personal narrative. No equivalent page
**E-E-A-T Review:** Author: Jarmo Halonen (self-referential). Date: 2026-06-07. Schema: `Article` + `FAQPage`. No scientific references (non-YMYL). Trust elements OK. About-page appropriateness: moderate
**Technical Review:** Root file ✅. Canonical ✅. No `noindex`. Schema: `Article`. Sitemap ✅ included. Robots: clean
**Production Review:** Pre-PAS V1.0. Uses older pre-pillar layout with serif body font, different visual identity from modern pages. Has nav.js/footer.js integration

| Problem | Reason | Recommended Action | Expected SEO Impact |
|---------|--------|--------------------|--------------------|
| No clear search intent | Personal narrative lacks primary keyword — Google sees low standalone value | Add `AboutPage` schema. Expand with specific biographical content (credentials, professional history) | MEDIUM |
| Low content density for article type | 295 lines of narrative prose — thin for an about page with 141 internal links | Expand with genuine detail about background, expertise, author credentials | MEDIUM |
| Article schema not ideal | `Article` schema is used — `AboutPage` or `ProfilePage` would be more appropriate | Switch to `AboutPage` schema | LOW |

**Classification:** IMPROVE

---

### 5. `https://levnytt.se/content/articles/naringsbrist-symptom.html`

**Article Type:** Informational (symptom guide)
**Search Intent:** Clear — `naringsbrist symptom`. Keyword matches exactly. Intent clarity: strong
**SEO Structure:**
- Title: `Näringsbrist symptom – vanliga tecken att känna igen` — ~55 chars, keyword-first, good
- Meta description: Present, well-written, includes symptom terms
- H1: Single H1. H2s by symptom category. Good structure
- URL: Crawled at `content/articles/naringsbrist-symptom.html` — physical file path
**Content Quality:** 434 lines. Stat cards (6 with PubMed references), SVG infographic (symptom-to-nutrient mapping), evidence-tier labels (T1-T4), method note, FAQ accordion, author box. Estimated ~2500 words
**Internal Linking:** Only ~6 incoming links. Weakest in informational article group
**Duplicate Risk:** HIGH with `/naringsbrist` (#2). Both cover: what is nutritional deficiency, causes, types, symptoms, solutions. Differentiation is minimal — this page focuses slightly more on symptoms but the overlap is substantial
**E-E-A-T Review:** Author: Jarmo Halonen. Date: 2026-06-09. Schema: `Article` + `FAQPage`. References to PubMed, MDPI Nutrients, PMC, Internetmedicin.se. Evidence-tier labels throughout. Strong E-E-A-T
**Technical Review:** Canonical ✅ points to `https://levnytt.se/naringsbrist-symptom/`. No `noindex`. Schema: `Article`. Sitemap: ❌ NOT included. Robots: clean
**Production Review:** Follows PAS V1.0 conventions. Post-pipeline quality. No root `.html` file

| Problem | Reason | Recommended Action | Expected SEO Impact |
|---------|--------|--------------------|--------------------|
| Crawled at `content/articles/` path | Google found physical file path — no root file for canonical URL | Publish root `/naringsbrist-symptom.html` file | HIGH |
| Not in sitemap | Missing from sitemap | Add to sitemap | MEDIUM |
| Duplicate topic with #2 | Near-identical topic coverage — Google likely picks the more-linked page | Differentiate into symptom-to-nutrient diagnostic table or merge with #2 | MEDIUM |
| Only 6 incoming links | Crawl isolation limits discovery | Add contextual links from supplement/nutrition cluster pages | MEDIUM |

**Classification:** KEEP — after differentiation from #2

---

### 6. `https://levnytt.se/neolife-pro-vitality`

**Article Type:** Product Pillar Page (hub for Pro Vitality+ category)
**Search Intent:** Mixed — title targets `dagligt näringssystem` (educational) but URL is product slug. Primary keyword unclear — mismatch between educational framing and product URL
**SEO Structure:**
- Title: `Vad är ett dagligt näringssystem — och vad bör det innehålla?` — ~70 chars. Educational framing. Keyword `neolife pro vitality` NOT in title
- Meta description: Present, educational tone
- H1: Single H1 matching title. H2s cover nutrition system components
- URL: `/neolife-pro-vitality` — product slug, doesn't match title
**Content Quality:** 319 lines. Component grids, stat row, evidence table, FAQ accordion, journey block. Educational approach with product framing. Less specific product detail than expected for a product pillar page
**Internal Linking:** ~43 incoming links. Strong. Links from supplement cluster pages
**Duplicate Risk:** Low within LevNytt — only Pro Vitality+ page. Educational framing differentiates from pure product pages
**E-E-A-T Review:** Author: Jarmo Halonen. Date: 2026-06-15. Schema: `Article` + `FAQPage` + `BreadcrumbList`. References: EFSA, Am J Clin Nutr, Livsmedelsverket. Method note with commercial disclosure. Good for product page
**Technical Review:** Root file ✅. Canonical ✅. No `noindex`. Schema: `Article`. Sitemap ✅ included. Robots: clean
**Production Review:** Modern pillar template. Post-pipeline. Has nav.js/footer.js

| Problem | Reason | Recommended Action | Expected SEO Impact |
|---------|--------|--------------------|--------------------|
| Title-URL mismatch | Title targets "dagligt näringssystem" but URL is product slug — Google sees conflicting signals | Include "NeoLife Pro Vitality" in title. Or split: educational page at `/dagligt-naringssystem` + redirect product URL | MEDIUM |
| Crosses informational/commercial line | Neither fully educational nor fully commercial — may not satisfy either intent well | Add `Product` schema or `ItemPage`. Consider dedicated pure-product page | LOW |

**Classification:** IMPROVE

---

### 7. `https://levnytt.se/neolife-tre-en-en`

**Article Type:** Product Article (historical/educational + product)
**Search Intent:** Niche — title targets historical claim (`världens första fytonäringstillskott sedan 1958`). Low search volume phrasing. Primary keyword unclear
**SEO Structure:**
- Title: `NeoLife Tre-en-en: Världens första fytonäringstillskott sedan 1958 | Levnytt.se` — ~85 chars (too long). Keyword `neolife tre en en` is present but buried
- Meta description: Present, detailed, includes Texas A&M reference
- H1: Matches title. Very long
- URL: `/neolife-tre-en-en` — matches product slug
**Content Quality:** 560 lines. Extensive historical background, Texas A&M research, cell membrane science, ingredient grid, product tables, CTA, FAQ, inline SVG infographic. Detailed for a product page
**Internal Linking:** Only ~7 incoming links. Relatively isolated
**Duplicate Risk:** HIGH with `/neolife-tre-en-en-cellnaring` — both cover same product from slightly different angles. Google may see them as duplicates
**E-E-A-T Review:** Author: Jarmo Halonen. Date: 2026-05-12. Schema: `Article` + `FAQPage` + `BreadcrumbList`. References to Texas A&M (1987), Livsmedelsverket. Method note present. Evidence: limited clinical human data (dairy study)
**Technical Review:** Root file ✅. Canonical ✅. No `noindex`. Has `robots` meta with `index, follow`. Schema: `Article`. Sitemap ✅ included. Robots: clean
**Production Review:** Pre-PAS V1.0 — different template (sticky nav, custom hero, footer). Standalone design not matching current pillar conventions

| Problem | Reason | Recommended Action | Expected SEO Impact |
|---------|--------|--------------------|--------------------|
| Title >70 chars | 85 chars — Google truncates in SERP | Shorten to 55-60 chars, keyword first: `NeoLife Tre-en-en — vad är det och hur fungerar det?` | MEDIUM |
| Duplicate with cellnaring variant | Two pages for same product splits link equity | Set clear canonical between `/neolife-tre-en-en` and `/neolife-tre-en-en-cellnaring`. Or merge | MEDIUM |
| Only 7 incoming links | Product page is isolated from main content clusters | Add contextual links from supplement, cellular health, Pro Vitality cluster | MEDIUM |
| Niche keyword with low search volume | "Fytonäringstillskott" and historical framing have minimal search volume | Retarget to searchable queries like "vad är tre en en" or "neolife tre en en fördelar" | LOW |

**Classification:** IMPROVE

---

### 8. `https://levnytt.se/karotenoid-tillskott-vs-mat`

**Article Type:** Informational (comparison / FAQ)
**Search Intent:** Moderate — `karotenoider från mat eller tillskott` is a legitimate comparison query but niche
**SEO Structure:**
- Title: `Karotenoider från mat eller tillskott — spelar källan roll?` — ~65 chars, question format, good
- Meta description: Present, includes CARET study mention, strong hook
- H1: Single H1 matching title
- URL: `/karotenoid-tillskott-vs-mat` — matches topic
**Content Quality:** 101 lines total — very thin. Essentially an FAQ with short intro. No punchline block (title serves as punchline via schema). No takeaways, no stat cards, no methodology note visible in scanned portion. Minimal preamble before FAQ
**Internal Linking:** ~9 incoming links. Links from carotenoid cluster. Moderate
**Duplicate Risk:** Moderate — overlaps with `/neolife-carotenoid-complex` and `/vad-ar-lutein`. The comparison angle is unique but thinly executed
**E-E-A-T Review:** Author: Jarmo Halonen. Date: 2026-06-16. Schema: `Article` + `FAQPage` + `BreadcrumbList`. References to CARET (NEJM), ATBC, Am J Clin Nutr. Commercial disclosure present. Few evidence-tier labels visible
**Technical Review:** Root file ✅. Canonical ✅. No `noindex`. Schema: `Article`. Sitemap ✅ included. Robots: clean
**Production Review:** Minimal template — seems to be a quick-format FAQ page, not full PAS V1.0

| Problem | Reason | Recommended Action | Expected SEO Impact |
|---------|--------|--------------------|--------------------|
| Very thin content (101 lines) | Google likely sees insufficient unique value for indexing. Topic deserves 400+ lines with CARET/ATBC analysis, bioavailability comparison, dietary guidance | Expand to 400+ lines with sections: CARET deep-dive, mechanism, dietary sources table, practical guidance. Or merge as section into broader carotenoid article | HIGH |
| FAQ-only format without preamble | No punchline, no takeaways, no author elaboration — reads as thin FAQ | Restructure as full article with the FAQ as an accordion section, not the primary content | MEDIUM |

**Classification:** MERGE — topic value should be folded into `/neolife-carotenoid-complex` or `/vad-ar-lutein` as a dedicated section

---

### 9. `https://levnytt.se/golden-home-care`

**Article Type:** Product / Commercial Page
**Search Intent:** Commercial — `golden home care pris`, `LDC diskmedel`, `NeoLife rengöring`. Title targets cost-per-liter comparison — specific but niche
**SEO Structure:**
- Title: `Golden Home Care — LDC diskmedel: vad kostar det egentligen per liter? | LevNytt.se` — ~88 chars (too long)
- Meta description: Present, includes cost comparison data
- H1: `LDC: vad kostar diskmedlet egentligen per liter?` — doesn't match URL slug (golden-home-care)
- URL: `/golden-home-care/` — brand/product slug
**Content Quality:** 395 lines. Cost comparison tables, dilution ratios, eco-credentials, usage guide, FAQ. Moderate depth. Well-structured for a product page
**Internal Linking:** ~13 incoming links. Links from cleaning/sustainability articles
**Duplicate Risk:** Low on LevNytt. Competes externally with NeoLife's own product pages
**E-E-A-T Review:** Author: Organization (LevNytt.se). Date: 2026-05-16. Schema: `Article` + `FAQPage` + `BreadcrumbList`. Fewer references than health articles (non-YMYL). Product-specific content
**Technical Review:** Root file ✅. Canonical ✅ (trailing slash). Has `robots` meta with `index, follow`. Schema: `Article`. Sitemap ✅ included. Robots: clean
**Production Review:** Older template — pre-PAS V1.0. Uses custom hero, table stats, internal-links-section. Has nav.js/footer.js

| Problem | Reason | Recommended Action | Expected SEO Impact |
|---------|--------|--------------------|--------------------|
| Title >70 chars | 88 chars — Google truncates in SERP | Shorten to 55-60 chars: `Golden Home Care LDC — pris per liter jämfört med butik` | MEDIUM |
| H1 doesn't match URL | H1 is about LDC cost per liter, URL is "golden-home-care" | Align: either change URL to `/ldc-diskmedel-pris` or make H1 match brand | MEDIUM |
| Commercial page on informational site | Google may deprioritize commercial pages on primarily informational publisher | Consider merging into broader "miljövänlig städning" pillar page | LOW |

**Classification:** MERGE — content should be part of a cleaning/sustainability hub, not standalone product page

---

### 10. `https://levnytt.se/ala-vs-epa-vs-dha`

**Article Type:** Informational (FAQ / comparison)
**Search Intent:** Clear comparison intent — `ALA vs EPA vs DHA`. Keyword matches exactly. However, low Swedish search volume
**SEO Structure:**
- Title: `ALA vs EPA vs DHA — varför kan inte växtomega-3 ersätta fisk?` — ~65 chars, excellent keyword match
- Meta description: Present, includes conversion rate statistic (0-8%)
- H1: Single H1 matching title
- URL: `/ala-vs-epa-vs-dha` — matches topic
**Content Quality:** 115 lines total. FAQ format with short intro. No punchline (title serves as punchline via schema). Minimal preamble. Stat table is brief. Thin for a topic that deserves full article treatment
**Internal Linking:** ~15 incoming links. Links from omega-3 cluster
**Duplicate Risk:** HIGH — overlaps extensively with `/omega-3-komplett-evidensbaserad-guide`, `/omega-3-fran-mat-racker-kosten`, `/varfor-fiskolja-inte-ar-likvardigt`. The conversion-rate data exists across multiple articles
**E-E-A-T Review:** Author: Jarmo Halonen. Date: 2026-06-15. Schema: `Article` + `FAQPage` + `BreadcrumbList`. References: Am J Clin Nutr, Simopoulos, PubMed. Commercial disclosure present. Minimal evidence-tier labeling
**Technical Review:** Root file ✅. Canonical ✅. No `noindex`. Schema: `Article`. Sitemap ✅ included. Robots: clean
**Production Review:** Minimal template — quick-format FAQ page, not full PAS V1.0

| Problem | Reason | Recommended Action | Expected SEO Impact |
|---------|--------|--------------------|--------------------|
| Very thin content (115 lines) | Topic deserves 400+ lines with conversion mechanism, enzyme biochemistry, dietary implications, vegan alternatives section | Remove standalone page. Add conversion-rate data as section in `/omega-3-komplett-evidensbaserad-guide`. 301 redirect | HIGH — eliminates duplicate signals |
| High duplicate risk | Conversion rate data already exists in multiple indexed omega-3 articles | See above | HIGH |

**Classification:** REMOVE

---

### 11. `https://levnytt.se/ekologisk-stadning-greenwashing`

**Article Type:** Informational (FAQ / explainer)
**Search Intent:** Clear — `greenwashing i städprodukter`, `ekologisk städning`. Reasonable keyword match
**SEO Structure:**
- Title: `Greenwashing i städprodukter — hur känner du igen det?` — ~55 chars, question format, good
- Meta description: Present, includes EU legislation and tensidkemi
- H1: Single H1 matching title
- URL: `/ekologisk-stadning-greenwashing` — matches topic
**Content Quality:** 123 lines total. FAQ format with minimal preamble. No punchline (title serves as punchline). Takeaways present but short. Minimal elaboration. Very thin for a topic covering EU legislation, chemistry, and consumer guidance
**Internal Linking:** Only ~3 incoming links — LOWEST in audit. Crawl isolation is severe
**Duplicate Risk:** LOW — topic is unique on LevNytt. But content is too thin to compete with established greenwashing resources
**E-E-A-T Review:** Author: Jarmo Halonen. Date: 2026-06-16. Schema: `Article` + `FAQPage` + `BreadcrumbList`. References: EU Green Claims Directive, EU tensidförordning, IJERPH. Commercial disclosure present. Thin execution undermines credibility
**Technical Review:** Root file ✅. Canonical ✅. No `noindex`. Schema: `Article`. Sitemap ✅ included. Robots: clean
**Production Review:** Minimal template — quick-format FAQ page, not full PAS V1.0

| Problem | Reason | Recommended Action | Expected SEO Impact |
|---------|--------|--------------------|--------------------|
| Very thin content (123 lines) | Insufficient unique value for indexing — Google sees no depth | Remove standalone page. Topic belongs as section in a broader cleaning/sustainability pillar page | MEDIUM |
| Severe crawl isolation (3 links) | Only linked from index and artiklar — no contextual integration | See above — consolidation solves crawl isolation | MEDIUM |

**Classification:** REMOVE

---

## Priority Recommendations

### Priority 1 — Critical (Expected SEO Impact: HIGH)

| # | Action | Affected URLs | Rationale |
|---|--------|---------------|-----------|
| P1.1 | **Publish root `.html` copies for 4 orphaned pages** | #1, #2, #3, #5 | These 4 pages exist only in `content/articles/` with no root file at the canonical URL path. 3 of them were crawled at the `content/articles/` physical path — Google found the raw source file, not a published page. Publishing root copies is the single highest-impact fix |
| P1.2 | **Add the 4 orphaned pages to sitemap** | #1, #2, #3, #5 | Currently excluded from sitemap.xml. Google cannot discover these URLs efficiently through normal crawl |
| P1.3 | **Resolve duplication between #2 and #5** | #2, #5 | Nearly identical topic. Google picks one and skips the other. Differentiate: #2 = broad overview, #5 = symptom-to-nutrient diagnostic table. Or merge and 301 |

### Priority 2 — Moderate (Expected SEO Impact: MEDIUM)

| # | Action | Affected URLs | Rationale |
|---|--------|---------------|-----------|
| P2.1 | **Increase internal links to isolated pages** | #5 (6 links), #7 (7 links), #8 (9 links), #11 (3 links), #10 (15 links) | Pages with <10 incoming links are crawl-disadvantaged |
| P2.2 | **Fix title length >70 chars** | #7 (85 chars), #9 (88 chars) | Google truncates at ~60 chars in SERP. Shorten to 55-60, keyword first |
| P2.3 | **Expand thin FAQ-only pages (100-150 lines) or merge them** | #8 (101 lines), #10 (115 lines), #11 (123 lines) | Pages under ~200 lines struggle to demonstrate sufficient value. These need substantial expansion or should be sections within broader articles |
| P2.4 | **Fix title-URL mismatch** | #6 (title says "dagligt näringssystem", URL is product slug), #9 (H1 says LDC pris, URL is golden-home-care) | Conflicting signals confuse Google about what the page is about |
| P2.5 | **Resolve duplicate with cellnaring variant** | #7 vs `/neolife-tre-en-en-cellnaring` | Two pages for same product splits link equity. Set clear canonical |

### Priority 3 — Lower (Expected SEO Impact: LOW)

| # | Action | Affected URLs | Rationale |
|---|--------|---------------|-----------|
| P3.1 | **Merge #8 into carotenoid cluster** | #8 | The CARET/comparison content is valuable but thin. Add as section in `/neolife-carotenoid-complex` |
| P3.2 | **Merge #9 into sustainability pillar** | #9 | Product cost-per-liter fits within a broader "miljövänlig städning" hub |
| P3.3 | **Remove #10 and #11** | #10, #11 | Thin content, duplicate/overlapping, crawl isolated. Removing consolidates link equity |
| P3.4 | **Improve #4 with AboutPage schema + expansion** | #4 | 141 links make it valuable as trust signal. Expand with genuine biographical content, switch to `AboutPage` schema |

---

## Classification Summary

| # | URL | Classification |
|---|-----|:---:|
| 1 | `/levnytt-principer` | IMPROVE |
| 2 | `content/articles/naringsbrist.html` | IMPROVE |
| 3 | `content/articles/varfor-ar-jag-trott-hela-tiden.html` | **KEEP** |
| 4 | `/den-fundersamma-mannen` | IMPROVE |
| 5 | `content/articles/naringsbrist-symptom.html` | **KEEP** |
| 6 | `/neolife-pro-vitality` | IMPROVE |
| 7 | `/neolife-tre-en-en` | IMPROVE |
| 8 | `/karotenoid-tillskott-vs-mat` | MERGE |
| 9 | `/golden-home-care` | MERGE |
| 10 | `/ala-vs-epa-vs-dha` | REMOVE |
| 11 | `/ekologisk-stadning-greenwashing` | REMOVE |

---

## Final Summary

### Common Problems (Affecting Multiple Pages)

1. **Missing root files (4 pages)** — #1, #2, #3, #5 exist only in `content/articles/` with no published root `.html` file. This is the single strongest signal correlating with non-indexing. These 4 pages also have the HIGHEST content quality in the audit. All are absent from the sitemap.

2. **Thin FAQ-only content (3 pages)** — #8 (101 lines), #10 (115 lines), #11 (123 lines) are essentially FAQ pages with minimal editorial framing. Google sees insufficient unique value.

3. **Low internal linking (5 pages)** — #5 (6 links), #7 (7 links), #8 (9 links), #11 (3 links), #10 (15 links) have <15 incoming links. Crawl discovery is constrained.

4. **Duplicate topic coverage (2 clusters)** — (#2 + #5) overlap on nutritional deficiency. (#10 overlaps with 3 indexed omega-3 articles). Google picks one and skips the rest.

### Patterns Found Across the Audit

- **Root file existence is the strongest non-indexing signal.** 7 pages with root files have sitemap inclusion and technical basics correct, yet many are still not indexed — but their content quality is lower.
- **The highest-quality content suffers from missing infrastructure.** The 4 `content/articles/` pages are the best articles on the site but lack published root files and sitemap entries.
- **Product/commercial pages (4 of 11)** disproportionately appear in GSC "crawled not indexed." Google may be deprioritizing commercial content on this primarily informational site.
- **FAQ-only format is a non-indexing pattern.** Pages consisting almost entirely of FAQ accordion with minimal preamble consistently fail to index, regardless of topic quality.

### Quick Wins

| Win | Action | Est. effort | Pages affected |
|-----|--------|:-----------:|:--------------:|
| **Highest impact** | Publish 4 root `.html` files from `content/articles/` to root | ~15 min | #1, #2, #3, #5 |
| **Immediate** | Add 4 missing URLs to sitemap.xml | ~5 min | #1, #2, #3, #5 |
| **Immediate** | Shorten 2 overlong titles to <60 chars | ~5 min | #7, #9 |
| **Fast** | Increase internal links to isolated pages | ~30 min | #5, #7, #8, #10, #11 |

### Structural Improvements

- **Topic deduplication:** Resolve #2 vs #5 overlap. Either merge or clearly differentiate with distinct article angles and internal links pointing to the preferred page.
- **Content depth threshold:** Consider setting a minimum ~200-line editorial body requirement for standalone pages. Topics that can't support this should be sections within broader articles.
- **Crawl isolation threshold:** Every new page should receive at least 5 contextual internal links at publication time from related cluster pages.

### Long-Term Improvements

- **Audit all `content/articles/` files** — there may be more than these 4 that lack root file copies. Ensure every `content/articles/` file has a corresponding root `.html`.
- **Review all product pages for search intent alignment** — several non-indexed pages (#6, #7, #9) have title-URL or H1-URL mismatches. Standardize naming conventions.
- **Consider pillar page consolidation** — topics like cleaning/greenwashing (#9, #11), omega-3 comparison (#10), and carotenoid comparison (#8) work better as sections within pillar pages than as standalone thin pages.

---

## Machine Readable Output

| URL | Classification | Priority | Expected Impact | Recommended Action |
|-----|:-------------:|:--------:|:---------------:|--------------------|
| `https://levnytt.se/levnytt-principer` | IMPROVE | P1 | HIGH | Publish root `.html`, add to sitemap |
| `https://levnytt.se/content/articles/naringsbrist.html` | IMPROVE | P1 | HIGH | Publish root `.html`, add to sitemap, differentiate from #5 |
| `https://levnytt.se/content/articles/varfor-ar-jag-trott-hela-tiden.html` | KEEP | P1 | HIGH | Publish root `.html`, add to sitemap |
| `https://levnytt.se/den-fundersamma-mannen` | IMPROVE | P3 | LOW | Add `AboutPage` schema, expand content |
| `https://levnytt.se/content/articles/naringsbrist-symptom.html` | KEEP | P1 | HIGH | Publish root `.html`, add to sitemap, differentiate from #2 |
| `https://levnytt.se/neolife-pro-vitality` | IMPROVE | P2 | MEDIUM | Fix title-URL mismatch, add product schema |
| `https://levnytt.se/neolife-tre-en-en` | IMPROVE | P2 | MEDIUM | Shorten title, resolve duplicate with cellnaring variant |
| `https://levnytt.se/karotenoid-tillskott-vs-mat` | MERGE | P3 | LOW | Fold into carotenoid pillar page |
| `https://levnytt.se/golden-home-care` | MERGE | P3 | LOW | Fold into sustainability pillar page |
| `https://levnytt.se/ala-vs-epa-vs-dha` | REMOVE | P2 | HIGH | Remove or 301 to comprehensive omega-3 guide |
| `https://levnytt.se/ekologisk-stadning-greenwashing` | REMOVE | P3 | MEDIUM | Remove or fold into cleaning pillar |

---

**End of GSC Content Audit — 2026-07-02**
