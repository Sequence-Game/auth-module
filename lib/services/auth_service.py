import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from lib.config import settings
from lib.models import User, RefreshToken, SocialAccount
from lib.services.hashing_service import hash_password, verify_password
from lib.services.token_service import create_access_token, create_refresh_token, decode_token

def register_user(db: Session, email: str, password: str):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        # User already exists with email/password method
        raise ValueError("User with this email already exists")
    
    # Create new user
    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        email=email,
        hashed_password=hash_password(password),
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.id

def link_social_account(db: Session, user_id: str, provider: str, external_id: str):
    # Check if already linked with this provider/external_id
    existing_social = db.query(SocialAccount).filter(
        SocialAccount.provider == provider,
        SocialAccount.external_id == external_id
    ).first()
    if existing_social:
        # Already linked
        if existing_social.user_id == user_id:
            # The user is trying to link the same social account again
            raise ValueError("This social account is already linked to your profile")
        else:
            # Another user owns this social account
            raise ValueError("This social account is linked to a different user")

    # If no existing link, create new link
    new_link = SocialAccount(
        id=str(uuid.uuid4()),
        user_id=user_id,
        provider=provider,
        external_id=external_id
    )
    db.add(new_link)
    db.commit()
    return new_link

def find_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> str:
    user = find_user_by_email(db, email)
    if user and verify_password(password, user.hashed_password):
        return user.id
    return None

def issue_tokens(db: Session, user_id: str):
    access = create_access_token(user_id)
    refresh = create_refresh_token(user_id)

    # Store refresh token
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = RefreshToken(
        token=refresh,
        user_id=user_id,
        expires_at=expires_at,
        revoked=False
    )
    db.add(db_token)
    db.commit()
    return access, refresh

def refresh_access_token(db: Session, refresh_token_str: str):
    payload = decode_token(refresh_token_str)
    if payload.get("type") != "refresh":
        raise ValueError("Invalid token type")

    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token_str,
        RefreshToken.revoked == False
    ).first()

    if not db_token or db_token.expires_at < datetime.now(timezone.utc):
        raise ValueError("Token expired or revoked")

    user_id = payload.get("sub")
    return create_access_token(user_id)

def logout(db: Session, refresh_token_str: str):
    db_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token_str).first()
    if db_token:
        db_token.revoked = True
        db.commit()

def link_or_create_user_via_social(db: Session, provider: str, external_id: str, email: str):
    # Check if a user already has this email
    user = find_user_by_email(db, email)
    if user:
        # User exists, try to link social if not already linked
        # Check if this provider is already linked
        existing_link = db.query(SocialAccount).filter(
            SocialAccount.user_id == user.id,
            SocialAccount.provider == provider
        ).first()
        if existing_link:
            # user already linked this provider
            raise ValueError("User already exists with this social provider")
        else:
            # link new social account to existing user
            link_social_account(db, user.id, provider, external_id)
            return user.id
    else:
        # No user with this email, create a new user with a dummy password
        user_id = str(uuid.uuid4())
        new_user = User(
            id=user_id,
            email=email,
            hashed_password=hash_password(uuid.uuid4().hex),  # dummy password
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        # Link social account
        link_social_account(db, user_id, provider, external_id)
        return new_user.id
