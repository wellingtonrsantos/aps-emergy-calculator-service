import pytest
from unittest.mock import patch, MagicMock
from datetime import timedelta
from jose import jwt
from app.core import auth
from app.exceptions.exceptions import UnauthorizedException


def test_create_access_token_generates_valid_jwt():
    data = {"sub": "test@example.com"}
    token = auth.create_access_token(data)
    decoded = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    assert decoded["sub"] == "test@example.com"
    assert "exp" in decoded


def test_create_access_token_with_custom_expiry():
    data = {"sub": "test@example.com"}
    token = auth.create_access_token(data, expires_delta=timedelta(minutes=1))
    decoded = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    assert decoded["sub"] == "test@example.com"
    assert "exp" in decoded


def test_authenticate_user_success():
    mock_session = MagicMock()
    mock_user = MagicMock()
    mock_user.hashed_password = "hashed"
    with (
        patch("app.core.auth.UserService") as mock_user_service_class,
        patch("app.core.auth.verify_password", return_value=True),
    ):
        mock_user_service = mock_user_service_class.return_value
        mock_user_service.get_user_by_email.return_value = mock_user

        user = auth.authenticate_user(mock_session, "test@example.com", "password")
        assert user == mock_user


def test_authenticate_user_invalid_password():
    mock_session = MagicMock()
    mock_user = MagicMock()
    mock_user.hashed_password = "hashed"
    with (
        patch("app.core.auth.UserService") as mock_user_service_class,
        patch("app.core.auth.verify_password", return_value=False),
    ):
        mock_user_service = mock_user_service_class.return_value
        mock_user_service.get_user_by_email.return_value = mock_user

        user = auth.authenticate_user(mock_session, "test@example.com", "wrongpass")
        assert user is None


def test_authenticate_user_not_found():
    mock_session = MagicMock()
    with patch("app.core.auth.UserService") as mock_user_service_class:
        mock_user_service = mock_user_service_class.return_value
        mock_user_service.get_user_by_email.return_value = None

        user = auth.authenticate_user(mock_session, "notfound@example.com", "password")
        assert user is None


def test_get_current_user_valid_token():
    email = "test@example.com"
    token = auth.create_access_token({"sub": email})
    # Simula o Depends do FastAPI passando o token diretamente
    result = auth.get_current_user(token)
    assert result == email


def test_get_current_user_invalid_token():
    with pytest.raises(UnauthorizedException):
        auth.get_current_user("invalid.token.here")


def test_get_current_user_missing_sub():
    # Gera token sem campo 'sub'
    token = jwt.encode({"foo": "bar"}, auth.SECRET_KEY, algorithm=auth.ALGORITHM)
    with pytest.raises(UnauthorizedException):
        auth.get_current_user(token)
