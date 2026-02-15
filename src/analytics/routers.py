import os
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import text

from src.analytics.schemas import (
    DashboardStats,
    RequirementTraceability,
    TraceabilityIssue,
    CoverageSummary,
    TestCoverage,
    TestCoverageUpdate
)
from src.authorization import UserDependency
from src.database.db_helper import SessionDep
from src.requirement.dao import RequirementDAO
from src.requirement_workflow.dao import RequirementWorkflowDAO

# Роутеры для требований (трассируемость и покрытие тестами)
requirement_analytics_router = APIRouter(prefix='/api/requirements', tags=['Требования'])

# Роутеры для отчётов
reports_router = APIRouter(prefix='/api/reports', tags=['Администрирование'])

# Путь к SQL файлам
SQL_DIR = Path(__file__).parent.parent.parent / 'sql' / 'business_logic'


# ================ Трассируемость требований ================

@requirement_analytics_router.get(
    "/{requirement_id}/traceability",
    response_model=RequirementTraceability,
    status_code=status.HTTP_200_OK,
    summary="Матрица трассируемости"
)
async def get_requirement_traceability(
        session: SessionDep,
        requirement_id: UUID,
        project_id: UUID = Query(..., description="ID проекта"),
        depth: int = Query(2, description="Глубина трассировки"),
        _=Depends(UserDependency())
):
    """Получение матрицы трассируемости требования"""
    
    sql_file = SQL_DIR / 'traceability.sql'
    
    if not sql_file.exists():
        # Если SQL файла нет, вернём пустую структуру
        requirement = await RequirementDAO.get(session, requirement_id)
        return RequirementTraceability(
            requirement_id=requirement.id,
            requirement_name=requirement.name,
            requirement_type=requirement.type,
            targets=[],
            sources=[]
        )
    
    with open(sql_file) as f:
        query = text(f.read())
    
    result = await session.execute(query, {
        "project_id": str(project_id),
        "requirement_id": str(requirement_id)
    })
    
    # Ищем требование в результатах
    for row in result.all():
        if str(row.requirement_id) == str(requirement_id):
            return RequirementTraceability(
                requirement_id=row.requirement_id,
                requirement_name=row.requirement_name,
                requirement_type=row.requirement_type,
                targets=list(row.targets) if row.targets else [],
                sources=list(row.sources) if row.sources else []
            )
    
    # Если не найдено, вернём пустую структуру
    requirement = await RequirementDAO.get(session, requirement_id)
    return RequirementTraceability(
        requirement_id=requirement.id,
        requirement_name=requirement.name,
        requirement_type=requirement.type,
        targets=[],
        sources=[]
    )


# ================ Покрытие тест-кейсами ================

@requirement_analytics_router.get(
    "/{requirement_id}/test-coverage",
    response_model=TestCoverage,
    status_code=status.HTTP_200_OK,
    summary="Получить покрытие тест-кейсами"
)
async def get_test_coverage(
        session: SessionDep,
        requirement_id: UUID,
        _=Depends(UserDependency())
):
    """Получение информации о покрытии требования тест-кейсами"""
    
    sql_file = SQL_DIR / 'test_case.sql'
    
    if not sql_file.exists():
        return TestCoverage(
            requirement_id=requirement_id,
            test_cases=[],
            coverage_percentage=0.0
        )
    
    with open(sql_file) as f:
        query = text(f.read())
    
    result = await session.execute(query, {"requirement_id": str(requirement_id)})
    rows = result.all()
    
    test_cases = [row.test_case_version_id for row in rows if hasattr(row, 'test_case_version_id')]
    
    return TestCoverage(
        requirement_id=requirement_id,
        test_cases=test_cases,
        coverage_percentage=100.0 if len(test_cases) > 0 else 0.0
    )


@requirement_analytics_router.post(
    "/{requirement_id}/test-coverage",
    status_code=status.HTTP_200_OK,
    summary="Обновить покрытие тест-кейсами"
)
async def update_test_coverage(
        session: SessionDep,
        requirement_id: UUID,
        data: TestCoverageUpdate,
        _=Depends(UserDependency())
):
    """Обновление информации о покрытии тест-кейсами"""
    
    from src.analytics.dao import ReqTestCaseCoverageDAO
    from src.analytics.models import ReqTestCaseCoverage
    
    # Создаём или обновляем запись о покрытии
    coverage = ReqTestCaseCoverage(
        requirement_id=requirement_id,
        test_case_version_id=data.test_case_version_id
    )
    
    created = await ReqTestCaseCoverageDAO.create(session, coverage)
    await session.commit()
    
    return {"message": "Покрытие обновлено", "id": str(created.id)}


# ================ Отчёты (Reports) ================

@reports_router.get(
    "/kpi",
    response_model=DashboardStats,
    status_code=status.HTTP_200_OK,
    summary="Дашборд KPI"
)
async def get_kpi_dashboard(
        session: SessionDep,
        project_id: UUID = Query(None, description="ID проекта"),
        period_start: str = Query(None, description="Начало периода"),
        period_end: str = Query(None, description="Конец периода"),
        _=Depends(UserDependency())
):
    """Получение дашборда с ключевыми показателями эффективности"""
    
    if not project_id:
        # Если проект не указан, возвращаем общую статистику по всем проектам
        total_query = text("""
            SELECT COUNT(*) as count
            FROM requirements
        """)
    else:
        total_query = text("""
            SELECT COUNT(*) as count
            FROM requirements
            WHERE project_id = :project_id
        """)
    
    total_result = await session.execute(
        total_query,
        {"project_id": str(project_id)} if project_id else {}
    )
    total = total_result.scalar() or 0
    
    # По статусам
    if project_id:
        status_query = text("""
            SELECT rw.status, COUNT(*) as count
            FROM requirements r
            JOIN requirement_workflows rw ON r.id = rw.requirement_id
            WHERE r.project_id = :project_id
            GROUP BY rw.status
        """)
        status_result = await session.execute(status_query, {"project_id": str(project_id)})
    else:
        status_query = text("""
            SELECT rw.status, COUNT(*) as count
            FROM requirements r
            JOIN requirement_workflows rw ON r.id = rw.requirement_id
            GROUP BY rw.status
        """)
        status_result = await session.execute(status_query)
    
    by_status = {row.status: row.count for row in status_result.all()}
    
    # По типам
    if project_id:
        type_query = text("""
            SELECT r.type, COUNT(*) as count
            FROM requirements r
            WHERE r.project_id = :project_id
            GROUP BY r.type
        """)
        type_result = await session.execute(type_query, {"project_id": str(project_id)})
    else:
        type_query = text("""
            SELECT r.type, COUNT(*) as count
            FROM requirements r
            GROUP BY r.type
        """)
        type_result = await session.execute(type_query)
    
    by_type = {row.type: row.count for row in type_result.all()}
    
    # Статистика покрытия трассируемостью
    coverage_file = SQL_DIR / 'traceability_report' / 'traceability_report_total.sql'
    if coverage_file.exists() and project_id:
        with open(coverage_file) as f:
            coverage_query = text(f.read())
        coverage_result = await session.execute(coverage_query, {"project_id": str(project_id)})
        traceability_coverage = [
            CoverageSummary(
                requirement_type=row.requirement_type,
                uncovered_count=row.uncovered_count,
                total_count=row.total_count,
                coverage_percentage=float(row.coverage_percentage or 0)
            )
            for row in coverage_result.all()
        ]
    else:
        traceability_coverage = []
    
    return DashboardStats(
        total=total,
        by_status=by_status,
        by_type=by_type,
        traceability_coverage=traceability_coverage
    )


@reports_router.get(
    "/requirements",
    status_code=status.HTTP_200_OK,
    summary="Отчет по требованиям"
)
async def get_requirements_report(
        session: SessionDep,
        project_id: UUID = Query(..., description="ID проекта"),
        format: str = Query("json", description="Формат отчета"),
        include_history: bool = Query(False, description="Включить историю"),
        _=Depends(UserDependency())
):
    """Генерация отчета по требованиям"""
    
    # Получение всех требований проекта
    from src.requirement.dao import RequirementDAO
    requirements = await RequirementDAO.get_by_project(session, project_id)
    
    report = {
        "project_id": str(project_id),
        "generated_at": "2026-01-16T00:00:00Z",
        "requirements": [
            {
                "id": str(req.id),
                "name": req.name,
                "type": req.type,
                "created_at": req.created_at.isoformat() if req.created_at else None
            }
            for req in requirements
        ],
        "summary": {
            "total": len(requirements)
        }
    }
    
    return report


@reports_router.get(
    "/traceability",
    status_code=status.HTTP_200_OK,
    summary="Отчет по трассируемости"
)
async def get_traceability_report(
        session: SessionDep,
        project_id: UUID = Query(..., description="ID проекта"),
        _=Depends(UserDependency())
):
    """Генерация отчета по трассируемости требований"""
    
    sql_file = SQL_DIR / 'traceability.sql'
    
    if not sql_file.exists():
        return {
            "project_id": str(project_id),
            "generated_at": "2026-01-16T00:00:00Z",
            "traceability_matrix": []
        }
    
    with open(sql_file) as f:
        query = text(f.read())
    
    result = await session.execute(query, {"project_id": str(project_id)})
    
    traceability_matrix = [
        {
            "requirement_id": str(row.requirement_id),
            "requirement_name": row.requirement_name,
            "linked_to": list(row.targets) if row.targets else [],
            "linked_from": list(row.sources) if row.sources else [],
            "test_coverage": len(row.sources or []) > 0
        }
        for row in result.all()
    ]
    
    return {
        "project_id": str(project_id),
        "generated_at": "2026-01-16T00:00:00Z",
        "traceability_matrix": traceability_matrix
    }
