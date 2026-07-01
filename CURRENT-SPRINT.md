# CURRENT-SPRINT.md
# LevNytt.se — Project Phase

Last updated: 2026-07-01

---

## Phase: Maintenance + Feature Development

The Gen 3 migration is **complete**.
The Brand System integration (Sprint 8), Brand Rollout (Sprint 9), and Repository Cleanup (Sprint 9b) are **complete**.

---

## Sprint History

### Sprint 9 — Brand Rollout + Repository Cleanup

| | |
|---|---|
| **Status** | ✅ Completed |
| **Completed** | 2026-07-01 |
| **Commit** | `c61eebc` |

- Brand OG images deployed to 70+ root pages + 37 content/articles
- `#site-nav` placeholders added to final 44 root pages
- `nav.js` + `footer.js` + `components.js` + `pillar.css` verified on all 80 root pages
- 28+ obsolete/superseded files removed
- SKILL-v2 backups moved to `.archive/`; `levnytt-se-master-template.html` marked LEGACY
- Production validation pass: `vad-ar-lutein` — 83/83 QA checks
- REPOSITORY-CLEANUP-REPORT.md written as deletion record

---

## Active Sprint — 10

| | |
|---|---|
| **Status** | 🟢 Active |
| **Sprint** | 10 — Post-Cleanup Baseline |
| **Started** | 2026-07-01 |

### Objective

Solidify the single production baseline after cleanup: update writer pipeline to PAS V1.0, resolve legacy references, and clear remaining broken references.

### Tasks

- [x] Update `.opencode/agents/levnytt-writer.md` to reference PAS V1.0 template (not SKILL.md)
- [x] Update `.opencode/agents/levnytt-writer.md` to use `<div class="ia-wrap"><article>` structure
- [x] Update `.opencode/agents/levnytt-writer.md` to use green/gold brand palette (already correct)
- [x] Update `.opencode/agents/levnytt-writer.md` to use dark evidence tier backgrounds (already correct)
- [x] Remove or update 5+ docs referencing `levnytt-se-master-template.html`
- [x] Decide fate of `levnytt-se-master-template.html` — removed (6 docs updated, file deleted)
- [x] Fix broken cron path in `reddit_niche_radar.py` (`/home/yampa/Documents/Levnytt/`)
- [x] Fix `informational-article/SKILL.md` reference to sibling `gpt-image-2` skill
- [x] Run Publication Agent for `vad-ar-lutein` (deploy to root)

### Completion criteria

- [x] Pipeline produces PAS V1.0 compliant articles (levnytt-writer.md updated)
- [x] No broken references to deleted files
- [x] No docs reference `levnytt-se-master-template.html` (file deleted, 6 docs updated)
- [x] levnytt-writer.md uses `<div class="ia-wrap"><article>` structure
- [x] SKILL.md `gpt-image-2` reference fixed
- [x] Cron paths in `reddit_niche_radar.py` fixed
- [x] Production article `vad-ar-lutein.html` deployed at root
- [x] CURRENT-SPRINT.md updated with Sprint 10 progress

### Next action

Serve `vad-ar-lutein.html` at http://127.0.0.1:8080/vad-ar-lutein for visual QA.
## Sprint status
Active.

## Sprint objective
[One sentence describing the goal.]

## Tasks
- [ ] Task 1
- [ ] Task 2

## Completion criteria
[Specific, verifiable conditions that define "done".]

## Next action
[Exactly what to do next.]
```
