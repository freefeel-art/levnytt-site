# Sprint 22 Plan — Production Hardening: Protect Markdown Source Files

**Status:** Planned
**Depends on:** Sprint 21 (Markdown-First Publication Pipeline)

---

## Problem Statement

The `md-to-article.py` pipeline stores both the Markdown source (`.md`) and the
generated HTML (`.html`) in the same subdirectory under `content/articles/`:

```
content/articles/kalcium-brist-symtom/
  kalcium-brist-symtom.md    ← source file, publicly accessible
  kalcium-brist-symtom.html  ← published output
```

Because Cloudflare Pages serves all files in the repository root, the `.md` source
file is publicly accessible at:

```
https://levnytt.se/content/articles/kalcium-brist-symtom/kalcium-brist-symtom.md
```

This returns HTTP 200 with `Content-Type: text/markdown`. Every future article
published through the pipeline will have the same exposure.

---

## Proposed Solutions

### Option A — Block via `_redirects`

Add a redirect rule that returns 404 for all `.md` files under `content/articles/`:

```
/content/articles/*/*.md /404.html 404
```

The `.md` files remain in the repository and are deployed to Cloudflare's CDN,
but HTTP access is blocked at the routing layer.

### Option B — Move Markdown sources outside the web root

Establish a separate `source/articles/` directory for `.md` files. The pipeline
reads from `source/` and writes HTML output to `content/articles/`. Source files
are never inside the served directory.

```
source/articles/kalcium-brist-symtom/
  kalcium-brist-symtom.md    ← authoring source, not deployed

content/articles/kalcium-brist-symtom/
  kalcium-brist-symtom.html  ← published output only
```

`md-to-article.py` input path changes from:
```
content/articles/{slug}/{slug}.md
```
to:
```
source/articles/{slug}/{slug}.md
```

---

## Comparison

### Security

**Option A:** Source files are deployed to Cloudflare's CDN and exist in the
bundle. HTTP access is blocked, but the files are present at the infrastructure
level. A misconfigured or missing redirect rule would immediately re-expose them.
The block must be maintained actively as the pipeline evolves.

**Option B:** Source files are never deployed. They do not exist on Cloudflare's
servers. There is no HTTP surface to protect. Security is structural, not
rule-dependent.

**Winner: Option B.**

---

### Maintainability

**Option A:** One redirect rule covers all current and future articles, assuming
the directory structure does not change. If the script is ever updated to use a
different nesting depth or directory name, the rule silently stops applying.
The rule is invisible to someone reading `md-to-article.py` — the protection is
implicit and easy to forget.

**Option B:** The separation is enforced by directory structure. Any engineer
reading the pipeline immediately understands: `source/` is input, `content/` is
output. No invisible rules. The protection cannot break unless someone deliberately
moves files.

**Winner: Option B.**

---

### Deployment Simplicity

**Option A:** Single line added to `_redirects`. No changes to the pipeline or
directory layout. Immediate effect after one commit.

**Option B:** Requires updating `md-to-article.py` (input path), moving the
existing `.md` file, and updating `PUBLICATION-SOURCE-V2.md` and
`MARKDOWN-FIRST-IMPLEMENTATION-PLAN.md` to reflect the new directory convention.
Each new article must be authored under `source/` instead of `content/`.

**Winner: Option A** (lower immediate complexity).

---

### Long-Term Architecture

**Option A:** Perpetuates the mixing of source and output in the same directory.
As the article library grows, `content/articles/` becomes harder to audit — it is
unclear at a glance which files are generated and which are inputs. Any tooling
that operates on `content/articles/` (QA scripts, sitemap generators, link
checkers) must be aware of and skip `.md` files.

**Option B:** Establishes a clean build-step model that mirrors standard static
site generator conventions: source files live in a source tree; the output
directory contains only what is published. This model scales well and is
immediately understood by any engineer familiar with static site tooling.
It also makes future automation easier — a script that generates all articles
by iterating `source/articles/` is simpler to write and less error-prone than
one that must filter `.md` from a mixed directory.

**Winner: Option B.**

---

### Migration Effort

**Option A:** Zero migration. The existing `kalcium-brist-symtom.md` stays in
place. The rule applies retroactively.

**Option B:** For the current state (one published article):
- Move `content/articles/kalcium-brist-symtom/kalcium-brist-symtom.md` to
  `source/articles/kalcium-brist-symtom/kalcium-brist-symtom.md`
- Update `md-to-article.py`: change input path constant
- Update `PUBLICATION-SOURCE-V2.md`: update directory convention section
- Update `MARKDOWN-FIRST-IMPLEMENTATION-PLAN.md`: update path references

Estimated scope: 3–4 files, low risk, no production HTML affected.

**Winner: Option A** (zero effort vs. low effort).

---

## Summary Table

| Criterion               | Option A (`_redirects`) | Option B (source/ directory) |
|-------------------------|-------------------------|------------------------------|
| Security                | Adequate                | Strong                       |
| Maintainability         | Fragile                 | Robust                       |
| Deployment simplicity   | Minimal change          | Low-medium change            |
| Long-term architecture  | Technical debt          | Correct separation           |
| Migration effort        | Zero                    | Low (3–4 files, 1 article)   |

---

## Recommendation

**Option B is the preferred long-term solution.**

Option A solves the immediate access problem but does not solve the underlying
architectural issue: source and output files coexisting in the published directory.
The redirect rule must be maintained indefinitely and can silently fail. As the
article library grows, the mixed directory becomes a liability for every tool
that operates on `content/articles/`.

Option B corrects the architecture at the point where it is cheapest: one article
exists, one file needs moving, the pipeline is young. The migration effort is low
now and grows linearly with each article published before the fix is applied.

Implementing Option B during Sprint 22, while the pipeline is new and the article
count is small, avoids a more disruptive migration later.

---

## Sprint 22 Deliverables (when approved)

1. Create `source/articles/` directory convention
2. Move `content/articles/kalcium-brist-symtom/kalcium-brist-symtom.md` to
   `source/articles/kalcium-brist-symtom/kalcium-brist-symtom.md`
3. Update `scripts/md-to-article.py`: read input from `source/articles/{slug}/{slug}.md`
4. Update `docs/PUBLICATION-SOURCE-V2.md`: reflect new source directory
5. Update `docs/MARKDOWN-FIRST-IMPLEMENTATION-PLAN.md`: reflect new path convention
6. QA: verify `https://levnytt.se/content/articles/kalcium-brist-symtom/kalcium-brist-symtom.md`
   returns 404 after the move
7. QA: verify `https://levnytt.se/kalcium-brist-symtom` continues to return 200
