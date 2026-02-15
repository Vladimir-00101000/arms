from typing import Optional, List
from uuid import UUID

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base_model import Base


class Project(Base):
    """Проект"""
    name: Mapped[str] = mapped_column(String(255), unique=True)
    code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        unique=True,
        comment="Код проекта"
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    status: Mapped[str] = mapped_column(String(50), default="active")
    test_system_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="ID проекта во внешней системе тестирования"
    )

    # Foreign Keys
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    user_roles = relationship(
        "UserProjectRole",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
