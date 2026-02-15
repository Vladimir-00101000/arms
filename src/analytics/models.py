from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base_model import Base


class ReqTestCaseCoverage(Base):
    """Покрытие требований тест-кейсами"""
    __tablename__ = "req_test_case_coverage"
    
    requirement_id: Mapped[UUID] = mapped_column(
        ForeignKey("requirements.id", ondelete="CASCADE")
    )
    test_case_version_id: Mapped[str] = mapped_column(String(255))

