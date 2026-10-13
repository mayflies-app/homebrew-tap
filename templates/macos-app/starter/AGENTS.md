# Agent Instructions

- Use `./scripts/app.py build|run|test|package` and `release --dry-run`.
- Shared scripts, workflows, and declared design and localization helpers are maintained in `homebrew-tap/templates/macos-app` and copied here. Update the source and synchronize from the tap checkout. See [Shared Maintenance](https://github.com/mayflies-app/homebrew-tap/tree/main/templates/macos-app#shared-maintenance). Do not add alternate builders or compatibility wrappers.
- Keep app configuration, native projects, Codex Run, translations, product behavior and targeted checks here. Preserve windows, focus, input methods, permissions and storage.
- Match validation to the change. Documentation-only changes need link, path and diff checks; executable changes need affected tests. Use isolated tests and protect real preferences, databases and credentials. Retain inspectable results for native checks.
- Review local and staged changes before synchronizing or committing. Local packaging and commits do not authorize uploads, notarization, publication, or tap updates.
