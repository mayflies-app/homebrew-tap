cask "simplecodexbar" do
  version "0.3.2"
  sha256 "b4f8f21ff231605ef52df53e95d83d23934d6c83ba5566dc32f8b4a901d220a3"

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
