# rule_id: v2.network_egress
package safecore

import rego.v1

egress_markers := {
	"curl ",
	"wget ",
	"scp ",
	"ftp://",
	"http://",
	"https://",
	"s3://",
	"upload",
	"transfer",
	"send",
	"sync",
	"exfil",
}

deny_network_egress_v2 if {
	command := lower(sprintf("%v", [object.get(input, "command", "")]))
	some marker in egress_markers
	contains(command, marker)
}

deny_network_egress_v2 if {
	action := lower(sprintf("%v", [object.get(input, "action", "")]))
	target := lower(sprintf("%v", [object.get(input, "target", object.get(input, "target_system", ""))]))
	contains(action, "upload")
	contains(target, "http")
}

deny_network_egress_v2 if {
	action := lower(sprintf("%v", [object.get(input, "action", "")]))
	target := lower(sprintf("%v", [object.get(input, "target", object.get(input, "target_system", ""))]))
	contains(action, "export")
	contains(target, "s3://")
}

deny_network_egress_v2 if {
	params := lower(sprintf("%v", [object.get(input, "params", {})]))
	some marker in {"http://", "https://", "s3://", "ftp://"}
	contains(params, marker)
	contains(params, "destination")
}

