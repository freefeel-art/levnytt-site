"""Production-focus tests for the dedicated LevNytt Commander.

Prove the two production-focus repairs:

1. Production (improve / produce / complete product pages / deploy / distribute)
   outranks measurement, so stale evidence never preempts publishable work.
2. NeoLife back-office accounting evidence is secondary: it is refreshed on a
   bounded cadence (cached otherwise) and never contributes to measurement
   success/failure, so it cannot dominate the loop or block production.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from commander import decision, procedure
from conftest import production_gsc_snapshot


def _evidence(**overrides) -> dict:
    base = {
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
    base.update(overrides)
    return base


def test_content_production_beats_stale_measurement():
    ev = _evidence(
        measurement_freshness={"fresh": False},
        runtime_capability_availability={
            "content_improvement": {"executable_now": False},
            "content_production": {"executable_now": True},
        },
        seo_intelligence={
            "opportunity_pool": {"exhausted": False},
            "next_eligible_keywords": ["fibrer"],
            "keywords": [{"keyword": "fibrer", "monthly_search_volume": 150}],
        },
    )
    d = decision.decide(ev, [], [])
    assert d["capability_id"] == "content_production"
    assert d["capability_id"] != "measurement"


def test_measurement_is_reachable_when_no_production():
    ev = _evidence(measurement_freshness={"fresh": False})
    d = decision.decide(ev, [], [])
    assert d["capability_id"] == "measurement"


def _ctx(tmp_path: Path) -> SimpleNamespace:
    repository = tmp_path / "site"
    runtime = tmp_path / "runtime"
    repository.mkdir()
    runtime.mkdir()
    return SimpleNamespace(working_repository=repository, runtime_directory=runtime)


def test_backoffice_collection_is_cached_when_fresh(tmp_path, monkeypatch):
    ctx = _ctx(tmp_path)
    intel = ctx.runtime_directory / "intelligence"
    intel.mkdir(parents=True)
    fresh = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    (intel / procedure.NEOLIFE_LATEST_FILENAME).write_text(
        json.dumps({"project_id": "levnytt", "status": "VERIFIED",
                    "collected_at": fresh, "datasets": {"orders": {"status": "VERIFIED"}}}),
        encoding="utf-8",
    )

    def fail_if_called(_ctx):
        raise AssertionError("back office must not be re-collected while fresh")

    monkeypatch.setattr(procedure, "_collect_neolife_backoffice", fail_if_called)
    result = procedure._collect_neolife_backoffice_if_due(ctx)
    assert result["cached"] is True
    assert result["status"] == "available"


def test_backoffice_is_recollected_when_stale(tmp_path, monkeypatch):
    ctx = _ctx(tmp_path)
    intel = ctx.runtime_directory / "intelligence"
    intel.mkdir(parents=True)
    stale = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    (intel / procedure.NEOLIFE_LATEST_FILENAME).write_text(
        json.dumps({"project_id": "levnytt", "status": "VERIFIED",
                    "collected_at": stale, "datasets": {}}),
        encoding="utf-8",
    )

    def recollect(_ctx):
        return {"status": "unavailable", "cached": False, "collected_at": None}

    monkeypatch.setattr(procedure, "_collect_neolife_backoffice", recollect)
    result = procedure._collect_neolife_backoffice_if_due(ctx)
    assert result.get("cached") is not True


def test_backoffice_does_not_gate_measurement_success(tmp_path, monkeypatch):
    ctx = _ctx(tmp_path)
    intel = ctx.runtime_directory / "intelligence"
    intel.mkdir(parents=True)
    fetched_at = datetime.now(timezone.utc).isoformat()
    (intel / "gsc-latest.json").write_text(
        json.dumps(production_gsc_snapshot(30, (datetime.now(timezone.utc) - timedelta(days=3)).isoformat())),
        encoding="utf-8",
    )

    def collect_gsc(*args, **kwargs):
        days = int(args[0][-1])
        (intel / "gsc-latest.json").write_text(
            json.dumps(production_gsc_snapshot(days, (datetime.now(timezone.utc) - timedelta(seconds=days)).isoformat())),
            encoding="utf-8",
        )
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(procedure.subprocess, "run", collect_gsc)
    monkeypatch.setattr(procedure, "_collect_cta_events", lambda _ctx: {
        "status": "available", "total_events": 3, "fetched_at": fetched_at,
    })
    # Back-office unavailable (e.g. missing credentials) must not degrade
    # otherwise-successful GSC + CTA measurement.
    monkeypatch.setattr(procedure, "_collect_neolife_backoffice_if_due", lambda _ctx: {
        "status": "unavailable", "cached": False, "collected_at": None,
    })

    execution = procedure.LevNyttProcedure()._execute_measurement(
        ctx, {"capability": "measurement", "summary": "refresh"}
    )
    assert execution["status"] == "SUCCEEDED"
    assert set(execution["evidence"]["sources"].keys()) == {"gsc", "cta_d1"}
    assert execution["evidence"]["neolife_backoffice"]["status"] == "unavailable"
