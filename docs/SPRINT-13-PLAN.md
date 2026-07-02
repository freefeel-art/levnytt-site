# SPRINT-13-PLAN.md — GSC Non-Indexed URL Remediation

**Status:** Proposed (awaiting approval)
**Target start:** 2026-07-02
**Estimated duration:** 1 session

---

## Sprint Objective

Maximize the indexability of the highest-priority non-indexed URLs by resolving all repository-side issues identified in the GSC audit.

The objective is to improve Google's ability to index the pages. Actual indexing remains Google's decision.

---

## Deliverables

### P1 — Critical (Expected SEO Impact: HIGH)

| # | Task | Source | Verification |
|---|------|--------|-------------|
| 1.1 | Publish root `.html` files for 4 orphaned pages (`levnytt-principer`, `naringsbrist`, `varfor-ar-jag-trott-hela-tiden`, `naringsbrist-symptom`) | GSC P1.1 | `ls <slug>.html` for each |
| 1.2 | Add 4 orphaned pages to `sitemap.xml` | GSC P1.2 | `grep <slug> sitemap.xml` |
| 1.3 | Resolve duplication: differentiate `naringsbrist` vs `naringsbrist-symptom` | GSC P1.3 | Distinct H1 + meta description pair |

### P2 — Moderate (Expected SEO Impact: MEDIUM)

| # | Task | Source | Verification |
|---|------|--------|-------------|
| 2.1 | Add contextual internal links to isolated pages (target: 5+ new links each to #5, #7, #8, #10, #11) | GSC P2.1 | `rg "href=.*<slug>"` count per page |
| 2.2 | Shorten overlong titles (#7: 85→60 chars, #9: 88→60 chars) | GSC P2.2 | `rg "<title>" <file>` length check |
| 2.3 | Fix title-URL mismatch on `/neolife-pro-vitality` | GSC P2.4 | Title contains "Pro Vitality" |
| 2.4 | Set canonical resolution between `/neolife-tre-en-en` and `/neolife-tre-en-en-cellnaring` | GSC P2.5 | Single canonical direction |

### Documentation

- Open Sprint 13 in `CURRENT-SPRINT.md`
- Update `PROJECT-STATUS.md` — update "Next Focus" to reflect GSC remediation priority
- Update `docs/plans/PHASE-2-ROADMAP.md` — add Sprint 13 milestone upon completion
- Create `docs/sprints/SPRINT-13-REPORT.md` — Sprint 13 close report (tick at end)

---

## Out of Scope

- Content rewriting or expanding thin FAQ pages (#8, #10, #11) — deferred to future sprint
- Product Entity System — separate initiative
- Merge/remove actions (#8→merge, #9→merge, #10→remove, #11→remove) — require owner decision first
- Any changes to `nav.js`, `footer.js`, `components.js`, `pillar.css`, or `_redirects`

---

## Dependencies

- All 4 `content/articles/<slug>.html` source files must exist (verified: they do)
- No OpenRouter/Ollama required — all work is file manipulation + grep

---

## Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Topic deduplication (#2 vs #5) is hard to resolve without rewriting content | Medium | Focus on meta differentiation (titles, descriptions, H1s) — content rewrite deferred |
| Adding 4 root files may trigger Cloudflare Pages re-deploy with unexpected routing | Low | Root files coexist with `_redirects` — Cloudflare handles precedence; verify after deploy |
| Internal link additions may be inconsistent with existing linking style | Low | Follow existing patterns (contextual links in relevant cluster pages) |

---

## Rollback Plan

If any Sprint 13 production change causes:

- routing problems
- deployment failures
- Production QA failures (see DoD #11)
- unexpected SEO regressions

then:

1. Revert the affected commit: `git revert <commit-hash>`
2. Push the revert: `git push`
3. Document the reason in the commit message
4. Stop Sprint 13 until the issue is reviewed and resolved

---

## Definition of Done

1. All 4 orphaned pages have root `.html` files in `/`
2. All 4 orphaned pages are in `sitemap.xml`
3. `naringsbrist` and `naringsbrist-symptom` have distinct titles, meta descriptions, and H1s
4. Title lengths on #7 and #9 are ≤60 chars
5. `/neolife-pro-vitality` title includes "Pro Vitality"
6. Internal links added to isolated pages (5+ each)
7. All changes committed and pushed
8. No production errors after deployment
9. `CURRENT-SPRINT.md` opened for Sprint 13
10. Sprint report created in `docs/sprints/SPRINT-13-REPORT.md`
11. Every modified page must pass the Production QA validator (`scripts/qa-article.sh`) with GREEN status before Sprint 13 can be considered complete
