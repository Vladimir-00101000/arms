from fastapi import Request, HTTPException, status
from uuid import UUID
from typing import List, Tuple

from src.database.db_helper import SessionDep

from src.user.models import User, UserStatus, Permission
from src.user.dao import UserDAO


class TestUserDependency:

    async def __call__(
            self,
            session: SessionDep,
            request: Request
    ) -> User:
        """
        Возвращает авторизированного пользователя
        """
        try:
            
            user = await UserDAO.get_by(session, login="ivan.petrov")
            return user[0]
        
        except HTTPException:
            raise

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Внутренняя ошибка сервера",
                    "detail": "Произошла непредвиденная ошибка"
                }
            )


class UserDependency:

    async def __call__(
            self,
            session: SessionDep,
            request: Request
    ) -> User:
        """
        Возвращает авторизированного пользователя
        """
        try:

            login = None
            external_id = request.headers.get("x-user")
            email = request.headers.get("x-user-email")
            name = request.headers.get("x-user-name")
            surname = request.headers.get("x-user-surname")
            
            if not external_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                            "error": "Пользователь не авторизован",
                            "detail": "Не указан идентификатор пользователя (X-User-ID)"
                        }
                )
            
            users = await UserDAO.get_by(session, external_id=external_id)
            
            if not users:
                if not email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": "Пользователь не авторизован",
                            "detail": "Не указан email для создания пользователя (X-User-Email)"
                        }
                    )

                user_data = {
                    "external_id": external_id,
                    "login": login or email.split("@")[0],
                    "name": name,
                    "surname": surname,
                    "email": email,
                    "status": UserStatus.ACTIVE
                }

                user = await UserDAO.create(session, **user_data)
                return user

            else:
                if users[0].status == UserStatus.INACTIVE:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={
                            "error": "Недостаточно прав",
                            "detail": "Пользователь деактивирован"
                        }
                    )

            return users[0]

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Внутренняя ошибка сервера",
                    "detail": f"Произошла непредвиденная ошибка: {e}"
                }
            )

# UserDependency=TestUserDependency


class TestAdminDependency:

    async def __call__(
            self,
            session: SessionDep,
            request: Request
    ) -> User:
        """
        Возвращает авторизированного админа
        """
        try:
            
            user = await UserDAO.get_by(session, login="admin")
            return user[0]
        
        except HTTPException:
            raise

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Внутренняя ошибка сервера",
                    "detail": "Произошла непредвиденная ошибка"
                }
            )


class AdminDependency:

    async def __call__(
            self,
            session: SessionDep,
            request: Request
    ) -> User:
        """
        Возвращает авторизированного пользователя
        """
        try:
            login = None
            external_id = request.headers.get("x-user")
            email = request.headers.get("x-user-email")
            name = request.headers.get("x-user-name")
            surname = request.headers.get("x-user-surname")
            
            if not external_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                            "error": "Пользователь не авторизован",
                            "detail": "Не указан идентификатор пользователя (X-User-ID)"
                        }
                )
            
            users = await UserDAO.get_by(session, external_id=external_id)
            
            if not users:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,

                    detail={
                        "error": "Недостаточно прав",
                        "detail": "Необходимы права администратора"
                    }
                )

            else:
                if users[0].status == UserStatus.INACTIVE:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={
                            "error": "Недостаточно прав",
                            "detail": "Пользователь деактивирован"
                        }
                    )
    
                if not users[0].is_admin:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,

                        detail={
                            "error": "Недостаточно прав",
                            "detail": "Необходимы права администратора"
                        }
                    )

            return users[0]

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Внутренняя ошибка сервера",
                    "detail": "Произошла непредвиденная ошибка"
                }
            )


# AdminDependency = TestAdminDependency

class UserRoleDependency:

    def __init__(self, project_id: UUID):
        self.user = UserDependency()
        self.project_id = project_id

    async def __call__(
            self,
            session: SessionDep,
            request: Request
    ) -> Tuple[User, List[Permission]]:
        """
        Возвращает авторизированного пользователя и его права доступа на проекте
        """
        try:
            
            role = next(
                (
                    project_role.role for project_role in user.project_roles 
                    if project_role.project_id == self.project_id
                ), 
                None
            )

            permissions = [role_permission.permission for role_permission in role.permissions]

            return [self.user, permissions]

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Внутренняя ошибка сервера",
                    "detail": "Произошла непредвиденная ошибка"
                }
            )
