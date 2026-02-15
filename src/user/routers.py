from sqlalchemy import select

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from src.database.db_helper import SessionDep

from src.user.models import User
from src.user.dao import UserDAO, UserProjectRoleDAO
from src.user.dependencies import UserDependency
from src.user.schemas import (
    UserProfileResponse,
    UserProfilePatchResponse,
    UserProfilePatchRequest,
    UserProjectRole,
    UserProjectsResponse)

import logging

logger = logging.getLogger(__name__)

user_router = APIRouter(prefix='/api/users', tags=['Users'])

@user_router.get(
    "/me/profile",
    response_model=UserProfileResponse,
    summary="Получить информацию о пользователе (о себе)",
    description="""
    Получение профиля текущего аутентифицированного пользователя.
    
    **Требует аутентификации:** Да
    **Права доступа:** Любой аутентифицированный пользователь
    **Возвращает:** Личные данные пользователя (без проектов и ролей)
    """
)
async def get_user_profile(
    session: SessionDep,
    status_code=status.HTTP_200_OK,
    me_user=Depends(UserDependency())
):
    """
    GET /api/users/me/profile
    
    Получение профиля текущего пользователя.
    Только аутентифицированный пользователь может получить свой профиль.
    """

    try:

        response_data = UserProfileResponse(
            id=me_user.id,
            login=me_user.login,
            surname=me_user.surname,
            name=me_user.name,
            email=me_user.email,
            status=me_user.status.lower(),
            created_at=me_user.created_at,
            is_admin=me_user.is_admin
        )
        
        return response_data
        
    except HTTPException:
        raise
        
    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Внутренняя ошибка сервера",
                "detail": "Не удалось получить информацию о профиле"
            }
        )

@user_router.patch(
    "/me/profile",
    response_model=UserProfilePatchResponse,
    summary="Обновить свои данные (логин, имя, фамилию)",
    description="""
    Обновление личных данных пользователем.
    
    **Что можно обновить:**
    - login: Логин пользователя
    - name: Имя пользователя
    - surname: Фамилия пользователя
    
    **Ограничения:**
    - Логин должен быть уникальным в системе
    - Можно обновлять одно или несколько полей одновременно
    """
)
async def patch_user_profile(
    update_data: UserProfilePatchRequest,
    session: SessionDep,
    status_code=status.HTTP_200_OK,
    me_user=Depends(UserDependency())
):
    """
    PATCH /api/users/me/profile
    
    Обновление личных данных текущим пользователем.
    Только аутентифицированный пользователь может обновлять свои данные.
    """
    
    logger.info("hello")
    try:
        update_values = {}
        
        if update_data.login is not None:
            if not update_data.login == me_user.login:
                user_query = select(User).where(
                    User.login == update_data.login,
                    User.id != me_user.id 
                )
                user = await UserDAO.get_by(session, user_query)

                if user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": "Логин уже занят",
                            "detail": f"Логин '{update_data.login}' уже используется другим пользователем",
                            "field": "login"
                        }
                    )
                
                update_values["login"] = update_data.login
        
        if update_data.name is not None:
            if update_data.name != me_user.name:
                update_values["name"] = update_data.name
        
        if update_data.surname is not None:
            if update_data.surname != me_user.surname:
                update_values["surname"] = update_data.surname

        if not update_values:

            return UserProfilePatchResponse(
                id=me_user.id,
                login=me_user.login,
                name=me_user.name,
                surname=me_user.surname,
                email=me_user.email,
                status=me_user.status.lower,
                is_admin=me_user.is_admin,
                created_at=me_user.created_at,
                message="Данные не были изменены"
            )

        user = await UserDAO.update(
            session,
            me_user.id,
            **update_values
        )
        
        response_data = UserProfilePatchResponse(
            id=user.id,
            login=user.login,
            name=user.name,
            surname=user.surname,
            email=user.email,
            status=user.status.lower(),
            is_admin=user.is_admin,
            created_at=me_user.created_at,
            message=f"Данные успешно обновлены"
        )
        
        return response_data
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Внутренняя ошибка сервера",
                "detail": f"Произошла непредвиденная ошибка: {e}"
            }
        )


@user_router.get(
    "/me/projects",
    response_model=UserProjectsResponse,
    summary="Получить информацию о проектах пользователя (о себе)",
    description="""
    Получение проектов текущего аутентифицированного пользователя.
    
    **Требует аутентификации:** Да
    **Права доступа:** Любой аутентифицированный пользователь
    **Возвращает:** Проекты пользователя и его роли на них
    """
)
async def get_user_projects(
    session: SessionDep,
    status_code=status.HTTP_200_OK,
    me_user=Depends(UserDependency())
):
    """
    GET /api/users/me/projects
    
    Получение проектов текущего пользователя.
    Только аутентифицированный пользователь может получить свои проекты.
    """

    try:

        user_project_role_list = await UserProjectRoleDAO.get_by(
            session,
            user_id=me_user.id
        )

        if not user_project_role_list:
            return UserProjectsResponse(
                project_roles=[]
            )

        project_roles = [
            UserProjectRole(
                project_id=user_project_role.project_id,
                project_name=user_project_role.project.name,
                role_id=user_project_role.role_id,
                role_name=user_project_role.role.name
            )
            for user_project_role in user_project_role_list]

        return UserProjectsResponse(
            project_roles=project_roles
        )

    except HTTPException:
        raise
        
    except Exception as e:
        print(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Внутренняя ошибка сервера",
                "detail": "Произошла непредвиденная ошибка"
            }
        )
