package dotfiles

import (
	"os"
	"path/filepath"
	"testing"
)

func makeRepo(t *testing.T, dir string) {
	t.Helper()
	if err := os.MkdirAll(filepath.Join(dir, ".git"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, "Makefile"), nil, 0o644); err != nil {
		t.Fatal(err)
	}
}

func isolate(t *testing.T) string {
	t.Helper()
	home := t.TempDir()
	t.Setenv("HOME", home)
	t.Setenv("DREAMCODER_DIR", "")
	t.Chdir(t.TempDir())
	return home
}

func TestFindDotfilesDirOrDefaultUsesWorkbenchLocation(t *testing.T) {
	home := isolate(t)

	got := FindDotfilesDirOrDefault(home)

	want := filepath.Join(home, "Documents", "PROYECTOS", "dreamcoder08", "dreamcoder-workbench")
	if got != want {
		t.Fatalf("FindDotfilesDirOrDefault() = %q, want %q", got, want)
	}
}

func TestFindDotfilesDirPrefersWorkbenchOverLegacyLocation(t *testing.T) {
	home := isolate(t)
	current := filepath.Join(home, "Documents", "PROYECTOS", "dreamcoder08", "dreamcoder-workbench")
	legacy := filepath.Join(home, "Documents", "PROYECTOS", "dreamcoder-dots")
	makeRepo(t, current)
	makeRepo(t, legacy)

	got, err := FindDotfilesDir()

	if err != nil || got != current {
		t.Fatalf("FindDotfilesDir() = %q, %v; want %q", got, err, current)
	}
}

func TestFindDotfilesDirKeepsLegacyLocationAsFallback(t *testing.T) {
	home := isolate(t)
	legacy := filepath.Join(home, "Documents", "PROYECTOS", "dreamcoder-dots")
	makeRepo(t, legacy)

	got, err := FindDotfilesDir()

	if err != nil || got != legacy {
		t.Fatalf("FindDotfilesDir() = %q, %v; want %q", got, err, legacy)
	}
}
