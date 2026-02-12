from __future__ import annotations
from sqlalchemy import String, Boolean, DateTime, Enum as PG_ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from datetime import datetime
from typing import TYPE_CHECKING
from app.model.basemodel import BaseModel

if TYPE_CHECKING:
    from app.model.refresh_token import RefreshToken
    from app.model.dataset import Dataset
class OTPType(Enum):
    EMAIL_VERIFICATION = "email_verification"

class User(BaseModel):
    __tablename__ = "users"
    
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, init=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, init=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, init=False)
    
    otp: Mapped[str | None ] = mapped_column(String, nullable=True)
    otp_type: Mapped[OTPType | None] = mapped_column(PG_ENUM(OTPType, name="otp_type_enum"), nullable=True)
    otp_expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin", init=False
    )
    
    datasets: Mapped[list["Dataset"]] = relationship(
        "Dataset", back_populates="user", lazy="selectin", cascade="all, delete-orphan", init=False
    )