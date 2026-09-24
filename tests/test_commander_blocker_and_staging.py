"""Local staging and live-revision verification remain distinct in production state."""

import hashlib
import json
import subprocess
from datetime import datetime, timezone

from app.commander.commitment_ledger import commitment_records
from commander import interventions, operating_loop, procedure
from commander.identity import load_state
from conftest import production_gsc_snapshot


def test_staged_product_confirms_local_receipt_and_remains_deployable(tmp_path, monkeypatch):
    repo = tmp_path / "site"
    repo.mkdir()
    runtime = repo / "runtime"
    (runtime / "commander").mkdir(parents=True)
    (runtime / "intelligence").mkdir()
    (runtime / "commander" / "commitments.json").write_text('{"commitments": []}')
    (runtime / "intelligence" / "gsc-latest.json").write_text(json.dumps(production_gsc_snapshot(30)))
    source = repo / "neolife-flavonoid-complex.html"
    source.write_text("<h1>Historical generic topic</h1>")
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "add", source.name], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=Test", "-c",
                    "user.email=test@example.com", "commit", "-qm", "fixture"], check=True)

    import app.core.projects as projects
    monkeypatch.setattr(projects, "project_runtime_directory", lambda project_id: runtime)
    monkeypatch.setattr(operating_loop.evidence_module, "detect_defects", lambda *args: [])
    monkeypatch.setattr(operating_loop, "load_active_defects", lambda *args: [])
    packet = {"measurement_freshness": {"gsc_fresh": True, "fresh": True},
              "staged_awaiting_deployment": [], "runtime_capability_availability": {},
              "product_backlog": [{"code": "790", "product_name": "Flavonoid Complex",
                                   "slug": "neolife-flavonoid-complex", "coverage": "MENTIONED_ONLY"}],
              "seo_intelligence": {"opportunity_pool": {"exhausted": True}},
              "search_demand_scout": {"checked_at": datetime.now(timezone.utc).isoformat()},
              "community": {"community_intelligence": {"last_run_at": datetime.now(timezone.utc).isoformat()}}}
    monkeypatch.setattr(operating_loop.evidence_module, "build_evidence", lambda *args: dict(packet))

    def stage(selected, root, rt):
        assert selected["code"] == "790"
        source.write_text("<h1>NeoLife Flavonoid Complex</h1>")
        return {"status": "SUCCEEDED", "detail": "Staged product page", "evidence": {
            "external_effect_attempted": False, "code": "790", "slug": "neolife-flavonoid-complex",
            "source_file": source.name, "gate_passed": True,
            "staged_content_sha256": hashlib.sha256(source.read_bytes()).hexdigest()}}
    monkeypatch.setattr(operating_loop, "_execute_decision", stage)

    step = operating_loop._run_step(project_root=repo, runtime=runtime)
    assert step["verification"]["verified"] is True
    assert step["verification"]["verification_class"] == "STAGED_VERIFIED"
    assert step["verification"]["external_effect_verified"] is False
    persisted = load_state(runtime)["prior_decisions"][-1]
    assert persisted["verification_class"] == "STAGED_VERIFIED"
    assert persisted["external_effect_verified"] is False
    commitment = next(r for r in commitment_records(runtime) if r["commitment_id"] == "levnytt:product_page:790")
    assert commitment["kind"] == "staged_work" and commitment["status"] == "CONFIRMED"
    work = procedure._first_staged_work(repo)
    assert work["slug"] == "neolife-flavonoid-complex"
    assert work["staged_content_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert interventions._rows(runtime)[-1]["stage"] == "EXECUTED"

    selected = {"kind": "opportunity", "capability_id": "deployment",
                "opportunity_id": "deployment:neolife-flavonoid-complex"}
    deployed = {"status": "SUCCEEDED", "detail": "Pushed and checked the intended revision", "evidence": {
        "slug": work["slug"], "source_file": source.name, "files": [source.name],
        "source_sha256": work["staged_content_sha256"], "commit": "abc123",
        "deployed": True, "live_verified": True, "external_effect_attempted": True}}
    monkeypatch.setattr(procedure, "_verify_live_revision", lambda slug, expected, wait_seconds=0: False)
    mismatch = operating_loop._verify_outcome(selected, deployed, repo, runtime)
    assert mismatch["verified"] is False and mismatch["verification_class"] != "EXTERNAL_EFFECT_VERIFIED"
    assert interventions._rows(runtime)[-1]["stage"] == "EXECUTED"
    monkeypatch.setattr(procedure, "_verify_live_revision",
                        lambda slug, expected, wait_seconds=0: slug == work["slug"]
                        and expected == work["staged_content_sha256"])
    proven = operating_loop._verify_outcome(selected, deployed, repo, runtime)
    assert proven["verified"] is True
    assert proven["verification_class"] == "EXTERNAL_EFFECT_VERIFIED"
    interventions.record_result(runtime, selected, deployed, proven, {})
    assert interventions._rows(runtime)[-1]["stage"] == "MEASUREMENT_PENDING"


def test_staged_content_cannot_claim_external_effect_from_receipt_flag(tmp_path):
    repo = tmp_path / "site"
    source = repo / "content" / "articles" / "torr-hud.html"
    source.parent.mkdir(parents=True)
    source.write_text("<h1>Torr hud</h1>")
    selected = {"kind": "opportunity", "capability_id": "content_production",
                "opportunity_id": "content-gap:torr hud", "target": "torr hud"}
    for claimed in (False, True):
        result = operating_loop._verify_outcome(selected, {"status": "SUCCEEDED", "detail": "Staged",
            "evidence": {"slug": "torr-hud", "gate_passed": True,
                         "external_effect_attempted": claimed}}, repo, repo / "runtime")
        assert result["verified"] is True
        assert result["verification_class"] == "STAGED_VERIFIED"
        assert result["external_effect_verified"] is False


def test_verified_measurement_is_observation_not_external_mutation(tmp_path):
    runtime = tmp_path / "runtime"
    (runtime / "intelligence").mkdir(parents=True)
    fetched_at = datetime.now(timezone.utc).isoformat()
    (runtime / "intelligence" / "cta-events-latest.json").write_text(json.dumps({
        "status": "available", "fetched_at": fetched_at, "total_events": 5}))
    selected = {"kind": "opportunity", "capability_id": "measurement",
                "opportunity_id": "measurement:cta-refresh"}
    outcome = {"status": "PARTIAL", "detail": "CTA observed", "evidence": {"sources": {
        "gsc": {"status": "unavailable"}, "cta_d1": {"status": "available", "fetched_at": fetched_at}}}}
    result = operating_loop._verify_outcome(selected, outcome, tmp_path, runtime)
    assert result["verified"] is True
    assert result["verification_class"] == "OBSERVATION_VERIFIED"
    assert result["external_effect_verified"] is False
