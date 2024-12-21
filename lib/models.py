from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)  # user UUID
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    social_accounts = relationship("SocialAccount", back_populates="user")

class SocialAccount(Base):
    __tablename__ = "social_accounts"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  # "google", "facebook", etc.
    external_id = Column(String, nullable=False, unique=True)

    user = relationship("User", back_populates="social_accounts")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    token = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
