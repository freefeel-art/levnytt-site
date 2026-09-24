"""Dedicated LevNytt Commander entrypoint.

Fixed business context — LevNytt and nothing else. There is no ``--project``
argument and no selector: the identity is resolved structurally from this file's
location. Invoke as:

    levnytt commander run            # one bounded cycle
    levnytt commander run --dry-run  # read-only
    levnytt commander status         # fixed identity

Run from the LevNytt repository with the Hermes virtualenv on PATH; this module
adds the Hermes control repository to sys.path so the shared providers and
primitives resolve, while identity/state remain fixed to the LevNytt repository
via ``commander.identity``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

LEVNYTT_ROOT = Path(__file__).resolve().parents[1]
_HERMES_ROOT = Path(
    os.environ.get(
        "HERMES_CONTROL_REPOSITORY",
        "/home/yampa/projects/active/hermes",
    )
).resolve()


def _prepare_path() -> None:
    for path in (LEVNYTT_ROOT, _HERMES_ROOT):
        if path.is_dir() and str(path) not in sys.path:
            sys.path.insert(0, str(path))
    # Hermes shared primitives resolve their registry (PROJECTS.md, config/)
    # relative to the current working directory. Anchor the process to the
    # Hermes control repository so those resolve, while identity/state remain
    # fixed to the LevNytt repository via commander.identity.
    os.chdir(_HERMES_ROOT)
    # Load Hermes' shared and repository-local environment layers before any
    # LevNytt provider reads process credentials. The dedicated Commander uses
    # a local decision model, so no other Hermes import can provide this side
    # effect reliably.
    os.environ.setdefault("HERMES_CONTROL_REPOSITORY", str(_HERMES_ROOT))
    from app.core.environment import load_hermes_environment

    load_hermes_environment()


def main(argv: list[str] | None = None) -> int:
    _prepare_path()

    from commander import identity

    parser = argparse.ArgumentParser(prog="levnytt commander")
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run")
    run_parser.add_argument("--dry-run", action="store_true")
    sub.add_parser("status")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.command == "status":
        print(json.dumps(identity.identity(), ensure_ascii=False, indent=2))
        return 0

    from commander.operating_loop import run_cycle

    report = run_cycle(execute=not args.dry_run)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
