"""Authoritative NeoLife product-coverage model for the LevNytt Commander.

Product identity is matched by the canonical Product Entity System
(``content/products/entities/<canonical_id>/sv.json``), keyed by the official
NeoLife product code (``neoLife_code``) — never by generic keyword or filename
similarity. The coverage invariant is:

    CURRENT_NEOLIFE_PRODUCT -> DEDICATED_LEVNYTT_PRODUCT_PAGE

A **topic page** (an informational guide whose ``<h1>`` is a generic subject
such as "Vad är C-vitamin…") does NOT satisfy coverage for a product, and one
NeoLife product's page does NOT satisfy coverage for a different NeoLife
product. A dedicated product page is one whose slug matches the product entity
and whose ``<h1>`` names the product itself (e.g. "NeoLife All C").
"""

from __future__ import annotations

import glob
import json
import os
import re
from pathlib import Path
from typing import Any

PRODUCT_ENTITIES_GLOB = "content/products/entities/entity_*/sv.json"

DEDICATED_PAGE_EXISTS = "DEDICATED_PAGE_EXISTS"
MENTIONED_ONLY = "MENTIONED_ONLY"
NO_CONTENT = "NO_CONTENT"
CONTENT_INCOMPLETE = "CONTENT_INCOMPLETE"
PRODUCT_NO_LONGER_CURRENT = "PRODUCT_NO_LONGER_CURRENT"


def _fold(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def load_product_entities(project_root: Path) -> dict[str, dict[str, Any]]:
    """All current product entities, keyed by official NeoLife product code."""
    entities: dict[str, dict[str, Any]] = {}
    for path in sorted(glob.glob(str(project_root / PRODUCT_ENTITIES_GLOB))):
        try:
            entity = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(entity, dict):
            continue
        code = entity.get("neoLife_code")
        if code is None:
            continue
        entities[str(code)] = entity
    return entities


def _page_path(project_root: Path, slug: str) -> Path | None:
    for candidate in (project_root / f"{slug}.html", project_root / slug / "index.html"):
        if candidate.is_file():
            return candidate
    return None


def _page_h1(page: Path) -> str:
    try:
        text = page.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S | re.I)
    if not match:
        return ""
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def _is_dedicated_product_page(entity: dict[str, Any], h1: str) -> bool:
    """A page is a dedicated product page only when its ``<h1>`` names the
    product itself (typically ``NeoLife <product>``), not a generic topic.

    A topic page begins with a subject question ("Vad är C-vitamin…",
    "Vad är CoQ10…") and must not be counted as product coverage, even when the
    product name appears in the heading text.
    """
    name = _fold(str(entity.get("product_name") or ""))
    h1f = _fold(h1)
    if not name:
        return False
    return h1f.startswith("neolife" + name) or h1f.startswith(name)


def classify_product(entity: dict[str, Any], project_root: Path) -> dict[str, Any]:
    """Classify one product entity against the live LevNytt repository.

    Returns a record with ``code``, ``product_name``, ``slug``, ``status``
    (one of DEDICATED_PAGE_EXISTS / MENTIONED_ONLY / NO_CONTENT), the page path,
    and the page's h1 (so a topic page is visibly distinct from a product page).
    """
    code = str(entity.get("neoLife_code"))
    name = str(entity.get("product_name") or "")
    slug = str(entity.get("slug") or "")
    page = _page_path(project_root, slug)
    record = {
        "code": code,
        "product_name": name,
        "slug": slug,
        "category": entity.get("category"),
        "status": NO_CONTENT,
        "page": str(page) if page else None,
        "h1": "",
    }
    if page is None:
        return record
    h1 = _page_h1(page)
    record["h1"] = h1
    record["status"] = DEDICATED_PAGE_EXISTS if _is_dedicated_product_page(entity, h1) else MENTIONED_ONLY
    return record


def compute_coverage(project_root: Path) -> dict[str, Any]:
    """Recompute the complete product coverage inventory."""
    entities = load_product_entities(project_root)
    rows = [classify_product(e, project_root) for e in entities.values()]
    summary: dict[str, int] = {}
    for row in rows:
        summary[row["status"]] = summary.get(row["status"], 0) + 1
    return {
        "schema": "levnytt-neolife-product-coverage-v2",
        "product_count": len(rows),
        "dedicated_product_pages": summary.get(DEDICATED_PAGE_EXISTS, 0),
        "mentioned_only": summary.get(MENTIONED_ONLY, 0),
        "no_content": summary.get(NO_CONTENT, 0),
        "products": rows,
    }


def vitamin_c_family(project_root: Path) -> list[dict[str, Any]]:
    """The three Vitamin C entities: Sustained Release Vitamin C (551),
    All C (552) and the generic topic page."""
    entities = load_product_entities(project_root)
    result = []
    for code in ("551", "552"):
        if code in entities:
            result.append(classify_product(entities[code], project_root))
    return result
