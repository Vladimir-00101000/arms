from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DependencyType(str, Enum):
    BLOCKS = "blocks"
    DEPENDS_ON = "depends_on"
    RELATED_TO = "related_to"
    DUPLICATES = "duplicates"
    REFINES = "refines"


class DependencyDirection(str, Enum):
    INCOMING = "incoming"
    OUTGOING = "outgoing"
    BOTH = "both"


# === Request Schemas ===
class DependencyCreate(BaseModel):
    target_requirement_id: UUID
    type: DependencyType
    strength: int = Field(default=3, ge=1, le=5)
    description: Optional[str] = None


# === Response Schemas ===
class Dependency(BaseModel):
    id: UUID
    source_requirement_id: UUID
    target_requirement_id: UUID
    type: DependencyType
    strength: int = Field(ge=1, le=5)
    description: Optional[str] = None
    source_requirement_group_id: Optional[UUID] = None
    target_requirement_group_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


class DependencyList(BaseModel):
    incoming: list[Dependency]
    outgoing: list[Dependency]
