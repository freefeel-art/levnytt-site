"""Official NeoLife product-image acquisition for the dedicated LevNytt Commander.

The product-page executor previously treated the official product image as an
Owner-only dependency: it looked in the local ``images/`` directory and, when the
exact image was absent, returned ``EVIDENCE_REQUIRED`` and blocked. That turns
one missing asset into a permanent stall, because the product then re-blocks on
every cycle forever.

This module is the autonomous recovery path for exactly that blocker. It follows
a bounded, evidence-bound resolution chain, in order:

    1. local validated assets                 (``product_page.resolve_image``)
    2. entity ``media`` fields                (rejected when they are the generic
                                               brand placeholder, never a product)
    3. the public NeoLife shop category page  (this module)

The shop exposes every current product thumbnail at a deterministic URL of the
form ``/thumb/<image_id>/<size>/<code>.<ext>`` where ``<code>`` is the NeoLife
product code (the same integer stored in the entity as ``neoLife_code``). The
code in the asset's own filename is the identity tie: an image whose filename
does not begin with the product's code is never accepted, so a wrong product or
a coincidental filename can never be substituted.

Acquisition is strictly read-only against the shop and stores the verified
download under the project's normal asset path (``images/<slug>.<ext>``), the
same directory ``product_page.resolve_image`` reads, so the next cycle finds it
locally and does not re-fetch.

Nothing here fabricates, generates, or guesses an image. Every non-success
returns a truthful status (``ACQUIRED`` / ``NOT_FOUND`` / ``UNMAPPED_CATEGORY`` /
``UNAVAILABLE`` / ``NO_CODE``) and never a fabricated success.
"""

from __future__ import annotations

import io
import os
import re
import tempfile
from pathlib import Path
from typing import Any

import requests
from PIL import Image

SHOP_BASE = "https://se.neolifeshop.com"
USER_AGENT = "Mozilla/5.0 (compatible; LevNyttHermes/1.0; +https://levnytt.se)"

ACQUIRED = "ACQUIRED"
NOT_FOUND = "NOT_FOUND"
UNMAPPED_CATEGORY = "UNMAPPED_CATEGORY"
UNAVAILABLE = "UNAVAILABLE"
NO_CODE = "NO_CODE"

# The shop's Swedish category paths, keyed by the entity's English ``category``.
# Discovered from the shop's own category navigation (2026-09-10): supplements ->
# kosttillskott; personal-care and skin-care both live under personlig-vard;
# home-care and accessories both live under rengoring; weight-management ->
# viktkontroll. A category not present here fails closed (UNMAPPED_CATEGORY), it
# is never guessed.
_CATEGORY_PATHS: dict[str, str] = {
    "supplements": "/c/kosttillskott/",
    "personal-care": "/c/personlig-vard/",
    "skin-care": "/c/personlig-vard/",
    "home-care": "/c/rengoring/",
    "accessories": "/c/rengoring/",
    "weight-management": "/c/viktkontroll/",
}

# A product thumbnail is ``/thumb/<image_id>/<size>/<code>[_suffix].<ext>``.
_THUMB_RE = re.compile(r"/thumb/(\d+)/[0-9x]+/([a-z0-9._-]+)", re.IGNORECASE)
_LEADING_CODE_RE = re.compile(r"^(\d+)")
_ALLOWED_EXTENSIONS = ("jpg", "jpeg", "png", "webp")
_MIN_IMAGE_BYTES = 64


def _category_path(category: str) -> str | None:
    return _CATEGORY_PATHS.get(str(category or "").strip().casefold())


def _validate_image_bytes(data: bytes) -> bool:
    """Fail closed: the downloaded bytes must be a real, decodable image."""
    if not data or len(data) < _MIN_IMAGE_BYTES:
        return False
    try:
        image = Image.open(io.BytesIO(data))
        fmt = image.format
        image.verify()
    except Exception:
        return False
    return (fmt or "").upper() in ("JPEG", "PNG", "WEBP")


def _store_image(project_root: Path, slug: str, extension: str, data: bytes) -> str:
    """Atomically store a validated image under the project's normal asset path."""
    images_dir = project_root / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    destination = images_dir / f"{slug}.{extension}"
    fd, temporary = tempfile.mkstemp(prefix=".product-image.", dir=images_dir)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise
    return f"/images/{slug}.{extension}"


def _extension_from_name(name: str) -> str:
    ext = (name.rsplit(".", 1)[-1] if "." in name else "").casefold()
    if ext == "jpeg":
        return "jpg"
    return ext if ext in _ALLOWED_EXTENSIONS else "jpg"


def acquire_official_image(
    entity: dict[str, Any],
    project_root: Path,
    *,
    timeout: int = 30,
) -> dict[str, Any]:
    """Attempt to acquire the official product image from the public NeoLife shop.

    Returns ``{"status", "image", "detail", "source_url"}`` where ``status`` is
    one of ACQUIRED / NOT_FOUND / UNMAPPED_CATEGORY / UNAVAILABLE / NO_CODE and
    ``image`` is a relative ``/images/...`` path only when status is ACQUIRED.
    """
    code = str(entity.get("neoLife_code") or "").strip()
    slug = str(entity.get("slug") or "").strip()
    category = str(entity.get("category") or "").strip()

    if not code:
        return {"status": NO_CODE, "image": None,
                "detail": "product entity has no neoLife_code", "source_url": None}
    if not slug:
        return {"status": NO_CODE, "image": None,
                "detail": "product entity has no slug", "source_url": None}

    category_path = _category_path(category)
    if category_path is None:
        return {"status": UNMAPPED_CATEGORY, "image": None,
                "detail": f"no shop category mapping for {category!r}",
                "source_url": None}

    listing_url = SHOP_BASE + category_path
    try:
        response = requests.get(
            listing_url, headers={"User-Agent": USER_AGENT}, timeout=timeout, allow_redirects=True
        )
    except requests.RequestException as error:
        return {"status": UNAVAILABLE, "image": None,
                "detail": f"shop category page unreachable: {type(error).__name__}",
                "source_url": listing_url}

    if response.status_code >= 400:
        return {"status": UNAVAILABLE, "image": None,
                "detail": f"shop category page returned HTTP {response.status_code}",
                "source_url": listing_url}

    # Find the thumbnail whose filename begins with this product's code. The
    # code is the identity tie: it is the shop's own product key, not a guess.
    match = None
    for thumb_match in _THUMB_RE.finditer(response.text or ""):
        image_id = thumb_match.group(1)
        filename = thumb_match.group(2)
        code_match = _LEADING_CODE_RE.match(filename)
        if code_match and code_match.group(1) == code:
            match = (image_id, filename)
            break

    if match is None:
        return {"status": NOT_FOUND, "image": None,
                "detail": f"no shop image whose filename carries product code {code}",
                "source_url": listing_url}

    image_id, filename = match
    # Full-size asset. The shop serves the same asset without a size constraint.
    full_url = f"{SHOP_BASE}/thumb/{image_id}/0x0/{filename}"

    try:
        image_response = requests.get(
            full_url, headers={"User-Agent": USER_AGENT}, timeout=timeout, allow_redirects=True
        )
    except requests.RequestException as error:
        return {"status": UNAVAILABLE, "image": None,
                "detail": f"image download failed: {type(error).__name__}",
                "source_url": full_url}

    if image_response.status_code >= 400:
        return {"status": UNAVAILABLE, "image": None,
                "detail": f"image download returned HTTP {image_response.status_code}",
                "source_url": full_url}

    data = image_response.content
    if not _validate_image_bytes(data):
        return {"status": NOT_FOUND, "image": None,
                "detail": f"downloaded asset for code {code} is not a decodable image",
                "source_url": full_url}

    extension = _extension_from_name(filename)
    try:
        stored = _store_image(project_root, slug, extension, data)
    except OSError as error:
        return {"status": UNAVAILABLE, "image": None,
                "detail": f"could not store image: {error}", "source_url": full_url}

    return {"status": ACQUIRED, "image": stored,
            "detail": f"acquired official image for code {code}",
            "source_url": full_url}
