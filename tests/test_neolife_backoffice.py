"""Tests for the LevNytt NeoLife back-office evidence provider.

These prove the credential boundary is honest and safe: missing credentials are
reported as MISSING_CREDENTIALS (never a zero), credential values never leak
into any returned record, and the four-way outcome classification is correct.
No network is involved; the HTTP-dependent branches are exercised only through
the deterministic classification helpers.
"""

from __future__ import annotations

from pathlib import Path

from commander import neolife_backoffice as nb


def test_required_env_vars_are_the_defined_convention():
    assert set(nb.REQUIRED_ENV_VARS) == {
        "NEOLIFE_BACKOFFICE_LOGIN",
        "NEOLIFE_BACKOFFICE_PASSWORD",
        "NEOLIFE_BACKOFFICE_URL",
    }


def test_credentials_present_reports_booleans_only(monkeypatch):
    monkeypatch.delenv("NEOLIFE_BACKOFFICE_LOGIN", raising=False)
    monkeypatch.delenv("NEOLIFE_BACKOFFICE_PASSWORD", raising=False)
    monkeypatch.delenv("NEOLIFE_BACKOFFICE_URL", raising=False)
    assert nb.credentials_present() == {
        "NEOLIFE_BACKOFFICE_LOGIN": False,
        "NEOLIFE_BACKOFFICE_PASSWORD": False,
        "NEOLIFE_BACKOFFICE_URL": False,
    }
    assert nb.all_credentials_present() is False


def test_collect_missing_credentials_is_not_zero(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("NEOLIFE_BACKOFFICE_LOGIN", raising=False)
    monkeypatch.delenv("NEOLIFE_BACKOFFICE_PASSWORD", raising=False)
    monkeypatch.delenv("NEOLIFE_BACKOFFICE_URL", raising=False)
    record = nb.collect(tmp_path)
    assert record["status"] == nb.MISSING_CREDENTIALS
    assert record["conversions"] is None and record["commissions"] is None
    # A missing credential boundary is never recorded as a measured zero.
    assert record["status"] != nb.ZERO


def test_collect_without_endpoint_paths_is_unavailable(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_LOGIN", "secret-login")
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_PASSWORD", "secret-password")
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_URL", "https://backoffice.example")
    record = nb.collect(tmp_path)
    assert record["status"] == nb.UNAVAILABLE
    # Credential values never appear in the returned record.
    blob = repr(record)
    assert "secret-login" not in blob
    assert "secret-password" not in blob


def test_redacted_credential_view_never_exposes_values(monkeypatch):
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_LOGIN", "supersecret-login-value")
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_PASSWORD", "supersecret-password-value")
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_URL", "https://x.example")
    summary = nb._redacted_credential_summary()
    assert set(summary.values()) <= {"missing", "populated"}
    assert "supersecret" not in repr(summary)


def test_extract_counts_classification():
    assert nb._extract_counts({"conversions": 3, "commissions": 120}) == {"conversions": 3, "commissions": 120}
    assert nb._extract_counts({"customers": 0}) == {"conversions": 0, "commissions": None}
    assert nb._extract_counts([1, 2, 3]) == {"conversions": 3, "commissions": None}
    assert nb._extract_counts({"unrelated": True}) == {"conversions": None, "commissions": None}


def test_session_never_stored_when_missing_credentials(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("NEOLIFE_BACKOFFICE_LOGIN", raising=False)
    monkeypatch.delenv("NEOLIFE_BACKOFFICE_PASSWORD", raising=False)
    monkeypatch.delenv("NEOLIFE_BACKOFFICE_URL", raising=False)
    nb.collect(tmp_path)
    assert not (tmp_path / "neolife-backoffice" / "session.json").exists()
