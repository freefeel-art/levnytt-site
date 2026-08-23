from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from commander import procedure


def _ctx(tmp_path: Path) -> SimpleNamespace:
    repository = tmp_path / "site"
    runtime = tmp_path / "runtime"
    repository.mkdir()
    runtime.mkdir()
    return SimpleNamespace(working_repository=repository, runtime_directory=runtime)


def _completed(*, returncode: int = 0, stdout: str = "", stderr: str = "") -> SimpleNamespace:
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def test_unsupported_node_records_failed_attempt_without_zero_or_overwriting_snapshot(tmp_path, monkeypatch):
    ctx = _ctx(tmp_path)
    latest = ctx.runtime_directory / "intelligence" / procedure.CTA_LATEST_FILENAME
    latest.parent.mkdir(parents=True)
    original = {
        "status": "available",
        "fetched_at": "2026-08-17T08:00:00+00:00",
        "total_events": 2,
    }
    latest.write_text(json.dumps(original), encoding="utf-8")

    monkeypatch.setattr(procedure.shutil, "which", lambda name: f"/fake/{name}")
    monkeypatch.setattr(procedure.subprocess, "run", lambda *args, **kwargs: _completed(stdout="v20.19.2\n"))

    result = procedure._collect_cta_events(ctx)

    assert result["status"] == "unavailable"
    assert "total_events" not in result
    assert "Node 22 or newer" in result["diagnostic"]
    assert json.loads(latest.read_text(encoding="utf-8")) == original
    attempt = json.loads(
        (ctx.runtime_directory / "intelligence" / procedure.CTA_ATTEMPT_FILENAME).read_text(encoding="utf-8")
    )
    assert attempt["status"] == "unavailable"
    assert "total_events" not in attempt


def test_successful_wrangler_collection_persists_zero_as_observed_zero(tmp_path, monkeypatch):
    ctx = _ctx(tmp_path)
    monkeypatch.setattr(procedure.shutil, "which", lambda name: f"/fake/{name}")

    def run(command, **kwargs):
        if command[1:] == ["--version"]:
            return _completed(stdout="v22.22.2\n")
        if "COUNT(*) AS total_events" in command[-2]:
            return _completed(stdout=json.dumps([{"results": [{
                "total_events": 0,
                "shop_clicks": 0,
                "registration_clicks": 0,
            }]}]))
        return _completed(stdout=json.dumps([{"results": []}]))

    monkeypatch.setattr(procedure.subprocess, "run", run)
    result = procedure._collect_cta_events(ctx)

    assert result["status"] == "available"
    assert result["total_events"] == 0
    latest = json.loads(
        (ctx.runtime_directory / "intelligence" / procedure.CTA_LATEST_FILENAME).read_text(encoding="utf-8")
    )
    assert latest["status"] == "available"
    assert latest["total_events"] == 0


def test_gsc_success_and_cta_failure_is_truthful_partial_measurement(tmp_path, monkeypatch):
    ctx = _ctx(tmp_path)
    fetched_at = "2026-08-23T01:00:00+00:00"
    destination = ctx.runtime_directory / "intelligence" / "gsc-latest.json"
    destination.parent.mkdir(parents=True)
    destination.write_text(
        json.dumps({"site": procedure.GSC_PROPERTY, "fetched_at": "2026-08-22T01:00:00+00:00"}),
        encoding="utf-8",
    )
    def collect_gsc(*args, **kwargs):
        destination.write_text(
            json.dumps({"site": procedure.GSC_PROPERTY, "fetched_at": fetched_at}),
            encoding="utf-8",
        )
        return _completed(stdout="GSC collection complete")

    monkeypatch.setattr(procedure.subprocess, "run", collect_gsc)
    monkeypatch.setattr(
        procedure,
        "_collect_cta_events",
        lambda _ctx: {
            "status": "unavailable",
            "attempted_at": "2026-08-23T01:00:01+00:00",
            "diagnostic": "Wrangler provider unavailable",
        },
    )

    action = {"capability": "measurement", "summary": "Refresh measurement"}
    execution = procedure.LevNyttProcedure()._execute_measurement(ctx, action)

    assert execution["status"] == "PARTIAL"
    assert "No zero-event inference" in execution["detail"]
    assert "total_events" not in execution["evidence"]["sources"]["cta_d1"]
    assert execution["evidence"]["sources"]["gsc"]["fetched_at"] == fetched_at
    assert "diagnostic" not in execution["evidence"]["sources"]["gsc"]
    assert procedure.LevNyttProcedure().verify(ctx, action, execution) is True


def test_gsc_success_without_a_new_artifact_does_not_mask_cta_failure(tmp_path, monkeypatch):
    ctx = _ctx(tmp_path)
    destination = ctx.runtime_directory / "intelligence" / "gsc-latest.json"
    destination.parent.mkdir(parents=True)
    destination.write_text(
        json.dumps({"site": procedure.GSC_PROPERTY, "fetched_at": "2026-08-22T01:00:00+00:00"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(procedure.subprocess, "run", lambda *a, **k: _completed())
    monkeypatch.setattr(procedure, "_collect_cta_events", lambda _ctx: {
        "status": "unavailable", "attempted_at": "2026-08-23T01:00:00+00:00"
    })

    execution = procedure.LevNyttProcedure()._execute_measurement(
        ctx, {"capability": "measurement", "summary": "Refresh measurement"}
    )

    assert execution["status"] == "BLOCKED"
    assert execution["evidence"]["sources"]["gsc"]["status"] == "unavailable"
    assert procedure.LevNyttProcedure().verify(ctx, {}, execution) is False


def test_cta_counts_are_aggregated_beyond_the_recent_event_window(tmp_path, monkeypatch):
    ctx = _ctx(tmp_path)
    monkeypatch.setattr(procedure.shutil, "which", lambda name: f"/fake/{name}")

    def run(command, **kwargs):
        if command[1:] == ["--version"]:
            return _completed(stdout="v22.22.2\n")
        if "COUNT(*) AS total_events" in command[-2]:
            return _completed(stdout=json.dumps([{"results": [{
                "total_events": 147,
                "shop_clicks": 100,
                "registration_clicks": 47,
            }]}]))
        return _completed(stdout=json.dumps([{"results": [{"cta_id": "levnytt-neolife-shop"}]}]))

    monkeypatch.setattr(procedure.subprocess, "run", run)
    result = procedure._collect_cta_events(ctx)

    assert result["total_events"] == 147
    assert result["shop_clicks"] == 100
    assert result["registration_clicks"] == 47
    assert len(result["recent_events"]) == 1


def test_provider_diagnostic_is_bounded_and_redacts_common_secret_shapes():
    diagnostic = procedure._bounded_provider_diagnostic(
        "prefix " + ("x" * 600) + " token=super-secret-value"
    )
    assert len(diagnostic) <= 500
    assert "super-secret-value" not in diagnostic
    assert "[REDACTED]" in diagnostic


def test_levnytt_scribe_brief_uses_project_owned_swedish_instructions():
    brief = procedure._scribe_brief("vad är lutein", "vad-ar-lutein", [])

    assert brief["project"] == "levnytt"
    assert brief["language"] == "Swedish"
    assert brief["writer_provider"] == "openai"
    assert brief["writing_instruction_source"] == "docs/LEVNYTT-EDITORIAL-SYSTEM.md"
    assert "Write calm, direct Swedish" in brief["project_context"]
    assert "olsp-article" not in brief["project_context"]
