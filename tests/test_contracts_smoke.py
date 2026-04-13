import json
from pathlib import Path

from jsonschema.validators import validator_for


CONTRACTS_DIR = Path(__file__).resolve().parents[1] / "contracts"
EXPECTED_CONTRACTS = {
    "Run.json",
    "Step.json",
    "SafetyDecision.json",
    "ToolCall.json",
    "AuditRecord.json",
}


def test_contract_files_exist_and_are_json_schema_valid():
    schema_paths = sorted(CONTRACTS_DIR.glob("*.json"))
    assert {path.name for path in schema_paths} == EXPECTED_CONTRACTS

    for schema_path in schema_paths:
        with schema_path.open("r", encoding="utf-8") as f:
            schema = json.load(f)

        validator_cls = validator_for(schema)
        validator_cls.check_schema(schema)

