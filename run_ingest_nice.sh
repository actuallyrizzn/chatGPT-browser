#!/usr/bin/env bash
# Run ingest with low CPU priority so the machine doesn't lock (nice -n 19).
# Always uses the project venv (uv run).
set -e
cd "$(dirname "$0")"
exec nice -n 19 uv run python run_ingest.py "$@"
