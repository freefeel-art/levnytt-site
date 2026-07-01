# Production Brief Specification V1

**Date:** 2026-07-01
**Status:** ACTIVE — single source of truth for the Production Brief data model
**Scope:** All LevNytt content production

---

## Purpose

The Production Brief is the canonical input to the LevNytt production pipeline. It describes an **editorial assignment**, not a keyword. The keyword is one field among many — the brief captures the full editorial intent.

A Production Brief answers: *What should be produced, for whom, why, and with what constraints?*

---

## Role in the Pipeline

```
Production Brief
    ↓
Research Commander       ← reads the brief, builds a research mission
    ↓
Research Package         ← structured research output
    ↓
Editorial Commander      ← reads the package, produces editorial brief
    ↓
Editorial Brief          ← writer-ready instructions
    ↓
Writer
    ↓
Publication Agent
    ↓
QA
    ↓
Production Report
```

No agent beyond Production Brief should handle raw keywords. Every downstream agent receives a structured input.

---

## Canonical Format

Production Briefs are stored as **YAML** files with a `.brief.yaml` extension. JSON is accepted as an alternative serialization; YAML is canonical.

**Location:** `content/briefs/<slug>.brief.yaml`

---

## Field Specification

### `title` (required)
The working title of the article. Used by the Writer as the primary H1 and `<title>` tag.

| Field | Value |
|---|---|
| **Type** | `string` |
| **Required** | Yes |
| **Min length** | 5 characters |
| **Max length** | 80 characters |
| **Example** | `"Vad är lutein? — karotenoiden för ögon, hud och hjärna"` |

---

### `entity` (required)
The primary topic entity. Can be a single string or an array. These are the subject(s) the article is about.

| Field | Value |
|---|---|
| **Type** | `string[]` |
| **Required** | Yes |
| **Min items** | 1 |
| **Example** | `["lutein"]` |

**Rules:**
- First entity is the primary subject
- Additional entities are the article's secondary focus
- Entity names should be lowercase, singular form preferred
- Used by Research Commander for authority research, PubMed queries, and entity disambiguation

---

### `primary_keyword` (required)
The target search keyword. This is the SEO entry point — but it does NOT define the article's scope. The entity and goal define the scope.

| Field | Value |
|---|---|
| **Type** | `string` |
| **Required** | Yes |
| **Example** | `"vad är lutein"` |

**Rules:**
- Lowercase
- Swedish language
- This is what the article targets in Google, not what it must only be about

---

### `content_type` (required)
The article type. Controls which section template the Writer uses.

| Field | Value |
|---|---|
| **Type** | `enum` |
| **Required** | Yes |
| **Values** | `informational_article`, `pillar_page`, `product_page`, `comparison`, `authority_page`, `news_brief` |
| **Default** | `informational_article` |

---

### `intent` (required)
The search intent of the primary keyword. Auto-detected but can be overridden.

| Field | Value |
|---|---|
| **Type** | `enum` |
| **Required** | Yes |
| **Values** | `definition`, `how_to`, `listicle`, `comparison`, `explainer` |

**Auto-detection rules:**
| Keyword pattern | Intent |
|---|---|
| `vad är`, `vad ar`, `definition`, `betydelse` | `definition` |
| `hur`, `hur fungerar`, `steg för steg` | `how_to` |
| `bästa`, `topp`, `lista`, `rankning` | `listicle` |
| `vs`, `eller`, `jämför`, `skillnad`, `alternativ` | `comparison` |
| Everything else | `explainer` |

---

### `topic` (required)
The high-level content domain. Used for category classification and authority research routing.

| Field | Value |
|---|---|
| **Type** | `enum` |
| **Required** | Yes |
| **Values** | `vitamins`, `minerals`, `fatty_acids`, `antioxidants`, `gut_health`, `protein`, `nutrition`, `supplements`, `skincare`, `cleaning`, `business`, `regulation`, `general_health`, `healthy_aging`, `sleep`, `stress`, `hormones`, `children`, `pregnancy`, `sports`, `weight` |

---

### `cluster` (required)
The topical cluster this article belongs to. Used for internal linking and hub-and-spoke architecture.

| Field | Value |
|---|---|
| **Type** | `enum` |
| **Required** | Yes |
| **Values** | `omega_3`, `vitamin_d`, `magnesium`, `carotenoids`, `probiotics`, `fiber`, `antioxidants`, `protein`, `zinc`, `iron`, `selenium`, `b_vitamins`, `multivitamins`, `collagen`, `creatine`, `melatonin`, `golden_home_care`, `direct_sales`, `neolife_products`, `general` |

**Rules:**
- Determines which hub page the article links to
- Research Commander uses this to find related existing content
- Writer uses this for internal linking priority

---

### `audience` (required)
The target reader.

| Field | Value |
|---|---|
| **Type** | `enum` |
| **Required** | Yes |
| **Values** | `consumers`, `health_enthusiasts`, `seniors`, `parents`, `athletes`, `women`, `men`, `distributors`, `researchers`, `general` |

**Rules:**
- Influences tone, complexity, and CTA strategy
- `consumers` = general public, accessible language
- `health_enthusiasts` = readers with existing supplement knowledge
- `distributors` = NeoLife distributors (business perspective)

---

### `language` (required)
The article language.

| Field | Value |
|---|---|
| **Type** | `enum` |
| **Required** | Yes |
| **Values** | `sv`, `en` |
| **Default** | `sv` |
| **Example** | `sv` |

---

### `authority_mode` (required)
The content authority mode. Controls citation strictness, tone, and YMYL rules.

| Field | Value |
|---|---|
| **Type** | `enum` |
| **Required** | Yes |
| **Values** | `health`, `science`, `business`, `general` |
| **Default** | `health` |

**Behavior by mode:**

| Mode | YMYL Reddit skip | Evidence tier required | Citation strictness |
|---|---|---|---|
| `health` | Yes | T1 preferred, min T3 | Every claim must have cited source |
| `science` | Yes | T1 preferred, min T2 | Same as health |
| `business` | No | Not required | Cited for factual claims only |
| `general` | No | Not required | Standard EEAT |

---

### `goal` (required)
The editorial goal. A 1-3 sentence description of what this article aims to accomplish. This is the brief's thesis statement.

| Field | Value |
|---|---|
| **Type** | `string` |
| **Required** | Yes |
| **Min length** | 20 characters |
| **Max length** | 500 characters |
| **Example** | `"Explain what lutein is, where it is found, what current research says about eye and skin health, and when supplementation may be relevant. Help the reader understand the carotenoid family and lutein's specific role."` |

**Rules:**
- Written in active voice
- Describes what the article DOES, not what it IS
- Research Commander uses this to scope the research mission
- Writer uses this as the article's north star

---

### `publication` (required)
Where the article will be published. Currently only `levnytt.se`.

| Field | Value |
|---|---|
| **Type** | `string` |
| **Required** | Yes |
| **Values** | `levnytt.se` |
| **Example** | `levnytt.se` |

---

### `related_entities` (optional)
Entities related to the primary entity that the article should mention, explain, or link to.

| Field | Value |
|---|---|
| **Type** | `string[]` |
| **Required** | No |
| **Min items** | 0 |
| **Example** | `["zeaxanthin", "macula", "carotenoids", "beta-carotene"]` |

**Rules:**
- Used by Research Commander for entity co-occurrence analysis
- Used by Writer for internal linking and "related concepts" sections
- Each entity should appear naturally in the article at least once

---

### `required_outputs` (required)
What content blocks the article must contain. Guides the writer's structural decisions.

| Field | Value |
|---|---|
| **Type** | `enum[]` |
| **Required** | Yes |
| **Min items** | 1 |

**Available outputs:**

| Value | Description | Article types that must have this |
|---|---|---|
| `definition` | Clear definition of the primary entity | `definition`, `explainer` |
| `evidence` | Research evidence with cited sources | All health/science articles |
| `food_sources` | Dietary sources of the entity | Nutrition/supplement articles |
| `safety` | Safety, side effects, contraindications | All health articles |
| `dosage` | Recommended intake, dosing guidance | Supplement articles |
| `comparison` | Comparison with alternatives or forms | `comparison`, supplement articles |
| `faq` | FAQ accordion (6-10 items) | All informational articles |
| `internal_links` | Links to existing LevNytt content | All articles |
| `cta` | Call-to-action block | All articles |
| `practical_guide` | How to implement in daily life | `how_to`, nutrition articles |
| `myth_busting` | Common misconceptions | `definition`, `explainer` |
| `history` | Historical context or origin | `definition`, authority pages |
| `mechanism` | How it works biologically | Health/science articles |
| `stat_cards` | Sourced statistics in card format | All articles |

---

## Validation Rules

### Required field check
All required fields must be present and non-empty.

### Enum check
Enum fields must contain only valid values.

### Entity-keyword coherence
The primary entity must be semantically related to the primary keyword. Flag a warning if they appear to describe different things.

### Cluster-entity coherence
The cluster must be relevant to the entity. e.g., `lutein` → `carotenoids`, not `omega_3`.

### Output completeness
`required_outputs` must include `faq` and `internal_links` for all `informational_article` types. Health articles must include `evidence`, `safety`, and `food_sources`.

### Title format
The title should contain the primary entity and be in the target language.

---

## Complete Example

```yaml
# content/briefs/vad-ar-lutein.brief.yaml
title: Vad är lutein? — karotenoiden för ögon, hud och hjärna

entity:
  - lutein

primary_keyword:
  vad är lutein

content_type:
  informational_article

intent:
  definition

topic:
  antioxidants

cluster:
  carotenoids

audience:
  consumers

language:
  sv

authority_mode:
  health

goal: >
  Explain what lutein is, where it is found in food, what current
  research says about eye health, skin protection and cognitive
  function, and when supplementation may be relevant. Help the
  reader understand lutein's role in the carotenoid family.

publication:
  levnytt.se

related_entities:
  - zeaxanthin
  - macula
  - carotenoids
  - beta-carotene
  - meso-zeaxanthin

required_outputs:
  - definition
  - evidence
  - food_sources
  - mechanism
  - safety
  - dosage
  - faq
  - internal_links
  - cta
  - stat_cards
  - practical_guide
```

---

## Version History

| Version | Date | Change |
|---|---|---|
| V1 | 2026-07-01 | Initial specification. 14 fields, YAML format, validation rules, example. |