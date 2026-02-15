from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base_model import Base


class ReqDependenceHistory(Base):
    """История изменений зависимостей между требованиями"""

    prev_req_dependence_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("requirement_dependences.id", ondelete="SET NULL"),
        nullable=True
    )
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
