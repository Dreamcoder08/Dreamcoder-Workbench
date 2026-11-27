package views

import (
	"fmt"
	"os/exec"
	"runtime"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/dreamcoder08/dreamcoder-dots/installer/internal/system"
	"github.com/dreamcoder08/dreamcoder-dots/installer/internal/tui/styles"
)

type DoctorModel struct {
	width    int
	height   int
	platform system.Platform
	configs  system.ExistingConfigs
}

func NewDoctorModel() DoctorModel {
	platform := system.DetectPlatform()
	configs := system.DetectExistingConfigs(platform.HomeDir)
	return DoctorModel{
		platform: platform,
		configs:  configs,
	}
}

func (m DoctorModel) Init() tea.Cmd {
	return nil
}

func (m DoctorModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
	case tea.KeyMsg:
		switch msg.String() {
		case "esc":
			return NewWelcomeModel(), nil
		case "q", "ctrl+c":
			return m, tea.Quit
		}
	}
	return m, nil
}

func (m DoctorModel) View() string {
	title := styles.TitleStyle.Render("🔍 Dreamcoder Workbench Doctor")
	separator := styles.CommentStyle.Render("========================")

	// Platform info
	platformInfo := fmt.Sprintf("Platform: %s/%s", runtime.GOOS, runtime.GOARCH)
	if m.platform.Distro != "" {
		platformInfo += fmt.Sprintf(" (%s)", m.platform.Distro)
	}

	// Tool checks
	var toolChecks []string
	tools := map[string]string{
		"git":      "Version control",
		"stow":     "Symlink manager",
		"nvim":     "Editor",
		"fish":     "Shell",
		"kitty":    "Terminal",
		"ghostty":  "Terminal",
		"starship": "Prompt",
		"fzf":      "Fuzzy finder",
		"zoxide":   "Smart cd",
	}

	for tool, desc := range tools {
		status := "✗ not found"
		if _, err := exec.LookPath(tool); err == nil {
			status = "✓ installed"
		}
		toolChecks = append(toolChecks, fmt.Sprintf("  %s %s (%s)", status, tool, desc))
	}
	toolsList := lipgloss.JoinVertical(lipgloss.Left, toolChecks...)

	// Config detection
	var configChecks []string
	if m.configs.Nvim {
		configChecks = append(configChecks, "  ✓ Neovim config detected")
	} else {
		configChecks = append(configChecks, "  ✗ Neovim config not found")
	}
	if m.configs.Fish {
		configChecks = append(configChecks, "  ✓ Fish config detected")
	}
	if m.configs.Zsh {
		configChecks = append(configChecks, "  ✓ Zsh config detected")
	}
	if m.configs.Tmux {
		configChecks = append(configChecks, "  ✓ Tmux config detected")
	}
	configsList := lipgloss.JoinVertical(lipgloss.Left, configChecks...)

	footer := styles.CommentStyle.Render("Press Esc to go back • q Quit")

	content := lipgloss.JoinVertical(
		lipgloss.Left,
		title,
		separator,
		styles.MenuItemStyle.Render(platformInfo),
		"",
		styles.SelectedStyle.Render("Tools:"),
		toolsList,
		"",
		styles.SelectedStyle.Render("Configs:"),
		configsList,
		"",
		footer,
	)

	return lipgloss.Place(
		m.width, m.height,
		lipgloss.Center, lipgloss.Center,
		content,
		lipgloss.WithWhitespaceBackground(styles.Primary),
	)
}
