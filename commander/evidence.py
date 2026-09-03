"""LevNytt facts-only evidence assembly for the dedicated Commander loop.

This module is the join, never the collection. It reuses the canonical LevNytt
evidence builder already shipped in the shared Hermes core
(``app.commander.evidence._levnytt``), which reads only LevNytt's own artifacts:

    * ``runtime/intelligence/gsc-latest.json`` (Search Console, first party)
    * ``runtime/intelligence/keywords.json`` (DataForSEO Swedish market)
    * ``content/data/production-pages.json`` (canonical production pages)
    * ``runtime/intelligence/gsc-index-coverage.json`` (URL Inspection API)
    * ``runtime/intelligence/cta-events-latest.json`` (D1 link-click events)
    * ``runtime/social/published.json`` (Facebook distribution ledger)

and reconciles it with the shared durable ledgers (open defects, open
commitments). It reads no OLSP or Cashbackkollen artifact, and it never invents
a fact: every field is read from a local artifact, and every absence is reported
as UNKNOWN/UNAVAILABLE rather than zero.
"""

from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from app.commander.commitment_ledger import ledger_path, open_commitments
from app.commander.operational_defects import load_active_defects, register_defect
from app.core.files import load_json_dict

from commander import identity, repairs

# A content_improvement is suppressed from re-selection for one GSC data window
# after it is confirmed, so the Commander does not re-improve a page using
# search evidence that predates the just-deployed revision.
_IMPROVEMENT_SUPPRESSION_DAYS = 28


def _recently_improved_slugs(runtime: Path) -> set[str]:
    """Slugs with a CONFIRMED content_improvement commitment resolved within the
    GSC data window. These must not be re-selected until fresh GSC evidence can
    actually reflect the deployed revision."""
    ledger = load_json_dict(ledger_path(runtime))
    rows = ledger.get("commitments")
    if not isinstance(rows, list):
        return set()
    cutoff = datetime.now(timezone.utc) - timedelta(days=_IMPROVEMENT_SUPPRESSION_DAYS)
    suppressed: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        if row.get("capability_id") != "content_improvement" or row.get("status") != "CONFIRMED":
            continue
        resolved_at = row.get("resolved_at")
        if isinstance(resolved_at, str):
            try:
                resolved = datetime.fromisoformat(resolved_at.replace("Z", "+00:00"))
            except ValueError:
                resolved = None
            if resolved is not None and resolved.tzinfo is None:
                resolved = resolved.replace(tzinfo=timezone.utc)
            if resolved is not None and resolved < cutoff:
                continue
        slug = None
        try:
            parsed = ast.literal_eval(str(row.get("resolution_reason") or ""))
            if isinstance(parsed, dict):
                slug = parsed.get("slug")
        except (ValueError, SyntaxError):
            slug = None
        if not slug:
            slug = str(row.get("commitment_id") or "").rsplit(":", 1)[-1]
        if slug:
            suppressed.add(str(slug))
    return suppressed


def _suppress_completed_improvements(packet: dict[str, Any], runtime: Path) -> dict[str, Any]:
    """Remove content_improvement opportunities for slugs that already have a
    recently-confirmed improvement, so the Commander moves on to fresh work
    instead of re-selecting a just-deployed page on stale GSC evidence."""
    suppressed = _recently_improved_slugs(runtime)
    opportunities = packet.get("content_improvement_opportunities")
    if not isinstance(opportunities, dict):
        return packet
    rows = opportunities.get("opportunities")
    if not isinstance(rows, list):
        return packet
    kept = [o for o in rows if isinstance(o, dict) and str(o.get("slug") or "") not in suppressed]
    if len(kept) == len(rows):
        return packet
    opportunities = dict(opportunities)
    opportunities["opportunities"] = kept
    opportunities["suppressed_recently_improved"] = sorted(suppressed)
    packet["content_improvement_opportunities"] = opportunities

    availability = packet.get("runtime_capability_availability")
    if isinstance(availability, dict):
        ci = availability.get("content_improvement")
        if isinstance(ci, dict):
            ci = dict(ci)
            ci["executable_now"] = bool(kept)
            if not kept:
                ci["blocking_reasons"] = ["ALL_RECENTLY_IMPROVED"]
            availability["content_improvement"] = ci
            packet["runtime_capability_availability"] = availability
    return packet


def build_evidence(project_root: Path, runtime: Path, today: str) -> dict[str, Any]:
    """Assemble one facts-only decision packet from LevNytt evidence."""
    from app.commander.evidence import _levnytt

    packet = _levnytt(project_root, runtime, today, identity.PROJECT_ID)
    packet = _suppress_completed_improvements(packet, runtime)

    # Persistent NeoLife product-coverage backlog. Every current product without
    # a dedicated PRODUCT_PAGE is eligible; search evidence only affects
    # ordering, never eligibility.
    packet["product_backlog"] = _product_backlog(project_root)

    # A staged product page must surface as awaiting deployment so the decision
    # model deploys it instead of staging the next product.
    packet["staged_awaiting_deployment"] = list(
        set(packet.get("staged_awaiting_deployment") or [])
        | set(_staged_product_pages(project_root, runtime))
    )

    # Reconcile open durable state so the decision sees everything at once.
    packet["open_defects"] = load_active_defects(runtime)
    packet["open_commitments"] = open_commitments(runtime)

    # Provenance: the packet must be labelled with the project it belongs to.
    packet["project_id"] = identity.PROJECT_ID
    return packet


def _staged_product_pages(project_root: Path, runtime: Path) -> list[str]:
    """Slugs of staged-but-not-yet-deployed product pages (CONFIRMED product_page
    commitments whose source file is still uncommitted)."""
    import subprocess

    ledger = load_json_dict(ledger_path(runtime))
    rows = ledger.get("commitments")
    if not isinstance(rows, list):
        return []
    completed = subprocess.run(
        ["git", "-C", str(project_root), "status", "--porcelain", "--untracked-files=all"],
        capture_output=True, text=True, check=False,
    )
    changed = {line[3:].strip() for line in completed.stdout.splitlines() if len(line) > 3}
    slugs: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if row.get("capability_id") != "product_page" or row.get("status") != "CONFIRMED":
            continue
        try:
            parsed = ast.literal_eval(str(row.get("resolution_reason") or ""))
        except (ValueError, SyntaxError):
            continue
        if not isinstance(parsed, dict) or not parsed.get("gate_passed"):
            continue
        source_file = str(parsed.get("source_file") or "")
        if source_file and source_file in changed:
            slugs.append(str(parsed.get("slug") or ""))
    return slugs


def _product_backlog(project_root: Path) -> list[dict[str, Any]]:
    from commander import product_coverage
    from commander import product_page

    coverage = product_coverage.compute_coverage(project_root)
    entities = product_coverage.load_product_entities(project_root)
    backlog: list[dict[str, Any]] = []
    for row in coverage["products"]:
        if row["status"] == product_coverage.DEDICATED_PAGE_EXISTS:
            continue
        entity = entities.get(str(row["code"]))
        if not entity:
            continue
        image = product_page.resolve_image(entity, project_root)
        backlog.append({
            "code": str(entity.get("neoLife_code")),
            "product_name": str(entity.get("product_name") or ""),
            "slug": str(entity.get("slug") or ""),
            "category": entity.get("category"),
            "coverage": row["status"],
            "image": image,
            "short_description": entity.get("short_description"),
            "summary": entity.get("summary"),
            "packaging": entity.get("packaging"),
            "usage": entity.get("usage"),
            "ingredients": entity.get("ingredients"),
        })
    # Supplements first (highest business value); then a mentioned-only topic
    # page (improve existing URL) before a no-content product (new page).
    def _rank(item: dict[str, Any]) -> tuple[int, int, int]:
        category = 0 if item.get("category") == "supplements" else 1
        coverage = 0 if item.get("coverage") == "MENTIONED_ONLY" else 1
        return (category, coverage, int(item.get("code") or 0))

    backlog.sort(key=_rank)
    return backlog


# ── defect detection ─────────────────────────────────────────────────────────


def detect_defects(project_root: Path, runtime: Path) -> list[dict[str, Any]]:
    """Detect internally actionable operational defects and persist them.

    A defect is durable (persisted in the LevNytt runtime) and, while open,
    machine-enforces that repair outranks ordinary production work. Detection is
    read-only; nothing here mutates a production page.
    """
    registered: list[dict[str, Any]] = []

    # 1. Broken internal links (missing_local_target, internal_opens_new_tab,
    #    shop link integrity). Repairable through the project's own link auditor.
    link_findings = repairs.detect_link_defects(project_root)
    if link_findings:
        registered.append(
            register_defect(
                runtime,
                defect_id="levnytt:link-defect:broken-internal-links",
                kind="broken_internal_link",
                capability_id="link_repair",
                description=(
                    f"{len(link_findings)} internal-link finding(s) require repair "
                    "(broken local target, internal new-tab, or Sponsor-ID link integrity)."
                ),
                repair={"repository_kind": "PROJECT", "verification_command": None},
                evidence={"findings": link_findings[:20], "count": len(link_findings)},
            )
        )
    else:
        from app.commander.operational_defects import close_defect

        close_defect(
            runtime,
            "levnytt:link-defect:broken-internal-links",
            reason="no repairable internal-link findings remain",
        )

    return registered
