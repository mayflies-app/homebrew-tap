cask "simplecodexbar" do
  version "0.3.0"
  sha256 "b8cae529bf1bcd9661da526373873466e400392788ac9428af62ede163c7ea47"

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
