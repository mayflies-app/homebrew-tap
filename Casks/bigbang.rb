cask "bigbang" do
  version "0.2.0"
  sha256 "1e0cfad2248a9e5470972450955924f5bcc71856bf9086f67a20e33db3db5f00"

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
