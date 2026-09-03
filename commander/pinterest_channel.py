"""LevNytt Pinterest organic-acquisition channel (Commander-owned).

Deterministic opportunity generation, board/destination selection, image/
product/destination validation, UTM attribution, and a durable publication
ledger — everything that does NOT require Pinterest Standard Access. The single
network boundary is the actual ``POST /pins`` call, which the provider already
gates on Standard Access.

Pinterest is a distribution channel, never a destination: every Pin points at a
LevNytt-owned page, and every Pin must have a clear reason to exist with a
truthful, Swedish, fact-grounded title/description and the correct image.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SITE = "https://levnytt.se"
UTM = "utm_source=pinterest&utm_medium=social&utm_campaign=levnytt"

# board_id -> (name, pin class)
BOARDS: dict[str, tuple[str, str]] = {
    "1151232792187766770": ("NeoLife Kosttillskott", "product"),
    "1151232792187766803": ("Hållbar Städning", "product"),
    "1151232792187766813": ("NeoLife Historia", "informational"),
    "1151232792187766808": ("Vetenskap & Näring", "informational"),
    "1151232792187766810": ("Hälsosam Livsstil", "informational"),
    "1151232792188035184": ("LevNytt – Hälsa", "informational"),
}

_PRODUCT_BOARD_BY_CATEGORY = {
    "supplements": "1151232792187766770",
    "weight_management": "1151232792187766770",
    "home_care": "1151232792187766803",
    "personal_care": "1151232792187766803",
    "skin_care": "1151232792187766803",
    "accessories": "1151232792187766770",
}

_INFORMATIONAL_BOARD_KEYWORDS = [
    ("1151232792187766813", ("historia", "grundare", "historia", "neolife historia", "1958")),
    ("1151232792187766808", ("vetenskap", "forskning", "näring", "vetenskaplig", "studie", "evidens")),
    ("1151232792187766810", ("livsstil", "vardag", "sömn", "träning", "stress", "hälsosam")),
]
_DEFAULT_INFORMATIONAL_BOARD = "1151232792188035184"  # LevNytt – Hälsa


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def utm_url(url: str) -> str:
    """Append UTM attribution to a LevNytt destination URL."""
    url = url.strip()
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}{UTM}"


def board_for_product(category: str | None) -> str:
    return _PRODUCT_BOARD_BY_CATEGORY.get(category or "", "1151232792187766770")


def board_for_informational(text: str) -> str:
    lowered = (text or "").casefold()
    for board_id, keywords in _INFORMATIONAL_BOARD_KEYWORDS:
        if any(k in lowered for k in keywords):
            return board_id
    return _DEFAULT_INFORMATIONAL_BOARD


def ledger_path(runtime: Path) -> Path:
    return Path(runtime) / "pinterest" / "published.json"


def _load_ledger(runtime: Path) -> dict[str, Any]:
    path = ledger_path(runtime)
    if not path.is_file():
        return {"published": [], "attempts": []}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"published": [], "attempts": []}
    if not isinstance(value, dict):
        return {"published": [], "attempts": []}
    value.setdefault("published", [])
    value.setdefault("attempts", [])
    return value


def _save_ledger(runtime: Path, ledger: dict[str, Any]) -> None:
    path = ledger_path(runtime)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".published.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(ledger, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise


def pin_key(destination: str, image: str, title: str) -> str:
    return f"{destination}|{image}|{title.strip().casefold()}"


def _fit_title(title: str, limit: int = 100) -> str:
    """Truncate a Pin title to Pinterest's 100-character limit at a word boundary."""
    title = title.strip()
    if len(title) <= limit:
        return title
    cut = title[:limit].rstrip()
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" —–-,")


def already_published(runtime: Path, destination: str, image: str, title: str) -> bool:
    ledger = _load_ledger(runtime)
    key = pin_key(destination, image, title)
    return any(item.get("key") == key for item in ledger.get("published", []) if isinstance(item, dict))


def record_published(runtime: Path, *, key: str, pin_id: str, destination: str, image: str, title: str, board_id: str, pin_class: str) -> None:
    ledger = _load_ledger(runtime)
    ledger.setdefault("published", []).append({
        "key": key, "pin_id": pin_id, "destination": destination, "image": image,
        "title": title, "board_id": board_id, "pin_class": pin_class,
        "published_at": _now(),
    })
    _save_ledger(runtime, ledger)


def record_attempt(runtime: Path, *, key: str, destination: str, title: str, board_id: str, status: str, detail: str) -> None:
    ledger = _load_ledger(runtime)
    ledger.setdefault("attempts", []).append({
        "key": key, "destination": destination, "title": title, "board_id": board_id,
        "status": status, "detail": detail, "attempted_at": _now(),
    })
    ledger["attempts"] = ledger["attempts"][-50:]
    _save_ledger(runtime, ledger)


def product_pin_opportunities(project_root: Path) -> list[dict[str, Any]]:
    """PRODUCT_PIN opportunities: every current NeoLife product with a dedicated
    PRODUCT_PAGE and an exact product image."""
    from commander import product_coverage, product_page

    coverage = product_coverage.compute_coverage(project_root)
    entities = product_coverage.load_product_entities(project_root)
    opportunities: list[dict[str, Any]] = []
    for row in coverage["products"]:
        if row["status"] != product_coverage.DEDICATED_PAGE_EXISTS:
            continue
        entity = entities.get(str(row["code"]))
        if not entity:
            continue
        image = product_page.resolve_image(entity, project_root)
        if not image:
            continue
        title = f"NeoLife {str(entity.get('product_name'))} — {str(entity.get('short_description') or '')}".strip(" —")
        title = _fit_title(title)
        opportunities.append({
            "pin_class": "product",
            "code": str(entity.get("neoLife_code")),
            "product_name": str(entity.get("product_name") or ""),
            "slug": str(entity.get("slug") or ""),
            "category": entity.get("category"),
            "image": image,
            "destination": f"{SITE}/{str(entity.get('slug'))}",
            "title": title,
            "description": str(entity.get("short_description") or "")[:500],
            "board_id": board_for_product(entity.get("category")),
        })
    return opportunities


def informational_pin_opportunities(project_root: Path) -> list[dict[str, Any]]:
    """INFORMATIONAL_PIN opportunities: published informational articles with a
    usable hero/og image."""
    import re

    from bs4 import BeautifulSoup

    opportunities: list[dict[str, Any]] = []
    for path in sorted(project_root.glob("*.html")) + sorted((project_root / "content" / "articles").rglob("*.html")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        title_m = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
        title = re.sub(r"\s*\| LevNytt.*$", "", title_m.group(1).strip()) if title_m else path.stem
        desc_m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', text, re.I)
        description = desc_m.group(1).strip() if desc_m else title
        # exclude product pages and utility pages
        if path.name.startswith("neolife-") or path.name in {"index.html", "artiklar.html", "404.html", "om-oss.html", "integritetspolicy.html"}:
            continue
        soup = BeautifulSoup(text, "html.parser")
        img = soup.find("img", attrs={"class": re.compile(r"hero|og|feature")}) or soup.find("img", attrs={"src": re.compile(r"/images/")})
        image = img.get("src") if img else None
        if not image or image.startswith("/assets/brand/") or image.startswith("/assets/brand"):
            continue
        rel = path.relative_to(project_root)
        public_path = "/" + str(rel).replace("\\", "/")
        public_path = re.sub(r"/index\.html$", "", public_path)
        public_path = re.sub(r"\.html$", "", public_path)
        if public_path == "/content/articles":
            public_path = ""
        slug = public_path.strip("/")
        if not slug:
            continue
        opportunities.append({
            "pin_class": "informational",
            "slug": slug,
            "title": _fit_title(title),
            "description": description[:500],
            "image": image,
            "destination": f"{SITE}/{slug}",
            "board_id": board_for_informational(title + " " + description),
        })
    return opportunities


def validate_pin(opportunity: dict[str, Any], image_abs: Path) -> tuple[bool, str]:
    """Deterministic product/image/destination agreement check.

    A product Pin's image filename must contain the product code or the folded
    product name, so an image of one product can never be linked to another.
    """
    if not opportunity.get("destination", "").startswith(SITE):
        return False, "destination is not a levnytt.se URL"
    if not image_abs.is_file() or image_abs.stat().st_size == 0:
        return False, f"image missing or empty: {image_abs}"
    if opportunity["pin_class"] == "product":
        code = str(opportunity.get("code") or "")
        name = str(opportunity.get("product_name") or "").casefold().replace(" ", "").replace("-", "")
        image_name = image_abs.name.casefold().replace(" ", "").replace("-", "").replace(".jpg", "").replace(".jpeg", "").replace(".png", "")
        if code and code in image_abs.name:
            return True, ""
        if name and name in image_name:
            return True, ""
        return False, f"image {image_abs.name!r} does not match product {opportunity.get('product_name')!r} (code {code})"
    return True, ""


def verify_pin(result: dict[str, Any], package: dict[str, Any]) -> tuple[bool, str]:
    """Production verification once a Pin ID exists."""
    pin_id = result.get("id")
    if not pin_id:
        return False, "no Pin ID returned"
    if result.get("link") and package.get("destination") and result.get("link").split("?")[0] != package["destination"].split("?")[0]:
        return False, "Pin link does not match the intended destination"
    return True, f"Pin {pin_id} published"


def publish(runtime: Path, opportunity: dict[str, Any], project_root: Path) -> dict[str, Any]:
    """Attempt one real publication. Returns BLOCKED_BY_PINTEREST_STANDARD_ACCESS
    (or another truthful status) rather than fabricating success."""
    from app.providers.pinterest import PinterestError, PinterestProvider, build_publication_package

    image_rel = opportunity["image"]
    image_abs = (project_root / image_rel.lstrip("/")).resolve()
    ok, reason = validate_pin(opportunity, image_abs)
    if not ok:
        return {"status": "BLOCKED", "detail": reason, "evidence": {"opportunity": opportunity}}

    destination = utm_url(opportunity["destination"])
    key = pin_key(opportunity["destination"], image_rel, opportunity["title"])
    if already_published(runtime, opportunity["destination"], image_rel, opportunity["title"]):
        return {"status": "DUPLICATE", "detail": "already published", "evidence": {"key": key, "opportunity": opportunity}}

    try:
        package = build_publication_package(
            board_id=opportunity["board_id"],
            title=opportunity["title"],
            description=opportunity["description"],
            image_path=image_abs,
            destination_url=destination,
            source_article_url=opportunity["destination"],
            alt_text=opportunity["product_name"] if opportunity["pin_class"] == "product" else opportunity["title"],
        )
    except PinterestError as error:
        return {"status": "BLOCKED", "detail": f"package invalid: {error}", "evidence": {"opportunity": opportunity}}

    provider = PinterestProvider()
    try:
        result = provider.publish_package(package, approved=True)
    except PinterestError as error:
        detail = str(error)
        if "Trial access" in detail or "standard" in detail.lower():
            status = "BLOCKED_BY_PINTEREST_STANDARD_ACCESS"
        else:
            status = "BLOCKED"
        record_attempt(runtime, key=key, destination=opportunity["destination"], title=opportunity["title"], board_id=opportunity["board_id"], status=status, detail=detail)
        return {"status": status, "detail": detail, "evidence": {"opportunity": opportunity, "pin_class": opportunity["pin_class"]}}

    verified, vdetail = verify_pin(result, package.artifact())
    if verified:
        record_published(runtime, key=key, pin_id=result.get("id", ""), destination=opportunity["destination"], image=image_rel, title=opportunity["title"], board_id=opportunity["board_id"], pin_class=opportunity["pin_class"])
    return {
        "status": "PUBLISHED" if verified else "UNVERIFIED",
        "detail": vdetail,
        "evidence": {"result": result, "pin_class": opportunity["pin_class"], "destination": opportunity["destination"]},
    }
