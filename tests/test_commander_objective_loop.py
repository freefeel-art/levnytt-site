"""Production entrypoint regressions using isolated runtime and GSC schema."""

import json
import subprocess
from datetime import datetime, timedelta, timezone

import pytest

from commander import decision, gsc_control, operating_loop, procedure, site_opportunities
from conftest import production_gsc_snapshot


def observed(ago=0):
    fetched = (datetime.now(timezone.utc) - timedelta(days=ago)).isoformat()
    windows = {days: production_gsc_snapshot(days, fetched) for days in gsc_control.WINDOWS}
    latest = windows[30]
    latest["trends"] = gsc_control.build_trends(windows)
    return latest


@pytest.fixture
def harness(tmp_path, monkeypatch):
    repo = tmp_path / "site"
    runtime = repo / "runtime"
    (runtime / "intelligence").mkdir(parents=True)
    (runtime / "commander").mkdir()
    (runtime / "commander" / "commitments.json").write_text('{"commitments": []}')
    import app.core.projects as projects
    monkeypatch.setattr(projects, "project_runtime_directory", lambda project_id: runtime)
    monkeypatch.setattr(operating_loop.evidence_module, "detect_defects", lambda *a: [])
    monkeypatch.setattr(operating_loop, "load_active_defects", lambda *a: [])
    state = {"product_backlog": [], "improvements": [], "staged": [], "scout_due": False,
             "community_due": False, "executed": [], "outcomes": {}}
    def packet(root, rt, today):
        gsc = json.loads((runtime / "intelligence" / "gsc-latest.json").read_text())
        fresh = gsc_control.fresh(gsc)
        return {"measurement_freshness": {"gsc_fresh": fresh, "fresh": fresh, "cta_fresh": True},
                "gsc_trends": gsc.get("trends"), "product_backlog": state["product_backlog"],
                "staged_awaiting_deployment": state["staged"],
                "runtime_capability_availability": {"content_improvement": {"executable_now": bool(state["improvements"])},
                                                    "content_production": {"executable_now": False}},
                "content_improvement_opportunities": {"opportunities": state["improvements"]},
                "seo_intelligence": {"opportunity_pool": {"exhausted": True}, "next_eligible_keywords": []},
                "search_demand_scout": {"checked_at": "2020-01-01T00:00:00+00:00"} if state["scout_due"] else
                                       {"checked_at": datetime.now(timezone.utc).isoformat()},
                "community": {"community_intelligence": {"last_run_at": "2020-01-01T00:00:00+00:00" if state["community_due"] else
                              datetime.now(timezone.utc).isoformat()}},
                "distribution": {"execution_eligibility": {"executable_now": False}}}
    monkeypatch.setattr(operating_loop.evidence_module, "build_evidence", packet)
    verify = operating_loop._verify_outcome
    monkeypatch.setattr(operating_loop, "_verify_outcome", lambda d, o, root, rt:
                        verify(d, o, root, rt) if d.get("capability_id") == "measurement" else
                        {"verified": o.get("status") == "SUCCEEDED", "verification_class": "TEST_EFFECT", "detail": "verified"})
    def execute(selected, root, rt):
        state["executed"].append(selected)
        if selected.get("capability_id") == "measurement":
            snap = observed()
            (runtime / "intelligence" / "gsc-latest.json").write_text(json.dumps(snap))
            return {"status": "SUCCEEDED", "evidence": {"sources": {"gsc": {
                "status": "available", "fetched_at": snap["fetched_at"]}}}}
        if selected.get("kind") == "product_backlog":
            state["product_backlog"] = [p for p in state["product_backlog"] if p.get("code") != selected.get("code")]
        return state["outcomes"].get(selected.get("capability_id"),
                                      {"status": "SUCCEEDED", "evidence": {}})
    monkeypatch.setattr(operating_loop, "_execute_decision", execute)
    (runtime / "intelligence" / "gsc-latest.json").write_text(json.dumps(observed()))
    return repo, runtime, state


def run(harness):
    repo, runtime, _ = harness
    return operating_loop.run_cycle(project_root=repo, runtime=runtime)


def test_refresh_rebuilds_and_executes_next_business_action(harness):
    repo, runtime, state = harness
    (runtime / "intelligence" / "gsc-latest.json").write_text(json.dumps(observed(ago=12)))
    state["product_backlog"] = [{"code": "789", "product_name": "Beta Guard", "slug": "neolife-betaguard"}]
    result = run(harness)
    assert [d["capability_id"] for d in state["executed"]] == ["measurement", "product_page"]
    assert result["stop_reason"] == "NO_JUSTIFIED_EXECUTABLE_WORK"
    assert result["action_count"] == 2


def test_exhausted_gsc_attempt_does_not_idle_independent_work(harness):
    repo, runtime, state = harness
    (runtime / "intelligence" / "gsc-latest.json").write_text(json.dumps(observed(ago=12)))
    from commander.identity import save_state
    save_state({"daily_measurement_budget": {"date": operating_loop._today(), "used": 1, "limit": 1}}, runtime)
    state["product_backlog"] = [{"code": "789", "product_name": "Beta Guard"}]
    result = run(harness)
    assert [d["capability_id"] for d in state["executed"]] == ["product_page"]
    assert result["stop_reason"] == "WAITING_FOR_MEASUREMENT"


def test_several_independent_actions_and_both_daily_budgets(harness):
    repo, runtime, state = harness
    state["product_backlog"] = [{"code": "789", "product_name": "Beta Guard"},
                                {"code": "790", "product_name": "Other"}]
    state["improvements"] = [{"opportunity_id": f"content-improvement:page-{n}", "slug": f"page-{n}"}
                             for n in range(5)]
    result = run(harness)
    assert [d["capability_id"] for d in state["executed"]] == ["product_page"] + ["content_improvement"] * 3
    assert result["content_budgets"]["publication"]["used"] == 1
    assert result["content_budgets"]["optimization"]["used"] == 3
    assert result["stop_reason"] == "CAPACITY_EXHAUSTED"


def test_failed_budgeted_action_does_not_consume_daily_capacity(harness):
    repo, runtime, state = harness
    state["product_backlog"] = [{"code": "789", "product_name": "Beta Guard"}]
    state["outcomes"]["product_page"] = {
        "status": "BLOCKED",
        "failure_class": "RECOVERABLE_EXECUTOR_FAILURE",
        "retry_eligible_this_run": True,
        "evidence": {"external_effect_attempted": False},
    }
    run(harness)
    persisted = json.loads((runtime / "commander" / "commander-state.json").read_text())
    assert persisted.get("daily_publication_budget", {}).get("used", 0) == 0


def test_idle_does_not_report_commitment_wait_when_open_commitments_are_not_executable(harness):
    repo, runtime, state = harness
    state["product_backlog"] = [{"code": "789", "product_name": "Beta Guard"}]
    state["improvements"] = [{"opportunity_id": "content-improvement:fixture"}]
    (runtime / "commander" / "commitments.json").write_text(json.dumps({"commitments": [{
        "commitment_id": "levnytt:content_improvement:content-improvement:fixture",
        "capability_id": "content_improvement", "status": "OPEN", "action": "fixture",
        "metadata": {}, "project_id": "levnytt",
    }]}))
    from commander.identity import save_state
    save_state({
        "daily_publication_budget": {"date": operating_loop._today(), "used": 1, "limit": 1},
        "daily_optimization_budget": {"date": operating_loop._today(), "used": 3, "limit": 3},
        "daily_measurement_budget": {"date": operating_loop._today(), "used": 1, "limit": 1},
    }, runtime)
    result = run(harness)
    assert result["executable_commitments"] == 0
    assert result["stop_reason"] == "CAPACITY_EXHAUSTED"


def test_blocked_deployment_is_parked_and_independent_work_runs(harness):
    repo, runtime, state = harness
    state["staged"] = ["blocked"]
    state["product_backlog"] = [{"code": "789", "product_name": "Beta Guard"}]
    state["outcomes"]["deployment"] = {"status": "BLOCKED", "failure_class": "EVIDENCE_REQUIRED",
        "retry_eligible_this_run": False, "evidence": {"slug": "blocked", "reasons": ["dirty file"],
                                                         "blocker_paths": ["unrelated.md"]}}
    result = run(harness)
    assert [d["capability_id"] for d in state["executed"]] == ["deployment", "product_page"]
    assert result["stop_reason"] == "WAITING_FOR_BLOCKED_DEPLOYMENT"
    assert "blocked" in json.loads((runtime / "commander" / "commander-state.json").read_text())["deployment_parked"]


def test_scout_and_existing_community_executor_are_decision_reachable(harness, monkeypatch):
    repo, runtime, state = harness
    state.update(scout_due=True, community_due=True)
    # Exercise the real dispatch, while replacing only the external provider calls.
    def scout(project, rt, **kwargs):
        artifact = {"status": "OPPORTUNITY_FOUND", "checked_at": datetime.now(timezone.utc).isoformat(),
                    "opportunities": [{"term": "hudvård", "classification": "CREATE"}]}
        (rt / "intelligence" / "search-demand-scout.json").write_text(json.dumps(artifact))
        return artifact
    import app.commander.search_demand_scout as shared
    monkeypatch.setattr(shared, "run_search_demand_scout", scout)
    called = []
    def community(self, ctx, action):
        called.append(action["opportunity_id"])
        return {"status": "SUCCEEDED", "evidence": {"read_only": True}}
    monkeypatch.setattr(procedure.LevNyttProcedure, "_execute_community_intelligence", community)
    monkeypatch.setattr(operating_loop, "_execute_decision",
                        lambda selected, root, rt: procedure.LevNyttProcedure().execute(
                            operating_loop._ctx(root, rt), operating_loop._action_for(selected, rt)))
    # Once the Scout runs, this fixture exposes its fresh timestamp on rebuild.
    original = operating_loop.evidence_module.build_evidence
    def packet(root, rt, today):
        result = original(root, rt, today)
        artifact = rt / "intelligence" / "search-demand-scout.json"
        if artifact.exists():
            result["search_demand_scout"]["checked_at"] = json.loads(artifact.read_text())["checked_at"]
        return result
    monkeypatch.setattr(operating_loop.evidence_module, "build_evidence", packet)
    result = run(harness)
    assert [s["decision"]["capability_id"] for s in result["steps"]] == ["search_demand_scout", "community_intelligence"]
    assert called == ["discovery:community"]


def test_selected_keyword_is_exact_and_cannot_be_substituted(tmp_path, monkeypatch):
    repo = tmp_path / "site"
    rt = repo / "runtime"
    (rt / "intelligence").mkdir(parents=True)
    (rt / "intelligence" / "keywords.json").write_text(json.dumps({"keywords": [
        {"keyword": "magnesium", "priority_score": 100}, {"keyword": "hudvård", "priority_score": 1}]}))
    import app.commander.evidence as shared
    monkeypatch.setattr(shared, "_seo_intelligence_levnytt", lambda *a: {"next_eligible_keywords": ["hudvård"]})
    ctx = operating_loop._ctx(repo, rt)
    chosen = {"kind": "opportunity", "capability_id": "content_production",
              "opportunity_id": "content-gap:hudvård", "target": "hudvård"}
    action = operating_loop._action_for(chosen, rt)
    assert procedure._keyword_from_action(ctx, action) == "hudvård"
    assert procedure._keyword_from_action(ctx, {**action, "target": "unknown"}) is None
    assert procedure._keyword_from_action(ctx, {**action, "target": "magnesium"}) is None


def test_finite_bound_and_truthful_idle_only_after_candidates_considered(harness, monkeypatch):
    repo, runtime, state = harness
    defects = [{"defect_id": f"defect:{n}", "status": "OPEN", "kind": "test", "capability_id": "link_repair",
                "repair": {"repository_kind": "PROJECT"}} for n in range(10)]
    monkeypatch.setattr(operating_loop, "load_active_defects", lambda *a: defects)
    monkeypatch.setattr(operating_loop, "record_repair_attempt", lambda *a: None)
    monkeypatch.setattr(operating_loop, "close_defect", lambda *a, **kw: None)
    monkeypatch.setattr(operating_loop.repairs, "run_link_repair", lambda *a: {"status": "SUCCEEDED"})
    monkeypatch.setattr(operating_loop.repairs, "verify_link_repair", lambda *a: (True, {"remaining_count": 0}))
    result = run(harness)
    assert result["action_count"] == operating_loop.MAX_ACTIONS_PER_INVOCATION == 8
    assert result["stop_reason"] == "BOUNDED_LOOP_SAFETY_LIMIT"
    assert len({d["defect_id"] for d in state["executed"]}) == 8


def test_discovery_handoffs_preserve_exact_target_and_cooldown():
    term = "omega 3 kvalitet"
    packet = {"measurement_freshness": {"gsc_fresh": True, "fresh": True},
              "search_demand_scout": {"checked_at": datetime.now(timezone.utc).isoformat(),
                  "actionable_opportunities": [{"term": term, "classification": "CREATE",
                                                 "provenance": {"discovered_at": "2026-09-22"}}]},
              "seo_intelligence": {"keywords": [], "opportunity_pool": {"exhausted": True}},
              "community": {"community_intelligence": {"last_run_at": datetime.now(timezone.utc).isoformat()}}}
    chosen = decision.decide(packet, [], [])
    assert chosen["target"] == term and chosen["opportunity_id"] == "scout:create:" + term
    assert operating_loop._action_for(chosen)["target"] == term
    packet["recent_decisions"] = [{"capability_id": "seo_intelligence", "opportunity_id": chosen["opportunity_id"],
                                   "selected_at": datetime.now(timezone.utc).isoformat()}]
    assert decision.decide(packet, [], [])["kind"] == "idle"


def test_unmeasured_content_seed_routes_to_research_not_publication():
    packet = {"measurement_freshness": {"gsc_fresh": True, "fresh": True},
              "runtime_capability_availability": {"content_production": {"executable_now": True}},
              "seo_intelligence": {"opportunity_pool": {"exhausted": False},
                                   "next_eligible_keywords": ["torr hud"],
                                   "keywords": [{"keyword": "torr hud", "monthly_search_volume": None}]}}
    selected = decision.decide(packet, [], [])
    assert selected["capability_id"] == "seo_intelligence"
    assert selected["target"] == "torr hud"


def test_commercial_click_routes_to_exact_existing_page_and_stages_canonical_pair(tmp_path, monkeypatch):
    monkeypatch.setattr(procedure, "_verify_live_ok", lambda slug: slug == "neolife-magnesium-complex")
    repo = tmp_path / "site"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "content" / "data").mkdir(parents=True)
    entity = repo / "content" / "products" / "entities" / "entity_magnesium" / "sv.json"
    entity.parent.mkdir(parents=True)
    entity.write_text(json.dumps({"neoLife_code": 42, "slug": "neolife-magnesium-complex",
                                  "product_name": "Magnesium Complex", "category": "supplements"}))
    (repo / "neolife-magnesium-complex.html").write_text("<h1>NeoLife Magnesium Complex</h1>")
    source = repo / "magnesium-komplett-guide.html"
    source.write_text("<main><h1>Magnesium – komplett guide</h1><p>Fakta</p></main>")
    data = repo / "content" / "data" / "production-pages.json"
    data.write_text(json.dumps({"pages": [{"path": "/magnesium-komplett-guide",
                 "source_file": source.name, "family": "informational-article",
                 "title": "Magnesium komplett guide", "body_html": "<h1>Magnesium</h1>"}]}))
    subprocess.run(["git", "-C", str(repo), "add", "content", source.name,
                    "neolife-magnesium-complex.html"], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=Test",
                    "-c", "user.email=test@example.com", "commit", "-qm", "fixture"], check=True)
    packet = {"gsc_pages": [{"page": "https://levnytt.se/magnesium-komplett-guide",
                             "clicks": 2, "impressions": 30}],
              "neolife_link_clicks": {"fresh": True, "recent_events": [{"page_path": "/magnesium-komplett-guide"}]}}
    rows = site_opportunities.opportunities(repo, packet)
    assert len(rows) == 1
    selected = decision.decide({"measurement_freshness": {"gsc_fresh": True, "fresh": True},
        "product_backlog": [{"code": "9", "product_name": "Other"}],
        "internal_link_opportunities": rows}, [], [])
    assert selected["capability_id"] == "internal_linking"
    assert selected["opportunity_id"] == rows[0]["opportunity_id"]
    execution = procedure.LevNyttProcedure().execute(operating_loop._ctx(repo, repo / "runtime"),
                                                      operating_loop._action_for(selected))
    assert execution["status"] == "SUCCEEDED"
    assert site_opportunities.verify_staged_link(repo, execution["evidence"])
    assert "href=\"/neolife-magnesium-complex\"" in json.loads(data.read_text())["pages"][0]["body_html"]
    (repo / "runtime" / "commander").mkdir(parents=True)
    (repo / "runtime" / "commander" / "commitments.json").write_text(json.dumps({"commitments": [{
        "status": "CONFIRMED", "capability_id": "internal_linking",
        "resolution_reason": repr(execution["evidence"])}]}))
    work = procedure._first_staged_work(repo)
    assert work["files"] == [source.name, "content/data/production-pages.json"]
    assert not site_opportunities.opportunities(repo, packet)  # no duplicate mutation


def test_missing_exact_discovery_target_is_not_substituted_in_scout(tmp_path, monkeypatch):
    repo = tmp_path / "site"
    rt = repo / "runtime"
    (rt / "intelligence").mkdir(parents=True)
    (repo / "config").mkdir()
    monkeypatch.setattr(procedure, "_seed_keyword_candidates", lambda ctx: None)
    monkeypatch.setattr(procedure, "_rebuild_content_inventory", lambda root: None)
    monkeypatch.setattr(procedure, "_build_scout_discovery_context", lambda ctx: {
        "seed_concepts": ["magnesium", "hudvård"], "business_scope": "LevNytt"})
    import app.commander.scout_executor as scout
    def execute(*, project, keywords):
        assert keywords == ["hudvård"]
        context = json.loads((rt / "intelligence" / "scout-discovery-context.json").read_text())
        assert context["seed_concepts"][0] == "hudvård"
        (rt / "intelligence" / "keywords.json").write_text(json.dumps({"keywords": [
            {"keyword": "magnesium"}]}))
        return 0, "provider completed but omitted selected term"
    monkeypatch.setattr(scout, "execute", execute)
    action = {"capability": "seo_intelligence", "target": "hudvård", "opportunity_id": "scout:create:hudvård"}
    ctx = operating_loop._ctx(repo, rt)
    result = procedure.LevNyttProcedure().execute(ctx, action)
    assert result["status"] == "BLOCKED"
    assert "selected term" in result["detail"]
    assert not procedure.LevNyttProcedure().verify(ctx, action, result)


def test_real_evidence_join_promotes_scout_and_forum_questions(tmp_path, monkeypatch):
    from commander import evidence as local_evidence
    from app.commander import evidence as shared_evidence
    from commander.community import record_discovery

    repo = tmp_path / "site"
    rt = repo / "runtime"
    (rt / "intelligence").mkdir(parents=True)
    (rt / "commander").mkdir()
    (rt / "commander" / "commitments.json").write_text('{"commitments": []}')
    (rt / "intelligence" / "gsc-latest.json").write_text(json.dumps(observed()))
    checked_at = datetime.now(timezone.utc).isoformat()
    artifact = {"checked_at": checked_at, "status": "OPPORTUNITY_FOUND", "opportunities": [
        {"term": "hudvård behov", "classification": "CREATE", "signal": "NEW",
         "commercial_relevance": "HIGH", "dataforseo_market": {"search_volume": 80,
                                                      "competition_index": 28},
         "coverage": {"coverage": "NONE"}, "provenance": {"discovered_at": checked_at}}]}
    (rt / "intelligence" / "search-demand-scout.json").write_text(json.dumps(artifact))
    record_discovery(rt, [{"query": "magnesium kosttillskott forum", "platform": "flashback_forum",
                           "url": "https://www.flashback.org/t3456000", "title": "Vilket magnesium ska jag välja?",
                           "snippet": "Jag undrar vilket magnesium som passar", "observed_at": checked_at,
                           "recommended_action": "POSSIBLE_REPLY"}])
    monkeypatch.setattr(shared_evidence, "_levnytt", lambda *args: {
        "measurement_freshness": {"cta_fresh": True}, "runtime_capability_availability": {},
        "staged_awaiting_deployment": [],
        "seo_intelligence": {"keywords": [], "opportunity_pool": {"exhausted": True}},
        "search_demand_scout": shared_evidence._search_demand_scout(rt),
        "community": {"community_intelligence": {"last_run_at": checked_at}},
        "neolife_link_clicks": {"fresh": False}})
    packet = local_evidence.build_evidence(repo, rt, datetime.now().date().isoformat())
    packet["product_catalog_discovery_due"] = False
    assert packet["search_demand_scout"]["actionable_opportunities"][0]["commercial_relevance"] == "HIGH"
    assert packet["community_demand_candidates"][0]["source_url"] == "https://www.flashback.org/t3456000"
    selected = decision.decide(packet, [], [])
    assert selected["capability_id"] == "seo_intelligence"
    assert selected["target"] == "hudvård behov"
    assert selected["provenance"]["dataforseo_market"]["search_volume"] == 80
    artifact["opportunities"] = []
    (rt / "intelligence" / "search-demand-scout.json").write_text(json.dumps(artifact))
    packet = local_evidence.build_evidence(repo, rt, datetime.now().date().isoformat())
    packet["product_catalog_discovery_due"] = False
    selected = decision.decide(packet, [], [])
    assert selected["target"] == "Vilket magnesium ska jag välja"
    assert selected["provenance"]["source_url"].endswith("t3456000")


def test_pinterest_access_blocker_parks_capability_not_independent_discovery(harness, monkeypatch):
    from commander import pinterest_channel as pins
    from commander.identity import load_state
    from app.commander.commitment_ledger import open_commitments
    import app.providers.pinterest as provider

    monkeypatch.setenv("PINTEREST_ACCESS_TIER", "trial")
    repo, runtime, state = harness
    state.update(scout_due=True, community_due=True)
    (repo / "images").mkdir()
    candidates = []
    for slug, name in (("neolife-all-c", "All C"), ("neolife-garlic-allium-complex", "Garlic Allium Complex")):
        image = name.casefold().replace(" ", "") + ".jpg"
        (repo / "images" / image).write_bytes(b"\xff\xd8\xff\x00small-jpeg")
        candidates.append({"pin_class": "product", "slug": slug, "code": "552" if name == "All C" else "555",
                           "product_name": name, "image": "/images/" + image,
                           "destination": "https://levnytt.se/" + slug, "title": "NeoLife " + name,
                           "description": "Product facts", "board_id": "1151232792187766770"})
    monkeypatch.setattr(pins, "product_pin_opportunities", lambda root: candidates)
    monkeypatch.setattr(pins, "informational_pin_opportunities", lambda root: [])
    built = operating_loop.evidence_module.build_evidence
    def packet(root, rt, today):
        result = built(root, rt, today)
        result["product_catalog_discovery_due"] = False
        result["pinterest_opportunities"] = [o for o in candidates if not pins.already_published(
            rt, o["destination"], o["image"], o["title"])]
        return result
    monkeypatch.setattr(operating_loop.evidence_module, "build_evidence", packet)

    calls = []
    class TrialProvider:
        def publish_package(self, package, approved=False):
            calls.append(package.title)
            raise provider.PinterestError("Pinterest publication is blocked until PINTEREST_ACCESS_TIER=standard")
    monkeypatch.setattr(provider, "PinterestProvider", lambda: TrialProvider())
    def execute(selected, root, rt):
        state["executed"].append(selected)
        if selected.get("capability_id") == "pinterest":
            return procedure.LevNyttProcedure().execute(operating_loop._ctx(root, rt),
                operating_loop._action_for(selected, rt))
        return {"status": "SUCCEEDED", "detail": "Independent discovery completed", "evidence": {}}
    monkeypatch.setattr(operating_loop, "_execute_decision", execute)

    report = run(harness)
    assert [s["decision"]["capability_id"] for s in report["steps"]] == [
        "pinterest", "search_demand_scout", "community_intelligence"]
    assert report["action_count"] == 3 < operating_loop.MAX_ACTIONS_PER_INVOCATION
    assert calls == ["NeoLife All C"]
    assert len(json.loads((runtime / "pinterest" / "published.json").read_text())["attempts"]) == 1
    blocker = load_state(runtime)["capability_blockers"]["pinterest"]
    assert blocker["blocker_id"] == "pinterest_standard_access"
    assert blocker["opportunity_id"] == "pinterest:product:neolife-all-c"
    assert blocker["condition"]["value"] == "standard"

    state.update(scout_due=False, community_due=False)
    second = run(harness)
    assert second["action_count"] == 0
    assert calls == ["NeoLife All C"]  # no blind retry in the next invocation
    assert len(open_commitments(runtime)) == 1

    monkeypatch.setenv("PINTEREST_ACCESS_TIER", "standard")
    saved = load_state(runtime)
    active, cleared = operating_loop._active_capability_blockers(saved)
    assert active == [] and cleared == ["pinterest"]
    assert saved["capability_blockers"]["pinterest"]["status"] == "CLEARED"
    evidence = packet(repo, runtime, operating_loop._today())
    evidence["recent_decisions"] = saved.get("prior_decisions") or []
    evidence["blocked_capabilities"] = active
    evidence["cleared_capability_blockers"] = cleared
    selected = decision.decide(evidence, [], open_commitments(runtime), budget_check=lambda _: True)
    assert selected["kind"] == "resume_commitment" and selected["capability_id"] == "pinterest"


def test_one_bad_pin_does_not_suppress_other_pin_or_discovery(harness, monkeypatch):
    repo, runtime, state = harness
    state.update(scout_due=True, community_due=False)
    built = operating_loop.evidence_module.build_evidence
    def packet(root, rt, today):
        result = built(root, rt, today)
        result["pinterest_opportunities"] = [
            {"slug": "pin-one", "pin_class": "product", "product_name": "One"},
            {"slug": "pin-two", "pin_class": "product", "product_name": "Two"}]
        return result
    monkeypatch.setattr(operating_loop.evidence_module, "build_evidence", packet)
    state["outcomes"]["pinterest"] = {"status": "BLOCKED", "detail": "Only this Pin has the wrong image",
                                         "evidence": {"external_effect_attempted": False}}
    report = run(harness)
    assert [s["decision"]["opportunity_id"] for s in report["steps"][:2]] == [
        "pinterest:product:pin-one", "pinterest:product:pin-two"]
    assert report["steps"][2]["decision"]["capability_id"] == "search_demand_scout"
    from commander.identity import load_state
    assert load_state(runtime).get("capability_blockers") in (None, {})


def test_existing_production_block_receipt_is_recognised_without_replaying_a_pin(monkeypatch):
    monkeypatch.setenv("PINTEREST_ACCESS_TIER", "trial")
    state = {"prior_decisions": [{
        "capability_id": "pinterest", "opportunity_id": "pinterest:product:neolife-all-c",
        "selected_at": datetime.now(timezone.utc).isoformat(),
        "execution": {"status": "BLOCKED_BY_PINTEREST_STANDARD_ACCESS",
                      "detail": "Pinterest publication is blocked until PINTEREST_ACCESS_TIER=standard"}}]}
    active, cleared = operating_loop._active_capability_blockers(state)
    assert active == ["pinterest"] and cleared == []
    assert state["capability_blockers"]["pinterest"]["opportunity_id"] == "pinterest:product:neolife-all-c"
    assert state["capability_blockers"]["pinterest"]["condition"]["value"] == "standard"
