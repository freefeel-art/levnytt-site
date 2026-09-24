"""Regression tests for the dedicated Commander's Hermes environment wiring."""

from __future__ import annotations

import os

from commander import neolife_backoffice as backoffice
from commander import run


def test_dedicated_entrypoint_loads_hermes_repository_environment(monkeypatch, tmp_path):
    hermes_root = tmp_path / "hermes"
    hermes_root.mkdir()
    (hermes_root / ".env").write_text(
        "NEOLIFE_BACKOFFICE_COUNTRY_CODE=test-country\n"
        "NEOLIFE_BACKOFFICE_ID=test-id\n"
        "NEOLIFE_BACKOFFICE_PIN=test-pin\n",
        encoding="utf-8",
    )
    missing_shared = tmp_path / "missing-shared.env"

    monkeypatch.setattr(run, "_HERMES_ROOT", hermes_root)
    monkeypatch.setenv("HERMES_CONTROL_REPOSITORY", str(hermes_root))
    monkeypatch.setenv("HERMES_ENV_FILE", str(missing_shared))
    for name in backoffice.REQUIRED_ENV_VARS:
        monkeypatch.delenv(name, raising=False)

    original_cwd = os.getcwd()
    try:
        run._prepare_path()

        assert backoffice.credentials_present() == {
            name: True for name in backoffice.REQUIRED_ENV_VARS
        }
        summary = backoffice._redacted_credential_summary()
        assert set(summary.values()) == {"populated"}
        assert all(value not in repr(summary)
                   for value in ("test-country", "test-id", "test-pin"))
        assert os.environ["HERMES_CONTROL_REPOSITORY"] == str(hermes_root)
    finally:
        os.chdir(original_cwd)
