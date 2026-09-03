"""Regression tests for the LevNytt Pinterest channel (pre-publication logic)."""

from __future__ import annotations

import json
from pathlib import Path

from commander import pinterest_channel as pc
from commander import product_page


def test_utm_attribution_appended():
    url = pc.utm_url("https://levnytt.se/neolife-garlic-allium-complex")
    assert url.startswith("https://levnytt.se/neolife-garlic-allium-complex?utm_source=pinterest")
    assert "utm_medium=social" in url


def test_board_selection_for_product_and_informational():
    assert pc.board_for_product("supplements") == "1151232792187766770"
    assert pc.board_for_product("home_care") == "1151232792187766803"
    assert pc.board_for_informational("Vad säger forskningen om vitamin D") == "1151232792187766808"
    assert pc.board_for_informational("En historik om NeoLife 1958") == "1151232792187766813"


def test_pin_key_and_dedup(tmp_path):
    key = pc.pin_key("https://levnytt.se/x", "/images/x.jpg", "Title")
    assert pc.already_published(tmp_path, "https://levnytt.se/x", "/images/x.jpg", "Title") is False
    pc.record_published(tmp_path, key=key, pin_id="123", destination="https://levnytt.se/x", image="/images/x.jpg", title="Title", board_id="b", pin_class="product")
    assert pc.already_published(tmp_path, "https://levnytt.se/x", "/images/x.jpg", "Title") is True


def test_fit_title_truncates_to_100_at_word_boundary():
    long_title = "NeoLife All C — Tuggbar C-vitamin med bioflavonoider — 120 tabletter, för immunförsvar, kollagenbildning och antioxidantskydd."
    fitted = pc._fit_title(long_title)
    assert len(fitted) <= 100
    assert fitted.startswith("NeoLife All C")
    assert not fitted.endswith((" —", "-", ","))


def test_fit_title_leaves_short_titles_untouched():
    assert pc._fit_title("NeoLife All C") == "NeoLife All C"


def test_validate_pin_image_product_agreement(tmp_path):
    img = tmp_path / "garlic-allium-complex.jpg"
    img.write_bytes(b"\xff\xd8\xff\x00fakejpeg")
    opp = {"pin_class": "product", "code": "555", "product_name": "Garlic Allium Complex",
           "destination": "https://levnytt.se/neolife-garlic-allium-complex", "image": "/images/garlic-allium-complex.jpg"}
    ok, reason = pc.validate_pin(opp, img)
    assert ok, reason
    # wrong image -> reject
    bad = tmp_path / "other.jpg"
    bad.write_bytes(b"\xff\xd8\xff\x00")
    opp2 = dict(opp, image="/images/other.jpg")
    ok2, _ = pc.validate_pin(opp2, bad)
    assert ok2 is False


def test_product_pin_opportunities_from_dedicated_pages(tmp_path):
    # A dedicated product page + image yields one product Pin opportunity.
    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "garlic-allium-complex.jpg").write_bytes(b"\xff\xd8\xff\x00")
    entity_dir = tmp_path / "content" / "products" / "entities" / "entity_garlic_allium_complex"
    entity_dir.mkdir(parents=True)
    (entity_dir / "sv.json").write_text(json.dumps({
        "neoLife_code": 555, "product_name": "Garlic Allium Complex", "slug": "neolife-garlic-allium-complex",
        "category": "supplements", "short_description": "Vitlök med lök och purjolök.",
        "summary": "Allium-spektrum.", "packaging": {"size": 60, "unit": "tabletter", "label": "60 tabletter"},
        "usage": {"dosage": "1 dagligen"}, "ingredients": [{"name": "Vitlök"}],
    }), encoding="utf-8")
    (tmp_path / "neolife-garlic-allium-complex.html").write_text("<h1>NeoLife Garlic Allium Complex</h1>", encoding="utf-8")
    opps = pc.product_pin_opportunities(tmp_path)
    assert any(o["code"] == "555" and o["pin_class"] == "product" for o in opps)


def test_publish_returns_blocked_status_when_trial_access(tmp_path, monkeypatch):
    img = tmp_path / "garlic-allium-complex.jpg"
    img.write_bytes(b"\xff\xd8\xff\x00")
    opp = {"pin_class": "product", "code": "555", "product_name": "Garlic Allium Complex",
           "destination": "https://levnytt.se/neolife-garlic-allium-complex", "image": "garlic-allium-complex.jpg",
           "title": "NeoLife Garlic Allium Complex", "description": "desc", "board_id": "1151232792187766770"}

    class _FakeProvider:
        def publish_package(self, package, approved=False):
            from app.providers.pinterest import PinterestError
            raise PinterestError("Apps with Trial access may not create Pins in production")

    import app.providers.pinterest as pin_provider
    monkeypatch.setattr(pin_provider, "PinterestProvider", lambda: _FakeProvider())
    result = pc.publish(tmp_path, opp, tmp_path)
    assert result["status"] == "BLOCKED_BY_PINTEREST_STANDARD_ACCESS"
    assert result["status"] != "PUBLISHED"
