package safecore

import rego.v1

shell_tools := {"shell", "bash", "sh", "cmd", "powershell", "terminal"}

safe_shell_prefixes := {
	"ls",
	"cat",
	"echo",
	"pwd",
	"whoami",
	"id",
	"date",
	"head",
	"tail",
	"grep",
	"find",
}

deny_shell_command if {
	tool := lower(sprintf("%v", [object.get(input, "tool", "")]))
	tool in shell_tools
	command := lower(trim_space(sprintf("%v", [object.get(input, "command", "")])))
	not safe_shell_command(command)
}

safe_shell_command(command) if {
	command != ""
	prefix := split(command, " ")[0]
	prefix in safe_shell_prefixes
}

