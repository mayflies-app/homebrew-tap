cask "bigbang" do
  version "0.2.1"
  sha256 "fa320c204071657795c7f0b3efda7e0dbe34690de6ee1a7c254a2fd2457a787d"

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
