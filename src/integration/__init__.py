"""
Пакет интеграции АСУТр с внешними системами тестирования.

Предоставляет API для:
- Синхронизации проектов и требований с системами тестирования
- Получения информации о покрытии требований тест-кейсами
- Обмена данными между АСУТр и внешними системами
"""
from src.analytics.models import ReqTestCaseCoverage
from src.integration.routers import integration_router
from src.integration.dao import ReqTestCaseCoverageDAO
from src.integration.schemas import TestCaseStatus
from src.integration.services import TestSystemIntegrationService, ApiKeyValidator

__all__ = [
    "integration_router",
    "ReqTestCaseCoverage",
    "TestCaseStatus",
    "ReqTestCaseCoverageDAO",
    "TestSystemIntegrationService",
    "ApiKeyValidator",
]
