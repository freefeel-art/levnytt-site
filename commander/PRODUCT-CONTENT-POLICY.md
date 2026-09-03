# LevNytt NeoLife Product-Content Policy

**Coverage invariant:** every current product in the Swedish NeoLife catalog must
eventually have its own dedicated LevNytt product page. This is not conditional
on search volume; search/GSC/DataForSEO evidence determines *priority and
optimization strategy*, never whether a current product deserves coverage.

## Product identity is by code, not keyword

- Product identity is matched by the official **NeoLife product code**
  (`neoLife_code`) from the Product Entity System
  (`content/products/entities/<canonical_id>/sv.json`).
- Two products are never merged merely because they address the same generic
  topic. For example:
  - generic C-vitamin guide = **TOPIC_PAGE**
  - Sustained Release Vitamin C, code **551** = one PRODUCT
  - All C, code **552** = another PRODUCT

## Classification rules

| Status | Meaning |
|---|---|
| `DEDICATED_PAGE_EXISTS` | a page whose slug matches the entity and whose `<h1>` names the product itself (`NeoLife <product>`), not a topic question |
| `MENTIONED_ONLY` | the product is mentioned inside a topic page or another product's page, but has no dedicated product page |
| `NO_CONTENT` | no page references the product at all |
| `CONTENT_INCOMPLETE` | a dedicated page exists but its facts are stale or missing against current official NeoLife documentation |
| `PRODUCT_NO_LONGER_CURRENT` | the product is no longer in the current Swedish catalog |

A **topic page** never satisfies `DEDICATED_PAGE_EXISTS`, and one NeoLife
product's page never satisfies coverage for a different NeoLife product.

## Production rules

- Before producing a page, confirm the exact product identity/code against the
  current official NeoLife documentation (authenticated back office), and
  against the entity's `neoLife_code`, image, package size and shop path.
- Never reuse another similar product's image.
- Never produce a duplicate when a dedicated page already exists.
- Authoritative NeoLife product materials (product cards/PDFs) are the primary
  source of truth for product facts; absence of a fact is `UNKNOWN`, never
  invented.
