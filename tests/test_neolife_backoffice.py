"""Tests for the LevNytt NeoLife back-office provider (real ASP.NET mechanism).

These prove the provider matches the factual NeoLife back office without any
Owner credentials: the two-step anti-CSRF login, LoginName/Password payload
construction with no secret leakage, login success/failure recognition,
expired-session re-authentication, and the ZERO/VERIFIED/UNAVAILABLE
distinction. The HTTP transport is faked only where the real network cannot be
reached without credentials; the parsed inputs are real page artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from commander import neolife_backoffice as nb

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _login_html() -> str:
    return (FIXTURES / "neolife-login-page.txt").read_text(encoding="utf-8")


class _Cookies:
    def __init__(self, values: dict[str, str]):
        self._values = values

    def get_dict(self):
        return dict(self._values)


class _Response:
    def __init__(self, *, text="", status_code=200, json_body=None, url="", cookies=None):
        self.text = text
        self.status_code = status_code
        self._json = json_body
        self.url = url or "https://myoffice.neolife.com/dashboard"
        self.cookies = cookies or _Cookies({})

    def json(self):
        if self._json is None:
            raise ValueError("no json")
        return self._json


# ── CSRF token extraction ────────────────────────────────────────────────────


def test_extract_verification_token_from_real_login_page():
    token = nb.extract_verification_token(_login_html())
    assert token, "real login page must yield an anti-CSRF token"
    assert token != ""


def test_extract_verification_token_missing_returns_none():
    assert nb.extract_verification_token("") is None
    assert nb.extract_verification_token("<html><body>no form</body></html>") is None


def test_token_input_is_outside_form_and_still_found():
    # The real page places the token input AFTER </form>; the extractor must
    # search the whole page, not just the form element.
    html = '<html><form></form><input name="__RequestVerificationToken" type="hidden" value="TOKEN123"/></html>'
    assert nb.extract_verification_token(html) == "TOKEN123"


# ── payload construction without leaking secrets ─────────────────────────────


def test_login_payload_uses_real_field_names():
    payload = nb._build_login_payload("the-login", "the-password")
    assert payload == {"LoginName": "the-login", "Password": "the-password"}
    assert "__RequestVerificationToken" not in payload  # token is a header, not body


def test_login_headers_carry_antiforgery_token():
    headers = nb._build_login_headers("TOKEN")
    assert headers["__RequestVerificationToken"] == "TOKEN"
    assert headers["Content-Type"] == "application/json; charset=utf-8"


def test_secret_values_never_appear_in_records(monkeypatch):
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_LOGIN", "SUPERSECRETLOGIN")
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_PASSWORD", "SUPERSECRETPASSWORD")
    summary = nb._redacted_credential_summary()
    assert set(summary.values()) <= {"missing", "populated"}
    assert "SUPERSECRET" not in repr(summary)
    # A login result record must not contain the credentials, even when the
    # credential values are exercised end-to-end through a faked transport.
    monkeypatch.setattr(nb.requests, "get", lambda *a, **k: _Response(text=_login_html(), cookies=_Cookies({"s": "1"})))
    monkeypatch.setattr(nb.requests, "post", lambda *a, **k: _Response(status_code=200, json_body={"Status": False, "ErrorMessage": "bad"}))
    result = nb._login("SUPERSECRETLOGIN", "SUPERSECRETPASSWORD", timeout=1)
    blob = json.dumps(result, default=str)
    assert "SUPERSECRET" not in blob


# ── login success / failure recognition ──────────────────────────────────────


def test_login_success_recognized_from_status_flag():
    ok = _Response(status_code=200, json_body={"Status": True, "RedirectUrl": "/"})
    assert nb._login_success(ok) is True
    fail = _Response(status_code=200, json_body={"Status": False, "ErrorMessage": "bad"})
    assert nb._login_success(fail) is False


def test_login_failure_when_token_missing(monkeypatch):
    monkeypatch.setattr(nb.requests, "get", lambda *a, **k: _Response(text="<html>no token</html>"))
    result = nb._login("login", "password")
    assert result["status"] == nb.AUTH_FAILURE


def test_login_rejection_returns_auth_failure(monkeypatch):
    monkeypatch.setattr(
        nb.requests, "get",
        lambda *a, **k: _Response(text=_login_html(), cookies=_Cookies({"ASP.NET_SessionId": "s"})),
    )
    monkeypatch.setattr(
        nb.requests, "post",
        lambda *a, **k: _Response(status_code=200, json_body={"Status": False, "ErrorMessage": "invalid credentials"}),
    )
    result = nb._login("login", "password")
    assert result["status"] == nb.AUTH_FAILURE


# ── HTML / Kendo report parsing ──────────────────────────────────────────────


def test_extract_grid_read_url_detects_kendo_datasource():
    html = (
        '<script>$("#grid").kendoGrid({ dataSource: { transport: { read: '
        '{ url: "/orders/read", dataType: "json" } } } });</script>'
    )
    assert nb.extract_grid_read_url(html) == "https://myoffice.neolife.com/orders/read"


def test_extract_grid_read_url_absent_for_server_rendered():
    assert nb.extract_grid_read_url("<html><table><tbody><tr><td>x</td></tr></tbody></table></html>") is None


def test_parse_counts_server_rendered_table():
    html = "<table><thead><tr><th>h</th></tr></thead><tbody><tr><td>1</td></tr><tr><td>2</td></tr></tbody></table>"
    assert nb._parse_counts(html)["count"] == 2


def test_parse_counts_empty_grid_is_zero():
    html = "<div class='k-grid'><table><tbody><tr><td class='k-no-data'>No records</td></tr></tbody></table></div>"
    assert nb._parse_counts(html)["count"] == 0


def test_parse_counts_no_report_container_is_none():
    assert nb._parse_counts("<html><body>not a report</body></html>")["count"] is None


def test_parse_json_counts():
    assert nb._parse_json_counts({"Data": [1, 2, 3]})["count"] == 3
    assert nb._parse_json_counts({"Total": 7})["count"] == 7
    assert nb._parse_json_counts([1, 2])["count"] == 2
    assert nb._parse_json_counts({"unrelated": True})["count"] is None


def test_looks_like_login_page():
    assert nb._looks_like_login_page(_login_html()) is True
    assert nb._looks_like_login_page("<html><body>dashboard</body></html>") is False


# ── ZERO vs VERIFIED vs UNAVAILABLE ──────────────────────────────────────────


def test_collect_missing_credentials_is_not_zero(tmp_path, monkeypatch):
    monkeypatch.delenv("NEOLIFE_BACKOFFICE_LOGIN", raising=False)
    monkeypatch.delenv("NEOLIFE_BACKOFFICE_PASSWORD", raising=False)
    record = nb.collect(tmp_path)
    assert record["status"] == nb.MISSING_CREDENTIALS
    assert record["status"] != nb.ZERO


def test_expired_session_triggers_reauthentication(tmp_path, monkeypatch):
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_LOGIN", "login")
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_PASSWORD", "password")
    # Seed a VALID persisted session so the initial auth is skipped and the
    # only re-authentication is the one triggered by a denied report fetch.
    nb._save_session(tmp_path, {"cookies": {"old": "1"}, "acquired_at": "x", "expired": False})

    login_calls = {"count": 0}
    fetch_calls = {"count": 0}

    def fake_login(login, password, timeout=30):
        login_calls["count"] += 1
        return {"status": nb.VERIFIED, "cookies": {"Auth": "1"}, "detail": "ok"}

    def fake_fetch(url, cookies, timeout=30):
        fetch_calls["count"] += 1
        if fetch_calls["count"] == 1:
            # First surface fetch: session denied -> triggers re-auth.
            return {"ok": False, "denied": True, "status_code": 302, "html": "", "detail": "session expired"}
        # After re-auth, all surfaces return server-rendered rows.
        return {"ok": True, "denied": False, "status_code": 200,
                "html": "<table><tbody><tr><td>a</td></tr></tbody></table>"}

    monkeypatch.setattr(nb, "_login", fake_login)
    monkeypatch.setattr(nb, "_fetch", fake_fetch)

    record = nb.collect(tmp_path)
    assert login_calls["count"] == 1  # one autonomous re-authentication
    assert record["status"] == nb.VERIFIED
    assert all(d["count"] == 1 for d in record["datasets"].values())


def test_authenticated_zero_reports_are_zero(tmp_path, monkeypatch):
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_LOGIN", "login")
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_PASSWORD", "password")
    monkeypatch.setattr(nb, "_login", lambda *a, **k: {"status": nb.VERIFIED, "cookies": {"Auth": "1"}, "detail": "ok"})
    monkeypatch.setattr(
        nb, "_fetch",
        lambda url, cookies, timeout=30: {"ok": True, "denied": False, "status_code": 200,
                                          "html": "<table><tbody></tbody></table>"},
    )
    record = nb.collect(tmp_path)
    assert record["status"] == nb.ZERO
    assert all(d["status"] == nb.ZERO for d in record["datasets"].values())


def test_unparseable_report_is_unavailable_not_zero(tmp_path, monkeypatch):
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_LOGIN", "login")
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_PASSWORD", "password")
    monkeypatch.setattr(nb, "_login", lambda *a, **k: {"status": nb.VERIFIED, "cookies": {"Auth": "1"}, "detail": "ok"})
    monkeypatch.setattr(
        nb, "_fetch",
        lambda url, cookies, timeout=30: {"ok": True, "denied": False, "status_code": 200,
                                          "html": "<html><body>not a report</body></html>"},
    )
    record = nb.collect(tmp_path)
    assert record["status"] == nb.UNAVAILABLE
    assert record["status"] != nb.ZERO


# ── LevNytt-only runtime isolation ───────────────────────────────────────────


def test_session_path_is_scoped_to_the_passed_runtime(tmp_path):
    path = nb._session_path(tmp_path)
    assert path.is_relative_to(tmp_path)
    assert "neolife-backoffice" in path.parts
    # Never under another project's runtime directory.
    assert not str(path).startswith("/home/yampa/projects/active/profitandprivilege-website")
    assert not str(path).startswith("/home/yampa/projects/active/cashbackkollen")


def test_session_stores_only_cookies_and_timestamps(tmp_path):
    nb._save_session(tmp_path, {"cookies": {"Auth": "1"}, "acquired_at": "t", "expired": False})
    raw = (nb._session_path(tmp_path)).read_text(encoding="utf-8")
    assert "password" not in raw.lower()
    assert "LoginName" not in raw
