# CONTRADICTION-RESOLUTION.md
# LevNytt.se — Contradiction Classification and Resolution Guide

**Date:** 2026-07-02  
**Author:** Production Engineer (Claude Code)  
**Scope:** Contradictions C1–C8 identified in `docs/PRODUCTION-READINESS-REVIEW.md`  
**Method:** Read-only analysis — no code or documents modified  

---

## Classification Key

| Code | Meaning |
|---|---|
| **A** | Documentation is outdated — the code/files reflect the correct state; a document has not been updated to match |
| **B** | Code is outdated — the specification is correct; the implementation diverges from it |
| **C** | Both are outdated — neither the specification nor the implementation fully reflects the intended state |
| **D** | False positive — no genuine contradiction exists; the finding was a wording imprecision in the review |

---

## C1 — ia-* CSS described as "pending extraction" when partial extraction already exists in `pillar.css`

**Classification: C — Both are outdated**

### Root cause

`PUBLICATION-ARTICLE-STANDARD.md` V1.0 (frozen 2026-06-30) contains the note: "NOT YET EXTRACTED. This standard documents the CSS as inline per article." The production readiness review reproduced this claim.

At some point after that note was written, 13 ia-* class groups were added to `pillar.css` (lines 53–101): `.ia-wrap`, `.ia-eyebrow`, `.ia-meta`, `.ia-punchline`, `.ia-takeaways`, `.ia-cta`, `.ia-method-table`, `.ia-author-box`, `.ia-author-avatar`, `.ia-method-note`, `.ia-kort-svar`, `.ia-prompt`, `.ia-svg-card`. However, these classes were added with values that differ from the PAS V1.0 inline specification (see C2). Neither the PAS note nor the pillar.css values accurately describes the intended end state.

### Source of truth

`DECISIONS.md B3` designates `pillar.css` as the single design system. `PUBLICATION-ARTICLE-STANDARD.md` V1.0 (FROZEN) is the canonical specification for ia-* component CSS values for articles. The two are in conflict because pillar.css received partially wrong values during an unrecorded operation.

### Recommended resolution

1. Update the "NOT YET EXTRACTED" note in `PUBLICATION-ARTICLE-STANDARD.md` to reflect the current state: "PARTIALLY EXTRACTED to `pillar.css`, but with incorrect values — see `docs/CONTRADICTION-RESOLUTION.md` C1/C2 before proceeding with any extraction sprint."
2. Resolving C2 and C3 is a prerequisite before the PAS note can be updated to "EXTRACTED."

### Risk if left unresolved

Any sprint that attempts ia-* CSS extraction on the assumption that "nothing has been extracted yet" will encounter pre-existing conflicting definitions in `pillar.css` and create further duplicate rules. The QA gate (`scripts/qa-article.sh`) checks for brand palette hex values but does not validate ia-* property values, so CSS regressions introduced by an extraction sprint will not be caught automatically.

---

## C2 — `pillar.css` ia-* values are the visual inverse of PAS V1.0 values used in live articles

**Classification: B — Code is outdated**

### Root cause

When ia-* classes were added to `pillar.css`, different property values were used than PAS V1.0 specifies. The critical divergences:

| Class | `pillar.css` | PAS V1.0 / live articles |
|---|---|---|
| `.ia-punchline` background | `var(--green-dark)` = dark green | `#F9F6EF` = cream |
| `.ia-punchline` color | `var(--gold-light)` = gold | `#1B4332` = dark green |
| `.ia-wrap` max-width | `var(--ia-max-width)` = 920 px | 760 px |
| `.ia-cta a` | plain link (`color:var(--gold-light)`) | gold button (`background:#C9A84C; padding:10px 20px; border-radius:6px`) |

Live articles are unaffected today because their inline `<style>` block overrides `pillar.css` by specificity. The pillar.css ia-* definitions are silently dead for article pages but would activate the moment inline CSS is removed.

### Source of truth

`PUBLICATION-ARTICLE-STANDARD.md` V1.0 is explicitly FROZEN and states: "The exact CSS values above are **the standard**." `DECISIONS.md A7` ("Implement before redesign. Verify before changing.") implies no CSS value change should be made without verification. Per `DECISIONS.md A1`, if documentation and repository disagree, the repository (live articles matching PAS) is correct — which in this case means PAS values are authoritative over `pillar.css`'s divergent values.

### Recommended resolution

Correct `pillar.css` ia-* property values to match PAS V1.0 exactly before any extraction sprint removes article inline CSS. The specific corrections needed are:

- `.ia-punchline`: change background to `#F9F6EF` (cream), color to `#1B4332` (dark green)
- `.ia-wrap`: change `max-width` from `var(--ia-max-width)` to `760px` (or introduce a new dedicated token)
- `.ia-cta a`: add button styling to match PAS (background, padding, border-radius, display)

If any pillar.css value represents an intentional redesign decision rather than an error, that decision must be documented in `DECISIONS.md` and PAS V1.0 must be unfrozen and updated before proceeding. That is a business and design decision, not an engineering one.

### Risk if left unresolved

Any extraction sprint (removing inline CSS from articles) would change the visual rendering of every published article without triggering a QA failure, because `scripts/qa-article.sh` does not validate ia-* property values. `.ia-punchline` would switch from cream background with dark green text to dark green background with gold text — affecting all articles simultaneously on the next deployment.

---

## C3 — `pillar.css` has duplicate conflicting definitions of `.ia-punchline` and `.ia-takeaways`

**Classification: B — Code is outdated**

### Root cause

`pillar.css` defines each class twice, in two separate locations, with conflicting values:

- `.ia-punchline`: defined at line 66 (dark green bg, gold text) and again at lines 135–137 (dark green bg, white text, different padding and border-radius). Neither matches PAS V1.0.
- `.ia-takeaways`: defined at lines 71–75 (dark green bg, gold heading) and again at lines 138–142 (cream-dark bg, border, checkmark bullets). These are visually opposite.

Additionally, line 71 uses `.ia-wrap .ia-takeaways` (higher specificity) while line 138 uses `.ia-takeaways` (lower specificity). The specificity difference means `.ia-wrap .ia-takeaways` (dark green bg) wins over `.ia-takeaways` (cream bg) whenever an `.ia-takeaways` element is inside `.ia-wrap` — which it always is in article pages. The cream-dark definition on line 138 is therefore effectively dead for articles but may apply on pages without `.ia-wrap`.

The duplicate definitions were added in separate unrecorded operations. No sprint report documents this change.

### Source of truth

PAS V1.0 (FROZEN) defines canonical ia-* values. `pillar.css` should contain one definition per class. `DECISIONS.md A8` prohibits HTML/CSS modifications outside an active sprint — if these additions were made without a sprint entry, they were not subject to the normal review process.

### Recommended resolution

Remove the duplicate definitions from `pillar.css`. Specifically:

1. Remove lines 66 and 135–137 (both `.ia-punchline` definitions) and replace with one definition matching PAS V1.0 values.
2. Remove lines 71–75 and 138–142 (both `.ia-takeaways` definitions) and replace with one definition matching PAS V1.0 values.
3. After removing duplicates, run the existing QA suite on a representative set of pages to confirm no regression.

This must be done inside a named sprint with a `CURRENT-SPRINT.md` entry, per `DECISIONS.md A8`.

### Risk if left unresolved

The CSS cascade behaviour of `pillar.css` is currently non-obvious and depends on selector specificity to resolve the conflict between the two definitions. Future edits to either definition may accidentally promote the previously-inactive one to dominance, changing page rendering unexpectedly. Developers reading `pillar.css` cannot know from inspection alone which definition applies.

---

## C4 — `research/packages/` specified throughout pipeline documentation but does not exist on disk

**Classification: A — Documentation is outdated**

### Root cause

`PRODUCTION-PIPELINE.md` V2, `PRODUCTION-ORCHESTRATOR.md` V2, and `RESEARCH-PACKAGE-SPEC.md` all specify `research/packages/<slug>/` as the Research Commander's output directory. This path is referenced at least 15 times across those three documents.

The actual `research/` directory contains: `authority/`, `briefs/`, `cache/`, `content-gap/`, `dataforseo/`, `gsc/`, `manifests/`, `modules/`, `news-radar/`, `product-db/`, `reddit/`, `selen-komplett-guide/`. No `packages/` subdirectory exists. Research outputs appear to be stored per-topic at `research/<topic>/` rather than in the specified `research/packages/<slug>/` path.

The production log `production/logs/20260701-133000-vad-ar-lutein.json` confirms the pipeline has executed at least once (for the `vad-ar-lutein` brief that exists), but `research/packages/vad-ar-lutein/` was never created. This confirms the Research Commander agent does not write to the documented path.

### Source of truth

The repository on disk (`DECISIONS.md A1`). The `research/` directory structure is the authoritative record of where research outputs actually live.

### Recommended resolution

1. Inspect `.opencode/agents/research-commander.md` (locally, not committed to git per `DECISIONS.md B11`) to determine the actual output path the Research Commander writes to.
2. Update `PRODUCTION-PIPELINE.md`, `PRODUCTION-ORCHESTRATOR.md`, and `RESEARCH-PACKAGE-SPEC.md` to reflect the actual output path.
3. If `research/packages/<slug>/` is the intended future output path but has not yet been implemented in the agent, mark it explicitly as "PLANNED — not yet implemented" in those documents.
4. Update the Production Orchestrator's Stage 2 resume detection logic (which checks `research/packages/<slug>/manifest.json`) to match the actual path.

### Risk if left unresolved

The Production Orchestrator's resume-from-checkpoint logic (`docs/PRODUCTION-ORCHESTRATOR.md` Stage 2 detection) checks for `research/packages/<slug>/manifest.json` with `lifecycle = completed`. If the Research Commander writes to a different path, this check never finds the output. Every production run re-executes Stage 2 from scratch rather than resuming from a completed research package, wasting API cost and time. Any engineer following the documentation to locate a specific research package will not find it.

---

## C5 — Phase 4 "ia-* CSS extraction" framed as a simple future task; requires prior reconciliation

**Classification: B — Code is outdated**

### Root cause

The production readiness review described Phase 4 as: "ia-* CSS extraction to `pillar.css` — Removes ~104 lines of duplicated inline CSS per article." This implied pillar.css does not yet have ia-* classes and the task is a straightforward copy-and-remove operation.

The actual state (revealed by C1, C2, C3) is that pillar.css already has ia-* classes with incorrect values and duplicate definitions. The task is not an extraction — it is a reconciliation followed by an extraction. Performing Phase 4 as written would encounter pre-existing conflicts and likely introduce further duplicates.

### Source of truth

C2 and C3 above. The root cause is in the code (pillar.css), not in the Phase 4 description itself.

### Recommended resolution

Revise the Phase 4 entry in `docs/PRODUCTION-READINESS-REVIEW.md` to read:

> **Phase 4 prerequisite:** Resolve C2 and C3 in `docs/CONTRADICTION-RESOLUTION.md` first. `pillar.css` already contains ia-* class definitions with values that diverge from PAS V1.0. Reconcile and deduplicate these before proceeding with any extraction sprint. Only after `pillar.css` carries the correct ia-* values can inline CSS be removed from articles.

Phase 4 should not be scheduled as a standalone sprint item until C2 and C3 are resolved.

### Risk if left unresolved

A sprint that executes Phase 4 as described in the review (treating it as a simple extraction) will import incorrect values from pillar.css into articles, silently changing every article's visual appearance in production. Because `scripts/qa-article.sh` does not validate ia-* property values, no automated gate will catch the regression before deployment.

---

## C6 — PAGE-BUILDER-MARKDOWN-SPEC.md truncation described as "mid-sentence"

**Classification: D — False positive**

### Root cause

The review described the `docs/PAGE-BUILDER-MARKDOWN-SPEC.md` truncation as occurring "mid-sentence." The file actually truncates mid-cell within the Explanation of Fields table, inside a backtick code span in the `author` row: `` `name:  ``. There is no sentence to truncate — the file ends within inline code inside a table cell.

The substantive finding — that the spec is incomplete and provides no body-section mapping — is correct and unaffected by the wording.

### Source of truth

`docs/PAGE-BUILDER-MARKDOWN-SPEC.md` as it exists on disk.

### Recommended resolution

No action required. The wording difference ("mid-sentence" vs. "mid-table-cell") has no bearing on implementation decisions. The important characterization — incomplete spec, no body mapping — stands.

### Risk if left unresolved

None. This is a description imprecision in the review, not a contradiction between project documents or between documents and code.

---

## C7 — `pillar.css` header comment specifies wrong stylesheet link path

**Classification: A — Documentation is outdated**

### Root cause

The header comment block at the top of `pillar.css` instructs:

```
Usage: <link rel="stylesheet" href="/assets/pillar.css">
```

Every live page in the repository uses:

```html
<link rel="stylesheet" href="/pillar.css">
```

The file is located at repository root `/pillar.css`, not at `/assets/pillar.css`. The comment was not updated when the file was moved to or created at the root path.

Additionally, the same comment shows `nav.js` and `footer.js` placed "before `</body>`", which contradicts PAS V1.0 and the actual page pattern — `nav.js` loads at the top of `<body>` (before content), `footer.js` and `components.js` load at the bottom.

### Source of truth

Every live page in the repository (`DECISIONS.md A1`). The actual `<link>` tag and actual file location define the correct path.

### Recommended resolution

Update the `pillar.css` header comment to show the correct path (`/pillar.css`) and the correct script placement pattern (nav.js at top of body, footer.js and components.js at bottom), matching PAS V1.0 and actual page structure. This is a comment-only change with no functional impact.

This change qualifies as documentation maintenance and may be made outside a sprint per `DECISIONS.md A8` ("Documentation files (`*.md`) may be updated at any time") — although the CSS comment is not a `.md` file, the same low-risk logic applies given the change is non-functional.

### Risk if left unresolved

Any Page Builder implementation that follows `pillar.css`'s own documentation to construct the `<link>` tag will generate `<link rel="stylesheet" href="/assets/pillar.css">` — a path that does not exist. The article loads without the design system and renders completely unstyled. This is a high-probability failure mode for a new implementer reading pillar.css as their reference.

---

## C8 — Review reproduces PAS "NOT YET EXTRACTED" note without flagging partial extraction in `pillar.css`

**Classification: D — False positive**

### Root cause

The review stated that ia-* CSS is "inline per-article pending extraction," citing PAS V1.0's "NOT YET EXTRACTED" note. Contradiction C1 identified that this note is outdated. C8 observed that the review reproduced the outdated note — making it a consequence of missing C1, not an independent finding.

There is no contradiction between two project documents on this specific point: PAS says "not yet extracted," and the review says the same thing. The finding in C8 is that both are wrong relative to `pillar.css`. That is fully covered by C1.

### Source of truth

Same as C1. No independent source required.

### Recommended resolution

Resolving C1 (updating the PAS note to reflect the actual partial extraction state) resolves C8 as a consequence. No additional action is needed for C8 specifically.

### Risk if left unresolved

None independent of C1. The risk is the same as C1: implementers believe pillar.css has no ia-* definitions and proceed on that assumption.

---

## Summary

| ID | Classification | Blocking for Markdown-first? | Dependency |
|---|---|---|---|
| C1 | C — Both outdated | Yes — PAS note misleads extraction planning | Resolved when C2 + C3 are fixed |
| C2 | B — Code outdated | **Yes — highest risk** | Must be resolved before Phase 1 Page Builder work |
| C3 | B — Code outdated | **Yes — blocks clean extraction** | Must be resolved before Phase 1 Page Builder work |
| C4 | A — Documentation outdated | Yes — resume detection and cost telemetry are unreliable | Requires inspecting Research Commander agent locally |
| C5 | B — Code outdated | Yes — Phase 4 as written would worsen C2/C3 | Resolved when C2 + C3 are resolved |
| C6 | D — False positive | No | No action required |
| C7 | A — Documentation outdated | **Yes — Page Builder would generate broken link** | One-line comment fix in `pillar.css` |
| C8 | D — False positive | No | Resolved by C1 |

### Sequence recommendation

Resolve in this order before writing any Page Builder code:

1. **C7 first** — one-line comment fix; no cascade risk; prevents the most likely first-hour implementation error
2. **C3 second** — remove duplicate definitions from `pillar.css`; low risk since duplicates are currently silently overridden
3. **C2 third** — correct pillar.css ia-* values to match PAS V1.0; this is the highest-risk item but depends on C3 being resolved first
4. **C4 fourth** — locate the actual Research Commander output path and update pipeline documentation
5. **C1 / C5 / C8** — these resolve automatically once C2, C3 are addressed and PAS note is updated

---

*No code or documents were modified during the preparation of this report.*
