from pathlib import Path

from src.policy.policy_engine import (
    DECISION_ALLOW,
    DECISION_DENY,
    DECISION_NEEDS_APPROVAL,
    PolicyEngine,
)


def test_policy_engine_initializes_with_defaults():
    engine = PolicyEngine(opa_binary="definitely-not-opa")
    assert engine.rules_path.name == "rules"
    assert engine.opa_available is False


def test_load_rules_returns_rego_files_without_crashing():
    engine = PolicyEngine(opa_binary="definitely-not-opa")
    rules = engine.load_rules()
    rule_names = {rule.name for rule in rules}
    assert {"base.rego", "data_exfiltration.rego", "shell_guard.rego"} <= rule_names


def test_safe_read_action_returns_allow():
    engine = PolicyEngine(opa_binary="definitely-not-opa")
    decision = engine.evaluate(
        {
            "action": "read_config",
            "tool": "config_reader",
            "params": {"key": "feature_flag"},
            "user": "analyst",
            "environment": "dev",
        }
    )
    assert decision["decision"] == DECISION_ALLOW
    assert 0 <= decision["risk_score"] <= 33


def test_suspicious_external_transfer_is_not_allow():
    engine = PolicyEngine(opa_binary="definitely-not-opa")
    decision = engine.evaluate(
        {
            "action": "export_data",
            "tool": "http_client",
            "target": "https://external.example/upload",
            "params": {"destination": "https://external.example/upload"},
            "user": "service_account",
        }
    )
    assert decision["decision"] in {DECISION_NEEDS_APPROVAL, DECISION_DENY}
    assert decision["risk_score"] >= 34


def test_unsafe_shell_command_returns_deny():
    engine = PolicyEngine(opa_binary="definitely-not-opa")
    decision = engine.evaluate(
        {
            "action": "execute",
            "tool": "shell",
            "command": "rm -rf /",
            "user": "operator",
            "environment": "dev",
        }
    )
    assert decision["decision"] == DECISION_DENY
    assert decision["risk_score"] >= 67


def test_result_always_matches_safetydecision_shape():
    engine = PolicyEngine(opa_binary="definitely-not-opa")
    decision = engine.evaluate({"action": "list_resources", "tool": "inventory"})

    assert set(decision.keys()) == {
        "decision",
        "risk_score",
        "reasons",
        "constraints",
        "operator_checks",
    }
    assert decision["decision"] in {DECISION_ALLOW, DECISION_DENY, DECISION_NEEDS_APPROVAL}
    assert isinstance(decision["risk_score"], int)
    assert 0 <= decision["risk_score"] <= 100
    assert isinstance(decision["reasons"], list)
    assert isinstance(decision["constraints"], list)
    assert isinstance(decision["operator_checks"], list)
    assert all(isinstance(item, str) for item in decision["reasons"])
    assert all(isinstance(item, str) for item in decision["constraints"])
    assert all(isinstance(item, str) for item in decision["operator_checks"])


def test_missing_rules_path_does_not_crash_load_rules():
    missing_path = Path("tests/nonexistent_rules_dir")
    engine = PolicyEngine(rules_path=missing_path, opa_binary="definitely-not-opa")
    assert engine.load_rules() == []

