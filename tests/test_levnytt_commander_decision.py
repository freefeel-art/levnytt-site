"""Decision-model tests for the dedicated LevNytt Commander.

The audited LevNytt objective is a NeoLife organic-acquisition asset. These
tests prove the decision model follows LevNytt's own hierarchy (defect repair >
commitment resumption > deploy staged > refresh stale measurement > improve an
existing page > produce for a verified gap > distribute > collect evidence >
truthful deferral), and that daily budgets gate NEW content work while defect
repair, deployment and resumption are never budgeted.
"""

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


def _state(today="2026-09-02") -> dict:
    return {"project_id": "levnytt", "prior_decisions": [], "latest_stop_reason": None,
            "daily_publication_budget": {"date": today, "used": 0, "limit": 1},
            "daily_optimization_budget": {"date": today, "used": 0, "limit": 3},
            "daily_measurement_budget": {"date": today, "used": 0, "limit": 1}}


def test_repairs_actionable_defect_first():
    defects = [{"kind": "broken_internal_link", "capability_id": "link_repair",
                "defect_id": "levnytt:link", "description": "broken link"}]
    d = decision.decide(_evidence(), defects, [])
    assert d["kind"] == "repair_defect"
    assert d["capability_id"] == "link_repair"


def test_resumes_open_commitment_before_opportunity():
    commitments = [{"commitment_id": "levnytt:content_production:x",
                    "capability_id": "content_production", "action": "make x"}]
    d = decision.decide(_evidence(), [], commitments)
    assert d["kind"] == "resume_commitment"


def test_deploys_staged_content_before_producing_more():
    ev = _evidence(staged_awaiting_deployment=["fibrer-tarmflora-prebiotisk"])
    d = decision.decide(ev, [], [])
    assert d["kind"] == "opportunity"
    assert d["capability_id"] == "deployment"


def test_refreshes_stale_measurement():
    ev = _evidence(measurement_freshness={"fresh": False})
    d = decision.decide(ev, [], [])
    assert d["capability_id"] == "measurement"


def test_improves_existing_page_over_new_content():
    ev = _evidence(runtime_capability_availability={
        "content_improvement": {"executable_now": True},
        "content_production": {"executable_now": True},
    }, content_improvement_opportunities={
        "opportunities": [{"opportunity_id": "content-improvement:finns-det-billigare-alternativ"}],
    })
    d = decision.decide(ev, [], [])
    assert d["capability_id"] == "content_improvement"
    assert d["opportunity_id"] == "content-improvement:finns-det-billigare-alternativ"


def test_publication_budget_gates_new_content():
    ev = _evidence(runtime_capability_availability={
        "content_improvement": {"executable_now": True},
        "content_production": {"executable_now": True},
    }, content_improvement_opportunities={"opportunities": [{"opportunity_id": "content-improvement:x"}]})
    state = _state()
    state["daily_optimization_budget"] = {"date": "2026-09-02", "used": 3, "limit": 3}
    budget = lambda c: decision.budget_available(state, "2026-09-02", c)
    # optimization budget exhausted -> content_improvement skipped; next is content_production
    d = decision.decide(ev, [], [], budget_check=budget)
    assert d["capability_id"] == "content_production"


def test_defect_repair_never_budgeted():
    defects = [{"kind": "broken_internal_link", "capability_id": "link_repair",
                "defect_id": "levnytt:link", "description": "broken link"}]
    state = _state()
    state["daily_publication_budget"] = {"date": "2026-09-02", "used": 99, "limit": 1}
    d = decision.decide(_evidence(), defects, [], budget_check=lambda c: decision.budget_available(state, "2026-09-02", c))
    assert d["kind"] == "repair_defect"


def test_no_fabricated_action_when_nothing_to_do():
    d = decision.decide(_evidence(), [], [])
    assert d["kind"] == "idle"
    assert d["capability_id"] is None


def test_budget_is_per_day():
    state = _state("2026-09-02")
    assert decision.budget_available(state, "2026-09-02", "content_production")
    decision.record_budget_use(state, "2026-09-02", "content_production")
    assert not decision.budget_available(state, "2026-09-02", "content_production")
    # A new day resets the budget.
    assert decision.budget_available(state, "2026-09-03", "content_production")
