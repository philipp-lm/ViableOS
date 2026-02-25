"""In-memory chat session management.

Sessions are ephemeral — lost on server restart. API keys are stored
only in memory, never persisted.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChatMessage:
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class ChatSession:
    id: str
    provider: str  # e.g. "anthropic", "openai", "google"
    model: str  # e.g. "claude-sonnet-4-6"
    api_key: str  # in-memory only, never persisted
    messages: list[ChatMessage] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    assessment_data: dict[str, Any] | None = None

    def to_litellm_messages(self) -> list[dict[str, str]]:
        """Convert session messages to LiteLLM format."""
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def add_message(self, role: str, content: str) -> ChatMessage:
        msg = ChatMessage(role=role, content=content)
        self.messages.append(msg)
        return msg

    def to_history(self) -> list[dict[str, Any]]:
        """Return serializable message history (no API keys)."""
        return [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp,
            }
            for m in self.messages
        ]


class SessionStore:
    """Thread-safe in-memory session store."""

    def __init__(self) -> None:
        self._sessions: dict[str, ChatSession] = {}

    def create(self, provider: str, model: str, api_key: str) -> ChatSession:
        session_id = str(uuid.uuid4())
        session = ChatSession(
            id=session_id,
            provider=provider,
            model=model,
            api_key=api_key,
        )
        self._sessions[session_id] = session
        return session

    def get(self, session_id: str) -> ChatSession | None:
        return self._sessions.get(session_id)

    def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def cleanup_old(self, max_age_hours: int = 24) -> int:
        """Remove sessions older than max_age_hours. Returns count removed."""
        cutoff = time.time() - (max_age_hours * 3600)
        old_ids = [sid for sid, s in self._sessions.items() if s.created_at < cutoff]
        for sid in old_ids:
            del self._sessions[sid]
        return len(old_ids)


# Global session store
store = SessionStore()
