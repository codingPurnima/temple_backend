from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class HomeContentResponse(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    content: Optional[str] = None


class DashboardImageResponse(BaseModel):
    id: int
    image_url: str
    display_order: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class QuoteResponse(BaseModel):
    text: Optional[str] = None
    image_url: Optional[str] = None


class ContentResponse(BaseModel):
    home: HomeContentResponse
    dashboard_images: list[DashboardImageResponse]
    quote: QuoteResponse
    updated_at: Optional[datetime] = None