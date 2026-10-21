# Homebrew Tap

Homebrew distribution and shared macOS development tools. Each app owns its product
configuration, code and native checks. Shared
scripts, workflows, design components, and localization helpers are copied into
the app repositories so they can build independently.

## Installation

```sh
brew tap mayflies-app/tap
brew install --cask dockautohide
```

The available casks are listed in [`Casks/`](Casks). For apps without a published
cask, follow the source-build instructions in the app's README.

## Development

Apps use `./scripts/app.py build|run|test|package` and
`./scripts/app.py release --dry-run`. Each also has a native Xcode project named
after the product; Codex Run uses `./scripts/app.py run`.

Run hub checks and synchronization commands from this repository:

```sh
bash scripts/check.sh
python3 -B scripts/sync_apps.py --check APP_CHECKOUT
python3 -B scripts/sync_apps.py --apply APP_CHECKOUT
```

Replace `APP_CHECKOUT` with the chosen app repository root; multiple checkout
arguments are supported. Locations are supplied only when running the command.
Each app's `macos-app.json` declares its repository-relative shared destinations.
Synchronization compares files by default. `--apply` copies only shared paths and
preserves product tools. Edit shared code in [`templates/macos-app`](templates/macos-app)
and synchronize consumers; edit product behavior in the app repository. Documentation
changes need link, path, and diff checks. Run the hub tests when executable tooling
changes, and affected app checks when consumer behavior changes. See
[Shared Maintenance](templates/macos-app/README.md#shared-maintenance) for ownership
and validation scope.

See the [template guide](templates/macos-app/README.md) for commands and configuration,
and the [distribution guide](docs/homebrew.md) for signing, notarization, and publication.

## License

[MIT](LICENSE).
