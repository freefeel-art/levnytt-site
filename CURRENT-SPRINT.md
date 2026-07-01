# CURRENT-SPRINT.md
# LevNytt.se — Project Phase

Last updated: 2026-07-01

---

## Phase: Content Factory Transition

The Gen 3 migration is **complete**.
The Brand System (Sprint 8), Brand Rollout (Sprint 9), Repository Cleanup (Sprint 9b), and Post-Cleanup Baseline (Sprint 10) are **complete**.
The Production Orchestrator V1 (Sprint 11) is built and being tested.

---

## Sprint History

### Sprint 9 — Brand Rollout + Repository Cleanup

| | |
|---|---|
| **Status** | ✅ Completed |
| **Completed** | 2026-07-01 |
| **Commit** | `c61eebc` |

- Brand OG images deployed to 70+ root pages + 37 content/articles
- 28+ obsolete/superseded files removed
- SKILL-v2 backups moved to `.archive/`
- REPOSITORY-CLEANUP-REPORT.md written

### Sprint 10 — Post-Cleanup Baseline

| | |
|---|---|
| **Status** | ✅ Completed |
| **Completed** | 2026-07-01 |
| **Commits** | `69c5359`, `a0ab42a` |

- levnytt-writer.md: `<div class="ia-wrap">` structure, PAS V1.0 note
- SKILL.md: `gpt-image-2` reference fixed
- reddit_niche_radar.py: cron path fixed
- levnytt-se-master-template.html: deleted, 6 docs updated
- vad-ar-lutein: deployed to root, QA 12/12

---

## Active Sprint — 11

| | |
|---|---|
| **Status** | 🟢 Active |
| **Sprint** | 11 — Production Orchestrator V1 |
| **Started** | 2026-07-01 |

### Objective

Transform the agent suite into a Content Factory with a single-command production pipeline. Pipeline documentation, orchestrator agent, shell runner, and QA validator are built. Ready for end-to-end testing.

### Tasks

- [x] Audit all 7 registered agents (responsibilities, inputs, outputs)
- [x] Write `docs/PRODUCTION-PIPELINE.md`
- [x] Write `docs/PRODUCTION-ORCHESTRATOR.md`
- [x] Create `.opencode/agents/production-orchestrator.md`
- [x] Create `scripts/run-production.sh`
- [x] Create `scripts/qa-article.sh` (12-check PAS V1.0 validator)
- [x] Fix QA edge cases (multi-line structure, gold variants)
- [ ] End-to-end production test with a real keyword
- [ ] Verify Publication Agent handles orchestrator publishes

### Completion criteria

- Single command: `./scripts/run-production.sh "<keyword>"`
- QA validator: correct GREEN/AMBER/RED gates
- Orchestrator agent: chains all agents via opencode Task tool
- End-to-end run produces published article at root

### Next action

Full end-to-end test: invoke orchestrator with a real keyword.
Run `"run production: vad-är-magnesium"` in opencode.

---

## Future work (backlog)

| Area | Description |
|---|---|
| Product Entity System | Structured product data via `content/products/` |
| Content expansion | New articles, internal linking |
| Research Commander modules | Implement authority, DataForSEO, reddit modules |
| Automated Editorial Review | Auto-approve routine QC gates |
| Performance | Image optimization, lazy loading, Core Web Vitals |