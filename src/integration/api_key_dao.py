from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_dao import BaseDAO
from src.integration.api_key_models import IntegrationApiKey


class IntegrationApiKeyDAO(BaseDAO[IntegrationApiKey]):
    model = IntegrationApiKey

    @classmethod
    async def get_by_key_hash(
            cls,
            session: AsyncSession,
            key_hash: str
    ) -> IntegrationApiKey | None:
        """Найти ключ по хэшу"""
        query = select(cls.model).where(cls.model.key_hash == key_hash)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_active_by_hash(
            cls,
            session: AsyncSession,
            key_hash: str
    ) -> IntegrationApiKey | None:
        """Найти активный непросроченный ключ"""
        from datetime import datetime

        query = select(cls.model).where(
            cls.model.key_hash == key_hash,
            cls.model.is_active == True
        )
        result = await session.execute(query)
        key = result.scalar_one_or_none()

        if key and key.expires_at and key.expires_at < datetime.utcnow():
            return None  # Ключ просрочен

        return key
