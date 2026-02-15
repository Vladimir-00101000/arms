import uvicorn
from fastapi import FastAPI

from src.analytics.routers import requirement_analytics_router, reports_router
from src.dependency.routers import dependency_router
from src.integration import integration_router
from src.integration.api_key_routers import api_key_router
from src.project.routers import project_router
from src.project_config import settings
from src.requirement.routers import requirement_router
from src.requirement_content.routers import requirement_content_router
from src.requirement_workflow.routers import requirement_workflow_router
from src.user.routers import user_router
from src.admin.routers import admin_router
from src.debug.routers import debug_router

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),  # В файл
        logging.StreamHandler()          # В консоль
    ]
)

def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description="API для системы управления требованиями согласно ТЗ ГОСТ 34.602-2020"
    )
    
    # Подключаем роутеры
    application.include_router(project_router)
    application.include_router(requirement_router)
    application.include_router(requirement_content_router)
    application.include_router(requirement_workflow_router)
    application.include_router(user_router)
    application.include_router(admin_router)
    application.include_router(debug_router)
    application.include_router(dependency_router)
    application.include_router(requirement_analytics_router)
    application.include_router(reports_router)
    application.include_router(integration_router)
    application.include_router(api_key_router)

    return application


app = get_application()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
