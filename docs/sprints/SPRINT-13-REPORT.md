# Sprint 13 Report — GSC Remediation & Indexability

**Period:** 2026-07-02
**Sprint Goal:** Maximize indexability of 4 orphaned pages and strengthen internal linking for 5 isolated pages.
**Status:** ✅ Completed

---

## Deliverables

### P1 — Critical (all completed)

| # | Task | Status | Verification |
|---|---|---|---|
| 1.1 | Root `.html` copies for 4 orphaned pages | ✅ | All 4 copies have canonical, #site-nav, nav.js, footer.js, components.js, GSC + Pinterest verification meta |
| 1.2 | Add 4 pages to sitemap.xml | ✅ | `levnytt-principer`, `naringsbrist`, `naringsbrist-symptom`, `varfor-ar-jag-trott-hela-tiden` added with `2026-07-02` lastmod |
| 1.3 | Differentiate `naringsbrist` vs `naringsbrist-symptom` | ✅ | naringsbrist: title "Näringsbrist – orsaker, riskgrupper och förebyggande" (52 chars), H1 updated, description refocused on causes/risk/prevention. naringsbrist-symptom: unchanged (already symptom-focused) |

### P2 — Moderate (all completed)

| # | Task | Status | Verification |
|---|---|---|---|
| 2.1 | 5+ internal links each to 5 isolated pages | ✅ | naringsbrist-symptom: 8 links (was 5); neolife-tre-en-en: 17 (was 7); karotenoid-tillskott-vs-mat: 12 (was 5); ala-vs-epa-vs-dha: 22 (was 14); ekologisk-stadning-greenwashing: 12 (was 3) |
| 2.2 | Shorten titles #7 (85→56) and #9 (88→59) | ✅ | neolife-tre-en-en: "NeoLife Tre-en-en – världens första fytonäringstillskott" (56); golden-home-care: "Golden Home Care – LDC diskmedel: verklig kostnad per liter" (59) |
| 2.3 | Fix title-URL mismatch on `/neolife-pro-vitality` | ✅ | Title: "NeoLife Pro Vitality+ – dagligt näringssystem förklarat" (55 chars). Now references "Pro Vitality+" matching URL slug |
| 2.4 | Canonical resolution between tre-en-en pages | ✅ | Both pages keep self-referencing canonicals (already correct). Cross-linking added: tre-en-en links to cellnaring in internal-links-section; cellnaring links to tre-en-en in journey block |

---

## Files Changed

**4 new root copies:**
- `levnytt-principer.html` — copy from `content/articles/`, added #site-nav, components.js, verification meta
- `naringsbrist.html` — copy from `content/articles/`, added verification meta, differentiated
- `naringsbrist-symptom.html` — copy from `content/articles/` (no changes needed — already had all production includes)
- `varfor-ar-jag-trott-hela-tiden.html` — copy from `content/articles/`, added verification meta

**19 modified files:**
- `sitemap.xml` — added 4 new URL entries
- `neolife-tre-en-en.html` — shortened title, added cellnaring internal link
- `golden-home-care.html` — shortened title
- `neolife-pro-vitality.html` — fixed title to include "Pro Vitality+"
- `neolife-tre-en-en-cellnaring.html` — added tre-en-en link in journey block
- 14 files with new internal links added (P2.1)
- 2 content/articles/ source files (side-effect from internal link agents)

---

## Verification

- **HTML structure**: All 8 key modified files verified (`<html>`, `<body>`, `</body>`, `</html>` present)
- **Production includes**: All 4 root copies have canonical, #site-nav, nav.js, footer.js, components.js, GSC + Pinterest verification
- **Title lengths**: All shortened titles confirmed ≤60 chars
- **Internal links**: Counted via grep across all root `.html` files
- **Sitemap**: 4 new entries confirmed present

**Note on QA script**: The existing `scripts/qa-article.sh` validates `content/articles/<slug>/<slug>.html` using the PAS article standard. Our root copies and product pages don't follow PAS or use the subdirectory structure. Manual verification was performed instead covering all 12 QA criteria where applicable.

---

## Risks & Mitigations

| Risk | Status |
|---|---|
| Root copies outrank source files | Acceptable — identical content, root copies have production includes |
| Doubling content inventory | Already mitigated by _redirects (canonical prevents duplicate indexation) |
| Google ignores new root files | Expected — indexing decision is Google's. Sitemap + links improve chances |
| Internal link changes cause regressions | Low risk — all links verified valid, no broken paths |

---

## Next Steps

- Deploy and monitor Google Search Console over sprint period
- Owner approval needed for merge/remove decisions on #8, #9, #10, #11
- Consider creating a root-level QA variant of `qa-article.sh` for non-PAS pages
