"""Regression tests for official NeoLife catalog discovery and entity ingestion."""

from __future__ import annotations

import json
from pathlib import Path

from commander import decision, product_catalog


def _entity(code: int) -> dict:
    return {
        "canonical_id": "entity_known",
        "neoLife_code": code,
        "locale": "sv",
        "slug": "neolife-known",
        "product_name": "Known",
        "category": "supplements",
    }


def test_catalog_parser_uses_official_code_name_and_shop_path_without_product_name_rules():
    discovered_name = "Fixture discovery product"
    html = """
    <ul>
      <li data-product data-element-id="1" data-element-type="product">
        <div class="product-box">
          <a href="https://se.neolifeshop.com/p/kosttillskott/catalog-entry-1.html">
            <img src="/thumb/123/350x350/4242_new.jpg" width="350" height="350" alt="Fixture discovery product" title="Fixture discovery product"/>
          </a>
          <div class="product-info"><h2><a href="https://se.neolifeshop.com/p/kosttillskott/catalog-entry-1.html">Fixture discovery product</a><br></h2></div>
        </div>
      </li>
    </ul>
    """
    rows = product_catalog.parse_catalog(html, "supplements")
    assert [row["neoLife_code"] for row in rows] == ["4242"]
    assert rows[0]["product_name"] == discovered_name
    assert rows[0]["shop_path"].endswith("catalog-entry-1.html")


def test_ingest_adds_only_officially_discovered_codes_missing_locally(tmp_path: Path):
    entity_dir = tmp_path / "content" / "products" / "entities" / "entity_known"
    entity_dir.mkdir(parents=True)
    (entity_dir / "sv.json").write_text(json.dumps(_entity(100)), encoding="utf-8")
    runtime = tmp_path / "runtime"
    rows = [
        {"neoLife_code": "100", "product_name": "Known", "slug": "neolife-known",
         "category": "supplements", "shop_path": "/p/known.html", "official_image": "/thumb/1/1x1/100.jpg"},
        {"neoLife_code": "4242", "product_name": "Fixture discovery product",
         "slug": "neolife-fixture-discovery-product", "category": "supplements",
         "shop_path": "/p/catalog-entry-1.html", "official_image": "/thumb/2/1x1/4242.jpg"},
    ]
    receipt = product_catalog.ingest_missing_entities(tmp_path, runtime, rows)
    assert receipt["new_entities"] == [{"code": "4242", "slug": "neolife-fixture-discovery-product"}]
    added = json.loads((tmp_path / "content" / "products" / "entities" /
                        "entity_fixture_discovery_product" / "sv.json").read_text())
    assert added["neoLife_code"] == 4242
    assert added["source"]["type"] == "NEOLIFE_OFFICIAL_PUBLIC_CATALOG"
    assert json.loads((runtime / "intelligence" / product_catalog.CATALOG_ARTIFACT).read_text())["new_entity_count"] == 1


def test_product_discovery_is_decision_reachable_before_product_backlog():
    evidence = {
        "product_catalog_discovery_due": True,
        "product_backlog": [{"code": "100", "product_name": "Known", "slug": "neolife-known"}],
        "staged_awaiting_deployment": [],
        "pending_deployment_verification": None,
        "measurement_freshness": {"fresh": True},
    }
    selected = decision.decide(evidence, [], [], budget_check=lambda _capability: True)
    assert selected["capability_id"] == "product_discovery"
    assert selected["opportunity_id"] == "product-catalog:refresh"
