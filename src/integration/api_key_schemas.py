"""Схемы для управления API ключами"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    """Создание нового API ключа"""
    name: str = Field(..., max_length=255, description="Название системы")
    description: Optional[str] = Field(None, max_length=1000,
                                       description="Описание")
    expires_at: Optional[datetime] = Field(None, description="Срок действия")


class ApiKeyResponse(BaseModel):
    """Ответ с информацией о ключе (без самого ключа)"""
    id: UUID
    key_prefix: str = Field(..., description="Префикс ключа для идентификации")
    name: str
    description: Optional[str] = None
    is_active: bool
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: datetime
    created_by_user_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


class ApiKeyCreatedResponse(BaseModel):
    """Ответ при создании ключа (с самим ключом - показывается ОДИН раз)"""
    id: UUID
    key: str = Field(...,
                     description="API ключ - сохраните его, он показывается только один раз!")
    key_prefix: str
    name: str
    description: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApiKeyList(BaseModel):
    """Список API ключей"""
    items: list[ApiKeyResponse]
    total: int
