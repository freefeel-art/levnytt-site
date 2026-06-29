# LevNytt — Question Gap Skill

Discover unanswered or poorly answered questions suitable for LevNytt informational articles.

This skill does **not** write articles. Its only job is finding high-value content opportunities. The output feeds directly into the [Informational Article Skill](../../../skills/informational-article/SKILL.md).

---

## Purpose

Replace manual article ideation with a repeatable workflow that surfaces:

- recurring questions from real consumers
- low-competition informational topics
- emerging concerns in health, supplements, and wellness
- evergreen authority opportunities for levnytt.se

---

## Research Sources

Use multiple independent sources in priority order:

1. **Google Autocomplete** — type seed keywords into Google and collect the suggested completions
2. **Google People Also Ask** — scrape PAA boxes for the top 3–5 SERP results
3. **Reddit** — mine r/Supplements, r/Nutrition, r/HealthyEating, r/Biohackers, r/SkincareAddiction, r/Sverige, r/Asksweddit for recurring questions
4. **Google Trends** — validate momentum and seasonality
5. **Perplexity research** — use Perplexity to surface related questions if available
6. **Existing LevNytt sitemap** — check against published pages to avoid duplication
7. **Competitor SERPs** — identify questions competitor authority pages rank for

---

## Workflow

### Step 1 — Discover recurring questions

Collect questions from all sources. Group similar phrasings together.

### Step 2 — Determine search intent

Classify each cluster as one of:

| Intent | Example |
|--------|---------|
| Informational | "Vad är Omega-3?" |
| Comparison | "Är fiskolja samma som Omega-3?" |
| Decision | "Ska jag ta Omega-3 eller inte?" |
| Troubleshooting | "Varför får jag hicka av Omega-3?" |
| Myth / misconception | "Är alla kosttillskott dyrt bajs?" |
| Scientific evidence | "Vad säger forskningen om Omega-3?" |
| Cost / value | "Är NeoLife värt priset?" |

### Step 3 — Estimate opportunity

For every topic cluster document:

- **Search intent** — from the classification above
- **Estimated difficulty** — Low / Medium / High (based on SERP competition)
- **Evergreen potential** — Low / Medium / High (will people ask this in 3 years?)
- **Authority potential** — Low / Medium / High (can LevNytt credibly own this?)
- **Internal linking opportunities** — list existing pages that could link to the new article

### Step 4 — Check existing LevNytt content

Search the sitemap and site inventory:

- If a matching page already exists → mark as **UPDATE EXISTING**
- Otherwise → **NEW ARTICLE**

### Step 5 — Cluster related questions

Group questions that belong to the same topic into one cluster.

**Example:**

Omega-3

```
- Does Omega-3 really work?
- How much Omega-3 should I take?
- Is fish oil the same as Omega-3?
- How long before Omega-3 works?
- Can you take too much Omega-3?
```

→ One content cluster.

### Step 6 — Rank opportunities

Assign a priority to every cluster:

- **A** — high search demand, high authority value, strategic fit
- **B** — moderate opportunity, useful but not urgent
- **C** — low priority, niche or low search volume

Priority is determined by both **search opportunity** and **strategic importance for LevNytt**. A lower-volume topic may still receive Priority A if it significantly strengthens internal linking, authority pages, EEAT, or an important content cluster.

### Step 7 — Strategic Fit

Evaluate how well each content opportunity strengthens the LevNytt ecosystem.

For every cluster determine:

| Field | Description |
|---|---|
| Supports Product Pages | Which existing product pages benefit from this article? |
| Supports Authority Pages | Which authority pages (NeoLife Vetenskap, Historia, Affärsmöjlighet, etc.) should receive internal links? |
| Supports Tools | Can this article naturally link to calculators, comparisons or future tools? |
| Builds Content Cluster | Does this expand an existing topic cluster or start a new one? |
| EEAT Value | Low / Medium / High |
| Long-term Strategic Value | Low / Medium / High |

The purpose is to prioritize articles that strengthen the entire LevNytt knowledge graph, not merely those with the highest search demand.

---

## Output Format

For every cluster produce the following block:

```
## Cluster

<name>

---

### Questions

- question 1
- question 2
- question 3

---

### Search intent

<classification>

---

### Why people ask this

<1–3 sentences explaining the consumer psychology or gap>

---

### Existing LevNytt pages

- linked page 1
- linked page 2
- (none)

---

### Suggested internal links

- /existing-slug
- /other-slug

---

### Suggested article titles (Swedish)

- title 1
- title 2

---

### Priority

A / B / C

---

### Publication Score

XX / 100

Score based on:

- Search Opportunity
- Strategic Fit
- Existing LevNytt Coverage
- EEAT Potential
- Internal Linking Value
- Cluster Importance
- Long-term Evergreen Value

<2–4 sentences explaining why the cluster received that score>

---

### Strategic Fit

- Supports Product Pages
- Supports Authority Pages
- Supports Tools
- Builds Content Cluster
- EEAT Value
- Long-term Strategic Value

---

### Recommended Content Type

<choose one: Informational Article, Authority Article, Product Pillar, Product Comparison, FAQ, Research Summary>

<1–2 sentence explanation of why this content type is the best choice>

---

### Recommendation

Write now | Update existing | Skip
```

---

## Rules

1. Do **not** generate article content.
2. Do **not** write HTML.
3. Do **not** create schema markup.
4. Only produce ranked editorial backlog entries.
5. Every output block must be self-contained and ready to hand to the Informational Article Skill.

---

## Integration

Output files from this skill should be saved as:

```
/docs/editorial-backlog/<topic-slug>-gap.md
```

Example: `/docs/editorial-backlog/omega-3-gap.md`

These files are consumed by the Informational Article Skill as the **Content Brief** input.

---

## Summary Table

Every backlog must end with a ranked summary table that includes:

| # | Cluster | Priority | Publication Score | Recommendation |
|---|---|---|---|---|
| 1 | Cluster name | A | 95/100 | Write now |
| 2 | Cluster name | B | 72/100 | Write now |

Sort the table by Publication Score descending. The top 3–5 entries are the immediate editorial backlog.

The Publication Score makes it immediately obvious which articles to publish next without requiring manual prioritization.
