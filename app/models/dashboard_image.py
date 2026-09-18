from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class DashboardImage(Base):
    __tablename__ = "dashboard_images"

    id = Column(Integer, primary_key=True, index=True)

    app_content_id = Column(
        Integer,
        ForeignKey("app_content.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    image_url = Column(String(1000), nullable=False)

    cloudinary_public_id = Column(
        String(500),
        nullable=False,
    )

    display_order = Column(Integer, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    app_content = relationship(
        "AppContent",
        back_populates="dashboard_images",
    )