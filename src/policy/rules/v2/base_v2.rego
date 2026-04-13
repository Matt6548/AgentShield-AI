# rule_id: v2.base
package safecore

import rego.v1

default risk_score := 10
default reasons := ["No blocking policy matched (policy pack v2)."]
default constraints := []
default operator_checks := []

risk_score := 95 if deny_shell_command_v2
risk_score := 90 if {
	not deny_shell_command_v2
	deny_privileged_operation_v2
}
risk_score := 85 if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	deny_network_egress_v2
}
risk_score := 80 if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	not deny_network_egress_v2
	deny_exfiltration_v2
}
risk_score := 70 if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	not deny_network_egress_v2
	not deny_exfiltration_v2
	deny_production_change_without_ticket_v2
}
risk_score := 55 if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	not deny_network_egress_v2
	not deny_exfiltration_v2
	not deny_production_change_without_ticket_v2
	needs_approval_production_change_v2
}
risk_score := 45 if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	not deny_network_egress_v2
	not deny_exfiltration_v2
	not deny_production_change_without_ticket_v2
	not needs_approval_production_change_v2
	needs_approval_unknown_context_v2
}

reasons := ["Shell command is blocked by shell_guard_v2.rego."] if deny_shell_command_v2
reasons := ["Privileged or destructive operation is blocked by privileged_ops_v2.rego."] if {
	not deny_shell_command_v2
	deny_privileged_operation_v2
}
reasons := ["Suspicious network egress is blocked by network_egress_v2.rego."] if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	deny_network_egress_v2
}
reasons := ["Sensitive payload exfiltration pattern is blocked by data_exfiltration_v2.rego."] if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	not deny_network_egress_v2
	deny_exfiltration_v2
}
reasons := ["Production change request is missing change ticket metadata."] if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	not deny_network_egress_v2
	not deny_exfiltration_v2
	deny_production_change_without_ticket_v2
}
reasons := ["Production change requires explicit approval."] if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	not deny_network_egress_v2
	not deny_exfiltration_v2
	not deny_production_change_without_ticket_v2
	needs_approval_production_change_v2
}
reasons := ["Context is incomplete; request requires approval in policy pack v2."] if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	not deny_network_egress_v2
	not deny_exfiltration_v2
	not deny_production_change_without_ticket_v2
	not needs_approval_production_change_v2
	needs_approval_unknown_context_v2
}

constraints := ["Only allow listed read-only shell commands without chaining."] if deny_shell_command_v2
constraints := ["Block privileged/destructive operations by default."] if {
	not deny_shell_command_v2
	deny_privileged_operation_v2
}
constraints := ["Block outbound network egress until destination is approved."] if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	deny_network_egress_v2
}
constraints := ["Block sensitive payload transfer to external destination."] if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	not deny_network_egress_v2
	deny_exfiltration_v2
}
constraints := ["Require change ticket metadata for production mutations."] if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	not deny_network_egress_v2
	not deny_exfiltration_v2
	deny_production_change_without_ticket_v2
}
constraints := ["Queue production change for approval before execution."] if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	not deny_network_egress_v2
	not deny_exfiltration_v2
	not deny_production_change_without_ticket_v2
	needs_approval_production_change_v2
}
constraints := ["Require explicit human review when context is incomplete."] if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	not deny_network_egress_v2
	not deny_exfiltration_v2
	not deny_production_change_without_ticket_v2
	not needs_approval_production_change_v2
	needs_approval_unknown_context_v2
}

operator_checks := ["Validate shell command intent and exact command text."] if deny_shell_command_v2
operator_checks := ["Confirm privileged operation necessity and rollback plan."] if {
	not deny_shell_command_v2
	deny_privileged_operation_v2
}
operator_checks := ["Validate destination ownership and approved egress path."] if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	deny_network_egress_v2
}
operator_checks := ["Confirm data classification and outbound transfer exception."] if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	not deny_network_egress_v2
	deny_exfiltration_v2
}
operator_checks := ["Provide change ticket before production mutation."] if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	not deny_network_egress_v2
	not deny_exfiltration_v2
	deny_production_change_without_ticket_v2
}
operator_checks := ["Approval required for production mutation."] if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	not deny_network_egress_v2
	not deny_exfiltration_v2
	not deny_production_change_without_ticket_v2
	needs_approval_production_change_v2
}
operator_checks := ["Add missing context fields before retry."] if {
	not deny_shell_command_v2
	not deny_privileged_operation_v2
	not deny_network_egress_v2
	not deny_exfiltration_v2
	not deny_production_change_without_ticket_v2
	not needs_approval_production_change_v2
	needs_approval_unknown_context_v2
}

needs_approval_unknown_context_v2 if {
	tool := lower(trim_space(sprintf("%v", [object.get(input, "tool", "")])))
	tool == ""
}

needs_approval_unknown_context_v2 if {
	action := lower(trim_space(sprintf("%v", [object.get(input, "action", "")])))
	action == ""
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

