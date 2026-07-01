# CURRENT-SPRINT.md
# LevNytt.se — Project Phase

Last updated: 2026-07-01

---

## Phase: Content Factory Transition

The Gen 3 migration is **complete**.
The Brand System (Sprint 8), Brand Rollout (Sprint 9), Repository Cleanup (Sprint 9b), and Post-Cleanup Baseline (Sprint 10) are **complete**.
The Production Orchestrator + Production Brief Architecture + Cost Telemetry (Sprint 11) is **complete**.

---

## Sprint History

### Sprint 9 — Brand Rollout + Repository Cleanup

| | |
|---|---|
| **Status** | ✅ Completed |
| **Completed** | 2026-07-01 |
| **Commit** | `c61eebc` |

### Sprint 10 — Post-Cleanup Baseline

| | |
|---|---|
| **Status** | ✅ Completed |
| **Completed** | 2026-07-01 |
| **Commits** | `69c5359`, `a0ab42a` |

### Sprint 11 — Production Orchestrator + Brief Architecture + Telemetry

| | |
|---|---|
| **Status** | ✅ Completed |
| **Completed** | 2026-07-01 |
| **Commits** | `4fd38ac`, `2bd61c6`, `ba7079f` |

**Delivered:**
- `docs/PRODUCTION-PIPELINE.md` — V2: Brief→Package→Editorial chain (7 stages)
- `docs/PRODUCTION-ORCHESTRATOR.md` — V2: brief-first invocation, QA gating, abort/resume
- `docs/PRODUCTION-BRIEF-SPEC.md` — 14-field canonical spec (YAML)
- `docs/RESEARCH-PACKAGE-SPEC.md` — 12-file structured research output
- `docs/COST-TELEMETRY.md` — model pricing, log format, aggregation queries
- `scripts/run-production.sh` — V2: generates `.brief.yaml` from keyword, detects intent/topic/audience
- `scripts/qa-article.sh` — 12-check PAS V1.0 validator (GREEN/AMBER/RED)
- `scripts/cost-report.sh` — CLI cost aggregator (--today, --month, --per-article)
- `content/briefs/vad-ar-lutein.brief.yaml` — example brief (verified against 12/12 QA article)
- `production/logs/` — telemetry directory + sample log
- `.opencode/agents/production-orchestrator.md` — V2: brief-first agent chainer with telemetry

**Key architectural decision:** Keyword is now one field in the Production Brief, not the pipeline input. Brief → Research Commander → Research Package → Editorial Commander → Editorial Brief → Writer.

---

## Active Sprint — 12

| | |
|---|---|
| **Status** | 🟢 Active |
| **Sprint** | 12 — Local LLM Pilot (Ollama) |
| **Started** | Pending reboot |

### Objective

Evaluate whether Editorial Commander, Writer, and QA can run locally via Ollama instead of OpenRouter. Benchmark output quality, execution time, RAM, GPU usage, and estimated cost savings.

### Phase 1 — Setup

- [ ] Reboot system (NVIDIA driver installation requires it)
- [ ] Verify NVIDIA: `nvidia-smi`, CUDA runtime
- [ ] Install Ollama
- [ ] Download qwen3:8b (or smaller model if needed)

### Phase 2 — Benchmark

- [ ] Run same Editorial Brief on OpenRouter (baseline)
- [ ] Run same Editorial Brief on Ollama (local)
- [ ] Compare: output quality, execution time, RAM, GPU, cost
- [ ] Document findings

### Phase 3 — Decision

- [ ] Decide which agents can be moved to local execution
- [ ] Update agent configuration if needed

### Completion criteria

- Ollama installed and running with at least one model
- Benchmark data collected for OpenRouter vs Ollama
- Clear recommendation: which agents to move local, which to keep on OpenRouter

### Next action

Reboot → `nvidia-smi` → install Ollama → pull model → run benchmark

---

## Future work (backlog)

| Area | Description |
|---|---|
| Product Entity System | Structured product data via `content/products/` |
| Content expansion | New articles, internal linking |
| Research Commander modules | Implement authority, DataForSEO, reddit modules |
| Agent migration to Production Brief | Update agents to consume `.brief.yaml` instead of keywords |
| Automated Editorial Review | Auto-approve routine QC gates |
| Performance | Image optimization, lazy loading, Core Web Vitals |