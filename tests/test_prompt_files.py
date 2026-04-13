from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / "prompts" / "v1"
DOCKERFILE = ROOT / "infra" / "Dockerfile"
COMPOSE_FILE = ROOT / "infra" / "docker-compose.yml"
ENV_EXAMPLE = ROOT / "infra" / ".env.example"

EXPECTED_PROMPT_FILES = {
    "safety_gate_system_en.md",
    "safety_gate_system_ru.md",
    "policy_author_system_en.md",
    "policy_author_system_ru.md",
    "action_planner_system_en.md",
    "action_planner_system_ru.md",
    "executor_ui_system_en.md",
    "executor_ui_system_ru.md",
    "executor_api_system_en.md",
    "executor_api_system_ru.md",
    "approval_assistant_system_en.md",
    "approval_assistant_system_ru.md",
    "audit_writer_system_en.md",
    "audit_writer_system_ru.md",
}


def test_prompt_pack_v1_files_exist_and_are_non_empty():
    missing = [name for name in EXPECTED_PROMPT_FILES if not (PROMPTS_DIR / name).exists()]
    assert not missing, f"Missing prompt files: {missing}"

    for name in EXPECTED_PROMPT_FILES:
        content = (PROMPTS_DIR / name).read_text(encoding="utf-8").strip()
        assert content, f"Prompt file is empty: {name}"


def test_safety_gate_prompt_contains_required_contract_keywords():
    en = (PROMPTS_DIR / "safety_gate_system_en.md").read_text(encoding="utf-8")
    ru = (PROMPTS_DIR / "safety_gate_system_ru.md").read_text(encoding="utf-8")

    for content in (en, ru):
        assert "ALLOW" in content
        assert "DENY" in content
        assert "NEEDS_APPROVAL" in content
        assert "risk_score" in content
        assert "reasons" in content
        assert "constraints" in content
        assert "operator_checks" in content
        assert "JSON" in content

    assert "unknown or incomplete context => `NEEDS_APPROVAL`".lower() in en.lower()
    assert "Неизвестный или неполный контекст => `NEEDS_APPROVAL`".lower() in ru.lower()


def test_prompt_pack_en_ru_pairs_have_same_family_set():
    en_files = {path.name.replace("_en.md", "") for path in PROMPTS_DIR.glob("*_en.md")}
    ru_files = {path.name.replace("_ru.md", "") for path in PROMPTS_DIR.glob("*_ru.md")}
    assert en_files == ru_files
    assert en_files == {
        "safety_gate_system",
        "policy_author_system",
        "action_planner_system",
        "executor_ui_system",
        "executor_api_system",
        "approval_assistant_system",
        "audit_writer_system",
    }


def test_infra_files_exist_and_look_locally_plausible():
    assert DOCKERFILE.exists()
    assert COMPOSE_FILE.exists()
    assert ENV_EXAMPLE.exists()

    docker_text = DOCKERFILE.read_text(encoding="utf-8")
    compose_text = COMPOSE_FILE.read_text(encoding="utf-8")
    env_text = ENV_EXAMPLE.read_text(encoding="utf-8")

    assert "FROM python:3.11-slim" in docker_text
    assert "WORKDIR /app" in docker_text
    assert "uvicorn" in docker_text
    assert "src.api.app:app" in docker_text
    assert "USER safecore" in docker_text
    assert "HEALTHCHECK" in docker_text

    assert "services:" in compose_text
    assert "dockerfile: infra/Dockerfile" in compose_text
    assert "uvicorn src.api.app:app" in compose_text
    assert "ports:" in compose_text
    assert "${SAFECORE_API_PORT:-8000}:8000" in compose_text
    assert "env_file:" in compose_text
    assert "read_only: true" in compose_text
    assert "healthcheck:" in compose_text

    assert "SAFECORE_API_PORT=8000" in env_text
    assert "SAFECORE_APPROVAL_ESCALATE_AFTER_SECONDS=" in env_text
