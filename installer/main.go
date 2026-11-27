package main

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
	"github.com/dreamcoder08/dreamcoder-dots/installer/cmd"
	"github.com/dreamcoder08/dreamcoder-dots/installer/internal/tui"
	"github.com/dreamcoder08/dreamcoder-dots/installer/pkg/version"
)

func main() {
	var (
		nonInteractive bool
		shell          string
		terminal       string
		wm             string
		nvim           bool
		font           bool
		backup         bool
		dryRun         bool
		verbose        bool
	)

	rootCmd := &cobra.Command{
		Use:     "dreamcoder-dots",
		Short:   "Dreamcoder Workbench - Token-governed visual operating layer",
		Version: version.Version,
		RunE: func(c *cobra.Command, args []string) error {
			if nonInteractive {
				config := tui.NonInteractiveConfig{
					Shell:    shell,
					Terminal: terminal,
					WM:       wm,
					Nvim:     nvim,
					Font:     font,
					Backup:   backup,
					DryRun:   dryRun,
					Verbose:  verbose,
				}
				return tui.RunNonInteractive(config)
			}
			return tui.RunTUI()
		},
	}

	// Non-interactive flags
	rootCmd.Flags().BoolVar(&nonInteractive, "non-interactive", false, "Run without TUI, use CLI flags instead")
	rootCmd.Flags().StringVar(&shell, "shell", "", "Shell to install (fish, zsh, nushell)")
	rootCmd.Flags().StringVar(&terminal, "terminal", "", "Terminal to install (kitty, ghostty, wezterm, alacritty)")
	rootCmd.Flags().StringVar(&wm, "wm", "", "Window manager to install (tmux, zellij)")
	rootCmd.Flags().BoolVar(&nvim, "nvim", false, "Install Neovim configuration")
	rootCmd.Flags().BoolVar(&font, "font", false, "Install Nerd Font")
	rootCmd.Flags().BoolVar(&backup, "backup", true, "Backup existing configs before install")
	rootCmd.Flags().BoolVar(&dryRun, "dry-run", false, "Show what would be installed without doing it")
	rootCmd.Flags().BoolVar(&verbose, "verbose", false, "Verbose output")

	rootCmd.AddCommand(cmd.InstallCmd())
	rootCmd.AddCommand(cmd.RepairCmd())
	rootCmd.AddCommand(cmd.DoctorCmd())

	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
