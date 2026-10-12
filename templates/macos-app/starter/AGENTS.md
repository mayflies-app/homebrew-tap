# Agent Instructions

- Use `./scripts/app.py build|run|test|package` and `release --dry-run`.
- Shared scripts and workflows are maintained in the tap and copied here. Do not add alternate builders or compatibility wrappers.
- Keep product configuration, windows, focus, input methods, permissions, storage, and native verification here.
- Use isolated tests and protect real preferences, databases, and credentials. Verify affected behavior with inspectable results.
- Review local and staged changes before synchronizing or committing. Local packaging and commits do not authorize uploads, notarization, publication, or tap updates.
