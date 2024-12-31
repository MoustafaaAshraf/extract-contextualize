from pydantic import BaseModel, Field


class Entity(BaseModel):
    """
    Represents an entity extracted from a PDF document.
    """
    entity: str = Field(..., description="The extracted entity")
    context: str = Field(..., description="The context of the entity")
    start: int = Field(..., description="The start index of the entity in the text")
    end: int = Field(..., description="The end index of the entity in the text")