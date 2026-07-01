# Cost Telemetry V1

**Date:** 2026-07-01
**Status:** ACTIVE
**Scope:** All Production Orchestrator runs

---

## Purpose

Lightweight cost and usage telemetry for every production run. Tracks token consumption, estimated cost, duration, and status per agent — enabling cost-per-article, cost-per-agent, and daily/monthly cost questions without a database or dashboard.

---

## What We Track

### Per-run fields

| Field | Type | Source | Description |
|---|---|---|---|
| `run_id` | string | Generated | UUID or `YYYYMMDD-HHMMSS-<slug>` |
| `timestamp` | ISO 8601 | Clock | When the run started |
| `article` | string | Brief | Slug of the produced article |
| `status` | enum | Pipeline | `success`, `partial`, `failed`, `aborted` |

### Per-agent fields (for each of: research, editorial, writer, publication, qa)

| Field | Type | Source | Description |
|---|---|---|---|
| `agent` | string | Orchestrator | Agent name (research-commander, editorial-commander, etc.) |
| `model` | string | Orchestrator | Model used for this agent's inference |
| `provider` | string | Orchestrator | API provider (openrouter, anthropic, openai) |
| `requests` | int | Orchestrator | Number of LLM API calls |
| `input_tokens` | int | Estimate | Input tokens consumed (0 if unavailable) |
| `output_tokens` | int | Estimate | Output tokens consumed (0 if unavailable) |
| `cost_estimate_usd` | float | Calculated | Estimated cost in USD |
| `duration_ms` | int | Clock | Wall clock duration |
| `cache_used` | bool | Manifest | Whether cached data was used (research only) |

### Totals

| Field | Type | Description |
|---|---|---|
| `total_requests` | int | Sum across all agents |
| `total_tokens` | int | Input + output tokens |
| `total_cost_estimate_usd` | float | Sum across all agents |
| `total_duration_ms` | int | End-to-end pipeline duration |

---

## Model Pricing Reference (V1 hardcoded)

Prices per million tokens. Updated manually when models change.

| Model | Provider | Input $/1M tokens | Output $/1M tokens |
|---|---|---|---|
| `deepseek-v4-pro` | openrouter | $0.27 | $1.10 |
| `deepseek-v3` | openrouter | $0.27 | $1.10 |
| `claude-sonnet-4` | anthropic | $3.00 | $15.00 |
| `claude-opus-4` | anthropic | $15.00 | $75.00 |
| `gpt-4o` | openai | $2.50 | $10.00 |
| `gpt-4.1-mini` | openai | $0.40 | $1.60 |

**Fallback:** If model is unknown, use `$1.00 / $4.00` per million as a conservative estimate.

**Cost formula:**
```
cost = (input_tokens / 1_000_000 * input_price) + (output_tokens / 1_000_000 * output_price)
```

---

## Log File Format

### Individual run log

**Path:** `production/logs/<run_id>.json`

```json
{
  "run_id": "20260701-135000-vad-ar-lutein",
  "timestamp": "2026-07-01T13:50:00Z",
  "article": "vad-ar-lutein",
  "status": "success",
  "agents": {
    "research": {
      "agent": "research-commander",
      "model": "deepseek-v4-pro",
      "provider": "openrouter",
      "requests": 3,
      "input_tokens": 45000,
      "output_tokens": 8000,
      "cost_estimate_usd": 0.021,
      "duration_ms": 15000,
      "cache_used": false
    },
    "editorial": {
      "agent": "editorial-commander",
      "model": "deepseek-v4-pro",
      "provider": "openrouter",
      "requests": 1,
      "input_tokens": 25000,
      "output_tokens": 3000,
      "cost_estimate_usd": 0.010,
      "duration_ms": 5000,
      "cache_used": null
    },
    "writer": {
      "agent": "levnytt-writer",
      "model": "deepseek-v4-pro",
      "provider": "openrouter",
      "requests": 2,
      "input_tokens": 60000,
      "output_tokens": 12000,
      "cost_estimate_usd": 0.030,
      "duration_ms": 60000,
      "cache_used": null
    },
    "publication": {
      "agent": "publication-agent",
      "model": "deepseek-v4-pro",
      "provider": "openrouter",
      "requests": 1,
      "input_tokens": 15000,
      "output_tokens": 2000,
      "cost_estimate_usd": 0.006,
      "duration_ms": 8000,
      "cache_used": null
    },
    "qa": {
      "agent": "qa-article.sh",
      "model": "none",
      "provider": "none",
      "requests": 0,
      "input_tokens": 0,
      "output_tokens": 0,
      "cost_estimate_usd": 0.0,
      "duration_ms": 500,
      "cache_used": null
    }
  },
  "totals": {
    "total_requests": 7,
    "total_input_tokens": 145000,
    "total_output_tokens": 25000,
    "total_tokens": 170000,
    "total_cost_estimate_usd": 0.067,
    "total_duration_ms": 88500
  }
}
```

### History aggregation file

**Path:** `production/logs/history.json`

Append-only array of run summaries. Used for daily/monthly aggregation without scanning all individual logs.

```json
[
  {
    "run_id": "20260701-135000-vad-ar-lutein",
    "timestamp": "2026-07-01T13:50:00Z",
    "article": "vad-ar-lutein",
    "models": ["deepseek-v4-pro"],
    "requests": 7,
    "total_tokens": 170000,
    "estimated_cost_usd": 0.067,
    "duration_ms": 88500,
    "status": "success"
  }
]
```

---

## Production Report — Telemetry Section

The Production Orchestrator appends a cost section to every Production Report:

```
============================================================
PRODUCTION COST METRICS
============================================================

Run ID:    20260701-135000-vad-ar-lutein
Timestamp: 2026-07-01 13:50:00 UTC

AGENT          MODEL              REQ    TOKENS      COST     DURATION
─────          ─────              ───    ──────      ────     ────────
Research       deepseek-v4-pro     3     53 000    $0.021        15.0s
Editorial      deepseek-v4-pro     1     28 000    $0.010         5.0s
Writer         deepseek-v4-pro     2     72 000    $0.030        60.0s
Publication    deepseek-v4-pro     1     17 000    $0.006         8.0s
QA             none (bash)         0          0    $0.000         0.5s
─────────────────────────────────────────────────────────────────
TOTAL                             7     170 000    $0.067        88.5s

Status: SUCCESS
============================================================
```

---

## Aggregation Queries

With the `history.json` file, simple CLI tools can answer cost questions:

### Cost per article
```bash
cat production/logs/history.json | jq '.[] | {article, cost: .estimated_cost_usd}'
```

### Cost per day
```bash
cat production/logs/history.json | jq '[.[] | select(.timestamp | startswith("2026-07-01"))] | length as $count | {articles: $count, total_cost: [.[].estimated_cost_usd] | add}'
```

### Cost per month
```bash
cat production/logs/history.json | jq '[.[] | select(.timestamp | startswith("2026-07"))] | length as $count | {articles: $count, total_cost: [.[].estimated_cost_usd] | add}'
```

### Total all-time
```bash
cat production/logs/history.json | jq '{articles: length, total_cost: [.[].estimated_cost_usd] | add, total_tokens: [.[].total_tokens] | add}'
```

### Helper script
`scripts/cost-report.sh` wraps common queries. See that file.

---

## Collection Strategy

### V1 — Orchestrator estimate

In V1, the Production Orchestrator **estimates** token usage based on known patterns:
- Research Commander: ~15-45K input, ~3-8K output (varies by topic complexity)
- Editorial Commander: ~15-25K input, ~2-5K output
- Writer: ~40-80K input, ~8-20K output
- Publication Agent: ~10-20K input, ~1-3K output
- QA: 0 (bash script, no LLM)

These are rough estimates. Actual token counts from the API are preferred when available.

### V2 (future) — Real API telemetry

When opencode exposes token usage per Task invocation, switch to actual counts. Until then, estimates are annotated with `"token_source": "estimate"` in the log.

---

## Directory Structure

```
production/
└── logs/
    ├── .gitkeep
    ├── history.json              ← Append-only run summaries
    └── <run_id>.json            ← Individual run telemetry
```

`history.json` is the primary query surface. Individual run logs provide per-agent detail for debugging.

---

## Rules

1. **Every production run must produce a telemetry log.** No exceptions.
2. **Token estimates must be flagged.** `"token_source": "estimate"` until real API data is available.
3. **history.json is append-only.** Never rewrite history entries. A new run appends a new entry.
4. **Costs are estimates, not invoices.** Rounded to 3 decimal places for USD.
5. **QA costs $0.** It runs locally as a bash script with no API calls.
6. **Publication Agent costs are negligible.** One API call to generate commit message.
7. **No database, no dashboard, no analytics service.** JSON files only.

---

## Version History

| Version | Date | Change |
|---|---|---|
| V1 | 2026-07-01 | Initial spec. Estimate-based telemetry, JSON logs, history.json aggregation. |