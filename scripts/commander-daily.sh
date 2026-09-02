#!/usr/bin/env bash
# Dedicated LevNytt Commander — fixed business context, no --project.
#
# This is the ONLY scheduled entrypoint for the LevNytt operating system. It
# does not use `hermes run --project`, project activation, or the mutable
# active-project selector. It runs one bounded cycle of the dedicated LevNytt
# Commander and stops.
#
# Cadence is NOT publication cadence. This entrypoint runs several times per day
# (see the crontab below), but the Commander's own daily budgets cap publication
# (1/day) and optimization (3/day) independently of how many cycles run, so more
# cycles never become more publishing. Defect repair, deployment of already
# accepted content, measurement, and commitment resumption are never budgeted.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
HERMES_PY="/home/yampa/projects/active/hermes/.venv/bin/python"
LOCK="/tmp/levnytt-commander.lock"

# Prevent overlapping executions (fail safe: skip rather than double-run).
exec 9>"${LOCK}"
if ! flock -n 9; then
    echo "levnytt commander: another run is in progress; skipping." >&2
    exit 0
fi

export HERMES_CONTROL_REPOSITORY="/home/yampa/projects/active/hermes"
export LEVNYTT_ROOT="${REPO}"

cd "${REPO}"
"${HERMES_PY}" -m commander.run run
