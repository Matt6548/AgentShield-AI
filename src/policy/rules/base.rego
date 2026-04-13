package safecore

import rego.v1

default risk_score := 10
default reasons := ["No blocking policy matched."]
default constraints := []
default operator_checks := []

risk_score := 95 if deny_shell_command
risk_score := 75 if {
	not deny_shell_command
	deny_privileged_operation
}
risk_score := 75 if {
	not deny_shell_command
	not deny_privileged_operation
	deny_network_egress
}
risk_score := 75 if {
	not deny_shell_command
	not deny_privileged_operation
	not deny_network_egress
	deny_exfiltration
}
risk_score := 55 if {
	not deny_shell_command
	not deny_privileged_operation
	not deny_network_egress
	not deny_exfiltration
	needs_approval_production_change
}
risk_score := 55 if {
	not deny_shell_command
	not deny_privileged_operation
	not deny_network_egress
	not deny_exfiltration
	not needs_approval_production_change
	needs_approval
}

reasons := ["Unsafe shell command blocked by shell_guard.rego."] if deny_shell_command
reasons := ["Privileged or destructive operation blocked by privileged_ops.rego."] if {
	not deny_shell_command
	deny_privileged_operation
}
reasons := ["Suspicious network egress blocked by network_egress.rego."] if {
	not deny_shell_command
	not deny_privileged_operation
	deny_network_egress
}
reasons := ["Potential data exfiltration pattern detected."] if {
	not deny_shell_command
	not deny_privileged_operation
	not deny_network_egress
	deny_exfiltration
}
reasons := ["Production change requires operator review."] if {
	not deny_shell_command
	not deny_privileged_operation
	not deny_network_egress
	not deny_exfiltration
	needs_approval_production_change
}
reasons := ["Action requires operator review under baseline policy."] if {
	not deny_shell_command
	not deny_privileged_operation
	not deny_network_egress
	not deny_exfiltration
	not needs_approval_production_change
	needs_approval
}

constraints := ["Block execution until command is in allowlist."] if deny_shell_command
constraints := ["Block privileged/destructive operation by default policy."] if {
	not deny_shell_command
	deny_privileged_operation
}
constraints := ["Block suspicious network egress until explicitly allowlisted."] if {
	not deny_shell_command
	not deny_privileged_operation
	deny_network_egress
}
constraints := ["Hold outbound transfer until destination is approved."] if {
	not deny_shell_command
	not deny_privileged_operation
	not deny_network_egress
	deny_exfiltration
}
constraints := ["Queue production change for human review before execution."] if {
	not deny_shell_command
	not deny_privileged_operation
	not deny_network_egress
	not deny_exfiltration
	needs_approval_production_change
}
constraints := ["Queue action for human review before execution."] if {
	not deny_shell_command
	not deny_privileged_operation
	not deny_network_egress
	not deny_exfiltration
	not needs_approval_production_change
	needs_approval
}

operator_checks := ["Confirm command intent and least privilege."] if deny_shell_command
operator_checks := ["Confirm privileged intent and rollback safety before retry."] if {
	not deny_shell_command
	deny_privileged_operation
}
operator_checks := ["Verify destination ownership and egress policy exceptions."] if {
	not deny_shell_command
	not deny_privileged_operation
	deny_network_egress
}
operator_checks := ["Validate business need and approved destination."] if {
	not deny_shell_command
	not deny_privileged_operation
	not deny_network_egress
	deny_exfiltration
}
operator_checks := ["Operator approval required before production change."] if {
	not deny_shell_command
	not deny_privileged_operation
	not deny_network_egress
	not deny_exfiltration
	needs_approval_production_change
}
operator_checks := ["Operator approval required before execution."] if {
	not deny_shell_command
	not deny_privileged_operation
	not deny_network_egress
	not deny_exfiltration
	not needs_approval_production_change
	needs_approval
}

decision := {
	"decision": classify_decision(risk_score),
	"risk_score": risk_score,
	"reasons": reasons,
	"constraints": constraints,
	"operator_checks": operator_checks,
}

classify_decision(score) := "ALLOW" if score <= 33
classify_decision(score) := "NEEDS_APPROVAL" if {
	score >= 34
	score <= 66
}
classify_decision(score) := "DENY" if score >= 67
