#!/usr/bin/env bash
set -euo pipefail
case "${1:-}" in
  '') ;;
  --help|-h) printf 'Usage: scripts/check.sh\nPublished cask Ruby syntax checks; no app checkouts required.\n'; exit 0 ;;
  *) printf 'Unknown argument: %s\n' "$1" >&2; exit 2 ;;
esac
[[ $# -eq 0 ]] || { printf 'Unexpected arguments\n' >&2; exit 2; }
TAP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$TAP_ROOT"
for cask in Casks/*.rb; do ruby -c "$cask"; done
printf 'PASS: cask checks completed\n'
