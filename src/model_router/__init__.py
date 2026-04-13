"""Model router entrypoints for SafeCore."""

from src.model_router.profile_selector import ProfileSelector
from src.model_router.router import ModelRouter

__all__ = ["ModelRouter", "ProfileSelector"]
