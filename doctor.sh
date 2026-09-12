#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ -f .env ]]; then set -a; . ./.env; set +a; fi
if [[ -x .venv/bin/python ]]; then exec .venv/bin/python -m laptop_guard.doctor; fi
exec python3 -m laptop_guard.doctor
