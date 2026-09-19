from pydantic import BaseModel, ConfigDict
from typing import Optional

class CharacterCreate(BaseModel):
    name: str
    description: str

class CharacterOut(BaseModel):
    id: int
    name: str
    description: str
    # image_url: Optional[str]= None

    model_config = ConfigDict(from_attributes=True)

class CharacterUpdate(BaseModel):
    name: Optional[str]= None
    description: Optional[str]= None