"""Regression tests for bounded Commander recovery state."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from commander import decision
from commander import operating_loop


def test_failed_open_commitment_gets_bounded_retry_metadata(tmp_path):
    from app.commander.commitment_ledger import commitment_records

    runtime = tmp_path / "runtime"
    ledger = runtime / "commander" / "commitments.json"
    ledger.parent.mkdir(parents=True)
    ledger.write_text("""{"commitments": [{
        "commitment_id": "levnytt:content_improvement:content-improvement:blocked",
        "capability_id": "content_improvement", "status": "OPEN",
        "metadata": {}, "project_id": "levnytt"
    }]}""")
    operating_loop._record_commitment_retry(
        {"kind": "resume_commitment", "commitment_id": "levnytt:content_improvement:content-improvement:blocked"},
        runtime,
    )
    metadata = commitment_records(runtime)[0]["metadata"]
    assert metadata["retry_attempts"] == 1
    assert metadata["retry_after"] > datetime.now(timezone.utc).timestamp()


def test_retry_parked_open_commitment_does_not_block_independent_work():
    future = (datetime.now(timezone.utc) + timedelta(hours=12)).timestamp()
    evidence = {
        "product_catalog_discovery_due": False,
        "product_backlog": [{"code": "4242", "product_name": "Fixture", "slug": "fixture"}],
        "staged_awaiting_deployment": [],
        "pending_deployment_verification": None,
        "measurement_freshness": {"fresh": True},
    }
    commitments = [{
        "commitment_id": "levnytt:content_improvement:content-improvement:blocked",
        "capability_id": "content_improvement",
        "action": "retry later",
        "metadata": {"retry_after": future},
    }]
    selected = decision.decide(evidence, [], commitments, budget_check=lambda _capability: True)
    assert selected["capability_id"] == "product_page"


def test_unknown_capability_blocker_becomes_a_bounded_reprobe():
    observed = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    state = {"capability_blockers": {"unknown_capability": {
        "scope": "CAPABILITY",
        "status": "BLOCKED",
        "condition": {"type": "provider_specific_unknown"},
        "observed_at": observed,
    }}}
    active, cleared = operating_loop._active_capability_blockers(state)
    assert active == []
    assert cleared == ["unknown_capability"]
    assert state["capability_blockers"]["unknown_capability"]["status"] == "RECHECK_DUE"
    assert state["capability_blockers"]["unknown_capability"]["recheck_after"] > datetime.now(timezone.utc).timestamp()


def test_invalid_commitment_retry_metadata_is_not_a_permanent_lock():
    evidence = {
        "product_catalog_discovery_due": False,
        "product_backlog": [{"code": "4242", "product_name": "Fixture", "slug": "fixture"}],
        "staged_awaiting_deployment": [],
        "pending_deployment_verification": None,
        "measurement_freshness": {"fresh": True},
    }
    commitments = [{
        "commitment_id": "levnytt:content_improvement:content-improvement:broken-metadata",
        "capability_id": "content_improvement",
        "action": "retry",
        "metadata": {"retry_after": "not-a-timestamp"},
    }]
    selected = decision.decide(evidence, [], commitments, budget_check=lambda _capability: True)
    assert selected["kind"] == "resume_commitment"
