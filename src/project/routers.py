from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException, Query, Path

from src.authorization import UserDependency, UserRoleDependency
from src.database.db_helper import SessionDep
from src.database.enums import Role as RoleEnum
from src.project.dao import ProjectDAO
from src.project.schemas import (
    ProjectCreate,
    ProjectUpdate,
    Project,
    ProjectList,
    Role,
    UserProjectRoleListResponse,
    UserProjectRole,
    UserProjectChangeRoleResponse)
from src.requirement.dao import RequirementDAO
from src.requirement.schemas import RequirementListResponse

from src.user.dao import UserProjectRoleDAO, RoleDao, UserDAO
# from src.user.models import Role

project_router = APIRouter(prefix='/api/projects', tags=['Проекты'])


@project_router.get(
    "/",
    response_model=ProjectList,
    status_code=status.HTTP_200_OK,
    summary="Получить список проектов",
    description="Получение списка проектов с возможностью фильтрации"
)
async def get_projects(
        session: SessionDep,
        user_id: UUID = Query(..., description="ID пользователя"),
        created_by: Optional[UUID] = Query(None, description="Фильтр по создателю"),
        _=Depends(UserDependency())
):
    filters = {"created_by_user_id": user_id}
    if created_by is not None:
        filters["created_by_user_id"] = created_by

    projects = await ProjectDAO.get_by(session, **filters)
    return ProjectList(data=projects)


@project_router.post(
    "/",
    response_model=Project,
    status_code=status.HTTP_201_CREATED,
    summary="Создать проект",
    description="Создание нового проекта. Требуется право PROJECT_CREATE"
)
async def create_project(
        session: SessionDep,
        project_data: ProjectCreate,
        current_user=Depends(UserDependency())
):
    # TODO: проверка прав PROJECT_CREATE
    existing = await ProjectDAO.get_by(session, name=project_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Проект с таким названием уже существует"
        )

    project = await ProjectDAO.create(
        session,
        **project_data.model_dump(),
        created_by_user_id=current_user.id
    )

    role = await RoleDao.get_by(session, name=RoleEnum.PROJECT_OWNER)

    _ = await UserProjectRoleDAO.create(
        session,
        project_id=project.id,
        user_id=current_user.id,
        role_id=role[0].id
    )

    return project


@project_router.get(
    "/{project_id}",
    response_model=Project,
    status_code=status.HTTP_200_OK,
    summary="Получить информацию о проекте"
)
async def get_project(
        session: SessionDep,
        project_id: UUID,
        _=Depends(UserDependency())
):
    try:
        project = await ProjectDAO.get(session, project_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )
    return project

@project_router.get(
    "/{project_id}/role",
    response_model=Role,
    status_code=status.HTTP_200_OK,
    summary="Получить роль на проекте"
)
async def get_project_role(
        session: SessionDep,
        project_id: UUID,
        current_user=Depends(UserDependency())
):
    try:
        user_project_role = await UserProjectRoleDAO.get_by(
            session,
            project_id=project_id,
            user_id=current_user.id
        )

        return user_project_role[0].role
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )


@project_router.get(
    "/{project_id}/users",
    response_model=UserProjectRoleListResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить пользователей проекта"
)
async def get_project_users(
        session: SessionDep,
        project_id: UUID,
        _=Depends(UserDependency())
):
    try:
        project_users = await UserProjectRoleDAO.get_by(session, project_id=project_id)
        
        users = []

        for project_user in project_users:
            user = project_user.user

            user_name = user.login
            if user.name and user.surname:
                user_name = user.name + ' ' + user.surname

            users.append(
                UserProjectRole(
                    user_id=user.id,
                    user_name=user_name,
                    user_email=user.email,
                    user_role_name=project_user.role.name,
                )
            )

        return UserProjectRoleListResponse(
            users=users
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Проект не найден {e}"
        )


@project_router.post(
    "/{project_id}/users",
    response_model=UserProjectRole,
    status_code=status.HTTP_200_OK,
    summary="Добавить пользователя на проект"
)
async def create_project_users(
        session: SessionDep,
        project_id: UUID,
        new_project_user_email: str = Query(description="Новый пользователь"),
        new_role: str = Query(description="Новая роль"),
        _=Depends(UserDependency())
):
    try:
        user = await UserDAO.get_by(
            session,
            email=new_project_user_email
        )
        
        if not user:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

        user = user[0]

        role = await RoleDao.get_by(
            session,
            name=new_role
        )

        if not role:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Роль не найдена"
        )

        role = role[0]

        user_project_role = await UserProjectRoleDAO.create(
            session,
            project_id=project_id,
            user_id=user.id,
            role_id=role.id
        )

        user_name = user.login
        if user.name and user.surname:
            user_name = user.name + ' ' + user.surname

        return UserProjectRole(
            user_id=user.id,
            user_name=user_name,
            user_email=user.email,
            user_role_name=role.name,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Проект не найден {e}"
        )


@project_router.post(
    "/{project_id}/users/{user_id}/changerole",
    response_model=UserProjectChangeRoleResponse,
    status_code=status.HTTP_200_OK,
    summary="Изменить роль пользователя на проекте"
)
async def changerole_project_users(
        session: SessionDep,
        user_id: UUID = Path(description="ID пользователя"),
        project_id: UUID = Path(description="ID проекта"),
        new_role: str = Query(description="Новая роль"),
        _=Depends(UserDependency())
):
    try:

        filters = {
            "project_id": project_id,
            "user_id": user_id
        }

        project_user = await UserProjectRoleDAO.get_by(
            session,
            **filters
        )
        
        if len(project_user) == 0:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь на проекте не найден"
        )

        project_user = project_user[0]

        new_role = await RoleDao.get_by(
            session,
            name=new_role
        )

        if len(new_role) == 0:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь на проекте не найден"
        )

        new_role = new_role[0]

        project_user = await UserProjectRoleDAO.update(
            session,
            project_user.id,
            role_id=new_role.id
        )
        
        return UserProjectChangeRoleResponse(
            new_role=new_role.name
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Проект не найден {e}"
        )


@project_router.delete(
    "/{project_id}/users/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить пользователя с проекта"
)
async def delete_project_user(
        session: SessionDep,
        user_id: UUID = Path(description="ID пользователя"),
        project_id: UUID = Path(description="ID проекта"),
        _=Depends(UserDependency())
):
    try:

        filters = {
            "project_id": project_id,
            "user_id": user_id
        }

        project_user = await UserProjectRoleDAO.get_by(
            session,
            **filters)
        
        if project_user is None:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь на проекте не найден"
        )

        project_user = project_user[0]

        _ = await UserProjectRoleDAO.delete(
            session,
            project_user.id
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )


@project_router.put(
    "/{project_id}",
    response_model=Project,
    status_code=status.HTTP_200_OK,
    summary="Обновить проект",
    description="Обновление проекта (возможно изменить описание проекта)"
)
async def update_project(
        session: SessionDep,
        project_id: UUID,
        project_data: ProjectUpdate,
        _=Depends(UserDependency())
):
    try:
        await ProjectDAO.get(session, project_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )

    update_data = project_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нет данных для обновления"
        )

    project = await ProjectDAO.update(session, project_id, **update_data)
    return project


@project_router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить проект",
    description="Полное удаление проекта со всеми связанными требованиями и историей"
)
async def delete_project(
        session: SessionDep,
        project_id: UUID,
        _=Depends(UserDependency())
):
    try:
        await ProjectDAO.get(session, project_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )

    await ProjectDAO.delete(session, project_id)


@project_router.get(
    "/{project_id}/requirements",
    response_model=RequirementListResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить требования проекта",
    description="Получение всех требований проекта"
)
async def get_project_requirements(
        session: SessionDep,
        project_id: UUID,
        type: Optional[str] = Query(None, description="Фильтр по типу требования"),
        req_status: Optional[str] = Query(None, alias="status", description="Фильтр по статусу"),
        _=Depends(UserDependency())
):
    try:
        await ProjectDAO.get(session, project_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )

    filters = {"project_id": project_id}
    if type:
        filters["type"] = type
    if req_status:
        filters["status"] = req_status

    requirements = await RequirementDAO.get_by(session, **filters)
    return RequirementListResponse(data=requirements)