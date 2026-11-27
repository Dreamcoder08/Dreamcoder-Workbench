package cmd

import "github.com/spf13/cobra"

var rootCmd = &cobra.Command{
	Use:   "dreamcoder-dots",
	Short: "Dreamcoder Workbench - Token-governed visual operating layer",
}

func RootCmd() *cobra.Command {
	return rootCmd
}
