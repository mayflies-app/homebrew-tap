#!/usr/bin/env bash
set -euo pipefail
CHECK_APPS=0
case "${1:-}" in
  '') ;;
  --apps) CHECK_APPS=1; shift ;;
  --help|-h) printf 'Usage: scripts/check.sh [--apps]\nOffline hub tests and cask syntax; --apps also compares local app bytes.\n'; exit 0 ;;
  *) printf 'Unknown argument: %s\n' "$1" >&2; exit 2 ;;
esac
[[ $# -eq 0 ]] || { printf 'Unexpected arguments\n' >&2; exit 2; }
TAP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$TAP_ROOT"
python3 -B -m unittest discover -s templates/macos-app/tests -p 'test_*.py'
shopt -s nullglob
for cask in Casks/*.rb; do ruby -c "$cask"; done
if command -v actionlint >/dev/null; then
  actionlint -config-file /dev/null -ignore 'label "xcode-27" is unknown' \
    .github/workflows/*.yml templates/macos-app/ci.yml templates/macos-app/release.yml
else
  printf 'SKIP: actionlint is not installed\n'
fi
if ((CHECK_APPS)); then python3 -B scripts/sync_apps.py --check; fi
printf 'PASS: hub checks completed\n'
