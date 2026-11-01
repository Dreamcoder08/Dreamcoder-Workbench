// Package dotfiles provides shared path resolution for the Dreamcoder installer.
// It finds the dotfiles repository directory by checking multiple strategies:
// environment variable, git detection, and common locations.
package dotfiles

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// ModuleMap maps component names to GNU Stow module directories.
var ModuleMap = map[string]string{
	"Kitty":       "DreamcoderKitty",
	"Ghostty":     "DreamcoderGhostty",
	"WezTerm":     "DreamcoderWezTerm",
	"Alacritty":   "DreamcoderAlacritty",
	"Fish":        "DreamcoderShell",
	"Zsh":         "DreamcoderShell",
	"Bash":        "DreamcoderShell",
	"Nushell":     "DreamcoderNushell",
	"Tmux":        "DreamcoderTmux",
	"Zellij":      "DreamcoderZellij",
	"Neovim":      "DreamcoderNvim",
	"Lazygit":     "DreamcoderLazygit",
	"Bat":         "DreamcoderBat",
	"Fastfetch":   "DreamcoderFastfetch",
	"KittyTheme":  "DreamcoderKitty",
	"NvimTheme":   "DreamcoderNvim",
	"Codex":       "DreamcoderCodexCLI",
	"Warp":        "DreamcoderWarp",
	"Pi":          "DreamcoderPi",
	"OpenCode":    "DreamcoderOpenCode",
	"Antigravity": "DreamcoderAntigravity",
}

// KnownComponents returns the canonical list of installable components
// with their display names, descriptions, and categories.
func KnownComponents() []Component {
	return []Component{
		{Name: "Kitty", Description: "GPU-accelerated terminal emulator", Category: "Terminals", Selected: true},
		{Name: "Ghostty", Description: "Fast, feature-rich terminal", Category: "Terminals", Selected: false},
		{Name: "WezTerm", Description: "Cross-platform terminal emulator", Category: "Terminals", Selected: false},
		{Name: "Alacritty", Description: "Minimal GPU-accelerated terminal", Category: "Terminals", Selected: false},
		{Name: "Fish", Description: "Friendly interactive shell", Category: "Shells", Selected: true},
		{Name: "Zsh", Description: "Z shell with syntax highlighting", Category: "Shells", Selected: false},
		{Name: "Bash", Description: "GNU Bourne-Again SHell", Category: "Shells", Selected: false},
		{Name: "Nushell", Description: "Modern structured shell", Category: "Shells", Selected: false},
		{Name: "Tmux", Description: "Terminal multiplexer", Category: "Multiplexers", Selected: true},
		{Name: "Zellij", Description: "Terminal workspace with UI", Category: "Multiplexers", Selected: false},
		{Name: "Neovim", Description: "Hyperextensible text editor", Category: "Editors", Selected: true},
		{Name: "Lazygit", Description: "Terminal UI for git", Category: "Tools", Selected: false},
		{Name: "Bat", Description: "Cat clone with syntax highlighting", Category: "Tools", Selected: false},
		{Name: "Codex", Description: "AI coding assistant CLI", Category: "AI Tools", Selected: false},
		{Name: "OpenCode", Description: "AI agent CLI with TUI", Category: "AI Tools", Selected: false},
		{Name: "Pi", Description: "Pi AI agent terminal", Category: "AI Tools", Selected: false},
		{Name: "Antigravity", Description: "VS Code-compatible editor", Category: "Editors", Selected: false},
		{Name: "Warp", Description: "AI-native terminal", Category: "Terminals", Selected: false},
		{Name: "Fastfetch", Description: "System info fetcher", Category: "Tools", Selected: true},
	}
}

// Component represents an installable component with metadata.
type Component struct {
	Name        string `json:"name"`
	Description string `json:"description"`
	Category    string `json:"category"`
	Selected    bool   `json:"selected"`
}

// FindDotfilesDir locates the dreamcoder-dots repository root.
// Priority: DREAMCODER_DIR env > .git parent walk > common locations.
func FindDotfilesDir() (string, error) {
	// 1. Environment variable
	if env := os.Getenv("DREAMCODER_DIR"); env != "" {
		if valid, _ := isValid(env); valid {
			return env, nil
		}
		return "", fmt.Errorf("DREAMCODER_DIR=%s does not contain a dreamcoder-dots repo", env)
	}

	// 2. Walk up from cwd looking for .git with dreamcoder remote
	if dir, err := findFromCWD(); err == nil {
		return dir, nil
	}

	// 3. Common locations
	home, _ := os.UserHomeDir()
	candidates := []string{
		filepath.Join(home, "Documents", "PROYECTOS", "dreamcoder08", "dreamcoder-workbench"),
		filepath.Join(home, "Documents", "PROYECTOS", "dreamcoder-dots"),
		filepath.Join(home, "Projects", "dreamcoder-dots"),
		filepath.Join(home, "code", "dreamcoder-dots"),
		filepath.Join(home, "dreamcoder-dots"),
		filepath.Join(home, ".local", "share", "dreamcoder-dots"),
	}

	for _, path := range candidates {
		if valid, _ := isValid(path); valid {
			return path, nil
		}
	}

	return "", fmt.Errorf("dreamcoder-dots repository not found. Set DREAMCODER_DIR or run from inside the repo")
}

// FindDotfilesDirOrDefault returns the dotfiles directory or a sensible default.
func FindDotfilesDirOrDefault(homeDir string) string {
	if dir, err := FindDotfilesDir(); err == nil {
		return dir
	}
	return filepath.Join(homeDir, "Documents", "PROYECTOS", "dreamcoder08", "dreamcoder-workbench")
}

// ResolveComponentModules maps selected component name list to stow module names.
func ResolveComponentModules(names []string) ([]string, error) {
	var modules []string
	for _, name := range names {
		module, ok := ModuleMap[name]
		if !ok {
			return nil, fmt.Errorf("unknown component: %s", name)
		}
		modules = append(modules, module)
	}
	return dedup(modules), nil
}

// ResolveSelectedModules maps selected Component structs to deduplicated stow modules.
func ResolveSelectedModules(components []Component) []string {
	var modules []string
	seen := make(map[string]bool)
	for _, c := range components {
		if !c.Selected {
			continue
		}
		module, ok := ModuleMap[c.Name]
		if !ok || seen[module] {
			continue
		}
		seen[module] = true
		modules = append(modules, module)
	}
	return modules
}

// isValid checks if dir contains a valid dreamcoder-dots repository.
func isValid(dir string) (bool, error) {
	gitDir := filepath.Join(dir, ".git")
	info, err := os.Stat(gitDir)
	if err != nil || !info.IsDir() {
		return false, err
	}

	// Quick sanity: check for known top-level files
	for _, marker := range []string{"src/dreamcoder_theme", "pyproject.toml", "Makefile"} {
		if _, err := os.Stat(filepath.Join(dir, marker)); err == nil {
			return true, nil
		}
	}
	return false, nil
}

// findFromCWD walks up from current directory looking for the repo root.
func findFromCWD() (string, error) {
	cwd, err := os.Getwd()
	if err != nil {
		return "", err
	}

	dir := cwd
	for {
		if valid, _ := isValid(dir); valid {
			return dir, nil
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			break
		}
		dir = parent
	}

	return "", fmt.Errorf("not inside a dreamcoder-dots repository")
}

// Stow runs GNU Stow for the given modules.
func Stow(dotfilesDir, homeDir string, modules []string) error {
	args := append([]string{"-d", dotfilesDir, "-t", homeDir}, modules...)
	cmd := exec.Command("stow", args...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

// StowDryRun shows what stow would do without making changes.
func StowDryRun(dotfilesDir, homeDir string, modules []string) (string, error) {
	args := append([]string{"-n", "-v", "-d", dotfilesDir, "-t", homeDir}, modules...)
	cmd := exec.Command("stow", args...)
	output, err := cmd.CombinedOutput()
	return string(output), err
}

// CheckStow verifies stow is installed and returns the version.
func CheckStow() (bool, string) {
	cmd := exec.Command("stow", "--version")
	output, err := cmd.CombinedOutput()
	if err != nil {
		return false, ""
	}
	return true, strings.TrimSpace(string(output))
}

func dedup(items []string) []string {
	seen := make(map[string]bool)
	var result []string
	for _, item := range items {
		if !seen[item] {
			seen[item] = true
			result = append(result, item)
		}
	}
	return result
}
