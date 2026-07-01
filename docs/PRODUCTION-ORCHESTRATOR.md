# Production Orchestrator V1

**Date:** 2026-07-01
**Status:** ACTIVE

---

## Purpose

The Production Orchestrator is the single entry point that transforms a keyword into a published article. It chains 5 registered agents through 7 pipeline stages, enforcing gates between each stage.

---

## How to Invoke

### Primary method — opencode agent

```
Kör produktionen för "vad är lutein"
```

The Production Orchestrator agent (`.opencode/agents/production-orchestrator.md`) intercepts this and runs the full pipeline.

**Trigger phrases:** `run production`, `kör produktion`, `production run`, `producera artikel`, `full pipeline`, `produktionspipeline`

### Shell script method

```bash
./scripts/run-production.sh "vad är lutein"
```

The shell script:
1. Validates the keyword
2. Creates `content/articles/<slug>/run-config.json`
3. Creates `content/articles/<slug>/` directory
4. Tells opencode to invoke the Production Orchestrator

---

## Agent Chain

The Production Orchestrator uses opencode's Task tool to invoke each downstream agent in sequence. No stage executes until the previous stage's gate passes.

```
Production Orchestrator
  │
  ├─(1)─→ Write run-config.json directly
  │
  ├─(2)─→ Task: Research Commander
  │       Input: run-config.json + keyword
  │       Gate: final_brief = approved
  │       Output: research/briefs/<slug>-approved.md
  │
  ├─(3)─→ Task: Editorial Commander (authority check only)
  │       Input: approved brief path
  │       Gate: authority CLEARED
  │
  ├─(4)─→ Task: LevNytt Writer
  │       Input: run-config.json + approved brief
  │       Gate: valid HTML written to content/articles/<slug>/
  │       Output: content/articles/<slug>/<slug>.html
  │
  ├─(5)─→ QA Gate (bash + manual review)
  │       Input: content/articles/<slug>/<slug>.html
  │       Gate: 12/12 checks pass (or AMBER with operator override)
  │       Output: QA report (terminal + qa-report.txt)
  │
  ├─(6)─→ Task: Publication Agent
  │       Input: <slug> (publish from content/articles/ to root)
  │       Gate: root file created, brand assets verified, index regenerated
  │       Output: /<slug>.html (published), git commit
  │
  └─(7)─→ Production Report (terminal output)
```

---

## File Passing Between Stages

Each stage writes to well-known paths. The next stage reads from those paths. No arguments passed — paths are inferred from the slug.

| From Stage | To Stage | File Passed |
|-----------|----------|-------------|
| Orchestrator | Research Commander | `content/articles/<slug>/run-config.json` |
| Research Commander | Writer | `research/briefs/<slug>-approved.md` |
| Editorial Commander | Writer | Authority clearance flag in approved brief |
| Writer | QA | `content/articles/<slug>/<slug>.html` |
| QA | Publication Agent | `content/articles/<slug>/<slug>.html` (QA passed) |
| Publication Agent | Report | Commit hash + production status |

---

## QA Gate — Detailed

### Critical checks (Q1-Q12)

| # | Check | How to verify |
|---|-------|---------------|
| Q1 | File exists | `test -f content/articles/<slug>/<slug>.html` |
| Q2 | File non-empty | `test -s` (size > 0) |
| Q3 | Valid HTML shell | `grep -c '<html'`, `</html>`, `<head>`, `<body>` |
| Q4 | PAS wrapper | `grep '<div class="ia-wrap"><article>'` (NOT `<main`) |
| Q5 | PAS CSS present | `grep '.ia-punchline'`, `.ia-takeaways`, `.ia-cta`, `.ia-faq` |
| Q6 | Green palette | `grep '#1B4332'` AND NOT `grep '#F25F4C\|#0F1B3A'` |
| Q7 | Dark evidence tiers | `grep '.ia-ev-t1'`, `.ia-ev-t2` |
| Q8 | #site-nav div | `grep '<div id="site-nav">'` |
| Q9 | Shared scripts | `grep 'nav.js'`, `footer.js`, `components.js` |
| Q10 | @graph schema | `grep 'FAQPage'` AND `grep 'Article'` in JSON-LD block |
| Q11 | Title length | Extract `<title>` text, verify ≤ 60 chars |
| Q12 | Description length | Extract `<meta name="description">` text, verify ≤ 155 chars |

### Outcome

| Score | Gate | Action |
|-------|------|--------|
| 12/12 | GREEN | Proceed to Publication |
| 10-11/12 | AMBER | Report warnings, prompt operator: `proceed? (y/n)` |
| <10/12 | RED | HALT — write `qa-failures.txt`, stop pipeline |

---

## Abort / Resume

### Abort points

The operator can abort at any gate. The pipeline is designed so that aborting after a stage does not lose work — the next invocation skips completed stages.

| Abort at | State saved | Resume from |
|----------|-------------|-------------|
| After Stage 1 | run-config.json exists | Stage 2 |
| After Stage 2 | Approved brief exists | Stage 3 |
| After Stage 4 | Article HTML exists | Stage 5 (QA) |
| After Stage 5 | QA passed flag | Stage 6 |
| After Stage 6 | Published, committed | Done |

### Resume command

```
Fortsätt produktionen för vad-ar-lutein från steg 5
```

The orchestrator detects existing files and skips completed stages automatically.

---

## How QA Blocks Publication

The QA gate is the final safety check before publication. A RED result blocks the Publication Agent entirely — no file is copied to root, no git commit is created, nothing is pushed.

The gate works at three levels:

1. **Automated (Q1-Q12):** Bash-level checks on the HTML file. Runs in <1 second.
2. **Manual review (optional):** Operator reads the article and confirms visual quality.
3. **Operator override:** AMBER results can be overridden. RED results cannot.

### Override rules

- AMBER → operator types `y` to proceed, `n` to abort
- RED → no override. Article must be fixed and re-QA'd.
- Overrides are logged in `content/articles/<slug>/qa-report.txt`

---

## Error Recovery

| Error | Stage | Recovery |
|-------|-------|----------|
| Duplicate slug | Stage 1 | Operator picks new slug |
| Research cache hit | Stage 2 | Skip research, use existing approved brief |
| Module failure (partial) | Stage 2 | Continue with partial package, editorial decides |
| Brief not approved | Stage 3 | Wait for approval or override |
| Authority blocked | Stage 3 | Run authority research, then retry |
| Writer fails | Stage 4 | Fix run-config or brief, retry writer |
| QA RED | Stage 5 | Fix article, re-run QA |
| Source missing | Stage 6 | Re-run writer |
| Brand asset missing | Stage 6 | Restore assets from backup |
| Index generation fails | Stage 6 | Debug script, retry |
| Push rejected | Stage 6 | Pull --rebase, retry push |

---

## Performance

| Stage | Typical Duration | Blocking? |
|-------|-----------------|-----------|
| Stage 1: Run Config | < 1s | Manual input only |
| Stage 2: Research | 30-120s (cache: 0s) | API calls |
| Stage 3: Editorial Brief | 5-10s | File reads |
| Stage 4: Write | 60-180s | LLM generation |
| Stage 5: QA | < 1s | Bash checks |
| Stage 6: Publish | 5-15s | Git + network |
| Stage 7: Report | < 1s | Terminal output |
| **Total** | **2-5 min** | |

With full cache hit on research: 1.5-3 minutes end-to-end.

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| V1 | 2026-07-01 | Initial orchestrator specification. 7 stages, 12 QA checks, 3 gate levels. |
