import pytest

from src.policy.policy_engine import DECISION_ALLOW, DECISION_DENY, POLICY_PACK_V1, PolicyEngine


def test_policy_engine_load_rules_by_pack():
    engine = PolicyEngine(opa_binary="definitely-not-opa")
    v1_names = {path.name for path in engine.load_rules(policy_pack="v1")}
    v2_names = {path.name for path in engine.load_rules(policy_pack="v2")}

    assert "base.rego" in v1_names
    assert "base_v2.rego" in v2_names
    assert all(not name.endswith("_v2.rego") for name in v1_names)


def test_policy_pack_v2_is_opt_in_and_default_stays_v1():
    engine = PolicyEngine(opa_binary="definitely-not-opa")
    request = {
        "action": "deploy_service",
        "tool": "config_reader",
        "command": "",
        "environment": "prod",
        "params": {},
    }

    default_result = engine.evaluate(request)
    explicit_v1_result = engine.evaluate(request, policy_pack=POLICY_PACK_V1)
    explicit_v2_result = engine.evaluate(request, policy_pack="v2")

    assert default_result == explicit_v1_result
    assert default_result["decision"] != explicit_v2_result["decision"]
    assert default_result["decision"] == "NEEDS_APPROVAL"
    assert explicit_v2_result["decision"] == DECISION_DENY


def test_policy_pack_v2_denies_shell_chaining_command():
    engine = PolicyEngine(opa_binary="definitely-not-opa")
    request = {
        "action": "read_status",
        "tool": "shell",
        "command": "ls && pwd",
        "environment": "dev",
    }

    v1_result = engine.evaluate(request, policy_pack="v1")
    v2_result = engine.evaluate(request, policy_pack="v2")

    assert v1_result["decision"] == DECISION_ALLOW
    assert v2_result["decision"] == DECISION_DENY


def test_policy_engine_rejects_unknown_policy_pack():
    engine = PolicyEngine(opa_binary="definitely-not-opa")
    with pytest.raises(ValueError, match="Unsupported policy_pack"):
        engine.evaluate({"action": "read_status", "tool": "shell", "command": "ls"}, policy_pack="v3")

