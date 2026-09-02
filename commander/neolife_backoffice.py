"""LevNytt-owned NeoLife distributor back-office reporting provider.

Read-only collection of the one outcome the rest of the LevNytt funnel cannot
see: attributable NeoLife customer/distributor conversions, orders and
commission/revenue. This replaces the generic provider that assumed a JSON
"reports" endpoint; it is built to match the real NeoLife back office, which
was discovered factually (no credentials required for the discovery):

* **Base URL (fixed):** ``https://myoffice.neolife.com`` — an ASP.NET MVC
  application (Microsoft-IIS/10.0 + ASP.NET Razor + RequireJS + RouteJs).
* **Two-step login.** ``GET /login`` returns a Razor form carrying
  ``LoginName``, ``Password`` and a hidden ``__RequestVerificationToken``
  (ASP.NET anti-CSRF token). The client then submits a **JSON POST to
  ``/login``** (``Content-Type: application/json``) with the serialized form,
  and with the token echoed in both the JSON body and the
  ``__RequestVerificationToken`` request header. Success is the JSON response
  ``{"Status": true, "RedirectUrl": ...}`` plus an established auth cookie.
* **Reporting surfaces are authenticated server-rendered HTML MVC pages**
  (Kendo UI grids), not a public JSON API. The factual routes are taken from
  the back office's RouteJs table (``routejs.axd``), reproduced below.

Binding constraints:

* Credentials come only from environment — ``NEOLIFE_BACKOFFICE_LOGIN`` and
  ``NEOLIFE_BACKOFFICE_PASSWORD``. The base URL is fixed and is **not** a
  required secret. Values are never printed, logged, or persisted.
* The authenticated session (cookies only) is persisted under the LevNytt
  runtime. A denied/expired session triggers one autonomous re-authentication
  before the collection is reported.
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
BASE_URL = "https://myoffice.neolife.com"
LOGIN_URL = BASE_URL + "/login"

_ENV_LOGIN = "NEOLIFE_BACKOFFICE_LOGIN"
_ENV_PASSWORD = "NEOLIFE_BACKOFFICE_PASSWORD"
REQUIRED_ENV_VARS = (_ENV_LOGIN, _ENV_PASSWORD)

MISSING_CREDENTIALS = "MISSING_CREDENTIALS"
AUTH_FAILURE = "AUTH_FAILURE"
UNAVAILABLE = "UNAVAILABLE"
ZERO = "ZERO"
VERIFIED = "VERIFIED"

_SESSION_FILENAME = "neolife-backoffice" + os.sep + "session.json"

# Factual reporting surfaces from the back office RouteJs table (routejs.axd):
#   url -> controller/action. Each is an authenticated HTML MVC page; the list
#   pages are Kendo UI grids. The provider fetches the HTML and, where the page
#   exposes a Kendo DataSource read endpoint, follows it — otherwise it parses
#   the server-rendered HTML.
REPORTING_SURFACES: tuple[dict[str, str], ...] = (
    {"path": "/new-customers", "kind": "new_customers", "label": "new customers (registrations)"},
    {"path": "/retail-customers", "kind": "retail_customers", "label": "retail customers"},
    {"path": "/preferred-customers", "kind": "preferred_customers", "label": "preferred customers"},
    {"path": "/personally-enrolled-team", "kind": "enrolled_distributors", "label": "personally enrolled team"},
    {"path": "/orders/1", "kind": "orders", "label": "orders"},
    {"path": "/history", "kind": "commission_history", "label": "commission history"},
    {"path": "/volumes", "kind": "volumes", "label": "volume"},
    {"path": "/retailmemberprofits", "kind": "retail_member_profits", "label": "retail member profits"},
    {"path": "/statements-report", "kind": "statements", "label": "statements (revenue)"},
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _session_path(runtime: Path) -> Path:
    return Path(runtime) / _SESSION_FILENAME


# ── credentials (values never leave this module) ─────────────────────────────


def _read_env() -> dict[str, str]:
    return {
        _ENV_LOGIN: os.getenv(_ENV_LOGIN, "").strip(),
        _ENV_PASSWORD: os.getenv(_ENV_PASSWORD, "").strip(),
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
    """A persisted session is reusable while it still carries cookies and has
    not yet been observed as expired."""
    if not session.get("cookies"):
        return False
    expired = session.get("expired")
    if expired is True:
        return False
    return True


# ── the real two-step ASP.NET login ──────────────────────────────────────────

_TOKEN_INPUT = re.compile(r'name=["\']__RequestVerificationToken["\'][^>]*value=["\']([^"\']+)', re.I)
_TOKEN_INPUT_ALT = re.compile(r'value=["\']([^"\']+)["\'][^>]*name=["\']__RequestVerificationToken', re.I)


def extract_verification_token(html: str) -> str | None:
    """Extract the ASP.NET anti-CSRF token from the /login HTML.

    Returns None when the token is absent — a caller must then treat the page
    as not being the real login form (AUTH_FAILURE, never a guessed token).
    """
    if not html:
        return None
    match = _TOKEN_INPUT.search(html) or _TOKEN_INPUT_ALT.search(html)
    if match:
        token = match.group(1).strip()
        return token or None
    # Fall back to attribute-order-agnostic parsing via BeautifulSoup.
    try:
        soup = BeautifulSoup(html, "html.parser")
        node = soup.find("input", attrs={"name": "__RequestVerificationToken"})
        if node is not None and node.get("value"):
            return str(node["value"]).strip()
    except Exception:
        return None
    return None


def _build_login_payload(login: str, password: str) -> dict[str, str]:
    """The exact JSON body the real client posts.

    The real client serializes the login ``<form>`` (``LoginName`` +
    ``Password``) and sends the anti-CSRF token as the
    ``__RequestVerificationToken`` *header* — the token input is rendered
    outside the form, so it is never part of the JSON body.
    """
    return {
        "LoginName": login,
        "Password": password,
    }


def _build_login_headers(token: str) -> dict[str, str]:
    """The request headers for the login POST: JSON content type plus the
    anti-CSRF token in the header ASP.NET validates for AJAX posts."""
    return {"__RequestVerificationToken": token, "Content-Type": "application/json; charset=utf-8"}


def _login(login: str, password: str, *, timeout: int = 30) -> dict[str, Any]:
    """Perform the real two-step login and return a factual result.

    Returns ``{status, cookies, detail}`` where status is one of
    AUTH_FAILURE / UNAVAILABLE / VERIFIED. Credentials are used only inside the
    HTTP calls and never enter the returned record.
    """
    # Step 1: fetch the login page to obtain the anti-CSRF token and any
    # initial session cookies.
    try:
        page = requests.get(LOGIN_URL, timeout=timeout, allow_redirects=True)
    except requests.RequestException as error:
        return {"status": UNAVAILABLE, "cookies": {}, "detail": f"login page unreachable: {type(error).__name__}"}

    token = extract_verification_token(page.text)
    if token is None:
        return {"status": AUTH_FAILURE, "cookies": {}, "detail": "login page did not expose an anti-CSRF token"}

    initial_cookies = page.cookies.get_dict()
    headers = _build_login_headers(token)
    payload = _build_login_payload(login, password)

    try:
        response = requests.post(
            LOGIN_URL, json=payload, headers=headers, cookies=initial_cookies,
            timeout=timeout, allow_redirects=False,
        )
    except requests.RequestException as error:
        return {"status": UNAVAILABLE, "cookies": {}, "detail": f"login request failed: {type(error).__name__}"}

    if response.status_code in (401, 403):
        return {"status": AUTH_FAILURE, "cookies": {}, "detail": "credentials rejected by the back office"}

    success = _login_success(response)
    cookies = {**initial_cookies, **response.cookies.get_dict()}
    if success:
        return {"status": VERIFIED, "cookies": cookies, "detail": "authenticated session established"}
    return {"status": AUTH_FAILURE, "cookies": cookies, "detail": _login_error(response) or "login returned failure status"}


def _login_success(response: Any) -> bool:
    """Factual success signal: the JSON ``Status`` flag (and an auth cookie).

    The real client treats ``response.Status == true`` as success. A
    non-JSON/5xx body is not success.
    """
    if response.status_code >= 400:
        return False
    try:
        body = response.json()
    except ValueError:
        return False
    return bool(body.get("Status")) if isinstance(body, dict) else False


def _login_error(response: Any) -> str:
    try:
        body = response.json()
    except ValueError:
        return f"login returned HTTP {response.status_code}"
    if isinstance(body, dict) and body.get("ErrorMessage"):
        return str(body["ErrorMessage"])[:300]
    return f"login returned HTTP {response.status_code}"


# ── authenticated report fetching ────────────────────────────────────────────

_KENDO_READ_URL = re.compile(
    r'transport\s*:\s*\{\s*read\s*:\s*\{[^}]*url\s*:\s*["\']([^"\']+)["\']', re.I | re.S
)
_KENDO_READ_URL_ALT = re.compile(
    r'read\s*:\s*\{\s*url\s*:\s*["\']([^"\']+)["\']', re.I | re.S
)


def extract_grid_read_url(html: str) -> str | None:
    """Detect a Kendo DataSource read (XHR) endpoint from an authenticated page.

    Returns None when the grid is server-rendered (or no grid config is found),
    in which case the caller falls back to parsing the HTML directly.
    """
    if not html:
        return None
    match = _KENDO_READ_URL.search(html) or _KENDO_READ_URL_ALT.search(html)
    if not match:
        return None
    url = match.group(1)
    if url.startswith("/"):
        return BASE_URL + url
    return url


def _looks_like_login_page(html: str) -> bool:
    return "loginbutton" in html and "LoginName" in html and "Password" in html


def _fetch(url: str, cookies: dict[str, str], *, timeout: int = 30) -> dict[str, Any]:
    """GET one authenticated URL and report whether it reached a report page,
    was denied (session expired), or failed."""
    try:
        response = requests.get(url, cookies=cookies, timeout=timeout, allow_redirects=True)
    except requests.RequestException as error:
        return {"ok": False, "denied": False, "status_code": None, "html": "", "detail": f"request failed: {type(error).__name__}"}

    # ASP.NET forms auth redirects to /login when the session is gone.
    if response.status_code in (401, 403) or response.url.startswith(LOGIN_URL):
        return {"ok": False, "denied": True, "status_code": response.status_code, "html": "", "detail": "session expired/denied"}

    if _looks_like_login_page(response.text):
        return {"ok": False, "denied": True, "status_code": response.status_code, "html": response.text, "detail": "session expired/denied"}

    if response.status_code >= 400:
        return {"ok": False, "denied": False, "status_code": response.status_code, "html": "", "detail": f"report returned HTTP {response.status_code}"}

    return {"ok": True, "denied": False, "status_code": response.status_code, "html": response.text, "detail": None}


def _parse_counts(html: str) -> dict[str, int | None]:
    """Best-effort extraction of a numeric record count from a report page.

    Distinguishes three states conservatively:

    * a report container (``<table>`` / Kendo grid) with data rows -> the row
      count;
    * a report container with no data rows -> ``0`` (a measured zero);
    * no report container at all -> ``None`` (unparseable, never a zero).
    """
    if not html:
        return {"count": None}
    soup = BeautifulSoup(html, "html.parser")
    data_rows = 0
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if not tds:
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


def _parse_json_counts(payload: Any) -> dict[str, int | None]:
    if isinstance(payload, dict):
        rows = payload.get("Data") or payload.get("data") or payload.get("Rows") or payload.get("rows")
        if isinstance(rows, list):
            return {"count": len(rows)}
        total = payload.get("Total") or payload.get("total")
        if isinstance(total, int) and not isinstance(total, bool):
            return {"count": total}
    if isinstance(payload, list):
        return {"count": len(payload)}
    return {"count": None}


# ── the Commander-facing entrypoint ──────────────────────────────────────────


def collect(runtime: Path, *, timeout: int = 30) -> dict[str, Any]:
    """Collect attributable NeoLife conversion/order/commission evidence.

    Returns a structured, Commander-consumable record. Never raises; never logs
    or returns credential values.
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
        auth = _login(env[_ENV_LOGIN], env[_ENV_PASSWORD], timeout=timeout)
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

        # Autonomous re-authentication: a denied session is refreshed once, then
        # this same surface is retried.
        if result.get("denied") and not reauthenticated:
            auth = _login(env[_ENV_LOGIN], env[_ENV_PASSWORD], timeout=timeout)
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

        # Prefer the factual Kendo DataSource XHR read endpoint when the page
        # exposes one; otherwise parse the server-rendered HTML.
        read_url = extract_grid_read_url(result["html"])
        count = None
        if read_url:
            xhr = _fetch(read_url, session.get("cookies") or {}, timeout=timeout)
            if xhr.get("ok"):
                try:
                    count = _parse_json_counts(json.loads(xhr["html"]))["count"]
                except (ValueError, TypeError):
                    count = _parse_counts(xhr["html"])["count"]
        if count is None:
            count = _parse_counts(result["html"])["count"]

        if count is None:
            datasets[kind] = {"status": UNAVAILABLE, "count": None, "label": surface["label"], "detail": "report body could not be parsed"}
        elif count > 0:
            datasets[kind] = {"status": VERIFIED, "count": count, "label": surface["label"]}
        else:
            datasets[kind] = {"status": ZERO, "count": 0, "label": surface["label"]}

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
