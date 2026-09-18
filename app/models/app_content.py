from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class AppContent(Base):
    __tablename__ = "app_content"

    id = Column(Integer, primary_key=True, index=True)

    home_title = Column(String(255), nullable=True)
    home_subtitle = Column(String(255), nullable=True)
    home_content = Column(Text, nullable=True)

    quote = Column(Text, nullable=True)
    quote_image_url = Column(String(1000), nullable=True)
    quote_image_public_id = Column(String(500), nullable=True)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    dashboard_images = relationship(
        "DashboardImage",
        back_populates="app_content",
        cascade="all, delete-orphan",
    )