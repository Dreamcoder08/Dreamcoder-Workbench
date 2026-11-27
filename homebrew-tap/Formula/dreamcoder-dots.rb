class DreamcoderDots < Formula
  desc "Dreamcoder Workbench - Token-governed visual operating layer"
  homepage "https://github.com/dreamcoder08/dreamcoder-dots"
  version "2.0.0"
  license "MIT"

  on_macos do
    on_arm64 do
      url "https://github.com/dreamcoder08/dreamcoder-dots/releases/download/v2.0.0/dreamcoder-dots-darwin-arm64"
      sha256 "169d05d53aeea7aa5ce2565dba13fd5e28e7b91b462bad15b93b81c62cff91b5"
    end
    on_intel do
      url "https://github.com/dreamcoder08/dreamcoder-dots/releases/download/v2.0.0/dreamcoder-dots-darwin-amd64"
      sha256 "9847d0bcabd64b670932b07950a7e960cc2bfc438811d4547796c8b07a665509"
    end
  end

  on_linux do
    on_arm64 do
      url "https://github.com/dreamcoder08/dreamcoder-dots/releases/download/v2.0.0/dreamcoder-dots-linux-arm64"
      sha256 "3bf937960f3c83854ee5849d88d53b35d3cffc8aeda9e05d76ad27b282f10d1e"
    end
    on_intel do
      url "https://github.com/dreamcoder08/dreamcoder-dots/releases/download/v2.0.0/dreamcoder-dots-linux-amd64"
      sha256 "c3772ac63507856f5ea965d25fb8564d5f6eb1e56fbffdf2a205cd3d7e252e69"
    end
  end

  def install
    bin.install "dreamcoder-dots"
  end

  test do
    assert_match "dreamcoder-dots", shell_output("#{bin}/dreamcoder-dots --version")
  end
end
