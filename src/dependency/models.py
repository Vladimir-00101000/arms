from uuid import UUID

from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base_model import Base


class RequirementDependence(Base):
    """Зависимость между требованиями"""

    source_requirement_id: Mapped[UUID] = mapped_column(
        ForeignKey("requirements.id", ondelete="CASCADE")
    )
    target_requirement_id: Mapped[UUID] = mapped_column(
        ForeignKey("requirements.id", ondelete="CASCADE")
    )
    type: Mapped[str] = mapped_column(String(50))
    strength: Mapped[int] = mapped_column(Integer, default=3)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    source_requirement_group_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("requirement_groups.id", ondelete="SET NULL"),
        nullable=True
    )
    target_requirement_group_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("requirement_groups.id", ondelete="SET NULL"),
        nullable=True
    )