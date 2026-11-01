package installer

import (
	"path/filepath"
	"testing"
)

func TestNewInstallerDefaultsToWorkbenchLocation(t *testing.T) {
	home := t.TempDir()
	t.Setenv("HOME", home)

	got := NewInstaller(Platform{}, nil, "dark").DotfilesDir

	want := filepath.Join(home, "Documents", "PROYECTOS", "dreamcoder08", "dreamcoder-workbench")
	if got != want {
		t.Fatalf("DotfilesDir = %q, want %q", got, want)
	}
}
