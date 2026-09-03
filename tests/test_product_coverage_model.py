"""Tests for the authoritative NeoLife product-coverage model.

These prove product identity is matched by the official NeoLife product code and
that a topic page never satisfies DEDICATED_PAGE_EXISTS for a product.
"""

from __future__ import annotations

from pathlib import Path

from commander import product_coverage as pc


def _entity(code, name, slug):
    return {"neoLife_code": code, "product_name": name, "slug": slug, "category": "supplements"}


def test_topic_page_does_not_satisfy_product_coverage(tmp_path: Path):
    # A page whose h1 is a generic topic question, even if it mentions the
    # product, is MENTIONED_ONLY, never a dedicated product page.
    (tmp_path / "neolife-all-c.html").write_text(
        "<h1>Vad är C-vitamin — och hur mycket behöver man?</h1><p>kod 552</p>",
        encoding="utf-8",
    )
    record = pc.classify_product(_entity(552, "All C", "neolife-all-c"), tmp_path)
    assert record["status"] == pc.MENTIONED_ONLY


def test_dedicated_product_page_is_recognised(tmp_path: Path):
    (tmp_path / "neolife-sustained-vitamin-c").mkdir()
    (tmp_path / "neolife-sustained-vitamin-c" / "index.html").write_text(
        "<h1>NeoLife Sustained Release Vitamin C</h1><p>Kod 551</p>",
        encoding="utf-8",
    )
    record = pc.classify_product(_entity(551, "Sustained Release Vitamin C", "neolife-sustained-vitamin-c"), tmp_path)
    assert record["status"] == pc.DEDICATED_PAGE_EXISTS


def test_no_page_is_no_content(tmp_path: Path):
    record = pc.classify_product(_entity(552, "All C", "neolife-all-c"), tmp_path)
    assert record["status"] == pc.NO_CONTENT


def test_one_product_page_does_not_cover_another_product(tmp_path: Path):
    # A generic topic page named after one slug does not cover a different code.
    (tmp_path / "neolife-all-c.html").write_text(
        "<h1>Vad är C-vitamin — och hur mycket behöver man?</h1>", encoding="utf-8"
    )
    # Sustained Release Vitamin C has its own slug, distinct from All C.
    record = pc.classify_product(_entity(551, "Sustained Release Vitamin C", "neolife-sustained-vitamin-c"), tmp_path)
    assert record["status"] == pc.NO_CONTENT
