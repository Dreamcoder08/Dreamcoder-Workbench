package dotfiles

import (
	"errors"
	"os"
	"path/filepath"
	"strings"
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

// fakeDispatcher writes a fake scripts/dreamcoder into dotfilesDir that
// records its arguments and DREAMCODER_WRITE_LIVE, then exits with code.
func fakeDispatcher(t *testing.T, dotfilesDir string, code int) string {
	t.Helper()
	calls := filepath.Join(t.TempDir(), "calls")
	script := "#!/bin/sh\nprintf '%s|%s\\n' \"$*\" \"${DREAMCODER_WRITE_LIVE:-unset}\" >>\"" + calls + "\"\nexit " + string(rune('0'+code)) + "\n"
	if err := os.MkdirAll(filepath.Join(dotfilesDir, "scripts"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dotfilesDir, "scripts", "dreamcoder"), []byte(script), 0o755); err != nil {
		t.Fatal(err)
	}
	return calls
}

func TestGenerateMirrorsRunsRepoOnlySync(t *testing.T) {
	isolate(t)
	t.Setenv("DREAMCODER_WRITE_LIVE", "1")
	dir := t.TempDir()
	calls := fakeDispatcher(t, dir, 0)

	if err := GenerateMirrors(dir); err != nil {
		t.Fatalf("GenerateMirrors() = %v, want nil", err)
	}
	got, err := os.ReadFile(calls)
	if err != nil {
		t.Fatal(err)
	}
	if string(got) != "sync|0\n" {
		t.Fatalf("dispatcher calls = %q, want %q", got, "sync|0\n")
	}
}

func TestGenerateMirrorsFailsWhenSyncFails(t *testing.T) {
	isolate(t)
	dir := t.TempDir()
	fakeDispatcher(t, dir, 3)

	err := GenerateMirrors(dir)
	if err == nil {
		t.Fatal("GenerateMirrors() = nil, want error")
	}
	if !strings.Contains(err.Error(), "repo-only theme sync failed: active mirrors missing, refusing to stow") {
		t.Fatalf("GenerateMirrors() error = %q, want the refusing-to-stow message", err)
	}
}

func TestStowAfterMirrorsGeneratesBeforeStowing(t *testing.T) {
	isolate(t)
	dir := t.TempDir()
	calls := fakeDispatcher(t, dir, 0)
	stowed := false

	err := StowAfterMirrors(dir, func() error {
		if _, err := os.Stat(calls); err != nil {
			t.Fatalf("stow ran before mirror generation: %v", err)
		}
		stowed = true
		return nil
	})

	if err != nil || !stowed {
		t.Fatalf("StowAfterMirrors() = %v, stowed = %v; want nil, true", err, stowed)
	}
}

func TestStowAfterMirrorsDoesNotStowWhenGenerationFails(t *testing.T) {
	isolate(t)
	dir := t.TempDir()
	fakeDispatcher(t, dir, 1)
	stowed := false

	err := StowAfterMirrors(dir, func() error { stowed = true; return nil })

	if err == nil || stowed {
		t.Fatalf("StowAfterMirrors() = %v, stowed = %v; want error, false", err, stowed)
	}
}

func TestStowAfterMirrorsReturnsStowError(t *testing.T) {
	isolate(t)
	dir := t.TempDir()
	fakeDispatcher(t, dir, 0)
	want := errors.New("stow failed")

	if err := StowAfterMirrors(dir, func() error { return want }); !errors.Is(err, want) {
		t.Fatalf("StowAfterMirrors() = %v, want %v", err, want)
	}
}

func TestGenerateMirrorsTargetsItsOwnCheckout(t *testing.T) {
	isolate(t)
	dir := t.TempDir()
	t.Setenv("DREAMCODER_DOTS_DIR", t.TempDir())
	seen := filepath.Join(t.TempDir(), "dots-dir")
	script := "#!/bin/sh\nprintf '%s' \"${DREAMCODER_DOTS_DIR:-unset}\" >\"" + seen + "\"\n"
	if err := os.MkdirAll(filepath.Join(dir, "scripts"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, "scripts", "dreamcoder"), []byte(script), 0o755); err != nil {
		t.Fatal(err)
	}

	if err := GenerateMirrors(dir); err != nil {
		t.Fatalf("GenerateMirrors() = %v, want nil", err)
	}
	got, err := os.ReadFile(seen)
	if err != nil {
		t.Fatal(err)
	}
	if string(got) != dir {
		t.Fatalf("sync ran with DREAMCODER_DOTS_DIR=%q, want the target checkout %q", got, dir)
	}
}
