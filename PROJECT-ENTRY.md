# PROJECT-ENTRY.md
# LevNytt.se — AI Agent Entry Point

---

## IMPORTANT

Every AI session must begin by reading:

1. `PROJECT-ENTRY.md` — this file
2. `PROJECT-STATUS.md` — current project state, architecture, priorities
3. `CURRENT-SPRINT.md` — active sprint goal, tasks, next action
4. `DECISIONS.md` — permanent engineering decisions

These four documents are the operational Source of Truth.

**Do NOT perform a full repository analysis unless explicitly requested.**

**Do NOT redefine priorities when an active sprint already exists.**

**Implement the current sprint.**

If documentation and repository disagree:
- Verify first.
- Report the conflict.
- Update the documentation.
- Never assume a historical document is current.

---

## Documentation Hierarchy

Always read documentation in this order before starting work:

1. `PROJECT-ENTRY.md` — entry point, workflow, skills
2. `PROJECT-STATUS.md` — current state, architecture, milestones, priorities
3. `CURRENT-SPRINT.md` — active sprint, tasks, next action
4. `DECISIONS.md` — permanent engineering decisions
5. Repository files — actual code and pages
6. Historical documents — context only, not authoritative

Reference documents (read only when relevant to the task):
- `docs/BRAND-DESIGN-SYSTEM.md` — brand identity, LV Mark spec, colors, usage rules
- `docs/PUBLICATION-ARTICLE-STANDARD.md` — Publication Agent rules and conventions
- `docs/ARTICLE-TEMPLATE-FAMILIES.md` — article template taxonomy

---

## Skill Loading (Mandatory)

Before starting any implementation work, explicitly load every Claude/OpenCode skill that is relevant to the current sprint.

Skills are **not loaded automatically**. Even if the repository or filesystem contains the skill, its instructions are **not available** until the skill is explicitly loaded with the skill tool.

Repository documentation remains the Source of Truth, but skills contain implementation workflows, migration rules, design guidance, checklists, and engineering constraints that must be available before implementation begins.

Skills are the implementation authority for their respective tasks and must be loaded before implementation begins.

Typical skills include:

- `pillar-page-template` — pillar page migration and audit
- `informational-article` — publish-ready HTML articles
- `astro-builder` — Astro-based websites (not used for levnytt.se)
- `direct-sales-reddit-research` — Reddit mining for direct sales market intelligence
- `olsp-authority-article` — OLSP authority articles (not used for levnytt.se)
- `search-gap-research` — keyword validation and content briefs
- `supplement-reddit-research` — Reddit mining for supplement/health niche content ideas

### Mandatory workflow

1. Read:
   - `PROJECT-ENTRY.md`
   - `PROJECT-STATUS.md`
   - `CURRENT-SPRINT.md`
   - `DECISIONS.md`

2. Determine which skills are required for the current sprint.

3. Explicitly load every required skill using the skill tool.

4. Confirm that the skills are active before making any implementation decisions.

5. Only then begin implementation.

If a relevant skill exists but has not been loaded, stop and load it before continuing.

This is a mandatory project rule for every future sprint.

---

## Autonomous Sprint Selection

If CURRENT-SPRINT.md contains no active sprint:

- Continue with the highest-priority backlog item.
- Do not stop simply because no sprint is defined.

If several candidates exist:

- Choose the recommended highest-priority item automatically.

Only ask the user when the decision is a business, branding, legal, content strategy, SEO strategy, or other user-owned decision.

Routine implementation decisions should be made autonomously.

---

## Sprint Workflow

For every sprint:

1. Read the four required documents (in order).
2. Load relevant skills.
3. Verify before implementing.
4. Apply changes.
5. Verify after changes.
6. Update documentation.
7. Commit and push.
8. Report completed work.

One concern per commit.

---

## Current Architecture Summary

LevNytt.se is a vanilla HTML5/CSS3/ES5 static site hosted on Cloudflare Pages.

**No build step, no framework, no npm.**

### Major systems

| System | Location | Purpose |
|---|---|---|
| Pages | Root `*.html` files + `neolife-*/index.html` subdirectories | All public content |
| Design System | `/pillar.css` | Shared CSS with brand CSS variables |
| Brand System | `assets/brand/` | LV Mark, favicon, apple-touch-icon, hero-watermark, OG image |
| Navigation | `/nav.js` | Self-injecting IIFE; all pages via `defer` |
| Footer | `/footer.js` | Self-injecting IIFE; all pages via `defer` |
| Components | `/components.js` | Brand injectors, sponsor-ID rewriting, scroll-to-top |
| Source articles | `content/articles/` | Informational articles (deployed via Publication Agent) |
| Routing | `_redirects` | Cloudflare rewrite rules for `content/articles/` |
| SEO | `sitemap.xml` | Hand-maintained URL index |

### Where brand assets live

```
assets/brand/
├── favicon.svg           ← Browser tab icon (injected by components.js)
├── apple-touch-icon.png   ← iOS home screen icon (injected by components.js)
├── hero-watermark.svg     ← Hero section watermark (injected by components.js)
├── og-brand.png           ← Default Open Graph image (1200x630)
├── og-brand.svg           ← OG image source
├── logo.svg               ← LV Mark light background variant
├── logo-dark.svg          ← LV Mark dark background variant
├── logo-light.svg         ← LV Mark optional variant
└── author-avatar.svg      ← Author avatar source (LV Mark inline SVG in components.js)
```

### Where articles are generated

Articles are created by the `informational-article` skill, which produces a `content/articles/<slug>.html` file. The Publication Agent deploys these to root level via `_redirects` 200-rewrites.

### Where pillar pages are generated

Pillar pages are created or migrated by the `pillar-page-template` skill. They are hand-authored `.html` files at root level that follow the Gen 3 production standard (13/13 audit checklist).

---

## Source of Truth hierarchy

| Priority | Source | Authoritative for |
|---|---|---|
| 1 | Git repository | What is actually live |
| 2 | `PROJECT-STATUS.md` | Current project state and priorities |
| 3 | `CURRENT-SPRINT.md` | What to work on right now |
| 4 | `DECISIONS.md` | Engineering conventions |
| 5 | Historical documents | Context only — not authoritative |

The repository is never modified to match outdated documentation. Documentation is updated to match the repository.

---

## Development workflow

### Starting a session

1. Read the four required documents above (in order).
2. Determine which skills are required for the current sprint and load them with the skill tool.
3. Check `CURRENT-SPRINT.md` — is a sprint active?
   - **Yes:** implement the active sprint. Do not introduce unrelated work.
   - **No:** select the highest-priority item from `PROJECT-STATUS.md → Next Development Priorities` and open it as the next sprint.
4. If the repository state appears to conflict with `PROJECT-STATUS.md`, verify before acting. Report the conflict. Do not invent a resolution.

### Doing work

- Work on **one task at a time**, as defined in `CURRENT-SPRINT.md`.
- Do not redesign, refactor, or change architectural decisions without first updating `DECISIONS.md` and getting explicit confirmation.
- Do not modify `sitemap.xml`, `nav.js`, `footer.js`, `pillar.css`, or `components.js` without understanding their role.
- After any HTML change, verify the page still loads `nav.js`, `footer.js`, and `pillar.css` with `defer`.

### Finishing a session

- Update `CURRENT-SPRINT.md` to reflect task progress.
- If a sprint is completed, update `PROJECT-STATUS.md` (milestones, priorities) and either close or advance `CURRENT-SPRINT.md`.
- Commit with a concise message matching the existing commit style.

### Committing

```bash
git add .
git commit -m "Short description of change"
git push
```

Cloudflare Pages deploys automatically on every push.

---

## Repository location

| | |
|---|---|
| Local path | `~/levnytt-site/` |
| GitHub | `freefeel-art/levnytt-site` |
| Live site | `https://levnytt.se/` |
| Hosting | Cloudflare Pages |

---

## Historical reference documents

These documents exist in the repository but are **not operational**. Read them only for background context when needed.

| Document | Content | Note |
|---|---|---|
| `LEVNYTT-MUISTIO.md` | Original ops memo (Finnish). Sponsor IDs, image naming, git workflow. | Partially outdated — superseded by `PROJECT-STATUS.md` |
| `AUDIT-REPORT.md` | Site audit from 2026-06-23. Issues documented were resolved in subsequent commits. | Historical record |
| `SITEMAP-VERIFICATION.md` | Sitemap completeness check from 2026-06-28. All pages confirmed. | Completed task record |
| `OPENCODE-REPOSITORY-ANALYSIS.md` | AI-generated architecture summary from 2026-06-28. | Superseded by `PROJECT-STATUS.md` |
| `DOCUMENTATION-MIGRATION-REPORT.md` | Record of the documentation consolidation on 2026-06-28. | Archive |
| `DOCUMENTATION-UPDATE-REPORT.md` | Record of a documentation update pass. Likely outdated. | Archive |
| `SPRINT-6-REPORT.md` | Sprint 6 (Wave 3B) report. | Historical record |
| `docs/reports/SPRINT-6-MIGRATION-INVENTORY.md` | Inventory of pages migrated in Sprint 6. | Archive |
| `docs/reports/SPRINT-6.1-CLEANUP-REPORT.md` | Sprint 6.1 cleanup record. | Archive |
| `docs/reports/SITE-PAGE-INVENTORY.md` | Site page inventory. Likely outdated. | Archive |
| `docs/reports/MORNING-BRIEF-VALIDATION-REPORT.md` | Validation report. | Archive |
| `docs/databank/LEVNYTT-PRICE-DATABASE.md` | NeoLife SE product prices (April 2026). Use when building cost calculators. | Active reference |
| `docs/editorial-state/README.md` | **Editorial State Interface** — official specification for Editorial Sync Engine generated files. All editorial agents must follow this interface. | **Active specification** |
| `docs/specifications/AGENT-REGISTRY.md` | **Agent Registry** — canonical inventory of all production agents, responsibilities, routing rules, and workflows. | **Active specification** |
| `docs/specifications/HOMEPAGE.md` | Homepage specification. | Active reference |
| `docs/specifications/MORNING-BRIEF-ARCHITECTURE.md` | Morning Brief architecture spec. | Active reference |
