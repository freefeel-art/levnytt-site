# SPRINT-13-PLAN.md — GSC Non-Indexed URL Remediation

**Status:** Proposed (awaiting approval)
**Target start:** 2026-07-02
**Estimated duration:** 1 session

---

## Sprint Objective

Resolve the highest-impact findings from the GSC Content Audit (`docs/gsc/GSC-CONTENT-AUDIT.md`) to get 4+ non-indexed URLs into Google's index. Focus on root-file publishing, sitemap inclusion, and topic deduplication — no content rewriting, no redesign.

---

## Deliverables

### P1 — Critical (Expected SEO Impact: HIGH)

| # | Task | Source | Verification |
|---|------|--------|-------------|
| 1.1 | Publish root `.html` files for 4 orphaned pages | GSC P1.1 | `ls <slug>.html` for each |
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

- Update `CURRENT-SPRINT.md` — close Sprint 12 with actual deliverables, open Sprint 13
- Update `PROJECT-STATUS.md` — add Sprint 11 and Sprint 12 milestones
- Update `docs/plans/PHASE-2-ROADMAP.md` — add Sprint 11, Sprint 12, and Sprint 13 milestones
- Create `docs/sprints/SPRINT-12-REPORT.md` — Sprint 12 close report
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
- Owner approval required before implementation begins
- No OpenRouter/Ollama required — all work is file manipulation + grep

---

## Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Topic deduplication (#2 vs #5) is hard to resolve without rewriting content | Medium | Focus on meta differentiation (titles, descriptions, H1s) — content rewrite deferred |
| Adding 4 root files may trigger Cloudflare Pages re-deploy with unexpected routing | Low | Root files coexist with `_redirects` — Cloudflare handles precedence |
| Internal link additions may be inconsistent with existing linking style | Low | Follow existing patterns (contextual links in relevant cluster pages) |

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
9. `CURRENT-SPRINT.md`, `PROJECT-STATUS.md`, `PHASE-2-ROADMAP.md` updated
10. Sprint reports created in `docs/sprints/`
