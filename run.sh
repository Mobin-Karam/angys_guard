#!/usr/bin/env bash
set -euo pipefail
umask 077
cd "$(dirname "$0")"

# Laptop Guard v11 no longer requires .env. Non-secret configuration is kept in
# ~/.config/laptop-guard/config.toml and secrets are kept in mode-0600
# ~/.config/laptop-guard/secrets.json. Missing/invalid required values are
# requested interactively by the Python runtime.
if [[ -x .venv/bin/python ]]; then
  exec .venv/bin/python -m laptop_guard "$@"
fi
exec python3 -m laptop_guard "$@"
