# NotebookLM Source Pack

Use this pack when you want NotebookLM to understand SafeCore quickly without drifting into claims the repository does not support.

## Recommended Files To Upload

Upload these first:

1. `README.md`
2. `docs/visual_story.md`
3. `docs/architecture_visual.md`
4. `docs/demo_quickstart.md`
5. `docs/demo_scenarios.md`
6. `docs/demo_value.md`
7. `docs/professional_positioning.md`
8. `docs/open_source_scope.md`
9. `docs/release_readiness_summary.md`
10. `docs/final_go_no_go.md`

## Why Each File Matters

- `README.md`
  - main public identity and quick understanding
- `docs/visual_story.md`
  - short narrative explaining why a control layer matters
- `docs/architecture_visual.md`
  - fast architectural understanding
- `docs/demo_quickstart.md`
  - exact local run path
- `docs/demo_scenarios.md`
  - compact `ALLOW / NEEDS_APPROVAL / DENY` matrix
- `docs/demo_value.md`
  - plain-language value explanation
- `docs/professional_positioning.md`
  - audience and professional value framing
- `docs/open_source_scope.md`
  - honest scope boundaries
- `docs/release_readiness_summary.md`
  - current validated state
- `docs/final_go_no_go.md`
  - final release posture and explicit recommendation

## Files Usually Not Needed For First-Pass NotebookLM Context

Do not upload these in the first round unless you need deeper detail:

- `src/` implementation files
- `tests/` files
- `docs/launch_checklist.md`
- `docs/handoff_pack.md`
- `docs/operations_runbook.md`
- `prompts/v1/` files
- workflow files under `.github/workflows/`

They are useful later, but they are not the cleanest first-pass public narrative.

## Recommended Upload Order

1. `README.md`
2. `docs/visual_story.md`
3. `docs/architecture_visual.md`
4. `docs/demo_quickstart.md`
5. `docs/demo_scenarios.md`
6. `docs/demo_value.md`
7. `docs/professional_positioning.md`
8. `docs/open_source_scope.md`
9. `docs/release_readiness_summary.md`
10. `docs/final_go_no_go.md`

## How To Preserve Honest Positioning

When using NotebookLM, keep these framing rules explicit:

- describe SafeCore as an open-source RC/MVP validated core
- describe it as a security/control layer for agent execution
- do not describe it as a production-ready platform
- do not imply real external side effects are enabled
- do not imply enterprise operating depth that the repository does not claim

## Short Framing Prompt

If you want a short framing instruction for NotebookLM, use:

"Summarize SafeCore as a control layer for AI agents. Keep the positioning honest: open-source RC/MVP, validated core, dry-run-first posture, not a production-ready platform."
