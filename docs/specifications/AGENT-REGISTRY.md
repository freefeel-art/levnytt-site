# LevNytt Agent Registry

**Version:** 1.0  
**Date:** 2026-06-30  
**Purpose:** Canonical registry of all production agents in the LevNytt editorial system

This document is the official registry of all agents implemented in the LevNytt editorial system. All agents are located in `.opencode/agents/` and follow OpenCode agent specification format.

---

## Production Agent Inventory

| # | Agent Name | File | Version | Status | Purpose |
|---|------------|------|---------|--------|---------|
| 1 | Editorial Commander | `editorial-commander.md` | V1.2 | **Production** | Orchestration layer — repository analysis, coverage gaps, authority checks, production recommendations |
| 2 | Morning Brief | `morning-brief.md` | V2.0 | **Production** | Consumer intelligence — external signals, trending topics, content opportunities |
| 3 | MLM Brief | `mlm-brief.md` | V1.2 | **Production** | Industry intelligence — editorial backlog, authority research, MLM/regulatory pipeline |
| 4 | MLM Editorial Agent | `mlm-editorial-agent.md` | V1.0 | **Production** | Specialist content producer — MLM, network marketing, consumer protection, FTC regulation |
| 5 | Publication Agent | `publication-agent.md` | V1.0 | **Production** | Deployment — copies source articles from content/articles/ to production root |
| 6 | LevNytt Writer | `levnytt-writer.md` | V1.0 | **Production** | Informational article writer — health, supplements, nutrition, wellness. Based on original LLM-Optimized Informational Article Generator. Produces PUBLICATION-ARTICLE-STANDARD-compliant HTML |

**Total Production Agents:** 6

---

## Agent Responsibilities

### 1. Editorial Commander V1.2
- **Type:** Orchestration Agent
- **Scope:** Entire editorial system
- **Primary Function:** Daily repository analysis and production recommendations
- **Triggers:** Manual execution before any production work
- **Key Responsibilities:**
  - Repository inventory (published pages, source articles, support files)
  - Coverage analysis against gap reports
  - Authority research status validation
  - Drift detection (outdated gap reports, ready-to-publish items)
  - Production queue prioritization
  - Single next-action recommendation
- **Never Does:** Write articles, edit content, perform research, publish content
- **Outputs:** Dated Editorial Brief in `docs/editorial-briefs/`

### 2. Morning Brief V2.0
- **Type:** Intelligence Agent (Consumer)
- **Scope:** External market signals
- **Primary Function:** Consumer demand discovery and content opportunity identification
- **Triggers:** `Run Morning Brief`
- **Key Responsibilities:**
  - Google Trends analysis (Swedish health topics)
  - Reddit mining (r/sweden, r/Supplements, r/Biohackers)
  - Google Autocomplete signal capture
  - Question-intent analysis (proxy for People Also Ask)
  - Coverage gap detection (consumer perspective)
  - Consumer opportunity prioritization
- **Never Does:** Editorial backlog analysis, authority research, content production
- **Outputs:** Consumer intelligence brief with content recommendations

### 3. MLM Brief V1.2
- **Type:** Intelligence Agent (Industry)
- **Scope:** Editorial pipeline and MLM/regulatory industry
- **Primary Function:** Editorial backlog analysis and industry intelligence
- **Triggers:** `Run MLM Brief`
- **Key Responsibilities:**
  - Authority research coverage analysis
  - Editorial backlog status tracking
  - Production pipeline monitoring
  - MLM/regulatory topic identification
  - Category routing to specialist agents
  - Editorial action prioritization
- **Never Does:** External signal analysis, consumer trend research, content production
- **Outputs:** Industry intelligence brief with editorial recommendations

### 4. MLM Editorial Agent V1.0
- **Type:** Specialist Content Producer
- **Scope:** MLM, network marketing, direct selling, consumer protection
- **Primary Function:** Evidence-based educational content production
- **Triggers:** `Run MLM Editorial Agent` or Editorial Commander routing
- **Key Responsibilities:**
  - Authority research synthesis (8 MLM research files)
  - Neutral, evidence-based article generation
  - Consumer protection focus
  - Risk disclosure and balanced perspective
  - Internal linking to existing MLM content
  - LLM optimization (schema, FAQ, question H2s)
- **Never Does:** Health content, promotional MLM content, income promises
- **Outputs:** Complete HTML articles with schema markup

### 5. Publication Agent V1.0
- **Type:** Deployment Agent
- **Scope:** Content publishing pipeline
- **Primary Function:** Deploy completed source articles to production
- **Triggers:** `publish`, `deploy`, `run publication agent`, READY TO PUBLISH references
- **Key Responsibilities:**
  - Copy source articles from `content/articles/` to root
  - Product entity reference validation
  - Brand asset verification
  - Production status updates
  - Git commit and push automation
- **Never Does:** Content creation, content editing, content modification
- **Outputs:** Published root HTML files, updated production-status.md

### 6. LevNytt Writer V1.0
- **Type:** Specialist Content Producer (Informational Articles)
- **Scope:** Health, supplements, nutrition, wellness, healthy aging
- **Primary Function:** LLM-optimized informational article production
- **Triggers:** Editorial Commander's "Run Informational Article" recommendation
- **Key Responsibilities:**
  - Web research, sitemap mining, LSI entity clustering
  - GPT Image 2 hero + infographic generation
  - PUBLICATION-ARTICLE-STANDARD-compliant HTML output
  - Authority Content Mode (evidence hierarchy, no treatment claims, tier-labeled citations)
  - Brand Design System compliance (colors, typography, LV Mark)
  - Product Entity System integration for product references
  - Internal linking following LevNytt Contextual Link Intelligence
  - Verification against combined SEO + LLM-optimization checklist
- **Never Does:** MLM content (routes to MLM Editorial Agent), promotional content, income claims
- **Outputs:** Complete HTML articles in `content/articles/[slug]/`

## Agent Workflow Architecture

```
┌─────────────────────┐
│  Editorial Sync     │ ← Repository traversal happens HERE
│  Engine             │
└─────────┬───────────┘
          │ Generates
          ▼
┌─────────────────────┐
│  Synchronized       │ ← Canonical editorial state
│  Editorial State    │
└─────────┬───────────┘
          │ Consumed by
          ▼
┌─────────────────────┐
│  Editorial          │ ← Daily orchestration
│  Commander          │
└─────────┬───────────┘
          │ Routes & Recommends
          ▼
┌─────────────────────┐    ┌─────────────────────┐
│  Morning Brief      │    │  MLM Brief          │ ← Parallel intelligence
│  (Consumer)         │    │  (Industry)         │
└─────────┬───────────┘    └─────────┬───────────┘
          │                          │ Routes MLM topics
          │                          ▼
          │                ┌─────────────────────┐
          │                │  MLM Editorial      │ ← Specialist producer
          │                │  Agent              │
          │                └─────────┬───────────┘
          │                          │
          │                          ▼
          │                ┌─────────────────────┐
          │                │  LevNytt Writer     │ ← Informational article
          │                │  (Health/Supplements)│   producer
          │                └─────────┬───────────┘
          │                          │
          ▼                          ▼
┌─────────────────────────────────────────────────┐
│              Publication Agent                   │ ← Deployment
│              (All content types)                 │
└─────────────────────────────────────────────────┘
```

---

## Category Routing Rules

The Editorial Commander and MLM Brief use these rules to route topics to appropriate specialist agents:

### MLM Editorial Agent Routes
| Topic Category | Example Keywords | Route To |
|---|---|---|
| MLM / Network Marketing | "What is MLM?", "How does network marketing work?" | **MLM Editorial Agent** |
| Direct Selling | "Direct selling vs retail", "WFDSA statistics" | **MLM Editorial Agent** |
| Compensation Plans | "Binary vs unilevel", "How MLM commissions work" | **MLM Editorial Agent** |
| Income Disclosure | "How to read IDS", "Realistic MLM earnings" | **MLM Editorial Agent** |
| Consumer Protection (MLM) | "MLM return rights", "Cooling-off period" | **MLM Editorial Agent** |
| FTC Regulation | "FTC vs Herbalife", "FTC 2024 MLM alert" | **MLM Editorial Agent** |
| Pyramid Schemes | "MLM vs pyramid", "Pyramid scheme red flags" | **MLM Editorial Agent** |
| Company Comparisons | "Amway vs NeoLife", "MLM company history" | **MLM Editorial Agent** |
| Recruitment Tactics | "Social pressure in MLM", "How to say no" | **MLM Editorial Agent** |

### LevNytt Writer Routes (Health / Supplement / Nutrition)
| Topic Category | Example Keywords | Route To |
|---|---|---|
| Health / Supplements | "Vitamin D deficiency", "Omega-3 benefits" | **LevNytt Writer** |
| Nutrition Science | "Probiotics for gut health", "Magnesium forms" | **LevNytt Writer** |
| Medical Research | "Clinical trials", "Systematic reviews" | **LevNytt Writer** |
| Wellness / Healthy Aging | "Anti-aging nutrients", "Longevity supplements" | **LevNytt Writer** |
| Informational / Explainer | "How does X work", "What is X" | **LevNytt Writer** |

---

## Agent Permissions

| Agent | Edit Files | WebFetch | WebSearch | Repository Access |
|---|---|---|---|---|---|
| Editorial Commander | ❌ Deny | ❌ Deny | ❌ Deny | ✅ Read-only |
| Morning Brief | ❌ Deny | ✅ Allow | ❌ Deny | ✅ Read-only |
| MLM Brief | ❌ Deny | ❌ Deny | ❌ Deny | ✅ Read-only |
| MLM Editorial Agent | ❌ Deny | ✅ Allow | ❌ Deny | ✅ Read-only |
| LevNytt Writer | ❌ Deny | ✅ Allow | ✅ Allow | ✅ Read-only |
| Publication Agent | ✅ Allow | ❌ Deny | ❌ Deny | ✅ Read-write |

**Security Note:** Only the Publication Agent has file modification permissions. All content production agents generate output that must be manually saved or deployed via the Publication Agent.

---

## Execution Rules

### Daily Workflow
1. **Editorial Commander** runs first (mandatory)
2. **Morning Brief** and **MLM Brief** run in parallel (recommended)
3. **Human approval** required before content production
4. **Specialist agents** (MLM Editorial Agent) produce content when routed
5. **Publication Agent** deploys completed content

### Agent Invocation
- **Manual triggers:** All agents require explicit user command
- **No automatic execution:** Agents never invoke other agents automatically
- **Human approval gate:** Content production requires explicit user approval
- **Single recommendation:** Each agent recommends exactly one primary action

### Content Production Rules
- **Never write promotional content:** All content must be educational and neutral
- **Evidence hierarchy required:** All claims must trace to cited sources
- **Consumer protection focus:** MLM content must include risk disclosure and consumer rights
- **Internal linking mandatory:** Minimum 3-5 contextual links to existing content
- **Schema markup required:** All articles include Article + FAQPage structured data

---

## Integration with Editorial Sync Engine

All agents consume synchronized editorial state generated by the Editorial Sync Engine rather than performing redundant repository traversal:

### Consumed Synchronized Files
| Generated File | Consumers | Purpose |
|---|---|---|
| `docs/editorial-backlog/production-status.md` | MLM Brief, Editorial Commander | Backlog status, priority scores, authority research status |
| `docs/reports/publication-queue.md` | MLM Brief | Pre-prioritized editorial queue |
| `docs/reports/repository-inventory.md` | Morning Brief, MLM Brief | Published page inventory by category |
| `docs/reports/drift-detection.md` | Editorial Commander | Content drift, stale gap reports |

### Canonical Rule
**Never inspect the repository directly if synchronized editorial state exists.**

Repository traversal is only permitted when synchronized state cannot answer the agent's specific question.

---

## Future Agent Roadmap

### Phase 2: Additional Specialist Agents
1. ~~**Health Editorial Agent**~~ — **SUPERSEDED by LevNytt Writer** (Sprint 10). All health/supplement/nutrition informational articles are now handled by LevNytt Writer.
2. **Product Editorial Agent** — NeoLife product pages, comparisons, savings analysis
3. **Pillar Page Agent** — Authority page updates and standardization

### Phase 3: Advanced Capabilities
1. **SEO Optimization Agent** — Content refresh, keyword optimization, performance analysis
2. **Content Calendar Agent** — Seasonal content planning and editorial scheduling
3. **Analytics Agent** — Performance analysis and update recommendations

### Phase 4: Cross-Agent Coordination
1. **Topic Graph Engine** — Shared knowledge graph across specialist agents
2. **Cross-Reference Engine** — Automatic internal linking suggestions
3. **Content Freshness Monitor** — Age tracking and regulatory change updates

---

## Validation Checklist

**For Agent Implementation:**
- [ ] Agent file exists in `.opencode/agents/`
- [ ] Proper OpenCode agent format (YAML frontmatter + markdown)
- [ ] Listed in this registry with correct version and status
- [ ] Permissions properly configured
- [ ] Integration with Editorial Sync Engine documented
- [ ] Category routing rules defined (if applicable)
- [ ] Authority research files mapped (if applicable)

**For Agent Updates:**
- [ ] Version number incremented in agent file
- [ ] Registry updated with new version
- [ ] Change documented in agent's version history
- [ ] Architecture documentation updated if workflow changes
- [ ] Integration impacts assessed and documented

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-30 | Initial agent registry. 5 production agents catalogued: Editorial Commander V1.2, Morning Brief V2.0, MLM Brief V1.2, MLM Editorial Agent V1.0, Publication Agent V1.0. Architecture workflows documented. Category routing rules defined. Integration with Editorial Sync Engine specified. |
| 1.1 | 2026-06-30 | Sprint 10 — LevNytt Writer V1.0 registered (agent #6). Workflow diagram updated. Health/Supplement/Nutrition routing moved from "Future Health Editorial Agent" to LevNytt Writer. Agent permissions table updated. Future roadmap updated. |

---

## References

- **Editorial State Interface:** `docs/editorial-state/README.md`
- **Morning Brief Architecture:** `docs/specifications/MORNING-BRIEF-ARCHITECTURE.md`
- **Editorial Sync Engine:** `docs/specifications/EDITORIAL-SYNC-ENGINE.md`
- **MLM Agent Architecture:** `docs/editorial-state/mlm-editorial-agent-architecture.md`
- **MLM Authority Mapping:** `docs/editorial-state/mlm-authority-source-mapping.md`