# LevNytt — Authority Research Skill

Build LevNytt's internal knowledge base from authoritative, historical, and primary sources **before** article generation.

This skill is **not** an SEO tool.

This skill is **not** a Question Gap replacement.

Its purpose is to answer:

> What should a reader know before forming an opinion?

rather than:

> What are people searching for?

---

## Purpose

Authority Research produces a factual foundation for LevNytt authority articles. It gathers, evaluates, and structures evidence from high-quality sources so that later writing can be source-first, transparent, and durable.

The skill supports **any topic**, not only network marketing. It is repeatable, neutral, and consumer-first.

---

## Mission

Answer:

> What should a reader know before forming an opinion?

This means:

- Establish what is documented before interpreting it.
- Separate fact from opinion.
- Surface contradictory evidence, not only supporting evidence.
- Provide historical context so readers understand *why* a topic matters.
- Identify what is unknown, uncertain, or contested.

---

## Research Philosophy

The skill prioritizes **evidence quality over popularity**.

- Popularity is never considered evidence.
- Community discussions may identify myths and recurring objections, but they must never define factual conclusions.
- Authority comes from source quality, not from repetition.
- Every conclusion must be traceable to a specific source.
- Uncertainty must be stated explicitly.

---

## Research Pyramid

Sources are evaluated in tiers. Work from the top down. Use lower tiers only when higher-tier evidence is unavailable or to understand perception gaps.

### Tier 1 — Primary Authorities

**Highest priority.**

These sources create, enforce, or document factual reality.

| Source type | Examples |
|---|---|
| Government agencies | FTC, Konsumentverket, Livsmedelsverket, FDA, EFSA |
| Courts and legal decisions | Patent- och marknadsdomstolen, FTC v. Amway (1979), Herbalife FTC settlement (2016) |
| Regulatory bodies | EU Commission, Konsumentombudsmannen, Finansinspektionen |
| Peer-reviewed research | PubMed, Google Scholar, institutional repositories |
| Official legislation | EU regulation, Swedish law, Marknadsföringslagen (2008:486) |
| Official company documentation | Annual reports, SEC filings, official policies, income disclosure statements |
| Historical source documents | Founding documents, court transcripts, original publications |

**How to use:**

- Start every research project here.
- Download or archive the source where possible.
- Note date, version, and jurisdiction.
- Distinguish between a raw document and a press summary.

---

### Tier 2 — Historical Industry Sources

Research the development of the industry or field itself.

| Source type | Examples |
|---|---|
| Industry history | Direct selling evolution, MLM milestones, trade association archives |
| Landmark cases | Amway 1979, Herbalife 2016, major EU rulings |
| Historical business models | Early catalog sales, door-to-door, party plan, digital direct sales |
| Consumer protection evolution | How regulation developed in response to abuse |

**How to use:**

- Build timelines.
- Identify cause-and-effect relationships.
- Show readers how current practices emerged.
- Avoid presentism: evaluate events in their historical context.

---

### Tier 3 — Influential Industry Figures

Study individuals who have significantly influenced the field.

The purpose is **understanding historical development**.

Examples:

- Jim Rohn
- Eric Worre
- Richard Bliss Brooke
- Jerry Brassfield
- Carl Rehnborg
- Jay Van Andel
- Rich DeVos

**How to use:**

- Identify claims they made.
- Identify supporting evidence for those claims.
- Identify limitations and conflicts of interest.
- Separate documented facts from personal philosophy or motivational framing.
- Never treat their opinions as facts.

---

### Tier 4 — Community Evidence

Use last. Use carefully.

| Source type | Examples |
|---|---|
| Reddit | r/antiMLM, r/Supplements, r/Nutrition, r/Sverige |
| Forums | Flashback, health forums, business forums |
| Facebook groups | Distributor groups, customer groups |
| Quora | Question threads, anecdotal answers |

**Purpose:**

- Identify myths.
- Surface recurring questions.
- Map misconceptions.
- Understand emotional objections.

**Rules:**

- Never use community consensus as factual evidence.
- Always verify claims against Tier 1–3 sources.
- Treat anecdotes as signals, not proof.
- Note bias: communities self-select for strong opinions.

---

## Authority Profiles Library

Authority Profiles are reusable, evidence-based evaluations of influential people, organizations, and institutions relevant to LevNytt.

They are **not biographies** and **not hero pages**. Their purpose is to separate documented facts, historical influence, philosophy, and conflicts of interest so future research and articles do not have to reconstruct the same background every time.

### Location

```
/docs/research/authority-profiles/
```

### When to use Authority Profiles

- When a research topic involves a person or organization already profiled.
- When evaluating claims made by industry figures, educators, or institutions.
- When assessing conflicts of interest or potential bias.
- When writing historical context for an authority article.

### How Authority Research uses Authority Profiles

1. Before researching a topic, check whether relevant Authority Profiles already exist.
2. If they exist, import the profile's Identity, Historical Importance, Major Contributions, Conflicts of Interest, and Reliability Assessment into the research report.
3. Do not duplicate the profile content. Reference the profile file and summarize only what is relevant to the current research question.
4. If a relevant authority is not yet profiled, consider creating a placeholder profile as part of the research output.

### Profile categories

| Category | Purpose | Examples |
|---|---|---|
| Regulatory & Scientific Authorities | Government, regulatory, and scientific bodies | FTC, EFSA, PubMed, Konsumentverket, WFDSA |
| Business Philosophy | Long-term thinking, value creation, decision quality | Warren Buffett, Charlie Munger, Richard Branson, Peter Drucker |
| Leadership | Leadership, personal development, communication | Jim Rohn, John C. Maxwell, Stephen Covey |
| Direct Selling History | Historical development of direct selling | Carl Rehnborg, Jay Van Andel, Rich DeVos, Jerry Brassfield |
| Network Marketing Education | Professional education and sales systems | Eric Worre, Richard Bliss Brooke |

### Profile structure

See the template:

```
/docs/research/authority-profiles/_template.md
```

---

## Workflow

### Step 1 — Define the research question

State the question in reader terms, not keyword terms.

Examples:

- "What should a reader know about the legal status of MLM in Sweden?"
- "What does the evidence actually say about Omega-3 and heart health?"
- "What is the documented history of NeoLife's scientific advisory board?"

### Step 2 — Search Tier 1 sources

- Identify relevant government agencies, regulators, courts, and peer-reviewed databases.
- Collect primary documents.
- Record URLs, archive links, publication dates, and document versions.

### Step 3 — Search Tier 2 sources

- Build a historical timeline.
- Identify landmark events, cases, and industry milestones.
- Note how practice evolved in response to regulation.

### Step 4 — Search Tier 3 sources and Authority Profiles

- Identify influential figures and organizations.
- Check whether relevant Authority Profiles already exist in `/docs/research/authority-profiles/`.
- If a profile exists, import its Reliability Assessment, Major Contributions, and Conflicts of Interest.
- If no profile exists, document the authority's claims and evidence, and consider creating a placeholder profile.
- Note conflicts of interest.

### Step 5 — Search Tier 4 sources (if useful)

- Mine communities for myths, objections, and recurring questions.
- Cross-check every claim against Tier 1–3 sources.

### Step 6 — Evaluate evidence

For every important claim, build an Evidence Matrix entry.

### Step 7 — Assess confidence

Assign a confidence level to every conclusion.

### Step 8 — Identify article opportunities

Based on the research, suggest which facts should become articles.

### Step 9 — Map internal links

Identify existing LevNytt pages that should link to the new authority content.

---

## Required Output

Every Authority Research report must include the following sections.

### 1. Executive Summary

- Topic and research question
- Key conclusion in 2–4 sentences
- Highest-confidence finding
- Biggest uncertainty or contradiction

### 2. Historical Timeline

| Date | Event | Significance | Source |
|---|---|---|---|
| 1979 | FTC v. Amway | Established legal distinction for MLM | FTC |
| 2016 | Herbalife FTC settlement | $200M settlement, restructuring of compensation | FTC |
| ... | ... | ... | ... |

### 3. Primary Sources

List all Tier 1 sources used.

For each:

- Title
- Author / publisher
- Date
- URL or archive link
- What it was used for

### 4. Key Facts

A numbered list of verified facts.

Each fact should be:

- Specific
- Sourced
- Limited to what the evidence actually shows

### 5. Common Myths

List misconceptions found in communities or popular discourse.

For each myth:

- The myth
- Why it persists
- What the evidence actually says
- Source

### 6. Evidence Matrix

| Claim | Evidence | Source type | Confidence | Notes |
|---|---|---|---|---|
| MLM is legal in Sweden when income derives primarily from product sales | Marknadsföringslagen, FTC v. Amway, Konsumentverket guidance | Tier 1 | High | Applies to legitimate MLM; pyramid schemes remain illegal |
| 79% of LifeWave active distributors earned nothing in 2024 | Company income disclosure statement, FTC 2024 report | Tier 1 | High | Single-company figure; not universal |
| "Everyone can succeed in MLM" | Motivational claim by industry trainers | Tier 3 | Low / Misleading | Contradicted by income disclosure data |

### 7. Contradictory Evidence

Explicitly surface evidence that does not fit the main narrative.

| Finding | Source | Why it matters |
|---|---|---|
| Some distributors report positive experiences | Anecdotal reports, company testimonials | Does not contradict aggregate income data; shows individual outcomes vary |
| MLM industry reports growth in wellness sector | WFDSA Global Report | Growth in sales volume does not imply distributor profitability |

### 8. Consensus Assessment

Summarize the state of agreement among credible sources.

- **Strong consensus:** Multiple Tier 1 sources agree.
- **Partial consensus:** Agreement with noted limitations or context.
- **Active debate:** Credible sources disagree; explain both sides.
- **Insufficient evidence:** Not enough high-quality evidence to conclude.

### 9. Research Confidence

For every major conclusion, assign:

- **High** — supported by multiple Tier 1 sources, little contradiction.
- **Moderate** — supported by Tier 1–2 sources, some limitations or context needed.
- **Low** — limited evidence, conflicting sources, or heavy reliance on Tier 3–4.

Include a one-sentence explanation for each confidence rating.

### 10. Recommended Article Opportunities

Based on the research, recommend articles that would help readers understand the topic.

For each:

- Working title
- Recommended content type (Authority Article, Research Summary, FAQ, Timeline, Comparison)
- Why it matters
- Key sources to use
- Suggested internal links

### 11. Internal Linking Opportunities

List existing LevNytt pages that should link to the new authority content.

| Existing page | Why it should link |
|---|---|---|
| `/direktforsaljning-fakta` | Could link to a new income-disclosure article |
| `/neolife-vetenskap` | Could link to a new evidence-review article |

### 12. Authority Profile Assessment

If the topic involves people, organizations, or institutions covered by Authority Profiles, include this section.

For each relevant profile:

- Profile file path
- Why the authority is relevant to this research
- Reliability Assessment (High / Moderate / Low)
- How the profile should influence the article (historical context, business philosophy, conflict-of-interest note, not suitable as evidence, etc.)

Example:

```
| Authority | Profile | Relevance | Reliability | Usage note |
|---|---|---|---|---|
| FTC | /docs/research/authority-profiles/ftc.md | Legal/regulatory framework for MLM | High | Primary authority; cite directly |
| Eric Worre | /docs/research/authority-profiles/eric-worre.md | Network marketing education philosophy | Low as evidence | Historical/educational context only; not scientific or regulatory proof |
```

If a relevant authority does not yet have a profile, note the gap and consider creating a placeholder profile.

---

## Evidence Matrix Rules

Every important claim in the report must be represented in the Evidence Matrix.

| Field | Requirement |
|---|---|
| Claim | A single, falsifiable statement |
| Evidence | The specific document, study, or source supporting it |
| Source type | Tier 1, Tier 2, Tier 3, or Tier 4 |
| Confidence | High / Moderate / Low |
| Notes | Limitations, caveats, or contradictions |

Claims without evidence are not allowed in the Key Facts section.

---

## Research Confidence Definitions

### High

- Multiple independent Tier 1 sources support the conclusion.
- Evidence is current and relevant to the target jurisdiction.
- Little or no credible contradictory evidence exists.

**Example:** *"Legitimate MLM is legal in Sweden; pyramid schemes are illegal."* Supported by Marknadsföringslagen, EU consumer protection directives, and FTC guidance.

### Moderate

- Supported by Tier 1 or strong Tier 2 sources.
- Some limitations apply: older data, narrow sample, or jurisdictional differences.
- Minor contradictions exist but do not overturn the conclusion.

**Example:** *"Most MLM distributors earn little or no profit."* Supported by FTC analysis of 70 companies, but percentages vary by company and year.

### Low

- Limited evidence available.
- Heavy reliance on Tier 3–4 sources.
- Significant contradictions or gaps remain.

**Example:** *"Supplement MLMs consistently produce higher-quality products than retail brands."* Often asserted by companies, but peer-reviewed comparative data is scarce and company-funded.

---

## Relationship to Other Skills

```
Authority Profiles
        ↓
Authority Research Skill
        ↓
Question Gap
        ↓
Informational Article Skill
```

- **Authority Profiles** provide reusable evaluations of people, organizations, and institutions.
- **Question Gap** identifies *what readers ask*.
- **Authority Research** identifies *what readers should know*.
- **Informational Article** combines both into publishable content.

The Authority Research Skill becomes the primary factual input for authority articles. Authority Profiles become reusable references throughout the LevNytt ecosystem.

---

## Output File Naming

Save Authority Research reports as:

```
/docs/research/<topic-slug>-authority-research.md
```

Example:

```
/docs/research/mlm-authority-research.md
/docs/research/omega-3-authority-research.md
```

If the research feeds a specific planned article, cross-reference the backlog file:

```
Related backlog: docs/editorial-backlog/<topic-slug>-gap.md
```

---

## Design Principles

| Principle | Meaning |
|---|---|
| **Neutral** | No promotional framing. No defensive framing. Let evidence speak. |
| **Transparent** | Sources are listed. Limitations are stated. Confidence is explicit. |
| **Repeatable** | Any researcher following the skill should reach similar factual conclusions. |
| **Source-first** | Evidence is collected before conclusions are written. |
| **Evidence before conclusions** | Claims must exist in the Evidence Matrix before they appear in Key Facts. |
| **History before opinion** | Historical context is established before evaluating current claims. |
| **Consumer-first** | The reader's need to understand outweighs any party's messaging goals. |

---

## Rules

1. Do **not** write article content.
2. Do **not** write HTML.
3. Do **not** create schema markup.
4. Do **not** treat popularity, search volume, or community consensus as evidence.
5. Do **not** rely on press releases or company blogs as Tier 1 sources.
6. Every Key Fact must appear in the Evidence Matrix.
7. Every conclusion must have a confidence rating with explanation.
8. Contradictory evidence must be surfaced, not hidden.
9. Community sources are allowed only for myth identification and must be cross-checked.
10. The final report must be usable as the factual input for an Informational Article or Authority Article.

---

## When to Use This Skill

| Scenario | Use Authority Research? |
|---|---|
| Writing a factual explainer on a regulated topic | Yes |
| Addressing a controversial or myth-heavy topic | Yes |
| Building a historical timeline | Yes |
| Evaluating health, finance, or legal claims | Yes |
| Simple product description | No (use product page template) |
| Keyword-driven listicle | No (use Question Gap + Informational Article) |
| Pure SEO content | No |

---

## Quick-Start Checklist

Before closing an Authority Research report, verify:

- [ ] Research question is stated in reader terms.
- [ ] Tier 1 sources were searched first.
- [ ] Relevant Authority Profiles were checked in `/docs/research/authority-profiles/`.
- [ ] Historical timeline includes dates, events, and sources.
- [ ] Every Key Fact is backed by the Evidence Matrix.
- [ ] Common Myths section includes source-based corrections.
- [ ] Contradictory Evidence is surfaced.
- [ ] Consensus Assessment is included.
- [ ] Research Confidence is assigned to major conclusions.
- [ ] Authority Profile Assessment is included when relevant.
- [ ] Article opportunities are suggested.
- [ ] Internal linking opportunities are mapped.
- [ ] No article content, HTML, or schema was generated.
