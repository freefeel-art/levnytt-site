"""Fixed LevNytt business identity — no runtime project selection.

The dedicated LevNytt Commander has exactly one business identity. It is resolved
to a fixed canonical path and verified against a repo-identity marker, never from
a mutable active-project selector, an environment switch, or a ``--project``
argument. A programming error cannot silently redirect this context to OLSP,
Cashbackkollen, or any other project: the canonical root is a constant, and the
marker check fails closed.

LevNytt is the NeoLife project (Sponsor-ID 41-830928). Its executable context,
repository, runtime, state and business documents all resolve structurally to the
LevNytt repository — ``/home/yampa/projects/active/levnytt-site`` — and nowhere
else.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

PROJECT_ID = "levnytt"
PROJECT_NAME = "LevNytt"
SITE = "https://levnytt.se"
SPONSOR_ID = "41-830928"

# Fixed canonical construction: the LevNytt repository, independent of which
# directory (canonical checkout or a development worktree) happens to execute
# this code. The marker check below fails closed if this is ever wrong.
PROJECT_ROOT = Path(
    os.environ.get("LEVNYTT_ROOT", "/home/yampa/projects/active/levnytt-site")
).resolve()
RUNTIME_DIR = PROJECT_ROOT / "runtime"

# This Commander's durable state file, under the project runtime. It uses a
# dedicated filename so the historical frozen operation-state.json (written by
# the retired shared autonomous loop) is never mutated or misread by the new
# dedicated loop.
STATE_FILE_NAME = "commander-state.json"

# The identity marker: the Cloudflare Pages Advanced-Mode worker carries the
# LevNytt first-party CTA receiver (`levnytt-neolife-shop`) and the NeoLife
# Sponsor-ID. Neither string exists in any other project's repository, so this
# is a unique, fail-closed proof that the resolved root is genuinely LevNytt.
_IDENTITY_MARKER = "_worker.js"


def _state_file(runtime: Path | None = None) -> Path:
    return (Path(runtime) if runtime is not None else RUNTIME_DIR) / "commander" / STATE_FILE_NAME


def _verify_identity() -> None:
    """Fail closed unless the resolved root is genuinely the LevNytt repo."""
    marker = PROJECT_ROOT / _IDENTITY_MARKER
    try:
        text = marker.read_text(encoding="utf-8")
    except OSError as error:
        raise RuntimeError(
            f"LevNytt identity marker missing at {marker}: {error}"
        ) from error
    if "levnytt-neolife-shop" not in text or SPONSOR_ID not in text:
        raise RuntimeError(
            f"LevNytt identity marker did not verify at {marker}"
        )


def assert_identity() -> None:
    """Raise unless the resolved identity is LevNytt (fail closed)."""
    _verify_identity()


def identity() -> dict[str, Any]:
    """Return the fixed identity, verifying it first."""
    _verify_identity()
    return {
        "project_id": PROJECT_ID,
        "project_name": PROJECT_NAME,
        "site": SITE,
        "sponsor_id": SPONSOR_ID,
        "project_root": str(PROJECT_ROOT),
        "runtime_dir": str(RUNTIME_DIR),
        "state_file": str(_state_file()),
    }


def load_state(runtime: Path | None = None) -> dict[str, Any]:
    """Read this Commander's durable state, or an empty baseline."""
    path = _state_file(runtime)
    if not path.is_file():
        return {"project_id": PROJECT_ID, "prior_decisions": [], "latest_stop_reason": None}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"project_id": PROJECT_ID, "prior_decisions": [], "latest_stop_reason": None}
    if not isinstance(value, dict):
        return {"project_id": PROJECT_ID, "prior_decisions": [], "latest_stop_reason": None}
    return value


def save_state(state: dict[str, Any], runtime: Path | None = None) -> None:
    """Atomically persist this Commander's durable state."""
    path = _state_file(runtime)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".commander-state.", dir=path.parent, text=True
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise
