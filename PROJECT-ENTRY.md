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

## Skill Loading (Mandatory)

Before starting any implementation work, explicitly load every Claude/OpenCode skill that is relevant to the current sprint.

Skills are **not loaded automatically**. Even if the repository or filesystem contains the skill, its instructions are **not available** until the skill is explicitly loaded with the skill tool.

Repository documentation remains the Source of Truth, but skills contain implementation workflows, migration rules, design guidance, checklists, and engineering constraints that must be available before implementation begins.

Typical skills include:

- `pillar-page-template`
- `informational-article`
- `astro-builder`
- `direct-sales-reddit-research`
- `olsp-authority-article`
- `search-gap-research`
- `supplement-reddit-research`

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

## Autonomous Execution (Mandatory)

After loading the required project documents and skills:

- If no sprint is active, automatically continue with the next planned sprint according to the project documentation.
- If multiple implementation candidates exist, select the highest-priority recommended item without asking the user.
- Resolve all routine implementation decisions using the repository, project documentation, and loaded skills.
- Do not interrupt the user for decisions that can be resolved from documented project rules.
- Ask the user only when a business, content, branding, SEO strategy, legal, or other user-owned decision is required, or when documentation is contradictory or ambiguous.

This rule is mandatory for all future sprints.

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
2. Determine which skills are required for the current sprint and load them with the skill tool (see **Skill Loading** above).
3. Check `CURRENT-SPRINT.md` — is a sprint active?
   - **Yes:** implement the active sprint. Do not introduce unrelated work.
   - **No:** select the highest-priority item from `PROJECT-STATUS.md → Open backlog` and open it as the next sprint. See **Autonomous Execution** above.
4. If the repository state appears to conflict with `PROJECT-STATUS.md`, verify before acting. Report the conflict. Do not invent a resolution.

### Doing work

- Work on **one task at a time**, as defined in `CURRENT-SPRINT.md`.
- Do not redesign, refactor, or change architectural decisions without first updating `DECISIONS.md` and getting explicit confirmation.
- Do not modify `sitemap.xml`, `nav.js`, `footer.js`, or `pillar.css` without understanding their role (see `PROJECT-STATUS.md → Architecture`).
- After any HTML change, verify the page still loads `nav.js`, `footer.js`, and `pillar.css` with `defer`.

### Finishing a session

- Update `CURRENT-SPRINT.md` to reflect task progress.
- If a sprint is completed, update `PROJECT-STATUS.md` (milestones, priorities) and clear `CURRENT-SPRINT.md`.
- Commit with a concise message matching the existing commit style (see `git log --oneline`).

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
| `SITEMAP-VERIFICATION.md` | Sitemap completeness check from 2026-06-28. All 73 pages confirmed. | Completed task record |
| `OPENCODE-REPOSITORY-ANALYSIS.md` | AI-generated architecture summary from 2026-06-28. | Superseded by `PROJECT-STATUS.md` |
| `DOCUMENTATION-MIGRATION-REPORT.md` | Record of the documentation consolidation on 2026-06-28. | Archive |
| `docs/databank/LEVNYTT-PRICE-DATABASE.md` | NeoLife SE product prices (April 2026). Use when building cost calculators. | Active reference |
