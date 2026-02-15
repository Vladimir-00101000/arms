"""Эндпоинты для управления API ключами интеграции"""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException

from src.authorization import UserDependency
from src.database.db_helper import SessionDep
from src.integration.api_key_dao import IntegrationApiKeyDAO
from src.integration.api_key_models import IntegrationApiKey
from src.integration.api_key_schemas import (
    ApiKeyCreate,
    ApiKeyResponse,
    ApiKeyCreatedResponse,
    ApiKeyList
)

api_key_router = APIRouter(
    prefix='/api/integration-keys',
    tags=['Управление API ключами интеграции']
)


@api_key_router.post(
    "/",
    response_model=ApiKeyCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать API ключ для внешней системы"
)
async def create_api_key(
        session: SessionDep,
        data: ApiKeyCreate,
        current_user=Depends(UserDependency())
):
    """
    Создание нового API ключа для интеграции.

    ⚠️ ВАЖНО: Ключ показывается ТОЛЬКО ОДИН РАЗ при создании!
    Сохраните его и передайте администратору внешней системы.
    """
    # Генерируем ключ
    raw_key = IntegrationApiKey.generate_key()
    key_hash = IntegrationApiKey.hash_key(raw_key)
    key_prefix = IntegrationApiKey.get_prefix(raw_key)

    # Сохраняем в БД (только хэш!)
    api_key = await IntegrationApiKeyDAO.create(
        session,
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=data.name,
        description=data.description,
        expires_at=data.expires_at,
        created_by_user_id=current_user.id
    )

    return ApiKeyCreatedResponse(
        id=api_key.id,
        key=raw_key,  # Показываем только здесь!
        key_prefix=key_prefix,
        name=api_key.name,
        description=api_key.description,
        expires_at=api_key.expires_at,
        created_at=api_key.created_at
    )


@api_key_router.get(
    "/",
    response_model=ApiKeyList,
    summary="Список всех API ключей"
)
async def list_api_keys(
        session: SessionDep,
        _=Depends(UserDependency())
):
    """Получение списка всех API ключей (без самих ключей)"""
    keys = await IntegrationApiKeyDAO.get_by(session)

    return ApiKeyList(
        items=[ApiKeyResponse.model_validate(k) for k in keys],
        total=len(keys)
    )


@api_key_router.get(
    "/{key_id}",
    response_model=ApiKeyResponse,
    summary="Информация о ключе"
)
async def get_api_key(
        session: SessionDep,
        key_id: UUID,
        _=Depends(UserDependency())
):
    """Получение информации о ключе (без самого ключа)"""
    try:
        key = await IntegrationApiKeyDAO.get(session, key_id)
        return ApiKeyResponse.model_validate(key)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API ключ не найден"
        )


@api_key_router.post(
    "/{key_id}/deactivate",
    response_model=ApiKeyResponse,
    summary="Деактивировать ключ"
)
async def deactivate_api_key(
        session: SessionDep,
        key_id: UUID,
        _=Depends(UserDependency())
):
    """Деактивация API ключа (отзыв доступа)"""
    try:
        key = await IntegrationApiKeyDAO.update(
            session,
            key_id,
            is_active=False
        )
        return ApiKeyResponse.model_validate(key)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API ключ не найден"
        )


@api_key_router.post(
    "/{key_id}/activate",
    response_model=ApiKeyResponse,
    summary="Активировать ключ"
)
async def activate_api_key(
        session: SessionDep,
        key_id: UUID,
        _=Depends(UserDependency())
):
    """Повторная активация API ключа"""
    try:
        key = await IntegrationApiKeyDAO.update(
            session,
            key_id,
            is_active=True
        )
        return ApiKeyResponse.model_validate(key)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API ключ не найден"
        )


@api_key_router.delete(
    "/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить ключ"
)
async def delete_api_key(
        session: SessionDep,
        key_id: UUID,
        _=Depends(UserDependency())
):
    """Полное удаление API ключа"""
    try:
        await IntegrationApiKeyDAO.delete(session, key_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API ключ не найден"
        )
