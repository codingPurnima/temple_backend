from pydantic import BaseModel, ConfigDict
from typing import Optional

class LyricsSchema(BaseModel):
    title: str
    content: str
    author: Optional[str]= None

    model_config = ConfigDict(from_attributes=True)

class LyricsOut(BaseModel):
    id: int
    title: str
    content: str
    author: Optional[str]= None

    model_config = ConfigDict(from_attributes=True)

class LyricsUpdate(BaseModel):
    title: Optional[str]= None
    content: Optional[str]= None
    author: Optional[str]= None