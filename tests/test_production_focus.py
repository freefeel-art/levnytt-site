"""Production-focus tests for the dedicated LevNytt Commander."""

from __future__ import annotations

from commander import decision


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
