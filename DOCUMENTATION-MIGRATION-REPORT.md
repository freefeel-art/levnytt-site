# DOCUMENTATION-MIGRATION-REPORT.md
# LevNytt.se — Documentation Consolidation Report

Date: 2026-06-28

---

## Source documents used

| Document | Language | Date | Role |
|---|---|---|---|
| `LEVNYTT-MUISTIO.md` | Finnish | 2026-06-23 | Operations memo: hosting, git workflow, sponsor IDs, image naming, future pages checklist |
| `AUDIT-REPORT.md` | Finnish | 2026-06-23 | Full site audit: 70 HTML files classified, 13 pillar pages scored, issues documented |
| `SITEMAP-VERIFICATION.md` | English | 2026-06-28 | Post-sprint sitemap completeness check: 73/73 pages confirmed |
| `OPENCODE-REPOSITORY-ANALYSIS.md` | English | 2026-06-28 | AI-generated architecture summary and priority recommendation |
| `docs/databank/LEVNYTT-PRICE-DATABASE.md` | Swedish | April 2026 | NeoLife SE price database and calculator variables |
| Git log (last 30 commits) | Mixed | Through 2026-06-28 | Definitive record of completed work |

---

## Information merged into new documents

### Into PROJECT-STATUS.md

| Source | Information |
|---|---|
| `LEVNYTT-MUISTIO.md` | Hosting (Cloudflare Pages), repo URL, domain, sponsor IDs |
| `OPENCODE-REPOSITORY-ANALYSIS.md` | Architecture overview, tech stack table, page tier definitions |
| `AUDIT-REPORT.md` | Page taxonomy (pillar vs informational article), file structure |
| `SITEMAP-VERIFICATION.md` | Current page count (73), sitemap status (complete) |
| Git log | Completed milestones (Wave B, Wave 3A, sitemap expansion, nav migration, author photo, hosting migration) |

### Into DECISIONS.md

| Source | Decision captured |
|---|---|
| `OPENCODE-REPOSITORY-ANALYSIS.md` | Static HTML architecture, no framework |
| `AUDIT-REPORT.md` | pillar.css as design system, no hardcoded nav, 13-check audit checklist |
| `LEVNYTT-MUISTIO.md` | Sponsor ID handling, image naming convention, verification meta tags |
| `_redirects` (file) | content/articles/ routing pattern, catch-all must be last |
| Git commit history | One-task-at-a-time workflow pattern inferred from sequential named commits (A1, A2, A3, B1…B9, Wave 3A) |
| `sitemap.xml` (file) | Hand-maintained, must be updated with each new page |

### Into PROJECT-ENTRY.md

| Source | Information |
|---|---|
| All source docs | Reading order and source-of-truth hierarchy |
| `LEVNYTT-MUISTIO.md` | Git workflow commands, local path, repo location |
| `OPENCODE-REPOSITORY-ANALYSIS.md` | Component injection pattern summary |

### Into CURRENT-SPRINT.md

| Source | Information |
|---|---|
| Git log | Completed sprint history (Audit A1–A3, Wave B1–B9, sitemap, nav migration, Wave 3A) |
| `AUDIT-REPORT.md` + git log | Proposed next sprint rationale (Wave 3B: informational article migration) |

---

## Conflicts found

### Conflict 1: Page count

- **AUDIT-REPORT.md (2026-06-23):** "70 HTML files"
- **SITEMAP-VERIFICATION.md (2026-06-28):** "73 production HTML pages"
- **Resolution:** The difference is real — 3 new articles were added after the audit (`vad-ar-vitamin-b12`, `hur-fungerar-natverksmarknadsforing-egentligen`, and one other). The 2026-06-28 figure of 73 is the current truth. Both figures were accurate at their respective dates.

### Conflict 2: Sitemap completeness

- **OPENCODE-REPOSITORY-ANALYSIS.md:** Recommended adding ~27 missing informational articles to `sitemap.xml` as the highest-priority task.
- **SITEMAP-VERIFICATION.md (2026-06-28):** Confirmed sitemap is complete — all 73 pages are present.
- **Resolution:** The OPENCODE analysis was based on the AUDIT-REPORT (dated 2026-06-23). Between that audit and 2026-06-28, all missing pages were added to `sitemap.xml` (git commit `edf826a` and subsequent commits). The SITEMAP-VERIFICATION is the current truth. The OPENCODE recommendation is superseded.

### Conflict 3: LEVNYTT-MUISTIO.md directory listing is outdated

- **LEVNYTT-MUISTIO.md:** Lists a directory structure with ~15 files including `nutriance-organic.html`.
- **Reality (2026-06-28):** The repo has 73 HTML files. `nutriance-organic.html` does not exist (it redirects to `personlig-vard.html`). Many files listed as "tuleva" (future) in the memo now exist.
- **Resolution:** The memo was a snapshot from early in the project. `PROJECT-STATUS.md` contains the current file structure. The memo is superseded for structural purposes.

### Conflict 4: AUDIT-REPORT pillar page failures are resolved

- **AUDIT-REPORT.md:** Documents that 7 pillar pages fail `at_least_3_breakpoints`, 3 fail `links_pillar_css`, 3 fail `og_image_present`, etc.
- **Git log:** Commits B1–B9 and subsequent work resolved all these failures.
- **Resolution:** The audit failures no longer exist. `PROJECT-STATUS.md` records that all pillar pages pass 13/13 as of 2026-06-28. The AUDIT-REPORT remains a useful historical record but its failure list is obsolete.

### Conflict 5: LEVNYTT-MUISTIO.md future pages list partially obsolete

- **LEVNYTT-MUISTIO.md:** Lists `/neolife-carotenoid-complex/` as a future pillar (not yet built).
- **Reality:** `neolife-carotenoid-complex.html` exists and is a full pillar page passing 13/13.
- **Resolution:** Several pages marked "tuleva" in the memo were completed. `PROJECT-STATUS.md` lists only the genuinely unbuilt future pages.

---

## Information intentionally discarded

| Information | Source | Reason discarded |
|---|---|---|
| Detailed file-by-file audit table (70 rows) | `AUDIT-REPORT.md §A` | Issues are resolved. The full table is preserved in `AUDIT-REPORT.md` as a historical record. Not needed in operational docs. |
| EPÄSELVÄ-class page analysis (C1–C6) | `AUDIT-REPORT.md §C` | The open questions were resolved: `neolife-all-c`/`neolife-vita-squares` subdir duplicates deleted, `personlig-vard` nav dedup fixed, `finns-det-billigare-alternativ` got a canonical. `AUDIT-REPORT.md` preserves the analysis. |
| Full trailing-slash inconsistency tables | `AUDIT-REPORT.md §D2, D6` | Functionally resolved by Cloudflare Pretty URLs and sitemap updates. Noted in `DECISIONS.md §7` as known exceptions. Full tables not needed in operational docs. |
| Git workflow command examples | `LEVNYTT-MUISTIO.md` | Standard git commands not project-specific enough to warrant repetition. Summarized in `PROJECT-ENTRY.md`. |
| Image-to-page mapping table | `LEVNYTT-MUISTIO.md` | Operational detail for manual image management. Preserved in `LEVNYTT-MUISTIO.md`. Not needed in strategic docs. |
| OPENCODE architecture summary | `OPENCODE-REPOSITORY-ANALYSIS.md` | Fully superseded by `PROJECT-STATUS.md`. |
| "Highest-priority task" recommendation | `OPENCODE-REPOSITORY-ANALYSIS.md` | The recommended task (sitemap completion) was already done when the recommendation was written. Superseded. |
| Sprint history narrative prose | `OPENCODE-REPOSITORY-ANALYSIS.md` | Condensed into the milestone table in `PROJECT-STATUS.md`. |

---

## Recommendations for retiring old documentation

| Document | Recommendation |
|---|---|
| `LEVNYTT-MUISTIO.md` | **Keep but freeze.** Valuable for: sponsor IDs, verification meta tags, image naming conventions, git workflow reference. The directory listing and future-pages checklist are outdated but harmless. Add a note at the top: "Operational reference — see PROJECT-STATUS.md for current state." Do not delete. |
| `AUDIT-REPORT.md` | **Keep as archive.** The full page classification, audit scores, and issue analysis are valuable engineering history. The failure lists are resolved but document what the site looked like before remediation. No changes needed. |
| `SITEMAP-VERIFICATION.md` | **Keep as a dated task record.** Documents that the sitemap was verified complete on 2026-06-28. Future sitemap verifications should create new dated files or update this one. |
| `OPENCODE-REPOSITORY-ANALYSIS.md` | **Can be deleted.** Fully superseded by `PROJECT-STATUS.md`. Contains no unique information. Recommendation: delete in a future cleanup commit. |
| `docs/databank/LEVNYTT-PRICE-DATABASE.md` | **Keep and maintain.** This is an active reference, not a historical document. Update when NeoLife publishes new price lists. |
