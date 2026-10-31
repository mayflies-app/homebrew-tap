cask "simplecodexbar" do
  version "0.1.1"
  sha256 "b8e3db466b04165e075c2d0356576b26bdb547f28acfbe30b20172e558de6b92"

  url "https://github.com/mayflies-app/simple-codex-bar/releases/download/v#{version}/SimpleCodexBar-#{version}-universal.dmg"
  name "SimpleCodexBar"
  desc "Track Codex and ChatGPT account usage from the menu bar"
  homepage "https://github.com/mayflies-app/simple-codex-bar"

  livecheck do
    url :url
    strategy :github_latest
  end

  depends_on macos: :sonoma

  app "SimpleCodexBar.app"

  uninstall quit: "app.mayfiles.SimpleCodexBar"

  zap trash: [
    "~/Library/Preferences/app.mayfiles.SimpleCodexBar.plist",
    "~/Library/Saved Application State/app.mayfiles.SimpleCodexBar.savedState",
  ]
end
