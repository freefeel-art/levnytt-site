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

from pathlib import Path
from typing import Any

from app.commander.commitment_ledger import open_commitments
from app.commander.operational_defects import load_active_defects, register_defect

from commander import identity, repairs


def build_evidence(project_root: Path, runtime: Path, today: str) -> dict[str, Any]:
    """Assemble one facts-only decision packet from LevNytt evidence."""
    from app.commander.evidence import _levnytt

    packet = _levnytt(project_root, runtime, today, identity.PROJECT_ID)

    # Reconcile open durable state so the decision sees everything at once.
    packet["open_defects"] = load_active_defects(runtime)
    packet["open_commitments"] = open_commitments(runtime)

    # Provenance: the packet must be labelled with the project it belongs to.
    packet["project_id"] = identity.PROJECT_ID
    return packet


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
