from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserProfile(BaseModel):
    id: UUID = Field(description='ID пользователя')
    login: str = Field(description='Логин пользователя')
    surname: Optional[str] = Field(description='Фамилия пользователя')
    name: Optional[str] = Field(description='Имя пользователя')
    email: str = Field(description='Электронная почта пользователя')
    status: str = Field(description='Статус пользователя')
    is_admin: bool = Field(description='Пользователь администратор')
    created_at: datetime = Field(description='Дата регистрации')

class UserProfileResponse(UserProfile):
    pass

class UserProfilePatchRequest(BaseModel):
    login: Optional[str] = Field(None, description='Логин пользователя')
    surname: Optional[str] = Field(None, description='Фамилия пользователя')
    name: Optional[str] = Field(None, description='Имя пользователя')

class UserProfilePatchResponse(UserProfile):
    message: str = Field(description='Сообщение')

class UserProjectRole(BaseModel):
    project_id: UUID = Field(description='ID проекта')
    project_name: str = Field(description='Название проекта')
    role_id: UUID = Field(description='ID роли')
    role_name: str = Field(description='Название роли')

class UserProjectsResponse(BaseModel):
    project_roles: List[UserProjectRole] = Field(description='Роли пользователя на проектах')
