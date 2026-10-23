cask "bigbang" do
  version "0.1.0"
  sha256 "326848c357e65e53b9591d974447a469fdcfe2739f59451e913ce4b1c974827e"

  url "https://github.com/mayflies-app/big-bang/releases/download/v#{version}/BigBang-#{version}-universal.dmg"
  name "BigBang"
  desc "Process selected text with configurable AI prompts"
  homepage "https://github.com/mayflies-app/big-bang"

  livecheck do
    url :url
    strategy :github_latest
  end

  depends_on macos: :sonoma

  app "BigBang.app"

  uninstall quit: "app.mayfiles.BigBang"

  zap trash: [
    "~/Library/Preferences/app.mayfiles.BigBang.plist",
    "~/Library/Saved Application State/app.mayfiles.BigBang.savedState",
  ]
end
