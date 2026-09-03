# LevNytt Pinterest Operating Model

Pinterest is a **distribution channel** for LevNytt, never a destination. Every
Pin points at a LevNytt-owned page; the site is the conversion asset.

## Current access state (verified 2026-09-03)

- OAuth app + access/refresh tokens present and refreshable.
- `boards:read` + `pins:read` + `pins:write` granted; **`boards:write` missing**,
  so `POST /pins` is rejected. The token scopes must be re-authorized.
- Six PUBLIC boards already exist and map cleanly onto LevNytt content:

| Board | Board ID | Pin class |
|---|---|---|
| NeoLife Kosttillskott | 1151232792187766770 | PRODUCT (supplements/weight) |
| NeoLife Historia | 1151232792187766813 | INFORMATIONAL (brand/history) |
| Vetenskap & Näring | 1151232792187766808 | INFORMATIONAL (science/nutrition) |
| Hälsosam Livsstil | 1151232792187766810 | INFORMATIONAL (lifestyle) |
| Hållbar Städning | 1151232792187766803 | PRODUCT (home care) |
| LevNytt – Hälsa | 1151232792188035184 | INFORMATIONAL (health) |

## Pin classes

1. **PRODUCT PIN** — eligible only when a current NeoLife product has a verified
   dedicated PRODUCT_PAGE. Uses the exact product identity, code and image.
   Destination = the product page (`https://levnytt.se/<slug>`).
2. **INFORMATIONAL PIN** — an existing informational/topic article. Destination
   = the most relevant topic article; never force a topic Pin onto a product page.

## Rules (permanent)

- A Pin must never use one product's image while linking to/describing another.
- Destination, image, product code/name must agree (deterministic validation).
- No invented product facts, benefits or health claims; Swedish; factual.
- No verbatim NeoLife marketing copy.
- Deduplicate by (destination_url, image, title) in the LevNytt publication
  ledger so a scheduled cycle never republishes the same Pin.
- A second Pin for the same destination is allowed only when it is a genuinely
  distinct angle (e.g. product vs "how to choose" informational).
- Attribution: UTM params (`utm_source=pinterest&utm_medium=social&utm_campaign=levnytt`) on the destination URL.
- Production verification: confirm the created Pin id + destination link.

## Decision integration

- Newly published PRODUCT_PAGE → downstream PRODUCT_PIN opportunity.
- High-value informational articles → INFORMATIONAL_PIN opportunity.
- `pinterest` capability in the Commander loop: evidence → opportunity → decision
  → Pin creation → publication → verify → ledger → learning → prioritization.

## Owner boundary

Publication is blocked only on the missing `boards:write` scope. The Owner must
re-authorize the Pinterest app (the provider's `DEFAULT_SCOPES` now includes
`boards:write`) via the OAuth flow; no other Owner decision is required.
