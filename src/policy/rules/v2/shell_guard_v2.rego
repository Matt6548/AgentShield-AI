# rule_id: v2.shell_guard
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

deny_shell_command_v2 if {
	tool := lower(sprintf("%v", [object.get(input, "tool", "")]))
	tool in shell_tools
	command := lower(trim_space(sprintf("%v", [object.get(input, "command", "")])))
	command == ""
}

deny_shell_command_v2 if {
	tool := lower(sprintf("%v", [object.get(input, "tool", "")]))
	tool in shell_tools
	command := lower(trim_space(sprintf("%v", [object.get(input, "command", "")])))
	not safe_shell_command_v2(command)
}

deny_shell_command_v2 if {
	tool := lower(sprintf("%v", [object.get(input, "tool", "")]))
	tool in shell_tools
	command := lower(trim_space(sprintf("%v", [object.get(input, "command", "")])))
	contains_command_chaining_v2(command)
}

safe_shell_command_v2(command) if {
	command != ""
	prefix := split(command, " ")[0]
	prefix in safe_shell_prefixes
}

contains_command_chaining_v2(command) if contains(command, "&&")
contains_command_chaining_v2(command) if contains(command, "||")
contains_command_chaining_v2(command) if contains(command, ";")
contains_command_chaining_v2(command) if contains(command, "|")
contains_command_chaining_v2(command) if contains(command, ">")
contains_command_chaining_v2(command) if contains(command, "<")
contains_command_chaining_v2(command) if contains(command, "$(")
contains_command_chaining_v2(command) if contains(command, "`")

