"""Operating-contract regression tests for the dedicated LevNytt Commander.

These lock the critical invariants of the consolidated contract (SOUL.md v2.0):

1. Self-repair is data-driven and universal: any registered defect with a
   bounded repair capability and a project (LevNytt) scope is routed to repair,
   without the defect kind being pre-enumerated.
2. Cross-project (HERMES) repair scopes are never auto-repaired inside the
   LevNytt loop (fail closed).
3. Repair backoff prevents a deterministically-failing repair from being
   retried every cycle.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.commander.operational_defects import repair_due

from commander import decision


def _evidence():
    return {
        "runtime_capability_availability": {
            "content_improvement": {"executable_now": False},
            "content_production": {"executable_now": False},
        },
        "content_improvement_opportunities": {"opportunities": []},
        "seo_intelligence": {"opportunity_pool": {"exhausted": True}, "next_eligible_keywords": []},
        "staged_awaiting_deployment": [],
        "pending_deployment_verification": None,
        "distribution": {
            "execution_eligibility": {"executable_now": False},
            "distribution_candidates": [],
        },
        "measurement_freshness": {"fresh": True},
    }


def test_unknown_defect_kind_with_project_repair_scope_is_routed():
    # A future/unknown defect kind is actionable: routing is data-driven from
    # the defect's own capability_id + project repair scope, not a hard-coded
    # kind -> capability map.
    defects = [{
        "defect_id": "levnytt:future-defect:1",
        "kind": "some_future_defect_kind",
        "capability_id": "technical_repair",
        "repair": {"repository_kind": "PROJECT"},
        "description": "a new internal defect",
    }]
    d = decision.decide(_evidence(), defects, [])
    assert d["kind"] == "repair_defect"
    assert d["capability_id"] == "technical_repair"
    assert d["defect_id"] == "levnytt:future-defect:1"


def test_cross_project_repair_scope_is_not_auto_repaired():
    # HERMES-scoped repair would touch shared control code; it must never be
    # auto-repaired inside the LevNytt loop (fail closed).
    defects = [{
        "defect_id": "levnytt:shared:1",
        "kind": "some_future_defect_kind",
        "capability_id": "technical_repair",
        "repair": {"repository_kind": "HERMES"},
        "description": "shared control defect",
    }]
    d = decision.decide(_evidence(), defects, [])
    assert d["kind"] != "repair_defect"


def test_defect_without_repair_capability_is_not_repaired():
    defects = [{
        "defect_id": "levnytt:owner-boundary:1",
        "kind": "owner_boundary_kind",
        "capability_id": None,
        "description": "requires owner",
    }]
    d = decision.decide(_evidence(), defects, [])
    assert d["kind"] != "repair_defect"


def test_repair_backoff_prevents_immediate_retry():
    recent = {"status": "OPEN", "last_attempt_at": datetime.now(timezone.utc).isoformat()}
    old = {"status": "OPEN", "last_attempt_at": "2020-01-01T00:00:00+00:00"}
    fresh = {"status": "OPEN"}
    assert repair_due(recent, backoff_seconds=24 * 3600) is False
    assert repair_due(old, backoff_seconds=24 * 3600) is True
    assert repair_due(fresh, backoff_seconds=24 * 3600) is True
