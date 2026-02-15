"""Модель API ключей для интеграции"""
import secrets
from datetime import datetime
from uuid import UUID

from sqlalchemy import String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base_model import Base


class IntegrationApiKey(Base):
    """API ключ для интеграции с внешними системами"""

    key_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        comment="Хэш API ключа"
    )
    key_prefix: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Префикс ключа для идентификации (asut_int_xxxx)"
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Название внешней системы"
    )
    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
        comment="Описание назначения ключа"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Активен ли ключ"
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Срок действия ключа"
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Последнее использование"
    )

    # Foreign Keys
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    @staticmethod
    def generate_key() -> str:
        """Генерация нового API ключа"""
        return f"asut_int_{secrets.token_hex(24)}"

    @staticmethod
    def get_prefix(key: str) -> str:
        """Получить префикс ключа для отображения"""
        # asut_int_abc123... -> asut_int_abc1****
        if len(key) > 16:
            return key[:16] + "****"
        return key[:8] + "****"

    @staticmethod
    def hash_key(key: str) -> str:
        """Хэширование ключа для хранения"""
        import hashlib
        return hashlib.sha256(key.encode()).hexdigest()
