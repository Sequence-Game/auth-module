import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from lib.services.auth_service import (
    register_user, authenticate_user, issue_tokens, refresh_access_token,
    logout, link_or_create_user_via_social, link_social_account, find_user_by_email
)
from lib.models import User, SocialAccount, RefreshToken
from lib.services.token_service import decode_token, create_access_token

# Mocking settings
@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    monkeypatch.setattr('lib.services.auth_service.settings', MagicMock())

# Mocking hashing_service
@pytest.fixture(autouse=True)
def mock_hashing_service(monkeypatch):
    monkeypatch.setattr('lib.services.auth_service.hash_password', MagicMock())
    monkeypatch.setattr('lib.services.auth_service.verify_password', MagicMock())

# Mocking token_service
@pytest.fixture(autouse=True)
def mock_token_service(monkeypatch):
    monkeypatch.setattr('lib.services.auth_service.create_access_token', MagicMock())
    monkeypatch.setattr('lib.services.auth_service.create_refresh_token', MagicMock())
    monkeypatch.setattr('lib.services.auth_service.decode_token', MagicMock())

# Mocking uuid
@pytest.fixture(autouse=True)
def mock_uuid(monkeypatch):
    monkeypatch.setattr('lib.services.auth_service.uuid', MagicMock())

@pytest.fixture
def db_session():
    # Mock the Session object
    return MagicMock(spec=Session)

# Tests for register_user
@patch('lib.services.auth_service.find_user_by_email')
def test_register_user_new(mock_find_user_by_email, db_session):
    mock_find_user_by_email.return_value = None
    user_id = register_user(db_session, "newuser@example.com", "mypassword")
    assert user_id is not None
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()

@patch('lib.services.auth_service.find_user_by_email')
def test_register_user_exists(mock_find_user_by_email, db_session):
    mock_find_user_by_email.return_value = User(id="123", email="existing@example.com", hashed_password="xxx", is_active=True)
    with pytest.raises(ValueError, match="User with this email already exists"):
        register_user(db_session, "existing@example.com", "new_password")

# Tests for link_social_account
def test_link_social_account_new(db_session):
    user_id = "test_user_id"
    provider = "test_provider"
    external_id = "test_external_id"
    link_social_account(db_session, user_id, provider, external_id)
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()

def test_link_social_account_existing_same_user(db_session):
    user_id = "test_user_id"
    provider = "test_provider"
    external_id = "test_external_id"
    db_session.query.return_value.filter.return_value.first.return_value = SocialAccount(
        user_id=user_id,
        provider=provider,
        external_id=external_id,
    )
    with pytest.raises(ValueError, match="This social account is already linked to your profile"):
        link_social_account(db_session, user_id, provider, external_id)

def test_link_social_account_existing_different_user(db_session):
    user_id = "test_user_id"
    provider = "test_provider"
    external_id = "test_external_id"
    db_session.query.return_value.filter.return_value.first.return_value = SocialAccount(
        user_id="another_user_id",
        provider=provider,
        external_id=external_id,
    )
    with pytest.raises(ValueError, match="This social account is linked to a different user"):
        link_social_account(db_session, user_id, provider, external_id)

# Tests for find_user_by_email
def test_find_user_by_email_found(db_session):
    email = "test@example.com"
    db_session.query.return_value.filter.return_value.first.return_value = User(
        id="test_user_id",
        email=email,
    )
    user = find_user_by_email(db_session, email)
    assert user is not None
    assert user.email == email

def test_find_user_by_email_not_found(db_session):
    email = "test@example.com"
    db_session.query.return_value.filter.return_value.first.return_value = None
    user = find_user_by_email(db_session, email)
    assert user is None

# Tests for authenticate_user
def test_authenticate_user_valid_credentials(db_session, mock_hashing_service):
    email = "test@example.com"
    password = "test_password"
    db_session.query.return_value.filter.return_value.first.return_value = User(
        id="test_user_id",
        email=email,
        hashed_password="hashed_password",
    )
    mock_hashing_service.verify_password.return_value = True
    user_id = authenticate_user(db_session, email, password)
    assert user_id == "test_user_id"

def test_authenticate_user_invalid_credentials(db_session, mock_hashing_service):
    email = "test@example.com"
    password = "test_password"
    db_session.query.return_value.filter.return_value.first.return_value = User(
        id="test_user_id",
        email=email,
        hashed_password="hashed_password",
    )
    mock_hashing_service.verify_password.return_value = False
    user_id = authenticate_user(db_session, email, password)
    assert user_id is None

def test_authenticate_user_user_not_found(db_session, mock_hashing_service):
    email = "test@example.com"
    password = "test_password"
    db_session.query.return_value.filter.return_value.first.return_value = None
    user_id = authenticate_user(db_session, email, password)
    assert user_id is None

# Tests for issue_tokens
def test_issue_tokens(db_session, mock_token_service, mock_settings):
    user_id = "test_user_id"
    mock_token_service.create_access_token.return_value = "access_token"
    mock_token_service.create_refresh_token.return_value = "refresh_token"
    access, refresh = issue_tokens(db_session, user_id)
    assert access == "access_token"
    assert refresh == "refresh_token"
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()

# Tests for refresh_access_token
def test_refresh_access_token_valid_refresh_token(db_session, mock_token_service, mock_settings):
    refresh_token_str = "refresh_token"
    mock_token_service.decode_token.return_value = {
        "type": "refresh",
        "sub": "test_user_id",
        "exp": datetime.now(timezone.utc) + timedelta(days=30),
    }
    db_session.query.return_value.filter.return_value.first.return_value = RefreshToken(
        token=refresh_token_str,
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        revoked=False,
    )
    access = refresh_access_token(db_session, refresh_token_str)
    assert access == mock_token_service.create_access_token.return_value

def test_refresh_access_token_invalid_refresh_token(db_session, mock_token_service):
    refresh_token_str = "refresh_token"
    mock_token_service.decode_token.return_value = {
        "type": "access",
        "sub": "test_user_id",
        "exp": datetime.now(timezone.utc) + timedelta(days=30),
    }
    with pytest.raises(ValueError, match="Invalid token type"):
        refresh_access_token(db_session, refresh_token_str)

def test_refresh_access_token_expired_refresh_token(db_session, mock_token_service, mock_settings):
    refresh_token_str = "refresh_token"
    mock_token_service.decode_token.return_value = {
        "type": "refresh",
        "sub": "test_user_id",
        "exp": datetime.now(timezone.utc) + timedelta(days=30),
    }
    db_session.query.return_value.filter.return_value.first.return_value = RefreshToken(
        token=refresh_token_str,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        revoked=False,
    )
    with pytest.raises(ValueError, match="Token expired or revoked"):
        refresh_access_token(db_session, refresh_token_str)

def test_refresh_access_token_revoked_refresh_token(db_session, mock_token_service, mock_settings):
    refresh_token_str = "refresh_token"
    mock_token_service.decode_token.return_value = {
        "type": "refresh",
        "sub": "test_user_id",
        "exp": datetime.now(timezone.utc) + timedelta(days=30),
    }
    db_session.query.return_value.filter.return_value.first.return_value = RefreshToken(
        token=refresh_token_str,
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        revoked=True,
    )
    with pytest.raises(ValueError, match="Token expired or revoked"):
        refresh_access_token(db_session, refresh_token_str)

# Tests for logout
def test_logout(db_session):
    refresh_token_str = "refresh_token"
    db_session.query.return_value.filter.return_value.first.return_value = RefreshToken(
        token=refresh_token_str,
    )
    logout(db_session, refresh_token_str)
    db_session.commit.assert_called_once()

# Tests for link_or_create_user_via_social
def test_link_or_create_user_via_social_new_user(db_session, mock_hashing_service):
    provider = "test_provider"
    external_id = "test_external_id"
    email = "test@example.com"
    db_session.query.return_value.filter.return_value.first.return_value = None
    mock_hashing_service.hash_password.return_value = "hashed_password"
    user_id = link_or_create_user_via_social(db_session, provider, external_id, email)
    assert user_id is not None
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()

def test_link_or_create_user_via_social_existing_user_no_link(db_session):
    provider = "test_provider"
    external_id = "test_external_id"
    email = "test@example.com"
    db_session.query.return_value.filter.return_value.first.return_value = User(
        id="test_user_id",
        email=email,
    )
    user_id = link_or_create_user_via_social(db_session, provider, external_id, email)
    assert user_id == "test_user_id"
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()

def test_link_or_create_user_via_social_existing_user_with_link(db_session):
    provider = "test_provider"
    external_id = "test_external_id"
    email = "test@example.com"
    db_session.query.return_value.filter.return_value.first.side_effect = [
        User(id="test_user_id", email=email),
        SocialAccount(user_id="test_user_id", provider=provider),
    ]
    with pytest.raises(ValueError, match="User already exists with this social provider"):
        link_or_create_user_via_social(db_session, provider, external_id, email)