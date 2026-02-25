"""Operations Room API routes — proxy to running agent deployments."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from viableos.ops.adapter import RuntimeAdapter
from viableos.ops.openclaw_adapter import OpenClawAdapter
from viableos.ops.langgraph_adapter import LangGraphAdapter

ops_router = APIRouter(prefix="/api/ops")

# In-memory adapter instance (one connection at a time)
_adapter: RuntimeAdapter | None = None


class ConnectRequest(BaseModel):
    runtime: str  # "openclaw" | "langgraph"
    url: str
    api_key: str


class ConnectResponse(BaseModel):
    connected: bool
    error: str | None = None


class ResolveRequest(BaseModel):
    action: str  # "approve" | "reject"


@ops_router.post("/connect", response_model=ConnectResponse)
async def ops_connect(req: ConnectRequest) -> ConnectResponse:
    """Connect to a running runtime deployment."""
    global _adapter

    if req.runtime == "openclaw":
        adapter = OpenClawAdapter()
    elif req.runtime == "langgraph":
        adapter = LangGraphAdapter()
    else:
        raise HTTPException(status_code=400, detail=f"Unknown runtime: {req.runtime}")

    success = await adapter.connect(req.url, req.api_key)
    if success:
        _adapter = adapter
        return ConnectResponse(connected=True)
    else:
        return ConnectResponse(connected=False, error="Failed to connect. Check URL and API key.")


@ops_router.post("/disconnect")
async def ops_disconnect() -> dict[str, bool]:
    """Disconnect from the current runtime."""
    global _adapter
    _adapter = None
    return {"disconnected": True}


def _require_adapter() -> RuntimeAdapter:
    if _adapter is None:
        raise HTTPException(status_code=400, detail="Not connected to any runtime")
    return _adapter


@ops_router.get("/agents")
async def ops_agents() -> list[dict[str, Any]]:
    return await _require_adapter().get_agents()


@ops_router.get("/activity")
async def ops_activity() -> list[dict[str, Any]]:
    return await _require_adapter().get_activity()


@ops_router.get("/signals")
async def ops_signals() -> list[dict[str, Any]]:
    return await _require_adapter().get_signals()


@ops_router.get("/workpackages")
async def ops_work_packages() -> list[dict[str, Any]]:
    return await _require_adapter().get_work_packages()


@ops_router.get("/decisions")
async def ops_decisions() -> list[dict[str, Any]]:
    return await _require_adapter().get_decisions()


@ops_router.post("/decisions/{decision_id}/resolve")
async def ops_resolve_decision(decision_id: str, req: ResolveRequest) -> dict[str, Any]:
    return await _require_adapter().resolve_decision(decision_id, req.action)
