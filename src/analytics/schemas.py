from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ================ Request Schemas ================
class TestCoverageCreate(BaseModel):
    """Добавить покрытие требования тест-кейсом"""
    requirement_id: UUID = Field(..., description="ID требования")
    test_case_version_id: str = Field(..., max_length=255, description="ID версии тест-кейса")


class TestCoverageUpdate(BaseModel):
    """Обновление покрытия тестами"""
    test_case_version_id: str = Field(..., description="ID версии тест-кейса")
    test_case_status: Optional[str] = Field(None, description="Статус тест-кейса")


# ================ Response Schemas ================
class TestCoverageResponse(BaseModel):
    """Покрытие тестами"""
    id: UUID
    requirement_id: UUID
    test_case_version_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class TestCoverage(BaseModel):
    """Покрытие требования тестами"""
    requirement_id: UUID
    test_cases: list[str] = Field(default_factory=list, description="Список ID тест-кейсов")
    coverage_percentage: float = Field(default=0.0, description="Процент покрытия")


class RequirementTraceability(BaseModel):
    """Трассируемость требования"""
    requirement_id: UUID
    requirement_name: str
    requirement_type: str
    targets: list[UUID] = Field(default_factory=list, description="Исходящие связи")
    sources: list[UUID] = Field(default_factory=list, description="Входящие связи")


class TraceabilityIssue(BaseModel):
    """Проблема трассируемости"""
    requirement_id: UUID
    requirement_name: str
    requirement_type: str
    issue_description: str


class CoverageSummary(BaseModel):
    """Статистика покрытия по типу"""
    requirement_type: str
    uncovered_count: int
    total_count: int
    coverage_percentage: float


class DashboardStats(BaseModel):
    """Статистика дашборда"""
    total: int
    by_status: dict[str, int]
    by_type: dict[str, int]
    traceability_coverage: list[CoverageSummary]

