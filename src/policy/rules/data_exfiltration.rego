package safecore

import rego.v1

deny_exfiltration if {
	action := lower(sprintf("%v", [object.get(input, "action", "")]))
	contains(action, "export")
	contains(external_target, "http://")
}

deny_exfiltration if {
	action := lower(sprintf("%v", [object.get(input, "action", "")]))
	contains(action, "upload")
	contains(external_target, "https://")
}

deny_exfiltration if {
	command := lower(sprintf("%v", [object.get(input, "command", "")]))
	contains(command, "curl ")
	contains(command, "http")
}

deny_exfiltration if {
	command := lower(sprintf("%v", [object.get(input, "command", "")]))
	contains(command, "wget ")
	contains(command, "http")
}

needs_approval if {
	env := lower(sprintf("%v", [object.get(input, "environment", object.get(input, "env", ""))]))
	action := lower(sprintf("%v", [object.get(input, "action", "")]))
	env == "prod"
	contains(action, "change")
}

needs_approval if {
	env := lower(sprintf("%v", [object.get(input, "environment", object.get(input, "env", ""))]))
	action := lower(sprintf("%v", [object.get(input, "action", "")]))
	env == "production"
	contains(action, "deploy")
}

external_target := lower(sprintf("%v", [object.get(input, "target", object.get(input, "target_system", ""))]))

