package cmd

import (
	"fmt"
	"os/exec"
	"runtime"

	"github.com/fatih/color"
	"github.com/spf13/cobra"
	"github.com/dreamcoder08/dreamcoder-dots/installer/internal/system"
)

func DoctorCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "doctor",
		Short: "Check health of Dreamcoder Workbench installation",
		RunE: func(cmd *cobra.Command, args []string) error {
			green := color.New(color.FgGreen).SprintFunc()
			dim := color.New(color.FgHiBlack).SprintFunc()

			platform := system.DetectPlatform()

			fmt.Println("🔍 Dreamcoder Workbench Doctor")
			fmt.Println("========================")
			fmt.Printf("Platform: %s/%s", runtime.GOOS, runtime.GOARCH)
			if platform.Distro != "" {
				fmt.Printf(" (%s)", platform.Distro)
			}
			fmt.Println()

			// Tools check
			fmt.Println("\nTools:")
			tools := []struct {
				Name string
				Desc string
			}{
				{"git", "Version control"},
				{"stow", "Symlink manager"},
				{"nvim", "Editor"},
				{"fish", "Shell"},
				{"zsh", "Shell"},
				{"nushell", "Shell"},
				{"kitty", "Terminal"},
				{"ghostty", "Terminal"},
				{"wezterm", "Terminal"},
				{"alacritty", "Terminal"},
				{"tmux", "Multiplexer"},
				{"zellij", "Multiplexer"},
				{"starship", "Prompt"},
				{"fzf", "Fuzzy finder"},
				{"zoxide", "Smart cd"},
			}

			var found, missing int
			for _, tool := range tools {
				if _, err := exec.LookPath(tool.Name); err == nil {
					fmt.Printf("  %s %s (%s)\n", green("✓"), tool.Name, tool.Desc)
					found++
				} else {
					fmt.Printf("  %s %s (%s)\n", dim("·"), tool.Name, tool.Desc)
					missing++
				}
			}

			// Existing configs
			fmt.Println("\nExisting Configs:")
			configs := system.DetectExistingConfigs(platform.HomeDir)

			configList := []struct {
				Name   string
				Exists bool
			}{
				{"Neovim", configs.Nvim},
				{"Fish", configs.Fish},
				{"Zsh", configs.Zsh},
				{"Nushell", configs.Nushell},
				{"Tmux", configs.Tmux},
				{"Zellij", configs.Zellij},
				{"Kitty", configs.Kitty},
				{"Ghostty", configs.Ghostty},
				{"WezTerm", configs.WezTerm},
				{"Alacritty", configs.Alacritty},
				{"Starship", configs.Starship},
				{"Fzf", configs.Fzf},
				{"Zoxide", configs.Zoxide},
			}

			var detected int
			for _, c := range configList {
				if c.Exists {
					fmt.Printf("  %s %s\n", green("✓"), c.Name)
					detected++
				}
			}

			if detected == 0 {
				fmt.Printf("  %s No configs detected\n", dim("·"))
			}

			// Summary
			fmt.Printf("\n%s tools found, %s not installed, %s configs detected\n",
				green(fmt.Sprintf("%d", found)),
				dim(fmt.Sprintf("%d", missing)),
				green(fmt.Sprintf("%d", detected)))

			return nil
		},
	}
}
