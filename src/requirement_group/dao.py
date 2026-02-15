from src.database.base_dao import BaseDAO
from src.requirement_group.models import RequirementGroup


class RequirementGroupDAO(BaseDAO[RequirementGroup]):
    model = RequirementGroup
