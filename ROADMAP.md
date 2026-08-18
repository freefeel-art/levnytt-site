ROLE: STRATEGIC

# LevNytt — Roadmap

> Ordered implementation plan. Highest priority first. This roadmap is a plan
> for post-activation autonomous operation; no phase executes until the project
> is activated and the production scheduler is enabled.

---

## Phase 1: NeoLife measurement & attribution foundation ⬜

**Status:** Not started (activation prerequisite)

- [ ] Instrument first-party NeoLife link-click events (customer shop +
      distributor registration Sponsor-ID links) through the existing D1
      `levnytt-cta-events` receiver (`_worker.js` CTA_PATHS extension + client
      beacon in `components.js`).
- [ ] Confirm the Google Search Console property (`sc-domain:levnytt.se`) is
      verified and collectible via `scripts/collect_gsc.py --project levnytt`.
- [ ] Reclassify the legacy OLSP CTA as an isolated cross-project artifact
      (kept or removed by Owner decision) so it never appears as a LevNytt
      conversion path.

**Outcome:** Every NeoLife conversion opportunity is observable first-party;
the missing attribution path (NeoLife back-office) is explicitly tracked as an
Owner boundary.

---

## Phase 2: Qualified organic traffic breakthrough ⬜

**Status:** Not started

- [ ] GSC-driven content selection: prioritize the direct-selling/MLM cluster
      (highest demonstrated signal, e.g. "direktförsäljning") and consumer
      supplement intents over low-signal science pages.
- [ ] Produce/refresh consumer-focused Swedish articles through Scribe +
      content gate, grounded in first-party GSC + DataForSEO evidence.
- [ ] Preserve and expand internal linking within the magnesium, vitamin D,
      omega-3, and MLM clusters.

**Outcome:** Measurable GSC click growth toward a page-1 position on a
non-branded Swedish query with >50 impressions/month.

---

## Phase 3: Conversion optimization ⬜

**Status:** Not started

- [ ] Strengthen the savings/comparison funnel (Affärsmöjlighet 2.0 +
      Sparkalkylator) toward the Sponsor-ID shop/registration conversion.
- [ ] Ensure sponsor-ID auto-rewrite (`components.js` fixLinks) coverage across
      all product pages.
- [ ] Truthful conversion-path disclosure on every CTA.

**Outcome:** NeoLife link-click events are measured and increasing with
traffic.

---

## Phase 4: Social distribution (gated) ⬜

**Status:** Not started

- [ ] Facebook page posting when a new article is published (page exists,
      never published).
- [ ] Pinterest publication only after `PINTEREST_ACCESS_TIER=standard`
      (currently trial-blocked).

**Outcome:** Multi-channel distribution driving qualified traffic back to the
site (secondary to organic search).

---

## Phase 5: NeoLife revenue attribution ⬜

**Status:** Not started — Owner boundary

- [ ] Obtain NeoLife back-office / affiliate reporting access to read
      attributable customer and distributor commissions.
- [ ] Join NeoLife revenue against link-click events and GSC traffic.

**Outcome:** Direct NeoLife revenue/conversions measurable (the north star),
not proxied.

---

## Legend

- ✅ Complete
- 🔵 In Progress
- ⬜ Planned / Not Started
