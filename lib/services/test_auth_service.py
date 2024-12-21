import os
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from lib.services.auth_service import (
    register_user, authenticate_user, issue_tokens, refresh_access_token,
    logout, link_or_create_user_via_social, link_social_account, find_user_by_email
)
from lib.models import User, SocialAccount, RefreshToken

@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    monkeypatch.setenv("SOCIAL_GOOGLE_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("SOCIAL_GOOGLE_CLIENT_SECRET", "test_client_secret")

@pytest.fixture
def db_session():
    # Mock the Session object
    return MagicMock(spec=Session)

def test_register_user_new(db_session):
    # User does not exist
    db_session.query.return_value.filter.return_value.first.return_value = None

    user_id = register_user(db_session, "newuser@example.com", "mypassword")
    assert user_id is not None
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()

def test_register_user_exists(db_session):
    existing_user = User(id="123", email="exists@example.com", hashed_password="hashed", is_active=True)
    db_session.query.return_value.filter.return_value.first.return_value = existing_user

    with pytest.raises(ValueError) as exc:
        register_user(db_session, "exists@example.com", "secret")
    assert "already exists" in str(exc.value)

def test_authenticate_user_success(db_session):
    # Mock user
    existing_user = User(id="u1", email="valid@example.com", hashed_password="hashed_pw", is_active=True)
    db_session.query.return_value.filter.return_value.first.return_value = existing_user

    with patch("auth_module.services.auth_service.verify_password", return_value=True):
        user_id = authenticate_user(db_session, "valid@example.com", "secret")
    assert user_id == "u1"

def test_authenticate_user_failure(db_session):
    # No user found
    db_session.query.return_value.filter.return_value.first.return_value = None
    user_id = authenticate_user(db_session, "nope@example.com", "secret")
    assert user_id is None

def test_issue_tokens(db_session):
    db_session.commit.return_value = None
    user_id = "u123"
    access, refresh = issue_tokens(db_session, user_id)
    assert access is not None
    assert refresh is not None
    # Ensure refresh token saved
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()

def test_refresh_access_token_valid(db_session):
    # Mock a valid refresh token
    token_str = "refresh_token"
    payload = {"sub": "user_id", "exp": (datetime.now(timezone.utc) + timedelta(days=1)).timestamp(), "type": "refresh"}

    with patch("auth_module.services.auth_service.decode_token", return_value=payload):
        db_session.query.return_value.filter.return_value.first.return_value = RefreshToken(
            token=token_str,
            user_id="user_id",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            revoked=False
        )
        new_access = refresh_access_token(db_session, token_str)
    assert new_access is not None

def test_refresh_access_token_invalid_type(db_session):
    token_str = "refresh_token"
    # Not a refresh token (type missing or invalid)
    payload = {"sub": "user_id", "exp": (datetime.now(timezone.utc) + timedelta(days=1)).timestamp()}

    with patch("auth_module.services.auth_service.decode_token", return_value=payload):
        with pytest.raises(ValueError) as exc:
            refresh_access_token(db_session, token_str)
    assert "Invalid token type" in str(exc.value)

def test_refresh_access_token_expired(db_session):
    token_str = "refresh_token"
    payload = {"sub": "user_id", "exp": (datetime.now(timezone.utc) - timedelta(days=1)).timestamp(), "type": "refresh"}

    with patch("auth_module.services.auth_service.decode_token", return_value=payload):
        with pytest.raises(ValueError) as exc:
            refresh_access_token(db_session, token_str)
    assert "expired or revoked" in str(exc.value)

def test_logout(db_session):
    token_str = "refresh_token"
    # Existing token
    mock_token = RefreshToken(token=token_str, user_id="user_id", expires_at=datetime.now(timezone.utc), revoked=False)
    db_session.query.return_value.filter.return_value.first.return_value = mock_token

    logout(db_session, token_str)
    assert mock_token.revoked is True
    db_session.commit.assert_called_once()

def test_find_user_by_email(db_session):
    user = User(id="u1", email="test@example.com", hashed_password="x", is_active=True)
    db_session.query.return_value.filter.return_value.first.return_value = user

    fetched = find_user_by_email(db_session, "test@example.com")
    assert fetched == user

def test_link_social_account_new_link(db_session):
    user_id = "u1"
    provider = "google"
    external_id = "google-123"
    # No existing link
    db_session.query.return_value.filter.return_value.first.return_value = None

    link_social_account(db_session, user_id, provider, external_id)
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()

def test_link_social_account_already_linked(db_session):
    user_id = "u1"
    provider = "google"
    external_id = "google-123"
    existing_link = SocialAccount(id="s1", user_id="u1", provider="google", external_id="google-123")
    db_session.query.return_value.filter.return_value.first.return_value = existing_link

    with pytest.raises(ValueError) as exc:
        link_social_account(db_session, user_id, provider, external_id)
    assert "already linked" in str(exc.value)

def test_link_or_create_user_via_social_new_user(db_session):
    provider = "google"
    external_id = "google-abc"
    email = "new_social@example.com"
    # No user with this email
    db_session.query.return_value.filter.return_value.first.side_effect = [None, None]
    # The first filter checks for user by email, second might check for external_id

    user_id = link_or_create_user_via_social(db_session, provider, external_id, email)
    assert user_id is not None
    # Check that user and social account were added
    assert db_session.add.call_count == 2
    db_session.commit.assert_called()

def test_link_or_create_user_via_social_existing_user_new_provider(db_session):
    provider = "google"
    external_id = "google-xyz"
    email = "exists@example.com"
    existing_user = User(id="u9", email=email, hashed_password="x", is_active=True)
    # First .first() for user by email, second .first() for social link
    db_session.query.return_value.filter.return_value.first.side_effect = [existing_user, None]

    user_id = link_or_create_user_via_social(db_session, provider, external_id, email)
    assert user_id == "u9"
    # Should have added a new social account
    db_session.add.assert_called()
    db_session.commit.assert_called()

def test_link_or_create_user_via_social_existing_user_same_provider(db_session):
    provider = "google"
    external_id = "google-xyz"
    email = "exists@example.com"
    existing_user = User(id="u9", email=email, hashed_password="x", is_active=True)
    existing_social = SocialAccount(id="s2", user_id="u9", provider="google", external_id="google-xyz")

    # user by email
    # social account by user and provider
    db_session.query.return_value.filter.return_value.first.side_effect = [existing_user, existing_social]

    with pytest.raises(ValueError) as exc:
        link_or_create_user_via_social(db_session, provider, external_id, email)
    assert "already exists with this social provider" in str(exc.value)
