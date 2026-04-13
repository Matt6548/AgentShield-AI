from src.model_router import ModelRouter


def test_model_router_safe_read_routes_to_fast_profile():
    router = ModelRouter()
    route = router.route(
        policy_decision={"decision": "ALLOW", "risk_score": 20},
        context={"action": "read_status", "tool": "shell", "command": "ls", "environment": "dev"},
    )

    assert route["route_id"] == "route_allow_fast_read"
    assert route["model_profile"] == "safe_fast_read"
    assert route["action_class"] == "READ_ONLY"


def test_model_router_prod_change_routes_to_strict_approval_profile():
    router = ModelRouter()
    route = router.route(
        policy_decision={"decision": "NEEDS_APPROVAL", "risk_score": 55},
        context={
            "action": "change_config",
            "tool": "config_reader",
            "command": "",
            "environment": "production",
        },
    )

    assert route["route_id"] == "route_approval_prod_change"
    assert route["model_profile"] == "review_strict"
    assert "approval" in route["constraints"][0].lower()


def test_model_router_deny_routes_to_deny_guard_profile():
    router = ModelRouter()
    route = router.route(
        policy_decision={"decision": "DENY", "risk_score": 90},
        context={"action": "delete_everything", "tool": "shell", "command": "rm -rf /"},
    )

    assert route["route_id"] == "route_deny_guard"
    assert route["model_profile"] == "deny_guard"


def test_model_router_is_deterministic_for_same_inputs():
    router = ModelRouter()
    policy = {"decision": "ALLOW", "risk_score": 10}
    context = {"action": "read_status", "tool": "shell", "command": "pwd", "environment": "dev"}

    first = router.route(policy_decision=policy, context=context)
    second = router.route(policy_decision=policy, context=context)

    assert first == second

