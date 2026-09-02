"""Dedicated LevNytt Commander operating loop.

One bounded business cycle: load state -> collect factual evidence -> reconcile
open defects / commitments -> select one action -> execute -> verify -> persist
-> report the real business result.

This loop owns LevNytt and nothing else. It resolves its identity, runtime and
evidence from fixed construction (``commander.identity``), never from a mutable
active-project selector, and never accepts a project argument. Every read and
write is scoped to the LevNytt repository/runtime; a programming error cannot
redirect it into OLSP's or Cashbackkollen's runtime.

Production truth rule: executor return values are never sufficient evidence of
success. Each outcome is re-checked against the thing it claimed to change (a
live page, a refreshed artifact, a permalink) before it may be marked verified.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from zoneinfo import ZoneInfo

from app.commander.commitment_ledger import (
    commitment_records,
    confirm_commitment,
    ledger_path,
    open_commitments,
    record_commitment,
    record_commitment_resolution,
)
from app.commander.operational_defects import (
    close_defect,
    load_active_defects,
)
from app.core.files import atomic_json_write, load_json_dict

from commander import decision as decision_model
from commander import evidence as evidence_module
from commander import identity, repairs
from commander.procedure import LevNyttProcedure

# Capabilities that stage content for a later deployment step. Their confirmed
# receipts must carry the executor's structured evidence (file hashes) so the
# evidence layer and the deployment executor recognise them as awaiting
# deployment.
_STAGED_CONTENT_CAPABILITIES = frozenset({"content_improvement", "content_production", "legacy_migration"})

TZ = ZoneInfo("Europe/Stockholm")


def _now() -> datetime:
    return datetime.now(TZ)


def _iso() -> str:
    return _now().isoformat()


def _today() -> str:
    return _now().date().isoformat()


def _ctx(project_root: Path, runtime: Path) -> Any:
    return SimpleNamespace(working_repository=project_root, runtime_directory=runtime)


# Commitments recorded by the dedicated Commander use the id scheme
# ``levnytt:<capability>:<opportunity_id>``. The retired shared autonomous loop
# used ``levnytt:<capability>-<hash>``. Legacy-format OPEN commitments are
# historical artifacts of a loop that no longer runs; the dedicated Commander
# re-derives any genuinely-needed work from its own evidence model, so it marks
# those legacy OPEN commitments SUPERSEDED (a recorded terminal transition, not
# a deletion) once, idempotently, so a stale row can never block the loop.
_NEW_COMMITMENT_ID = re.compile(r"^levnytt:[a-z_]+:.+$")


def _reconcile_legacy_commitments(runtime: Path) -> None:
    for row in commitment_records(runtime):
        if row.get("status") != "OPEN":
            continue
        commitment_id = str(row.get("commitment_id") or "")
        if not commitment_id or _NEW_COMMITMENT_ID.match(commitment_id):
            continue
        record_commitment_resolution(
            commitment_id=commitment_id,
            resolution="SUPERSEDED",
            reason=(
                "retired shared autonomous loop commitment; re-derived by the "
                "dedicated LevNytt Commander evidence model"
            ),
            runtime=runtime,
        )


# ── execution + verification ─────────────────────────────────────────────────


def _action_for(decision: dict[str, Any]) -> dict[str, Any]:
    kind = decision.get("kind")
    capability = decision.get("capability_id")
    if kind == "repair_defect":
        return {"capability": capability}
    if kind == "resume_commitment":
        parts = str(decision.get("commitment_id") or "").split(":", 2)
        if len(parts) == 3 and parts[0] == identity.PROJECT_ID:
            return {"capability": parts[1], "summary": parts[2]}
        return {"capability": None}
    if kind == "opportunity":
        summary = decision.get("opportunity_id") or decision.get("reason", "")
        return {"capability": capability, "summary": summary}
    return {"capability": None}


def _execute_decision(decision: dict[str, Any], project_root: Path, runtime: Path) -> dict[str, Any]:
    kind = decision.get("kind")
    capability = str(decision.get("capability_id") or "").strip().casefold()

    if kind == "repair_defect" and capability == "link_repair":
        return repairs.run_link_repair(project_root)

    procedure = LevNyttProcedure()
    ctx = _ctx(project_root, runtime)
    action = _action_for(decision)

    if kind == "idle":
        return {"status": "IDLE", "detail": decision.get("reason", ""), "evidence": {}}
    if action.get("capability") is None:
        return {
            "status": "DEFERRED",
            "detail": "commitment resumption could not be mapped to a capability",
            "evidence": {"commitment_id": decision.get("commitment_id")},
        }
    return procedure.execute(ctx, action)


def _verify_outcome(decision: dict[str, Any], outcome: dict[str, Any], project_root: Path, runtime: Path) -> dict[str, Any]:
    """Turn an executor return into a verified / unverified production effect.

    SUCCEEDED is never trusted on its own. The effect is re-checked against the
    thing it claimed to change: a live page, a refreshed artifact, a permalink.
    """
    kind = decision.get("kind")
    capability = str(decision.get("capability_id") or "").strip().casefold()

    if kind == "repair_defect" and capability == "link_repair":
        verified, detail = repairs.verify_link_repair(project_root)
        return {
            "verified": verified,
            "verification_class": "LINK_REPAIR_RECHECK" if verified else "UNVERIFIED",
            "detail": f"repairable internal-link findings remaining: {detail.get('remaining_count', 0)}",
        }

    if kind == "idle":
        return {"verified": False, "verification_class": "IDLE", "detail": outcome.get("detail", "")}

    procedure = LevNyttProcedure()
    ctx = _ctx(project_root, runtime)
    action = _action_for(decision)
    if action.get("capability") is None:
        return {"verified": False, "verification_class": "UNVERIFIED", "detail": outcome.get("detail", "")}

    verified = procedure.verify(ctx, action, outcome)
    return {
        "verified": verified,
        "verification_class": "EXTERNAL_EFFECT_VERIFIED" if verified else "EXTERNAL_EFFECT_UNVERIFIED",
        "detail": outcome.get("detail", ""),
    }


# ── persistence ─────────────────────────────────────────────────────────────


def _action_id(decision: dict[str, Any]) -> str:
    import hashlib

    seed = json.dumps(decision, sort_keys=True, default=str) + _iso()
    return hashlib.sha1(seed.encode()).hexdigest()[:10]


def _commitment_for(decision: dict[str, Any]) -> dict[str, Any] | None:
    """A durable commitment for work that may not finish in one step."""
    if decision.get("kind") != "opportunity":
        return None
    opportunity_id = decision.get("opportunity_id") or "no-opportunity"
    return {
        "commitment_id": f"{identity.PROJECT_ID}:{decision.get('capability_id')}:{opportunity_id}",
        "kind": "unverified_external_effect",
        "capability_id": decision.get("capability_id"),
        "executor_id": decision.get("capability_id"),
        "action": decision.get("reason", decision.get("kind", "")),
        "reason": decision.get("reason", ""),
    }


def _confirmation_evidence(decision: dict[str, Any], outcome: dict[str, Any], verification: dict[str, Any]) -> str:
    """The durable receipt written into a confirmed commitment.

    Staged-content capabilities must persist the executor's structured evidence
    (the exact file hashes) so ``_staged_articles`` / ``_confirmed_staged_work``
    can later recognise the artifact as awaiting deployment. A plain detail
    string breaks that recognition (the defect this fixes). Other capabilities
    keep a plain, human-readable receipt.
    """
    capability = str(decision.get("capability_id") or "")
    evidence = outcome.get("evidence")
    if capability in _STAGED_CONTENT_CAPABILITIES and isinstance(evidence, dict) and evidence:
        return repr(evidence)
    return verification.get("detail", "verified external effect")


def _sha256(project_root: Path, rel: str) -> str | None:
    try:
        return hashlib.sha256((project_root / rel).read_bytes()).hexdigest()
    except OSError:
        return None


def _slug_from_commitment_row(row: dict[str, Any]) -> str:
    """Best-effort slug for a staged-content commitment: the last segment of its
    ``commitment_id`` (e.g. ``levnytt:content_improvement:content-improvement:x``
    -> ``x``)."""
    return str(row.get("commitment_id") or "").rsplit(":", 1)[-1]


def _reconcile_staged_commitments(runtime: Path, project_root: Path) -> int:
    """Repair confirmed staged-content commitments whose receipt is a plain
    string (from the historical defect) into a structured, hash-bound receipt.

    The structured evidence is recovered from the Commander's own persisted
    decision records, and only accepted when the staged files on disk still
    match those hashes — so a regenerated/stale variant is never repaired into
    a deployable receipt. Idempotent; returns the number of receipts repaired.
    """
    state = identity.load_state(runtime=runtime)
    evidence_by_slug: dict[str, dict[str, Any]] = {}
    for decision in state.get("prior_decisions", []):
        if decision.get("capability_id") not in _STAGED_CONTENT_CAPABILITIES:
            continue
        ev = (decision.get("execution") or {}).get("evidence")
        if not isinstance(ev, dict) or not ev.get("gate_passed"):
            continue
        slug = ev.get("slug")
        source_file = ev.get("source_file")
        if not slug or not source_file:
            continue
        # Only accept evidence whose artifact hashes match the files on disk.
        if _sha256(project_root, str(source_file)) != ev.get("staged_content_sha256"):
            continue
        if _sha256(project_root, "content/data/production-pages.json") != ev.get("production_data_sha256"):
            continue
        evidence_by_slug[str(slug)] = ev

    ledger = load_json_dict(ledger_path(runtime))
    rows = ledger.get("commitments")
    if not isinstance(rows, list):
        return 0
    repaired = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        if row.get("capability_id") not in _STAGED_CONTENT_CAPABILITIES:
            continue
        if row.get("status") != "CONFIRMED":
            continue
        reason = row.get("resolution_reason")
        try:
            parsed = ast.literal_eval(reason) if isinstance(reason, str) else None
        except (ValueError, SyntaxError):
            parsed = None
        if isinstance(parsed, dict) and parsed.get("gate_passed"):
            continue  # already structured
        slug = _slug_from_commitment_row(row)
        ev = evidence_by_slug.get(slug)
        if not ev:
            continue
        row["resolution_reason"] = repr(ev)
        repaired += 1
    if repaired:
        atomic_json_write(ledger_path(runtime), ledger)
    return repaired


def _persist(state, decision, outcome, verification, runtime) -> None:
    decision_record = {
        "selected_at": _iso(),
        "project_id": identity.PROJECT_ID,
        "action_id": _action_id(decision),
        "capability_id": decision.get("capability_id"),
        "decision": decision.get("kind"),
        "action": decision.get("reason") or decision.get("kind"),
        "reason": decision.get("reason"),
        "execution": {
            "status": outcome.get("status"),
            "detail": str(outcome.get("detail", ""))[:500],
            "evidence": outcome.get("evidence"),
        },
        "verified": verification.get("verified"),
        "verification_class": verification.get("verification_class"),
        "measurement": {},
    }
    state.setdefault("prior_decisions", []).append(decision_record)
    state["prior_decisions"] = state["prior_decisions"][-50:]
    state["latest_stop_reason"] = decision.get("kind")

    if decision.get("kind") == "repair_defect" and verification.get("verified"):
        close_defect(runtime, decision.get("defect_id"), reason=verification.get("detail", "verified repaired"))

    identity.save_state(state, runtime=runtime)


# ── cycle ───────────────────────────────────────────────────────────────────


def run_cycle(
    *,
    project_root: Path | None = None,
    runtime: Path | None = None,
    today: str | None = None,
    execute: bool = True,
) -> dict[str, Any]:
    """Run one bounded LevNytt Commander cycle."""
    identity.assert_identity()
    project_root = Path(project_root) if project_root is not None else identity.PROJECT_ROOT
    runtime = Path(runtime) if runtime is not None else identity.RUNTIME_DIR
    today = today or _today()

    state = identity.load_state(runtime=runtime)
    evidence = evidence_module.build_evidence(project_root, runtime, today)
    evidence_module.detect_defects(project_root, runtime)
    _reconcile_legacy_commitments(runtime)
    _reconcile_staged_commitments(runtime, project_root)
    # Re-read evidence now that the reconciliation may have made staged content
    # recognisable as awaiting deployment.
    evidence = evidence_module.build_evidence(project_root, runtime, today)
    defects = load_active_defects(runtime)
    commitments = open_commitments(runtime)

    budget_check = lambda capability: decision_model.budget_available(state, today, capability)
    decision = decision_model.decide(evidence, defects, commitments, budget_check=budget_check)

    summary = {
        "project_id": identity.PROJECT_ID,
        "today": today,
        "decision": decision,
        "evidence_summary": _evidence_summary(evidence),
        "open_defects": len(defects),
        "open_commitments": len(commitments),
        "content_budgets": decision_model.budgets_summary(state, today),
        "executed": False,
    }

    if not execute:
        return summary

    # A NEW budgeted action (publication/optimization/measurement) consumes its
    # budget at the moment it is decided, so more cycles cannot become more
    # publishing. Defect repair, deployment, resumption and verification never
    # consume a content budget.
    if decision.get("kind") == "opportunity":
        decision_model.record_budget_use(state, today, str(decision.get("capability_id") or ""))

    commitment = _commitment_for(decision)
    if commitment is not None:
        record_commitment(
            runtime=runtime,
            project_id=identity.PROJECT_ID,
            commitment_id=commitment["commitment_id"],
            kind=commitment["kind"],
            capability_id=commitment["capability_id"],
            executor_id=commitment["executor_id"],
            action=commitment["action"],
            reason=commitment["reason"],
        )

    outcome = _execute_decision(decision, project_root, runtime)
    verification = _verify_outcome(decision, outcome, project_root, runtime)

    if commitment is not None and verification.get("verified"):
        confirm_commitment(
            commitment_id=commitment["commitment_id"],
            evidence=_confirmation_evidence(decision, outcome, verification),
            runtime=runtime,
        )

    _persist(state, decision, outcome, verification, runtime)

    summary.update({
        "outcome": outcome,
        "verification": verification,
        "executed": True,
    })
    return summary


def _evidence_summary(evidence: dict[str, Any]) -> dict[str, Any]:
    freshness = evidence.get("measurement_freshness") or {}
    availability = evidence.get("runtime_capability_availability") or {}
    work = evidence.get("work_availability") or {}
    return {
        "gsc_fresh": freshness.get("gsc_fresh"),
        "cta_fresh": freshness.get("cta_fresh"),
        "monetization": (evidence.get("neolife_monetization") or {}).get("sponsor_wired"),
        "attribution_instrumented": (evidence.get("attribution_state") or {}).get(
            "neolife_link_click_instrumented"
        ),
        "staged_awaiting_deployment": evidence.get("staged_awaiting_deployment"),
        "content_improvement_executable": bool(
            (availability.get("content_improvement") or {}).get("executable_now")
        ),
        "content_production_executable": bool(
            (availability.get("content_production") or {}).get("executable_now")
        ),
        "no_autonomous_production_action": work.get("no_autonomous_production_action"),
        "search_index_coverage": evidence.get("search_index_coverage"),
    }
