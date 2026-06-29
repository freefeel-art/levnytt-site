# CURRENT-SPRINT.md
# LevNytt.se — Active Sprint

Last updated: 2026-06-29

See `PROJECT-ENTRY.md` for workflow. See `PROJECT-STATUS.md` for the open backlog.

---

## Sprint status

**Completed.** Sprint 13 — `index.html` (front page) migrated from Gen 1 to Gen 3.

---

## Sprint objective

Migrate `index.html` from Generation 1 (Legacy) to Generation 3 (Complete):
inline `:root` → `pillar.css`, add `components.js` with `defer`, add
verification meta tags, add `og:image`, add 3+ `@media` breakpoints.

---

## Tasks

- [x] Add google-site-verification and p:domain_verify meta tags
- [x] Add og:image meta tags
- [x] Add `<link rel="stylesheet" href="/pillar.css">`
- [x] Remove inline `:root` token block (tokens now from pillar.css)
- [x] Add tablet `@media` breakpoint for 3+ total breakpoints
- [x] Add `<script src="/components.js" defer>`
- [x] Verify 13/13 audit pass (was 9/13 pre-migration)
- [x] Commit and push
- [x] Update PROJECT-STATUS.md

---

## Completion criteria

All met. `index.html` passes 13/13 audit checklist. All Gen 3 requirements
satisfied: `pillar.css`, no inline `:root`, scripts with `defer`, verification
meta, `og:image`, Google Fonts, 3+ breakpoints, canonical, viewport.

---

## Blockers

None.

---

## Next action

No active sprint. Recommended next sprint: `neolife-kosttillskott/index.html`
(hub page) — last remaining hub page still at Gen 1 with inline `:root` and
components.js without defer.

---

## Sprint template

When opening a new sprint, replace the sections above with:

```
## Sprint status
Active.

## Sprint objective
[One sentence describing the goal.]

## Tasks
- [ ] Task 1
- [ ] Task 2

## Completion criteria
[Specific, verifiable conditions that define "done".]

## Blockers
[Anything preventing progress, or "None".]

## Next action
[Exactly what to do next — specific enough to act on immediately.]
```
