"""
Сервисы для интеграции с внешними системами тестирования.
Содержит логику для синхронизации данных между АСУТр и внешними системами.
"""
import httpx
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.integration.dao import ReqTestCaseCoverageDAO
from src.integration.schemas import TestCase, TestCaseList, TestCaseStatus


class TestSystemIntegrationService:
    """Сервис интеграции с внешней системой тестирования"""

    def __init__(
            self,
            base_url: str,
            api_key: str,
            timeout: float = 30.0
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout

    async def fetch_test_cases(
            self,
            project_id: str
    ) -> Optional[TestCaseList]:
        """
        Получить тест-кейсы из внешней системы тестирования.

        Args:
            project_id: ID проекта в системе тестирования

        Returns:
            TestCaseList или None при ошибке
        """
        url = f"{self.base_url}/projects/{project_id}/test-cases"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    url,
                    headers={"X-API-Key": self.api_key}
                )
                response.raise_for_status()
                data = response.json()

                return TestCaseList(
                    project_id=data.get("project_id", project_id),
                    project_name=data.get("project_name"),
                    test_cases=[
                        TestCase(
                            requirement_id=UUID(tc["requirement_id"]),
                            test_case_id=tc["test_case_id"],
                            test_case_name=tc.get("test_case_name"),
                            test_case_status=TestCaseStatus(
                                tc["test_case_status"])
                        )
                        for tc in data.get("test_cases", [])
                    ],
                    total_count=data.get("total_count", 0)
                )
            except httpx.HTTPError as e:
                # Логирование ошибки
                print(f"Error fetching test cases: {e}")
                return None

    async def sync_test_cases_to_db(
            self,
            session: AsyncSession,
            test_cases: list[TestCase],
            user_id: Optional[UUID] = None
    ) -> dict:
        """
        Синхронизировать тест-кейсы в локальную БД.

        Args:
            session: Сессия БД
            test_cases: Список тест-кейсов для синхронизации
            user_id: ID пользователя, выполняющего синхронизацию

        Returns:
            Статистика синхронизации
        """
        created = 0
        updated = 0
        errors = 0

        for tc in test_cases:
            try:
                # Проверяем существование записи
                existing = await ReqTestCaseCoverageDAO.get_by(
                    session,
                    requirement_id=tc.requirement_id,
                    test_case_version_id=tc.test_case_id
                )

                if existing:
                    # Обновляем существующую запись
                    await ReqTestCaseCoverageDAO.update(
                        session,
                        existing[0].id,
                        test_case_name=tc.test_case_name,
                        test_case_status=tc.test_case_status.value
                    )
                    updated += 1
                else:
                    # Создаем новую запись
                    await ReqTestCaseCoverageDAO.create(
                        session,
                        requirement_id=tc.requirement_id,
                        test_case_version_id=tc.test_case_id,
                        test_case_name=tc.test_case_name,
                        test_case_status=tc.test_case_status.value,
                        created_by_user_id=user_id
                    )
                    created += 1
            except Exception as e:
                print(f"Error syncing test case {tc.test_case_id}: {e}")
                errors += 1

        return {
            "created": created,
            "updated": updated,
            "errors": errors,
            "total_processed": len(test_cases),
            "sync_timestamp": datetime.utcnow().isoformat()
        }


class ApiKeyValidator:
    """Валидатор API ключей для интеграции"""

    # TODO: Реализовать хранение ключей в БД
    _valid_keys: set[str] = set()

    @classmethod
    def add_key(cls, key: str):
        """Добавить валидный ключ"""
        cls._valid_keys.add(key)

    @classmethod
    def remove_key(cls, key: str):
        """Удалить ключ"""
        cls._valid_keys.discard(key)

    @classmethod
    def is_valid(cls, key: str) -> bool:
        """Проверить валидность ключа"""
        # Если ключи не настроены - принимаем любой непустой
        if not cls._valid_keys:
            return bool(key)
        return key in cls._valid_keys
