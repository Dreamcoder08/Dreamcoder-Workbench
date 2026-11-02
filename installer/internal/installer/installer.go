package installer

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
)

type Installer struct {
	Platform    Platform
	Components  []string
	ThemeMode   string
	DotfilesDir string
}

func NewInstaller(platform Platform, components []string, themeMode string) *Installer {
	home, _ := os.UserHomeDir()
	return &Installer{
		Platform:    platform,
		Components:  components,
		ThemeMode:   themeMode,
		DotfilesDir: filepath.Join(home, "Documents", "PROYECTOS", "dreamcoder08", "dreamcoder-workbench"),
	}
}

func (i *Installer) Install(progressFunc func(component string, status string)) error {
	for _, comp := range i.Components {
		progressFunc(comp, "installing")

		if err := i.installComponent(comp); err != nil {
			progressFunc(comp, "error: "+err.Error())
			return fmt.Errorf("failed to install %s: %w", comp, err)
		}

		progressFunc(comp, "done")
	}
	return nil
}

func (i *Installer) installComponent(component string) error {
	moduleMap := map[string]string{
		"kitty":     "DreamcoderKitty",
		"ghostty":   "DreamcoderGhostty",
		"wezterm":   "DreamcoderWezTerm",
		"alacritty": "DreamcoderAlacritty",
		"fish":      "DreamcoderShell",
		"zsh":       "DreamcoderShell",
		"nushell":   "DreamcoderNushell",
		"tmux":      "DreamcoderTmux",
		"zellij":    "DreamcoderZellij",
		"nvim":      "DreamcoderNvim",
		"lazygit":   "DreamcoderLazygit",
	}

	module, ok := moduleMap[component]
	if !ok {
		return fmt.Errorf("unknown component: %s", component)
	}

	return i.stow(module)
}

func (i *Installer) stow(module string) error {
	cmd := exec.Command("stow", "-d", i.DotfilesDir, "-t", os.Getenv("HOME"), module)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}
