"""Chat API routes — SSE streaming for the VSM Expert Chat."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from viableos.chat.engine import (
    finalize_assessment,
    get_history,
    send_message,
    start_session,
)

chat_router = APIRouter(prefix="/api/chat")


class StartRequest(BaseModel):
    provider: str
    model: str
    api_key: str


class StartResponse(BaseModel):
    session_id: str


class MessageRequest(BaseModel):
    session_id: str
    message: str


@chat_router.post("/start", response_model=StartResponse)
async def chat_start(req: StartRequest) -> StartResponse:
    """Start a new chat session. Returns session ID."""
    session = start_session(
        provider=req.provider,
        model=req.model,
        api_key=req.api_key,
    )
    return StartResponse(session_id=session.id)


@chat_router.post("/message")
async def chat_message(req: MessageRequest) -> StreamingResponse:
    """Send a message and receive SSE-streamed response."""

    async def event_stream():
        async for chunk in send_message(req.session_id, req.message):
            # SSE format: data: <chunk>\n\n
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


class FinalizeResponse(BaseModel):
    assessment: dict[str, Any] | None
    success: bool


@chat_router.post("/finalize", response_model=FinalizeResponse)
async def chat_finalize(req: dict[str, str]) -> FinalizeResponse:
    """Extract assessment data from the conversation."""
    session_id = req.get("session_id", "")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")

    data = finalize_assessment(session_id)
    return FinalizeResponse(assessment=data, success=data is not None)


@chat_router.get("/history/{session_id}")
async def chat_history(session_id: str) -> list[dict[str, Any]]:
    """Get message history for a session."""
    history = get_history(session_id)
    if history is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return history
