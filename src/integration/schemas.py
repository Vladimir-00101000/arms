"""Схемы для API интеграции с системами тестирования"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


# ================ Enums ================
class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DRAFT = "draft"


class RequirementStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class RequirementType(str, Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non-functional"
    BUSINESS = "business"


class TestCaseStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    NOT_EXECUTED = "not_executed"
    RETEST = "retest"
    IN_PROGRESS = "in_progress"


# ================ Error Schema ================
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ================ Project Schemas ================
class TestSystemProject(BaseModel):
    """Проект для синхронизации с системой тестирования"""
    id: UUID
    name: str = Field(..., description="Название проекта")
    code: Optional[str] = Field(None, description="Код проекта")
    description: Optional[str] = Field(None, description="Описание проекта")
    status: ProjectStatus = Field(..., description="Статус проекта")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")
    test_system_id: Optional[str] = Field(
        None,
        description="ID проекта в системе тестирования"
    )

    model_config = {"from_attributes": True}


class TestSystemProjectList(BaseModel):
    """Список проектов для синхронизации"""
    projects: list[TestSystemProject]
    sync_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Время синхронизации"
    )
    total_count: int = Field(..., description="Общее количество проектов")
    filtered_count: int = Field(..., description="Количество отфильтрованных")


# ================ Requirement Schemas for Integration ================
class IntegrationRequirement(BaseModel):
    """Требование для интеграции"""
    id: UUID = Field(..., description="ID требования в АСУТр")
    name: str = Field(..., description="Название требования")
    description: Optional[str] = Field(None, description="Описание")
    status: RequirementStatus = Field(..., description="Статус требования")
    priority: int = Field(1, ge=1, le=5, description="Приоритет (1-5)")
    type: RequirementType = Field(..., description="Тип требования")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")
    version: int = Field(1, description="Версия требования")
    has_test_coverage: bool = Field(False, description="Есть покрытие тестами")

    model_config = {"from_attributes": True}


class RequirementListPagination(BaseModel):
    """Пагинация для списка требований"""
    limit: int
    offset: int
    has_more: bool = False


class IntegrationRequirementList(BaseModel):
    """Список требований проекта для интеграции"""
    project_id: UUID = Field(..., description="ID проекта")
    project_name: str = Field(..., description="Название проекта")
    requirements: list[IntegrationRequirement]
    total_count: int = Field(..., description="Общее количество требований")
    filtered_count: int = Field(..., description="Отфильтрованных")
    sync_timestamp: datetime = Field(default_factory=datetime.utcnow)
    pagination: RequirementListPagination


# ================ Test Case Schemas ================
class TestCase(BaseModel):
    """Тест-кейс из системы тестирования"""
    requirement_id: UUID = Field(..., description="ID требования в АСУТр")
    test_case_id: str = Field(...,
                              description="ID тест-кейса в системе тестирования")
    test_case_name: Optional[str] = Field(None,
                                          description="Название тест-кейса")
    test_case_status: TestCaseStatus = Field(...,
                                             description="Статус тест-кейса")

    model_config = {"from_attributes": True}


class TestCaseList(BaseModel):
    """Список тест-кейсов проекта"""
    project_id: str = Field(..., description="ID проекта")
    project_name: Optional[str] = Field(None, description="Название проекта")
    test_cases: list[TestCase]
    total_count: int = Field(..., description="Общее количество тест-кейсов")


class TestCaseSyncRequest(BaseModel):
    """Запрос на синхронизацию тест-кейсов"""
    test_cases: list[TestCase]
