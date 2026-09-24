"""Discover current NeoLife products from the official public shop catalog.

The catalog is the source of truth for product existence. Existing LevNytt
entities remain authoritative for their editorial facts; discovery only creates
minimal, explicitly sourced entities for official products not known locally.
"""

from __future__ import annotations

from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import re
import tempfile
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

from commander import product_media


CATALOG_ARTIFACT = "neolife-product-catalog.json"
CATALOG_TTL_DAYS = 1
USER_AGENT = product_media.USER_AGENT

_CATEGORY_PATHS = {
    "supplements": ("/c/kosttillskott/", "supplements"),
    "weight_management": ("/c/viktkontroll/", "weight_management"),
    "personal_care": ("/c/personlig-vard/", "personal_care"),
    "skin_care": ("/c/personlig-vard/", "skin_care"),
    "home_care": ("/c/rengoring/", "home_care"),
    "accessories": ("/c/rengoring/", "accessories"),
}
_VOID_TAGS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
})


def artifact_path(runtime: Path) -> Path:
    return runtime / "intelligence" / CATALOG_ARTIFACT


def _slugify(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    folded = re.sub(r"[^a-zA-Z0-9]+", "-", folded.lower()).strip("-")
    return f"neolife-{folded}" if folded else "neolife-product"


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


class _CatalogParser(HTMLParser):
    """Extract product cards without depending on presentation CSS classes."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.products: list[dict[str, str]] = []
        self._card: dict[str, str] | None = None
        self._card_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "li" and "data-product" in values:
            self._card = {}
            self._card_depth = 1
            return
        if self._card is None:
            return
        if tag not in _VOID_TAGS:
            self._card_depth += 1
        if tag == "img" and values.get("src"):
            self._card.setdefault("image", values["src"])
            self._card.setdefault("product_name", values.get("alt", ""))
        elif tag == "a" and values.get("href"):
            self._card.setdefault("shop_path", urlparse(values["href"]).path)

    def handle_endtag(self, tag: str) -> None:
        if self._card is None:
            return
        if tag in _VOID_TAGS:
            return
        self._card_depth -= 1
        if tag == "li" and self._card_depth == 0:
            product = {key: _clean_text(value) for key, value in self._card.items()}
            if product.get("image") and product.get("product_name") and product.get("shop_path"):
                self.products.append(product)
            self._card = None

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        # ``img`` is commonly serialized as a self-closing tag; it must not
        # alter the card depth used by the surrounding ``li``.
        if self._card is None or tag != "img":
            return
        values = {key: value or "" for key, value in attrs}
        if values.get("src"):
            self._card.setdefault("image", values["src"])
            self._card.setdefault("product_name", values.get("alt", ""))


def parse_catalog(html: str, category: str) -> list[dict[str, Any]]:
    parser = _CatalogParser()
    parser.feed(html or "")
    products: dict[str, dict[str, Any]] = {}
    for raw in parser.products:
        image_name = Path(urlparse(raw["image"]).path).name
        code_match = re.match(r"(\d+)(?:[_-].*)?\.[a-z0-9]+$", image_name, re.I)
        if not code_match:
            continue
        code = code_match.group(1)
        name = raw["product_name"]
        products[code] = {
            "neoLife_code": code,
            "product_name": name,
            "slug": _slugify(name),
            "category": category,
            "shop_path": raw["shop_path"],
            "official_image": raw["image"],
        }
    return sorted(products.values(), key=lambda row: int(row["neoLife_code"]))


def _fetch(url: str, timeout: int = 30) -> str:
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    response.raise_for_status()
    return response.text


def discover_catalog(*, timeout: int = 30) -> list[dict[str, Any]]:
    """Fetch and merge the official public Swedish catalog category pages."""
    discovered: dict[str, dict[str, Any]] = {}
    fetched_paths: set[str] = set()
    for category, (path, entity_category) in _CATEGORY_PATHS.items():
        if path in fetched_paths:
            continue
        fetched_paths.add(path)
        rows = parse_catalog(_fetch(product_media.SHOP_BASE + path, timeout), entity_category)
        for row in rows:
            discovered.setdefault(row["neoLife_code"], row)
    return sorted(discovered.values(), key=lambda row: int(row["neoLife_code"]))


def _entity(row: dict[str, Any], now: str) -> dict[str, Any]:
    name = str(row["product_name"])
    code = int(row["neoLife_code"])
    slug = str(row["slug"])
    return {
        "canonical_id": f"entity_{slug.removeprefix('neolife-').replace('-', '_')}",
        "neoLife_code": code,
        "locale": "sv",
        "slug": slug,
        "product_name": name,
        "aliases": [],
        "category": row["category"],
        "short_description": f"NeoLife {name}. Officiell produktkatalogpost, kod {code}.",
        "summary": "Produktfakta behöver kompletteras från verifierade officiella källor.",
        "ingredients": [],
        "usage": {},
        "packaging": {},
        "shop_path": row["shop_path"],
        "media": {"official_catalog_image": row["official_image"]},
        "source": {
            "type": "NEOLIFE_OFFICIAL_PUBLIC_CATALOG",
            "url": product_media.SHOP_BASE + row["shop_path"],
            "verified_at": now,
        },
        "last_verified": now[:10],
        "entity_version": 1,
    }


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with open(handle, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
        Path(temporary).replace(path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def ingest_missing_entities(project_root: Path, runtime: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Write only missing official products and persist the catalog receipt."""
    known = set()
    entities_root = project_root / "content" / "products" / "entities"
    for path in entities_root.glob("entity_*/sv.json"):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(value, dict) and value.get("neoLife_code") is not None:
            known.add(str(value["neoLife_code"]))

    now = datetime.now(timezone.utc).isoformat()
    added: list[dict[str, Any]] = []
    for row in rows:
        if str(row["neoLife_code"]) in known:
            continue
        entity = _entity(row, now)
        path = entities_root / f"entity_{entity['canonical_id'].removeprefix('entity_')}" / "sv.json"
        if path.exists():
            continue
        _atomic_json(path, entity)
        known.add(str(row["neoLife_code"]))
        added.append({"code": str(row["neoLife_code"]), "slug": entity["slug"]})

    artifact = {
        "source": product_media.SHOP_BASE,
        "source_type": "NEOLIFE_OFFICIAL_PUBLIC_CATALOG",
        "fetched_at": now,
        "products": rows,
        "new_entity_count": len(added),
        "new_entities": added,
    }
    _atomic_json(artifact_path(runtime), artifact)
    return {"catalog_count": len(rows), "new_entities": added, "fetched_at": now}


def discovery_due(runtime: Path, now: datetime | None = None) -> bool:
    path = artifact_path(runtime)
    if not path.is_file():
        return True
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        fetched = datetime.fromisoformat(str(data["fetched_at"]).replace("Z", "+00:00"))
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return True
    observed = now or datetime.now(timezone.utc)
    if fetched.tzinfo is None:
        fetched = fetched.replace(tzinfo=timezone.utc)
    return (observed - fetched).total_seconds() >= CATALOG_TTL_DAYS * 86400
