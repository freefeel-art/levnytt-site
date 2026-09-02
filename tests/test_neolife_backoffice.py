"""Tests for the LevNytt NeoLife regional distributor back-office provider.

These prove the provider matches the real Swedish distributor login
(``se.neolifeshop.com/login.php`` → ``reseller_admin/login``) without any Owner
credentials: the three-field payload construction (Landskod/ID/Pinkod) with no
secret leakage, redirect-based login success/failure recognition,
expired-session re-authentication, and the ZERO/VERIFIED/UNAVAILABLE
distinction. The HTTP transport is faked only where the real network cannot be
reached without credentials; the login-page fixture is a real page excerpt.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from commander import neolife_backoffice as nb

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _reseller_login_html() -> str:
    return (FIXTURES / "neolife-reseller-login.txt").read_text(encoding="utf-8")


class _Cookies:
    def __init__(self, values: dict[str, str]):
        self._values = values

    def get_dict(self):
        return dict(self._values)


class _Response:
    def __init__(self, *, text="", status_code=200, headers=None, url="", cookies=None):
        self.text = text
        self.status_code = status_code
        self.headers = headers or {}
        self.url = url or "https://se.neolifeshop.com/"
        self.cookies = cookies or _Cookies({})


# ── payload construction (three real fields, no leak) ────────────────────────


def test_login_payload_uses_real_field_names():
    payload = nb._build_login_payload("41", "12345678", "9999")
    assert payload == {
        "login[country_code]": "41",
        "login[id]": "12345678",
        "login[pincode]": "9999",
    }


def test_required_env_vars_are_the_three_distributor_fields():
    assert set(nb.REQUIRED_ENV_VARS) == {
        "NEOLIFE_BACKOFFICE_COUNTRY_CODE",
        "NEOLIFE_BACKOFFICE_ID",
        "NEOLIFE_BACKOFFICE_PIN",
    }


def test_credentials_present_reports_booleans_only(monkeypatch):
    monkeypatch.delenv("NEOLIFE_BACKOFFICE_COUNTRY_CODE", raising=False)
    monkeypatch.delenv("NEOLIFE_BACKOFFICE_ID", raising=False)
    monkeypatch.delenv("NEOLIFE_BACKOFFICE_PIN", raising=False)
    assert nb.credentials_present() == {
        "NEOLIFE_BACKOFFICE_COUNTRY_CODE": False,
        "NEOLIFE_BACKOFFICE_ID": False,
        "NEOLIFE_BACKOFFICE_PIN": False,
    }
    assert nb.all_credentials_present() is False


def test_secret_values_never_appear_in_records(monkeypatch):
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_COUNTRY_CODE", "41")
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_ID", "SUPERSECRETID")
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_PIN", "SUPERSECRETPIN")
    summary = nb._redacted_credential_summary()
    assert set(summary.values()) <= {"missing", "populated"}
    assert "SUPERSECRET" not in repr(summary)
    monkeypatch.setattr(nb.requests, "get", lambda *a, **k: _Response(text=_reseller_login_html(), cookies=_Cookies({"visitorid": "1"})))
    monkeypatch.setattr(nb.requests, "post", lambda *a, **k: _Response(status_code=302, headers={"Location": "https://se.neolifeshop.com/login.php?error"}))
    result = nb._login("41", "SUPERSECRETID", "SUPERSECRETPIN", timeout=1)
    assert "SUPERSECRET" not in json.dumps(result, default=str)


# ── login success / failure recognition (redirect-based) ─────────────────────


def test_login_success_is_redirect_away_from_login():
    ok = _Response(status_code=302, headers={"Location": "https://se.neolifeshop.com/plugin/neolife_shop_in_shop/reseller_admin/dashboard"})
    assert nb._login_success(ok) is True
    fail = _Response(status_code=302, headers={"Location": "https://se.neolifeshop.com/login.php?error=1"})
    assert nb._login_success(fail) is False


def test_login_failure_when_returned_to_login(monkeypatch):
    monkeypatch.setattr(nb.requests, "get", lambda *a, **k: _Response(text=_reseller_login_html(), cookies=_Cookies({"visitorid": "1"})))
    monkeypatch.setattr(nb.requests, "post", lambda *a, **k: _Response(status_code=302, headers={"Location": "https://se.neolifeshop.com/login.php?error=1"}))
    result = nb._login("41", "id", "pin")
    assert result["status"] == nb.AUTH_FAILURE


def test_login_success_establishes_session(monkeypatch):
    monkeypatch.setattr(nb.requests, "get", lambda *a, **k: _Response(text=_reseller_login_html(), cookies=_Cookies({"visitorid": "1"})))
    monkeypatch.setattr(nb.requests, "post", lambda *a, **k: _Response(status_code=302, headers={"Location": "https://se.neolifeshop.com/plugin/neolife_shop_in_shop/reseller_admin/"}))
    result = nb._login("41", "id", "pin")
    assert result["status"] == nb.VERIFIED
    assert result["cookies"]  # session cookies captured


# ── login-page detection / report parsing ────────────────────────────────────


def test_looks_like_reseller_login_page():
    assert nb._looks_like_login_page(_reseller_login_html()) is True
    assert nb._looks_like_login_page("<html><body>dashboard</body></html>") is False


def test_parse_counts_server_rendered_table():
    html = "<table><thead><tr><th>h</th></tr></thead><tbody><tr><td>1</td></tr><tr><td>2</td></tr></tbody></table>"
    assert nb._parse_counts(html)["count"] == 2


def test_parse_counts_empty_grid_is_zero():
    html = "<div class='k-grid'><table><tbody><tr><td class='k-no-data'>No records</td></tr></tbody></table></div>"
    assert nb._parse_counts(html)["count"] == 0


def test_parse_counts_no_report_container_is_none():
    assert nb._parse_counts("<html><body>not a report</body></html>")["count"] is None


def test_extract_turnover_from_dashboard():
    html = '<span class="pv-amount">PV: 123</span><span class="total">1 824,00</span>'
    assert nb._extract_turnover(html) == {"personal_volume": 123, "turnover": "1 824,00"}
    assert nb._extract_turnover("<html>no dashboard</html>") is None


def test_count_order_rows_excludes_header_row():
    html = (
        "<table><tr><td>IDOrdernummer</td><td>Datum</td></tr>"
        "<tr><td>479091</td><td>2026-08-14</td></tr>"
        "<tr><td>430564</td><td>2025-10-27</td></tr></table>"
    )
    assert nb._count_order_rows(html) == 2


def test_parse_surface_client_rendered_is_unavailable():
    html = '<div id="app">{{ order.label }} {{ order.invoiceNo }}</div><script>var app = new Vue()</script>'
    assert nb._is_client_rendered(html) is True
    parsed = nb._parse_surface(html, "commission_invoices")
    assert parsed["status"] == nb.UNAVAILABLE


# ── ZERO vs VERIFIED vs UNAVAILABLE + re-auth + isolation ────────────────────


def test_collect_missing_credentials_is_not_zero(tmp_path, monkeypatch):
    monkeypatch.delenv("NEOLIFE_BACKOFFICE_COUNTRY_CODE", raising=False)
    monkeypatch.delenv("NEOLIFE_BACKOFFICE_ID", raising=False)
    monkeypatch.delenv("NEOLIFE_BACKOFFICE_PIN", raising=False)
    record = nb.collect(tmp_path)
    assert record["status"] == nb.MISSING_CREDENTIALS
    assert record["status"] != nb.ZERO


def test_authenticated_client_side_surfaces_are_unavailable_not_zero(tmp_path, monkeypatch):
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_COUNTRY_CODE", "41")
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_ID", "id")
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_PIN", "pin")
    monkeypatch.setattr(nb, "_login", lambda *a, **k: {"status": nb.VERIFIED, "cookies": {"sid": "1"}, "detail": "ok"})
    # All real surfaces are client-side Vue templates or empty: nothing is zero.
    monkeypatch.setattr(
        nb, "_fetch",
        lambda url, cookies, timeout=30: {"ok": True, "denied": False, "status_code": 200,
                                          "html": '<div>{{ order.label }}</div><script>new Vue()</script>'},
    )
    record = nb.collect(tmp_path)
    assert record["status"] == nb.UNAVAILABLE
    assert record["status"] != nb.ZERO
    assert all(d["status"] != nb.ZERO for d in record["datasets"].values())


def test_expired_session_triggers_reauthentication(tmp_path, monkeypatch):
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_COUNTRY_CODE", "41")
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_ID", "id")
    monkeypatch.setenv("NEOLIFE_BACKOFFICE_PIN", "pin")
    nb._save_session(tmp_path, {"cookies": {"sid": "old"}, "acquired_at": "x", "expired": False})
    # Simulate a known reporting surface to exercise the re-auth path.
    monkeypatch.setattr(nb, "REPORTING_SURFACES", ({"path": "/reports/orders", "kind": "orders", "label": "orders"},))

    login_calls = {"count": 0}
    fetch_calls = {"count": 0}

    def fake_login(*a, **k):
        login_calls["count"] += 1
        return {"status": nb.VERIFIED, "cookies": {"sid": "new"}, "detail": "ok"}

    def fake_fetch(url, cookies, timeout=30):
        fetch_calls["count"] += 1
        if fetch_calls["count"] == 1:
            return {"ok": False, "denied": True, "status_code": 302, "html": "", "detail": "session expired"}
        return {"ok": True, "denied": False, "status_code": 200,
                "html": "<table><tr><td>479091</td><td>2026-08-14</td></tr></table>"}

    monkeypatch.setattr(nb, "_login", fake_login)
    monkeypatch.setattr(nb, "_fetch", fake_fetch)

    record = nb.collect(tmp_path)
    assert login_calls["count"] == 1
    assert record["status"] == nb.VERIFIED


def test_session_path_is_scoped_to_the_passed_runtime(tmp_path):
    path = nb._session_path(tmp_path)
    assert path.is_relative_to(tmp_path)
    assert "neolife-backoffice" in path.parts
    assert not str(path).startswith("/home/yampa/projects/active/profitandprivilege-website")
    assert not str(path).startswith("/home/yampa/projects/active/cashbackkollen")


def test_session_stores_only_cookies_and_timestamps(tmp_path):
    nb._save_session(tmp_path, {"cookies": {"sid": "1"}, "acquired_at": "t", "expired": False})
    raw = (nb._session_path(tmp_path)).read_text(encoding="utf-8")
    assert "pincode" not in raw.lower()
    assert "login[id]" not in raw
