# Homebrew Distribution

## Installation

Install a cask from this tap:

```sh
brew tap mayflies-app/tap
brew install --cask dockautohide
```

[`Casks/`](../Casks) contains the published installation definitions. A cask is
added or updated by the app's release workflow after its public DMG is verified.
Apps without a published cask provide source-build instructions in their README.

## Configuration

Each app's `macos-app.json` defines its product name, bundle ID, GitHub repository,
cask token, and minimum macOS version. `VERSION` supplies the release version.
Before running a release, ensure `repository` matches the GitHub repository that
hosts the workflow and that the version identifies the intended source commit.
The tap destination is `mayflies-app/homebrew-tap`.

## Local Packaging

Run these commands from the target app repository root. The tap maintains the
shared template and published casks; each application builds in its own checkout.

```sh
./scripts/app.py package --sign developer-id
./scripts/app.py release --dry-run
```

Packaging creates a Release Universal app, DMG, manifest, and checksum under
`dist/release/universal`. Developer ID packaging uses the locally installed signing
identity and does not submit notarization or upload artifacts. A release dry run
inspects the plan without building or making external requests.

## GitHub Actions Release

The manual **macOS release** workflow accepts `version`, `dry_run` (default `true`),
and `publish` (default `false`). Leaving `version` empty reads `VERSION`.

Dry-run uses a separate `ubuntu-latest` job without Xcode or signing credentials.
With `dry_run` disabled, manual CI calls `release --execute` to build one Universal
package containing arm64 and x86_64, sign with Developer ID, submit its DMG once for
notarization, and staple the accepted result. Explicit `publish` also uploads
release assets, verifies downloaded bytes, and updates the tap. Both CI and release
execution use the GitHub-hosted `xcode-27` runner and select Xcode 27. The CLI
`package --arch` options remain available for local single-architecture packages.

Release execution stays serialized and does not cancel a running release. Preview
runs have a separate concurrency group and can replace an older preview. Ordinary
CI cancels superseded runs while retaining tests, bundle builds, and release-plan checks.

Compilation caches contain only `.build/app/debug/<native architecture>` for CI or
`.build/app/release` for releases. Their keys separate configurations, OS and CPU,
actual Xcode/SDK/Swift fingerprints, dependency/configuration hashes, and source SHA.
Fallback stays within the same toolchain and dependency prefix. Pull requests restore
only; successful branch pushes may save Debug caches within GitHub's branch scope.
Release execution on the default branch may save Release caches. `dist`,
signing material, and notarization receipts are excluded. Cache hits never skip
validation, signing, notarization, or public download verification.

## Credentials

Configure these secrets in each app repository. Signing and notarization require the
first seven; publication and tap updates also require the eighth. Never put private
material in source or logs.

| Secret | Purpose |
| --- | --- |
| `MACOS_CERTIFICATE` | Base64 Developer ID Application PKCS#12 including its private key |
| `MACOS_CERTIFICATE_PASSWORD` | PKCS#12 password |
| `MACOS_SIGNING_IDENTITY` | Expected full signing identity or certificate SHA-1 |
| `MACOS_TEAM_ID` | Developer Team ID matching the certificate |
| `APPLE_NOTARIZATION_KEY_ID` | App Store Connect API key ID |
| `APPLE_NOTARIZATION_ISSUER_ID` | API key issuer ID |
| `APPLE_NOTARIZATION_PRIVATE_KEY` | Corresponding `.p8` private key contents |
| `HOMEBREW_TAP_TOKEN` | Fine-grained PAT limited to this tap with Contents write |

App releases use the workflow's `github.token`; no separate `GH_TOKEN` secret is needed.
CI creates and cleans a temporary signing keychain and notarization key. The API key
issuer UUID and signing Team ID are separate values. A dry run validates the release
plan; executing the workflow validates credentials. Publication requires a public
app repository and explicit authorization to publish.

## Homebrew Distribution

Verify signing, notarization acceptance, stapling, and public asset contents separately.
Calculate final checksums after stapling. The release and cask must identify the same
version and actual public download bytes. Add casks only through the verified release
workflow, with a SHA-256 checksum for the final DMG.

Uninstall quits the app. Zap removes preferences and saved window state while preserving
notes, account data, and Keychain items. Apps requiring macOS 13.5 use `:ventura` with
a read-only minor-version guard; apps requiring macOS 14 use `:sonoma`.

## Validation

`bash scripts/check.sh` runs isolated template tests, Ruby syntax checks, and available
actionlint checks. Hosted hub CI requires a pinned actionlint binary and caches it;
Go setup and tool compilation run only on a cache miss. `--apps` also compares shared
consumer files. Product tests, bundle
validation, notarization, and Homebrew installation are separate checks performed
by their respective app and release workflows.
