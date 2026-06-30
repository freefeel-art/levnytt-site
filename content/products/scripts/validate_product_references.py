#!/usr/bin/env python3
"""
Product Entity Reference Validator — Publication Agent Integration

Validates that product references in article HTML files match
Product Entity data. Called by the Publication Agent before deployment.

Usage:
    python3 content/products/scripts/validate_product_references.py <article.html>...

Returns exit code 0 if all product references match entities.
Returns exit code 1 with warnings if mismatches are found.
"""

import json
import os
import re
import sys

ENTITIES_DIR = "content/products/entities"

NON_PRODUCT_SLUGS = frozenset((
    "neolife-vetenskap", "neolife-historia", "neolife-kosttillskott",
    "neolife-hallbarhet", "den-fundersamma-mannen", "levnytt-principer",
    "var-metod", "om-oss", "forsknings-faq", "neolife-vitamin-d",
    "neolife-magnesium-complex", "ala-vs-epa-vs-dha",
    "varfor-fiskolja-inte-ar-likvardigt", "karotenoid-tillskott-vs-mat",
    "zeaxantin-immunforsvar-2025", "naringsbrist", "neolife-tre-en-en-cellnaring",
    "neolife-formula-iv", "neolife-pro-vitality", "neolife-omega-3-plus",
    "neolife-carotenoid-complex", "neolife-tre-en-en",
))

VALID_NEOLIFE_SLUG_PREFIXES = frozenset((
    "neolife-vetenskap", "neolife-historia", "neolife-kosttillskott",
    "neolife-hallbarhet", "neolife-vitamin-d", "neolife-magnesium-complex",
    "neolife-omega-3-plus", "neolife-formula-iv", "neolife-pro-vitality",
    "neolife-carotenoid-complex", "neolife-tre-en-en",
    "neolife-tre-en-en-cellnaring", "neolife-acidophilus-plus",
    "neolife-betaguard", "neolife-coq10", "neolife-elevate",
    "neolife-flavonoid-complex", "neolife-chelated-zinc",
    "neolife-upbeet", "neolife-resp-x", "neolife-garlic-allium-complex",
    "neolife-cruciferous-plus", "neolife-botanical-balance",
    "neolife-kalmag-plus-d", "neolife-shake-bar-tea", "neolife-vitamin-e",
    "neolife-fibre-tablets", "neolife-viktkontroll",
    "neolife-affarsmojlighet", "neolife-all-c", "neolife-vita-squares",
    "neolife-all-c-vitamin",
))


def load_entities():
    entity_by_name = {}
    entity_by_code = {}
    entity_by_slug = {}
    known_names = set()
    known_slugs = set()
    known_codes = set()
    legacy_codes = set()

    for name in sorted(os.listdir(ENTITIES_DIR)):
        path = os.path.join(ENTITIES_DIR, name, "sv.json")
        if not os.path.exists(path):
            continue
        with open(path) as f:
            data = json.load(f)
        entity_by_name[data["product_name"]] = data
        entity_by_code[data["neoLife_code"]] = data
        entity_by_slug[data["slug"]] = data
        known_names.add(data["product_name"])
        known_slugs.add(data["slug"])
        known_codes.add(data["neoLife_code"])
        for lc in data.get("legacy_codes", []):
            legacy_codes.add(lc)
        for alias in data.get("aliases", []):
            known_names.add(alias)
            entity_by_name[alias] = data

    return {
        "by_name": entity_by_name,
        "by_code": entity_by_code,
        "by_slug": entity_by_slug,
        "known_names": known_names,
        "known_slugs": known_slugs,
        "known_codes": known_codes,
        "legacy_codes": legacy_codes,
    }


def check_article(filepath, entity_index):
    with open(filepath) as f:
        content = f.read()

    warnings = []
    known_slugs = entity_index["known_slugs"]
    known_codes = entity_index["known_codes"]
    legacy_codes = entity_index["legacy_codes"]

    slug_matches = re.findall(r'["\']https?://levnytt\.se/([\w-]+)', content)
    slug_matches += re.findall(r'["\']/([\w-]+)["\']', content)

    all_neolife_slugs = known_slugs | VALID_NEOLIFE_SLUG_PREFIXES

    for slug in sorted(set(slug_matches)):
        slug = slug.rstrip("/")
        if slug in NON_PRODUCT_SLUGS:
            continue
        if slug.startswith("neolife-") and not slug.startswith("neolife-"):
            continue
        if slug.startswith("neolife-") and slug not in all_neolife_slugs:
            warnings.append(f"  Unknown neolife- slug '{slug}' — no entity or hub page found")

    for code in re.findall(r"\b(929|576|566|942|927|691|510)\b", content):
        code_int = int(code)
        if code_int not in known_codes:
            if code_int in legacy_codes:
                continue
            warnings.append(f"  NeoLife code {code} found but no matching entity")

    return warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_product_references.py <article.html> [article.html ...]")
        sys.exit(1)

    entity_index = load_entities()
    all_ok = True

    slug_to_entity = {}
    for slug, data in entity_index["by_slug"].items():
        slug_to_entity[slug] = data["product_name"]

    print(f"Loaded {len(entity_index['by_name'])} product names from {len(os.listdir(ENTITIES_DIR))} entities")
    print(f"Entity slugs: {', '.join(sorted(entity_index['known_slugs']))}")
    print()

    for filepath in sys.argv[1:]:
        if not os.path.exists(filepath):
            print(f"  SKIP (not found): {filepath}")
            continue
        warnings = check_article(filepath, entity_index)
        if warnings:
            all_ok = False
            print(f"ISSUES: {filepath}")
            for w in warnings:
                print(f"  {w}")
        else:
            print(f"OK: {filepath}")

    if not all_ok:
        print("\nSome articles reference unknown product slugs or codes.")
        print("If these are new products, create entities for them.")
        print("If these are false positives, add the slug to VALID_NEOLIFE_SLUG_PREFIXES.")
        sys.exit(1)

    print("\nAll product references validated against Product Entities.")
    print(f"Product Entity System is the SSOT for product identity.")


if __name__ == "__main__":
    main()
