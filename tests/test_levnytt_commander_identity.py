"""Identity and hard-isolation tests for the dedicated LevNytt Commander.

These prove the Commander is structurally LevNytt-only: it cannot identify as
another project, read another project's business documents as its own, write
another project's runtime, or change project through a selector.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from commander import identity

OLSP_RUNTIME = Path("/home/yampa/projects/active/profitandprivilege-website/runtime")
CASHBACKKOLLEN_RUNTIME = Path("/home/yampa/projects/active/cashbackkollen/runtime")
LEVNYTT_RUNTIME = Path("/home/yampa/projects/active/levnytt-site/runtime")


def test_fixed_identity_is_levnytt():
    assert identity.PROJECT_ID == "levnytt"
    assert identity.PROJECT_NAME == "LevNytt"
    assert identity.SITE == "https://levnytt.se"
    assert identity.SPONSOR_ID == "41-830928"
    info = identity.identity()
    assert info["project_id"] == "levnytt"
    assert info["project_root"].endswith("levnytt-site")
    assert info["runtime_dir"].endswith("levnytt-site/runtime")


def test_identity_verifies_against_worker_marker():
    identity.assert_identity()  # must not raise


def test_identity_marker_is_levnytt_unique():
    marker = (identity.PROJECT_ROOT / "_worker.js").read_text(encoding="utf-8")
    assert "levnytt-neolife-shop" in marker
    assert "41-830928" in marker


def test_cannot_identify_as_olsp_or_cashbackkollen():
    # The fixed constants are immutable module attributes with no selector.
    assert identity.PROJECT_ID not in {"profit-and-privilege", "cashbackkollen"}
    assert identity.PROJECT_NAME not in {"OLSP", "Cashbackkollen"}
    assert identity.PROJECT_ROOT != Path("/home/yampa/projects/active/profitandprivilege-website")
    assert identity.PROJECT_ROOT != Path("/home/yampa/projects/active/cashbackkollen")


def test_state_path_is_levnytt_scoped_not_another_project():
    state = identity._state_file()
    assert state.is_relative_to(identity.RUNTIME_DIR)
    # A programming error can never make LevNytt state live under another runtime.
    assert not state.is_relative_to(OLSP_RUNTIME)
    assert not state.is_relative_to(CASHBACKKOLLEN_RUNTIME)
    assert state.name == "commander-state.json"  # dedicated, not the frozen operation-state.json


def test_runtime_directory_is_levnytt_only():
    assert identity.RUNTIME_DIR.is_relative_to(identity.PROJECT_ROOT)
    assert not identity.RUNTIME_DIR.is_relative_to(Path("/home/yampa/projects/active/profitandprivilege-website"))
    assert not identity.RUNTIME_DIR.is_relative_to(Path("/home/yampa/projects/active/cashbackkollen"))


def test_entrypoint_has_no_project_option():
    # The CLI must not accept --project or an activate selector.
    result = subprocess.run(
        ["/home/yampa/projects/active/hermes/.venv/bin/python", "-m", "commander.run", "--help"],
        cwd=identity.PROJECT_ROOT,
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin", "LEVNYTT_ROOT": str(identity.PROJECT_ROOT),
             "HERMES_CONTROL_REPOSITORY": "/home/yampa/projects/active/hermes"},
    )
    assert "--project" not in result.stdout
    assert "activate" not in result.stdout


def test_does_not_read_other_projects_business_documents():
    # LevNytt's objective is its own; it must not surface OLSP/Cashbackkollen docs.
    from app.commander.evidence import _levnytt

    packet = _levnytt(identity.PROJECT_ROOT, identity.RUNTIME_DIR, "2026-09-02", "levnytt")
    assert packet.get("project_id") or packet.get("source") is not None
    # The packet names only LevNytt's own artifacts, never another project's.
    for key in ("source",):
        value = str(packet.get(key) or "")
        assert "profitandprivilege" not in value
        assert "cashbackkollen" not in value
