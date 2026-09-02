"""LevNytt-owned NeoLife distributor back-office reporting provider.

Read-only collection of the one outcome the rest of the LevNytt funnel cannot
see: attributable NeoLife customer/distributor conversions, orders and
commission/revenue.

This provider is built to the real **regional Swedish NeoLife distributor
login**, which the Owner actually uses. Factual discovery (no credentials
required) established:

* The distributor login lives on the Swedish shop at
  ``https://se.neolifeshop.com/login.php`` ("Logga in som återförsäljare") —
  **not** the international ``myoffice.neolife.com`` portal.
* The form POSTs to ``/plugin/neolife_shop_in_shop/reseller_admin/login``
  (``method="POST"``, standard form-urlencoded, no JSON, no anti-CSRF token)
  with exactly three fields:
      Landskod  -> ``login[country_code]``   (numeric; Sweden = 41)
      ID nummer -> ``login[id]``
      Pinkod    -> ``login[pincode]``
* On success the server redirects to the reseller-admin area; on failure it
  returns to the login page. The authenticated session is the shop's cookies.

Binding constraints:

* Credentials come only from environment — ``NEOLIFE_BACKOFFICE_COUNTRY_CODE``,
  ``NEOLIFE_BACKOFFICE_ID`` and ``NEOLIFE_BACKOFFICE_PIN``. Values are never
  printed, logged, or persisted.
* Only the authenticated session cookies are persisted under the LevNytt
  runtime. A denied/expired session triggers one autonomous re-authentication.
* Outcomes are classified truthfully into ``MISSING_CREDENTIALS``,
  ``AUTH_FAILURE``, ``UNAVAILABLE``, ``ZERO`` or ``VERIFIED``. A missing
  credential boundary is never a measured zero, and a failed parse is never a
  zero.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

PROJECT_ID = "levnytt"
BASE_URL = "https://se.neolifeshop.com"
LOGIN_PAGE_URL = BASE_URL + "/login.php"
RESELLER_LOGIN_URL = BASE_URL + "/plugin/neolife_shop_in_shop/reseller_admin/login"

_ENV_COUNTRY_CODE = "NEOLIFE_BACKOFFICE_COUNTRY_CODE"
_ENV_ID = "NEOLIFE_BACKOFFICE_ID"
_ENV_PIN = "NEOLIFE_BACKOFFICE_PIN"
REQUIRED_ENV_VARS = (_ENV_COUNTRY_CODE, _ENV_ID, _ENV_PIN)

MISSING_CREDENTIALS = "MISSING_CREDENTIALS"
AUTH_FAILURE = "AUTH_FAILURE"
UNAVAILABLE = "UNAVAILABLE"
ZERO = "ZERO"
VERIFIED = "VERIFIED"

_SESSION_FILENAME = "neolife-backoffice" + os.sep + "session.json"

# Factual reporting surfaces of the regional reseller account, discovered from
# the authenticated account (2026-09-02). Orders are server-rendered; the
# dashboard exposes Personal Volume and turnover server-side; the invoice pages
# are Vue.js templates whose rows are loaded client-side (see _parse_surface).
REPORTING_SURFACES: tuple[dict[str, str], ...] = (
    {"path": "/account_history.php", "kind": "orders", "label": "orders"},
    {"path": "/account.php", "kind": "turnover", "label": "turnover / personal volume"},
    {"path": "/account.php?sub_page=commission_invoices", "kind": "commission_invoices", "label": "commission invoices"},
    {"path": "/account.php?sub_page=invoices", "kind": "purchase_invoices", "label": "purchase invoices"},
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _session_path(runtime: Path) -> Path:
    return Path(runtime) / _SESSION_FILENAME


# ── credentials (values never leave this module) ─────────────────────────────


def _read_env() -> dict[str, str]:
    return {
        _ENV_COUNTRY_CODE: os.getenv(_ENV_COUNTRY_CODE, "").strip(),
        _ENV_ID: os.getenv(_ENV_ID, "").strip(),
        _ENV_PIN: os.getenv(_ENV_PIN, "").strip(),
    }


def credentials_present() -> dict[str, bool]:
    """Whether each required secret exists and is non-empty. Never returns the
    values themselves."""
    env = _read_env()
    return {name: bool(env[name]) for name in REQUIRED_ENV_VARS}


def all_credentials_present() -> bool:
    return all(credentials_present().values())


def _redacted_credential_summary() -> dict[str, str]:
    return {name: ("populated" if present else "missing") for name, present in credentials_present().items()}


# ── session persistence (cookies only, never credentials) ────────────────────


def _load_session(runtime: Path) -> dict[str, Any]:
    path = _session_path(runtime)
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _save_session(runtime: Path, session: dict[str, Any]) -> None:
    path = _session_path(runtime)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".session.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(session, handle, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise


def _session_fresh(session: dict[str, Any]) -> bool:
    if not session.get("cookies"):
        return False
    if session.get("expired") is True:
        return False
    return True


# ── the real regional distributor login ──────────────────────────────────────


def _build_login_payload(country_code: str, distributor_id: str, pin: str) -> dict[str, str]:
    """The exact form fields the real distributor login posts."""
    return {
        "login[country_code]": country_code,
        "login[id]": distributor_id,
        "login[pincode]": pin,
    }


def _login(country_code: str, distributor_id: str, pin: str, *, timeout: int = 30) -> dict[str, Any]:
    """Perform the real regional distributor login and return a factual result.

    Returns ``{status, cookies, detail}`` with status in
    AUTH_FAILURE / UNAVAILABLE / VERIFIED. Credential values are used only in
    the HTTP call and never enter the returned record.
    """
    # Step 1: fetch the login page to obtain the shop's initial cookies.
    try:
        page = requests.get(LOGIN_PAGE_URL, timeout=timeout, allow_redirects=True)
    except requests.RequestException as error:
        return {"status": UNAVAILABLE, "cookies": {}, "detail": f"login page unreachable: {type(error).__name__}"}

    initial_cookies = page.cookies.get_dict()

    # Step 2: post the three distributor fields (form-urlencoded).
    try:
        response = requests.post(
            RESELLER_LOGIN_URL,
            data=_build_login_payload(country_code, distributor_id, pin),
            cookies=initial_cookies,
            timeout=timeout,
            allow_redirects=False,
        )
    except requests.RequestException as error:
        return {"status": UNAVAILABLE, "cookies": {}, "detail": f"login request failed: {type(error).__name__}"}

    cookies = {**initial_cookies, **response.cookies.get_dict()}
    if _login_success(response):
        return {"status": VERIFIED, "cookies": cookies, "detail": "authenticated reseller session established"}
    return {"status": AUTH_FAILURE, "cookies": cookies, "detail": _login_error(response) or "login rejected"}


def _login_success(response: Any) -> bool:
    """The regional login redirects away from the login page on success."""
    if response.status_code in (301, 302, 303, 307, 308):
        location = response.headers.get("Location", "")
        if location and "login" not in location.lower():
            return True
    return False


def _login_error(response: Any) -> str:
    location = response.headers.get("Location", "")
    if "login" in location.lower():
        return "login rejected (returned to the login page)"
    if response.status_code >= 400:
        return f"login returned HTTP {response.status_code}"
    return f"login returned HTTP {response.status_code}"


# ── authenticated report fetching ────────────────────────────────────────────


def _looks_like_login_page(html: str) -> bool:
    return "login[pincode]" in html and "login[id]" in html


def _fetch(url: str, cookies: dict[str, str], *, timeout: int = 30) -> dict[str, Any]:
    """GET one authenticated URL and report whether it reached a report page,
    was denied (session expired), or failed."""
    try:
        response = requests.get(url, cookies=cookies, timeout=timeout, allow_redirects=True)
    except requests.RequestException as error:
        return {"ok": False, "denied": False, "status_code": None, "html": "", "detail": f"request failed: {type(error).__name__}"}

    if response.status_code in (401, 403) or response.url.startswith(LOGIN_PAGE_URL):
        return {"ok": False, "denied": True, "status_code": response.status_code, "html": "", "detail": "session expired/denied"}

    if _looks_like_login_page(response.text):
        return {"ok": False, "denied": True, "status_code": response.status_code, "html": response.text, "detail": "session expired/denied"}

    if response.status_code >= 400:
        return {"ok": False, "denied": False, "status_code": response.status_code, "html": "", "detail": f"report returned HTTP {response.status_code}"}

    return {"ok": True, "denied": False, "status_code": response.status_code, "html": response.text, "detail": None}


def _parse_counts(html: str) -> dict[str, int | None]:
    """Best-effort extraction of a numeric record count from a report page.

    Distinguishes three states conservatively: a report container with data
    rows -> the row count; a report container with no data rows -> 0 (measured
    zero); no report container -> None (unparseable, never a zero). Vue.js
    template placeholder rows (``{{ ... }}``) are not real data and are skipped.
    """
    if not html:
        return {"count": None}
    soup = BeautifulSoup(html, "html.parser")
    data_rows = 0
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if not tds:
            continue
        cell_text = " ".join(td.get_text() for td in tds)
        if "{{" in cell_text:
            continue
        classes = list(tr.get("class") or [])
        for td in tds:
            classes.extend(td.get("class") or [])
        if "k-no-data" in classes:
            continue
        data_rows += 1
    if data_rows:
        return {"count": data_rows}
    if soup.find("table") is not None or soup.select_one(".k-grid"):
        return {"count": 0}
    return {"count": None}


def _is_client_rendered(html: str) -> bool:
    """True when a page's data is rendered client-side (Vue.js template) rather
    than server-rendered — its rows exist only as placeholders, so a raw fetch
    cannot observe real records."""
    return "{{" in html and ("vue" in html.lower() or "v-" in html.lower())


_TURNOVER_PATTERN = re.compile(r"PV:\s*(\d+)")
_TOTAL_SPAN = ".total"


def _extract_turnover(html: str) -> dict[str, Any] | None:
    """Extract the dashboard's Personal Volume and turnover from server-rendered
    HTML. The account dashboard renders ``<span class="pv-amount">PV: N</span>``
    and ``<span class="total"><amount></span>`` server-side."""
    soup = BeautifulSoup(html or "", "html.parser")
    pv_el = soup.select_one(".pv-amount")
    total_el = soup.select_one(_TOTAL_SPAN)
    if pv_el is None or total_el is None:
        return None
    pv_match = _TURNOVER_PATTERN.search(pv_el.get_text())
    if not pv_match:
        return None
    return {
        "personal_volume": int(pv_match.group(1)),
        "turnover": total_el.get_text(strip=True),
    }


def _count_order_rows(html: str) -> int | None:
    """Count real order rows on the order-history page.

    The order-history table renders its header with ``<td>`` too, so a plain row
    count over-counts by one. A real order row's first cell is a numeric order
    id; the header's first cell is the label ``IDOrdernummer``.
    """
    soup = BeautifulSoup(html or "", "html.parser")
    rows = 0
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if not tds:
            continue
        if tds[0].get_text(strip=True).isdigit():
            rows += 1
    return rows


def _parse_surface(html: str, kind: str) -> dict[str, Any]:
    """Parse one authenticated surface into a truthful dataset record.

    Returns ``{"status", "count", "value"}``. Client-side (Vue.js) surfaces are
    UNAVAILABLE rather than zero, because a raw fetch cannot see their records.
    """
    if kind == "turnover":
        value = _extract_turnover(html)
        if value is None:
            return {"status": UNAVAILABLE, "count": None, "value": None}
        return {"status": VERIFIED, "count": None, "value": value}

    if _is_client_rendered(html):
        return {"status": UNAVAILABLE, "count": None, "value": None, "detail": "client-side rendered; no server-visible records"}

    if kind == "orders":
        count = _count_order_rows(html)
        if count is None:
            return {"status": UNAVAILABLE, "count": None, "value": None, "detail": "report body could not be parsed"}
        return {"status": VERIFIED if count > 0 else ZERO, "count": count, "value": None}

    count = _parse_counts(html)["count"]
    if count is None:
        return {"status": UNAVAILABLE, "count": None, "value": None, "detail": "report body could not be parsed"}
    if count > 0:
        return {"status": VERIFIED, "count": count, "value": None}
    return {"status": ZERO, "count": 0, "value": None}


# ── the Commander-facing entrypoint ──────────────────────────────────────────


def collect(runtime: Path, *, timeout: int = 30) -> dict[str, Any]:
    """Collect attributable NeoLife conversion/order/commission evidence.

    Authenticates using the real three-field regional distributor login, then
    reads the configured reporting surfaces. Never raises; never logs or
    returns credential values.
    """
    base = {
        "schema": "neolife-backoffice-evidence-v1",
        "project_id": PROJECT_ID,
        "base_url": BASE_URL,
        "collected_at": _now(),
        "credentials": _redacted_credential_summary(),
    }

    if not all_credentials_present():
        return {
            **base,
            "status": MISSING_CREDENTIALS,
            "datasets": {},
            "limitations": [
                "NeoLife back-office credentials are not fully populated; this is a "
                "temporary configuration boundary, not a measured zero."
            ],
        }

    env = _read_env()
    session = _load_session(runtime)
    if not _session_fresh(session):
        session = {}

    if not session.get("cookies"):
        auth = _login(env[_ENV_COUNTRY_CODE], env[_ENV_ID], env[_ENV_PIN], timeout=timeout)
        if auth["status"] != VERIFIED:
            return {
                **base,
                "status": auth["status"],
                "datasets": {},
                "limitations": [auth["detail"]],
            }
        session = {"cookies": auth["cookies"], "acquired_at": _now(), "expired": False}
        _save_session(runtime, session)

    datasets: dict[str, Any] = {}
    reauthenticated = False
    for surface in REPORTING_SURFACES:
        kind = surface["kind"]
        url = BASE_URL + surface["path"]
        result = _fetch(url, session.get("cookies") or {}, timeout=timeout)

        if result.get("denied") and not reauthenticated:
            auth = _login(env[_ENV_COUNTRY_CODE], env[_ENV_ID], env[_ENV_PIN], timeout=timeout)
            if auth["status"] == VERIFIED:
                session = {"cookies": auth["cookies"], "acquired_at": _now(), "expired": False}
                _save_session(runtime, session)
                reauthenticated = True
                result = _fetch(url, session.get("cookies") or {}, timeout=timeout)

        if result.get("denied"):
            _save_session(runtime, {**session, "expired": True})
            datasets[kind] = {"status": AUTH_FAILURE, "count": None, "label": surface["label"]}
            continue

        if not result.get("ok"):
            datasets[kind] = {"status": UNAVAILABLE, "count": None, "label": surface["label"], "detail": result.get("detail")}
            continue

        parsed = _parse_surface(result["html"], kind)
        datasets[kind] = {"label": surface["label"], **parsed}

    statuses = [d["status"] for d in datasets.values()]
    if any(s == VERIFIED for s in statuses):
        overall = VERIFIED
    elif statuses and all(s == ZERO for s in statuses):
        overall = ZERO
    elif any(s == AUTH_FAILURE for s in statuses):
        overall = AUTH_FAILURE
    else:
        overall = UNAVAILABLE

    return {
        **base,
        "status": overall,
        "datasets": datasets,
        "limitations": [] if overall in (VERIFIED, ZERO) else [
            "One or more reporting surfaces could not be collected; no zero was fabricated."
        ],
    }
