# rule_id: v2.production_change
package safecore

import rego.v1

production_envs := {"prod", "production"}
change_markers := {"change", "update", "modify", "deploy", "restart", "write", "delete"}

needs_approval_production_change_v2 if {
	is_production_change_v2
}

deny_production_change_without_ticket_v2 if {
	is_production_change_v2
	not has_change_ticket_v2
}

is_production_change_v2 if {
	env := lower(sprintf("%v", [object.get(input, "environment", object.get(input, "env", ""))]))
	env in production_envs
	action := lower(sprintf("%v", [object.get(input, "action", "")]))
	some marker in change_markers
	contains(action, marker)
}

has_change_ticket_v2 if {
	params := object.get(input, "params", {})
	raw_ticket := object.get(params, "change_ticket", "")
	ticket := trim_space(sprintf("%v", [raw_ticket]))
	ticket != ""
}

has_change_ticket_v2 if {
	payload := object.get(input, "payload", {})
	approved := object.get(payload, "approved_change", false)
	approved == true
}

