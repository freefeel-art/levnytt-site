"""Dedicated LevNytt Commander operating loop.

One bounded business cycle: load state -> collect factual evidence -> reconcile
open defects / commitments -> select an action -> execute -> verify -> persist
-> rebuild evidence and select again, until a truthful stop reason or the finite
action bound is reached.

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
from datetime import datetime, timezone
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
    update_commitment_metadata,
)
from app.commander.operational_defects import (
    close_defect,
    load_active_defects,
    record_repair_attempt,
    repair_due,
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
_STAGED_CONTENT_CAPABILITIES = frozenset({"content_improvement", "content_production", "legacy_migration", "product_page", "link_repair", "internal_linking"})
MAX_ACTIONS_PER_INVOCATION = 8

# A failing repair is retried at most once per this interval, so a deterministic
# internal failure cannot be re-attempted every cycle (anti-stall / §7 backoff).
REPAIR_BACKOFF_SECONDS = 24 * 3600
COMMITMENT_RETRY_BASE_SECONDS = 24 * 3600
COMMITMENT_RETRY_MAX_SECONDS = 7 * 24 * 3600
CAPABILITY_BLOCKER_RECHECK_SECONDS = 24 * 3600

TZ = ZoneInfo("Europe/Stockholm")


def _now() -> datetime:
    return datetime.now(TZ)


def _iso() -> str:
    return _now().isoformat()


def _commitment_id_for(decision: dict[str, Any]) -> str:
    commitment_id = str(decision.get("commitment_id") or "")
    if commitment_id:
        return commitment_id
    commitment = _commitment_for(decision)
    return str(commitment.get("commitment_id") or "") if commitment else ""


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


def _action_for(decision: dict[str, Any], runtime: Path | None = None) -> dict[str, Any]:
    kind = decision.get("kind")
    capability = decision.get("capability_id")
    if kind == "repair_defect":
        return {"capability": capability}
    if kind == "product_backlog":
        return {"capability": "product_page", "code": decision.get("code")}
    if kind == "resume_commitment":
        parts = str(decision.get("commitment_id") or "").split(":", 2)
        if len(parts) == 3 and parts[0] == identity.PROJECT_ID:
            prior = next((r for r in reversed(identity.load_state(runtime=runtime).get("prior_decisions", []))
                          if r.get("capability_id") == parts[1] and r.get("opportunity_id") == parts[2]), None) if runtime else None
            row = (next((r for r in open_commitments(runtime) if r.get("commitment_id") == decision.get("commitment_id")), {})
                   if runtime else {})
            metadata = row.get("metadata") or {}
            fallback = (parts[2].removeprefix("content-gap:") if parts[1] == "content_production"
                        and parts[2].startswith("content-gap:") else None)
            return {"capability": parts[1], "summary": parts[2],
                    "opportunity_id": parts[2],
                    "target": (prior.get("target") if prior else None) or metadata.get("target") or fallback,
                    "provenance": prior.get("provenance") if prior else metadata.get("provenance")}
        return {"capability": None}
    if kind == "opportunity":
        summary = decision.get("opportunity_id") or decision.get("reason", "")
        return {"capability": capability, "summary": summary, "target": decision.get("target"),
                "opportunity_id": decision.get("opportunity_id"), "provenance": decision.get("provenance")}
    return {"capability": None}


def _execute_decision(decision: dict[str, Any], project_root: Path, runtime: Path) -> dict[str, Any]:
    kind = decision.get("kind")
    capability = str(decision.get("capability_id") or "").strip().casefold()

    if kind == "repair_defect" and capability == "link_repair":
        return repairs.run_link_repair(project_root)

    procedure = LevNyttProcedure()
    ctx = _ctx(project_root, runtime)
    action = _action_for(decision, runtime)

    if kind == "idle":
        return {"status": "IDLE", "detail": decision.get("reason", ""), "evidence": {}}
    if action.get("capability") is None:
        return {
            "status": "DEFERRED",
            "detail": "commitment resumption could not be mapped to a capability",
            "evidence": {"commitment_id": decision.get("commitment_id")},
        }
    try:
        return procedure.execute(ctx, action)
    except Exception as error:
        return {"status": "BLOCKED", "failure_class": "RECOVERABLE_EXECUTOR_FAILURE",
                "detail": f"{capability} executor failed: {type(error).__name__}: {error}",
                "evidence": {"external_effect_attempted": False}}


def _verify_outcome(decision: dict[str, Any], outcome: dict[str, Any], project_root: Path, runtime: Path) -> dict[str, Any]:
    """Distinguish a verified local result from a verified external effect.

    SUCCEEDED is never trusted on its own. The effect is re-checked against the
    thing it claimed to change: a live page, a refreshed artifact, a permalink.
    """
    kind = decision.get("kind")
    capability = str(decision.get("capability_id") or "").strip().casefold()

    if kind == "repair_defect" and capability == "link_repair":
        verified, detail = repairs.verify_link_repair(project_root)
        verified = verified and outcome.get("status") == "SUCCEEDED"
        return {
            "verified": verified,
            "verification_class": "LINK_REPAIR_RECHECK" if verified else "UNVERIFIED",
            "detail": f"repairable internal-link findings remaining: {detail.get('remaining_count', 0)}",
        }

    if kind == "idle":
        return {"verified": False, "verification_class": "IDLE", "detail": outcome.get("detail", "")}

    if outcome.get("status") not in {"SUCCEEDED", "PARTIAL", "PUBLISHED"}:
        return {"verified": False, "verification_class": "EXTERNAL_EFFECT_UNVERIFIED",
                "detail": outcome.get("detail", "")}

    procedure = LevNyttProcedure()
    ctx = _ctx(project_root, runtime)
    action = _action_for(decision, runtime)
    if action.get("capability") is None:
        return {"verified": False, "verification_class": "UNVERIFIED", "detail": outcome.get("detail", "")}

    verified = procedure.verify(ctx, action, outcome)
    if capability == "measurement" and decision.get("opportunity_id") == "measurement:gsc-refresh":
        verified = verified and (outcome.get("evidence") or {}).get("sources", {}).get("gsc", {}).get("status") == "available"
    receipt = outcome.get("evidence") or {}
    if not verified:
        verification_class = "EXTERNAL_EFFECT_UNVERIFIED"
    elif (capability in {"deployment", "social_publishing", "pinterest"}
          and receipt.get("external_effect_attempted") is True):
        # procedure.verify checks the live revision / provider receipt for the
        # exact selected action; an executor assertion alone is never enough.
        verification_class = "EXTERNAL_EFFECT_VERIFIED"
    elif capability in _STAGED_CONTENT_CAPABILITIES and receipt.get("gate_passed"):
        verification_class = "STAGED_VERIFIED"
    elif capability in {"measurement", "seo_intelligence", "search_demand_scout", "community_intelligence", "legacy_audit"}:
        verification_class = "OBSERVATION_VERIFIED"
    else:
        verification_class = "EXECUTION_VERIFIED"
    return {
        "verified": verified,
        "verification_class": verification_class,
        "external_effect_verified": verification_class == "EXTERNAL_EFFECT_VERIFIED",
        "detail": outcome.get("detail", ""),
    }


def _record_capability_blocker(state: dict[str, Any], decision: dict[str, Any], outcome: dict[str, Any]) -> None:
    """Only an explicit capability-scoped executor receipt parks an entire lane."""
    blocker = (outcome.get("evidence") or {}).get("blocker")
    capability = str(decision.get("capability_id") or "")
    if (not str(outcome.get("status") or "").startswith("BLOCKED") or not capability
            or not isinstance(blocker, dict) or blocker.get("scope") != "CAPABILITY"
            or not blocker.get("blocker_id") or not isinstance(blocker.get("condition"), dict)):
        return
    state.setdefault("capability_blockers", {})[capability] = {
        "scope": "CAPABILITY", "blocker_id": blocker["blocker_id"],
        "condition": blocker["condition"], "status": outcome["status"],
        "opportunity_id": decision.get("opportunity_id"),
        "detail": str(outcome.get("detail") or "")[:300], "observed_at": _iso(),
    }


def _hydrate_capability_blockers(state: dict[str, Any]) -> None:
    """Recognise the already-recorded production Pinterest block on upgrade.

    The real operation before this repair persisted the provider status in its
    decision history but did not yet persist the capability scope. No production
    state is cleared or fabricated; the existing receipt supplies the evidence.
    """
    blockers = state.setdefault("capability_blockers", {})
    if "pinterest" in blockers:
        return
    for row in reversed(state.get("prior_decisions") or []):
        if row.get("capability_id") != "pinterest":
            continue
        execution = row.get("execution") or {}
        status = execution.get("status")
        if status == "PUBLISHED":
            break
        if status != "BLOCKED_BY_PINTEREST_STANDARD_ACCESS":
            continue
        from commander.pinterest_channel import standard_access_blocker
        detail = str(execution.get("detail") or "")
        blocker = standard_access_blocker(detail)
        blockers["pinterest"] = {
            **blocker, "status": status, "opportunity_id": row.get("opportunity_id"),
            "detail": detail[:300], "observed_at": row.get("selected_at"),
        }
        break


def _blocker_still_active(blocker: dict[str, Any]) -> bool:
    """Recheck the *recorded* external condition, never a different Pin."""
    condition = blocker.get("condition") or {}
    if condition.get("type") == "environment_required" and condition.get("name") == "PINTEREST_ACCESS_TIER":
        # Importing the existing provider loads the same dotenv configuration
        # used by its publication gate, without reading credentials or posting.
        from app.providers import pinterest as _pinterest  # noqa: F401
        import os
        return os.getenv("PINTEREST_ACCESS_TIER", "trial").strip().lower() != condition.get("value")
    if condition.get("type") == "retry_after_seconds":
        try:
            observed = datetime.fromisoformat(str(blocker["observed_at"]).replace("Z", "+00:00"))
            seconds = int(condition["seconds"])
            return seconds <= 0 or (datetime.now(timezone.utc) - observed).total_seconds() < seconds
        except (KeyError, TypeError, ValueError):
            return True  # invalid provenance is not evidence that access cleared
    return True  # unknown conditions fail closed


def _active_capability_blockers(state: dict[str, Any]) -> tuple[list[str], list[str]]:
    _hydrate_capability_blockers(state)
    blockers = state.get("capability_blockers") or {}
    cleared: list[str] = []
    active: list[str] = []
    for capability, blocker in blockers.items():
        if not isinstance(blocker, dict):
            # A malformed receipt is not safe to treat as cleared. Permit one
            # bounded executor re-probe after the recovery interval instead of
            # making corrupted state a permanent capability lock.
            blocker = {
                "status": "RECHECK_DUE", "condition": {}, "observed_at": None,
                "recheck_after": _now().timestamp() + CAPABILITY_BLOCKER_RECHECK_SECONDS,
            }
            blockers[capability] = blocker
            active.append(capability)
        elif blocker.get("status") == "CLEARED":
            continue
        elif blocker.get("status") == "RECHECK_DUE":
            if _blocker_recheck_due(blocker):
                blocker["recheck_after"] = (_now().timestamp() + CAPABILITY_BLOCKER_RECHECK_SECONDS)
                cleared.append(capability)
            else:
                active.append(capability)
        elif _blocker_still_active(blocker):
            if _unknown_blocker_recheck_due(blocker):
                blocker["status"] = "RECHECK_DUE"
                blocker["recheck_after"] = (_now().timestamp() + CAPABILITY_BLOCKER_RECHECK_SECONDS)
                cleared.append(capability)
            else:
                active.append(capability)
        else:
            blocker["status"] = "CLEARED"
            blocker["cleared_at"] = _iso()
            cleared.append(capability)
    return sorted(active), sorted(cleared)


def _blocker_recheck_due(blocker: dict[str, Any]) -> bool:
    try:
        return _now().timestamp() >= float(blocker.get("recheck_after"))
    except (TypeError, ValueError):
        return True


def _unknown_blocker_recheck_due(blocker: dict[str, Any]) -> bool:
    condition = blocker.get("condition") or {}
    if condition.get("type") in {"environment_required", "retry_after_seconds"}:
        return False
    try:
        observed = datetime.fromisoformat(str(blocker["observed_at"]).replace("Z", "+00:00"))
        if observed.tzinfo is None:
            observed = observed.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - observed).total_seconds() >= CAPABILITY_BLOCKER_RECHECK_SECONDS
    except (KeyError, TypeError, ValueError):
        return True


def _record_commitment_retry(decision: dict[str, Any], runtime: Path) -> None:
    commitment_id = _commitment_id_for(decision)
    if not commitment_id:
        return
    row = next((item for item in commitment_records(runtime)
                if item.get("commitment_id") == commitment_id and item.get("status") == "OPEN"), None)
    if not row:
        return
    metadata = dict(row.get("metadata") or {})
    try:
        attempts = int(metadata.get("retry_attempts", 0)) + 1
    except (TypeError, ValueError):
        attempts = 1
    delay = min(COMMITMENT_RETRY_MAX_SECONDS,
                COMMITMENT_RETRY_BASE_SECONDS * (2 ** min(attempts - 1, 3)))
    metadata.update({
        "retry_attempts": attempts,
        "retry_after": (_now().timestamp() + delay),
    })
    update_commitment_metadata(commitment_id=commitment_id, metadata=metadata, runtime=runtime)


def _clear_rechecked_capability_blocker(
    state: dict[str, Any], decision: dict[str, Any], verification: dict[str, Any],
) -> None:
    if not verification.get("verified"):
        return
    capability = str(decision.get("capability_id") or "")
    blocker = (state.get("capability_blockers") or {}).get(capability)
    if isinstance(blocker, dict) and blocker.get("status") == "RECHECK_DUE":
        blocker["status"] = "CLEARED"
        blocker["cleared_at"] = _iso()


def _escalate_if_non_retryable(decision: dict[str, Any], outcome: dict[str, Any], runtime: Path) -> None:
    """Anti-stall: escalate a determinately-blocked commitment instead of retrying.

    A commitment whose execution returned BLOCKED with ``failure_class``
    EVIDENCE_REQUIRED and ``retry_eligible_this_run`` False is a determinate
    absence of required evidence (for example an official product image that
    neither the local assets nor the autonomous acquisition path could supply).
    It can never self-resolve by retrying, so it is preserved as an
    OWNER_BOUNDARY terminal resolution carrying the blocker detail, and the loop
    proceeds to the next independent priority on the following cycle.

    Transient blocks (UNAVAILABLE, RECOVERABLE_*, or any retryable outcome) are
    deliberately left OPEN so a later cycle may retry them.
    """
    if outcome.get("status") != "BLOCKED":
        return
    if outcome.get("failure_class") != "EVIDENCE_REQUIRED":
        return
    if outcome.get("retry_eligible_this_run", True):
        return
    commitment_id = str(decision.get("commitment_id") or "")
    if not commitment_id:
        commitment = _commitment_for(decision)
        if commitment:
            commitment_id = str(commitment["commitment_id"])
    if not commitment_id:
        return
    record_commitment_resolution(
        commitment_id=commitment_id,
        resolution="OWNER_BOUNDARY",
        reason=str(outcome.get("detail") or "blocked")[:500],
        runtime=runtime,
    )


def _park_deployment_if_stalled(
    decision: dict[str, Any],
    outcome: dict[str, Any],
    state: dict[str, Any],
    project_root: Path,
) -> None:
    """Park a determinately-blocked deployment so it is not re-selected.

    A deterministic dirty-tree failure is recorded with its blocking paths and
    staged revision identity. The evidence builder excludes that revision until
    the deployment safety check actually clears. Unrelated accepted staged work
    cannot expire this park; it remains independently selectable.

    The staged-product commitment itself is never discarded;
    ``_escalate_if_non_retryable`` already resolved only the transient
    deployment-attempt commitment, leaving the confirmed staged-product
    commitment intact.
    """
    if decision.get("capability_id") != "deployment":
        return
    if outcome.get("status") != "BLOCKED":
        return
    if outcome.get("failure_class") != "EVIDENCE_REQUIRED":
        return
    if outcome.get("retry_eligible_this_run", True):
        return
    evidence = outcome.get("evidence") or {}
    slug = str(evidence.get("slug") or "")
    if not slug:
        return

    reasons = list(evidence.get("reasons") or [])

    parked = state.get("deployment_parked")
    if not isinstance(parked, dict):
        parked = {}
        state["deployment_parked"] = parked
    entry = parked.get(slug, {})
    count = int(entry.get("escalation_count", 0)) + 1

    parked[slug] = {
        "slug": slug,
        "staged_content_sha256": evidence.get("staged_content_sha256"),
        "source_file": evidence.get("source_file"),
        "blocker_paths": evidence.get("blocker_paths", []),
        "files": evidence.get("files", [evidence.get("source_file")]),
        "source_capability_id": evidence.get("source_capability_id", "product_page"),
        "reasons": reasons[:20],
        "parked_at": _iso(),
        "escalation_count": count,
    }


# ── persistence ─────────────────────────────────────────────────────────────


def _action_id(decision: dict[str, Any]) -> str:
    import hashlib

    seed = json.dumps(decision, sort_keys=True, default=str) + _iso()
    return hashlib.sha1(seed.encode()).hexdigest()[:10]


def _commitment_for(decision: dict[str, Any]) -> dict[str, Any] | None:
    """A durable commitment for work that may not finish in one step."""
    if decision.get("kind") == "product_backlog":
        code = decision.get("code") or "no-code"
        return {
            "commitment_id": f"{identity.PROJECT_ID}:product_page:{code}",
            "kind": "staged_work",
            "capability_id": "product_page",
            "executor_id": "product_page",
            "action": decision.get("reason", decision.get("kind", "")),
            "reason": decision.get("reason", ""),
            "metadata": {"target": decision.get("target"), "provenance": decision.get("provenance")},
        }
    if decision.get("kind") != "opportunity":
        return None
    opportunity_id = decision.get("opportunity_id") or "no-opportunity"
    return {
        "commitment_id": f"{identity.PROJECT_ID}:{decision.get('capability_id')}:{opportunity_id}",
        "kind": "staged_work" if decision.get("capability_id") in _STAGED_CONTENT_CAPABILITIES else "unverified_external_effect",
        "capability_id": decision.get("capability_id"),
        "executor_id": decision.get("capability_id"),
        "action": decision.get("reason", decision.get("kind", "")),
        "reason": decision.get("reason", ""),
        "metadata": {"target": decision.get("target"), "provenance": decision.get("provenance")},
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
    return verification.get("detail") or ("verified external effect"
            if verification.get("verification_class") == "EXTERNAL_EFFECT_VERIFIED" else "verified execution result")


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
        "opportunity_id": decision.get("opportunity_id"),
        "commitment_id": decision.get("commitment_id"),
        "target": decision.get("target"),
        "provenance": decision.get("provenance"),
        "execution": {
            "status": outcome.get("status"),
            "detail": str(outcome.get("detail", ""))[:500],
            "evidence": outcome.get("evidence"),
        },
        "verified": verification.get("verified"),
        "external_effect_verified": verification.get("verification_class") == "EXTERNAL_EFFECT_VERIFIED",
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


def _run_step(
    *,
    project_root: Path | None = None,
    runtime: Path | None = None,
    today: str | None = None,
    execute: bool = True,
    attempted: set[str] | None = None,
) -> dict[str, Any]:
    """Run one decision against newly assembled evidence."""
    identity.assert_identity()
    project_root = Path(project_root) if project_root is not None else identity.PROJECT_ROOT
    runtime = Path(runtime) if runtime is not None else identity.RUNTIME_DIR
    today = today or _today()

    state = identity.load_state(runtime=runtime)
    prior_blockers = json.dumps(state.get("capability_blockers") or {}, sort_keys=True, default=str)
    active_blockers, cleared_blockers = _active_capability_blockers(state)
    if execute and json.dumps(state.get("capability_blockers") or {}, sort_keys=True, default=str) != prior_blockers:
        identity.save_state(state, runtime=runtime)
    evidence = evidence_module.build_evidence(project_root, runtime, today)
    if execute:
        evidence_module.detect_defects(project_root, runtime)
        _reconcile_legacy_commitments(runtime)
        _reconcile_staged_commitments(runtime, project_root)
        # Re-read evidence now that reconciliation may have made staged work
        # recognisable as awaiting deployment.
        evidence = evidence_module.build_evidence(project_root, runtime, today)
    defects = [
        d for d in load_active_defects(runtime)
        if repair_due(d, backoff_seconds=REPAIR_BACKOFF_SECONDS)
    ]
    commitments = open_commitments(runtime)

    budget_check = lambda capability: decision_model.budget_available(state, today, capability)
    evidence["recent_decisions"] = state.get("prior_decisions", [])
    evidence["blocked_capabilities"] = active_blockers
    evidence["cleared_capability_blockers"] = cleared_blockers
    decision = decision_model.decide(evidence, defects, commitments, budget_check=budget_check,
                                     attempted=attempted)

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

    if not execute or decision.get("kind") == "idle":
        return summary

    # Record the bounded repair attempt so backoff (repair_due) prevents an
    # immediately-failing repair from being retried every cycle.
    if decision.get("kind") == "repair_defect":
        record_repair_attempt(runtime, str(decision.get("defect_id") or ""))

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
            metadata=commitment.get("metadata"),
        )

    outcome = _execute_decision(decision, project_root, runtime)
    verification = _verify_outcome(decision, outcome, project_root, runtime)

    # A failed action must not consume pacing capacity. Count a budget only
    # after an independently verified result, or after an external effect was
    # actually attempted and therefore must be paced despite uncertain receipt.
    if decision.get("kind") in {"opportunity", "product_backlog"}:
        receipt = outcome.get("evidence") or {}
        if verification.get("verified") or receipt.get("external_effect_attempted") is True:
            decision_model.record_budget_use(state, today, str(decision.get("capability_id") or ""))

    _record_capability_blocker(state, decision, outcome)
    _escalate_if_non_retryable(decision, outcome, runtime)
    _park_deployment_if_stalled(decision, outcome, state, project_root)
    _clear_rechecked_capability_blocker(state, decision, verification)

    if (commitment is not None or decision.get("kind") == "resume_commitment") and not verification.get("verified"):
        _record_commitment_retry(decision, runtime)

    if commitment is not None and verification.get("verified"):
        confirm_commitment(
            commitment_id=commitment["commitment_id"],
            evidence=_confirmation_evidence(decision, outcome, verification),
            runtime=runtime,
        )
    elif decision.get("kind") == "resume_commitment" and verification.get("verified"):
        # A resumed commitment has no new commitment record (``_commitment_for``
        # only covers product_backlog / opportunity). On a verified success the
        # pre-existing OPEN commitment must still reach CONFIRMED, otherwise it
        # lingers OPEN and is re-selected on the next cycle forever.
        confirm_commitment(
            commitment_id=decision.get("commitment_id"),
            evidence=_confirmation_evidence(decision, outcome, verification),
            runtime=runtime,
        )

    _persist(state, decision, outcome, verification, runtime)

    from commander import interventions
    interventions.record_result(runtime, decision, outcome, verification, evidence)
    if decision.get("capability_id") == "measurement" and (outcome.get("evidence") or {}).get("sources", {}).get("gsc", {}).get("status") == "available":
        interventions.follow_up(runtime, runtime / "intelligence" / "gsc-latest.json")

    summary.update({
        "outcome": outcome,
        "verification": verification,
        "executed": True,
    })
    return summary


def run_cycle(
    *, project_root: Path | None = None, runtime: Path | None = None,
    today: str | None = None, execute: bool = True,
) -> dict[str, Any]:
    """One finite objective loop: re-observe after every action, then decide again.

    A failed action may be skipped for this invocation; no safety or publication
    budget is reset between steps. Cron still owns the next independent visit.
    """
    identity.assert_identity()
    project_root = Path(project_root) if project_root is not None else identity.PROJECT_ROOT
    runtime = Path(runtime) if runtime is not None else identity.RUNTIME_DIR
    today = today or _today()
    if not execute:
        return _run_step(project_root=project_root, runtime=runtime, today=today, execute=False)

    attempted: set[str] = set()
    steps: list[dict[str, Any]] = []
    for _ in range(MAX_ACTIONS_PER_INVOCATION):
        result = _run_step(project_root=project_root, runtime=runtime, today=today,
                           attempted=attempted)
        if result["decision"]["kind"] == "idle":
            if result["evidence_summary"].get("gsc_fresh") is False and (
                result["content_budgets"]["measurement"]["used"] >= result["content_budgets"]["measurement"]["limit"]
            ):
                stop = "WAITING_FOR_MEASUREMENT"
            elif result["open_commitments"]:
                stop = "WAITING_FOR_COMMITMENT_RETRY_OR_EXTERNAL_EFFECT"
            elif identity.load_state(runtime=runtime).get("deployment_parked"):
                stop = "WAITING_FOR_BLOCKED_DEPLOYMENT"
            elif ((result["evidence_summary"].get("product_backlog_count", 0) > 0 and
                   result["content_budgets"]["publication"]["used"] >= result["content_budgets"]["publication"]["limit"]) or
                  (result["evidence_summary"].get("optimization_opportunity_count", 0) > 0 and
                   result["content_budgets"]["optimization"]["used"] >= result["content_budgets"]["optimization"]["limit"])):
                stop = "CAPACITY_EXHAUSTED"
            else:
                stop = "NO_JUSTIFIED_EXECUTABLE_WORK"
            state = identity.load_state(runtime=runtime)
            state["latest_stop_reason"] = stop
            identity.save_state(state, runtime=runtime)
            return {**result, "steps": steps, "action_count": len(steps),
                    "stop_reason": stop}
        attempted.add(decision_model.action_key(result["decision"]))
        commitment = _commitment_for(result["decision"])
        if commitment and not result.get("verification", {}).get("verified"):
            attempted.add(decision_model.action_key({"kind": "resume_commitment",
                "capability_id": commitment["capability_id"], "commitment_id": commitment["commitment_id"]}))
        steps.append(result)
    state = identity.load_state(runtime=runtime)
    state["latest_stop_reason"] = "BOUNDED_LOOP_SAFETY_LIMIT"
    identity.save_state(state, runtime=runtime)
    return {**steps[-1], "steps": steps, "action_count": len(steps),
            "stop_reason": "BOUNDED_LOOP_SAFETY_LIMIT"}


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
        "product_backlog_count": len(evidence.get("product_backlog") or []),
        "blocked_capabilities": evidence.get("blocked_capabilities") or [],
        "optimization_opportunity_count": (len((evidence.get("content_improvement_opportunities") or {}).get("opportunities") or [])
                                           + len(evidence.get("internal_link_opportunities") or [])),
    }
