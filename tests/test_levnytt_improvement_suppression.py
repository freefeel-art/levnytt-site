"""Tests for the content-improvement re-selection suppression."""

from __future__ import annotations

import json
from pathlib import Path

from commander.evidence import _recently_improved_slugs, _suppress_completed_improvements


def _write_commitments(runtime: Path, rows: list[dict]) -> None:
    p = runtime / "commander" / "commitments.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"commitments": rows}, ensure_ascii=False), encoding="utf-8")


def test_recently_improved_slugs_reads_confirmed_commitments(tmp_path: Path):
    _write_commitments(tmp_path, [
        {"commitment_id": "levnytt:content_improvement:content-improvement:cellmembran-funktion",
         "capability_id": "content_improvement", "status": "CONFIRMED",
         "resolved_at": "2026-09-02T20:00:34+00:00",
         "resolution_reason": "{'gate_passed': True, 'slug': 'cellmembran-funktion', 'source_file': 'x', 'staged_content_sha256': 'a', 'production_data_sha256': 'b'}"},
        {"commitment_id": "levnytt:measurement:no-opportunity",
         "capability_id": "measurement", "status": "CONFIRMED",
         "resolved_at": "2026-09-02T20:00:00+00:00", "resolution_reason": "refreshed"},
        {"commitment_id": "levnytt:content_improvement:content-improvement:old",
         "capability_id": "content_improvement", "status": "CONFIRMED",
         "resolved_at": "2025-01-01T00:00:00+00:00",
         "resolution_reason": "{'gate_passed': True, 'slug': 'old-page', 'source_file': 'x', 'staged_content_sha256': 'a', 'production_data_sha256': 'b'}"},
    ])
    slugs = _recently_improved_slugs(tmp_path)
    assert "cellmembran-funktion" in slugs
    assert "old-page" not in slugs  # outside the suppression window


def test_suppress_completed_improvements_removes_recent_slug():
    packet = {
        "content_improvement_opportunities": {
            "opportunities": [
                {"opportunity_id": "content-improvement:cellmembran-funktion", "slug": "cellmembran-funktion"},
                {"opportunity_id": "content-improvement:direktforsaljning-fakta", "slug": "direktforsaljning-fakta"},
            ],
        },
        "runtime_capability_availability": {
            "content_improvement": {"executable_now": True},
        },
    }
    runtime = Path("/nonexistent")  # suppression set supplied via monkeypatch-free path
    # Use a real temp runtime
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    _write_commitments(tmp, [
        {"commitment_id": "levnytt:content_improvement:content-improvement:cellmembran-funktion",
         "capability_id": "content_improvement", "status": "CONFIRMED",
         "resolved_at": "2026-09-02T20:00:34+00:00",
         "resolution_reason": "{'gate_passed': True, 'slug': 'cellmembran-funktion', 'source_file': 'x', 'staged_content_sha256': 'a', 'production_data_sha256': 'b'}"},
    ])
    out = _suppress_completed_improvements(packet, tmp)
    opps = out["content_improvement_opportunities"]["opportunities"]
    assert [o["slug"] for o in opps] == ["direktforsaljning-fakta"]
    assert out["runtime_capability_availability"]["content_improvement"]["executable_now"] is True
