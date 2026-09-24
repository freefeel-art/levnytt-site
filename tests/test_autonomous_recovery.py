"""Autonomous-recovery and anti-stall tests for the dedicated LevNytt Commander.

Two halves of the recovery design:

1. A missing official product image is no longer treated as an Owner-only
   dependency: ``product_media.acquire_official_image`` recovers it from the
   public NeoLife shop keyed by the product code (the identity tie), validates
   the bytes, and stores it under the project's normal asset path.

2. A determinately-blocked commitment is escalated (OWNER_BOUNDARY) rather than
   retried forever, and an escalated product with no local image is excluded
   from the backlog so it cannot starve unrelated work.
"""

from __future__ import annotations

import io
import json
from pathlib import Path

from PIL import Image

from commander import evidence
from commander import product_media
from commander.operating_loop import _escalate_if_non_retryable
from app.commander.commitment_ledger import commitment_records


class _FakeResponse:
    def __init__(self, status_code: int, text: str, content: bytes):
        self.status_code = status_code
        self.text = text
        self.content = content


def _png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (12, 12), (180, 40, 40)).save(buffer, format="PNG")
    return buffer.getvalue()


def _entity(code="740", name="Vita Squares", slug="neolife-vita-squares", category="supplements"):
    return {
        "neoLife_code": code, "product_name": name, "slug": slug, "category": category,
        "short_description": "kort", "summary": "sammanfattning",
        "packaging": {"label": "180 tuggtabletter"}, "usage": {"dosage": "enligt anvisning"},
        "ingredients": [{"name": "spektrum"}],
    }


def _make_get(listing_html: str, image_bytes: bytes, image_status: int = 200):
    calls: list[str] = []

    def get(url, headers=None, timeout=None, allow_redirects=True):
        calls.append(url)
        if "/c/" in url:
            return _FakeResponse(200, listing_html, b"")
        if "/thumb/" in url and "/0x0/" in url:
            return _FakeResponse(image_status, "", image_bytes)
        return _FakeResponse(404, "", b"")

    return get, calls


# ── acquisition ──────────────────────────────────────────────────────────────


def test_acquire_matches_code_and_stores(monkeypatch, tmp_path):
    html = '<img src="/thumb/605/350x350/740.jpg">'
    fake, calls = _make_get(html, _png_bytes())
    monkeypatch.setattr(product_media.requests, "get", fake)

    result = product_media.acquire_official_image(_entity(), tmp_path)
    assert result["status"] == product_media.ACQUIRED
    assert result["image"] == "/images/neolife-vita-squares.jpg"
    assert (tmp_path / "images" / "neolife-vita-squares.jpg").is_file()
    # Downloaded the full-size asset, not the thumbnail.
    assert any("/0x0/740.jpg" in u for u in calls)


def test_acquire_not_found_when_no_code_match(monkeypatch, tmp_path):
    html = '<img src="/thumb/605/350x350/552.jpg">'
    monkeypatch.setattr(product_media.requests, "get", _make_get(html, b"")[0])
    result = product_media.acquire_official_image(_entity(), tmp_path)
    assert result["status"] == product_media.NOT_FOUND


def test_acquire_code_match_is_exact_not_prefix(monkeypatch, tmp_path):
    # 7400.jpg must not match code 740.
    html = '<img src="/thumb/605/350x350/7400.jpg">'
    monkeypatch.setattr(product_media.requests, "get", _make_get(html, _png_bytes())[0])
    result = product_media.acquire_official_image(_entity(code="740"), tmp_path)
    assert result["status"] == product_media.NOT_FOUND


def test_acquire_unmapped_category(monkeypatch, tmp_path):
    monkeypatch.setattr(product_media.requests, "get", _make_get("", b"")[0])
    result = product_media.acquire_official_image(_entity(category="novelty"), tmp_path)
    assert result["status"] == product_media.UNMAPPED_CATEGORY


def test_acquire_unavailable_on_network_error(monkeypatch, tmp_path):
    def boom(url, headers=None, timeout=None, allow_redirects=True):
        raise product_media.requests.RequestException("down")

    monkeypatch.setattr(product_media.requests, "get", boom)
    result = product_media.acquire_official_image(_entity(), tmp_path)
    assert result["status"] == product_media.UNAVAILABLE


def test_acquire_rejects_non_image_bytes(monkeypatch, tmp_path):
    html = '<img src="/thumb/605/350x350/740.jpg">'
    monkeypatch.setattr(product_media.requests, "get", _make_get(html, b"not an image")[0])
    result = product_media.acquire_official_image(_entity(), tmp_path)
    assert result["status"] == product_media.NOT_FOUND
    assert not (tmp_path / "images").exists() or not list((tmp_path / "images").glob("*.jpg"))


def test_acquire_no_code_is_not_acquisition(monkeypatch, tmp_path):
    monkeypatch.setattr(product_media.requests, "get", _make_get("", b"")[0])
    result = product_media.acquire_official_image(_entity(code=None), tmp_path)
    assert result["status"] == product_media.NO_CODE


# ── escalation (anti-stall) ──────────────────────────────────────────────────


def _write_ledger(runtime: Path, rows: list[dict]) -> None:
    path = runtime / "commander" / "commitments.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"commitments": rows}, ensure_ascii=False), encoding="utf-8")


def _open_row():
    return {
        "commitment_id": "levnytt:product_page:740", "status": "OPEN",
        "kind": "unverified_external_effect", "capability_id": "product_page",
        "project_id": "levnytt", "action": "Vita Squares", "reason": "no page",
        "executor_id": "product_page", "metadata": {},
        "recorded_at": "2026-09-04T16:00:00+02:00",
        "resolution_reason": None, "resolved_at": None,
    }


def test_escalate_determinate_evidence_block(tmp_path):
    runtime = tmp_path / "runtime"
    _write_ledger(runtime, [_open_row()])
    decision = {"kind": "resume_commitment", "commitment_id": "levnytt:product_page:740"}
    outcome = {"status": "BLOCKED", "failure_class": "EVIDENCE_REQUIRED",
               "retry_eligible_this_run": False, "detail": "no exact image"}
    _escalate_if_non_retryable(decision, outcome, runtime)
    records = {r["commitment_id"]: r for r in commitment_records(runtime)}
    assert records["levnytt:product_page:740"]["status"] == "OWNER_BOUNDARY"
    assert "no exact image" in records["levnytt:product_page:740"]["resolution_reason"]


def test_escalate_leaves_retryable_block_open(tmp_path):
    runtime = tmp_path / "runtime"
    _write_ledger(runtime, [_open_row()])
    decision = {"kind": "resume_commitment", "commitment_id": "levnytt:product_page:740"}
    outcome = {"status": "BLOCKED", "failure_class": "EVIDENCE_REQUIRED",
               "retry_eligible_this_run": True, "detail": "shop unreachable"}
    _escalate_if_non_retryable(decision, outcome, runtime)
    records = {r["commitment_id"]: r for r in commitment_records(runtime)}
    assert records["levnytt:product_page:740"]["status"] == "OPEN"


def test_escalate_ignores_non_evidence_failure_classes(tmp_path):
    runtime = tmp_path / "runtime"
    _write_ledger(runtime, [_open_row()])
    decision = {"kind": "resume_commitment", "commitment_id": "levnytt:product_page:740"}
    outcome = {"status": "BLOCKED", "failure_class": "RECOVERABLE_QA_REJECTION",
               "retry_eligible_this_run": False, "detail": "self-link"}
    _escalate_if_non_retryable(decision, outcome, runtime)
    records = {r["commitment_id"]: r for r in commitment_records(runtime)}
    assert records["levnytt:product_page:740"]["status"] == "OPEN"


# ── backlog excludes escalated products without a local image ────────────────


def _build_entity_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    entities = repo / "content" / "products" / "entities" / "entity_vita_squares"
    entities.mkdir(parents=True)
    (entities / "sv.json").write_text(
        json.dumps(_entity(), ensure_ascii=False), encoding="utf-8"
    )
    return repo


def test_backlog_skips_escalated_product_without_local_image(tmp_path):
    repo = _build_entity_repo(tmp_path)
    runtime = tmp_path / "runtime"
    _write_ledger(runtime, [{
        "commitment_id": "levnytt:product_page:740", "status": "OWNER_BOUNDARY",
        "capability_id": "product_page", "project_id": "levnytt",
        "resolution_reason": "no image", "resolved_at": "2099-09-10T10:00:00+02:00",
    }])
    backlog = evidence._product_backlog(repo, runtime)
    assert backlog == []


def test_expired_owner_boundary_rechecks_product_condition(tmp_path):
    repo = _build_entity_repo(tmp_path)
    runtime = tmp_path / "runtime"
    _write_ledger(runtime, [{
        "commitment_id": "levnytt:product_page:740", "status": "OWNER_BOUNDARY",
        "capability_id": "product_page", "project_id": "levnytt",
        "resolution_reason": "no image", "resolved_at": "2026-09-10T10:00:00+02:00",
    }])
    backlog = evidence._product_backlog(repo, runtime)
    assert any(row["code"] == "740" for row in backlog)


def test_backlog_reincludes_escalated_product_once_local_image_exists(tmp_path):
    repo = _build_entity_repo(tmp_path)
    (repo / "images").mkdir()
    (repo / "images" / "neolife-vita-squares.jpg").write_bytes(_png_bytes())
    runtime = tmp_path / "runtime"
    _write_ledger(runtime, [{
        "commitment_id": "levnytt:product_page:740", "status": "OWNER_BOUNDARY",
        "capability_id": "product_page", "project_id": "levnytt",
        "resolution_reason": "no image", "resolved_at": "2026-09-10T10:00:00+02:00",
    }])
    backlog = evidence._product_backlog(repo, runtime)
    assert any(b["code"] == "740" for b in backlog)


def test_product_page_deployment_record_includes_image(tmp_path):
    from commander.procedure import _confirmed_staged_work
    import hashlib
    import subprocess

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / ".git" / "info" / "exclude").write_text("runtime/\n")
    source = tmp_path / "neolife-vita-squares.html"
    source.write_text("accepted product revision")

    runtime = tmp_path / "runtime"
    _write_ledger(runtime, [{
        "commitment_id": "levnytt:product_page:740", "status": "CONFIRMED",
        "capability_id": "product_page", "project_id": "levnytt",
        "resolution_reason": repr({
            "gate_passed": True, "slug": "neolife-vita-squares",
            "source_file": "neolife-vita-squares.html",
            "staged_content_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "image": "/images/neolife-vita-squares.jpg",
        }),
    }])
    records = _confirmed_staged_work(tmp_path)
    assert records[0]["files"] == [
        "neolife-vita-squares.html", "images/neolife-vita-squares.jpg"
    ]


# ── deployment parking (anti-stall for repeated deployment-safety blocks) ─────


def _seed_staged_vita(repo: Path) -> Path:
    import hashlib
    (repo / ".git" / "info" / "exclude").write_text("runtime/\n")
    page = repo / "neolife-vita-squares.html"
    page.write_text("staged revision")
    runtime = repo / "runtime"
    _write_ledger(runtime, [{"capability_id": "product_page", "status": "CONFIRMED",
                             "resolution_reason": repr({"gate_passed": True, "slug": "neolife-vita-squares",
                                                       "source_file": page.name,
                                                       "staged_content_sha256": hashlib.sha256(page.read_bytes()).hexdigest()})}])
    return runtime


def test_deployment_safety_block_is_classified_determinate(tmp_path):
    """A deployment safety-gate BLOCKED must carry failure_class EVIDENCE_REQUIRED
    and retry_eligible_this_run False so the loop can reason about it."""
    from commander.operating_loop import _escalate_if_non_retryable

    runtime = tmp_path / "runtime"
    _write_ledger(runtime, [{
        "commitment_id": "levnytt:deployment:deployment:staged",
        "status": "OPEN", "kind": "unverified_external_effect",
        "capability_id": "deployment", "project_id": "levnytt",
        "action": "deploy staged", "reason": "staged",
        "executor_id": "deployment", "metadata": {},
        "recorded_at": "2026-09-10T22:00:00+02:00",
        "resolution_reason": None, "resolved_at": None,
    }])
    decision = {"kind": "opportunity", "capability_id": "deployment",
                "commitment_id": "levnytt:deployment:deployment:staged"}
    outcome = {
        "status": "BLOCKED",
        "failure_class": "EVIDENCE_REQUIRED",
        "retry_eligible_this_run": False,
        "detail": "Deployment safety check failed: unexpected tracked change",
        "evidence": {
            "ok": False, "slug": "neolife-vita-squares",
            "reasons": ["unexpected tracked change ' M' ROADMAP.md"],
            "external_effect_attempted": False,
        },
    }
    _escalate_if_non_retryable(decision, outcome, runtime)
    from app.commander.commitment_ledger import commitment_records
    records = {r["commitment_id"]: r for r in commitment_records(runtime)}
    assert records["levnytt:deployment:deployment:staged"]["status"] == "OWNER_BOUNDARY"


def test_deployment_parked_in_state_after_safety_block(tmp_path):
    from commander.operating_loop import _park_deployment_if_stalled

    project_root = tmp_path / "repo"
    project_root.mkdir()
    import subprocess
    subprocess.run(["git", "-C", str(project_root), "init"], capture_output=True, check=True)
    (project_root / "ROADMAP.md").write_text("dirty")
    subprocess.run(["git", "-C", str(project_root), "add", "ROADMAP.md"], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(project_root), "commit", "-m", "base"], capture_output=True, check=True)
    (project_root / "ROADMAP.md").write_text("modified")
    _seed_staged_vita(project_root)

    state: dict = {}
    decision = {"kind": "opportunity", "capability_id": "deployment"}
    outcome = {
        "status": "BLOCKED",
        "failure_class": "EVIDENCE_REQUIRED",
        "retry_eligible_this_run": False,
        "detail": "Deployment safety check failed: unexpected",
        "evidence": {
            "slug": "neolife-vita-squares",
                "reasons": ["unexpected tracked change ' M' ROADMAP.md"],
                "blocker_paths": ["ROADMAP.md"],
            "external_effect_attempted": False,
        },
    }
    _park_deployment_if_stalled(decision, outcome, state, project_root)
    parked = state.get("deployment_parked") or {}
    assert "neolife-vita-squares" in parked
    assert parked["neolife-vita-squares"]["escalation_count"] == 1
    assert parked["neolife-vita-squares"]["blocker_paths"] == ["ROADMAP.md"]


def test_parked_deployment_stays_parked_when_tree_unchanged(tmp_path):
    from commander.operating_loop import _park_deployment_if_stalled

    project_root = tmp_path / "repo"
    project_root.mkdir()
    import subprocess
    subprocess.run(["git", "-C", str(project_root), "init"], capture_output=True, check=True)
    (project_root / "ROADMAP.md").write_text("dirty")
    subprocess.run(["git", "-C", str(project_root), "add", "ROADMAP.md"], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(project_root), "commit", "-m", "base"], capture_output=True, check=True)
    (project_root / "ROADMAP.md").write_text("modified")
    runtime = _seed_staged_vita(project_root)

    state: dict = {}
    decision = {"kind": "opportunity", "capability_id": "deployment"}
    outcome = {
        "status": "BLOCKED",
        "failure_class": "EVIDENCE_REQUIRED",
        "retry_eligible_this_run": False,
        "detail": "Deployment safety check failed",
        "evidence": {"slug": "neolife-vita-squares", "reasons": ["dirty"], "external_effect_attempted": False},
    }
    _park_deployment_if_stalled(decision, outcome, state, project_root)
    persisted_state = dict(state)
    from commander.identity import save_state, load_state
    save_state(persisted_state, runtime=runtime)

    from commander.evidence import _filter_parked_deployments
    filtered = _filter_parked_deployments(
        ["neolife-vita-squares"], project_root, runtime,
    )
    assert filtered == []


def test_parked_deployment_unparks_when_tree_changes(tmp_path):
    from commander.operating_loop import _park_deployment_if_stalled

    project_root = tmp_path / "repo"
    project_root.mkdir()
    import subprocess
    subprocess.run(["git", "-C", str(project_root), "init"], capture_output=True, check=True)
    (project_root / "ROADMAP.md").write_text("dirty")
    subprocess.run(["git", "-C", str(project_root), "add", "ROADMAP.md"], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(project_root), "commit", "-m", "base"], capture_output=True, check=True)
    (project_root / "ROADMAP.md").write_text("modified")
    runtime = _seed_staged_vita(project_root)

    state: dict = {}
    decision = {"kind": "opportunity", "capability_id": "deployment"}
    outcome = {
        "status": "BLOCKED",
        "failure_class": "EVIDENCE_REQUIRED",
        "retry_eligible_this_run": False,
        "detail": "Deployment safety check failed",
        "evidence": {"slug": "neolife-vita-squares", "reasons": ["dirty"], "external_effect_attempted": False},
    }
    _park_deployment_if_stalled(decision, outcome, state, project_root)

    from commander.identity import save_state
    save_state(state, runtime=runtime)

    subprocess.run(["git", "-C", str(project_root), "add", "ROADMAP.md"], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(project_root), "commit", "-m", "clean"], capture_output=True, check=True)

    from commander.evidence import _filter_parked_deployments
    filtered = _filter_parked_deployments(
        ["neolife-vita-squares"], project_root, runtime,
    )
    assert filtered == ["neolife-vita-squares"]


def test_parked_deployment_recovers_when_commitment_receipt_is_missing(tmp_path):
    import hashlib
    import subprocess

    project_root = tmp_path / "repo"
    project_root.mkdir()
    subprocess.run(["git", "-C", str(project_root), "init"], capture_output=True, check=True)
    (project_root / ".git" / "info" / "exclude").write_text("runtime/\n")
    (project_root / "neolife-vita-squares.html").write_text("staged revision")
    source_hash = hashlib.sha256((project_root / "neolife-vita-squares.html").read_bytes()).hexdigest()
    runtime = project_root / "runtime"
    from commander.identity import save_state
    save_state({"deployment_parked": {"neolife-vita-squares": {
        "slug": "neolife-vita-squares",
        "source_file": "neolife-vita-squares.html",
        "staged_content_sha256": source_hash,
        "blocker_paths": ["ROADMAP.md"],
    }}}, runtime=runtime)

    from commander.evidence import _filter_parked_deployments
    assert _filter_parked_deployments(["neolife-vita-squares"], project_root, runtime) == ["neolife-vita-squares"]

    from commander.procedure import _parked_staged_work
    work = _parked_staged_work(
        project_root, {"neolife-vita-squares": {
            "source_file": "neolife-vita-squares.html",
            "staged_content_sha256": source_hash,
        }},
    )
    assert work and work["source_file"] == "neolife-vita-squares.html"


def test_deployment_safety_remains_fail_closed(tmp_path):
    """The deployment safety gate must never be weakened: it still rejects
    unexpected working-tree changes regardless of parking state."""
    project_root = tmp_path / "repo"
    project_root.mkdir()
    import subprocess
    subprocess.run(["git", "-C", str(project_root), "init"], capture_output=True, check=True)
    (project_root / "legit.html").write_text("ok")
    (project_root / "untracked.py").write_text("suspicious")
    subprocess.run(["git", "-C", str(project_root), "add", "legit.html"], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(project_root), "commit", "-m", "base"], capture_output=True, check=True)
    (project_root / "legit.html").write_text("modified")

    from commander.procedure import _deployment_safety
    safety = _deployment_safety(
        project_root, "test-slug", {"legit.html", "neolife-vita-squares.html"}
    )
    assert safety["ok"] is False
    assert any("untracked.py" in r for r in safety["reasons"])


def test_no_public_effect_on_safety_failure():
    """A deployment safety failure must never reach external effect."""
    outcome = {
        "status": "BLOCKED",
        "failure_class": "EVIDENCE_REQUIRED",
        "retry_eligible_this_run": False,
        "detail": "Deployment safety check failed",
        "evidence": {
            "ok": False, "reasons": ["dirty"],
            "external_effect_attempted": False,
        },
    }
    assert outcome["evidence"]["external_effect_attempted"] is False
    assert outcome["status"] == "BLOCKED"


def test_parked_staged_commitment_remains_intact(tmp_path):
    """A parked deployment must never discard or modify the CONFIRMED product_page
    commitment. The product_page:740 commitment stays CONFIRMED regardless of
    deployment parking."""
    runtime = tmp_path / "runtime"
    _write_ledger(runtime, [{
        "commitment_id": "levnytt:product_page:740", "status": "CONFIRMED",
        "capability_id": "product_page", "project_id": "levnytt",
        "resolution_reason": repr({
            "gate_passed": True, "slug": "neolife-vita-squares",
            "source_file": "neolife-vita-squares.html",
            "staged_content_sha256": "abc",
            "image": "/images/neolife-vita-squares.jpg",
        }),
        "resolved_at": "2026-09-10T16:00:00+02:00",
    }, {
        "commitment_id": "levnytt:deployment:deployment:staged",
        "status": "OPEN", "kind": "unverified_external_effect",
        "capability_id": "deployment", "project_id": "levnytt",
        "action": "deploy", "reason": "staged",
        "executor_id": "deployment", "metadata": {},
        "recorded_at": "2026-09-10T22:00:00+02:00",
    }])
    from commander.operating_loop import _escalate_if_non_retryable
    decision = {"kind": "opportunity", "capability_id": "deployment",
                "commitment_id": "levnytt:deployment:deployment:staged"}
    outcome = {
        "status": "BLOCKED",
        "failure_class": "EVIDENCE_REQUIRED",
        "retry_eligible_this_run": False,
        "detail": "Deployment safety check failed",
        "evidence": {"slug": "neolife-vita-squares", "external_effect_attempted": False},
    }
    _escalate_if_non_retryable(decision, outcome, runtime)
    from app.commander.commitment_ledger import commitment_records
    records = {r["commitment_id"]: r for r in commitment_records(runtime)}
    assert records["levnytt:product_page:740"]["status"] == "CONFIRMED"


def test_alternative_work_proceeds_when_deployment_parked():
    """When deployment is parked, the decision layer must proceed past priority 3
    (deployment) to lower priorities (product_backlog, etc.)."""
    from commander import decision as decision_model

    evidence = {
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
        "product_backlog": [{"code": "740", "product_name": "Vita Squares",
                              "slug": "neolife-vita-squares", "coverage": "MENTIONED_ONLY"}],
    }
    d = decision_model.decide(evidence, [], [])
    assert d["kind"] == "product_backlog"
    assert d["capability_id"] == "product_page"


def test_deployment_selected_when_not_parked():
    """When staged_awaiting_deployment is non-empty and deployment is not parked,
    the decision layer must select deployment before product backlog."""
    from commander import decision as decision_model

    evidence = {
        "runtime_capability_availability": {
            "content_improvement": {"executable_now": False},
            "content_production": {"executable_now": False},
        },
        "content_improvement_opportunities": {"opportunities": []},
        "seo_intelligence": {"opportunity_pool": {"exhausted": True}, "next_eligible_keywords": []},
        "staged_awaiting_deployment": ["neolife-vita-squares"],
        "pending_deployment_verification": None,
        "distribution": {
            "execution_eligibility": {"executable_now": False},
            "distribution_candidates": [],
        },
        "measurement_freshness": {"fresh": True},
        "product_backlog": [{"code": "740", "product_name": "Vita Squares",
                              "slug": "neolife-vita-squares", "coverage": "MENTIONED_ONLY"}],
    }
    d = decision_model.decide(evidence, [], [])
    assert d["kind"] == "opportunity"
    assert d["capability_id"] == "deployment"


def test_empty_staged_params_are_safe(tmp_path):
    from commander.evidence import _filter_parked_deployments
    assert _filter_parked_deployments([], tmp_path, tmp_path) == []


def test_no_parked_deployments_returns_unfiltered(tmp_path):
    runtime = tmp_path / "runtime"
    from commander.identity import save_state
    save_state({"deployment_parked": {}}, runtime=runtime)
    from commander.evidence import _filter_parked_deployments
    assert _filter_parked_deployments(["slug"], tmp_path, runtime) == ["slug"]
