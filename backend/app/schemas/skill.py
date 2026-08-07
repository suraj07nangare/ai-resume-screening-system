import uuid

from pydantic import BaseModel


class SkillRead(BaseModel):
    id: uuid.UUID
    name: str
    normalized_name: str

    model_config = {"from_attributes": True}
