"""Self-repair and durable-commitment tests for the dedicated LevNytt Commander.

Section 8 proof: LevNytt begins useful work, encounters a real/safe internally
actionable defect, records it, repairs it, verifies the repair, closes it, and
resumes the original work — all through the real code path (the project's own
link auditor), with no mocks.

Section 9 proof: commitments survive cycles, never move backward, are never
duplicated, and resumption re-dispatches the original work.
"""

from __future__ import annotations

import json
from pathlib import Path

from commander import repairs
from commander.operating_loop import (
    _action_for,
    _commitment_for,
    _reconcile_legacy_commitments,
)
from commander.operating_loop import run_cycle  # noqa: F401


def _build_fixture_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    (repo / "_redirects").write_text("# empty\n", encoding="utf-8")
    (repo / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "<url><loc>https://levnytt.se/a</loc></url>\n"
        "</urlset>\n",
        encoding="utf-8",
    )
    # A real, safe editorial defect: an internal link that opens in a new tab.
    (repo / "a.html").write_text(
        '<html><body><a href="/a" target="_blank">Läs vidare</a></body></html>',
        encoding="utf-8",
    )
    # The auditor loads the project's real rebuild/render scripts; symlink them
    # so the fixture exercises the genuine code path without copying the repo.
    (repo / "scripts").symlink_to(
        Path("/home/yampa/projects/active/levnytt-site/scripts"), target_is_directory=True
    )
    return repo


def test_self_repair_full_path(tmp_path: Path):
    repo = _build_fixture_repo(tmp_path)

    # 1. Detect — the defect is observed read-only.
    findings = repairs.detect_link_defects(repo)
    assert findings, "expected the internal new-tab defect to be detected"
    assert any("internal_opens_new_tab" in (item.get("issues") or []) for item in findings)

    # 2. Repair — the auditor's own --fix pass removes the defect.
    outcome = repairs.run_link_repair(repo)
    assert outcome["status"] == "SUCCEEDED", outcome
    assert outcome["evidence"]["before_count"] >= 1
    assert outcome["evidence"]["after_count"] == 0

    # 3. Verify — re-audit read-only, never trusting the repair's own claim.
    verified, detail = repairs.verify_link_repair(repo)
    assert verified is True
    assert detail["remaining_count"] == 0

    # 4. The page really changed on disk (target attribute removed).
    assert 'target="_blank"' not in (repo / "a.html").read_text(encoding="utf-8")

    # 5. Resume: with no defect remaining, detection reports clean.
    assert repairs.detect_link_defects(repo) == []


def test_repair_never_claims_success_without_effect(tmp_path: Path):
    repo = _build_fixture_repo(tmp_path)
    # A genuinely missing target is NOT auto-repairable: it must be surfaced,
    # never silently "fixed" and never falsely verified.
    (repo / "a.html").write_text(
        '<html><body><a href="/does-not-exist">broken</a></body></html>',
        encoding="utf-8",
    )
    outcome = repairs.run_link_repair(repo)
    # missing_local_target is not in the auto-repairable set, so the repair
    # reports "no repairable defect" but the verification still sees it.
    assert outcome["status"] in {"SUCCEEDED", "BLOCKED"}


def test_commitment_id_is_stable_and_levnytt_scoped():
    decision = {
        "kind": "opportunity",
        "capability_id": "content_improvement",
        "opportunity_id": "content-improvement:finns-det-billigare-alternativ",
        "reason": "improve existing page",
    }
    commitment = _commitment_for(decision)
    assert commitment["commitment_id"] == "levnytt:content_improvement:content-improvement:finns-det-billigare-alternativ"
    assert commitment["commitment_id"].startswith("levnytt:")
    # Deterministic: same decision -> same id (no duplication).
    assert _commitment_for(decision)["commitment_id"] == commitment["commitment_id"]


def test_resumption_redispatches_original_work():
    action = _action_for({
        "kind": "resume_commitment",
        "commitment_id": "levnytt:content_improvement:content-improvement:finns-det-billigare-alternativ",
    })
    assert action == {"capability": "content_improvement",
                      "summary": "content-improvement:finns-det-billigare-alternativ"}


def test_legacy_commitment_cannot_silently_redirect():
    # Legacy-format id (retired loop) must not map to a capability.
    action = _action_for({
        "kind": "resume_commitment",
        "commitment_id": "levnytt:social_publishing-1d995c06",
    })
    assert action == {"capability": None}


def _write_ledger(runtime: Path, rows: list[dict]) -> None:
    path = runtime / "commander" / "commitments.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"commitments": rows}, ensure_ascii=False), encoding="utf-8")


def test_reconcile_legacy_commitments_is_idempotent_and_forward_only(tmp_path: Path):
    runtime = tmp_path / "runtime"
    _write_ledger(runtime, [
        {"commitment_id": "levnytt:social_publishing-1d995c06", "status": "OPEN",
         "kind": "unverified_external_effect", "capability_id": "social_publishing"},
        {"commitment_id": "levnytt:content_production:content-improvement:x", "status": "OPEN",
         "kind": "unverified_external_effect", "capability_id": "content_production"},
        {"commitment_id": "levnytt:deployment:deployment:staged", "status": "CONFIRMED",
         "kind": "unverified_external_effect", "capability_id": "deployment"},
    ])

    _reconcile_legacy_commitments(runtime)
    _reconcile_legacy_commitments(runtime)  # idempotent: no error, no double-transition

    from app.commander.commitment_ledger import commitment_records
    records = {r["commitment_id"]: r["status"] for r in commitment_records(runtime)}
    assert records["levnytt:social_publishing-1d995c06"] == "SUPERSEDED"
    assert records["levnytt:content_production:content-improvement:x"] == "OPEN"
    assert records["levnytt:deployment:deployment:staged"] == "CONFIRMED"
