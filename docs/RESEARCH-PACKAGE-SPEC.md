# Research Package Specification V1

**Date:** 2026-07-01
**Status:** ACTIVE
**Input:** Production Brief (`content/briefs/<slug>.brief.yaml`)
**Output:** Research Package (`research/packages/<slug>/`)

---

## Purpose

The Research Package is the structured output of the Research Commander. It is the **only** input to the Editorial Commander. It contains all raw research data organized by domain — sources, studies, entities, competitor analysis, and editorial guidance.

The Research Commander does NOT write articles. It builds research packages.

---

## Directory Structure

```
research/packages/<slug>/
├── manifest.json                 ← Package metadata + provenance
├── research-summary.md           ← Human-readable synthesis
├── sources.json                  ← All cited sources with evidence tiers
├── studies.json                  ← Scientific studies with extracted claims
├── entities.json                 ← Named entities and their relationships
├── internal-links.json           ← Recommended internal link targets
├── faq.json                      ← FAQ candidates with draft answers
├── competitor-analysis.md        ← Top 3-5 SERP competitor breakdown
├── evidence.md                   ← Evidence tier map for each major claim
├── keywords.json                 ← LSI + co-occurring keyword clusters
├── product-notes.json            ← Relevant NeoLife products (optional)
└── audit.json                    ← Execution log (module status, cache hits, errors)
```

---

## Field Specifications

### `manifest.json` (required)

Package metadata and provenance. Every package must carry a manifest.

```json
{
  "manifest_version": 1,
  "package_version": 1,
  "slug": "vad-ar-lutein",
  "brief_source": "content/briefs/vad-ar-lutein.brief.yaml",
  "created": "2026-07-01T12:00:00Z",
  "commander_version": "1.0",
  "lifecycle": "completed",
  "total_duration_ms": 15200,
  "cache_used": true,
  "modules": [
    {
      "module": "authority",
      "status": "completed",
      "cached": false,
      "duration_ms": 4520,
      "confidence": "high",
      "output": "research/packages/vad-ar-lutein/sources.json"
    }
  ],
  "conflicts": [],
  "research_valid_until": "2026-07-31T12:00:00Z"
}
```

| Field | Type | Description |
|---|---|---|
| `manifest_version` | int | Schema version (currently 1) |
| `package_version` | int | Incrementing version for this topic |
| `slug` | string | URL slug, matches brief |
| `brief_source` | string | Path to the Production Brief that spawned this package |
| `created` | ISO 8601 | Timestamp when package was completed |
| `commander_version` | string | Research Commander version |
| `lifecycle` | enum | `draft`, `running`, `completed`, `approved`, `rejected` |
| `total_duration_ms` | int | Total execution time in milliseconds |
| `cache_used` | bool | Whether any module used cached data |
| `modules` | array | Per-module execution status |
| `conflicts` | array | Cross-module contradictions detected |
| `research_valid_until` | ISO 8601 | Expiry date (shortest module TTL) |

---

### `research-summary.md` (required)

Human-readable 2-3 paragraph synthesis. This is what a human editor reads first.

**Structure:**
```markdown
# Research Summary: <Topic Name>

**Slug:** <slug>
**Generated:** YYYY-MM-DD
**Modules run:** authority, dataforseo, content-gap

## Key findings

- 2-3 paragraphs covering: what the research consensus is, what
  is contested, what the reader needs to know, and what the
  article should emphasize.

## Knowledge gaps

- What research couldn't answer
- What evidence is thin or conflicting

## Recommended angle

- How the article should frame the topic
- What to lead with
- What to avoid
```

---

### `sources.json` (required)

All sources found during research, ranked by evidence tier.

```json
{
  "sources": [
    {
      "id": "src-001",
      "title": "Lutein and Zeaxanthin — Food Sources, Bioavailability and Dietary Variety in Age-Related Macular Degeneration Protection",
      "type": "systematic_review",
      "authors": ["Eisenhauer B", "Natoli S", "Liew G", "Flood VM"],
      "year": 2017,
      "journal": "Nutrients",
      "doi": "10.3390/nu9020120",
      "url": "https://pubmed.ncbi.nlm.nih.gov/28218718/",
      "evidence_tier": 1,
      "sample_size": null,
      "key_claims": [
        "Lutein and zeaxanthin are the only carotenoids that accumulate in the macula",
        "Dietary intake of 6 mg/day lutein associated with reduced AMD risk"
      ],
      "retrieval_date": "2026-07-01",
      "confidence": "high",
      "origin_module": "authority"
    }
  ],
  "counts": {
    "tier_1": 3,
    "tier_2": 5,
    "tier_3": 8,
    "tier_4": 2,
    "total": 18
  }
}
```

| Field | Type | Description |
|---|---|---|
| `id` | string | Internal reference ID |
| `title` | string | Full publication title |
| `type` | enum | `systematic_review`, `meta_analysis`, `rct`, `observational`, `review`, `guideline`, `expert_opinion`, `regulatory` |
| `authors` | string[] | Author names |
| `year` | int | Publication year |
| `journal` | string | Journal or publisher name |
| `doi` | string | DOI if available |
| `url` | string | Fetchable URL |
| `evidence_tier` | int | 1-4 (see Evidence Tiers below) |
| `sample_size` | int or null | n= value if available |
| `key_claims` | string[] | 1-3 direct claims from the source |
| `retrieval_date` | string | When the source was accessed |
| `confidence` | enum | `high`, `medium`, `low` |
| `origin_module` | string | Which research module found this source |

**Evidence Tiers:**
| Tier | Sources |
|---|---|
| 1 | Systematic reviews, meta-analyses, clinical guidelines |
| 2 | Human RCTs, controlled trials |
| 3 | Observational studies (cohort, cross-sectional, case-control) |
| 4 | Expert commentary, review articles by named experts |

---

### `studies.json` (required for health/science topics)

Extracted study data with sample sizes, endpoints, and key statistics.

```json
{
  "studies": [
    {
      "id": "study-001",
      "source_id": "src-001",
      "design": "systematic_review",
      "population": "Adults 50+ with AMD risk",
      "intervention": "Dietary lutein intake analysis",
      "sample_size": 12000,
      "duration": "5 years follow-up",
      "primary_endpoint": "AMD progression",
      "key_result": "6 mg/day lutein associated with 26% lower AMD progression risk",
      "p_value": "<0.05",
      "effect_size": "RR 0.74",
      "limitations": "Observational — association, not causation"
    }
  ]
}
```

---

### `entities.json` (required)

Named entities and their relationships. Used for LSI clustering and internal linking.

```json
{
  "primary_entity": "lutein",
  "entities": [
    {
      "name": "lutein",
      "type": "nutrient",
      "category": "carotenoid",
      "synonyms": ["E161b", "xanthophyll"],
      "related": ["zeaxanthin", "meso-zeaxanthin", "beta-carotene"],
      "co_occurrence_frequency": "high",
      "brief_context": "Yellow carotenoid pigment found in green leafy vegetables and egg yolks. Accumulates in the macula."
    }
  ],
  "relationships": [
    {
      "from": "lutein",
      "to": "zeaxanthin",
      "relation": "structural_isomer",
      "context": "Both accumulate in the macula; lutein dominates peripherally, zeaxanthin centrally."
    }
  ]
}
```

---

### `internal-links.json` (required)

Recommended internal link targets with anchor text and placement context.

```json
{
  "links": [
    {
      "url": "/neolife-carotenoid-complex",
      "anchor_text": "karotenoidkomplex",
      "placement_context": "When discussing carotenoid supplements — introduce Carotenoid Complex as an example of a multi-carotenoid formula",
      "priority": "primary",
      "flow_stage": "research",
      "page_type": "product"
    }
  ],
  "flow": "eye_health_explanation → carotenoid_science → product_example"
}
```

| Field | Description |
|---|---|
| `url` | levnytt.se page path |
| `anchor_text` | Suggested Swedish anchor text |
| `placement_context` | When and where in the article to place this link |
| `priority` | `primary` (must link), `secondary` (link if natural), `tertiary` (optional) |
| `flow_stage` | `problem`, `research`, `education`, `product`, `cta` |
| `page_type` | `product`, `pillar`, `article`, `hub`, `authority` |

---

### `faq.json` (required)

FAQ candidates with draft answers. 6-10 items.

```json
{
  "questions": [
    {
      "id": "faq-001",
      "question": "Vad är lutein?",
      "draft_answer": "Lutein är en karotenoid — ett gult pigment som finns i gröna bladgrönsaker, äggulor och andra livsmedel. Det tillhör xantofyllfamiljen och är en av de två karotenoiderna (tillsammans med zeaxantin) som ansamlas i ögats gula fläck (makula).",
      "source_ids": ["src-001", "src-004"],
      "confidence": "high",
      "search_query": "vad är lutein"
    }
  ]
}
```

---

### `competitor-analysis.md` (required)

Top 3-5 ranking pages for the primary keyword. What they cover, what they miss.

```markdown
# Competitor Analysis: <keyword>

**Generated:** YYYY-MM-DD
**SERP date:** YYYY-MM-DD

## Position 1: <URL>
- **Title:** ...
- **Word count:** ~X
- **Covers:** [topics they cover]
- **Missing:** [gaps we can fill]
- **Evidence tier:** [what level of sourcing they use]
- **CTAs:** [how they monetize]

## Position 2: ...
## Position 3: ...

## Gap summary

- Competitors miss: [X], [Y], [Z]
- Our angle: ...
```

---

### `evidence.md` (required for health/science)

Maps every major claim the article will make to its evidence tier and source.

```markdown
# Evidence Map: <Topic>

| Claim | Evidence Tier | Source ID | Strength |
|---|---|---|---|
| Lutein accumulates in the macula | Tier 1 | src-001 | Strong consensus |
| 6 mg/day associated with AMD risk reduction | Tier 3 | src-001 | Observational — association |
| Supplementation improves MPOD | Tier 2 | src-007 | RCT — moderate evidence |
| Skin photoprotection effect | Tier 2 | src-011 | Small RCT — promising |
```

---

### `product-notes.json` (optional)

Relevant NeoLife products for CTA placement.

```json
{
  "products": [
    {
      "name": "Carotenoid Complex",
      "slug": "neolife-carotenoid-complex",
      "relevance": "Contains lutein as part of a full-spectrum carotenoid blend",
      "efsa_status": "compliant",
      "cta_placement": "secondary_cta",
      "evidence_notes": "Product contains lutein from marigold extract"
    }
  ]
}
```

---

## Research Commander Contract

The Research Commander receives a Production Brief and produces a Research Package.

### Input
`content/briefs/<slug>.brief.yaml`

### Output
`research/packages/<slug>/` with all required files

### Gate
- `manifest.json` exists and `lifecycle = completed`
- `sources.json` has at least 3 Tier 1-2 sources (health/science topics)
- `faq.json` has at least 6 questions
- `internal-links.json` has at least 3 links

### Failure
If not enough sources exist or modules fail critically, the package lifecycle is set to `partial`. Editorial Commander decides whether to proceed.

---

## Version History

| Version | Date | Change |
|---|---|---|
| V1 | 2026-07-01 | Initial specification. 12 package files, JSON/YAML/MD formats. |
