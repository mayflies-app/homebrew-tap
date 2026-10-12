# Agent Instructions

- Maintain shared source in `templates/macos-app`, the app catalog, and published casks here. Product behavior and native checks belong to the app repositories.
- Use `bash scripts/check.sh`; add `--apps` to compare consumers. `scripts/sync_apps.py --check` is read-only; `--apply` explicitly copies shared files.
- Keep `./scripts/app.py build|run|test|package` and `release --dry-run` as the common app entrypoints. Do not add alternate builders, compatibility wrappers, historical receipts, or governance layers.
- Use relevant Build macOS Apps skills and verify affected behavior. Protect unrelated changes and staged content.
- Local validation, packaging, and commits do not authorize remote writes. Release requires an explicitly authorized manual CI run. See [distribution](docs/homebrew.md).
