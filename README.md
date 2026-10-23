# Homebrew Tap

Homebrew casks for Mayflies macOS apps. Published installation definitions live in
[`Casks/`](Casks); each cask references a verified public release asset.

## Installation

```sh
brew tap mayflies-app/tap
brew install --cask dockautohide
```

For apps without a published cask, follow the source-build instructions in the app's
README. Homebrew installs the version recorded in the cask.

## Maintenance

Run distribution checks from this repository:

```sh
bash scripts/check.sh
```

App release workflows add or update only their corresponding cask after verifying
the public DMG and its checksum. Keep published `main` history append-only and use
a separate development checkout from Homebrew's installed tap. See
[Homebrew Distribution](docs/homebrew.md) for promotion requirements and tap updates.

Shared app scripts, workflow templates, design and localization helpers, and
synchronization tools live in
[macos-app-tooling](https://github.com/mayflies-app/macos-app-tooling).
Each app keeps the copied common `./scripts/app.py` entrypoint and builds independently.

## License

[MIT](LICENSE).
