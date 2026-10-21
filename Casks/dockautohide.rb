cask "dockautohide" do
  version "0.2.3"
  sha256 "7170e72552bf6a055b382a7a2157f168d2f64abb9e6d5c04da1bffcc6ded4f03"

  url "https://github.com/mayflies-app/DockAutoHide/releases/download/v#{version}/DockAutoHide-#{version}-universal.dmg"
  name "DockAutoHide"
  desc "Auto-hide the Dock only when a window would cover it"
  homepage "https://github.com/mayflies-app/DockAutoHide"

  livecheck do
    url :url
    strategy :github_latest
  end

  depends_on macos: :ventura

  app "DockAutoHide.app"

  preflight_steps do
    run "/bin/sh", args: ["-c", <<~SH]
      version=$(/usr/bin/sw_vers -productVersion)
      major=${version%%.*}
      minor=${version#*.}
      [ "$minor" = "$version" ] && minor=0
      patch=${minor#*.}
      [ "$patch" = "$minor" ] && patch=0
      minor=${minor%%.*}
      if [ "$major" -lt 13 ] || { [ "$major" -eq 13 ] && [ "$minor" -lt 5 ]; } || { [ "$major" -eq 13 ] && [ "$minor" -eq 5 ] && [ "$patch" -lt 0 ]; }; then
        echo "DockAutoHide requires macOS 13.5 or later." >&2
        exit 1
      fi
    SH
  end

  uninstall quit: "io.github.nshcr.DockAutoHide"

  zap trash: [
    "~/Library/Preferences/io.github.nshcr.DockAutoHide.plist",
    "~/Library/Saved Application State/io.github.nshcr.DockAutoHide.savedState",
  ]
end
