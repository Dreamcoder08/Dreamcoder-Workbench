package cmd

import (
	"fmt"

	"github.com/dreamcoder08/dreamcoder-dots/installer/internal/dotfiles"
	"github.com/dreamcoder08/dreamcoder-dots/installer/internal/system"
	"github.com/fatih/color"
	"github.com/spf13/cobra"
)

func InstallCmd() *cobra.Command {
	var (
		components []string
		themeMode  string
		dryRun     bool
	)

	cmd := &cobra.Command{
		Use:   "install",
		Short: "Install Dreamcoder OS components via stow",
		Long: `Install Dreamcoder OS components using GNU Stow.

Installs symlinks for each specified component from the dotfiles
repository to your home directory. Uses the shared dotfiles path
resolution (DREAMCODER_DIR env var, git parent walk, or common
locations).

Examples:
  dreamcoder-dots install
  dreamcoder-dots install --components kitty,fish,nvim
  dreamcoder-dots install --dry-run --components all`,
		RunE: func(cmd *cobra.Command, args []string) error {
			green := color.New(color.FgGreen).SprintFunc()
			yellow := color.New(color.FgYellow).SprintFunc()
			red := color.New(color.FgRed).SprintFunc()

			platform := system.DetectPlatform()

			fmt.Println("📦 Dreamcoder OS Installer")
			fmt.Printf("Platform: %s/%s (%s)\n", platform.OS, platform.Arch, platform.Distro)

			// Resolve dotfiles directory
			dotfilesDir, err := dotfiles.FindDotfilesDir()
			if err != nil {
				fmt.Printf("  %s %v\n", yellow("⚠"), err)
				dotfilesDir = dotfiles.FindDotfilesDirOrDefault(platform.HomeDir)
				fmt.Printf("  Using: %s\n", dotfilesDir)
			}

			// Check for stow
			if ok, ver := dotfiles.CheckStow(); !ok {
				fmt.Printf("  %s stow is required but not installed\n", red("✗"))
				fmt.Println("  Install stow: https://www.gnu.org/software/stow/")
				return fmt.Errorf("stow not found")
			} else {
				fmt.Printf("  %s %s\n", green("✓"), ver)
			}

			// Check existing configs
			configs := system.DetectExistingConfigs(platform.HomeDir)
			printExistingConfigs(configs)

			// Resolve component names to modules
			if len(components) == 1 && components[0] == "all" {
				all := dotfiles.KnownComponents()
				allSelected := make([]string, len(all))
				for i, c := range all {
					allSelected[i] = c.Name
				}
				components = allSelected
			}

			modules, err := dotfiles.ResolveComponentModules(components)
			if err != nil {
				fmt.Printf("  %s %v\n", red("✗"), err)
				return err
			}

			// Deduplicate modules
			seen := make(map[string]bool)
			var uniqueModules []string
			for _, m := range modules {
				if !seen[m] {
					seen[m] = true
					uniqueModules = append(uniqueModules, m)
				}
			}
			modules = uniqueModules

			fmt.Printf("\n  Target: %s\n", dotfilesDir)
			fmt.Printf("  Modules: %v\n", modules)

			// Backup if requested
			if backup, _ := cmd.Flags().GetBool("backup"); backup {
				fmt.Println("\n📦 Backing up existing configurations...")
				backupDir, manifest, err := system.CreateBackup(platform, components)
				if err != nil {
					fmt.Printf("  %s Backup failed: %v\n", red("✗"), err)
					return err
				}
				fmt.Printf("  %s Backup created: %s (%d files)\n", green("✓"), backupDir, len(manifest.Files))
			}

			if dryRun {
				fmt.Println("\n🔍 Dry run:")
				output, err := dotfiles.StowDryRun(dotfilesDir, platform.HomeDir, modules)
				if err != nil {
					fmt.Printf("  %s\n", output)
				} else {
					fmt.Println(output)
				}
				return nil
			}

			// Install: generate the gitignored active mirrors, then stow.
			fmt.Println("\n🎨 Generating active theme mirrors...")
			var installed, failed int
			err = dotfiles.StowAfterMirrors(dotfilesDir, func() error {
				fmt.Println("\n📦 Installing components...")
				for _, comp := range components {
					compModules, _ := dotfiles.ResolveComponentModules([]string{comp})
					if len(compModules) == 0 {
						fmt.Printf("  %s Unknown component: %s\n", red("✗"), comp)
						failed++
						continue
					}
					fmt.Printf("  Installing %s... ", comp)
					if err := dotfiles.Stow(dotfilesDir, platform.HomeDir, compModules); err != nil {
						fmt.Printf("%s %v\n", red("✗"), err)
						failed++
						continue
					}
					fmt.Printf("%s\n", green("✓"))
					installed++
				}
				return nil
			})
			if err != nil {
				fmt.Printf("  %s %v\n", red("✗"), err)
				return err
			}

			fmt.Printf("\n✅ Installation complete: %s installed", yellow(fmt.Sprintf("%d", installed)))
			if failed > 0 {
				fmt.Printf(", %s failed", red(fmt.Sprintf("%d", failed)))
			}
			fmt.Println()

			return nil
		},
	}

	cmd.Flags().StringSliceVarP(&components, "components", "c",
		[]string{"kitty", "fish", "nvim"}, "Components to install (comma-separated, or 'all')")
	cmd.Flags().StringVarP(&themeMode, "theme", "t", "dark", "Theme mode (dark/light/dusk)")
	cmd.Flags().Bool("backup", true, "Backup existing configs before install")
	cmd.Flags().BoolVar(&dryRun, "dry-run", false, "Show what would be installed without doing it")

	return cmd
}

func printExistingConfigs(configs system.ExistingConfigs) {
	green := color.New(color.FgGreen).SprintFunc()
	dim := color.New(color.FgHiBlack).SprintFunc()

	var detected []string
	if configs.Nvim {
		detected = append(detected, "nvim")
	}
	if configs.Fish {
		detected = append(detected, "fish")
	}
	if configs.Zsh {
		detected = append(detected, "zsh")
	}
	if configs.Tmux {
		detected = append(detected, "tmux")
	}
	if configs.Kitty {
		detected = append(detected, "kitty")
	}
	if configs.Ghostty {
		detected = append(detected, "ghostty")
	}
	if configs.WezTerm {
		detected = append(detected, "wezterm")
	}
	if configs.Alacritty {
		detected = append(detected, "alacritty")
	}
	if configs.Starship {
		detected = append(detected, "starship")
	}
	if configs.Fzf {
		detected = append(detected, "fzf")
	}
	if configs.Zoxide {
		detected = append(detected, "zoxide")
	}

	if len(detected) > 0 {
		fmt.Printf("\n  %s Existing configs: %s\n", green("✓"), dim(fmt.Sprintf("%v", detected)))
	} else {
		fmt.Println("\n  No existing configs detected")
	}
}
