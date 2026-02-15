from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class User(BaseModel):
    id: UUID = Field(description='ID пользователя')
    login: str = Field(description='Логин пользователя')
    surname: Optional[str] = Field(description='Фамилия пользователя')
    name: Optional[str] = Field(description='Имя пользователя')
    email: str = Field(description='Электронная почта пользователя')
    status: str = Field(description='Статус пользователя')
    is_admin: bool = Field(description='Пользователь администратор')
    created_at: datetime = Field(description='Дата и время создания пользователя')
    updated_at: datetime = Field(description='Дата и время редактирования пользователя')


class Pagination(BaseModel):
    total: int = Field(description='Всего записей')
    page: int = Field(description='Страница'),
    limit: int = Field(description='Количество элементов на странице'),
    pages: int = Field(description='Всего страниц')


class UserListResponse(BaseModel):
    data: List[User] = Field(description='Список пользователей')
    pagination: Pagination = Field(description='Пагинация')


class UserProjectRole(BaseModel):
    project_id: UUID = Field(description='ID проекта')
    project_name: str = Field(description='Название проекта')
    role_id: UUID = Field(description='ID роли')
    role_name: str = Field(description='Название роли')


class UserDetailResponce(User):
    project_roles: List[UserProjectRole] = Field(description='Проекты и роли пользователя')

class UserChangeStatResponse(BaseModel):
    status: str = Field(description='Новый статус пользователя')

class UserChangeRoleResponse(BaseModel):
    is_admin: bool = Field(description='Администратор/не администратор')
