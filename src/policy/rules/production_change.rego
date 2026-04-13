package safecore

import rego.v1

production_envs := {"prod", "production"}
change_markers := {"change", "update", "modify", "deploy", "restart", "write", "delete"}

needs_approval_production_change if {
	env := lower(sprintf("%v", [object.get(input, "environment", object.get(input, "env", ""))]))
	env in production_envs
	action := lower(sprintf("%v", [object.get(input, "action", "")]))
	some marker in change_markers
	contains(action, marker)
}

