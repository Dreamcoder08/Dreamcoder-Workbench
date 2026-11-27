package cmd

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/dreamcoder08/dreamcoder-dots/installer/internal/dotfiles"
	"github.com/dreamcoder08/dreamcoder-dots/installer/internal/system"
	"github.com/fatih/color"
	"github.com/spf13/cobra"
)

func RepairCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "repair",
		Short: "Reapply symlinks after upstream updates",
		Long: `Re-stow all detected Dreamcoder components after updates to ML4W,
Gentleman Dots, or other upstream configs. Removes stale symlinks
that point outside the dreamcoder-dots repository.`,
		RunE: func(cmd *cobra.Command, args []string) error {
			green := color.New(color.FgGreen).SprintFunc()
			yellow := color.New(color.FgYellow).SprintFunc()
			red := color.New(color.FgRed).SprintFunc()

			platform := system.DetectPlatform()

			fmt.Println("🔧 Repairing Dreamcoder Workbench...")
			fmt.Printf("Platform: %s/%s (%s)\n", platform.OS, platform.Arch, platform.Distro)

			if !platform.HasStow {
				fmt.Printf("  %s stow is required but not installed\n", red("✗"))
				return fmt.Errorf("stow not found")
			}

			// Resolve dotfiles directory
			dotfilesDir, err := dotfiles.FindDotfilesDir()
			if err != nil {
				fmt.Printf("  %s %v\n", yellow("⚠"), err)
				dotfilesDir = dotfiles.FindDotfilesDirOrDefault(platform.HomeDir)
			}
			fmt.Printf("  Dotfiles: %s\n", dotfilesDir)

			// Detect what's installed and re-stow
			configs := system.DetectExistingConfigs(platform.HomeDir)
			components := detectInstalledComponents(configs)

			if len(components) == 0 {
				fmt.Println("  No components detected to repair")
				return nil
			}

			fmt.Printf("  Detected: %s\n", yellow(fmt.Sprintf("%v", components)))

			fmt.Println("  Generating active theme mirrors...")
			if err := dotfiles.GenerateMirrors(dotfilesDir); err != nil {
				fmt.Printf("  %s %v\n", red("✗"), err)
				return err
			}

			var repaired int
			for _, comp := range components {
				fmt.Printf("  Re-stowing %s... ", comp)

				compModules, _ := dotfiles.ResolveComponentModules([]string{comp})
				if len(compModules) == 0 {
					fmt.Printf("%s unknown module\n", red("✗"))
					continue
				}

				// Remove stale symlinks that point to other repos
				for _, mod := range compModules {
					removeStaleSymlinks(dotfilesDir, mod)

					// Delete then fresh stow
					_, _ = system.RunCommand("stow", "-d", dotfilesDir, "-t", platform.HomeDir, "--delete", mod)
				}

				if err := dotfiles.Stow(dotfilesDir, platform.HomeDir, compModules); err != nil {
					fmt.Printf("%s %v\n", red("✗"), err)
					continue
				}
				fmt.Printf("%s\n", green("✓"))
				repaired++
			}

			fmt.Printf("\n✅ Repair complete: %s components re-stowed\n", yellow(fmt.Sprintf("%d", repaired)))
			return nil
		},
	}
}

// removeStaleSymlinks finds and removes symlinks in target that point
// outside our dotfiles directory (e.g., from gentleman-dots or other repos)
func removeStaleSymlinks(dotfilesDir, module string) {
	moduleDir := filepath.Join(dotfilesDir, module)
	_ = filepath.Walk(moduleDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return nil
		}
		relPath, err := filepath.Rel(moduleDir, path)
		if err != nil || relPath == "." {
			return nil
		}

		target := filepath.Join(dotfilesDir, "..", relPath)
		target = filepath.Clean(target)
		link, err := os.Readlink(target)
		if err != nil {
			return nil // not a symlink
		}

		// If symlink doesn't point into our dotfiles dir, remove it
		if !strings.Contains(link, dotfilesDir) {
			os.Remove(target)
		}
		return nil
	})
}

func detectInstalledComponents(configs system.ExistingConfigs) []string {
	var components []string
	if configs.Nvim {
		components = append(components, "nvim")
	}
	if configs.Fish {
		components = append(components, "fish")
	}
	if configs.Zsh {
		components = append(components, "zsh")
	}
	if configs.Tmux {
		components = append(components, "tmux")
	}
	if configs.Kitty {
		components = append(components, "kitty")
	}
	if configs.Ghostty {
		components = append(components, "ghostty")
	}
	if configs.WezTerm {
		components = append(components, "wezterm")
	}
	if configs.Alacritty {
		components = append(components, "alacritty")
	}
	if configs.Nushell {
		components = append(components, "nushell")
	}
	if configs.Zellij {
		components = append(components, "zellij")
	}
	return components
}
