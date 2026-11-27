package tui

import (
	"fmt"
	"os"

	"github.com/dreamcoder08/dreamcoder-dots/installer/internal/dotfiles"
	"github.com/dreamcoder08/dreamcoder-dots/installer/internal/system"
)

// NonInteractiveConfig holds CLI flags for non-interactive mode
type NonInteractiveConfig struct {
	Shell    string
	Terminal string
	WM       string
	Nvim     bool
	Font     bool
	Backup   bool
	DryRun   bool
	Verbose  bool
}

// RunNonInteractive executes installation without TUI
func RunNonInteractive(config NonInteractiveConfig) error {
	platform := system.DetectPlatform()

	fmt.Println("🎨 Dreamcoder Workbench - Non-Interactive Installer")
	fmt.Printf("Platform: %s/%s (%s)\n", platform.OS, platform.Arch, platform.Distro)

	// Resolve dotfiles directory
	dotfilesDir, err := dotfiles.FindDotfilesDir()
	if err != nil {
		fmt.Fprintf(os.Stderr, "⚠️  %v\n", err)
		fmt.Fprintf(os.Stderr, "   Using default: %s\n", dotfiles.FindDotfilesDirOrDefault(platform.HomeDir))
		dotfilesDir = dotfiles.FindDotfilesDirOrDefault(platform.HomeDir)
	}
	fmt.Printf("Dotfiles: %s\n", dotfilesDir)

	// Check stow
	if ok, ver := dotfiles.CheckStow(); ok {
		fmt.Printf("Stow: %s\n", ver)
	} else {
		fmt.Fprintln(os.Stderr, "❌ GNU Stow is required but not installed.")
		fmt.Fprintln(os.Stderr, "   Install: brew install stow  or  sudo apt install stow")
		return fmt.Errorf("stow not found")
	}

	// Build component list from flags
	var components []dotfiles.Component

	// Start with defaults, then override from flags
	allComponents := dotfiles.KnownComponents()
	componentMap := make(map[string]dotfiles.Component)
	for _, c := range allComponents {
		componentMap[c.Name] = c
	}

	if config.Terminal != "" && config.Terminal != "none" {
		if c, ok := componentMap[config.Terminal]; ok {
			c.Selected = true
			components = append(components, c)
		}
	}
	if config.Shell != "" && config.Shell != "none" {
		if c, ok := componentMap[config.Shell]; ok {
			c.Selected = true
			components = append(components, c)
		}
	}
	if config.WM != "" && config.WM != "none" {
		if c, ok := componentMap[config.WM]; ok {
			c.Selected = true
			components = append(components, c)
		}
	}
	if config.Nvim {
		if c, ok := componentMap["Neovim"]; ok {
			c.Selected = true
			components = append(components, c)
		}
	}

	if len(components) == 0 {
		fmt.Println("No components specified. Use --help for usage.")
		fmt.Println("Example: dreamcoder-dots --non-interactive --terminal kitty --shell fish --nvim")
		return nil
	}

	// Resolve modules
	modules := dotfiles.ResolveSelectedModules(components)
	fmt.Printf("Components: %v\n", components)
	fmt.Printf("Stow modules: %v\n", modules)

	// Backup existing configs if requested
	if config.Backup {
		fmt.Println("\n📦 Backing up existing configurations...")
		backupDir, manifest, err := system.CreateBackup(platform, nil)
		if err != nil {
			fmt.Fprintf(os.Stderr, "⚠️  Backup warning: %v\n", err)
		} else {
			fmt.Printf("Backup created: %s (%d files)\n", backupDir, len(manifest.Files))
		}
	}

	if config.DryRun {
		fmt.Println("\n🔍 Dry run - would install:")
		for _, comp := range components {
			fmt.Printf("  - %s (%s)\n", comp.Name, comp.Description)
		}
		fmt.Println("\nStow dry-run output:")
		output, err := dotfiles.StowDryRun(dotfilesDir, platform.HomeDir, modules)
		if err != nil {
			fmt.Printf("  Dry run result: %s\n", output)
		} else {
			fmt.Println(output)
		}
		return nil
	}

	// Generate the gitignored active mirrors before stowing anything.
	fmt.Println("\n🎨 Generating active theme mirrors...")
	if err := dotfiles.GenerateMirrors(dotfilesDir); err != nil {
		fmt.Fprintf(os.Stderr, "❌ %v\n", err)
		return err
	}

	// Install components
	fmt.Println("\n📦 Installing components...")
	for _, comp := range components {
		compModules := dotfiles.ResolveSelectedModules([]dotfiles.Component{comp})
		if len(compModules) == 0 {
			fmt.Fprintf(os.Stderr, "  ❌ Unknown component: %s\n", comp.Name)
			continue
		}
		fmt.Printf("  Installing %s... ", comp.Name)
		if err := dotfiles.Stow(dotfilesDir, platform.HomeDir, compModules); err != nil {
			fmt.Fprintf(os.Stderr, "❌ Failed: %v\n", err)
			continue
		}
		fmt.Println("✅")
	}

	fmt.Println("\n✅ Installation complete!")
	fmt.Println("   Restart your terminal or run: source ~/.zshrc")
	return nil
}
