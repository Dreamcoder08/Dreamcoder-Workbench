package views

import (
	"fmt"
	"strings"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/dreamcoder08/dreamcoder-dots/installer/internal/dotfiles"
	"github.com/dreamcoder08/dreamcoder-dots/installer/internal/system"
	"github.com/dreamcoder08/dreamcoder-dots/installer/internal/tui/styles"
)

// --- Messages ---

type installProgressMsg struct {
	component string
	status    string // "pending" | "installing" | "done" | "error"
	err       error
}

type installDoneMsg struct {
	success int
	failed  int
}

type mirrorsGeneratedMsg struct {
	err error
}

type installLogMsg struct {
	line string
}

// --- Model ---

type InstallProgressModel struct {
	components  []dotfiles.Component
	modules     []string
	results     map[string]string // component name -> status
	errors      map[string]string // component name -> error message
	currentName string
	currentIdx  int
	done        bool
	success     int
	failed      int
	width       int
	height      int
	logs        []string
	dotfilesDir string
	homeDir     string
}

func NewInstallProgressModel(components []dotfiles.Component) InstallProgressModel {
	home, _ := system.UserHomeDir()
	dfDir := dotfiles.FindDotfilesDirOrDefault(home)
	modules := dotfiles.ResolveSelectedModules(components)
	results := make(map[string]string)
	errs := make(map[string]string)

	for _, c := range components {
		if c.Selected {
			results[c.Name] = "pending"
		}
	}

	return InstallProgressModel{
		components:  components,
		modules:     modules,
		results:     results,
		errors:      errs,
		currentIdx:  0,
		dotfilesDir: dfDir,
		homeDir:     home,
	}
}

func (m InstallProgressModel) Init() tea.Cmd {
	dir := m.dotfilesDir
	return func() tea.Msg {
		return mirrorsGeneratedMsg{err: dotfiles.GenerateMirrors(dir)}
	}
}

func (m InstallProgressModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height

	case mirrorsGeneratedMsg:
		if msg.err == nil {
			return m, m.installNext()
		}
		// Without the active mirrors no component may be stowed.
		for _, c := range m.components {
			if c.Selected {
				m.results[c.Name] = "error"
				m.errors[c.Name] = msg.err.Error()
				m.failed++
			}
		}
		return m, func() tea.Msg { return installDoneMsg{success: m.success, failed: m.failed} }

	case installProgressMsg:
		m.results[msg.component] = msg.status
		if msg.err != nil {
			m.errors[msg.component] = msg.err.Error()
			m.failed++
		} else if msg.status == "done" {
			m.success++
		}
		// Continue to next
		return m, m.installNext()

	case installLogMsg:
		m.logs = append(m.logs, msg.line)
		// Keep max 50 log lines
		if len(m.logs) > 50 {
			m.logs = m.logs[len(m.logs)-50:]
		}

	case installDoneMsg:
		m.done = true

	case tea.KeyMsg:
		switch msg.String() {
		case "enter", "esc", "q":
			return NewSummaryModel(m.success, m.failed, m.errors), nil
		case "ctrl+c":
			return m, tea.Quit
		}
	}

	return m, nil
}

func (m InstallProgressModel) installNext() tea.Cmd {
	// Find next selected component that hasn't been processed
	for m.currentIdx < len(m.components) {
		comp := m.components[m.currentIdx]
		m.currentIdx++

		if !comp.Selected {
			continue
		}

		m.currentName = comp.Name
		return m.installComponent(comp)
	}

	// All done
	return func() tea.Msg {
		return installDoneMsg{success: m.success, failed: m.failed}
	}
}

func (m InstallProgressModel) installComponent(comp dotfiles.Component) tea.Cmd {
	return func() tea.Msg {
		modules := dotfiles.ResolveSelectedModules([]dotfiles.Component{comp})
		if len(modules) == 0 {
			return installProgressMsg{
				component: comp.Name,
				status:    "error",
				err:       fmt.Errorf("unknown component: %s", comp.Name),
			}
		}

		// Try stow with --no-folding for cleaner symlink management
		args := []string{"--no-folding", "-d", m.dotfilesDir, "-t", m.homeDir}
		args = append(args, modules...)

		_, err := system.RunCommand("stow", args...)
		if err != nil {
			// Retry without --no-folding if it fails (older stow versions)
			retryArgs := []string{"-d", m.dotfilesDir, "-t", m.homeDir}
			retryArgs = append(retryArgs, modules...)
			_, retryErr := system.RunCommand("stow", retryArgs...)
			if retryErr != nil {
				return installProgressMsg{
					component: comp.Name,
					status:    "error",
					err:       fmt.Errorf("stow failed: %w", retryErr),
				}
			}
		}

		return installProgressMsg{
			component: comp.Name,
			status:    "done",
		}
	}
}

func (m InstallProgressModel) progressBar(completed, total int) string {
	if total == 0 {
		return ""
	}
	width := 30
	filled := int(float64(completed) / float64(total) * float64(width))
	if filled > width {
		filled = width
	}

	bar := strings.Repeat("█", filled) + strings.Repeat("░", width-filled)
	pct := int(float64(completed) / float64(total) * 100)

	return fmt.Sprintf("%s %d/%d (%d%%)", bar, completed, total, pct)
}

func (m InstallProgressModel) View() string {
	if m.width == 0 {
		m.width = 80
	}
	if m.height == 0 {
		m.height = 24
	}

	title := styles.TitleStyle.Render("📦 Installing Dreamcoder OS")

	// Count totals
	total := 0
	for _, c := range m.components {
		if c.Selected {
			total++
		}
	}
	completed := m.success + m.failed

	// Progress bar
	progress := styles.MenuItemStyle.Render(m.progressBar(completed, total))

	// Status per component
	var items []string
	for _, c := range m.components {
		if !c.Selected {
			continue
		}
		status, hasStatus := m.results[c.Name]
		if !hasStatus {
			status = "pending"
		}

		var icon, label string
		var style lipgloss.Style

		switch status {
		case "done":
			icon = "✅"
			label = "Installed"
			style = styles.SuccessStyle
		case "installing":
			icon = "🔄"
			label = "Installing..."
			style = styles.SelectedStyle
		case "error":
			icon = "❌"
			label = fmt.Sprintf("Failed: %s", m.errors[c.Name])
			style = styles.ErrorStyle
		default:
			icon = "⏳"
			label = "Pending"
			style = styles.CommentStyle
		}

		cat := styles.CommentStyle.Render(fmt.Sprintf("[%s]", c.Category))
		line := fmt.Sprintf("%s %s %s — %s", icon, cat, c.Name, label)
		items = append(items, style.Render(line))
	}

	// Active component indicator
	var activeLine string
	if !m.done && m.currentName != "" {
		spin := []string{"⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"}
		// Use current completed as deterministic spinner frame
		frame := completed % len(spin)
		activeLine = fmt.Sprintf("\n  %s Installing %s...", spin[frame], m.currentName)
	}

	// Log section (last few lines)
	var logSection string
	if len(m.logs) > 0 {
		start := 0
		if len(m.logs) > 5 {
			start = len(m.logs) - 5
		}
		logLines := m.logs[start:]
		logSection = "\n" + styles.CommentStyle.Render(strings.Join(logLines, "\n"))
	}

	// Summary when done
	var summary string
	if m.done {
		summary = fmt.Sprintf(
			"\n  %s %d installed, %s %d failed",
			styles.SuccessStyle.Render("✅"),
			m.success,
			styles.ErrorStyle.Render("❌"),
			m.failed,
		)
		hint := styles.CommentStyle.Render("\n  Press Enter to see summary")
		summary += hint
	}

	list := lipgloss.JoinVertical(lipgloss.Left, items...)
	content := lipgloss.JoinVertical(
		lipgloss.Center,
		title,
		"",
		progress,
		activeLine,
		"",
		list,
		logSection,
		summary,
	)

	footer := styles.CommentStyle.Render("Ctrl+C to cancel")

	return lipgloss.Place(
		m.width, m.height,
		lipgloss.Center, lipgloss.Center,
		lipgloss.JoinVertical(lipgloss.Center, content, "", footer),
		lipgloss.WithWhitespaceBackground(styles.Primary),
	)
}

// --- Summary Model ---

type SummaryModel struct {
	success int
	failed  int
	errors  map[string]string
	width   int
	height  int
}

func NewSummaryModel(success, failed int, errors map[string]string) SummaryModel {
	return SummaryModel{success: success, failed: failed, errors: errors}
}

func (m SummaryModel) Init() tea.Cmd { return nil }

func (m SummaryModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
	case tea.KeyMsg:
		switch msg.String() {
		case "enter", "q", "esc":
			return NewWelcomeModel(), nil
		case "ctrl+c":
			return m, tea.Quit
		}
	}
	return m, nil
}

func (m SummaryModel) View() string {
	if m.width == 0 {
		m.width = 80
	}
	if m.height == 0 {
		m.height = 24
	}

	title := styles.TitleStyle.Render("📊 Installation Complete")
	separator := styles.CommentStyle.Render(strings.Repeat("─", 40))

	var lines []string
	if m.failed == 0 {
		lines = append(lines, styles.SuccessStyle.Render("  ✅ All components installed successfully!"))
	} else {
		lines = append(lines, styles.MenuItemStyle.Render(fmt.Sprintf(
			"  %d installed, %d failed", m.success, m.failed)))
		for comp, errMsg := range m.errors {
			lines = append(lines, styles.ErrorStyle.Render(fmt.Sprintf("  ❌ %s: %s", comp, errMsg)))
		}
	}

	// Next steps
	nextSteps := []string{
		"",
		styles.CommentStyle.Render("  📋 Next Steps:"),
		styles.CommentStyle.Render("  • Restart your terminal or run: source ~/.zshrc"),
		styles.CommentStyle.Render("  • Run 'dreamcoder-theme sync' to generate themes"),
		styles.CommentStyle.Render("  • Run 'dreamcoder doctor' for a health check"),
		"",
	}

	content := lipgloss.JoinVertical(
		lipgloss.Center,
		title,
		separator,
		"",
		lipgloss.JoinVertical(lipgloss.Left, lines...),
		lipgloss.JoinVertical(lipgloss.Left, nextSteps...),
		separator,
		styles.CommentStyle.Render("  Press Enter to return to menu"),
	)

	return lipgloss.Place(
		m.width, m.height,
		lipgloss.Center, lipgloss.Center,
		content,
		lipgloss.WithWhitespaceBackground(styles.Primary),
	)
}
