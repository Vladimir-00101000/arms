"""Перечисления (Enums) для базы данных"""
from enum import Enum


class UserStatus(str, Enum):
    """Статус пользователя"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class RequirementType(str, Enum):
    """Тип требования"""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non-functional"
    BUSINESS = "business"


class WorkflowStatus(str, Enum):
    """Статус workflow требования"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    ARCHIVED = "archived"


class ApprovalAction(str, Enum):
    """Действие при согласовании"""
    APPROVE = "approve"
    REJECT = "reject"


class RejectReason(str, Enum):
    """Причина отклонения требования"""
    INCORRECT = "incorrect"
    INCOMPLETE = "incomplete"
    DUPLICATE = "duplicate"
    OUTDATED = "outdated"


class Permission(str, Enum):
    """Права доступа"""

    PROJECT_EDIT = "project:edit"
    PROJECT_DELETE = "project:delete"
    PROJECT_MANAGE_USERS = "project:manage_users"

    REQUIREMENT_CREATE = "requirement:create"
    REQUIREMENT_READ = "requirement:read"
    REQUIREMENT_UPDATE = "requirement:update"
    REQUIREMENT_DELETE = "requirement:delete"
    REQUIREMENT_APPROVE = "requirement:approve"
    REQUIREMENT_REJECT = "requirement:reject"
    REQUIREMENT_REVIEW = "requirement:review"

class Role(str, Enum):
    """Роли"""

    PROJECT_OWNER = "Владелец проекта"
    PROJECT_MANAGER = "Менеджер проекта"
    PROJECT_ANALYST = "Аналитик"
    PROJECT_REVIEWER = "Участник"
    PROJECT_PARTICIPANT = "Рецензент"
