import pytest
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from lib.models import Base, User, SocialAccount, RefreshToken

@pytest.fixture(scope="module")
def engine():
    # Use an in-memory SQLite DB for testing
    return create_engine("sqlite:///:memory:")

@pytest.fixture(scope="module")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine, tables):
    # Create a new session for each test
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_create_user(db_session):
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email="test@example.com",
        hashed_password="hashed_secret",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # Fetch the user
    fetched = db_session.query(User).filter_by(email="test@example.com").first()
    assert fetched is not None
    assert fetched.id == user_id
    assert fetched.email == "test@example.com"
    assert fetched.hashed_password == "hashed_secret"
    assert fetched.is_active is True

def test_unique_email_constraint(db_session):
    # Attempt to create another user with the same email "test@example.com"
    user_id = str(uuid.uuid4())
    duplicate_user = User(
        id=user_id,
        email="test@example.com",  # same email as above
        hashed_password="other_hash",
        is_active=True
    )
    db_session.add(duplicate_user)
    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()

def test_add_social_account(db_session):
    # Create a new user
    user = User(
        id=str(uuid.uuid4()),
        email="social_user@example.com",
        hashed_password="another_hash",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # Add a social account
    social = SocialAccount(
        id=str(uuid.uuid4()),
        user_id=user.id,
        provider="google",
        external_id="google-12345"
    )
    db_session.add(social)
    db_session.commit()

    # Verify the link
    fetched_user = db_session.query(User).filter_by(email="social_user@example.com").first()
    assert len(fetched_user.social_accounts) == 1
    assert fetched_user.social_accounts[0].provider == "google"
    assert fetched_user.social_accounts[0].external_id == "google-12345"

def test_refresh_token(db_session):
    # Create a user for token association
    user = User(
        id=str(uuid.uuid4()),
        email="token_user@example.com",
        hashed_password="tok_hash",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # Create a refresh token
    token_str = "refresh_token_abc"
    refresh = RefreshToken(
        token=token_str,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        revoked=False
    )
    db_session.add(refresh)
    db_session.commit()

    fetched_token = db_session.query(RefreshToken).filter_by(token=token_str).first()
    assert fetched_token is not None
    assert fetched_token.user_id == user.id
    assert fetched_token.revoked is False
    assert fetched_token.expires_at > datetime.now(timezone.utc)
