# rule_id: v2.privileged_ops
package safecore

import rego.v1

privileged_identities := {"root", "admin", "administrator", "system"}
destructive_action_markers := {"delete", "destroy", "drop", "truncate", "wipe", "shutdown", "reboot"}
destructive_command_markers := {"rm -rf", "mkfs", "dd if=", "format", "del /f"}
mutation_markers := {"delete", "modify", "update", "deploy", "restart", "write"}

deny_privileged_operation_v2 if {
	action := lower(sprintf("%v", [object.get(input, "action", "")]))
	some marker in destructive_action_markers
	contains(action, marker)
}

deny_privileged_operation_v2 if {
	command := lower(sprintf("%v", [object.get(input, "command", "")]))
	some marker in destructive_command_markers
	contains(command, marker)
}

deny_privileged_operation_v2 if {
	user := lower(sprintf("%v", [object.get(input, "user", object.get(input, "actor", ""))]))
	user in privileged_identities
	action := lower(sprintf("%v", [object.get(input, "action", "")]))
	some marker in mutation_markers
	contains(action, marker)
}

