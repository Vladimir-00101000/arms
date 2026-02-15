from sqlalchemy import String, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import UUID, uuid4
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from src.database.base_model import Base
from src.database.enums import UserStatus, Permission as PermissionEnum

if TYPE_CHECKING:
    from .user_project_role import UserProjectRole
    from .role_permission import RolePermission


class User(Base):
    """Пользователь"""

    external_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    login: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    surname: Mapped[Optional[str]] = mapped_column(String(255))
    name: Mapped[Optional[str]] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    status: Mapped[UserStatus] = mapped_column(String(50), nullable=False, default=UserStatus.ACTIVE)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    project_roles = relationship(
        "UserProjectRole",
        back_populates="user", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class Role(Base):
    """Роль в проекте"""

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))

    permissions = relationship(
        "RolePermission",
        back_populates="role", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    project_assignments = relationship(
        "UserProjectRole",
        back_populates="role",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class Permission(Base):
    """Право доступа"""

    permission: Mapped[PermissionEnum] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(255))

    role_permissions = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class RolePermission(Base):
    """Право доступа у роли"""

    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    
    role = relationship("Role", back_populates="permissions", lazy="joined")
    permission = relationship("Permission", back_populates="role_permissions", lazy="joined")

    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )


class UserProjectRole(Base):
    """Роль пользователя на проекте"""

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    
    user = relationship("User", back_populates="project_roles", lazy="joined")
    project = relationship("Project", back_populates="user_roles", lazy="joined")
    role = relationship("Role", back_populates="project_assignments", lazy="joined")

    __table_args__ = (
        UniqueConstraint('user_id', 'project_id', name='uq_user_project'),
    )
