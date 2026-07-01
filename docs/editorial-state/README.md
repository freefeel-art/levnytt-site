# Editorial State Interface

**Version:** 1.0  
**Date:** 2026-06-30  
**Status:** Production  

This document defines the official interface between the Editorial Sync Engine and all editorial agents in the LevNytt editorial system.

---

## Architecture Overview

The Editorial Sync Engine is the **canonical producer** of editorial state. All editorial agents are **canonical consumers** of this synchronized state.

```
┌─────────────────────┐
│  Editorial Sync     │ ← Repository traversal happens HERE
│  Engine             │
└─────────┬───────────┘
          │ Generates
          ▼
┌─────────────────────┐
│  Generated          │ ← Synchronized editorial state
│  Editorial State    │
└─────────┬───────────┘
          │ Consumed by
          ▼
┌─────────────────────┐
│  Morning Brief      │ ← Editorial agents consume state
│  MLM Brief          │
│  Future Agents      │
└─────────────────────┘
```

### Core Principle

**Repository traversal occurs ONLY within the Editorial Sync Engine.**

Editorial agents consume synchronized state and perform repository inspection only when synchronized state cannot answer their questions.

---

## Generated Editorial State Files

### Production Status
- **File:** `docs/editorial-backlog/production-status.md`
- **Purpose:** Complete backlog status with priority scores, publication state, and authority research status
- **Producer:** Editorial Sync Engine V1.0
- **Consumers:** MLM Brief, Future editorial agents
- **Update Trigger:** `python3 scripts/sync-editorial-state.py`
- **Edit Policy:** AUTO-GENERATED — DO NOT EDIT

### Publication Queue  
- **File:** `docs/reports/publication-queue.md`
- **Purpose:** Pre-prioritized editorial queue with Ready to Write, Blocked, and Ready to Publish categories
- **Producer:** Editorial Sync Engine V1.0
- **Consumers:** MLM Brief, Publication planning agents
- **Update Trigger:** `python3 scripts/sync-editorial-state.py`
- **Edit Policy:** AUTO-GENERATED — DO NOT EDIT

### Repository Inventory
- **File:** `docs/reports/repository-inventory.md`
- **Purpose:** Complete inventory of published pages, source articles, product entities, and authority research coverage
- **Producer:** Editorial Sync Engine V1.0
- **Consumers:** Morning Brief, MLM Brief, Coverage analysis agents
- **Update Trigger:** `python3 scripts/sync-editorial-state.py`
- **Edit Policy:** AUTO-GENERATED — DO NOT EDIT

### Drift Detection
- **File:** `docs/reports/drift-detection.md`
- **Purpose:** Analysis of content drift, stale gap reports, and synchronization issues
- **Producer:** Editorial Sync Engine V1.0
- **Consumers:** Editorial health monitoring agents
- **Update Trigger:** `python3 scripts/sync-editorial-state.py`
- **Edit Policy:** AUTO-GENERATED — DO NOT EDIT

---

## Interface Contract

### For Editorial Agents

**MANDATORY SEQUENCE:**

1. **Read synchronized state first** from the files listed above
2. **Extract required information** from synchronized reports  
3. **Only inspect repository directly** if synchronized state lacks the required information
4. **Limit repository inspection** to the smallest subset needed to answer the specific question

**PROHIBITED:**

- Reading gap reports individually when `production-status.md` contains the same information
- Rebuilding repository inventories when `repository-inventory.md` exists
- Re-computing publication queues when `publication-queue.md` exists
- Traversing `content/articles/` or published pages for coverage analysis when synchronized state exists

### For Future Agent Development

**New editorial agents MUST:**

1. **Start with this interface specification** as their primary input source
2. **Read `docs/editorial-state/README.md`** to understand the canonical state files
3. **Follow the mandatory sequence** for repository access
4. **Document their consumption** of synchronized state in their agent specification

---

## Synchronization Triggers

### Manual Sync
```bash
python3 scripts/sync-editorial-state.py
```

### When to Sync
- After gap report updates
- After authority research completion  
- After publication of new content
- Before running editorial agent batches
- When drift detection indicates stale state

### Sync Engine Location
```
scripts/sync-editorial-state.py
docs/specifications/EDITORIAL-SYNC-ENGINE.md
```

---

## Canonical Rules

### 1. Repository Inspection Rule

**Never inspect the repository directly if synchronized editorial state already exists.**

Repository traversal is only permitted when synchronized state cannot answer the question.

This is a permanent architectural principle for the LevNytt editorial system.

### 2. Producer-Consumer Separation

- **Editorial Sync Engine:** Canonical producer of editorial state
- **Editorial Agents:** Canonical consumers of editorial state
- **No overlap:** Editorial agents do not produce editorial state

### 3. Generated File Policy

All files marked "AUTO-GENERATED — DO NOT EDIT" are part of the synchronized editorial state interface.

**NEVER modify these files manually.**

Always regenerate using the Editorial Sync Engine.

---

## Interface Evolution

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-06-30 | Initial interface specification. Formalized Editorial Sync Engine as canonical producer. Established producer-consumer architecture. |

### Adding New Generated Files

1. **Update Editorial Sync Engine** to generate the new file
2. **Document the file** in this interface specification
3. **Update consumers** to use the new synchronized state
4. **Version the interface** and update agent specifications

### Deprecating Generated Files

1. **Update all consumers** to use alternative synchronized state
2. **Remove generation** from Editorial Sync Engine
3. **Update interface specification**
4. **Version the interface**

---

## Specialist Agents

### MLM Editorial Agent
- **File:** `.opencode/agents/mlm-editorial-agent.md`
- **Scope:** MLM, network marketing, direct selling, compensation plans, income disclosures, consumer protection, FTC regulation, pyramid scheme education, company comparisons
- **Authority Sources:** 8 MLM authority research files in `docs/authority-research/`
- **Authority Source Mapping:** `docs/editorial-state/mlm-authority-source-mapping.md`
- **Never Handles:** Health, supplements, nutrition, medical research (belongs to LevNytt Writer — `.opencode/agents/levnytt-writer.md`)

### MLM Brief V1.1 (Compliant)
```markdown
### STEP 2 — Read Synchronized Editorial State

Read `docs/editorial-backlog/production-status.md` (generated by Editorial Sync Engine). Extract:
* Full backlog status with priority and scores
* Published vs New Article classification  
* Authority research status (CLEARED / BLOCKED / PROXY)

Read `docs/reports/publication-queue.md` (generated by Editorial Sync Engine). Extract:
* Ready to Write items (Authority CLEARED)
* Blocked items (Needs Authority Research)
```

### Morning Brief V2.1 (Compliant)
```markdown  
### STEP 3 — Read Synchronized Coverage State

Read `docs/reports/repository-inventory.md` (generated by Editorial Sync Engine) for current published page inventory.

**Only if synchronized state lacks required information:** Use Glob to list root `/*.html` files for verification.
```

---

## Validation Checklist

**For Editorial Agents:**

- [ ] Reads synchronized state files first
- [ ] Documents which synchronized files it consumes
- [ ] Only performs repository traversal when synchronized state is insufficient  
- [ ] Limits repository inspection to minimum required subset
- [ ] Does not rebuild information that exists in synchronized state

**For Editorial Sync Engine:**

- [ ] Generates all documented interface files
- [ ] Marks generated files as "AUTO-GENERATED — DO NOT EDIT"
- [ ] Includes generation metadata (timestamp, commit, version)
- [ ] Provides complete editorial state for consumer needs

**For Documentation:**

- [ ] All generated files are documented in this interface
- [ ] Consumer agents reference this interface specification
- [ ] Architecture diagrams show producer-consumer relationship
- [ ] Cross-references from other documentation point to this interface

---

## Future Roadmap

### Planned Enhancements
- **Content Performance State:** Article traffic, engagement, conversion metrics
- **Editorial Calendar State:** Publication scheduling, seasonal content planning  
- **Quality Assurance State:** Content quality scores, SEO compliance, fact-checking status
- **Consumer Intelligence State:** Search trends, social signals, competitor analysis integration

### Integration Points
- **Publication Agent:** Will consume publication queue and production status
- **Content Calendar Agent:** Will consume editorial calendar state when implemented
- **Analytics Agent:** Will consume performance state when implemented

---

## Support

**Documentation:** This file (`docs/editorial-state/README.md`)  
**Sync Engine Spec:** `docs/specifications/EDITORIAL-SYNC-ENGINE.md`  
**Agent Examples:** `.opencode/agents/morning-brief.md`, `.opencode/agents/mlm-brief.md`  
**Generation Script:** `scripts/sync-editorial-state.py`

For architectural questions about the Editorial State Interface, consult this documentation first.