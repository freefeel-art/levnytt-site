# LevNytt Product Entities

This directory contains structured product data for every NeoLife product marketed on LevNytt.se.

## Structure

```
content/products/
├── README.md                     ← This file
├── categories.json               ← Category and subcategory taxonomy
└── entities/
    ├── entity_<canonical_id>/
    │   ├── sv.json               ← Swedish product entity
    │   └── ... (future: en.json, images, etc.)
    └── ...
```

## Creating a new product entity

1. Create `content/products/entities/<canonical_id>/sv.json`
2. Follow the schema in `docs/specifications/PRODUCT-ENTITY-SYSTEM.md`
3. Use `categories.json` for valid `category` and `subcategory` values
4. Reference `docs/databank/LEVNYTT-PRICE-DATABASE.md` for price data — do not duplicate prices
5. Set `entity_version: 1` and `last_verified` to the current date

## Validation checklist

- [ ] `canonical_id` is unique
- [ ] `neoLife_code` matches Price Database
- [ ] `category`/`subcategory` are from `categories.json`
- [ ] All required fields populated
- [ ] No price data in entity (prices stay in Price Database)
- [ ] `shop_path` matches a NeoLife SE product page
- [ ] `related_product_ids` reference existing entities
- [ ] If `variants` used: unique codes per variant, valid Price DB refs
- [ ] If `status: "inactive"`: product in Price DB, not actively marketed

## Usage

Entities are consumed by:
- **Pillar pages** — for consistent product metadata
- **Publication Agent** — for validating product references in articles
- **Calculators** — for packaging and dosage data
- **Future tools** — comparison tables, recommendation engines, video scripts

## Current status

**Product Entity System: Complete (Sprint 14)**

| Category | Entities | With variants | Inactive |
|---|---|---|---|
| Supplements | 29 | 0 | 2 (Multi, Bio-Tone) |
| Weight Management | 3 | 1 (NeoLifeShake: 3 flavors) | 0 |
| Home Care | 4 | 2 (Super 10: 4 sizes, LDC: 2 sizes) | 0 |
| Personal Care | 6 | 0 | 0 |
| Skin Care | 9 | 0 | 0 |
| Accessories | 10 | 0 | 0 |
| **Total** | **61** | **3 (9 variants)** | **2** |

All 57 NeoLife product codes from the Price Database are represented across 61 entity files (4 additional codes covered by multi-variant entities).
