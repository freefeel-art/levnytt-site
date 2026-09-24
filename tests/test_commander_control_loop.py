"""Production-schema and state-transition regressions for LevNytt control."""

import hashlib
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from conftest import production_gsc_snapshot
from commander import decision, evidence, gsc_control, interventions, procedure
from commander.identity import save_state
from commander.operating_loop import _park_deployment_if_stalled, _verify_outcome


def _dated(days: int, ago: int = 0) -> dict:
    return production_gsc_snapshot(days, (datetime.now(timezone.utc) - timedelta(days=ago)).isoformat())


def _snapshots(ago: int = 0) -> dict:
    return {days: _dated(days, ago) for days in gsc_control.WINDOWS}


def _observed(ago: int = 0) -> dict:
    snapshots = _snapshots(ago)
    result = snapshots[30]
    result["trends"] = gsc_control.build_trends(snapshots)
    return result


def _packet(gsc: dict) -> dict:
    return {"measurement_freshness": {"gsc_fresh": gsc_control.fresh(gsc), "fresh": gsc_control.fresh(gsc)},
            "gsc_trends": gsc.get("trends"), "staged_awaiting_deployment": ["staged"],
            "product_backlog": [{"code": "789", "product_name": "Beta Guard", "slug": "neolife-betaguard"}]}


def test_stale_gsc_precedes_deployment_and_product_but_fresh_does_not():
    old = _observed(ago=10)
    assert not gsc_control.fresh(old)
    assert decision.decide(_packet(old), [], [])["capability_id"] == "measurement"
    assert decision.decide(_packet(old), [], [{"capability_id": "deployment", "commitment_id": "levnytt:deployment:old"}])["capability_id"] == "measurement"
    assert decision.decide(_packet(old), [], [], budget_check=lambda _: False)["capability_id"] == "deployment"
    current = _observed()
    assert gsc_control.fresh(current)
    assert decision.decide(_packet(current), [], [])["capability_id"] == "deployment"


def test_real_query_page_trends_reach_decision():
    snapshots = _snapshots()
    assert snapshots[7]["page"]["all_pages"] and snapshots[7]["query"]["all_queries"]
    page = next(r for r in snapshots[7]["page"]["all_pages"] if r["page"].endswith("/cellmembran-funktion"))
    page["impressions"] += 40
    next(r for r in snapshots[14]["page"]["all_pages"] if r["page"].endswith("/cellmembran-funktion"))["impressions"] = 500
    trends = gsc_control.build_trends(snapshots)
    snapshots[30]["trends"] = trends
    assert set(trends["windows"]) == {"7", "14", "30"}
    assert trends["windows"]["7"]["query"]["current"]["rows"][0]["query"]
    assert trends["windows"]["14"]["page"]["newly_observed"]
    assert page["ctr"] == 0 and "position" in page
    packet = _packet(snapshots[30])
    packet.update(gsc_trends=trends, staged_awaiting_deployment=[], product_backlog=[],
                  runtime_capability_availability={"content_improvement": {"executable_now": True}},
                  content_improvement_opportunities={"opportunities": [
                      {"slug": "direktforsaljning-fakta", "opportunity_id": "content-improvement:direktforsaljning-fakta"},
                      {"slug": "cellmembran-funktion", "opportunity_id": "content-improvement:cellmembran-funktion"}]})
    # Both have positive demand, but the packet makes each current/prior period
    # available; selected action carries actual trend values, not a guessed total.
    selected = decision.decide(packet, [], [])
    assert selected["capability_id"] == "content_improvement"
    assert "preceding 7d" in selected["reason"]


def test_comparable_seven_fourteen_thirty_day_periods_keep_both_dimensions():
    snapshots = _snapshots()
    for dimension, key in (("query", "all_queries"), ("page", "all_pages")):
        for days, impressions, clicks in ((7, 80, 4), (14, 115, 5),
                                           (28, 175, 7), (30, 190, 8), (60, 280, 10)):
            row = snapshots[days][dimension][key][0]
            row.update(impressions=impressions, clicks=clicks,
                       ctr=round(100 * clicks / impressions, 2), position=11.5)
    trends = gsc_control.build_trends(snapshots)
    for days, current, previous in ((7, 80, 35), (14, 115, 60), (30, 190, 90)):
        for dimension in ("query", "page"):
            period = trends["windows"][str(days)][dimension]
            row = period["current"]["rows"][0]
            assert row["impressions"] == current and "clicks" in row and "ctr" in row and "position" in row
            assert period["previous"]["rows"][0]["impressions"] == previous
            assert period["impressions_change"] == period["current"]["summary"]["impressions"] - period["previous"]["summary"]["impressions"]


def test_evidence_builder_preserves_production_trends_and_detects_staleness(tmp_path, monkeypatch):
    import app.commander.evidence as shared
    from commander import evidence as local
    intel = tmp_path / "intelligence"
    intel.mkdir()
    (tmp_path / "commander").mkdir()
    (tmp_path / "commander" / "commitments.json").write_text('{"commitments": []}')
    snapshot = _observed()
    (intel / "gsc-latest.json").write_text(json.dumps(snapshot))
    monkeypatch.setattr(shared, "_levnytt", lambda *a: {"measurement_freshness": {"cta_fresh": True},
        "runtime_capability_availability": {}, "staged_awaiting_deployment": []})
    monkeypatch.setattr(local, "_product_backlog", lambda *a: [])
    monkeypatch.setattr(local, "_pinterest_opportunities", lambda *a: [])
    monkeypatch.setattr(local, "_staged_product_pages", lambda *a: [])
    monkeypatch.setattr(local, "load_active_defects", lambda *a: [])
    monkeypatch.setattr(local, "open_commitments", lambda *a: [])
    packet = local.build_evidence(tmp_path, tmp_path, datetime.now().date().isoformat())
    assert packet["measurement_freshness"]["gsc_fresh"] is True
    assert packet["gsc_trends"]["windows"]["14"]["query"]["current"]["rows"]
    snapshot["fetched_at"] = (datetime.now(timezone.utc) - timedelta(days=9)).isoformat()
    (intel / "gsc-latest.json").write_text(json.dumps(snapshot))
    assert local.build_evidence(tmp_path, tmp_path, datetime.now().date().isoformat())["measurement_freshness"]["gsc_fresh"] is False


def test_failed_refresh_preserves_prior_artifact_and_never_creates_freshness(tmp_path, monkeypatch):
    repo, runtime = tmp_path / "site", tmp_path / "runtime"
    repo.mkdir()
    (runtime / "intelligence").mkdir(parents=True)
    path = runtime / "intelligence" / "gsc-latest.json"
    previous = _observed(ago=15)
    path.write_text(json.dumps(previous))
    calls = []

    def collect(args, **kwargs):
        days = int(args[-1])
        calls.append(days)
        path.write_text(json.dumps(_dated(days)))
        return SimpleNamespace(returncode=1 if days == 14 else 0, stdout="", stderr="provider unavailable")

    monkeypatch.setattr(procedure.subprocess, "run", collect)
    monkeypatch.setattr(procedure, "_collect_cta_events", lambda _: {"status": "unavailable"})
    monkeypatch.setattr(procedure, "_collect_neolife_backoffice_if_due", lambda _: {"status": "unavailable"})
    result = procedure.LevNyttProcedure()._execute_measurement(SimpleNamespace(working_repository=repo, runtime_directory=runtime), {})
    assert calls == [7, 14]
    assert result["evidence"]["sources"]["gsc"]["status"] == "unavailable"
    assert json.loads(path.read_text()) == previous
    assert not gsc_control.fresh(json.loads(path.read_text()))


def _parked_repo(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
    (repo / ".git" / "info" / "exclude").write_text("runtime/\n")
    (repo / "ROADMAP.md").write_text("clean")
    (repo / "unrelated.md").write_text("clean")
    subprocess.run(["git", "-C", str(repo), "add", "ROADMAP.md", "unrelated.md"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
    (repo / "ROADMAP.md").write_text("blocking edit")
    page = repo / "product.html"
    page.write_text("accepted revision")
    sha = hashlib.sha256(page.read_bytes()).hexdigest()
    ledger = repo / "runtime" / "commander" / "commitments.json"
    ledger.parent.mkdir(parents=True)
    ledger.write_text(json.dumps({"commitments": [{"capability_id": "product_page", "status": "CONFIRMED",
        "resolution_reason": repr({"slug": "product", "source_file": "product.html", "gate_passed": True,
                                   "staged_content_sha256": sha})}]}))
    state = {}
    _park_deployment_if_stalled({"capability_id": "deployment"},
        {"status": "BLOCKED", "failure_class": "EVIDENCE_REQUIRED", "retry_eligible_this_run": False,
         "evidence": {"slug": "product", "source_file": "product.html", "staged_content_sha256": sha,
                      "blocker_paths": ["ROADMAP.md"], "reasons": ["dirty ROADMAP.md"]}}, state, repo)
    save_state(state, runtime=repo / "runtime")
    return repo


def test_park_only_reconsiders_when_deployment_blockers_clear(tmp_path):
    repo = _parked_repo(tmp_path)
    runtime = repo / "runtime"
    assert evidence._filter_parked_deployments(["product"], repo, runtime) == []
    (repo / "unrelated.md").write_text("unrelated change")
    assert evidence._filter_parked_deployments(["product"], repo, runtime) == []
    # A separate, legitimately staged page is independently selectable; its
    # presence is not evidence that ROADMAP.md was fixed.
    second = repo / "new-product.html"
    second.write_text("accepted second revision")
    sha = hashlib.sha256(second.read_bytes()).hexdigest()
    ledger_path = runtime / "commander" / "commitments.json"
    ledger = json.loads(ledger_path.read_text())
    ledger["commitments"].append({"capability_id": "product_page", "status": "CONFIRMED",
        "resolution_reason": repr({"slug": "new-product", "source_file": second.name,
                                   "gate_passed": True, "staged_content_sha256": sha})})
    ledger_path.write_text(json.dumps(ledger))
    assert evidence._filter_parked_deployments(["product", "new-product"], repo, runtime) == ["new-product"]
    outcome = procedure.LevNyttProcedure()._execute_deployment(
        SimpleNamespace(working_repository=repo, runtime_directory=runtime),
        {"capability": "deployment", "summary": "deployment:new-product"})
    assert outcome["status"] == "BLOCKED" and outcome["evidence"]["slug"] == "new-product"
    assert outcome["evidence"]["external_effect_attempted"] is False
    other = {"measurement_freshness": {"gsc_fresh": True}, "staged_awaiting_deployment": [],
             "product_backlog": [{"code": "789", "product_name": "Beta", "slug": "beta"}]}
    assert decision.decide(other, [], [])["capability_id"] == "product_page"
    subprocess.run(["git", "-C", str(repo), "restore", "ROADMAP.md", "unrelated.md"], check=True)
    assert evidence._filter_parked_deployments(["product"], repo, runtime) == ["product"]


def test_existing_http_200_cannot_verify_blocked_deployment(tmp_path, monkeypatch):
    monkeypatch.setattr(procedure, "_verify_live", lambda *a, **kw: True)
    monkeypatch.setattr(procedure, "_verify_live_revision", lambda *a, **kw: True)
    blocked = {"status": "BLOCKED", "evidence": {"slug": "existing", "external_effect_attempted": False}}
    assert not _verify_outcome({"kind": "opportunity", "capability_id": "deployment"}, blocked, tmp_path, tmp_path)["verified"]


def test_live_revision_must_match_intended_bytes(monkeypatch):
    class OldPage:
        status = 200
        def __enter__(self):
            return self
        def __exit__(self, *_):
            pass
        def read(self):
            return b"old page at the same URL"
    monkeypatch.setattr(procedure.urllib.request, "urlopen", lambda *a, **kw: OldPage())
    assert not procedure._verify_live_revision("existing", hashlib.sha256(b"new revision").hexdigest())
    assert procedure._verify_live_revision("existing", hashlib.sha256(b"old page at the same URL").hexdigest())


def test_cta_only_measurement_does_not_confirm_gsc_refresh(tmp_path, monkeypatch):
    monkeypatch.setattr(procedure.LevNyttProcedure, "verify", lambda *args: True)
    outcome = {"status": "PARTIAL", "evidence": {"sources": {
        "gsc": {"status": "unavailable"}, "cta_d1": {"status": "available"}}}}
    result = _verify_outcome({"kind": "opportunity", "capability_id": "measurement",
                              "opportunity_id": "measurement:gsc-refresh"}, outcome, tmp_path, tmp_path)
    assert result["verified"] is False


def test_intervention_is_pending_then_measured_and_guides_next_selection(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    runtime = repo / "runtime"
    (runtime / "intelligence").mkdir(parents=True)
    page = repo / "cellmembran-funktion.html"
    page.write_text("new revision")
    sha = hashlib.sha256(page.read_bytes()).hexdigest()
    baseline = _observed(ago=22)
    path = runtime / "intelligence" / "gsc-latest.json"
    path.write_text(json.dumps(baseline))
    decision_row = {"capability_id": "content_improvement", "opportunity_id": "content-improvement:cellmembran-funktion"}
    interventions.record_result(runtime, decision_row, {"status": "SUCCEEDED", "evidence": {
        "slug": "cellmembran-funktion", "source_file": page.name, "staged_content_sha256": sha, "gate_passed": True}},
        {"verified": True}, {})
    rows = interventions._rows(runtime)
    assert rows[0]["stage"] == "EXECUTED" and rows[0]["baseline"]["page_7d"]
    monkeypatch.setattr(procedure, "_verify_live_revision", lambda slug, expected, wait_seconds=0: expected == sha)
    interventions.record_result(runtime, {"capability_id": "deployment"}, {"status": "SUCCEEDED", "evidence": {
        "slug": "cellmembran-funktion", "source_file": page.name, "files": [page.name], "commit": "abc",
        "source_sha256": sha, "deployed": True}}, {"verified": True}, {})
    rows = interventions._rows(runtime)
    assert rows[0]["stage"] == "MEASUREMENT_PENDING"
    assert rows[0]["stage_history"] == ["EXECUTED", "PUBLISHED/DEPLOYED_VERIFIED", "MEASUREMENT_PENDING"]
    rows[0]["published_at"] = (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
    interventions_path = runtime / "commander" / "interventions.json"
    interventions_path.write_text(json.dumps({"interventions": rows}))
    later = _observed()
    row = next(r for r in later["trends"]["windows"]["7"]["page"]["current"]["rows"] if r["page"].endswith("/cellmembran-funktion"))
    row["impressions"] = 10  # observed decline from the real-schema baseline
    path.write_text(json.dumps(later))
    interventions.follow_up(runtime, path)
    measured = interventions.measured_outcomes(runtime)
    assert measured[0]["direction"] == "DECLINED"
    assert interventions._rows(runtime)[0]["stage_history"][-1] == "MEASURED"
    packet = {"measurement_freshness": {"gsc_fresh": True},
              "runtime_capability_availability": {"content_improvement": {"executable_now": True}},
              "content_improvement_opportunities": {"opportunities": [
                  {"slug": "direktforsaljning-fakta", "opportunity_id": "content-improvement:direktforsaljning-fakta"},
                  {"slug": "cellmembran-funktion", "opportunity_id": "content-improvement:cellmembran-funktion"}]},
              "intervention_followups": measured}
    selected = decision.decide(packet, [], [])
    assert selected["opportunity_id"] == "content-improvement:cellmembran-funktion"
    assert "later GSC" in selected["reason"]


def test_newly_observed_page_and_subsequent_window_are_truthfully_measured(tmp_path):
    runtime = tmp_path / "runtime"
    (runtime / "intelligence").mkdir(parents=True)
    path = runtime / "intelligence" / "gsc-latest.json"
    now = datetime.now(timezone.utc)
    prior = _observed(ago=22)
    slug = "fytosteroler-cellmembran"
    row = {"slug": slug, "stage": "MEASUREMENT_PENDING",
           "stage_history": ["EXECUTED", "PUBLISHED/DEPLOYED_VERIFIED", "MEASUREMENT_PENDING"],
           "published_at": (now - timedelta(days=20)).isoformat(),
           "baseline": {"fetched_at": prior["fetched_at"], "page_7d": None}}
    ledger_path = runtime / "commander" / "interventions.json"
    ledger_path.parent.mkdir()
    ledger_path.write_text(json.dumps({"interventions": [row]}))
    recent = _observed()
    recent["fetched_at"] = (now - timedelta(seconds=10)).isoformat()
    path.write_text(json.dumps(recent))
    interventions.follow_up(runtime, path)
    measured = interventions._rows(runtime)[0]
    assert measured["direction"] == "NEWLY_OBSERVED"
    assert measured["followup"]["impressions_change"] is None
    assert measured["followup"]["baseline_presence"] == "not_reported"
    # A later, disjoint measurement window can replace that direction with a
    # measured decline, making the outcome eligible for reconsideration.
    measured["followup"]["end"] = (now.date() - timedelta(days=11)).isoformat()
    ledger_path.write_text(json.dumps({"interventions": [measured]}))
    current_row = next(r for r in recent["trends"]["windows"]["7"]["page"]["current"]["rows"] if r["page"].endswith("/" + slug))
    current_row["impressions"] = 1
    recent["fetched_at"] = now.isoformat()
    path.write_text(json.dumps(recent))
    interventions.follow_up(runtime, path)
    latest = interventions._rows(runtime)[0]
    assert latest["direction"] == "DECLINED"
    assert latest["followup_history"][0]["direction"] == "NEWLY_OBSERVED"


def test_verified_link_repair_is_staged_not_misreported_as_published(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
    (repo / ".git" / "info" / "exclude").write_text("runtime/\n")
    source = repo / "fytosteroler-cellmembran.html"
    source.write_text("old links")
    subprocess.run(["git", "-C", str(repo), "add", source.name], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
    source.write_text("repaired links")
    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    runtime = repo / "runtime"
    (runtime / "intelligence").mkdir(parents=True)
    (runtime / "intelligence" / "gsc-latest.json").write_text(json.dumps(_observed()))
    interventions.record_result(runtime, {"capability_id": "link_repair", "defect_id": "levnytt:links"},
        {"status": "SUCCEEDED", "evidence": {"changed_files": {source.name: sha}}},
        {"verified": True}, {})
    assert interventions._rows(runtime)[0]["stage"] == "EXECUTED"
    assert evidence._staged_link_repairs(repo, runtime) == ["fytosteroler-cellmembran"]
    assert procedure._first_staged_work(repo)["capability_id"] == "link_repair"
    packet = {"measurement_freshness": {"gsc_fresh": True},
              "staged_awaiting_deployment": evidence._staged_link_repairs(repo, runtime)}
    assert decision.decide(packet, [], [])["capability_id"] == "deployment"
    monkeypatch.setattr(procedure, "_verify_live_revision", lambda slug, expected, wait_seconds=0: expected == sha)
    interventions.record_result(runtime, {"capability_id": "deployment"},
        {"status": "SUCCEEDED", "evidence": {"source_file": source.name, "files": [source.name],
                                           "commit": "abc", "source_sha256": sha}}, {"verified": True}, {})
    assert interventions._rows(runtime)[0]["stage"] == "MEASUREMENT_PENDING"
