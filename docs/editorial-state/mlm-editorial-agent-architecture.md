# MLM Editorial Agent — Architecture and Production Workflow

**Version:** 1.0  
**Date:** 2026-06-30  
**Agent:** `.opencode/agents/mlm-editorial-agent.md`

This document describes the MLM Editorial Agent's architecture, production workflows, and integration with the LevNytt editorial system.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│                    Editorial Sync Engine              │
│  (Canonical Producer — Repository Traversal HERE)    │
└───────────────────┬──────────────────────────────────┘
                    │ Generates
                    ▼
┌──────────────────────────────────────────────────────┐
│              Synchronized Editorial State             │
│  • production-status.md                              │
│  • publication-queue.md                              │
│  • repository-inventory.md                           │
│  • drift-detection.md                                │
└───────────────────┬──────────────────────────────────┘
                    │ Consumed by
                    ▼
┌──────────────────────────────────────────────────────┐
│                    MLM Brief V1.2                     │
│  (Industry & Editorial Intelligence)                 │
│  • Reads synchronized state                          │
│  • Identifies MLM-category topics                    │
│  • Routes to specialist agents                       │
└───────────────────┬──────────────────────────────────┘
                    │ Routes MLM topics
                    ▼
┌──────────────────────────────────────────────────────┐
│              MLM Editorial Agent V1.0                │
│  (Specialist Producer — MLM Domain)                  │
│  • Reads 8 MLM authority research files              │
│  • Produces neutral, evidence-based articles          │
│  • Never writes health/supplement content            │
└───────────────────┬──────────────────────────────────┘
                    │ Produces
                    ▼
┌──────────────────────────────────────────────────────┐
│              Publication Agent                        │
│  (Publishing — File Placement)                       │
└──────────────────────────────────────────────────────┘
```

---

## Production Workflow

### Phase 1: Topic Identification (MLM Brief)

1. **MLM Brief reads synchronized state**
   - `production-status.md` — full backlog with priority scores
   - `publication-queue.md` — pre-prioritized queue
   - `repository-inventory.md` — published page coverage

2. **MLM Brief identifies MLM-category topics**
   - Scans backlog for MLM-related clusters
   - Checks authority research status (CLEARED / BLOCKED)
   - Prioritizes by business impact and readiness

3. **MLM Brief routes topic to MLM Editorial Agent**
   - Topic category matches MLM routing table
   - Authority research is CLEARED
   - Human approval granted

### Phase 2: Content Production (MLM Editorial Agent)

1. **Read authority research files** (PRIMARY)
   - Identify relevant files from the 8 MLM authority research documents
   - Extract evidence, statistics, case studies, regulatory positions
   - Follow evidence hierarchy (Tier 1 preferred)

2. **Analyze existing coverage** (SECONDARY)
   - Review 7 published MLM pages for internal linking
   - Identify coverage gaps the new article should address
   - Build contextual link sequences

3. **Generate article** (PRODUCTION)
   - Follow informational-article structure (punchline, Key Takeaways, FAQ)
   - Apply MLM-specific writing rules (neutral, evidence-based, consumer-first)
   - Include risk disclosure and consumer rights information
   - Add LLM optimization (schema markup, question H2s, stat cards)

4. **Verify against MLM checklist** (QUALITY)
   - No promotional language
   - No income promises
   - No health content
   - Evidence hierarchy followed
   - Source types labeled
   - Internal links included

### Phase 3: Publishing (Publication Agent)

1. **File placement** — Place HTML file at root level
2. **Sitemap update** — Add new URL to sitemap.xml
3. **Sync state regeneration** — Run `sync-editorial-state.py` to update production-status.md

---

## Authority Research File Usage

### Primary Files (Always Read)

| File | When to Read | What to Extract |
|------|-------------|-----------------|
| `direct-selling-authority-research.md` | Any MLM/direct selling article | Definitions, legal framework, industry scope |
| `pyramid-schemes-authority-research.md` | MLM vs pyramid, red flags articles | Definitions, legal status, landmark cases |
| `income-disclosure-statements-authority-research.md` | Income, earnings, IDS articles | IDS analysis, misleading tactics, interpretation |

### Secondary Files (Read When Relevant)

| File | Trigger | What to Extract |
|------|---------|-----------------|
| `ftc-mlm-regulation-authority-research.md` | FTC, enforcement, legal cases | Case outcomes, regulatory positions |
| `mlm-compensation-plans-authority-research.md` | Compensation, commission articles | Plan types, legal implications |
| `swedish-consumer-protection-authority-research.md` | Swedish consumer rights | Marknadsföringslagen, cooling-off, ARN |
| `eu-consumer-protection-authority-research.md` | EU regulation, cross-border | Consumer Rights Directive, UCPD |
| `direct-selling-associations-authority-research.md` | Industry structure, ethics | WFDSA data, codes of ethics |

---

## Example Production Flow

### Scenario: Produce "Konsumenträtt vid MLM-köp"

**Step 1 — MLM Brief identifies topic**
- Reads `publication-queue.md` → finds "Konsumenträtt vid MLM-köp" (Priority B, Score 72, Authority CLEARED)
- Routes to MLM Editorial Agent

**Step 2 — MLM Editorial Agent reads authority research**
- Primary: `swedish-consumer-protection-authority-research.md` (Marknadsföringslagen, Distanslagen, ARN)
- Secondary: `eu-consumer-protection-authority-research.md` (Consumer Rights Directive, cooling-off)
- Supporting: `direct-selling-authority-research.md` (self-regulation, buy-back policies)

**Step 3 — MLM Editorial Agent analyzes existing coverage**
- `/direktforsaljning-fakta` — foundational MLM context
- `/mlm-rekrytering-social-press-taktiker` — social pressure context
- `/neolife-affarsmojlighet` — NeoLife-specific business context

**Step 4 — MLM Editorial Agent generates article**
- Title: "Konsumenträtt vid MLM-köp — returrätt, ångerrätt och anmälan"
- Structure: Punchline → Key Takeaways → Question H2s → FAQ → Schema
- Internal links: 4 contextual links to existing MLM content
- Risk disclosure: Documented consumer complaints, limitations of self-regulation
- Evidence: Tier 1 (Swedish law), Tier 2 (Konsumentverket guidance)

**Step 5 — Verification**
- ✅ No promotional language
- ✅ No health content
- ✅ Evidence hierarchy followed
- ✅ Consumer rights documented
- ✅ 4 internal links included
- ✅ FAQ section with real consumer questions

**Step 6 — Publication**
- File placed at root: `/mlm-konsumentratt-retur-angeratt.html`
- Sitemap updated
- Sync Engine regenerates production-status.md

---

## Integration with Editorial Commander

### Category Routing Decision Tree

```
Editorial Commander identifies topic
         ↓
   Check topic category
         ↓
   Is it MLM/Network Marketing/Direct Selling? ──YES──→ MLM Editorial Agent
         ↓
   Is it Consumer Protection (MLM context)? ──YES──→ MLM Editorial Agent
         ↓
   Is it FTC Regulation/Pyramid Schemes? ──YES──→ MLM Editorial Agent
         ↓
    Is it Health/Supplements/Nutrition? ──YES──→ LevNytt Writer (`.opencode/agents/levnytt-writer.md`)
         ↓
   Is it Product-specific (NeoLife)? ──YES──→ Product Editorial Agent
```

### Decision Criteria

| Criteria | MLM Editorial Agent | LevNytt Writer |
|----------|-------------------|----------------------|
| Topic involves MLM business model | ✅ Yes | ❌ No |
| Topic involves consumer rights (MLM) | ✅ Yes | ❌ No |
| Topic involves income/earnings (MLM) | ✅ Yes | ❌ No |
| Topic involves health claims | ❌ No | ✅ Yes |
| Topic involves supplement efficacy | ❌ No | ✅ Yes |
| Topic involves nutrition science | ❌ No | ✅ Yes |

---

## Future Extension Recommendations

### Phase 2: Additional Specialist Agents

1. **Product Editorial Agent** — Handles product-specific content (NeoLife product pages, comparisons, savings analysis)
2. **Pillar Page Agent** — Handles authority/pillar page updates and standardization
3. **SEO Optimization Agent** — Handles content refresh, keyword optimization, performance analysis

### Phase 3: Advanced Capabilities

1. **Competitor Analysis Agent** — Monitors competitor content and identifies gaps
2. **Performance Analytics Agent** — Analyzes published content performance and recommends updates
3. **Content Calendar Agent** — Plans seasonal content and editorial calendar

### Phase 4: Cross-Agent Coordination

1. **Unified Topic Graph** — Shared knowledge graph across all specialist agents
2. **Cross-Reference Engine** — Automatic internal linking suggestions across topic domains
3. **Content Freshness Monitor** — Tracks content age and recommends updates based on regulatory changes

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-30 | Initial architecture documentation. Production workflow defined. Authority research file usage mapped. Example production flow documented. Category routing rules established. Future extension recommendations provided. |
