# Launch Checklist

Use this checklist as the final public open-source RC/MVP release snapshot.
The current state recorded below is aligned with:

- `docs/final_go_no_go.md`
- `docs/signoff_status.md`
- `docs/release_readiness_summary.md`
- `docs/stakeholder_review_pack.md`
- `docs/known_issues.md`

## 1) Validation Gates

- [x] `python -m pytest -q tests/test_contracts_smoke.py`
- [x] `python -m pytest -q tests/test_prompt_files.py`
- [x] `python -m pytest -q tests/test_rc_freeze_consistency.py`
- [x] `python -m pytest -q tests/test_final_rc_decision_consistency.py`
- [x] `python -m pytest -q`
- [x] `python -m compileall src tests`
- [x] `python -m build`

## 2) Prompt-Pack Presence and Consistency

- [x] `prompts/v1/*.md` files are present and non-empty.
- [x] SafetyGate prompt keywords still align with `SafetyDecision`.
- [x] CI prompt gate remains enabled.

## 3) Policy Pack Selection Verification

- [x] default behavior remains on `v1`.
- [x] explicit `v2` selection works.
- [x] invalid policy pack selection fails safely.
- [x] no silent switch from `v1` to `v2`.

## 4) Audit Integrity Verification

- [x] valid audit chain verification passes.
- [x] tampered chain detection fails explicitly with broken indices/errors.
- [x] service response surfaces integrity status clearly.

## 5) Rollback Readiness

- [x] rollback path to `v1` policy pack is documented (`docs/migration_guide_v2.md`).
- [x] rollback trigger conditions reviewed (`docs/rc_freeze_notes.md`).
- [x] known blockers reviewed (`docs/known_issues.md`).

## 6) Stakeholder Review and Signoff

- [x] stakeholder pack reviewed (`docs/stakeholder_review_pack.md`).
- [x] signoff status reviewed (`docs/signoff_status.md`).
- [x] final recommendation reviewed (`docs/final_go_no_go.md`).
- [x] readiness snapshot reviewed (`docs/release_readiness_summary.md`).
- [x] required owners recorded with decision fields.
- [x] final go/no-go decision captured.

## 7) Post-Launch Monitoring Expectations (Foundation Baseline)

- [x] observability counters/timers checked in guarded responses.
- [x] blocked-flow audit evidence confirmed.
- [x] no real side effects observed (dry-run-only posture intact).

## 8) Current Final Status

- Release posture: `RC/MVP`
- Recommendation: `GO`
- Signoff status: `APPROVED`
- RC blockers: none currently open
- Accepted limitations remain in force and are not reclassified as blockers
