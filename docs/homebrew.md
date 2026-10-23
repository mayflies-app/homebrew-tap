# Homebrew Distribution

## Installation

```sh
brew tap mayflies-app/tap
brew install --cask dockautohide
```

[`Casks/`](../Casks) contains published installation definitions. Homebrew installs
the recorded version and checks the downloaded DMG against its SHA-256 checksum.
Apps without a published cask provide source-build instructions in their README.

## Cask Updates

Each app's manual release workflow verifies its immutable public Universal DMG,
manifest, checksum, notarization acceptance and stapling before updating the tap.
The cask's version, URL, checksum, app bundle name and minimum macOS version must
match those published bytes. Calculate the final checksum after stapling.

The destination is `mayflies-app/homebrew-tap`, branch `main`. The app repository's
`HOMEBREW_TAP_TOKEN` must have Contents write access to this tap. The cask job uses
a fresh isolated checkout, commits only the target `Casks/<token>.rb`, and pushes
normally. Retry only confirmed concurrent update failures; fix access or credential
failures before retrying. A failed cask update does not roll back a public release.
Recover from the verified public assets without rebuilding or replacing that version.

The shared [release guide](https://github.com/mayflies-app/macos-app-tooling/blob/main/docs/releasing.md)
covers packaging, credentials, workflow jobs, retries and diagnostics. The common
release entrypoint and workflow templates are maintained in
[macos-app-tooling](https://github.com/mayflies-app/macos-app-tooling), copied into
each application repository. This tap does not build, sign or notarize apps.

Uninstall quits the app. Zap removes preferences and saved window state while
preserving notes, account data and Keychain items. Apps requiring macOS 13.5 use
`:ventura` with a read-only minor-version guard; apps requiring macOS 14 use `:sonoma`.

## Tap Updates

Keep published `main` history append-only; correct mistakes with new commits or
reverts. Homebrew maintains an independent tap
checkout and updates it with a direct Git rebase. Rewriting published history makes
previously published commits appear local-only in existing installations; replaying
them can conflict with the rewritten casks. Git's `pull.ff` setting does not control
Homebrew's direct rebase.

Develop cask changes in a separate checkout. Keep the installed tap on
`main`, tracking `origin/main`, with no local edits or unpublished commits on that
branch. Its origin must be
`https://github.com/mayflies-app/homebrew-tap.git`. Inspect it without assuming an
installation path:

```sh
brew update
tap_checkout="$(brew --repo mayflies-app/tap)"
git -C "$tap_checkout" status --short --branch
git -C "$tap_checkout" rev-list --left-right --count HEAD...origin/main
```

A synchronized consumer reports a clean working tree and `0 0`. Use
`git config --local pull.ff only` for manual pulls in each checkout; Homebrew's
update behavior remains separate. If a consumer still carries obsolete history from
a previous rewrite, preserve its work and original history before realigning its
consumed branch with upstream. Keep recovery branches without upstream tracking;
do not replay obsolete published commits or change unrelated taps.

## Validation

Run `bash scripts/check.sh` from this checkout to validate the published casks'
Ruby syntax. When a cask's behavior changes, also verify the affected Homebrew
command, such as `brew install --cask <token> --dry-run`. Syntax checks do not prove
asset availability, signing, notarization, or installation behavior.

Documentation changes need link, path and diff checks. Shared-tool tests and
consumer synchronization belong to macos-app-tooling; product tests and bundle
checks belong to each app repository.
