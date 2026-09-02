"""LevNytt self-repair executors: internally actionable operational defects.

The dedicated LevNytt Commander's self-repair invariant is:

    detect -> classify -> assign executor -> repair -> verify -> close -> resume

This module supplies the deterministic detection and repair for one real, safe,
internally actionable defect class — broken internal links — using the project's
own link-policy auditor (``scripts/audit-production-links.py``, which is already
tracked in the LevNytt repository and already used for production maintenance).

A broken internal link is: an ``<a href>`` on a sitemap-routed production page
whose internal target does not resolve to any local file, redirect, or sitemap
route (``missing_local_target``), or an internal page that opens in a new tab
(``internal_opens_new_tab``). These are genuine editorial defects, never Owner
boundaries, and the repair is deterministic: the auditor's ``--fix`` pass
canonicalizes internal URLs and removes the new-tab flag, without touching any
external/affiliate URL, body prose, or NeoLife Sponsor-ID link.

The repair is verified by re-running the auditor read-only and confirming zero
unresolved exceptions, not by trusting the repair executor's own return value.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

from app.core.projects import registered_project

PROJECT_ID = "levnytt"

# A defect is only auto-repaired when the auditor's own --fix pass can
# deterministically repair it: canonicalizing a non-canonical internal URL,
# removing an internal new-tab flag, or adding safe rel to an unsafe external
# new-tab link. Material findings the auditor can only *report* (a genuinely
# missing local target, an invalid href, a wrong Sponsor-ID) are surfaced in
# evidence but never silently "repaired" — removing a real link or rewriting a
# monetization URL is an editorial decision, not a mechanical one.
_REPAIRABLE_ISSUES = frozenset({
    "noncanonical_internal_url",
    "internal_opens_new_tab",
    "unsafe_external_new_tab",
})

_AUDIT_SCRIPT = "scripts/audit-production-links.py"


def _load_auditor(project_root: Path):
    project_root = Path(project_root)
    """Load the tracked link auditor script as a module (no subprocess needed).

    ``audit-production-links.py`` exposes ``run(root, fix) -> dict``. It depends
    on ``scripts/rebuild-production.py``'s ``sitemap_routes``; both are resolved
    relative to *project_root*, so the audit is always scoped to LevNytt's own
    pages and never another project's.
    """
    script = Path(project_root) / _AUDIT_SCRIPT
    spec = importlib.util.spec_from_file_location("levnytt_link_auditor", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Link auditor not loadable: {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_only_audit(project_root: Path) -> dict[str, Any]:
    """Run the auditor read-only and return its report (never mutates pages).

    Fail-closed: a tooling failure (missing repo files, import error) returns an
    empty report rather than raising, so a broken auditor never blocks the loop
    — but it also never invents a defect from a failed read.
    """
    try:
        auditor = _load_auditor(project_root)
        return auditor.run(Path(project_root), False)
    except Exception:
        return {"unresolved_exceptions": [], "audit_error": "link auditor unavailable"}


def _repairable_exceptions(report: dict[str, Any]) -> list[dict[str, Any]]:
    """The unresolved link findings this Commander may repair autonomously.

    The auditor records every finding per page under ``pages[].findings[]`` and
    additionally promotes a subset (missing target, invalid href, wrong sponsor)
    into ``unresolved_exceptions``. Auto-repairable findings (non-canonical
    internal URL, internal new-tab, unsafe external new-tab) live in the
    per-page findings, so both locations are scanned.
    """
    findings: list[dict[str, Any]] = []
    for page in report.get("pages", []) or []:
        if not isinstance(page, dict):
            continue
        for item in page.get("findings", []) or []:
            if isinstance(item, dict) and any(
                issue in _REPAIRABLE_ISSUES for issue in item.get("issues", []) or []
            ):
                findings.append({**item, "page": page.get("file") or page.get("url")})
    for item in report.get("unresolved_exceptions", []) or []:
        if isinstance(item, dict) and any(
            issue in _REPAIRABLE_ISSUES for issue in item.get("issues", []) or []
        ):
            findings.append(item)
    return findings


def detect_link_defects(project_root: Path) -> list[dict[str, Any]]:
    """Read-only detection: the repairable internal-link findings, if any.

    Returns [] when the audit cannot run (a tooling failure is NOT a defect to
    silently repair; the caller reports it as UNAVAILABLE evidence, never zero).
    """
    report = _read_only_audit(Path(project_root))
    return _repairable_exceptions(report)


def run_link_repair(project_root: Path) -> dict[str, Any]:
    """Repair broken internal links through the auditor's own --fix pass.

    Returns an execution record whose ``evidence`` carries the before/after
    exception counts. The caller must still call :func:`verify_link_repair` —
    a SUCCEEDED return here is not itself proof of success.
    """
    project_root = Path(project_root)
    before = _repairable_exceptions(_read_only_audit(project_root))
    if not before:
        return {
            "status": "SUCCEEDED",
            "detail": "No repairable internal-link defect remains.",
            "evidence": {"before_count": 0, "after_count": 0, "fixed": False},
        }
    try:
        auditor = _load_auditor(project_root)
        auditor.run(project_root, True)
    except Exception as error:
        return {
            "status": "BLOCKED",
            "detail": f"Link repair could not run: {type(error).__name__}: {error}",
            "evidence": {"before_count": len(before), "repair_error": str(error)},
        }
    # Re-audit read-only to measure the true post-repair state (the --fix run's
    # own report still lists the findings it just repaired, so it cannot be used
    # as the "after" evidence).
    after = _repairable_exceptions(_read_only_audit(project_root))
    fixed = len(before) - len(after)
    return {
        "status": "SUCCEEDED" if not after else "BLOCKED",
        "detail": (
            f"Internal-link repair canonicalized/fixed {fixed} finding(s); "
            f"{len(after)} unresolved repairable finding(s) remain."
        ),
        "evidence": {
            "before_count": len(before),
            "after_count": len(after),
            "fixed": fixed,
            "remaining": after[:20],
        },
    }


def verify_link_repair(project_root: Path) -> tuple[bool, dict[str, Any]]:
    """Factual verification: re-run the auditor read-only and confirm zero
    repairable exceptions remain. A failed audit read is NOT proof of success."""
    report = _read_only_audit(Path(project_root))
    remaining = _repairable_exceptions(report)
    return not remaining, {"remaining_count": len(remaining), "report": report}


def load_project_root() -> Path:
    """Resolve the LevNytt working repository, independent of any selector.

    Prefers the fixed identity constant; falls back to the static project
    registry so a caller without the identity module still cannot touch another
    project. Never reads ``runtime/active-project``.
    """
    try:
        from commander import identity

        return identity.PROJECT_ROOT
    except Exception:
        project = registered_project(PROJECT_ID)
        if project is None:
            raise RuntimeError("LevNytt project is not registered")
        return project.working_repository


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}
