#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
if ! command -v uv >/dev/null 2>&1; then
  printf '%s\n' 'Install uv first; see docs/MIGRATION.md.' >&2
  exit 1
fi
if [ ! -f uv.lock ]; then
  printf '%s\n' 'Missing uv.lock; do not resolve dependencies silently.' >&2
  exit 1
fi
uv sync --frozen
uv run --frozen python tools/migration.py doctor
uv run --frozen python tools/design_baseline.py
printf '%s\n' 'Environment prepared. Restore private assets and credentials separately. No login, send or deployment was performed.'
