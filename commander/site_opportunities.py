"""Bounded LevNytt adapter for owned informational-to-product routing gaps.

Hermes content_network reads OLSP Astro files and URLs. LevNytt's existing
canonical production-page and product-entity records are the source of truth
here; this adapter supplies only the site-specific graph edge and safe staging.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


def _clean(repo: Path, rel: str) -> bool:
    status = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--", rel],
                            capture_output=True, text=True, check=False)
    tracked = subprocess.run(["git", "-C", str(repo), "ls-files", "--error-unmatch", "--", rel],
                             capture_output=True, check=False)
    return status.returncode == 0 and not status.stdout.strip() and tracked.returncode == 0


def opportunities(repo: Path, packet: dict[str, Any]) -> list[dict[str, Any]]:
    from commander.product_coverage import DEDICATED_PAGE_EXISTS, compute_coverage

    data = repo / "content" / "data" / "production-pages.json"
    try:
        pages = json.loads(data.read_text(encoding="utf-8")).get("pages", [])
    except (OSError, ValueError):
        return []
    if not _clean(repo, "content/data/production-pages.json"):
        return []
    products = compute_coverage(repo)["products"]
    gsc_pages = {str(row.get("page", "")).rstrip("/"): row
                 for row in (packet.get("gsc_pages") or []) if isinstance(row, dict)}
    cta = packet.get("neolife_link_clicks") or {}
    clicks = {str(row.get("page_path", "")).rstrip("/")
              for row in cta.get("recent_events") or []} if cta.get("fresh") else set()
    found: list[dict[str, Any]] = []
    for page in pages:
        if not isinstance(page, dict) or page.get("family") != "informational-article":
            continue
        rel = str(page.get("source_file") or "")
        url_path = str(page.get("path") or "").rstrip("/")
        if not rel or not url_path or not (repo / rel).is_file() or not _clean(repo, rel):
            continue
        # Only a real observed or clicked owned page qualifies; no filler links.
        observed = gsc_pages.get("https://levnytt.se" + url_path, {})
        if not observed and url_path not in clicks:
            continue
        text = (repo / rel).read_text(encoding="utf-8", errors="replace")
        topic = str(page.get("title") or page.get("h1") or "").casefold() + " " + url_path.casefold()
        for product in products:
            if product["status"] != DEDICATED_PAGE_EXISTS:
                continue
            slug = str(product["slug"])
            target = f"/{slug}"
            if slug == url_path.lstrip("/") or not _clean(repo, f"{slug}.html"):
                continue
            # Shared distinctive-topic principle; omit generic marketing words.
            terms = {word for word in re.findall(r"[\wåäö]+", str(product["product_name"]).casefold())
                     if len(word) >= 5 and word not in {"neolife", "complex", "plus", "formula", "tablets"}}
            if not terms or not any(re.search(rf"\b{re.escape(term)}\b", topic) for term in terms):
                continue
            if re.search(rf'href=["\'](?:https://levnytt\.se)?{re.escape(target)}(?:[/?#][^"\']*)?["\']', text):
                continue
            found.append({"opportunity_id": f"internal-link:{url_path.lstrip('/')}:{slug}",
                          "source_file": rel, "source_path": url_path,
                          "target_slug": slug, "product_name": product["product_name"],
                          "evidence": {"gsc": observed, "cta_click_observed": url_path in clicks,
                                       "product_code": product["code"]}})
    found.sort(key=lambda row: (row["evidence"]["cta_click_observed"],
                                int(row["evidence"]["gsc"].get("clicks") or 0),
                                int(row["evidence"]["gsc"].get("impressions") or 0)), reverse=True)
    return found[:5]


def stage_link(repo: Path, action: dict[str, Any]) -> dict[str, Any]:
    target = action.get("target") or {}
    if not isinstance(target, dict) or action.get("opportunity_id") != target.get("opportunity_id"):
        return {"status": "BLOCKED", "detail": "Exact internal-link opportunity required.", "evidence": {}}
    rel = str(target.get("source_file") or "")
    slug = str(target.get("target_slug") or "")
    if not rel or not slug or not _clean(repo, rel):
        return {"status": "BLOCKED", "detail": "Source is not a clean published file.", "evidence": {}}
    if not _clean(repo, f"{slug}.html"):
        return {"status": "BLOCKED", "detail": "Product destination is not a published file.", "evidence": {}}
    from commander.procedure import _verify_live_ok
    if not _verify_live_ok(slug):
        return {"status": "BLOCKED", "detail": "Product destination was not verified live.", "evidence": {}}
    data_path = repo / "content" / "data" / "production-pages.json"
    if not _clean(repo, "content/data/production-pages.json"):
        return {"status": "BLOCKED", "detail": "Canonical page data has uncommitted changes.", "evidence": {}}
    source = repo / rel
    html = source.read_text(encoding="utf-8")
    if "</main>" not in html or f'href="/{slug}"' in html:
        return {"status": "BLOCKED", "detail": "Source has no safe insertion point or already links to target.", "evidence": {}}
    import html as html_lib
    label = html_lib.escape(str(target.get("product_name") or slug))
    section = (f'<aside class="levnytt-related-product"><p>Relaterad produkt: '
               f'<a href="/{slug}">{label}</a>. Läs produktfakta och jämför innan du bestämmer dig.'
               f'</p></aside>\n')
    rendered = html.replace("</main>", section + "</main>", 1)
    from commander.procedure import _atomic_text_write
    data = json.loads(data_path.read_text(encoding="utf-8"))
    page = next((p for p in data.get("pages", []) if p.get("path") == target.get("source_path")
                 and p.get("source_file") == rel), None)
    if not page or not isinstance(page.get("body_html"), str):
        return {"status": "BLOCKED", "detail": "Canonical source record is unavailable.", "evidence": {}}
    page["body_html"] += "\n" + section
    _atomic_text_write(source, rendered)
    _atomic_text_write(data_path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return {"status": "SUCCEEDED", "detail": f"Staged exact internal route {rel} -> /{slug}.",
            "evidence": {"slug": Path(rel).stem, "source_file": rel, "target_slug": slug,
                         "opportunity_id": action["opportunity_id"], "gate_passed": True,
                         "target_live_verified": True,
                         "staged_content_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                         "production_data_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest()}}


def verify_staged_link(repo: Path, evidence: dict[str, Any]) -> bool:
    rel = str(evidence.get("source_file") or "")
    path = repo / rel
    expected = evidence.get("staged_content_sha256")
    data_path = repo / "content" / "data" / "production-pages.json"
    return bool(rel and expected and path.is_file() and data_path.is_file() and evidence.get("gate_passed")
                and hashlib.sha256(path.read_bytes()).hexdigest() == expected
                and hashlib.sha256(data_path.read_bytes()).hexdigest() == evidence.get("production_data_sha256")
                and f'href="/{evidence.get("target_slug")}"' in path.read_text(encoding="utf-8"))
