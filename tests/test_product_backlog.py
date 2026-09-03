"""Tests for the product-backlog decision integration and product-page builder."""

from __future__ import annotations

import json

from commander import decision
from commander import product_page


def _entity(code, name, slug):
    return {
        "neoLife_code": code, "product_name": name, "slug": slug,
        "category": "supplements",
        "short_description": f"{name} kort beskrivning.",
        "summary": f"{name} sammanfattning.",
        "packaging": {"size": 60, "unit": "tabletter", "label": "60 tabletter"},
        "usage": {"dosage": "1 tablett dagligen"},
        "ingredients": [{"name": "Ingrediens"}],
    }


def test_decision_selects_product_backlog_without_keyword():
    evidence = {
        "product_backlog": [{
            "code": "555", "product_name": "Garlic Allium Complex",
            "slug": "neolife-garlic-allium-complex", "category": "supplements",
            "coverage": "MENTIONED_ONLY", "image": "/images/x.jpg",
        }],
        "staged_awaiting_deployment": [],
        "pending_deployment_verification": None,
        "measurement_freshness": {"fresh": True},
    }
    d = decision.decide(evidence, [], [], budget_check=lambda c: True)
    assert d["kind"] == "product_backlog"
    assert d["capability_id"] == "product_page"
    assert d["code"] == "555"


def test_product_backlog_respects_publication_budget():
    evidence = {
        "product_backlog": [{"code": "555", "product_name": "Garlic", "slug": "x", "category": "supplements", "coverage": "NO_CONTENT"}],
        "staged_awaiting_deployment": [], "pending_deployment_verification": None,
        "measurement_freshness": {"fresh": True},
    }
    state = {"project_id": "levnytt", "prior_decisions": [],
             "daily_publication_budget": {"date": "2026-09-03", "used": 1, "limit": 1}}
    d = decision.decide(evidence, [], [], budget_check=lambda c: decision.budget_available(state, "2026-09-03", c))
    # publication budget exhausted -> product_backlog skipped -> falls through to idle
    assert d["kind"] != "product_backlog"


def test_build_product_page_uses_entity_identity(tmp_path):
    e = _entity(555, "Garlic Allium Complex", "neolife-garlic-allium-complex")
    html = product_page.build_product_page(e, "/images/garlic-allium-complex.jpg", tmp_path)
    assert "<h1>NeoLife Garlic Allium Complex</h1>" in html
    assert "Kod 555" in html
    assert 'src="/images/garlic-allium-complex.jpg"' in html
    assert "neolifeshop.com" in html


def test_resolve_image_matches_slug(tmp_path):
    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "garlic-allium-complex.jpg").write_bytes(b"x")
    e = _entity(555, "Garlic Allium Complex", "neolife-garlic-allium-complex")
    assert product_page.resolve_image(e, tmp_path) == "/images/garlic-allium-complex.jpg"
