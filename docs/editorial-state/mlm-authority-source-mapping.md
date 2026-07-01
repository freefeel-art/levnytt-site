# MLM Editorial Agent — Authority Source Mapping

**Version:** 1.0  
**Date:** 2026-06-30  
**Agent:** `.opencode/agents/mlm-editorial-agent.md`

This document maps every MLM authority research file to the topics it covers, the questions it can answer, and the content gaps it fills.

---

## Authority Research File Inventory

| # | File | Topic | Confidence | Date | Covers |
|---|------|-------|-----------|------|--------|
| 1 | `direct-selling-authority-research.md` | Direct selling as distribution channel | Moderate | 2026-06-29 | Definitions, legal framework, industry scope, WFDSA data, consumer protection |
| 2 | `direct-selling-associations-authority-research.md` | Trade bodies and self-regulation | Moderate | 2026-06-29 | WFDSA, Seldia, national DSAs, ethics codes, industry statistics |
| 3 | `pyramid-schemes-authority-research.md` | Pyramid scheme identification | High | 2026-06-29 | Definitions, legal status, red flags, landmark cases, Swedish/EU context |
| 4 | `ftc-mlm-regulation-authority-research.md` | FTC regulation and enforcement | High | 2026-06-29 | FTC authority, landmark cases (Amway, Herbalife, Vemma), rules, guidance |
| 5 | `mlm-compensation-plans-authority-research.md` | Compensation structures | Moderate | 2026-06-29 | Plan types (unilevel, binary, matrix, breakaway, stairstep), legal implications |
| 6 | `income-disclosure-statements-authority-research.md` | IDS analysis and interpretation | High | 2026-06-29 | IDS content, misleading tactics, how to read them, regulatory requirements |
| 7 | `swedish-consumer-protection-authority-research.md` | Swedish legal framework | High | 2026-06-29 | Marknadsföringslagen, Distanslagen, Konsumentverket, ARN, cooling-off rights |
| 8 | `eu-consumer-protection-authority-research.md` | EU consumer protection | High | 2026-06-29 | Consumer Rights Directive, UCPD, distance selling, health claims regulation |

---

## Topic-to-File Mapping

### MLM Definitions and Mechanics
- **Primary:** `direct-selling-authority-research.md`
- **Secondary:** `mlm-compensation-plans-authority-research.md`
- **Supporting:** `pyramid-schemes-authority-research.md` (for MLM vs pyramid distinction)

### Income and Earnings
- **Primary:** `income-disclosure-statements-authority-research.md`
- **Secondary:** `mlm-compensation-plans-authority-research.md` (for compensation mechanics)
- **Supporting:** `ftc-mlm-regulation-authority-research.md` (FTC 2024 Consumer Alert data)

### Consumer Protection and Rights
- **Primary:** `swedish-consumer-protection-authority-research.md`
- **Secondary:** `eu-consumer-protection-authority-research.md`
- **Supporting:** `direct-selling-authority-research.md` (self-regulation aspects)

### Regulation and Enforcement
- **Primary:** `ftc-mlm-regulation-authority-research.md`
- **Secondary:** `swedish-consumer-protection-authority-research.md`
- **Supporting:** `eu-consumer-protection-authority-research.md`

### Pyramid Scheme Education
- **Primary:** `pyramid-schemes-authority-research.md`
- **Secondary:** `ftc-mlm-regulation-authority-research.md` (landmark cases)
- **Supporting:** `direct-selling-authority-research.md` (legal boundary)

### Industry Structure and Associations
- **Primary:** `direct-selling-associations-authority-research.md`
- **Secondary:** `direct-selling-authority-research.md`
- **Supporting:** `mlm-compensation-plans-authority-research.md`

### Company Comparisons and History
- **Primary:** `ftc-mlm-regulation-authority-research.md` (enforcement cases)
- **Secondary:** `direct-selling-authority-research.md` (industry history)
- **Supporting:** `direct-selling-associations-authority-research.md` (membership data)

### Recruitment and Social Dynamics
- **Primary:** `income-disclosure-statements-authority-research.md` (incentive structures)
- **Secondary:** `mlm-compensation-plans-authority-research.md` (rank/pin pressure)
- **Supporting:** `swedish-consumer-protection-authority-research.md` (aggressive practices law)

### Ethics and Self-Regulation
- **Primary:** `direct-selling-associations-authority-research.md` (codes of ethics)
- **Secondary:** `ftc-mlm-regulation-authority-research.md` (regulatory enforcement)
- **Supporting:** `swedish-consumer-protection-authority-research.md` (legal standards)

---

## Evidence Hierarchy

The MLM Editorial Agent must follow this evidence hierarchy when building articles:

| Tier | Source Types | Examples |
|------|-------------|----------|
| **Tier 1** | Court decisions, regulatory enforcement actions, peer-reviewed MLM research | FTC v. Amway, FTC v. Herbalife, BurnLounge case, Journal of Consumer Affairs studies |
| **Tier 2** | FTC guidance, Konsumentverket publications, official IDS documents | FTC 2024 Consumer Alert, Business Opportunity Rule, company IDS filings |
| **Tier 3** | Academic commentary, industry reports (with bias disclosure) | WFDSA Global STATS, academic papers on MLM economics |
| **Tier 4** | Company materials, distributor testimonials | Company compensation plan documents, income testimonials (label as marketing) |
| **❌ Never** | Unverified claims, anonymous anecdotes, recruitment promises | Social media earnings claims, "success story" testimonials without verification |

---

## External Source Policy

The MLM Editorial Agent may fetch external sources **only when repository authority research is insufficient**. Approved external sources:

### Approved External Sources
- **FTC.gov** — Consumer alerts, enforcement actions, guidance documents
- **Konsumentverket.se** — Swedish consumer protection guidance
- **Patent- och marknadsdomstolen** — Swedish court decisions
- **WFDSA.org** — Global industry statistics (label as industry-funded)
- **Academic databases** — Peer-reviewed MLM research (Journal of Consumer Affairs, etc.)
- **Company IDS filings** — Official income disclosure statements

### Prohibited External Sources
- **PubMed** — Health research (belongs to LevNytt Writer — `.opencode/agents/levnytt-writer.md`)
- **EFSA** — European Food Safety Authority health claims (belongs to LevNytt Writer)
- **Livsmedelsverket** — Swedish Food Agency nutrition guidance (belongs to LevNytt Writer)
- **Supplement retailer sites** — Product claims and marketing
- **MLM company marketing pages** — Income promises and lifestyle claims

---

## Gap Report Integration

The MLM gap report (`docs/editorial-backlog/mlm-gap.md`) provides consumer question patterns and search intent data. The MLM Editorial Agent uses gap reports to:

1. **Understand consumer questions** — What are people actually asking?
2. **Identify search intent** — Informational, commercial, transactional?
3. **Prioritize coverage** — Which questions have the strongest signal?
4. **Build FAQ sections** — Real questions from real consumers

The MLM Editorial Agent reads the gap report **after** reading authority research files, using it for question patterns and consumer language, not as a primary evidence source.

---

## Coverage Map

### Already Published (from production-status.md)

| Page | Topic | Status |
|------|-------|--------|
| `/direktforsaljning-fakta` | Legal definitions, MLM vs pyramid | Published |
| `/hur-fungerar-natverksmarknadsforing-egentligen` | FTC 2024 data, compensation mechanics | Published |
| `/mlm-inkomstredovisningar-vad-sager-siffrorna` | Income disclosure analysis | Published |
| `/mlm-rekrytering-social-press-taktiker` | Recruitment tactics | Published |
| `/mlm-foretag-skandaler-sverige-varlden` | Company scandals | Published |
| `/mlm-konsumentratt-retur-angeratt` | Consumer rights and returns | Published |
| `/mlm-produkter-kosttillskott-pris` | Product pricing | Published |

### Ready to Write (Authority CLEARED)

| Topic | Priority | Score | Business Impact | Authority File |
|-------|----------|-------|-----------------|----------------|
| Konsumenträtt vid MLM-köp — returrätt, ångerrätt och anmälan | B | 72 | 54 ★★☆☆☆ | direct-selling-associations-authority-research.md |

### Blocked (Needs Authority Research)

| Topic | Priority | Score | Business Impact | Blocker |
|-------|----------|-------|-----------------|---------|
| *(No current MLM topics blocked)* | — | — | — | — |

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-30 | Initial authority source mapping. 8 MLM authority research files documented. Topic-to-file mapping established. Evidence hierarchy defined. External source policy set. |
