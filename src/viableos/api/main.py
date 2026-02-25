"""FastAPI application for ViableOS."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from viableos.api.routes import router
from viableos.api.chat_routes import chat_router
from viableos.api.ops_routes import ops_router

app = FastAPI(
    title="ViableOS API",
    version="0.3.0",
    description="REST API for the ViableOS multi-agent design tool",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(chat_router)
app.include_router(ops_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "version": "0.3.0"}
