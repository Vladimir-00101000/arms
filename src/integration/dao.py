from src.analytics.models import ReqTestCaseCoverage
from src.database.base_dao import BaseDAO


class ReqTestCaseCoverageDAO(BaseDAO[ReqTestCaseCoverage]):
    model = ReqTestCaseCoverage
