from src.database.base_dao import BaseDAO
from src.user.models import User, Role, Permission, RolePermission, UserProjectRole


class UserDAO(BaseDAO[User]):
    model = User

class RoleDao(BaseDAO[Role]):
    model = Role

class PermissionDAO(BaseDAO[Permission]):
    model = Permission

class RolePermissionDAO(BaseDAO[RolePermission]):
    model = RolePermission

class UserProjectRoleDAO(BaseDAO[UserProjectRole]):
    model = UserProjectRole
