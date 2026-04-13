# rule_id: v2.data_exfiltration
package safecore

import rego.v1

sensitive_markers := {"token", "secret", "password", "ssn", "credit_card", "customer_pii", "api_key"}
external_markers := {"http://", "https://", "s3://", "ftp://"}

deny_exfiltration_v2 if {
	payload := lower(sprintf("%v", [object.get(input, "payload", {})]))
	some marker in sensitive_markers
	contains(payload, marker)
	target := lower(sprintf("%v", [object.get(input, "target", object.get(input, "target_system", ""))]))
	some external in external_markers
	contains(target, external)
}

deny_exfiltration_v2 if {
	params := lower(sprintf("%v", [object.get(input, "params", {})]))
	some marker in sensitive_markers
	contains(params, marker)
	command := lower(sprintf("%v", [object.get(input, "command", "")]))
	some external in external_markers
	contains(command, external)
}

