"""Abstract base class for runtime adapters.

Each adapter connects to a specific runtime (OpenClaw, LangGraph)
and provides a unified interface for the Operations Room.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class RuntimeAdapter(ABC):
    """Abstract interface for connecting to a running agent deployment."""

    @abstractmethod
    async def connect(self, url: str, api_key: str) -> bool:
        """Test connectivity. Returns True if successful."""
        ...

    @abstractmethod
    async def get_agents(self) -> list[dict[str, Any]]:
        """Get list of agents with status."""
        ...

    @abstractmethod
    async def get_activity(self) -> list[dict[str, Any]]:
        """Get recent activity feed."""
        ...

    @abstractmethod
    async def get_signals(self) -> list[dict[str, Any]]:
        """Get pending signals/alerts."""
        ...

    @abstractmethod
    async def get_work_packages(self) -> list[dict[str, Any]]:
        """Get work packages (queued, active, done)."""
        ...

    @abstractmethod
    async def get_decisions(self) -> list[dict[str, Any]]:
        """Get pending human decisions."""
        ...

    @abstractmethod
    async def resolve_decision(self, decision_id: str, action: str) -> dict[str, Any]:
        """Approve or reject a pending decision."""
        ...
