#!/usr/bin/env bash
set -euo pipefail
project_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
exec python3 "$project_root/scripts/project-check.py" --build "$@"
