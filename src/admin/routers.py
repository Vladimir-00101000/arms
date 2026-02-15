from fastapi import APIRouter, Depends, Query, HTTPException, status, Path
from typing import List, Optional
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import NoResultFound
from uuid import UUID

import math

from src.database.db_helper import SessionDep
from src.user.models import User
from src.user.dao import UserDAO
from src.admin.schemas import (
    User as UserSchema,
    Pagination,
    UserListResponse,
    UserDetailResponce,
    UserProjectRole,
    UserChangeStatResponse,
    UserChangeRoleResponse)

from src.authorization import AdminDependency


admin_router = APIRouter(prefix='/api/admin', tags=['Admin'])

@admin_router.get(
    "/users",
    response_model=UserListResponse,
    summary="Получить список всех пользователей",
    description="""
    Получение списка всех пользователей системы.
    
    **Требует аутентификации:** Да
    **Права доступа:** Только администраторы
    **Возвращает:** Пагинированный список пользователей
    """
)
async def get_all_users(
    session: SessionDep,
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
    status: Optional[str] = Query(None, description="Фильтр по статусу", regex="^(active|inactive)$"),
    is_admin: Optional[bool] = Query(None, description="Фильтр по администраторам"),
    _=Depends(AdminDependency())
):
    """
    GET /api/admin/users
    
    Получение списка всех пользователей.
    Доступно только для администраторов.
    """
    try:
        base_query = (
            select(User)
            .order_by(User.id.desc())
            .limit(limit)
            .offset((page - 1) * limit)
        )

        if status is not None:
            base_query = base_query.where(User.status == status.upper())

        # if is_admin is not None:
        #     base_query = base_query.where(User.status == new_status.upper())

        users = await UserDAO.get_by(session, base_query)

        count_query = select(func.count(User.id))
        if status is not None:
            count_query = count_query.where(User.status == status.upper())
                
        total_result = await session.execute(count_query)
        total = total_result.scalar_one()

        pages = math.ceil(total / limit) if total > 0 else 1

        users = [
            UserSchema(
                id=user.id, 
                login=user.login,
                surname=user.surname,
                name=user.name,
                email=user.email,
                status=user.status.lower(),
                is_admin=user.is_admin,
                created_at=user.created_at,
                updated_at=user.updated_at)
            for user in users]

        pagination = Pagination(
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )

        return UserListResponse(
            data=users,
            pagination=pagination
        )
    
    except HTTPException:
        raise

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Внутренняя ошибка сервера",
                "detail": f"Не удалось получить список пользователей: {str(e)}"
            }
        )

@admin_router.get(
    "/users/{user_id}",
    response_model=UserDetailResponce,
    summary="Получить детальную информацию о пользователе",
    description="""
    Получение детальной информации о конкретном пользователе.
    
    **Требует аутентификации:** Да
    **Права доступа:** Только администраторы
    **Возвращает:** Полную информацию о пользователе и его проектах
    """
)
async def get_user_by_id(
    session: SessionDep,
    user_id: UUID = Path(description="ID пользователя"),
    _=Depends(AdminDependency())
):
    """
    GET /api/admin/users/{user_id}
    
    Получение детальной информации о пользователе.
    Доступно только для администраторов.
    """
    try:
        
        user = await UserDAO.get(session, user_id)

        return UserDetailResponce(
            id=user.id, 
            login=user.login,
            surname=user.surname,
            name=user.name,
            email=user.email,
            status=user.status.lower(),
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at,
            project_roles=[
                UserProjectRole(
                    project_id=user_project_role.project_id,
                    project_name=user_project_role.project.name,
                    role_id=user_project_role.role_id,
                    role_name=user_project_role.role.name
                )
                for user_project_role in user.project_roles])
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Пользователь не найден",
                "detail": "Пользователь не найден"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Внутренняя ошибка сервера",
                "detail": f"Не удалось получить информацию о пользователе: {str(e)}"
            }
        )

@admin_router.post(
    "/users/{user_id}/changestat",
    response_model=UserChangeStatResponse,
    summary="Изменить статус пользователя",
    description="""
    Изменение статуса пользователя (активация, деактивация).
    
    **Требует аутентификации:** Да
    **Права доступа:** Только администраторы
    **Доступные статусы:** ACTIVE, INACTIVE (зависит от вашей модели)
    """
)
async def change_user_status(
    session: SessionDep,
    user_id: UUID = Path(description="ID пользователя"),
    new_status: str = Query(None, description="Новый статус", regex="^(active|inactive)$"),
    _=Depends(AdminDependency())
):
    """
    POST /api/admin/users/{user_id}/changestat
    
    Изменение статуса пользователя.
    Доступно только для администраторов.
    """
    try:
    
        user = await UserDAO.get(session, user_id)

        if new_status.upper() == user.status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Некорректный статус",
                    "detail": f"Статус должен отличаться от текущего"
                }
            )

        _ = await UserDAO.update(session, user.id, status=new_status.upper())

        return UserChangeStatResponse(
            status=new_status.lower()
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Пользователь не найден",
                "detail": "Пользователь не найден"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Внутренняя ошибка сервера",
                "detail": f"Не удалось изменить статус пользователя: {str(e)}"
            }
        )


@admin_router.post(
    "/users/{user_id}/changerole",
    response_model=UserChangeRoleResponse,
    summary="Изменить роль пользователя",
    description="""
    Изменение роли пользователя (админ, не админ).
    
    **Требует аутентификации:** Да
    **Права доступа:** Только администраторы
    **Доступные статусы:** ACTIVE, INACTIVE (зависит от вашей модели)
    """
)
async def change_user_role(
    session: SessionDep,
    user_id: UUID = Path(description="ID пользователя"),
    is_admin: bool = Query(None, description="Администратор"),
    _=Depends(AdminDependency())
):
    """
    POST /api/admin/users/{user_id}/changerole
    
    Изменение статуса пользователя.
    Доступно только для администраторов.
    """
    try:
    
        user = await UserDAO.get(session, user_id)

        if is_admin == user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Некорректная роль",
                    "detail": f"Роль должна отличаться"
                }
            )

        _ = await UserDAO.update(session, user.id, is_admin=is_admin)

        return UserChangeRoleResponse(
            is_admin=is_admin
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Пользователь не найден",
                "detail": "Пользователь не найден"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Внутренняя ошибка сервера",
                "detail": f"Не удалось изменить статус пользователя: {str(e)}"
            }
        )
