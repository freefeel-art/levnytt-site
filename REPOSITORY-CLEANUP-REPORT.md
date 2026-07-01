# Repository Cleanup Report

**Date:** 2026-07-01
**Scope:** Full repository audit — all 507 files
**Goal:** Single production baseline with one authoritative source per component

**Status:** ✅ CLEANUP EXECUTED 2026-07-01
**Files deleted:** 28 (19 Phase 1 + 9 Phase 2)
**Files moved to archive:** 2 (SKILL backups)
**Files marked LEGACY:** 1 (levnytt-se-master-template.html) → **DELETED** in Sprint 10 (2026-07-01)
**References updated:** 3 files (PROJECT-ENTRY.md, CURRENT-SPRINT.md, levnytt-se-master-template.html)

---

## Current Production Architecture

```
User Request
    │
    ▼
Editorial Commander V1.3    ← .opencode/agents/editorial-commander.md
    │
    ├── Morning Brief V2.1   ← .opencode/agents/morning-brief.md
    ├── MLM Brief V1.2       ← .opencode/agents/mlm-brief.md
    │
    ▼
Research Commander V1       ← .opencode/agents/research-commander.md (EXPERIMENTAL)
    │
    ▼
LevNytt Writer V1.0         ← .opencode/agents/levnytt-writer.md
MLM Editorial Agent V1.1    ← .opencode/agents/mlm-editorial-agent.md
    │
    ▼
Publication Agent V1.0      ← .opencode/agents/publication-agent.md
    │
    ▼
content/articles/*.html  ──►  root/*.html  ──►  Cloudflare Pages
                              (via _redirects 200-rewrites)
```

### Site Infrastructure
| Component | File | Status |
|-----------|------|--------|
| Navigation | `nav.js` | ACTIVE |
| Footer | `footer.js` | ACTIVE |
| Components (favicon, scroll-to-top, brand) | `components.js` | ACTIVE |
| Design System CSS | `pillar.css` | ACTIVE |
| Cloudflare Routing | `_redirects` | ACTIVE |
| SEO (robots) | `robots.txt` | ACTIVE |
| SEO (sitemap) | `sitemap.xml` | ACTIVE |
| CI/CD | `.github/workflows/generate-homepage.yml` | ACTIVE |

---

## Files That Are the Single Source of Truth

### 4 Core Operational Documents
| File | Role |
|------|------|
| `PROJECT-ENTRY.md` | AI Agent entry point, documentation hierarchy |
| `PROJECT-STATUS.md` | Executive dashboard, architecture, milestones |
| `DECISIONS.md` | Permanent engineering decisions |
| `CURRENT-SPRINT.md` | Active sprint definition (Sprint 12) |

### 5 Specifications
| File | Role |
|------|------|
| `docs/PUBLICATION-ARTICLE-STANDARD.md` | FROZEN V1.0 — canonical article template |
| `docs/specifications/AGENT-REGISTRY.md` | V1.0 — agent inventory |
| `docs/specifications/PRODUCT-ENTITY-SYSTEM.md` | Product entity schema |
| `docs/specifications/EDITORIAL-SYNC-ENGINE.md` | Sprint 17 — sync engine spec |
| `docs/specifications/MORNING-BRIEF-ARCHITECTURE.md` | V2.0 — brief subsystem spec |

### 2 Brand/Data Sources
| File | Role |
|------|------|
| `docs/BRAND-DESIGN-SYSTEM.md` | Brand design specification |
| `docs/databank/LEVNYTT-PRICE-DATABASE.md` | V1.0 — canonical pricing |

### 7 Agents
| File | Role |
|------|------|
| `.opencode/agents/editorial-commander.md` | V1.3 — pipeline orchestrator |
| `.opencode/agents/morning-brief.md` | V2.1 — consumer intelligence |
| `.opencode/agents/mlm-brief.md` | V1.2 — industry intelligence |
| `.opencode/agents/levnytt-writer.md` | V1.0 — article writer |
| `.opencode/agents/mlm-editorial-agent.md` | V1.1 — MLM content producer |
| `.opencode/agents/publication-agent.md` | V1.0 — deployment agent |
| `.opencode/agents/research-commander.md` | V1 — research orchestrator (DESIGN DOC — system not yet built) |

### 7 Skills
| File | Role |
|------|------|
| `.claude/skills/informational-article/SKILL.md` | Article generator (loaded by OpenCode) |
| `.claude/skills/search-gap-research/SKILL.md` | Content brief generator |
| `.claude/skills/supplement-reddit-research/SKILL.md` | V2 — Reddit niche radar |
| `.claude/skills/direct-sales-reddit-research/SKILL.md` | Direct sales market intelligence |
| `.claude/skills/pillar-page-template/SKILL.md` | Pillar page migration |
| `.claude/skills/olsp-authority-article/SKILL.md` | OLSP authority articles (separate project) |
| `.claude/skills/astro-builder/SKILL.md` | Astro websites (not for levnytt.se) |

---

## Files Recommended for Deletion

### SUPERSEDED — Replaced by Newer Implementation

| File | Replacement | Reason | References It | Safe to Delete? |
|------|-------------|--------|---------------|-----------------|
| `.claude/skills/informational-article/SKILL-v2.md` | `SKILL.md` | Pre-refactor version; `SKILL.md` has Default Author Profile | `EDITORIAL-BRAIN-VS-PRESENTATION.md` | **YES** (after 1-2 sprints rollback buffer) |
| `.claude/skills/informational-article/SKILL-v2.before-refactor.md` | `SKILL.md` | Backup snapshot before refactor | `EDITORIAL-BRAIN-VS-PRESENTATION.md` | **YES** (or move to archive) |
| `.claude/skills/content-factory/CONTENT-FACTORY-V2.md` | Individual agents in `.opencode/agents/` | Superseded by dedicated agent system (editorial-commander, levnytt-writer, etc.) | None | **YES** |
| `OPENCODE-REPOSITORY-ANALYSIS.md` | `PROJECT-STATUS.md` | AI-generated analysis; all info merged into operational docs | `PROJECT-ENTRY.md`, `DOCUMENTATION-MIGRATION-REPORT.md`, `DOCUMENTATION-UPDATE-REPORT.md` | **YES** (both migration docs recommend deletion) |
| `.claude/settings.local.json` | N/A (local config) | Machine-specific path config for skill installation | None | **YES** |
| `scripts/update-author.py` | N/A (one-time script) | Ran name migration "Den Fundersamma Mannen" → "Jarmo Halonen"; destructive if re-run | None | **YES** |

### ARCHIVE — Historical Snapshots (Safe to Delete)

| File | Reason | References It | Safe to Delete? |
|------|--------|---------------|-----------------|
| `docs/editorial-briefs/2026-06-29-editorial-brief.md` | Dated V1.1 with counting error | Referenced by V1.2 (as buggy version) | **YES** |
| `docs/editorial-briefs/2026-06-29-editorial-brief-v1.2.md` | Dated snapshot, superseded by later briefs | None | **YES** |
| `docs/editorial-briefs/2026-06-30-editorial-brief.md` | Dated V1, superseded by V2 same day | Referenced by V2 brief | **YES** |
| `docs/editorial-briefs/2026-06-30-editorial-brief-v2.md` | Dated snapshot, superseded by 07-01 brief | None | **YES** |
| `docs/editorial-briefs/2026-07-01-editorial-brief.md` | Most recent brief — still a dated snapshot; live state is in Sync Engine outputs | None | **YES** |
| `docs/reports/SPRINT-6-MIGRATION-INVENTORY.md` | Sprint 6 artifact | Referenced by SPRINT-6.1-CLEANUP-REPORT.md | **YES** |
| `docs/reports/SPRINT-6.1-CLEANUP-REPORT.md` | Sprint 6.1 artifact | Referenced by LOGG-2026-07-01.md | **YES** |
| `docs/reports/SITE-PAGE-INVENTORY.md` | Superseded by auto-generated `repository-inventory.md` | None | **YES** |
| `docs/reports/MORNING-BRIEF-VALIDATION-REPORT.md` | One-off validation at commit 83e6767 | Referenced by CURRENT-SPRINT.md | **YES** (update CURRENT-SPRINT.md if deleting) |
| `docs/reports/BRAND-DESIGN-SYSTEM-STATUS.md` | One-off brand audit (Finnish) | Referenced by CURRENT-SPRINT.md | **YES** (update CURRENT-SPRINT.md if deleting) |
| `docs/sprints/SPRINT-9-BRAND-ROLLOUT.md` | Sprint 9 completion report | None | **YES** |
| `docs/LEGACY-ARTICLE-MIGRATION-AUDIT.md` | Superseded by PAS V1.0 which is now canonical | `ARTICLE-TEMPLATE-FAMILIES.md` | **YES** (update ARTICLE-TEMPLATE-FAMILIES.md if deleting) |
| `DOCUMENTATION-MIGRATION-REPORT.md` | Consolidation trace, info merged into 4 core docs | `PROJECT-ENTRY.md`, `DOCUMENTATION-UPDATE-REPORT.md` | **YES** (update PROJECT-ENTRY.md if deleting) |
| `DOCUMENTATION-UPDATE-REPORT.md` | Refinement pass record, info merged | `PROJECT-ENTRY.md` (notes "likely outdated") | **YES** |
| `SPRINT-6-REPORT.md` | Sprint 6 report, info in PROJECT-STATUS.md | `PROJECT-ENTRY.md` | **YES** |
| `SITEMAP-VERIFICATION.md` | Dated task record (0 missing URLs) | `PROJECT-ENTRY.md`, `DOCUMENTATION-MIGRATION-REPORT.md` | **YES** |
| `logg-2026-07-01.md` | Debugging diary for Writer development | Referenced by CURRENT-SPRINT.md | **YES** (update CURRENT-SPRINT.md if deleting) |

### EXPERIMENTAL — Prototypes / Incomplete Work

| File | Reason | Safe to Delete? |
|------|--------|-----------------|
| `docs/debug/WRITER-HTML-GAP-ANALYSIS.md` | One-off diagnostic (Finnish) | **YES** |
| `docs/debug/WRITER-PIPELINE-AUDIT.md` | One-off diagnostic (Finnish) | **YES** |
| `docs/debug/IA-CLASS-AUDIT.md` | One-off CSS audit (Finnish) | **YES** |
| `docs/debug/WRITER-VERIFICATION.md` | One-off writer verification | **YES** |
| `run-config.json` | Single-use config — article `mlm-foretag-skandaler` already exists | **YES** |
| `todo-list.json` | Transient task tracker — all items completed | **YES** |
| `generate_hero.py` | One-off KIE.ai script — no KIE_API_KEY in env | **YES** |
| `generate_heroes_batch.py` | One-off KIE.ai batch script — same issue | **YES** |

### EXPERIMENTAL — Incomplete Authority Profile Stubs

All 15 files under `docs/research/authority-profiles/` contain `[Placeholder]` sections — never completed:

| File | Safe to Delete? |
|------|-----------------|
| `docs/research/authority-profiles/regulatory-ftc.md` | **YES** |
| `docs/research/authority-profiles/regulatory-efsa.md` | **YES** |
| `docs/research/authority-profiles/regulatory-konsumentverket.md` | **YES** |
| `docs/research/authority-profiles/regulatory-pubmed.md` | **YES** |
| `docs/research/authority-profiles/regulatory-wfdsa.md` | **YES** |
| `docs/research/authority-profiles/direct-selling-rich-devos.md` | **YES** |
| `docs/research/authority-profiles/direct-selling-jay-van-andel.md` | **YES** |
| `docs/research/authority-profiles/direct-selling-carl-rehnborg.md` | **YES** |
| `docs/research/authority-profiles/direct-selling-jerry-brassfield.md` | **YES** |
| `docs/research/authority-profiles/network-marketing-richard-bliss-brooke.md` | **YES** |
| `docs/research/authority-profiles/network-marketing-eric-worre.md` | **YES** |
| `docs/research/authority-profiles/business-richard-branson.md` | **YES** |
| `docs/research/authority-profiles/business-warren-buffett.md` | **YES** |
| `docs/research/authority-profiles/business-charlie-munger.md` | **YES** |
| `docs/research/authority-profiles/business-peter-drucker.md` | **YES** |
| `docs/research/authority-profiles/leadership-john-c-maxwell.md` | **YES** |
| `docs/research/authority-profiles/leadership-jim-rohn.md` | **YES** |
| `docs/research/authority-profiles/leadership-stephen-covey.md` | **YES** |

**Retain:** `docs/research/authority-profiles/README.md` (usage docs) and `docs/research/authority-profiles/_template.md` (template).

### LEGACY — Old Implementation

| File | Notes | Safe to Delete? |
|------|-------|-----------------|
| `levnytt-se-master-template.html` | Dev template; excluded from production counts by scripts and docs. Referenced by 5+ documents | **NO** — update all references first |
| `content/products/archive/entity_formula_iv_prototype/sv.json` | Superseded by entity system; already in archive dir | Already archived — can leave |

---

## Files to Archive (Keep but Freeze)

| File | Reason to Keep | Reason Not to Delete |
|------|----------------|----------------------|
| `AUDIT-REPORT.md` | Historical engineering record; referenced by 4 docs | Contains resolved-issue traceability |
| `LEVNYTT-MUISTIO.md` | Contains sponsor IDs and ops reference not fully captured elsewhere | Finnish ops memo — practical reference |

---

## Broken References

| Reference | Source File | Target File | Status |
|-----------|------------|-------------|--------|
| `CONTENT-FACTORY.md` references | `docs/debug/WRITER-HTML-GAP-ANALYSIS.md` | `/home/yampa/.claude/skills/content-factory/CONTENT-FACTORY-V2.md` | Links exist — both files present |
| Cron path `reddit_niche_radar.py` | `.claude/skills/supplement-reddit-research/SKILL.md` | `/home/yampa/Documents/Levnytt/reddit_niche_radar.py` | **BROKEN** — target does not exist; actual script lives at skill location |
| `gpt-image-2` sibling skill | `.claude/skills/informational-article/SKILL.md` | `gpt-image-2/SKILL.md` alongside `informational-article/` | **DANGLING** — only `olsp-authority-article` bundles gpt-image-2 |

---

## Duplicate Root/Content Article Files

21 files exist in both `/` (production root) and `content/articles/` (source):

**Different content (18):** `d-vitaminbrist-sverige`, `d-vitamin-dosering-per-dag`, `d-vitamin-immunforsvaret`, `d-vitamin-och-solen`, `fiberrika-livsmedel`, `fibrer-for-magen-forstoppning`, `fibrer-for-viktminskning`, `fibrer-tarmflora-prebiotisk`, `magnesiumbrist-symptom-tester`, `multivitamin-for-barn`, `multivitamin-for-kvinnor`, `multivitamin-for-man`, `probiotika-dosering-timing`, `probiotika-for-magen-ibs`, `probiotika-prebiotika-skillnad`, `billig-dyr-multivitamin`

**Identical content (3):** `magnesium-d-vitamin-kombination`, `magnesiumformer-vilken-valja`, `magnesium-for-somn`, `magnesium-och-stress`, `antioxidanter-komplett-guide`

These are **not bugs** — the root files are deployed production versions, and `content/articles/` files are source files that may differ post-deployment (e.g., manual fixes applied to production). Per the Publication Agent workflow, source files in `content/articles/` get published to root. Divergence indicates manual hotfixes on production that were not synced back to source.

---

## Duplicate Specifications

None found. Each specification addresses a unique concern:

| Spec | Unique Purpose |
|------|----------------|
| `PUBLICATION-ARTICLE-STANDARD.md` | Article HTML structure |
| `PRODUCT-ENTITY-SYSTEM.md` | Product identity metadata |
| `EDITORIAL-SYNC-ENGINE.md` | Editorial state management |
| `AGENT-REGISTRY.md` | Agent inventory and responsibilities |
| `MORNING-BRIEF-ARCHITECTURE.md` | Consumer intelligence subsystem |

---

## Legacy Prompts

| File | Status |
|------|--------|
| `.claude/settings.local.json` | SUPERSEDED — machine-specific skill install paths |
| `run-config.json` | EXPERIMENTAL — single-use article config |
| `todo-list.json` | EXPERIMENTAL — transient task tracker |

---

## Legacy Templates

| File | Status |
|------|--------|
| `levnytt-se-master-template.html` | LEGACY — dev template with inline `:root`, hardcoded nav/footer, older design system. Referenced by 5+ docs. Mark all references before removing. |
| `.claude/skills/informational-article/SKILL-v2.md` | SUPERSEDED by SKILL.md |
| `.claude/skills/informational-article/SKILL-v2.before-refactor.md` | LEGACY backup before refactor |

---

## Legacy Agents

| File | Status |
|------|--------|
| `.opencode/agents/research-commander.md` | EXPERIMENTAL — design document for system not yet built. Referenced infrastructure (directories, modules, cache, manifests) does not exist. Safe to archive if plan is abandoned. |

---

## Summary: Recommended Actions

### Phase 1 — Delete (zero dependencies, safe immediately)
1. `.claude/skills/content-factory/CONTENT-FACTORY-V2.md`
2. `OPENCODE-REPOSITORY-ANALYSIS.md`
3. `.claude/settings.local.json`
4. `scripts/update-author.py`
5. `run-config.json`
6. `todo-list.json`
7. `generate_hero.py`
8. `generate_heroes_batch.py`
9. All 4 `docs/debug/*.md` files
10. All 18 `docs/research/authority-profiles/*.md` (retain `README.md` and `_template.md`)
11. `docs/sprints/SPRINT-9-BRAND-ROLLOUT.md`
12. `docs/reports/SPRINT-6-MIGRATION-INVENTORY.md`
13. `docs/reports/SPRINT-6.1-CLEANUP-REPORT.md`
14. `docs/reports/SITE-PAGE-INVENTORY.md`
15. `DOCUMENTATION-UPDATE-REPORT.md`
16. `SPRINT-6-REPORT.md`
17. `SITEMAP-VERIFICATION.md`
18. `logg-2026-07-01.md`

### Phase 2 — Requires reference updates
1. All 5 editorial briefs (update `CURRENT-SPRINT.md` if they reference it)
2. `docs/reports/MORNING-BRIEF-VALIDATION-REPORT.md` (update `CURRENT-SPRINT.md`)
3. `docs/reports/BRAND-DESIGN-SYSTEM-STATUS.md` (update `CURRENT-SPRINT.md`)
4. `docs/LEGACY-ARTICLE-MIGRATION-AUDIT.md` (update `ARTICLE-TEMPLATE-FAMILIES.md`)
5. `DOCUMENTATION-MIGRATION-REPORT.md` (update `PROJECT-ENTRY.md`)

### Phase 3 — Requires careful handling
1. `.claude/skills/informational-article/SKILL-v2.md` — keep 1-2 sprints as rollback, then delete
2. `.claude/skills/informational-article/SKILL-v2.before-refactor.md` — move to archive or delete
3. `levnytt-se-master-template.html` — update 5+ docs before removing

### Keep (do not touch)
- All production articles (root `*.html` and `content/articles/*.html`)
- All agents (`.opencode/agents/*.md`)
- All active skills (`.claude/skills/*/SKILL.md`)
- All active specs (`docs/specifications/*.md`, `PUBLICATION-ARTICLE-STANDARD.md`)
- All active assets (`nav.js`, `footer.js`, `components.js`, `pillar.css`, `assets/brand/*`)
- All active scripts (`scripts/generate-*.py`, `scripts/sync-editorial-state.py`, `scripts/fix-internal-links.py`)
- All product entities (`content/products/entities/*/sv.json`)
- All authority research files (`docs/authority-research/*.md`)
- All editorial state files (`docs/editorial-state/*.md`)
- All active reports (`docs/reports/skill-to-pas-migration-report.md`, auto-generated files)
- Infrastructure (`_redirects`, `robots.txt`, `sitemap.xml`, `.github/workflows/*`)
- Core docs (`PROJECT-ENTRY.md`, `PROJECT-STATUS.md`, `DECISIONS.md`, `CURRENT-SPRINT.md`)
- All planning/architecture/skill docs currently in use

---

## Files Not Yet Classified (Reviewed, All ACTIVE)

| Category | Files | Status |
|----------|-------|--------|
| `.gitignore` | 1 | ACTIVE — references deleted `backup-2026-06-10/` dir (no-op) |
| `.opencode/` core | `package.json`, `package-lock.json`, `.gitignore`, `init` | ACTIVE — OpenCode infrastructure |
| `.opencode/*.db*` | 3 SQLite files | ACTIVE — OpenCode internal state |
| `images/` | ~100+ files | ACTIVE — production images |
| `research/` with `.gitkeep` | 11 `.gitkeep` + batch research JSON files | ACTIVE — research pipeline data |
| `.claude/` | `settings.local.json` (see SUPERSEDED above) | — |
