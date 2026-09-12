#!/usr/bin/env bash
set -euo pipefail
umask 077
cd "$(dirname "$0")"
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi
if [[ -x .venv/bin/python ]]; then
  exec .venv/bin/python -m laptop_guard "$@"
fi
exec python3 -m laptop_guard "$@"
