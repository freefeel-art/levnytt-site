# Product Entity System Specification

**Status:** Specification — Complete (Sprint 14)
**Last updated:** 2026-06-30
**Supersedes:** `content/products/entity_formula_iv/sv.json` (prototype — archived to `content/products/archive/entity_formula_iv_prototype/` in Sprint 14)
**Related:** `docs/databank/LEVNYTT-PRICE-DATABASE.md`, `docs/PUBLICATION-ARTICLE-STANDARD.md`,
`DECISIONS.md`, `docs/BRAND-DESIGN-SYSTEM.md`

---

## 1. Purpose

The Product Entity System creates a single, structured, machine-readable record for every NeoLife product that LevNytt markets. It is the canonical source for product identity, classification, and metadata — separate from price data (Price Database) and editorial content (articles/pillar pages).

Each Product Entity is a JSON file that captures what a product *is* — its identity, classification, benefits, ingredients, research references, and relationships. It does NOT capture what a product *costs* (that belongs in the Price Database) or what we have *written* about it (that belongs in articles).

### Why this exists

Before this specification, product information was scattered across:

- **Pillar pages** (`neolife-*.html`) — the richest source, but embedded in prose
- **Price Database** (`docs/databank/LEVNYTT-PRICE-DATABASE.md`) — prices only, no product metadata
- **Entity prototype** (`content/products/entity_formula_iv/sv.json`) — proof-of-concept, 1 of ~25 products (archived Sprint 14)
- **Affärsmöjlighet page** — hardcoded prices for 7 products
- **Internal linking and tier boxes** — hand-coded per page

This duplication creates inconsistency. The Product Entity System centralizes product metadata so every page, tool, and future integration derives identity data from the same source.

---

## 2. Schema

> **Decisions integrated (Sprint 13):** Multi-variant products use `variants[]` array; unmarketed products use `status` field.

### 2.1 Core Identity Fields

#### `canonical_id` (string, required)
Unique machine-readable identifier for this entity. Convention: `entity_<snake_case_product_name>`.

**Why:** Every entity needs a stable key that never changes, regardless of product name changes, rebranding, or NeoLife code changes. Used for internal references, relationships, and future API lookups.

**Example:** `"entity_omega_3_plus"`

#### `neoLife_code` (integer, required)
The official NeoLife product code (numeric).

**Why:** This is NeoLife's own primary key. It appears on product packaging, in the NeoLife shop URL, and in NeoLife's internal systems. Having it in the entity enables cross-referencing with NeoLife's official data and confirms product identity unambiguously.

**Example:** `929`

#### `locale` (string, required)
ISO 639-1 language code. Always `"sv"` for current production content.

**Why:** Supports future multilingual expansion. The entity directory structure uses locale subdirectories, and this field makes the locale explicit in the data.

**Example:** `"sv"`

#### `slug` (string, required)
URL-safe slug for the product page on LevNytt. Matches the page filename (without extension) or canonical URL.

**Why:** Enables automatic linking between entities and their production pages. A tool can construct `https://levnytt.se/{slug}` from the entity without hardcoding URLs.

**Example:** `"neolife-omega-3-plus"`

---

### 2.2 Naming Fields

#### `product_name` (string, required)
Official NeoLife Swedish product name.

**Why:** This is the authoritative name used in NeoLife's price list, packaging, and shop. All pages should use this name for consistency.

**Example:** `"Omega-3 Plus"`

#### `aliases` (array of strings, optional)
Alternative names the product is known by, including older names, variant names, or colloquial names.

**Why:** Products may have older names, variant suffixes (Plus, Classic, etc.), or be referred to by key ingredients rather than brand name. This enables search tools, link matchers, and future AI features to recognize the product across different naming conventions.

**Example:** `["Omega-3", "Laxoljekapslar", "Fiskolja"]`

**Note on Tre-en-en dual codes:** The entity for Tre-en-en will document both code 927 (current, 120 caps) and code 510 (older/variant) in aliases or a dedicated `legacy_codes` field, resolving this inconsistency in a single authoritative record.

#### `legacy_codes` (array of integers, optional)
NeoLife product codes that this product has been known under in the past.

**Why:** NeoLife may change product codes over time. The Tre-en-en product (currently 927, previously known as 510) is a documented case. Maintaining legacy codes prevents customer confusion and enables historical data continuity.

**Example:** `[510]`

---

### 2.3 Classification Fields

#### `category` (string, required)
Top-level product category. Must be one of the defined categories from the product taxonomy.

**Why:** Categories group products for navigation, filtering, and comparison. Using a controlled vocabulary prevents the category fragmentation seen between pillar pages and Price Database.

**Allowed values:** `"supplements"`, `"weight_management"`, `"home_care"`, `"personal_care"`, `"skin_care"`, `"accessories"`

#### `subcategory` (string, required)
Second-level classification within the category. More specific than `category`.

**Why:** Within supplements, there are fundamentally different product types (omega-3, multivitamin, mineral, probiotic, phytonutrient, etc.). Subcategories enable precise grouping for related product suggestions, comparison tables, and content clustering.

**Allowed values:** `"omega-3"`, `"multivitamin"`, `"mineral"`, `"phytonutrient"`, `"probiotic"`, `"protein_meal"`, `"green_drink"`, `"targeted_supplement"`, `"all_cleaner"`, `"dish_soap"`, `"laundry"`, `"fabric_softener"`, `"shampoo"`, `"conditioner"`, `"body_lotion"`, `"facial_care"`, `"accessory"`

#### `product_family` (string, optional)
Group name if the product belongs to a product system or family.

**Why:** Several NeoLife products are designed to work together (Pro Vitality system: Formula IV + Tre-en-en + Omega-3 Plus + Carotenoid Complex). The `product_family` field captures this relationship explicitly.

**Example:** `"pro_vitality_system"`

#### `keywords` (array of strings, optional)
List of relevant search terms, ingredient names, health conditions, and topics.

**Why:** Enables content recommendation engines, internal search, and future AI integrations to match products to relevant content and user queries.

**Example:** `["EPA", "DHA", "DPA", "triglyceridform", "omega-3", "fiskolja", "hjärtat", "inflammation", "cellmembran"]`

---

### 2.4 Descriptive Fields

#### `short_description` (string, required)
One-sentence description of the product, for use in OG meta tags, tier boxes, link previews, and summary cards.

**Why:** Standardized short descriptions eliminate the hand-crafted, sometimes inconsistent summaries currently spread across tier boxes, meta tags, and link previews. Every reference to this product uses the same description.

**Max length:** 155 characters

**Example:** `"Högkoncentrerat omega-3-tillskott i triglyceridform från kallvattensfisk — 460 mg EPA, 480 mg DHA per kapsel."`

#### `summary` (string, required)
2–4 sentence summary of what the product is and why it exists. Used for entity pages, comparison tables, and tooltips.

**Why:** Provides consistent product positioning across all surfaces that need more than a single sentence but less than a full article.

**Example:** `"Omega-3 Plus är NeoLifes koncentrerade omega-3-tillskott från vildfångad kallvattensfisk. Fettsyrorna föreligger i triglyceridform — samma form som förekommer naturligt i fisk — vilket enligt forskning ger bättre absorption än etylesterformer. Varje kapsel innehåller 460 mg EPA och 480 mg DHA."`

---

### 2.5 Technical Fields

#### `ingredients` (array of objects, optional)
Key ingredients/components with known amounts.

**Why:** Pillar pages currently list ingredients inconsistently — some with exact amounts, some generic. A structured list enables comparison tables, automated FAQ generation, and future "compare this product" features.

**Structure:** `{"name": "string", "amount": "string (optional)", "unit": "string (optional)"}`

**Example:** `[{"name": "EPA", "amount": "460", "unit": "mg"}, {"name": "DHA", "amount": "480", "unit": "mg"}, {"name": "DPA", "amount": "50", "unit": "mg"}]`

#### `usage` (object, optional)
How the product is used, with dosage and method.

**Why:** Dosage information is scattered across pillar pages and product packaging. A structured record enables consistency in FAQ answers, comparison tables, and future interactive tools.

**Fields:**
- `dosage`: recommended daily intake (e.g., `"3 kapslar dagligen"`)
- `method`: how to take (e.g., `"i samband med måltid"`)
- `timing`: when to take (e.g., `"morgon"`, `"kväll"`, `"valfri tid"`)
- `duration`: how long a package lasts at recommended dosage (e.g., `"30 dagar"`)
- `safety`: safety notes or contraindications (e.g., `"Bör ej tas av personer med blodförtunnande medicinering utan läkarkontakt"`)

#### `certifications` (array of strings, optional)

**Why:** Certifications (KRAV, ekologisk, MSC, etc.) are trust signals. A structured field ensures they are consistently represented.

**Example:** `["Friend of the Sea"]`

#### `packaging` (object, required)
Physical package information.

**Why:** Package size is essential for price-per-use calculations, comparison tables, and customer decision-making. Currently duplicated between Price Database and pillar pages.

**Fields:**
- `size`: `"integer"` (package quantity)
- `unit`: `"string"` (e.g., `"kapslar"`, `"tabletter"`, `"ml"`, `"sachet"`, `"portioner"`)
- `label`: Human-readable string (e.g., `"90 kapslar"`)

**Example:** `{"size": 90, "unit": "kapslar", "label": "90 kapslar"}`

#### `variants` (array, optional)
For multi-variant products (identical formulation but different package sizes, flavors, or codes). One entity with shared identity/descriptive fields and a `variants` array.

**Why:** Multi-variant products (e.g., Super 10 in 1L/5L/10L/25L) would otherwise require duplicate entities for each size. A single entity with variants keeps formulation, ingredients, research, and descriptions in one place while listing the packaging/code differences per variant.

**Structure per variant:**
```json
{
  "code": 17,
  "packaging": {"size": 5, "unit": "l", "label": "5 l"},
  "price_database_ref": {"code": 17, "database": "docs/databank/LEVNYTT-PRICE-DATABASE.md", "section": "3. GOLDEN RENGÖRING"}
}
```

When `variants` is present:
- The top-level `neoLife_code`, `packaging`, and `price_database_ref` refer to the primary/default variant.
- Each variant in the array specifies its own `code`, `packaging`, and `price_database_ref`.

---

### 2.6a Status Field

#### `status` (string, optional)
Product marketing status. Omit or set to `"active"` for currently marketed products. Set to `"inactive"` for products in the Price Database but not actively marketed.

**Why:** Some NeoLife products exist in the Price Database (legacy or passive availability) but are not actively marketed by LevNytt. A status field distinguishes between "we sell this" and "we can order this if asked."

**Allowed values:** `"active"` (default if omitted), `"inactive"`

**Example:** `"inactive"`

---


### 2.6 Reference Fields

#### `price_database_ref` (object, required)
Reference to the product's entry in the Price Database.

**Why:** The entity must connect to the Price Database without duplicating price data. A reference ensures prices remain a single source of truth while the entity provides the identity layer.

**Fields:**
- `code`: the NeoLife code matching the Price Database row
- `database`: `"docs/databank/LEVNYTT-PRICE-DATABASE.md"`
- `section`: category section in the Price Database (e.g., `"1. KOSTTILLSKOTT"`)

**Example:** `{"code": 929, "database": "docs/databank/LEVNYTT-PRICE-DATABASE.md", "section": "1. KOSTTILLSKOTT"}`

#### `shop_path` (string, required)
Relative path to the product page on the NeoLife shop. Used by `components.js` to construct sponsor-linked URLs.

**Why:** Currently hardcoded in `components.js`'s `productMap`. Moving this to the entity enables a single source of truth for shop URLs, which can then be consumed by any tool or page.

**Example:** `"/i/shop/nutrition/omega-3-plus.html"`

#### `media` (object, optional)
References to product images and other media assets.

**Why:** Product images are scattered across `images/`, `img/og/`, and product subdirectories. A structured reference enables consistent image use and future media automation.

**Fields:**
- `og_image`: URL to the product-specific OG image (if different from brand default)
- `hero_image`: URL to the product hero image used on the pillar page
- `product_image`: URL to the product photo

---

### 2.7 Relationship Fields

#### `related_product_ids` (array of strings, optional)
Array of `canonical_id` values for products commonly purchased or used alongside this one.

**Why:** Enables automated "related products" sections, bundle suggestions, and cross-linking without hand-coding. Products in the same family or frequently mentioned together are naturally linked.

**Example:** `["entity_tre_en_en", "entity_carotenoid_complex", "entity_formula_iv"]`

#### `related_article_slugs` (array of strings, optional)
Array of article slugs (`content/articles/{slug}.html`) that are contextually related to this product.

**Why:** Currently, related articles are linked by hand in pillar pages and tier boxes. An entity-level relationship allows automated tier box generation and content recommendation.

#### `faq_references` (array of strings, optional)
Array of questions or question slugs from FAQ sections that are relevant to this product.

**Why:** Enables future FAQ generation or FAQ cross-linking tools to automatically pull product-relevant questions.

---

### 2.8 Research Fields

#### `research_references` (array of objects, optional)
Key scientific research directly relevant to this product's ingredients or health claims. Not a comprehensive bibliography — only the most authoritative and LevNytt-relevant sources.

**Why:** Pillar pages cite research inconsistently. A structured reference list, with evidence tiers matching the Publication Article Standard, makes research portable: any page referencing this product can pull the same authoritative sources.

**Structure:** `{"tier": "T1|T2|T3|T4", "label": "string", "url": "URL (optional)"}`

**Tier mapping:** Matches the PA standard: T1 = systematic review/meta-analysis/health authority, T2 = individual RCT, T3 = observational study, T4 = mechanistic/expert opinion.

**Example:**
```json
[
  {"tier": "T1", "label": "Omega-3 fatty acids and cardiovascular disease: a systematic review", "url": "https://pubmed.ncbi.nlm.nih.gov/..."},
  {"tier": "T2", "label": "Triglyceride vs ethyl ester omega-3 absorption: RCT", "url": "https://pubmed.ncbi.nlm.nih.gov/..."},
  {"tier": "T1", "label": "EFSA scientific opinion on EPA/DHA health claims", "url": "https://efsa.europa.eu/..."}
]
```

---

### 2.9 Audit Fields

#### `last_verified` (string, required)
ISO 8601 date when the entity data was last verified against NeoLife's official product information.

**Why:** Product information changes over time. This field creates accountability and enables automated audit cycles.

**Example:** `"2026-06-30"`

#### `entity_version` (integer, required)
Monotonically increasing version number for this entity file. Starts at 1.

**Why:** Enables change tracking, caching invalidation, and downstream consumers to know when the entity has changed.

**Example:** `1`

---

## 3. Full Schema (Reference)

```json
{
  "$schema": "Product Entity v1",
  "required": [
    "canonical_id",
    "neoLife_code",
    "locale",
    "slug",
    "product_name",
    "category",
    "subcategory",
    "short_description",
    "summary",
    "packaging",
    "price_database_ref",
    "shop_path",
    "last_verified",
    "entity_version"
  ],
  "fields": {
    "canonical_id": "string",
    "neoLife_code": "integer",
    "locale": "string (sv)",
    "slug": "string",
    "product_name": "string",
    "aliases": ["string"],
    "legacy_codes": ["integer"],
    "status": "string (\"active\"|\"inactive\")",
    "category": "string (controlled vocabulary)",
    "subcategory": "string (controlled vocabulary)",
    "product_family": "string",
    "keywords": ["string"],
    "short_description": "string (≤155 chars)",
    "summary": "string",
    "ingredients": [{"name": "string", "amount": "string?", "unit": "string?"}],
    "usage": {"dosage": "string?", "method": "string?", "timing": "string?", "duration": "string?", "safety": "string?"},
    "certifications": ["string"],
    "packaging": {"size": "integer", "unit": "string", "label": "string"},
    "variants": [{"code": "integer", "packaging": {"size": "integer", "unit": "string", "label": "string"}, "price_database_ref": {"code": "integer", "database": "string", "section": "string"}}],
    "price_database_ref": {"code": "integer", "database": "string", "section": "string"},
    "shop_path": "string",
    "media": {"og_image": "string?", "hero_image": "string?", "product_image": "string?"},
    "related_product_ids": ["string"],
    "related_article_slugs": ["string"],
    "faq_references": ["string"],
    "research_references": [{"tier": "string", "label": "string", "url": "string?"}],
    "last_verified": "string (date)",
    "entity_version": "integer"
  }
}
```

---

## 4. Repository Structure

### 4.1 Location

Product entities live in:
```
content/products/entities/<canonical_id>/<locale>.json
```

**Rationale:**
- `content/products/` already exists and housed the Formula IV prototype entity (archived to `content/products/archive/entity_formula_iv_prototype/`). The new structure extends this convention.
- Per-entity directories (not a flat file list) allow future expansion with per-locale translations (`sv.json`, `en.json`, etc.) and associated assets (images, PDFs) without crowding a single directory.
- JSON is chosen because it is machine-parseable, language-agnostic, requires no build step, and can be loaded by JavaScript at runtime if needed.

### 4.2 Supporting Files

| File | Purpose |
|---|---|
| `content/products/categories.json` | Controlled vocabulary for category and subcategory values |
| `content/products/README.md` | How to create, update, and consume product entities |
| `docs/specifications/PRODUCT-ENTITY-SYSTEM.md` | This specification (schema, architecture, integration, migration) |

### 4.3 Example File

`content/products/entities/entity_omega_3_plus/sv.json`:

```json
{
  "canonical_id": "entity_omega_3_plus",
  "neoLife_code": 929,
  "locale": "sv",
  "slug": "neolife-omega-3-plus",
  "product_name": "Omega-3 Plus",
  "aliases": ["Omega-3", "Laxoljekapslar"],
  "legacy_codes": [],
  "category": "supplements",
  "subcategory": "omega-3",
  "product_family": "pro_vitality_system",
  "keywords": ["EPA", "DHA", "DPA", "triglyceridform", "fiskolja", "cellmembran"],
  "short_description": "Högkoncentrerat omega-3-tillskott i triglyceridform från kallvattensfisk — 460 mg EPA, 480 mg DHA per kapsel.",
  "summary": "Omega-3 Plus är NeoLifes koncentrerade omega-3-tillskott från vildfångad kallvattensfisk. Fettsyrorna föreligger i triglyceridform — samma form som förekommer naturligt i fisk — vilket enligt forskning ger bättre absorption än etylesterformer. Varje kapsel innehåller 460 mg EPA och 480 mg DHA.",
  "ingredients": [
    {"name": "EPA", "amount": "460", "unit": "mg"},
    {"name": "DHA", "amount": "480", "unit": "mg"},
    {"name": "DPA", "amount": "50", "unit": "mg"}
  ],
  "usage": {
    "dosage": "3 kapslar dagligen",
    "method": "i samband med måltid",
    "timing": "valfri tid",
    "duration": "30 dagar (90 kapslar)",
    "safety": "Bör ej tas av personer med blodförtunnande medicinering utan läkarkontakt"
  },
  "certifications": ["Friend of the Sea"],
  "packaging": {"size": 90, "unit": "kapslar", "label": "90 kapslar"},
  "price_database_ref": {
    "code": 929,
    "database": "docs/databank/LEVNYTT-PRICE-DATABASE.md",
    "section": "1. KOSTTILLSKOTT"
  },
  "shop_path": "/i/shop/nutrition/omega-3-plus.html",
  "media": {
    "og_image": "https://levnytt.se/images/omega-3-plus.jpg",
    "hero_image": "https://levnytt.se/images/omega-3-plus.jpg"
  },
  "related_product_ids": [
    "entity_formula_iv",
    "entity_tre_en_en",
    "entity_carotenoid_complex",
    "entity_pro_vitality"
  ],
  "related_article_slugs": [
    "ala-vs-epa-vs-dha",
    "varfor-fiskolja-inte-ar-likvardigt"
  ],
  "faq_references": [
    "Vad är skillnaden mellan triglyceridform och etylester?",
    "Hur mycket EPA och DHA behöver jag per dag?"
  ],
  "research_references": [
    {"tier": "T1", "label": "Omega-3 polyunsaturated fatty acids and cardiovascular health: a systematic review", "url": "https://pubmed.ncbi.nlm.nih.gov/..."},
    {"tier": "T2", "label": "Absorption of omega-3 in triglyceride vs ethyl ester form: a randomized controlled trial", "url": "https://pubmed.ncbi.nlm.nih.gov/..."}
  ],
  "last_verified": "2026-06-30",
  "entity_version": 1
}
```

---

## 5. Category Taxonomy

### 5.1 Categories (Level 1)

| ID | Swedish Label | Price DB Section |
|---|---|---|
| `supplements` | Kosttillskott | 1. KOSTTILLSKOTT |
| `weight_management` | Viktkontroll | 2. VIKTKONTROLL |
| `home_care` | Golden Rengöring | 3. GOLDEN RENGÖRING |
| `personal_care` | Hår & Kroppsvård | 4. NUTRIANCE HÅR & KROPSVÅRD |
| `skin_care` | Hudvård | 5. NUTRIANCE ORGANIC HUDVÅRD |
| `accessories` | Tillbehör | TILLBEHÖR |

### 5.2 Subcategories (Level 2)

| Category | Subcategory | Description |
|---|---|---|
| `supplements` | `omega-3` | Omega-3 and fish oil products |
| `supplements` | `multivitamin` | Multivitamin and broad-spectrum |
| `supplements` | `mineral` | Single-mineral products |
| `supplements` | `phytonutrient` | Plant-based nutrient complexes |
| `supplements` | `probiotic` | Probiotic and digestive health |
| `supplements` | `targeted` | Targeted single-nutrient products (CoQ10, etc.) |
| `supplements` | `protein_meal` | Meal replacement and protein |
| `supplements` | `green_drink` | Vegetable/green drink concentrates |
| `weight_management` | `meal_replacement` | Shakes, bars, teas |
| `home_care` | `all_cleaner` | Multi-purpose and heavy-duty cleaners |
| `home_care` | `dish_soap` | Dish and light cleaning |
| `home_care` | `laundry` | Laundry products |
| `home_care` | `fabric_softener` | Fabric softeners |
| `personal_care` | `shampoo` | Shampoos |
| `personal_care` | `conditioner` | Conditioners |
| `personal_care` | `body_care` | Body wash, lotion, gel |
| `skin_care` | `facial_care` | Facial skin care products |
| `accessories` | `accessory` | Dispensers, bottles, containers |

---

## 6. Relationship to Other Systems

### 6.1 Price Database

The Product Entity and Price Database are separate but linked systems:

| | Product Entity | Price Database |
|---|---|---|
| **What it stores** | Product identity, classification, metadata, ingredients, research | Prices only: customer price, distributor price, savings |
| **Primary key** | `canonical_id` | NeoLife product `code` |
| **Connection** | Entity contains `price_database_ref.code` | Price Database uses product code as row identifier |
| **Update cadence** | When product information changes | When NeoLife publishes new price lists |
| **SSOT for** | Product identity | Product pricing |

**Boundary rule:** Entity files never include price fields (`customer_price`, `distributor_price`, `savings`). Price Database never includes ingredient lists, benefits, or research references.

### 6.2 Facts Library

The "Facts Library" concept does not yet exist in the repository. When it is created, it should store **general health and nutrition facts** (e.g., "EPA reduces inflammation", "Magnesium supports sleep") that are **not specific to NeoLife products**.

The Product Entity stores **product-specific** data. The Facts Library would store **topic-specific** data.

**Boundary rule:** If a fact is about a *product*, it goes in the entity or the article. If a fact is about a *health topic* (ingredient, condition, mechanism), it would go in the Facts Library.

### 6.3 Pillar Pages

Pillar pages are the primary consumers of entity data. When an entity exists, the pillar page should:

- Derive its product name, code, and description from the entity
- Use entity research references as the source for citations
- Link to related products and articles via entity relationships
- Reference but not duplicate data that lives in the entity

This is a future integration. Current pillar pages remain hand-authored. The migration strategy describes how they will be aligned incrementally.

---

## 7. Integration Plan

### 7.1 Publication Agent Integration

**Current state (Sprint 14):** Phase 1 is implemented.

The PA validates article product references against entities before deployment using `content/products/scripts/validate_product_references.py`. Warnings are logged but do not block publication. The PA standard (`docs/PUBLICATION-ARTICLE-STANDARD.md`) documents the SSOT mapping: Product Entities for product identity, Price Database for pricing, Facts Library for scientific claims.

**Implementation sequence:**
1. ✅ **Phase 1 (Sprint 14):** PA validates product references against entities and warns on mismatch. Validator script created. PA agent updated.
2. **Phase 2 (pending):** PA auto-populates shop paths and short descriptions from entities
3. **Phase 3 (pending):** PA generates tier box links from entity `related_product_ids`

### 7.2 Pillar Page Integration

**Current state:** Pillar pages are hand-authored. Product data is embedded in prose.

**Future integration:**
- Pillar page templates include an "entity reference" section that auto-populates product code, price reference, shop link, and related products
- Entity data provides the "ingredients" and "research references" sections of pillar page JSON-LD and content

### 7.3 Calculator Integration

**Current state:** Cost-per-use calculations (in Price Database) use hand-entered reference values.

**Future integration:** Calculators read:
- `packaging.size` from entity for bottle/capsule count
- `usage.dosage` for daily serving count
- Price from Price Database via entity `price_database_ref.code`

This enables any product's cost-per-use to be calculated automatically without manual data entry.

### 7.4 Video Generation Integration

**Future integration:** Entity data (summary, ingredients, research references) provides the script outline for product explainer videos. Each entity becomes a potential video script, with the entity fields mapping to video sections:

| Entity Field | Video Section |
|---|---|
| `short_description` | Hook / intro |
| `summary` | What is this product |
| `ingredients` | What's inside |
| `research_references` | The science |
| `usage` | How to use |
| `related_product_ids` | Related products / what to try next |

### 7.5 Facts Library Integration

The Product Entity System is the foundation for a future Facts Library. Once entities exist, a Facts Library can reference entities in its `related_products` field, and entities can reference Facts Library entries in their `faq_references` or `research_references`. The two systems would be complementary rather than overlapping.

---

## 8. Migration Strategy

### 8.1 Principles

1. **Create entities one at a time.** Each entity is an independent JSON file. There is no "big bang" migration.
2. **Start with the highest-traffic products.** Create entities for the products with the most pillar pages and article references first: Omega-3 Plus, Carotenoid Complex, Pro Vitality, Formula IV, Tre-en-en.
3. **Do not modify existing pages during entity creation.** Entities are a new data layer, not a page migration. Pages continue to work exactly as before.
4. **Entities become the SSOT gradually.** As each entity is created, it is the canonical record for that product. New content (articles, pages) can use it. Existing content is migrated only when that page is next updated for other reasons.
5. **Resolve inconsistencies during entity creation.** The Tre-en-en dual-code issue, category naming, and missing fields are documented and resolved in the entity file — no need to change production pages yet.

### 8.2 Sequence

| Wave | Products | Entity Count | Status |
|---|---|---|---|
| 1 | Omega-3 Plus, Carotenoid Complex, Pro Vitality, Formula IV, Tre-en-en | 5 | ✅ Complete (Sprint 13) |
| 2–6 | All remaining products (supplements, weight management, home care, personal care, skin care, accessories) | ~42 | ✅ Complete (Sprint 14) |

### 8.3 What each migration step involves

For each product:

1. Create `content/products/entities/<canonical_id>/sv.json` using the schema in this specification
2. Populate fields from: pillar page (ingredients, research, usage, benefits), Price Database (code, packaging), existing entity prototype (if any)
3. Resolve any inconsistencies found during population (e.g., dual codes, naming conflicts)
4. Set `last_verified` and `entity_version: 1`
5. The entity is now SSOT for this product. No pages change.

### 8.4 Avoiding duplicate maintenance

- **Entity creation never modifies a production page.** The entity is a new file, not an edit.
- **When a Price Database update occurs:** The Price Database is updated independently. Entity `price_database_ref.code` remains unchanged (the code stays the same even if the price changes).
- **When product information changes (reformulation, new packaging):** The entity is updated to version 2+. Pillar pages are updated only when they are next revised for editorial reasons.
- **When a new article references a product:** The PA can optionally read the entity to validate names and get shop paths. If the entity exists, the PA uses it. If not, the PA falls back to manual reference (current behavior).

---

## 9. Validation Checklist

When a Product Entity is created or updated, verify:

- [ ] `canonical_id` is unique across all entities
- [ ] `neoLife_code` matches the Price Database
- [ ] `slug` matches an existing or planned production page URL
- [ ] All required fields are present
- [ ] `category` and `subcategory` are from the controlled vocabulary
- [ ] `price_database_ref.code` exists in `LEVNYTT-PRICE-DATABASE.md`
- [ ] All `related_product_ids` reference existing entities (validated at creation time)
- [ ] All `related_article_slugs` reference existing or planned articles
- [ ] `short_description` ≤ 155 characters
- [ ] No price data is included in the entity (prices stay in Price Database)
- [ ] `last_verified` is the current date
- [ ] If `variants` is used: each variant has unique `code`, valid `packaging`, and correct `price_database_ref`
- [ ] If `status: "inactive"`: product exists in Price DB but is not actively marketed

---

## 10. Resolved Decisions

| Question | Decision | Resolved |
|---|---|---|
| Safety warnings (disclaimer field) | Use `usage.safety` field in entity — no separate disclaimer needed | Sprint 13 |
| Multi-variant products (Super 10 sizes) | One entity with `variants[]` array; code, packaging, price-DB ref per variant; all else shared | Sprint 13 |
| Unmarketed products (Bio-Tone 935, etc.) | Use `status: "inactive"` field to indicate products not actively marketed but in Price DB | Sprint 13 |
| Publication Agent entity integration | Phase 1 implemented in Sprint 14: validator script, PA agent Step 2, SSOT docs in PA standard | Sprint 14 |

---

## 11. Sprint 13 Recommendation

The highest-value next step is **Wave 1 entity creation** — create entities for the 5 highest-traffic products (Omega-3 Plus, Carotenoid Complex, Pro Vitality, Formula IV, Tre-en-en). This validates the schema against real products, resolves the Tre-en-en dual-code issue in a single authoritative record, and establishes the pattern for all remaining products.

Before Wave 1 creation, resolve the open question about multi-variant products (Super 10 sizes) since it affects the schema design.
