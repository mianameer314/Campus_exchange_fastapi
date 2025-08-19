from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean
from typing import List
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    university: Mapped[str] = mapped_column(String(255), nullable=True)

    listings: Mapped[List["Listing"]] = relationship("Listing", back_populates="owner")
    favorites: Mapped[List["Favorite"]] = relationship("Favorite", back_populates="user")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user")

    # ✅ Add this:
    verifications = relationship("Verification", back_populates="user")