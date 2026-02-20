"""Pydantic response models for the ViableOS API."""

from __future__ import annotations

from pydantic import BaseModel


class TemplateItem(BaseModel):
    key: str
    name: str
    tagline: str
    description: str
    units: int


class ModelInfo(BaseModel):
    id: str
    provider: str
    tier: str
    note: str
    agent_reliability: str
    warning: str | None = None


class BudgetAllocationResponse(BaseModel):
    system: str
    friendly_name: str
    monthly_usd: float
    model: str
    percentage: float


class BudgetPlanResponse(BaseModel):
    total_monthly_usd: float
    strategy: str
    allocations: list[BudgetAllocationResponse]
    model_routing: dict[str, str]


class CheckResultResponse(BaseModel):
    system: str
    name: str
    present: bool
    details: str
    suggestions: list[str] = []


class WarningResponse(BaseModel):
    category: str
    severity: str
    message: str
    suggestion: str = ""


class ViabilityReportResponse(BaseModel):
    score: int
    total: int
    checks: list[CheckResultResponse]
    warnings: list[WarningResponse]


class CoordinationRule(BaseModel):
    trigger: str
    action: str
    scope: str = ""


class PresetsResponse(BaseModel):
    values: list[str]
    autonomy_levels: dict[str, str]
    tool_categories: dict[str, list[str]]
    approval_presets: list[str]
    review_presets: list[str]
    emergency_presets: list[str]
    notification_channels: list[str]
    never_do_presets: list[str]
    persistence_strategies: dict[str, str]
    model_tiers: dict[str, str]
    agent_reliability_labels: dict[str, str]
    strategy_presets: list[str]
