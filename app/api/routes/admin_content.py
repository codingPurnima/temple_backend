from typing import Optional, Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.app_content import AppContent
from app.models.dashboard_image import DashboardImage
from app.models.roles import UserRole
from app.models.user import User
from app.schemas.content import (
    ContentResponse,
    DashboardImageResponse,
)
from app.services.cloudinary_service import (
    delete_image,
    upload_image,
)
from app.services.role_service import require_role


router = APIRouter(
    prefix="/content",
    tags=["admin-content"],
)


def get_or_create_content(db: Session) -> AppContent:
    content = db.query(AppContent).first()

    if not content:
        content = AppContent()
        db.add(content)
        db.flush()

    return content


# ---------------------------------------------------------
# UPDATE HOME + QUOTE CONTENT
# ---------------------------------------------------------

@router.put("", response_model=ContentResponse)
async def update_content(
    home_title: Optional[str] = Form(None),
    home_subtitle: Optional[str] = Form(None),
    home_content: Optional[str] = Form(None),

    quote: Optional[str] = Form(None),

    quote_image: Optional[UploadFile] = File(None),
    clear_quote_image: bool = Form(False),

    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])
    ),
):
    has_text_update = any(
        value is not None
        for value in [
            home_title,
            home_subtitle,
            home_content,
            quote,
        ]
    )

    has_image_update = (
        quote_image is not None
        or clear_quote_image
    )

    if not has_text_update and not has_image_update:
        raise HTTPException(
            status_code=400,
            detail="No content changes were provided",
        )

    if quote_image is not None:
        if (
            not quote_image.content_type
            or not quote_image.content_type.startswith("image/")
        ):
            raise HTTPException(
                status_code=400,
                detail="Quote image must be an image",
            )

    if quote_image is not None and clear_quote_image:
        raise HTTPException(
            status_code=400,
            detail="Choose either a new quote image or clear the existing image",
        )

    content = get_or_create_content(db)

    old_quote_public_id = None
    uploaded_public_id = None

    try:
        # -------------------------
        # Text fields
        # -------------------------

        if home_title is not None:
            content.home_title = home_title

        if home_subtitle is not None:
            content.home_subtitle = home_subtitle

        if home_content is not None:
            content.home_content = home_content

        if quote is not None:
            content.quote = quote

        # -------------------------
        # Quote image
        # -------------------------

        if quote_image is not None:
            result = upload_image(
                quote_image,
                folder="bhaktipath/quote",
            )

            uploaded_public_id = result["public_id"]

            old_quote_public_id = content.quote_image_public_id

            content.quote_image_url = result["url"]
            content.quote_image_public_id = result["public_id"]

        elif clear_quote_image:
            old_quote_public_id = content.quote_image_public_id

            content.quote_image_url = None
            content.quote_image_public_id = None

        db.commit()
        db.refresh(content)

    except Exception as e:
        db.rollback()

        # If Cloudinary upload succeeded but DB update failed,
        # remove the newly uploaded image.
        if uploaded_public_id:
            try:
                delete_image(uploaded_public_id)
            except Exception:
                pass

        raise HTTPException(
            status_code=500,
            detail=f"Content update failed: {str(e)}",
        )

    # Delete the old Cloudinary image only after
    # the database successfully points to the new state.
    if old_quote_public_id:
        try:
            delete_image(old_quote_public_id)
        except Exception:
            pass

    images = (
        db.query(DashboardImage)
        .filter(
            DashboardImage.app_content_id == content.id
        )
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


# ---------------------------------------------------------
# ADD DASHBOARD/CAROUSEL IMAGES
# ---------------------------------------------------------

@router.post(
    "/dashboard-images",
    response_model=list[DashboardImageResponse],
)
async def add_dashboard_images(
    dashboard_images: Annotated[list[UploadFile], File(...)],

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])
    ),
):
    if not dashboard_images:
        raise HTTPException(
            status_code=400,
            detail="At least one dashboard image is required",
        )

    for image in dashboard_images:
        if (
            not image.content_type
            or not image.content_type.startswith("image/")
        ):
            raise HTTPException(
                status_code=400,
                detail="All dashboard files must be images",
            )

    content = get_or_create_content(db)

    uploaded_public_ids = []
    new_images = []

    try:
        existing_count = (
            db.query(DashboardImage)
            .filter(
                DashboardImage.app_content_id == content.id
            )
            .count()
        )

        for index, image in enumerate(dashboard_images):
            result = upload_image(
                image,
                folder="bhaktipath/dashboard",
            )

            uploaded_public_ids.append(result["public_id"])

            new_images.append(
                DashboardImage(
                    app_content_id=content.id,
                    image_url=result["url"],
                    cloudinary_public_id=result["public_id"],
                    display_order=existing_count + index,
                )
            )

        db.add_all(new_images)
        db.commit()

        for image in new_images:
            db.refresh(image)

    except Exception as e:
        db.rollback()

        for public_id in uploaded_public_ids:
            try:
                delete_image(public_id)
            except Exception:
                pass

        raise HTTPException(
            status_code=500,
            detail=f"Dashboard image upload failed: {str(e)}",
        )

    return new_images


# ---------------------------------------------------------
# DELETE ONE DASHBOARD/CAROUSEL IMAGE
# ---------------------------------------------------------

@router.delete("/dashboard-images/{image_id}")
def delete_dashboard_image(
    image_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])
    ),
):
    image = (
        db.query(DashboardImage)
        .filter(DashboardImage.id == image_id)
        .first()
    )

    if not image:
        raise HTTPException(
            status_code=404,
            detail="Dashboard image not found",
        )

    public_id = image.cloudinary_public_id

    db.delete(image)
    db.commit()

    # Database deletion succeeded, so now remove the
    # corresponding Cloudinary asset.
    try:
        delete_image(public_id)
    except Exception:
        # The DB state is already correct. Cloudinary cleanup
        # failure should not make the API return a false failure.
        pass

    return {
        "message": "Dashboard image deleted"
    }