"""LangGraph Platform runtime adapter.

Connects to a running LangGraph Platform instance via its REST API
(assistants, threads, runs).
"""

from __future__ import annotations

from typing import Any

import httpx

from viableos.ops.adapter import RuntimeAdapter


class LangGraphAdapter(RuntimeAdapter):
    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None
        self._base_url = ""

    async def connect(self, url: str, api_key: str) -> bool:
        self._base_url = url.rstrip("/")
        headers: dict[str, str] = {}
        if api_key:
            headers["x-api-key"] = api_key
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=headers,
            timeout=10.0,
        )
        try:
            resp = await self._client.get("/ok")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def get_agents(self) -> list[dict[str, Any]]:
        if not self._client:
            return []
        try:
            resp = await self._client.post("/assistants/search", json={"limit": 100})
            if resp.status_code == 200:
                assistants = resp.json()
                agents = []
                for a in assistants:
                    agents.append({
                        "id": a.get("assistant_id", ""),
                        "name": a.get("name", a.get("assistant_id", "")),
                        "role": a.get("metadata", {}).get("role", ""),
                        "status": "online",
                        "lastSeen": a.get("updated_at", ""),
                    })
                return agents
        except httpx.HTTPError:
            pass
        return []

    async def get_activity(self) -> list[dict[str, Any]]:
        if not self._client:
            return []
        try:
            resp = await self._client.post("/threads/search", json={"limit": 20})
            if resp.status_code == 200:
                threads = resp.json()
                activity = []
                for t in threads:
                    thread_id = t.get("thread_id", "")
                    runs_resp = await self._client.get(f"/threads/{thread_id}/runs", params={"limit": 5})
                    if runs_resp.status_code == 200:
                        for run in runs_resp.json():
                            activity.append({
                                "id": run.get("run_id", ""),
                                "timestamp": run.get("created_at", ""),
                                "agent": run.get("assistant_id", ""),
                                "type": run.get("status", ""),
                                "summary": f"Run {run.get('status', '')} on thread {thread_id[:8]}...",
                            })
                return activity[:50]
        except httpx.HTTPError:
            pass
        return []

    async def get_signals(self) -> list[dict[str, Any]]:
        # LangGraph doesn't have a native signals API;
        # signals would come from agent state or interrupts
        return []

    async def get_work_packages(self) -> list[dict[str, Any]]:
        if not self._client:
            return []
        try:
            resp = await self._client.post("/threads/search", json={"limit": 50})
            if resp.status_code == 200:
                threads = resp.json()
                packages = []
                for t in threads:
                    status_map = {
                        "idle": "queued",
                        "busy": "active",
                        "interrupted": "active",
                        "error": "active",
                    }
                    packages.append({
                        "id": t.get("thread_id", ""),
                        "title": t.get("metadata", {}).get("title", f"Thread {t.get('thread_id', '')[:8]}..."),
                        "assignee": t.get("metadata", {}).get("assignee", ""),
                        "status": status_map.get(t.get("status", ""), "queued"),
                        "created": t.get("created_at", ""),
                    })
                return packages
        except httpx.HTTPError:
            pass
        return []

    async def get_decisions(self) -> list[dict[str, Any]]:
        # Decisions map to LangGraph interrupts
        if not self._client:
            return []
        try:
            resp = await self._client.post(
                "/threads/search",
                json={"status": "interrupted", "limit": 20},
            )
            if resp.status_code == 200:
                threads = resp.json()
                decisions = []
                for t in threads:
                    decisions.append({
                        "id": t.get("thread_id", ""),
                        "title": t.get("metadata", {}).get("decision_title", "Pending decision"),
                        "description": t.get("metadata", {}).get("decision_desc", ""),
                        "requestedBy": t.get("metadata", {}).get("agent", ""),
                        "timestamp": t.get("updated_at", ""),
                        "status": "pending",
                    })
                return decisions
        except httpx.HTTPError:
            pass
        return []

    async def resolve_decision(self, decision_id: str, action: str) -> dict[str, Any]:
        if not self._client:
            return {"error": "Not connected"}
        try:
            # Resume the interrupted thread
            resp = await self._client.post(
                f"/threads/{decision_id}/runs",
                json={
                    "input": {"human_decision": action},
                    "metadata": {"resolved_by": "human", "action": action},
                },
            )
            if resp.status_code in (200, 201):
                return resp.json()
            return {"error": f"HTTP {resp.status_code}"}
        except httpx.HTTPError as e:
            return {"error": str(e)}
