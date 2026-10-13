# Agent Instructions

- Maintain shared scripts, workflows, design and localization helpers in `templates/macos-app`, plus the app catalog and published casks here. App configuration, translations, product behavior and native checks belong to the app repositories. See [Shared Maintenance](templates/macos-app/README.md#shared-maintenance).
- Run synchronization commands from this repository. `python3 -B scripts/sync_apps.py --check` is read-only; `--apply` explicitly copies shared files. Review local and staged changes before applying, and resulting consumer diffs before committing.
- Match validation to the change. For documentation only, check links, paths and `git diff --check`; no product build or test is needed. For executable template or hub changes, use `bash scripts/check.sh`; add `--apps` when shared files or the catalog change. Validate only affected product behavior in consumers.
- Keep `./scripts/app.py build|run|test|package` and `release --dry-run` as the common app entrypoints. Do not add alternate builders, compatibility wrappers, historical receipts, or governance layers.
- Use relevant Build macOS Apps skills and verify affected behavior. Protect unrelated changes and staged content.
- Local validation, packaging, and commits do not authorize remote writes. Release requires an explicitly authorized manual CI run. See [distribution](docs/homebrew.md).
