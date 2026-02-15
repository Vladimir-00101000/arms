from src.database.base_dao import BaseDAO
from src.dependency.models import RequirementDependence
from src.dependency.history_models import ReqDependenceHistory


class RequirementDependenceDAO(BaseDAO[RequirementDependence]):
    model = RequirementDependence


class ReqDependenceHistoryDAO(BaseDAO[ReqDependenceHistory]):
    model = ReqDependenceHistory
