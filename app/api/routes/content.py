from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.deps import get_db
from app.models.app_content import AppContent
from app.models.dashboard_image import DashboardImage
from app.models.roles import UserRole
from app.models.user import User
from app.schemas.content import ContentResponse
from app.services.cloudinary_service import upload_image
from app.services.role_service import require_role


router = APIRouter(tags=["content"])


@router.get("", response_model=ContentResponse)
def get_content(
    db: Session = Depends(get_db),
):
    content = db.query(AppContent).first()

    if not content:
        return ContentResponse(
            home={
                "title": None,
                "subtitle": None,
                "content": None,
            },
            dashboard_images=[],
            quote={
                "text": None,
                "image_url": None,
            },
            updated_at=None,
        )

    images = (
        db.query(DashboardImage)
        .filter(DashboardImage.app_content_id == content.id)
        .order_by(DashboardImage.display_order.asc())
        .all()
    )

    return {
        "home": {
            "title": content.home_title,
            "subtitle": content.home_subtitle,
            "content": content.home_content,
        },
        "dashboard_images": images,
        "quote": {
            "text": content.quote,
            "image_url": content.quote_image_url,
        },
        "updated_at": content.updated_at,
    }
