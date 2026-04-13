# Prompt Pack v1

SafeCore Prompt Pack v1 defines versioned system-prompt artifacts for key control-plane roles.

## Scope

- Prompts are specification artifacts in this iteration.
- Prompts are not fully wired into runtime execution yet.
- Prompt content is strict and reusable for later integration.

## Prompt Families

- `safety_gate_system_en.md` / `safety_gate_system_ru.md`
  - Contract-aligned SafetyDecision generation.
- `policy_author_system_en.md` / `policy_author_system_ru.md`
  - Deterministic policy/rule drafting guidance.
- `action_planner_system_en.md` / `action_planner_system_ru.md`
  - Safe step planning guidance.
- `executor_ui_system_en.md` / `executor_ui_system_ru.md`
  - Operator-facing execution summary format.
- `executor_api_system_en.md` / `executor_api_system_ru.md`
  - Guarded API payload construction guidance.
- `approval_assistant_system_en.md` / `approval_assistant_system_ru.md`
  - Human approval recommendation support.
- `audit_writer_system_en.md` / `audit_writer_system_ru.md`
  - AuditRecord-aligned event writing format.

## Language Alignment

- EN and RU files are paired by role and version.
- RU wording must preserve EN constraints and strictness.

## Usage Note

Prompts should be treated as versioned interface specs. Runtime modules can adopt them later through explicit wiring.

