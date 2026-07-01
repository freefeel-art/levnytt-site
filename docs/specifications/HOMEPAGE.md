# Homepage Specification — LevNytt

**Status:** Specification (not implemented)  
**Applies to:** `index.html`  
**Last updated:** 2026-06-29  
**Supersedes:** None (first version)

---

## 1. Latest Article

The homepage shall always display the latest published article.

- The **latest article** is determined from article publication metadata (`date` field) during the content generation pipeline.
- The article title, URL, and label ("Senaste artikeln") shall be rendered in the gold banner at the top of the page.
- Manual editing of `index.html` to update the latest article is forbidden.

---

## 2. Latest Articles Section

The homepage shall display a section titled "Senaste artiklarna" listing the most recently published articles.

| Property | Value |
|---|---|
| Ordering | Descending by `date` metadata (newest first) |
| Maximum displayed | 6 |
| Update behaviour | Regenerated every time a new article is published through the pipeline |
| Fallback (< 6 articles) | Display all available articles; no filler placeholders |
| Empty state (< 1 article) | Section is hidden entirely |

Each entry shall show:

- Article title (linked)
- Publication date
- Reading time

---

## 3. Homepage Pipeline

The homepage update is triggered by the **post-generation pipeline step** that runs after all articles for a batch have been written to disk.

**Pipeline sequence:**

1. Generate article HTML files (LevNytt Writer / pillar-page-template skill)
2. Run homepage generator script (rewrites `index.html`)
3. Update `_redirects` if new routes were added
4. Commit and deploy

The homepage generator shall:

- Scan the articles directory for `.html` files with front-matter metadata
- Sort by `date` descending
- Render the Latest Article banner (Rule 1) and Latest Articles section (Rule 2)
- Preserve all non-article areas of `index.html` unchanged (hero, Decision Hub, content clusters, footer, navigation, SEO meta)

The homepage must always reflect the current article repository after a successful build.

---

## 4. Homepage Links

All links from the homepage to articles shall open in a new browser tab.

```html
target="_blank"
rel="noopener noreferrer"
```

**Scope:** This applies to every article link rendered on the homepage — the Latest Article banner, the Latest Articles section, and any future article-driven sections.

**Non-scope:** Internal links from one article to another (article-to-article) remain unaffected and open in the same tab.

---

## 5. Manual Editing

The homepage article area shall never be maintained manually.

- No article title, URL, or date on the homepage shall be hand-edited in `index.html`.
- All article references must be generated automatically by the pipeline.
- The only acceptable manual edits to `index.html` are structural changes (hero copy, navigation, footer, layout, styling).

---

## 6. Future Compatibility

The specification is designed to support the following expansions without structural changes to the homepage generator:

| Future feature | How it fits |
|---|---|
| Featured article | A `featured: true` front-matter flag promotes an article to a dedicated featured slot; if multiple are flagged, the newest one wins |
| Featured category | A `category` taxonomy field groups articles; the generator can render one card per active category using the latest article in each |
| Popular articles | A `popular` or `views` metadata field (populated by analytics or manual editorial input) can drive a secondary sorted section |
| Recently updated articles | A `updated` date field, distinct from `date`, allows a "Recently updated" section sorted by last-modified timestamp |
| Pagination | The Latest Articles section (Rule 2) can accept a `max_displayed` configuration parameter without changing the sort or render logic |

Each expansion adds a new section to the homepage but reuses the same rendering primitives (sort by metadata field, render title + link + metadata, open in new tab).

---

*End of specification.*
