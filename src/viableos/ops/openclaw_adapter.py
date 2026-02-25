"""OpenClaw Gateway runtime adapter.

Connects to a running OpenClaw instance via its REST API.
"""

from __future__ import annotations

from typing import Any

import httpx

from viableos.ops.adapter import RuntimeAdapter


class OpenClawAdapter(RuntimeAdapter):
    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None
        self._base_url = ""

    async def connect(self, url: str, api_key: str) -> bool:
        self._base_url = url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10.0,
        )
        try:
            resp = await self._client.get("/health")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def get_agents(self) -> list[dict[str, Any]]:
        if not self._client:
            return []
        try:
            resp = await self._client.get("/api/agents")
            if resp.status_code == 200:
                agents = resp.json()
                return [
                    {
                        "id": a.get("id", ""),
                        "name": a.get("name", a.get("id", "")),
                        "role": a.get("workspace", "").split("/")[-1] if a.get("workspace") else "",
                        "status": _map_openclaw_status(a.get("status", "")),
                        "lastSeen": a.get("last_active", ""),
                        "currentTask": a.get("current_task", ""),
                    }
                    for a in agents
                ]
        except httpx.HTTPError:
            pass
        return []

    async def get_activity(self) -> list[dict[str, Any]]:
        if not self._client:
            return []
        try:
            resp = await self._client.get("/api/activity", params={"limit": 50})
            if resp.status_code == 200:
                return resp.json()
        except httpx.HTTPError:
            pass
        return []

    async def get_signals(self) -> list[dict[str, Any]]:
        if not self._client:
            return []
        try:
            resp = await self._client.get("/api/signals")
            if resp.status_code == 200:
                return resp.json()
        except httpx.HTTPError:
            pass
        return []

    async def get_work_packages(self) -> list[dict[str, Any]]:
        if not self._client:
            return []
        try:
            resp = await self._client.get("/api/work-packages")
            if resp.status_code == 200:
                return resp.json()
        except httpx.HTTPError:
            pass
        return []

    async def get_decisions(self) -> list[dict[str, Any]]:
        if not self._client:
            return []
        try:
            resp = await self._client.get("/api/decisions", params={"status": "pending"})
            if resp.status_code == 200:
                return resp.json()
        except httpx.HTTPError:
            pass
        return []

    async def resolve_decision(self, decision_id: str, action: str) -> dict[str, Any]:
        if not self._client:
            return {"error": "Not connected"}
        try:
            resp = await self._client.post(
                f"/api/decisions/{decision_id}/resolve",
                json={"action": action},
            )
            if resp.status_code == 200:
                return resp.json()
            return {"error": f"HTTP {resp.status_code}"}
        except httpx.HTTPError as e:
            return {"error": str(e)}


def _map_openclaw_status(status: str) -> str:
    mapping = {
        "active": "online",
        "running": "working",
        "error": "error",
        "idle": "online",
        "stopped": "offline",
    }
    return mapping.get(status.lower(), "offline")
