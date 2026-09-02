"""LevNytt-owned NeoLife back-office reporting provider.

Read-only evidence collection for the one outcome the rest of the LevNytt
funnel cannot see: attributable NeoLife customer/distributor conversions and
commission/revenue. This is the missing attribution path named in
``OBJECTIVES.md`` and ``STATE.md`` — the north-star outcome the site currently
proxies through first-party Sponsor-ID link-click events and GSC traffic.

Design constraints (binding):

* **Credentials only from environment/secrets** — never hard-coded, never
  committed. The three required variables are ``NEOLIFE_BACKOFFICE_LOGIN``,
  ``NEOLIFE_BACKOFFICE_PASSWORD`` and ``NEOLIFE_BACKOFFICE_URL``.
* **Never log credentials.** Every error/diagnostic path redacts the secret
  values before they can reach a log line; the values are read once and only
  ever used inside the authenticated HTTP call.
* **Session reuse + autonomous re-authentication.** A successful login stores
  an opaque session (cookies) plus an expiry under the LevNytt runtime. A
  collection that observes an expired/denied session re-authenticates once and
  retries, so a scheduled cycle is not permanently blocked by a stale session.
* **Read-only.** Only login (credential exchange) and report/GET requests are
  made. Nothing here mutates back-office state.
* **Four-way outcome, never a silent zero.** ``collect`` returns exactly one of
  ``AUTH_FAILURE`` (credentials rejected), ``UNAVAILABLE`` (authenticated but
  the reports endpoint is unreachable/unparseable), ``ZERO`` (authenticated and
  a real, empty report), or ``VERIFIED`` (authenticated and a real, non-empty
  report). Missing credentials are reported separately as
  ``MISSING_CREDENTIALS`` — a temporary configuration boundary, never a zero
  and never a permanent Owner boundary.

The NeoLife back office does not expose a documented public API, so the login
and reports endpoints are configurable and fail closed: with no URL configured
the provider reports ``MISSING_CREDENTIALS`` and refuses to guess an endpoint.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

PROJECT_ID = "levnytt"

_ENV_LOGIN = "NEOLIFE_BACKOFFICE_LOGIN"
_ENV_PASSWORD = "NEOLIFE_BACKOFFICE_PASSWORD"
_ENV_URL = "NEOLIFE_BACKOFFICE_URL"

REQUIRED_ENV_VARS = (_ENV_LOGIN, _ENV_PASSWORD, _ENV_URL)

# Evidence outcome states. These are the exact distinctions the Commander must
# preserve; "authenticated but no data" and "not authenticated" are never the
# same thing, and neither is "zero".
MISSING_CREDENTIALS = "MISSING_CREDENTIALS"
AUTH_FAILURE = "AUTH_FAILURE"
UNAVAILABLE = "UNAVAILABLE"
ZERO = "ZERO"
VERIFIED = "VERIFIED"

_SESSION_FILENAME = "neolife-backoffice" + os.sep + "session.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _session_path(runtime: Path) -> Path:
    return Path(runtime) / _SESSION_FILENAME


def _read_env() -> dict[str, str]:
    """Read the three credential variables once. Values never leave this module
    except into the authenticated HTTP call; callers receive only booleans."""
    return {
        _ENV_LOGIN: os.getenv(_ENV_LOGIN, "").strip(),
        _ENV_PASSWORD: os.getenv(_ENV_PASSWORD, "").strip(),
        _ENV_URL: os.getenv(_ENV_URL, "").strip().rstrip("/"),
    }


def credentials_present() -> dict[str, bool]:
    """Whether each required variable exists and is non-empty. Never returns
    the values themselves."""
    env = _read_env()
    return {name: bool(env[name]) for name in REQUIRED_ENV_VARS}


def all_credentials_present() -> bool:
    return all(credentials_present().values())


def _redacted_credential_summary() -> dict[str, str]:
    """A safe (boolean) view of credential state for evidence records."""
    return {name: "populated" if present else "missing" for name, present in credentials_present().items()}


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
    expiry = session.get("expires_at")
    if not expiry:
        return False
    try:
        parsed = datetime.fromisoformat(str(expiry).replace("Z", "+00:00"))
    except ValueError:
        return False
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed > datetime.now(timezone.utc)


def _authenticate(runtime: Path, env: dict[str, str], login_url: str) -> dict[str, Any]:
    """Exchange credentials for an opaque session cookie and persist it.

    ``login_url`` is the full back-office login endpoint (base URL + suffix).
    Returns a status record; a rejected login is AUTH_FAILURE, never UNAVAILABLE
    and never ZERO.
    """
    try:
        response = requests.post(
            login_url,
            data={
                "username": env[_ENV_LOGIN],
                "password": env[_ENV_PASSWORD],
            },
            timeout=30,
            allow_redirects=True,
        )
    except requests.RequestException as error:
        return {"status": AUTH_FAILURE, "detail": f"login request failed: {type(error).__name__}"}

    if response.status_code in (401, 403):
        return {"status": AUTH_FAILURE, "detail": "credentials rejected by the NeoLife back office"}

    if response.status_code >= 400:
        return {"status": AUTH_FAILURE, "detail": f"login returned HTTP {response.status_code}"}

    cookies = response.cookies.get_dict()
    if not cookies:
        return {"status": AUTH_FAILURE, "detail": "login did not establish a session"}

    _save_session(runtime, {
        "cookies": cookies,
        "acquired_at": _now(),
        # Session validity is unknown a priori; persist without an expiry and
        # let the first denied report trigger autonomous re-authentication.
        "expires_at": None,
    })
    return {"status": VERIFIED, "detail": "authenticated session established"}


def _collect_reports(reports_url: str, session: dict[str, Any]) -> dict[str, Any]:
    """Fetch the reports endpoint with the stored session cookies (read-only).

    Returns a raw outcome; classification happens in :func:`collect`.
    """
    try:
        response = requests.get(reports_url, cookies=session.get("cookies") or {}, timeout=30)
    except requests.RequestException as error:
        return {"ok": False, "http_status": None, "detail": f"reports request failed: {type(error).__name__}", "payload": None}

    if response.status_code in (401, 403):
        return {"ok": False, "http_status": response.status_code, "detail": "session denied", "payload": None}

    if response.status_code >= 400:
        return {"ok": False, "http_status": response.status_code, "detail": f"reports returned HTTP {response.status_code}", "payload": None}

    try:
        payload = response.json()
    except ValueError:
        return {"ok": True, "http_status": response.status_code, "detail": "non-JSON report body", "payload": None}

    return {"ok": True, "http_status": response.status_code, "detail": None, "payload": payload}


def collect(
    runtime: Path,
    *,
    login_suffix: str | None = None,
    reports_suffix: str | None = None,
) -> dict[str, Any]:
    """The Commander-facing entrypoint: collect attributable NeoLife conversion
    and commission evidence read-only, classifying the outcome truthfully.

    ``login_suffix`` / ``reports_suffix`` are the back-office endpoint paths
    relative to ``NEOLIFE_BACKOFFICE_URL``. They are caller-supplied because the
    real back office determines them; when omitted, the provider returns
    UNAVAILABLE rather than guessing.
    """
    env = _read_env()
    if not all_credentials_present():
        return {
            "schema": "neolife-backoffice-evidence-v1",
            "project_id": PROJECT_ID,
            "status": MISSING_CREDENTIALS,
            "credentials": _redacted_credential_summary(),
            "collected_at": _now(),
            "conversions": None,
            "commissions": None,
            "evidence": {},
            "limitations": [
                "NeoLife back-office credentials/URL are not fully populated in the environment; "
                "this is a temporary configuration boundary, not a measured zero."
            ],
        }

    if not login_suffix or not reports_suffix:
        return {
            "schema": "neolife-backoffice-evidence-v1",
            "project_id": PROJECT_ID,
            "status": UNAVAILABLE,
            "credentials": _redacted_credential_summary(),
            "collected_at": _now(),
            "conversions": None,
            "commissions": None,
            "evidence": {},
            "limitations": [
                "The NeoLife back-office login/reports endpoint paths are not specified; refusing to guess an endpoint."
            ],
        }

    login_url = env[_ENV_URL] + login_suffix
    reports_url = env[_ENV_URL] + reports_suffix

    session = _load_session(runtime)
    if not _session_fresh(session) and session.get("cookies"):
        session = {}  # stale cookies dropped; re-authenticate below

    if not session.get("cookies"):
        auth = _authenticate(runtime, env, login_url)
        if auth["status"] != VERIFIED:
            return {
                "schema": "neolife-backoffice-evidence-v1",
                "project_id": PROJECT_ID,
                "status": auth["status"],
                "credentials": _redacted_credential_summary(),
                "collected_at": _now(),
                "conversions": None,
                "commissions": None,
                "evidence": {"auth": auth},
                "limitations": [auth["detail"]],
            }
        session = _load_session(runtime)

    outcome = _collect_reports(reports_url, session)

    # Autonomous re-authentication: a denied session is refreshed once and the
    # report retried, so a scheduled cycle survives a session expiry.
    if outcome.get("ok") is False and outcome.get("http_status") in (401, 403):
        auth = _authenticate(runtime, env, login_url)
        if auth["status"] == VERIFIED:
            session = _load_session(runtime)
            outcome = _collect_reports(reports_url, session)

    if outcome.get("ok") is False:
        return {
            "schema": "neolife-backoffice-evidence-v1",
            "project_id": PROJECT_ID,
            "status": AUTH_FAILURE if outcome.get("http_status") in (401, 403) else UNAVAILABLE,
            "credentials": _redacted_credential_summary(),
            "collected_at": _now(),
            "conversions": None,
            "commissions": None,
            "evidence": {"http_status": outcome.get("http_status"), "detail": outcome.get("detail")},
            "limitations": [outcome.get("detail") or "report collection failed"],
        }

    payload = outcome.get("payload")
    if payload is None:
        return {
            "schema": "neolife-backoffice-evidence-v1",
            "project_id": PROJECT_ID,
            "status": UNAVAILABLE,
            "credentials": _redacted_credential_summary(),
            "collected_at": _now(),
            "conversions": None,
            "commissions": None,
            "evidence": {"http_status": outcome.get("http_status"), "detail": outcome.get("detail")},
            "limitations": [outcome.get("detail") or "report body could not be parsed"],
        }

    # The report is parsed and normalised by the caller's field mapping; here we
    # preserve the raw payload and classify only presence vs absence.
    counts = _extract_counts(payload)
    status = VERIFIED if any(v for v in counts.values() if v) else ZERO

    return {
        "schema": "neolife-backoffice-evidence-v1",
        "project_id": PROJECT_ID,
        "status": status,
        "credentials": _redacted_credential_summary(),
        "collected_at": _now(),
        "conversions": counts.get("conversions"),
        "commissions": counts.get("commissions"),
        "evidence": {"raw_report": payload},
        "limitations": [] if status == VERIFIED else [
            "The back office returned an authenticated, empty report (measured zero)."
        ],
    }


def _extract_counts(payload: Any) -> dict[str, int | None]:
    """Best-effort extraction of conversion and commission counts from a report
    payload. Conservative: unknown shapes yield None (UNAVAILABLE upstream),
    never a fabricated number."""
    if isinstance(payload, dict):
        conversions = _first_int(payload, "conversions", "conversion_count", "customer_count", "customers")
        commissions = _first_int(payload, "commissions", "commission_total", "revenue", "total_commission")
        return {"conversions": conversions, "commissions": commissions}
    if isinstance(payload, list):
        return {"conversions": len(payload), "commissions": None}
    return {"conversions": None, "commissions": None}


def _first_int(payload: dict[str, Any], *keys: str) -> int | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    return None
