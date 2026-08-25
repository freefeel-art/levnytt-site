from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import types
from pathlib import Path
from types import SimpleNamespace

from app.commander.procedure_contract import normalize_execution_receipt


ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "levnytt_content_improvement_procedure", ROOT / "commander" / "procedure.py"
)
procedure = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = procedure
_spec.loader.exec_module(procedure)


def _git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _ctx(tmp_path: Path) -> SimpleNamespace:
    repo = tmp_path / "repo"
    runtime = repo / "runtime"
    (repo / "content" / "data").mkdir(parents=True)
    runtime.mkdir(parents=True)
    _git("init", "-q", cwd=repo)
    _git("config", "user.email", "test@example.com", cwd=repo)
    _git("config", "user.name", "Test", cwd=repo)
    return SimpleNamespace(working_repository=repo, runtime_directory=runtime)


def _opportunity() -> dict:
    return {
        "opportunity_id": "content-improvement:existing",
        "slug": "existing",
        "canonical_url": "https://levnytt.se/existing",
        "public_path": "/existing",
        "source_file": "existing.html",
        "title": "Befintlig guide",
        "research_topic": "befintlig guide",
        "gsc": {"impressions": 42, "clicks": 0, "ctr": 0, "position": 12.0},
    }


def _rendered() -> str:
    return (
        '<!doctype html><html lang="sv"><head>'
        '<link rel="canonical" href="https://levnytt.se/existing">'
        '</head><body><p>Sponsor-ID: 41-830928</p>'
        '<a href="https://se.neolifeshop.com/i/shop.html?sponsor=41-830928" '
        'rel="nofollow sponsored noopener noreferrer">NeoLife</a>'
        '<h2>Källor</h2><a href="https://www.livsmedelsverket.se/example">Källa</a>'
        '<script src="/assets/js/levnytt-rebuild.js?v=abc123"></script>'
        '</body></html>'
    )


def _install_scribe(monkeypatch) -> None:
    scribe = types.ModuleType("agents.scribe.run")
    scribe.run = lambda brief, project_id: {
        "status": "READY_FOR_HANDOFF",
        "title_or_subject": "Befintlig guide",
        "sections_or_messages": [
            {"heading_or_subject": "Aktuell evidens", "body": "Saklig svensk text. " * 120},
            {"heading_or_subject": "Vad det innebär", "body": "Ytterligare saklig text. " * 80},
        ],
        "claims": [{"claim": "grounded"}],
    }
    agents = types.ModuleType("agents")
    package = types.ModuleType("agents.scribe")
    agents.scribe = package
    package.run = scribe
    monkeypatch.setitem(sys.modules, "agents", agents)
    monkeypatch.setitem(sys.modules, "agents.scribe", package)
    monkeypatch.setitem(sys.modules, "agents.scribe.run", scribe)


def test_exact_existing_page_is_revised_and_receipt_conforms(tmp_path: Path, monkeypatch):
    ctx = _ctx(tmp_path)
    source = ctx.working_repository / "existing.html"
    source.write_text("<html><h1>Original</h1></html>", encoding="utf-8")
    data = ctx.working_repository / "content" / "data" / "production-pages.json"
    data.write_text('{"pages": [{"path": "/existing"}]}', encoding="utf-8")
    _git("add", "existing.html", "content/data/production-pages.json", cwd=ctx.working_repository)
    _git("commit", "-m", "seed", cwd=ctx.working_repository)

    monkeypatch.setattr(procedure, "_content_improvement_target", lambda action: _opportunity())
    monkeypatch.setattr(
        procedure,
        "_topic_scribe_evidence",
        lambda current, keyword, slug: (
            [{"url": "https://www.livsmedelsverket.se/example"}],
            {"sufficiency": {"passed": True}},
        ),
    )
    monkeypatch.setattr(procedure, "_content_gate", lambda keyword, result: (True, []))
    monkeypatch.setattr(
        procedure,
        "_render_improved_production_page",
        lambda *args: (_rendered(), '{"pages": [{"path": "/existing"}]}\n'),
    )
    monkeypatch.setattr(procedure, "_final_publication_gate", lambda html: (True, []))
    _install_scribe(monkeypatch)

    action = {
        "capability": "content_improvement",
        "summary": "Improve exact content-improvement:existing from current GSC evidence.",
    }
    raw = procedure.LevNyttProcedure().execute(ctx, action)
    receipt = normalize_execution_receipt(
        raw, project_id="levnytt", capability_id="content_improvement", action=action,
    )

    assert receipt["status"] == "SUCCEEDED"
    assert receipt["selected_opportunity_id"] == "content-improvement:existing"
    assert source.read_text(encoding="utf-8") == _rendered()
    assert not (ctx.working_repository / "content" / "articles" / "existing.html").exists()
    assert receipt["evidence"]["source_file"] == "existing.html"
    assert receipt["evidence"]["renderer"] == "scripts/site_renderer.py"
    assert procedure.LevNyttProcedure().verify(ctx, action, receipt) is True


def test_missing_exact_opportunity_id_fails_closed_without_writes(tmp_path: Path, monkeypatch):
    ctx = _ctx(tmp_path)
    monkeypatch.setattr(procedure, "_content_improvement_target", lambda action: None)

    result = procedure.LevNyttProcedure().execute(
        ctx, {"capability": "content_improvement", "summary": "Improve something."},
    )

    assert result["status"] == "BLOCKED"
    assert result["failure_class"] == "EVIDENCE_REQUIRED"
    assert result["retry_eligible_this_run"] is False
    assert result["evidence"]["external_effect_attempted"] is False
    assert list(ctx.working_repository.glob("*.html")) == []


def test_insufficient_research_blocks_before_scribe_or_source_change(tmp_path: Path, monkeypatch):
    ctx = _ctx(tmp_path)
    source = ctx.working_repository / "existing.html"
    source.write_text("original", encoding="utf-8")
    monkeypatch.setattr(procedure, "_content_improvement_target", lambda action: _opportunity())
    monkeypatch.setattr(
        procedure,
        "_topic_scribe_evidence",
        lambda *args: ([], {"sufficiency": {"passed": False, "notes": ["no independent source"]}}),
    )

    result = procedure.LevNyttProcedure().execute(
        ctx,
        {"capability": "content_improvement", "summary": "Use content-improvement:existing."},
    )

    assert result["status"] == "BLOCKED"
    assert result["failure_class"] == "EVIDENCE_REQUIRED"
    assert source.read_text(encoding="utf-8") == "original"


def test_final_publication_gate_prevents_staging(tmp_path: Path, monkeypatch):
    ctx = _ctx(tmp_path)
    source = ctx.working_repository / "existing.html"
    source.write_text("original", encoding="utf-8")
    monkeypatch.setattr(procedure, "_content_improvement_target", lambda action: _opportunity())
    monkeypatch.setattr(
        procedure,
        "_topic_scribe_evidence",
        lambda *args: ([{"url": "https://authority.example"}], {"sufficiency": {"passed": True}}),
    )
    monkeypatch.setattr(procedure, "_content_gate", lambda *args: (True, []))
    monkeypatch.setattr(procedure, "_render_improved_production_page", lambda *args: ("unsafe", "{}\n"))
    monkeypatch.setattr(procedure, "_final_publication_gate", lambda html: (False, ["missing_disclosure"]))
    _install_scribe(monkeypatch)

    result = procedure.LevNyttProcedure().execute(
        ctx,
        {"capability": "content_improvement", "summary": "Use content-improvement:existing."},
    )

    assert result["status"] == "BLOCKED"
    assert result["failure_class"] == "RECOVERABLE_QA_REJECTION"
    assert result["evidence"]["attempts"] == 3
    assert source.read_text(encoding="utf-8") == "original"


def test_current_renderer_preserves_canonical_identity_and_publication_date(tmp_path: Path, monkeypatch):
    ctx = _ctx(tmp_path)
    data = ctx.working_repository / "content" / "data" / "production-pages.json"
    data.write_text(json.dumps({"pages": [{
        "url": "https://levnytt.se/existing",
        "path": "/existing",
        "family": "informational-article",
        "language": "sv",
        "source_file": "existing.html",
        "date_published": "2026-06-15",
        "date_modified": "2026-06-15",
    }]}), encoding="utf-8")
    calls = []

    class Renderer:
        @staticmethod
        def extract_document(url, html, source_file, root):
            calls.append(("extract", url, source_file))
            return {"title": "Ny", "h1": "Ny", "head_html": "", "body_html": "ny"}

        @staticmethod
        def render_page(page, root):
            calls.append(("render", dict(page)))
            return _rendered()

    monkeypatch.setattr(procedure, "_load_site_renderer", lambda: Renderer)
    monkeypatch.setattr(procedure, "_assemble_page", lambda *args: "draft")

    rendered, payload = procedure._render_improved_production_page(
        ctx.working_repository,
        _opportunity(),
        {"title_or_subject": "Ny", "sections_or_messages": []},
        {"sufficiency": {"passed": True}},
    )
    updated = json.loads(payload)["pages"][0]

    assert rendered == _rendered()
    assert [call[0] for call in calls] == ["extract", "render"]
    assert updated["url"] == "https://levnytt.se/existing"
    assert updated["path"] == "/existing"
    assert updated["source_file"] == "existing.html"
    assert updated["date_published"] == "2026-06-15"
    assert updated["date_modified"] != "2026-06-15"


def test_real_phase1_renderer_preserves_sponsor_disclosure_and_final_gate():
    production = json.loads(
        (ROOT / "content" / "data" / "production-pages.json").read_text(encoding="utf-8")
    )
    previous = next(page for page in production["pages"] if page["path"] == "/direktforsaljning-fakta")
    opportunity = {
        "opportunity_id": "content-improvement:direktforsaljning-fakta",
        "slug": "direktforsaljning-fakta",
        "canonical_url": previous["url"],
        "public_path": previous["path"],
        "source_file": previous["source_file"],
        "title": previous["title"],
        "research_topic": "direktförsäljning fakta",
    }
    paragraphs = " ".join(
        "Direktförsäljning behöver bedömas med tydliga kriterier och oberoende källor."
        for _ in range(45)
    )
    scribe = {
        "title_or_subject": "Direktförsäljning fakta – aktuell guide",
        "sections_or_messages": [
            {"heading_or_subject": "Vad modellen innebär", "body": paragraphs},
            {"heading_or_subject": "Så granskar du uppgifter", "body": paragraphs},
        ],
        "claims": [{"claim": "grounded"}],
    }
    research = {
        "sufficiency": {"passed": True},
        "claims": [{
            "source_url": "https://www.konsumentverket.se/example",
            "source_type": "AUTHORITY",
            "source_title": "Konsumentverket",
        }],
    }

    rendered, payload = procedure._render_improved_production_page(
        ROOT, opportunity, scribe, research,
    )
    updated = next(page for page in json.loads(payload)["pages"] if page["path"] == previous["path"])
    final_ok, issues = procedure._final_publication_gate(rendered)

    assert final_ok, issues
    assert updated["url"] == previous["url"]
    assert updated["source_file"] == previous["source_file"]
    assert updated["date_published"] == previous["date_published"]
    assert "Sponsor-ID 41-830928" in rendered
    assert "sponsor=41-830928" in rendered
    assert 'rel="nofollow noopener noreferrer sponsored"' in rendered
    assert "levnytt-rebuild.js?v=" in rendered


def test_pending_live_verification_resumes_on_later_invocation(tmp_path: Path, monkeypatch):
    ctx = _ctx(tmp_path)
    _git("commit", "--allow-empty", "-m", "published", cwd=ctx.working_repository)
    marker = ctx.runtime_directory / "commander" / procedure.PENDING_DEPLOYMENT_FILENAME
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps({
        "slug": "existing",
        "commit": procedure._git_head(ctx.working_repository),
        "pushed": True,
        "files": ["existing.html"],
    }), encoding="utf-8")
    monkeypatch.setattr(procedure, "_verify_live", lambda slug, wait_seconds: True)

    result = procedure.LevNyttProcedure().execute(
        ctx, {"capability": "deployment", "summary": "Resume pending deployment."},
    )

    assert result["status"] == "SUCCEEDED"
    assert result["evidence"]["recovered_pending_deployment"] is True
    assert not marker.exists()
