from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException, Query, Request

from src.authorization import UserDependency
from src.database.db_helper import SessionDep
from src.project.dao import ProjectDAO
from src.project.schemas import (ProjectCreate, ProjectUpdate, Project,
                                 ProjectList)
from src.requirement.dao import RequirementDAO
from src.requirement.schemas import RequirementListResponse

debug_router = APIRouter(prefix='/api/debug', tags=['Проекты'])


@debug_router.get(
    "/request"
)
async def debug_request(request: Request):
    """Выводит всю информацию о запросе"""
    
    # Все заголовки
    headers = dict(request.headers)
    
    # Параметры запроса
    query_params = dict(request.query_params)
    
    # Тело запроса (если есть)
    body = {}
    try:
        body = await request.json()
    except:
        body_bytes = await request.body()
        if body_bytes:
            body = {"raw_body": body_bytes.decode('utf-8', errors='ignore')}
    
    # Cookies
    cookies = request.cookies
    
    return {
        "method": request.method,
        "url": str(request.url),
        "headers": headers,
        "query_params": query_params,
        "cookies": cookies,
        "body": body,
        "client": {
            "host": request.client.host if request.client else None,
            "port": request.client.port if request.client else None
        }
    }

@debug_router.get(
    "/headers-only"
)
async def debug_headers(request: Request):
    """Только заголовки (проще для анализа)"""
    return {
        "all_headers": dict(request.headers),
        "important_headers": {
            "x-user": request.headers.get("x-user"),
            "x-user-id": request.headers.get("x-user-id"),
            "x-user-email": request.headers.get("x-user-email"),
            "x-user-name": request.headers.get("x-user-name"),
            "x-user-surname": request.headers.get("x-user-surname"),
            "authorization": request.headers.get("authorization"),
            "cookie": request.headers.get("cookie")
        }
    }