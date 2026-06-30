# LevNytt Morning Brief Architecture

## Overview

The LevNytt Morning Brief system consists of two independent agents that run every morning. Both analyze different information sources, produce independent recommendations, and return control to the editor. The editor compares both briefs and decides the single highest-value action for the day.

| Agent | File | Purpose |
|---|---|---|
| Morning Brief | `.opencode/agents/morning-brief.md` | Consumer Intelligence |
| MLM Brief | `.opencode/agents/mlm-brief.md` | Industry & Editorial Intelligence |

Neither agent publishes content. Neither writes articles. Both only make editorial recommendations.

---

## Mission

The Morning Brief system is the daily editorial decision apparatus for LevNytt.

Its purpose is to analyze both external consumer demand and internal editorial readiness, then surface the single highest-value action for the day.

The system never publishes content.

It never writes articles.

It only makes editorial recommendations.

---

## Position in the Workflow

```
  Morning Brief            MLM Brief
  (consumer intel)    (industry intel)
         ↓                    ↓
     ───────── Human Approval ─────────
                    ↓
            Publication Agent
                    ↓
            Published Content
```

Both briefs are executed first every morning. Control always returns to the user. No other agent is executed automatically. Human approval is always required before continuing.

---

## Agent Responsibilities

### Morning Brief — Consumer Intelligence

The Morning Brief analyzes what consumers are searching for and discussing today.

**Inputs:**

External signals only:
* Google Trends
* Reddit discussions (r/sweden, r/Supplements, r/Biohackers)
* Google Autocomplete
* Question-intent Autocomplete proxy (in lieu of People Also Ask)
* Published content (for coverage comparison)
* Sitemap

**Responsibilities:**
* Detect what consumers are searching for today
* Detect trending topics and emerging consumer interests
* Compare external demand with existing published coverage
* Identify content gaps from the consumer perspective
* Detect new consumer language and framing
* Recommend one primary consumer-facing content opportunity
* Recommend one secondary opportunity if appropriate

**Does NOT analyze:**
* Editorial backlog (gap reports)
* Authority research status
* Production status
* Editorial briefs history
* MLM/regulatory pipeline

### MLM Brief — Industry & Editorial Intelligence

The MLM Brief analyzes the internal editorial pipeline and industry landscape.

**Inputs:**

Internal signals:
* Editorial Backlog (gap reports)
* Editorial Briefs
* Production Status
* Authority Research
* Existing Articles
* Sitemap
* Published HTML pages
* Industry context (MLM, direct selling, FTC, regulatory)

**Responsibilities:**
* Analyze authority research coverage and gaps
* Track editorial backlog state
* Monitor production status (generated vs published)
* Detect coverage gaps from editorial backlog perspective
* Detect outdated priorities and stale gap reports
* Identify production blockers
* Identify missing authority research
* Recommend one primary editorial/pipeline action
* Recommend one secondary action if appropriate

**Does NOT analyze:**
* Google Trends
* Reddit discussions
* Google Autocomplete
* Consumer search behavior
* External market signals

---

## Non-Responsibilities (Both Agents)

Neither agent may:
* Write articles
* Generate HTML
* Modify repository files
* Publish content
* Perform Page Builder tasks
* Invoke another agent automatically

---

## Integration

Morning Brief consumes:
* External signals (Google Trends, Reddit, Autocomplete)
* Published content (for coverage comparison)

MLM Brief consumes:
* Editorial Backlog
* Authority Research
* Production Status
* Editorial Briefs

Both agents hand control to:

Publication Agent

No other agent is automatically executed.

Human approval is always required before continuing.

---

## Shared Guiding Principle

Morning Brief is not an AI writer.

MLM Brief is not an AI writer.

Both are editorial decision engines.

Their shared success is measured by helping the editor consistently choose the highest-value work each day — whether driven by consumer demand or editorial pipeline readiness.