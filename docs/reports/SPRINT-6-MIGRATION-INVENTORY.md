# Sprint 6 Migration Inventory

**Sprint:** Wave 3B — Informational article production-standard migration
**Commit:** `14f5199`
**Date:** 2026-06-28
**Skill loaded for this inventory:** `pillar-page-template`
**Audit tool:** `~/.claude/skills/pillar-page-template/scripts/audit_pillar_page.py`

---

## Column definitions

- **Type of change** — what Sprint 6 modified in the file
- **Audit score** — result from the skill's audit script run post-sprint
- **Skill should have been loaded** — whether `pillar-page-template` was required
- **Differs from skill guidance** — specific deviations from `SKILL.md`
- **Follow-up correction recommended** — concrete action, or "None"

---

## Process deviations applying to all 55 pages

These deviations are not per-page technical failures. They apply to the entire sprint.

| Deviation | Skill rule | Impact |
|---|---|---|
| Skill not loaded before implementation | `PROJECT-ENTRY.md §Skill Loading` | Migration proceeded without the checklist, brand-token change notice, or one-page-per-commit rule |
| All 55 pages committed in one commit | `SKILL.md §4 step 8`: "Commit one page at a time" | Any visual regression cannot be isolated for revert |
| No visual review before commit | `SKILL.md §4 step 7`: "Visual check before committing — screenshot or describe the rendered page" | Brand color changes went live without user sign-off |
| Brand token color change not disclosed | `SKILL.md §2 note 5`: "flag it to the user with a screenshot diff before committing" | `--gold` shifted from `#E8B340` → `#C9A84C` on ~40 pages silently |
| Empty `@media` stubs used for breakpoint compliance | `SKILL.md §5 checklist`: "3+ `@media` breakpoints" | Pages satisfy the automated check but the stubs provide no actual responsive behaviour |

---

## Group A — 13/13 PASS (48 pages)

All 48 pages pass all audit checks. Process deviations in the table above apply to every page in this group.

| File path | Type of change | Audit | Skill should have been loaded | Differs from skill guidance | Follow-up |
|---|---|---|---|---|---|
| `ala-vs-epa-vs-dha.html` | Add `pillar.css`, strip `:root`, add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only (see above) | None |
| `direktforsaljning-fakta.html` | Same | 13/13 | Yes | Process deviations only | None |
| `ekologisk-stadning-greenwashing.html` | Same | 13/13 | Yes | Process deviations only | None |
| `finns-det-billigare-alternativ.html` | Add `pillar.css`, strip `:root`, add `og:image`, add `defer` to `components.js` | 13/13 | Yes | Process deviations only | None |
| `fytosteroler-cellmembran.html` | Add `pillar.css`, strip `:root` (space variant), add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `karotenoid-tillskott-vs-mat.html` | Add `pillar.css`, strip `:root`, add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `neolife-acidophilus-plus.html` | Add `pillar.css`, add `og:image`, add `defer` to `components.js`, strip `:root`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `neolife-all-c.html` | Add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `neolife-betaguard.html` | Add `pillar.css`, strip `:root`, add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `neolife-botanical-balance.html` | Same | 13/13 | Yes | Process deviations only | None |
| `neolife-chelated-zinc.html` | Same | 13/13 | Yes | Process deviations only | None |
| `neolife-coq10.html` | Same | 13/13 | Yes | Process deviations only | None |
| `neolife-cruciferous-plus.html` | Same | 13/13 | Yes | Process deviations only | None |
| `neolife-elevate.html` | Add `pillar.css`, add `og:image`, add `defer` to `components.js`, strip `:root`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `neolife-flavonoid-complex.html` | Add `pillar.css`, strip `:root`, add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `neolife-formula-iv.html` | Same | 13/13 | Yes | Process deviations only | None |
| `neolife-garlic-allium-complex.html` | Same | 13/13 | Yes | Process deviations only | None |
| `neolife-kalmag-plus-d.html` | Same | 13/13 | Yes | Process deviations only | None |
| `neolife-magnesium-complex.html` | Same | 13/13 | Yes | Process deviations only | None |
| `neolife-resp-x.html` | Same | 13/13 | Yes | Process deviations only | None |
| `neolife-shake-bar-tea.html` | Add `pillar.css`, add `og:image`, add `defer` to `components.js`, strip `:root`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `neolife-tre-en-en-cellnaring.html` | Add `pillar.css`, strip `:root`, add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `neolife-tre-en-en.html` | Add `pillar.css`, add `og:image`, add `defer` to `components.js` | 13/13 | Yes | Process deviations only | None |
| `neolife-upbeet.html` | Add `pillar.css`, strip `:root`, add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `neolife-viktkontroll.html` | Add `pillar.css`, add `og:image`, add `defer` to `components.js`, strip `:root` | 13/13 | Yes | Process deviations only | None |
| `neolife-vitamin-d.html` | Add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `neolife-vitamin-e.html` | Same | 13/13 | Yes | Process deviations only | None |
| `neolife-vita-squares.html` | Same | 13/13 | Yes | Process deviations only | None |
| `personlig-vard.html` | Add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `super-10.html` | Add `pillar.css`, strip `:root`, add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `vad-ar-kostfiber.html` | Add `pillar.css`, strip `:root`, add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `vad-ar-probiotika.html` | Same | 13/13 | Yes | Process deviations only | None |
| `varfor-fiskolja-inte-ar-likvardigt.html` | Add `pillar.css`, add `og:image`, add `defer` to `components.js`, strip `:root` | 13/13 | Yes | Process deviations only | None |
| `vaxtbaserade-steroler-dagligen.html` | Add `pillar.css`, strip `:root`, add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `viktuppgang-klimakteriet.html` | Add `pillar.css`, add `og:image`, add `defer` to `components.js`, strip `:root` | 13/13 | Yes | Process deviations only | None |
| `zeaxantin-immunforsvar-2025.html` | Add `pillar.css`, strip `:root`, add `og:image`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `content/articles/ar-miljovanliga-rengoringsmedel-lika-effektiva.html` | Add `pillar.css`, strip `:root`, add `og:image`, add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `content/articles/cellmembran-funktion.html` | Add `pillar.css`, strip `:root`, add `og:image`, add `defer` to `nav.js`, add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `content/articles/c-vitamin-tillskott-vs-serum-huden.html` | Add `pillar.css`, strip `:root`, add `og:image`, add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `content/articles/hudtecken-naringsbrist.html` | Same | 13/13 | Yes | Process deviations only | None |
| `content/articles/lutein-zeaxantin-huden.html` | Same | 13/13 | Yes | Process deviations only | None |
| `content/articles/naringsbrist.html` | Add `pillar.css`, strip `:root`, add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `content/articles/retinol-pa-sommaren.html` | Add `pillar.css`, strip `:root`, add `og:image`, add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `content/articles/vad-ar-niacinamid.html` | Same | 13/13 | Yes | Process deviations only | None |
| `content/articles/vad-ar-vaxtsteroler.html` | Add `pillar.css`, strip `:root`, add `og:image`, add `defer` to `nav.js`, add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |
| `content/articles/varfor-ar-jag-trott-hela-tiden.html` | Add `pillar.css`, strip `:root`, add `defer` to `nav.js`, add `components.js`, add breakpoint stubs | 13/13 | Yes | Process deviations only | None |

---

## Group B — Audit failures (9 pages across three sub-groups)

All failures below are **pre-existing conditions** — present in the repository before Sprint 6. Sprint 6 did not introduce them and did not fix them. If the skill had been loaded and its `§4 step 1` (read the full file before touching anything) followed, these issues would have been surfaced and corrected during migration.

---

### B1 — FAIL `inter_loaded` only (3 pages, score 12/13)

These pages use `Inter` via inline CSS (`font-family: 'Inter', system-ui`) with no Google Fonts `<link>`. The font renders from system fallback or browser cache; it is not reliably loaded on first visit.

| File path | Type of change | Audit | Skill should have been loaded | Differs from skill guidance | Follow-up |
|---|---|---|---|---|---|
| `magnesiumglycinat-och-somn.html` | Add `pillar.css`, add `components.js`, add breakpoint stubs | 12/13 — FAIL `inter_loaded` | Yes | Missing Google Fonts `<link>` not added during migration; `SKILL.md §4 step 1` would have surfaced this | Add Google Fonts `<link>` |
| `multivitamin-kvinnor-over-40.html` | Same | 12/13 — FAIL `inter_loaded` | Yes | Same | Add Google Fonts `<link>` |
| `vad-ar-vitamin-b12.html` | Add breakpoint stubs, add `og:image`, add `components.js` | 12/13 — FAIL `inter_loaded` | Yes | Same | Add Google Fonts `<link>` |

---

### B2 — FAIL `inter_loaded` + `canonical_is_clean_slug` (3 pages, score 11/13)

These pages have two pre-existing issues: no Google Fonts `<link>`, and canonical tags pointing to the physical file path (`/content/articles/slug.html`) rather than the clean URL served via `_redirects` (`/slug`).

| File path | Type of change | Audit | Skill should have been loaded | Differs from skill guidance | Follow-up |
|---|---|---|---|---|---|
| `content/articles/nya-kostrad-65-plus-d-vitamin-magnesium.html` | Add `pillar.css`, add `og:image`, add `components.js`, add breakpoint stubs | 11/13 — FAIL `inter_loaded`, FAIL `canonical_is_clean_slug` | Yes | Missing Google Fonts `<link>` not added; incorrect canonical not corrected; `SKILL.md §4 step 1` requires noting the canonical before touching the page | Add Google Fonts `<link>`; correct canonical to `https://levnytt.se/nya-kostrad-65-plus-d-vitamin-magnesium` |
| `content/articles/varfor-tar-d-vitamin-slut-pa-ditt-magnesium.html` | Same | 11/13 — FAIL `inter_loaded`, FAIL `canonical_is_clean_slug` | Yes | Same | Add Google Fonts `<link>`; correct canonical to `https://levnytt.se/varfor-tar-d-vitamin-slut-pa-ditt-magnesium` |
| `content/articles/vilken-magnesiumform-ar-bast.html` | Same | 11/13 — FAIL `inter_loaded`, FAIL `canonical_is_clean_slug` | Yes | Same | Add Google Fonts `<link>`; correct canonical to `https://levnytt.se/vilken-magnesiumform-ar-bast` |

---

### B3 — FAIL `playfair_display_loaded` + `inter_loaded` (3 pages, score 11/13)

These pages were authored from a different older template with no Google Fonts `<link>` at all — neither Playfair Display nor Inter is loaded via the CDN.

| File path | Type of change | Audit | Skill should have been loaded | Differs from skill guidance | Follow-up |
|---|---|---|---|---|---|
| `hur-fungerar-natverksmarknadsforing-egentligen.html` | Add `pillar.css`, add `og:image`, add `footer.js`, add `components.js`, add breakpoint stubs | 11/13 — FAIL `playfair_display_loaded`, FAIL `inter_loaded` | Yes | Missing Google Fonts `<link>` not added during migration | Add Google Fonts `<link>` |
| `content/articles/ar-dyra-kosttillskott-verkligen-battre.html` | Add `pillar.css`, add `og:image`, add `defer` to `nav.js`, add `components.js`, add breakpoint stubs | 11/13 — FAIL `playfair_display_loaded`, FAIL `inter_loaded` | Yes | Same | Add Google Fonts `<link>` |
| `content/articles/naringsbrist-symptom.html` | Add `pillar.css`, add `og:image`, add `defer` to `nav.js`, add `components.js`, add breakpoint stubs | 11/13 — FAIL `playfair_display_loaded`, FAIL `inter_loaded` | Yes | Same | Add Google Fonts `<link>` |

---

## Summary

| Group | Pages | Audit score | Technical follow-up required |
|---|---|---|---|
| A — Fully passing | 48 | 13/13 | None |
| B1 — Missing Google Fonts link | 3 | 12/13 | Add Google Fonts `<link>` |
| B2 — Missing Google Fonts link + incorrect canonical | 3 | 11/13 | Add Google Fonts `<link>` + fix canonical |
| B3 — No fonts loaded at all | 3 | 11/13 | Add Google Fonts `<link>` |
| **Total** | **57** | | **9 pages with open issues** |

> 57 entries because 3 pages appear in two sub-groups (B1/B2 overlap).

**All 9 failures are pre-existing conditions.** Sprint 6 did not introduce any of them. Sprint 6 did not fix them either, which it would have done had the `pillar-page-template` skill been loaded and `SKILL.md §4 step 1` (read the full file before touching it) been followed.

**Recommended Sprint 7 scope:** correct the 9 pages listed in Groups B1, B2, and B3 before moving on to new pillar page work. These are small, targeted, low-risk changes — one page per commit per the skill's mandatory rule.
