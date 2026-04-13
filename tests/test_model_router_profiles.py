from src.model_router.profile_selector import ProfileSelector
from src.model_router.router import ModelRouter


def test_profile_selector_maps_low_risk_read_to_safe_low_risk():
    selector = ProfileSelector()
    selected = selector.select_profile(
        decision="ALLOW",
        risk_score=10,
        action_class="READ_ONLY",
        environment="dev",
    )

    assert selected["profile_id"] == "safe_low_risk"
    assert selected["profile_name"] == "Safe Low Risk"


def test_profile_selector_maps_prod_change_to_high_risk_review():
    selector = ProfileSelector()
    selected = selector.select_profile(
        decision="NEEDS_APPROVAL",
        risk_score=55,
        action_class="CHANGE",
        environment="production",
    )

    assert selected["profile_id"] == "high_risk_review"


def test_profile_selector_maps_deny_to_restricted_no_execute():
    selector = ProfileSelector()
    selected = selector.select_profile(
        decision="DENY",
        risk_score=90,
        action_class="DESTRUCTIVE",
        environment="prod",
    )

    assert selected["profile_id"] == "restricted_no_execute"


def test_router_response_contains_profile_metadata():
    router = ModelRouter()
    route = router.route(
        policy_decision={"decision": "ALLOW", "risk_score": 20},
        context={"action": "read_status", "tool": "shell", "command": "ls", "environment": "dev"},
    )

    assert route["route_id"] == "route_allow_fast_read"
    assert route["model_profile"] == "safe_fast_read"
    assert route["profile_id"] == "safe_low_risk"
    assert route["profile_guardrails"]


def test_profile_selection_is_deterministic():
    selector = ProfileSelector()
    first = selector.select_profile(
        decision="NEEDS_APPROVAL",
        risk_score=55,
        action_class="CHANGE",
        environment="production",
    )
    second = selector.select_profile(
        decision="NEEDS_APPROVAL",
        risk_score=55,
        action_class="CHANGE",
        environment="production",
    )
    assert first == second

