"""Regression tests for the internal-link publication rule."""

from __future__ import annotations

from commander import product_page


def _entity(code, name, slug, related=()):
    return {
        "neoLife_code": code, "product_name": name, "slug": slug,
        "category": "supplements",
        "short_description": f"{name} kort beskrivning.",
        "summary": f"{name} sammanfattning.",
        "packaging": {"size": 60, "unit": "tabletter", "label": "60 tabletter"},
        "usage": {"dosage": "1 tablett dagligen"},
        "ingredients": [{"name": "Ingrediens"}],
        "related_article_slugs": list(related),
    }


def test_generated_product_page_cannot_link_to_itself(tmp_path):
    # The entity's related_article_slugs names the product's own slug (the old
    # topic-page location). The builder must drop it rather than self-link.
    e = _entity(555, "Garlic Allium Complex", "neolife-garlic-allium-complex",
                related=["neolife-garlic-allium-complex"])
    html = product_page.build_product_page(e, "/images/x.jpg", tmp_path)
    assert 'href="/neolife-garlic-allium-complex"' not in html
    assert "Läs mer i vår guide" not in html


def test_related_link_omitted_when_no_distinct_destination(tmp_path):
    e = _entity(555, "Garlic Allium Complex", "neolife-garlic-allium-complex", related=[])
    html = product_page.build_product_page(e, "/images/x.jpg", tmp_path)
    assert "Läs mer i vår guide" not in html


def test_distinct_related_article_used_when_it_exists(tmp_path):
    (tmp_path / "neolife-vitamin-d.html").write_text("<h1>topic</h1>", encoding="utf-8")
    e = _entity(865, "Vegan D", "neolife-vegan-d", related=["neolife-vitamin-d"])
    assert product_page.distinct_related_article(e, tmp_path) == "neolife-vitamin-d"
    html = product_page.build_product_page(e, "/images/x.jpg", tmp_path)
    assert 'href="/neolife-vitamin-d"' in html
    assert 'href="/neolife-vegan-d"' not in html


def test_validate_internal_links_detects_self_link(tmp_path):
    html = '<a href="/neolife-garlic-allium-complex">NeoLife Garlic</a>'
    defects = product_page.validate_internal_links(html, "neolife-garlic-allium-complex", tmp_path)
    assert any(d["kind"] == "self_link" for d in defects)


def test_validate_internal_links_detects_stale_destination(tmp_path):
    html = '<a href="/no-such-page">Missing</a>'
    defects = product_page.validate_internal_links(html, "other", tmp_path)
    assert any(d["kind"] == "stale_destination" for d in defects)


def test_validate_internal_links_detects_duplicate_destination(tmp_path):
    (tmp_path / "other.html").write_text("<h1>x</h1>", encoding="utf-8")
    html = '<a href="/other">One</a><a href="/other">Two</a>'
    defects = product_page.validate_internal_links(html, "current", tmp_path)
    assert any(d["kind"] == "duplicate_destination" for d in defects)
