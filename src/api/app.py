"""FastAPI app skeleton for SafeCore guarded dry-run execution."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.demo_ui import (
    build_ui_content,
    build_product_shell_approval_queue,
    build_product_shell_audit_view,
    build_product_shell_history,
    build_product_shell_view,
    run_demo_scenario,
    run_reference_product_flow,
    run_safe_http_example,
)
from src.api.provider_status import build_provider_status
from src.api.safety_copilot import AssistantInsightRequest, SafetyCopilotService
from src.api.schemas import GuardedExecutionRequest, GuardedExecutionResponse, HealthResponse
from src.api.service import GuardedExecutionService


UI_DIR = Path(__file__).resolve().parent / "ui"


def create_app(
    service: GuardedExecutionService | None = None,
    *,
    demo_ui_audit_dir: Path | None = None,
    product_shell_store_path: Path | None = None,
    safety_copilot: SafetyCopilotService | None = None,
) -> FastAPI:
    """Create and configure the SafeCore API application."""
    app = FastAPI(title="SafeCore API", version="0.1.0")
    app.state.guarded_service = service or GuardedExecutionService()
    app.state.demo_ui_audit_dir = demo_ui_audit_dir
    app.state.product_shell_store_path = product_shell_store_path
    app.state.safety_copilot = safety_copilot or SafetyCopilotService()
    app.mount("/ui-assets", StaticFiles(directory=UI_DIR), name="ui-assets")

    @app.get("/health", response_model=HealthResponse)
    def health() -> dict[str, object]:
        return {"status": "ok", "service": "safecore-api", "dry_run_only": True}

    @app.get("/ui", include_in_schema=False)
    def demo_ui() -> FileResponse:
        return FileResponse(UI_DIR / "index.html")

    @app.get("/v1/demo-ui/content")
    def demo_ui_content(lang: str | None = None) -> dict[str, object]:
        return build_ui_content(lang=lang)

    @app.get("/v1/demo-ui/scenarios")
    def demo_ui_scenarios(lang: str | None = None) -> dict[str, object]:
        content = build_ui_content(lang=lang)
        return {"scenarios": content["demo"]["scenarios"]}

    @app.get("/v1/demo-ui/scenarios/{scenario_name}")
    def demo_ui_run_scenario(scenario_name: str, lang: str | None = None) -> dict[str, object]:
        return run_demo_scenario(
            scenario_name,
            audit_dir=app.state.demo_ui_audit_dir,
            product_shell_store_path=app.state.product_shell_store_path,
            lang=lang,
        )

    @app.get("/v1/demo-ui/integration-examples")
    def demo_ui_integration_examples(lang: str | None = None) -> dict[str, object]:
        content = build_ui_content(lang=lang)
        return {"examples": content["safe_integration"]["examples"]}

    @app.get("/v1/demo-ui/integration-examples/{example_name}")
    def demo_ui_run_integration_example(example_name: str, lang: str | None = None) -> dict[str, object]:
        return run_safe_http_example(
            example_name,
            audit_dir=app.state.demo_ui_audit_dir,
            product_shell_store_path=app.state.product_shell_store_path,
            lang=lang,
        )

    @app.get("/v1/demo-ui/reference-product-flows")
    def demo_ui_reference_product_flows(lang: str | None = None) -> dict[str, object]:
        content = build_ui_content(lang=lang)
        return {"flows": content["reference_product"]["flows"]}

    @app.get("/v1/demo-ui/reference-product-flows/{flow_name}")
    def demo_ui_run_reference_product_flow(flow_name: str, lang: str | None = None) -> dict[str, object]:
        return run_reference_product_flow(
            flow_name,
            audit_dir=app.state.demo_ui_audit_dir,
            product_shell_store_path=app.state.product_shell_store_path,
            lang=lang,
        )

    @app.get("/v1/demo-ui/product-shell")
    def demo_ui_product_shell(lang: str | None = None) -> dict[str, object]:
        return build_product_shell_view(
            lang=lang,
            product_shell_store_path=app.state.product_shell_store_path,
        )

    @app.get("/v1/demo-ui/product-shell/history")
    def demo_ui_product_shell_history(
        decision: str | None = None,
        run_status: str | None = None,
        provider: str | None = None,
        lang: str | None = None,
    ) -> dict[str, object]:
        return build_product_shell_history(
            decision=decision,
            run_status=run_status,
            provider=provider,
            lang=lang,
            product_shell_store_path=app.state.product_shell_store_path,
        )

    @app.get("/v1/demo-ui/product-shell/approval-queue")
    def demo_ui_product_shell_approval_queue(lang: str | None = None) -> dict[str, object]:
        return build_product_shell_approval_queue(
            lang=lang,
            product_shell_store_path=app.state.product_shell_store_path,
        )

    @app.get("/v1/demo-ui/product-shell/audit-view")
    def demo_ui_product_shell_audit_view(
        decision: str | None = None,
        integrity_state: str | None = None,
        provider: str | None = None,
        lang: str | None = None,
    ) -> dict[str, object]:
        return build_product_shell_audit_view(
            decision=decision,
            integrity_state=integrity_state,
            provider=provider,
            lang=lang,
            product_shell_store_path=app.state.product_shell_store_path,
        )

    @app.get("/v1/demo-ui/provider-status")
    def demo_ui_provider_status(lang: str | None = None) -> dict[str, object]:
        return build_provider_status(lang=lang)

    @app.get("/v1/demo-ui/assistant-capabilities")
    def demo_ui_assistant_capabilities(lang: str | None = None) -> dict[str, object]:
        return app.state.safety_copilot.capabilities(lang=lang)

    @app.post("/v1/demo-ui/assistant-insight")
    def demo_ui_assistant_insight(payload: AssistantInsightRequest) -> dict[str, object]:
        return app.state.safety_copilot.explain_latest_result(
            payload.payload,
            lang=payload.lang,
            source=payload.source,
        )

    @app.post("/v1/guarded-execute", response_model=GuardedExecutionResponse)
    def guarded_execute(payload: GuardedExecutionRequest) -> dict[str, object]:
        request_dict = payload.model_dump()
        if payload.approval is not None:
            request_dict["approval"] = payload.approval.model_dump()
        return app.state.guarded_service.execute_guarded_request(request_dict)

    return app


app = create_app()
