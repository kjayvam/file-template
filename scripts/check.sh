#!/usr/bin/env bash
set -euo pipefail
project_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
case "${1:-}" in
  --structure)
    [ "$#" -eq 1 ]
    python3 "$project_root/scripts/verify-projects.py" --structure-only
    python3 "$project_root/scripts/verify-template-modules.py" --wiki-only
    ;;
  ""|--docker)
    [ "$#" -le 1 ]
    "$project_root/scripts/check-template-modules.sh" "$@"
    python3 "$project_root/scripts/verify-projects.py" "$@"
    ;;
  *) echo "사용법: $0 [--structure|--docker]" >&2; exit 2 ;;
esac
