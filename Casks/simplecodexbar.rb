cask "simplecodexbar" do
  version "0.1.0"
  sha256 "90586c74ee65b0f10b57f19b05e43db1c0fe33f5b8c33deca6d17c51dd3a9ca0"

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
