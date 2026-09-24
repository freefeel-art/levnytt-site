"""Shared fixtures for the dedicated LevNytt Commander tests.

These tests exercise the LevNytt-owned Commander package (``levnytt-site/
commander``) against the Hermes control repository's shared primitives. They run
under the Hermes virtualenv; this conftest ensures both the LevNytt repository
and the Hermes control repository are importable, and that the Hermes relative
paths (PROJECTS.md, config/) resolve by anchoring the working directory to the
Hermes control repository.
"""

from __future__ import annotations

import os
import copy
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

LEVNYTT_ROOT = Path(__file__).resolve().parents[1]
HERMES_ROOT = Path(
    os.environ.get(
        "HERMES_CONTROL_REPOSITORY",
        "/home/yampa/projects/active/hermes",
    )
).resolve()


def _ensure_paths() -> None:
    for root in (LEVNYTT_ROOT, HERMES_ROOT):
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
    os.environ.setdefault("HERMES_CONTROL_REPOSITORY", str(HERMES_ROOT))
    os.environ.setdefault("LEVNYTT_ROOT", str(LEVNYTT_ROOT))


_ensure_paths()


def production_gsc_snapshot(days: int, fetched_at: str | None = None) -> dict:
    """Use the actual LevNytt query/page schema; vary only observation dates."""
    snapshot = copy.deepcopy(json.loads((LEVNYTT_ROOT / "runtime" / "intelligence" / "gsc-latest.json").read_text(encoding="utf-8")))
    observed = datetime.fromisoformat(fetched_at.replace("Z", "+00:00")) if fetched_at else datetime.now(timezone.utc)
    end = (observed - timedelta(days=3)).date()
    for dimension in ("query", "page"):
        snapshot[dimension]["date_range"] = {"days": days, "start": (end - timedelta(days=days - 1)).isoformat(), "end": end.isoformat()}
        snapshot[dimension]["fetched_at"] = observed.isoformat()
    snapshot["fetched_at"] = observed.isoformat()
    snapshot.pop("trends", None)
    return snapshot
