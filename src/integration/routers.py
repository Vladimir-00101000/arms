"""
API для интеграции АСУТр с системами тестирования.
Предоставляет endpoints для обмена информацией о проектах,
требованиях и тест-кейсах.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException, Query, Security
from fastapi.security import APIKeyHeader

from src.database.db_helper import SessionDep
from src.integration.schemas import (
    TestSystemProjectList,
    TestSystemProject,
    IntegrationRequirementList,
    IntegrationRequirement,
    RequirementListPagination,
    TestCaseList,
    TestCase,
    RequirementStatus,
    RequirementType,
    ErrorResponse
)
from src.integration.dao import ReqTestCaseCoverageDAO
from src.integration.api_key_dao import IntegrationApiKeyDAO
from src.integration.api_key_models import IntegrationApiKey
from src.project.dao import ProjectDAO
from src.requirement.dao import RequirementDAO
from src.requirement_content.dao import RequirementContentDAO
from src.requirement_workflow.dao import RequirementWorkflowDAO

# API Key аутентификация
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

integration_router = APIRouter(
    tags=['Интеграция с системами тестирования']
)


async def verify_api_key(
    session: SessionDep,
    api_key: str = Security(api_key_header)
) -> IntegrationApiKey:
    """Проверка API ключа для интеграции через БД"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "MISSING_API_KEY",
                "message": "API ключ не предоставлен",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    # Хэшируем полученный ключ и ищем в БД
    key_hash = IntegrationApiKey.hash_key(api_key)
    key_record = await IntegrationApiKeyDAO.get_active_by_hash(session, key_hash)

    if not key_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_API_KEY",
                "message": "Недействительный или просроченный API ключ",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    # Обновляем время последнего использования
    await IntegrationApiKeyDAO.update(
        session,
        key_record.id,
        last_used_at=datetime.utcnow()
    )

    return key_record


# ================ Система тестирования → АСУТр ================

@integration_router.get(
    "/integration/requirements-projects",
    response_model=TestSystemProjectList,
    status_code=status.HTTP_200_OK,
    summary="Получить список проектов для синхронизации",
    description="""
    Возвращает список проектов, доступных для синхронизации с системой тестирования.
    Система тестирования использует этот endpoint для получения списка проектов,
    доступных для синхронизации требований и тест-кейсов.
    """,
    responses={
        401: {"model": ErrorResponse, "description": "Недействительный API ключ"},
        403: {"model": ErrorResponse, "description": "Нет прав доступа"}
    }
)
async def get_requirements_projects(
    session: SessionDep,
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        description="Фильтр по статусу проекта"
    ),
    api_key: IntegrationApiKey = Depends(verify_api_key)
):
    """Получение списка проектов для синхронизации с системой тестирования"""
    filters = {}
    if status_filter:
        filters["status"] = status_filter

    projects = await ProjectDAO.get_by(session, **filters)

    project_list = [
        TestSystemProject(
            id=p.id,
            name=p.name,
            code=getattr(p, 'code', None),
            description=p.description,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at,
            test_system_id=getattr(p, 'test_system_id', None)
        )
        for p in projects
    ]

    return TestSystemProjectList(
        projects=project_list,
        sync_timestamp=datetime.utcnow(),
        total_count=len(projects),
        filtered_count=len(project_list)
    )


@integration_router.get(
    "/integration/projects/{project_id}/requirements",
    response_model=IntegrationRequirementList,
    status_code=status.HTTP_200_OK,
    summary="Получить список требований проекта",
    description="""
    Возвращает список требований указанного проекта для синхронизации.
    Система тестирования использует этот endpoint для получения требований,
    которые должны быть покрыты тест-кейсами.
    """,
    responses={
        401: {"model": ErrorResponse, "description": "Недействительный API ключ"},
        403: {"model": ErrorResponse, "description": "Нет прав доступа"},
        404: {"model": ErrorResponse, "description": "Проект не найден"}
    }
)
async def get_project_requirements(
    session: SessionDep,
    project_id: UUID,
    status_filter: Optional[RequirementStatus] = Query(
        None,
        alias="status",
        description="Фильтр по статусу требования"
    ),
    type_filter: Optional[RequirementType] = Query(
        None,
        alias="type",
        description="Фильтр по типу требования"
    ),
    limit: int = Query(1000, ge=1, le=10000, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    _: str = Depends(verify_api_key)
):
    """Получение списка требований проекта для синхронизации"""
    # Проверяем существование проекта
    try:
        project = await ProjectDAO.get(session, project_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "PROJECT_NOT_FOUND",
                "message": f"Проект с ID {project_id} не найден",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    # Получаем требования проекта
    filters = {"project_id": project_id}
    if type_filter:
        filters["type"] = type_filter.value

    requirements = await RequirementDAO.get_by(session, **filters)

    # Собираем полную информацию о требованиях
    result = []
    for req in requirements:
        # Получаем content для description
        content_list = await RequirementContentDAO.get_by(
            session, requirement_id=req.id
        )
        content = content_list[0] if content_list else None

        # Получаем workflow для status и priority
        workflow_list = await RequirementWorkflowDAO.get_by(
            session, requirement_id=req.id
        )
        workflow = workflow_list[0] if workflow_list else None

        # Фильтруем по статусу если указан
        req_status = workflow.status if workflow else "draft"
        if status_filter and req_status != status_filter.value:
            continue

        # Проверяем наличие тест-кейсов
        test_cases = await ReqTestCaseCoverageDAO.get_by(
            session, requirement_id=req.id
        )

        result.append(IntegrationRequirement(
            id=req.id,
            name=req.name,
            description=content.description_text if content else None,
            status=RequirementStatus(req_status),
            priority=workflow.priority if workflow else 1,
            type=RequirementType(req.type),
            created_at=req.created_at,
            updated_at=req.updated_at,
            version=1,  # TODO: получать из истории
            has_test_coverage=len(test_cases) > 0
        ))

    total = len(result)
    # Применяем пагинацию
    paginated = result[offset:offset + limit]

    return IntegrationRequirementList(
        project_id=project.id,
        project_name=project.name,
        requirements=paginated,
        total_count=total,
        filtered_count=len(paginated),
        sync_timestamp=datetime.utcnow(),
        pagination=RequirementListPagination(
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total
        )
    )


# ================ АСУТр → Система тестирования ================

@integration_router.get(
    "/test-systems/projects/{project_id}/test-cases",
    response_model=TestCaseList,
    status_code=status.HTTP_200_OK,
    summary="Получить тест-кейсы проекта",
    description="""
    Возвращает список тест-кейсов для указанного проекта из локального хранилища.
    Данные о покрытии тест-кейсами синхронизируются из внешней системы тестирования.
    """,
    responses={
        401: {"model": ErrorResponse, "description": "Недействительный API ключ"},
        404: {"model": ErrorResponse, "description": "Проект не найден"}
    }
)
async def get_project_test_cases(
    session: SessionDep,
    project_id: UUID,
    _: str = Depends(verify_api_key)
):
    """Получение тест-кейсов проекта из локального хранилища"""
    # Проверяем существование проекта
    try:
        project = await ProjectDAO.get(session, project_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "PROJECT_NOT_FOUND",
                "message": f"Проект с ID {project_id} не найден",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    # Получаем все требования проекта
    requirements = await RequirementDAO.get_by(session, project_id=project_id)
    req_ids = [r.id for r in requirements]

    # Собираем тест-кейсы для всех требований
    test_cases = []
    for req_id in req_ids:
        coverages = await ReqTestCaseCoverageDAO.get_by(
            session, requirement_id=req_id
        )
        for cov in coverages:
            test_cases.append(TestCase(
                requirement_id=cov.requirement_id,
                test_case_id=cov.test_case_version_id,
                test_case_name=cov.test_case_name,
                test_case_status=cov.test_case_status
            ))

    return TestCaseList(
        project_id=str(project_id),
        project_name=project.name,
        test_cases=test_cases,
        total_count=len(test_cases)
    )
