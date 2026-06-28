# CURRENT-SPRINT.md
# LevNytt.se — Active Sprint

Last updated: 2026-06-28

See `PROJECT-ENTRY.md` for workflow. See `PROJECT-STATUS.md` for the open backlog.

---

## Sprint status

**Completed.** Sprint 6 — Wave 3B: Informational article production-standard migration.

---

## Sprint objective

Audit all informational articles for production-standard compliance and migrate every non-compliant page to pass the required checks.

---

## Tasks

- [x] Define sprint in CURRENT-SPRINT.md
- [x] Audit all informational articles — produce a pass/fail list
- [x] Migrate each non-compliant article to production standard
- [x] Verify each migrated page passes all required checks
- [x] Update PROJECT-STATUS.md milestones
- [x] Create SPRINT-6-REPORT.md

---

## Completion criteria

All met. Every informational article (55 pages):
1. Links `pillar.css` ✓
2. Has no inline `:root` token block ✓
3. Has at least 3 `@media` breakpoints ✓
4. Has `<meta property="og:image">` ✓
5. Loads `nav.js`, `footer.js`, `components.js` with `defer` ✓

---

## Blockers

None.

---

## Next action

Sprint 6 is complete. Project owner: open the next sprint from `PROJECT-STATUS.md → Open backlog`.

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
