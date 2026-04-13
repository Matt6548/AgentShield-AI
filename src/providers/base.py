"""Safe provider gateway abstractions for backend integrations."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urljoin, urlparse


LOCAL_HOSTS = {"127.0.0.1", "localhost"}


@dataclass(frozen=True)
class ProviderCapability:
    """Describe one backend capability exposed by a provider adapter."""

    name: str
    detail: str


@dataclass(frozen=True)
class ProviderHealth:
    """Minimal provider health metadata without network calls."""

    status: str
    ok: bool
    summary: str


@dataclass(frozen=True)
class ProviderSnapshot:
    """Safe public metadata for UI or docs-facing provider visibility."""

    id: str
    name: str
    adapter_kind: str
    configured: bool
    enabled: bool
    env_source: str
    base_url_env: str
    local_demo_mode: bool
    base_url_status: str
    base_url_label: str
    masked_key_status: bool
    capability_names: list[str]
    capability_details: list[dict[str, str]]
    health: dict[str, Any]
    gateway_support: str
    auth_mode: str
    supports_base_url: bool
    supports_token: bool

    def as_public_dict(self) -> dict[str, Any]:
        """Return a JSON-safe public view."""
        return asdict(self)


class ProviderAdapter(ABC):
    """Backend provider adapter base class with safe env-based status helpers."""

    provider_id = "provider"
    display_name = "Provider"
    adapter_kind = "provider"
    api_key_env: str | None = None
    base_url_env: str | None = None
    default_base_url: str | None = None
    auth_mode = "none"
    shell_enabled = False
    token_optional = False
    gateway_support = "baseline"

    def __init__(self) -> None:
        self._api_key = self._read_env(self.api_key_env)
        self._configured_base_url = self._read_env(self.base_url_env)

    def capabilities(self) -> tuple[ProviderCapability, ...]:
        """Return safe capability metadata."""
        return ()

    def health(self) -> ProviderHealth:
        """Return non-network health metadata."""
        if self.is_configured():
            return ProviderHealth(
                status="READY",
                ok=True,
                summary="Backend configuration is present for this adapter.",
            )
        return ProviderHealth(
            status="NOT_CONFIGURED",
            ok=False,
            summary="Backend configuration is not present for this adapter yet.",
        )

    def is_configured(self) -> bool:
        """Return whether the backend has enough config for this adapter."""
        if self.local_demo_mode:
            return True

        has_base_url = bool(self._effective_base_url())
        has_key = bool(self._api_key)
        requires_key = bool(self.api_key_env) and not self.token_optional

        if self.supports_base_url and not has_base_url:
            return False
        if requires_key and not has_key:
            return False
        if self.api_key_env and not self.token_optional:
            return has_key
        if self.api_key_env and self.token_optional:
            return has_base_url
        return has_base_url or self.local_demo_mode

    @property
    def local_demo_mode(self) -> bool:
        """Return whether the adapter is the built-in local/demo path."""
        return False

    @property
    def supports_base_url(self) -> bool:
        """Return whether the adapter supports base URL override."""
        return self.base_url_env is not None or self.default_base_url is not None

    @property
    def supports_token(self) -> bool:
        """Return whether the adapter can use token-based auth."""
        return self.api_key_env is not None

    def safe_snapshot(self) -> ProviderSnapshot:
        """Return safe public metadata for this adapter."""
        capabilities = list(self.capabilities())
        health = self.health()
        base_url_status, base_url_label, local_demo_mode = self._describe_base_url()
        return ProviderSnapshot(
            id=self.provider_id,
            name=self.display_name,
            adapter_kind=self.adapter_kind,
            configured=self.is_configured(),
            enabled=bool(self.shell_enabled),
            env_source=self.api_key_env or "NO_KEY_REQUIRED",
            base_url_env=self.base_url_env or "NOT_APPLICABLE",
            local_demo_mode=local_demo_mode,
            base_url_status=base_url_status,
            base_url_label=base_url_label,
            masked_key_status=bool(self._api_key),
            capability_names=[item.name for item in capabilities],
            capability_details=[asdict(item) for item in capabilities],
            health=asdict(health),
            gateway_support=self.gateway_support,
            auth_mode=self.auth_mode,
            supports_base_url=self.supports_base_url,
            supports_token=self.supports_token,
        )

    @abstractmethod
    def build_request_spec(
        self,
        *,
        path: str,
        body: dict[str, Any] | None = None,
        method: str = "POST",
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Build one backend-only request specification for future integrations."""

    def _build_headers(self, extra_headers: dict[str, str] | None = None) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def _effective_base_url(self) -> str | None:
        return self._configured_base_url or self.default_base_url

    def _join_url(self, path: str) -> str:
        base_url = self._effective_base_url()
        if not base_url:
            raise ValueError(f"{self.provider_id} is not configured with a base URL.")
        normalized_base = base_url.rstrip("/") + "/"
        return urljoin(normalized_base, path.lstrip("/"))

    def _read_env(self, name: str | None) -> str | None:
        if not name:
            return None
        value = os.getenv(name)
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    def _describe_base_url(self) -> tuple[str, str, bool]:
        if self.local_demo_mode:
            return ("LOCAL_DEMO", "Built in", True)

        raw_url = self._configured_base_url
        if raw_url:
            parsed = urlparse(raw_url)
            host = (parsed.hostname or "").strip().lower()
            if host in LOCAL_HOSTS:
                return ("LOCAL_OVERRIDE", raw_url, True)
            return ("CUSTOM_OVERRIDE", "Custom base URL configured", False)

        if self.default_base_url:
            return ("DEFAULT", "Default API URL", False)
        return ("NOT_CONFIGURED", "Not configured", False)


class LocalDemoProviderAdapter(ProviderAdapter):
    """Built-in local/demo provider card used by the product shell."""

    provider_id = "local_demo"
    display_name = "Local / demo mode"
    adapter_kind = "local_demo"
    auth_mode = "none"
    shell_enabled = True
    gateway_support = "built_in"

    @property
    def local_demo_mode(self) -> bool:
        return True

    def capabilities(self) -> tuple[ProviderCapability, ...]:
        return (
            ProviderCapability(
                name="local_product_shell",
                detail="Built-in provider mode for the current product shell and demo flows.",
            ),
            ProviderCapability(
                name="no_secret_required",
                detail="Does not require provider keys or remote provider configuration.",
            ),
        )

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            status="READY",
            ok=True,
            summary="Built in and enabled for current local demo and product shell flows.",
        )

    def build_request_spec(
        self,
        *,
        path: str,
        body: dict[str, Any] | None = None,
        method: str = "POST",
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "adapter_kind": self.adapter_kind,
            "method": method.upper(),
            "path": path,
            "headers": self._build_headers(extra_headers),
            "json": body or {},
            "local_demo_mode": True,
        }
