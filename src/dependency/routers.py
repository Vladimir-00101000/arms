from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException, Query

from src.authorization import UserDependency
from src.database.db_helper import SessionDep
from src.dependency.dao import RequirementDependenceDAO, \
    ReqDependenceHistoryDAO
from src.dependency.schemas import (
    DependencyCreate, Dependency, DependencyList, DependencyDirection
)
from src.requirement.dao import RequirementDAO

dependency_router = APIRouter(tags=['Зависимости'])


@dependency_router.get(
    "/api/requirements/{requirement_id}/dependencies",
    response_model=DependencyList,
    status_code=status.HTTP_200_OK,
    summary="Получить зависимости требования",
    description="Получение всех зависимостей требования"
)
async def get_dependencies(
        session: SessionDep,
        requirement_id: UUID,
        direction: DependencyDirection = Query(
            DependencyDirection.BOTH,
            description="Направление зависимостей"
        ),
        _=Depends(UserDependency())
):
    try:
        await RequirementDAO.get(session, requirement_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Требование не найдено"
        )

    incoming = []
    outgoing = []

    if direction in (DependencyDirection.INCOMING, DependencyDirection.BOTH):
        incoming = await RequirementDependenceDAO.get_by(
            session,
            target_requirement_id=requirement_id
        )

    if direction in (DependencyDirection.OUTGOING, DependencyDirection.BOTH):
        outgoing = await RequirementDependenceDAO.get_by(
            session,
            source_requirement_id=requirement_id
        )

    return DependencyList(incoming=incoming, outgoing=outgoing)


@dependency_router.post(
    "/api/requirements/{requirement_id}/dependencies",
    response_model=Dependency,
    status_code=status.HTTP_201_CREATED,
    summary="Создать зависимость",
    description="Создание новой зависимости между требованиями"
)
async def create_dependency(
        session: SessionDep,
        requirement_id: UUID,
        dependency_data: DependencyCreate,
        current_user=Depends(UserDependency())
):
    # Проверяем существование исходного требования
    try:
        source_req = await RequirementDAO.get(session, requirement_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Исходное требование не найдено"
        )

    # Проверяем существование целевого требования
    try:
        target_req = await RequirementDAO.get(
            session,
            dependency_data.target_requirement_id
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Целевое требование не найдено"
        )

    # Нельзя создать зависимость на само себя
    if requirement_id == dependency_data.target_requirement_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя создать зависимость требования на само себя"
        )

    # Проверяем дубликаты
    existing = await RequirementDependenceDAO.get_by(
        session,
        source_requirement_id=requirement_id,
        target_requirement_id=dependency_data.target_requirement_id,
        type=dependency_data.type
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такая зависимость уже существует"
        )

    # Создаём зависимость с группами требований
    dependency = await RequirementDependenceDAO.create(
        session,
        source_requirement_id=requirement_id,
        source_requirement_group_id=getattr(
            source_req, 'requirement_group_id', None
        ),
        target_requirement_group_id=getattr(
            target_req, 'requirement_group_id', None
        ),
        **dependency_data.model_dump()
    )

    # Сохраняем в историю
    await ReqDependenceHistoryDAO.create(
        session,
        prev_req_dependence_id=dependency.id,
        created_by_user_id=current_user.id
    )

    return dependency


@dependency_router.delete(
    "/api/dependencies/{dependency_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить зависимость",
    description="Удаление зависимости между требованиями"
)
async def delete_dependency(
        session: SessionDep,
        dependency_id: UUID,
        current_user=Depends(UserDependency())
):
    try:
        await RequirementDependenceDAO.get(session, dependency_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Зависимость не найдена"
        )

    # Сохраняем в историю перед удалением (для аудита)
    await ReqDependenceHistoryDAO.create(
        session,
        prev_req_dependence_id=dependency_id,
        created_by_user_id=current_user.id
    )

    await RequirementDependenceDAO.delete(session, dependency_id)
    return None
