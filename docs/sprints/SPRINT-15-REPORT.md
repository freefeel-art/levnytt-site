# Sprint 15 Report — Product Entity System V1

**Dates:** 2026-07-02
**Status:** Completed
**Commit:** `03b4a82`

---

## Objective

Create centralized structured product data so every page references the same prices, descriptions, and categories. No build step.

## Deliverables

| # | Deliverable | Status |
|---|-------------|--------|
| 1 | `content/products/prices.json` — all 57 products with prices (customer/distributor/savings) from Price Database | ✅ |
| 2 | `content/products/product-data.js` — runtime JS module with embedded price data, entity slug index, sponsor link fixing, public API (`LevNyttProductData.getPrice()`, `.getProduct()`, `.getShopUrl()`, `.formatPrice()`) | ✅ |
| 3 | `golden-home-care.html` — migrated as reference implementation. LDC prices (code 21) injected dynamically from data module using `data-price-code`, `data-ppu-code`, `data-ppu-prose`, `data-ppu-faq` attributes. Replaces outdated hardcoded "ca 80–90 kr" with current 268 kr (kund) / 211 kr (distributör). | ✅ |
| 4 | `components.js` — `fixLinks()` delegates to `LevNyttProductData` when product-data.js is loaded; falls back to legacy `productMap` for backward compatibility | ✅ |

## Files Changed

| File | Change |
|------|--------|
| `content/products/prices.json` | Created — 123 lines, 57 products across 6 categories |
| `content/products/product-data.js` | Created — 213 lines, runtime data module |
| `golden-home-care.html` | Updated — price table, prose, FAQ now use dynamic data from `product-data.js` |
| `components.js` | Updated — `fixLinks()` delegates to `LevNyttProductData` when available |
| `CURRENT-SPRINT.md` | Sprint 15 set as active |
| `PROJECT-STATUS.md` | Milestone updated to Sprint 15 |
| `docs/plans/PHASE-2-ROADMAP.md` | Product Entity System → In progress; Sprint 15 added to milestones |
| `docs/SPRINT-REGISTRY.md` | Sprint 15 → Active |

## Verification

- [x] `prices.json` contains all 57 products with correct prices matching Price Database
- [x] `product-data.js` exposes public API: `getPrice(code)`, `getProduct(slug)`, `getShopUrl(slug)`, `formatPrice(sek)`
- [x] `product-data.js` `fixLinks()` replaces `components.js` `productMap` logic
- [x] `golden-home-care.html` price table row has `data-price-code="21"` — JS fills real price at runtime
- [x] `golden-home-care.html` FAQ and prose also use data attributes for dynamic pricing
- [x] `components.js` gracefully falls back when `LevNyttProductData` is not loaded
- [x] Committed (`03b4a82`) and pushed to `origin/main`

## Rollback

To revert: `git revert 03b4a82`

## Migration Pattern

Future pages can adopt the same pattern:
1. Add `<script src="/content/products/product-data.js" defer></script>` to the page
2. Use `data-price-code="<NeoLifeCode>"` on price display elements
3. Use `data-ppu-code="<NeoLifeCode>"` with `data-ppu-dilution="<factor>"` for per-use calculations
4. Or use `LevNyttProductData.getPrice(code)` directly in custom scripts
