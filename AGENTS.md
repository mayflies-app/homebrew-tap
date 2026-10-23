# Agent Instructions

- Maintain published casks, installation documentation, and distribution checks here. Shared app scripts, workflows, design and localization helpers belong in [macos-app-tooling](https://github.com/mayflies-app/macos-app-tooling); app configuration and product behavior belong in the app repositories.
- Keep published tap `main` history append-only. Develop in a separate checkout; the Homebrew-managed tap only consumes upstream updates and is not a shared-tool synchronization target. See [Tap Updates](docs/homebrew.md#tap-updates).
- Match validation to the change. Documentation-only changes need link, path and `git diff --check` checks. Run `bash scripts/check.sh` for cask or distribution-check changes; verify affected Homebrew behavior when needed. Do not build or test products for tap documentation changes.
- Add or update casks through the app's authorized release workflow after verifying the public DMG and final checksum. Preserve immutable published assets and inspect only the target cask diff. See [Cask Updates](docs/homebrew.md#cask-updates).
- Protect unrelated changes and staged content. Do not commit host-specific paths, compatibility wrappers, historical receipts, or governance layers.
- Local checks and commits do not authorize remote writes or publication. Signing, notarization, and release execution belong to the app's explicitly authorized manual CI workflow.
