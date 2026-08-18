ROLE: OPERATIONAL

# LevNytt — State

**Last updated:** 2026-08-18

## Primary Business Objective (Owner-set)

Build and operate a profitable Swedish NeoLife organic acquisition asset
(Sponsor-ID 41-830928). See OBJECTIVES.md for the binding operating hierarchy.

## Current status

- **Project:** LevNytt (`levnytt`), project-scoped Hermes architecture.
- **Site:** Live at https://levnytt.se (Cloudflare Pages). ~113 root pages,
  112 sitemap URLs, ~95-article index. Homepage, article pages, rewrites and
  product pages all serve correctly (verified 2026-08-16).
- **Monetization:** NeoLife Sponsor-ID 41-830928 wired across ~100+ links via
  `components.js` fixLinks; 57-product price database. Revenue **unmeasured**.
- **Traffic baseline:** ~2 clicks / 366 impressions per rolling 28 days (GSC),
  avg position ~31.5, CTR ~0.55%. Pre-traction.
- **Phase:** activation-ready (no autonomous production started).

## Measurement

- North star: NeoLife revenue/conversions — **unmeasured** (no NeoLife
  back-office/affiliate reporting access; Owner boundary).
- Strongest truthful proxy: NeoLife link-click events via D1
  `levnytt-cta-events` — **receiver deployed, client beacon pending** (Phase 1).
- Leading indicator: Google Search Console organic traffic — **available**
  (`scripts/collect_gsc.py --project levnytt --site sc-domain:levnytt.se`).

## Cross-project artifacts (resolved 2026-08-18)

- **OLSP CTA:** removed. On direct re-verification, only 1 page
  (`direktforsaljning-fakta`) actually contained a live
  `https://olsp.profitandprivilege.com` link — the "5 pages" figure in the
  prior version of this note was stale/inaccurate; `neolife-affarsmojlighet`,
  `neolife-carotenoid-complex`, `neolife-flavonoid-complex`, and
  `fytosteroler-cellmembran` do not and did not contain an OLSP reference at
  time of check. The one real link (and its content-source entry in
  `content/data/production-pages.json`) has been removed; `_worker.js`'s
  `CTA_PATHS` allowlist entry for it has been cleared; the D1 schema file's
  top comment (which referenced "OLSP" only in a comment, never in actual
  column names) has been corrected. OLSP is not part of the LevNytt project
  (`config/conversion-attribution.json`) — this is no longer a pending Owner
  decision, it is the current, implemented state.

## Social

- **Facebook:** page "LevNytt", id **1300898706431018** (corrected
  2026-08-18 -- the previously recorded id, 61592255235938, does not exist
  / is not reachable with the current token; verified via a live read-only
  Graph API call against `GET /me/accounts`, the set of pages
  FACEBOOK_USER_ACCESS_TOKEN actually manages). Fixed in
  `app/commander/facebook_identity.py`'s `LEVNYTT_FACEBOOK_PAGE_ID_DEFAULT`.
  Verified live: 0 followers, category "News & media website", not
  verified, About text matches LevNytt's positioning. Profile+cover
  branding assets exist locally (`assets/brand/facebook-*.png`, now
  git-tracked) but were not independently confirmed as uploaded to the
  page (would require a page-scoped token, not fetched). No post history
  was confirmed either way for the same reason. `content_published: false`
  self-report is consistent with 0 followers but not independently proven.
  `social.py` (legacy standalone) holds 8 queued Swedish articles and its
  own hardcoded (now-also-stale) page id; not wired into the autonomous
  loop -- see the Hermes-side classification note for disposition.
- **Pinterest:** domain claimed, board verified, OAuth authorized,
  trial-blocked (`PINTEREST_ACCESS_TIER=standard` required).

## Repository

- Working repository: `/home/yampa/projects/active/levnytt-site`
  (github `freefeel-art/levnytt-site`), Cloudflare Pages auto-deploy on push.
- Project-control documents and runtime are local-only (`.git/info/exclude`),
  never committed to the public static site.
- Working tree matches HEAD (deployed state); the previously dangerous
  uncommitted `content/` deletion was reverted on 2026-08-16.

## Known missing evidence / gaps

1. NeoLife back-office/affiliate reporting access (revenue/conversions) —
   Owner boundary.
2. NeoLife link-click client beacon (frontend instrumentation) — Phase 1.
3. GSC property authorization status for `sc-domain:levnytt.se` — verified at
   first measurement run.
