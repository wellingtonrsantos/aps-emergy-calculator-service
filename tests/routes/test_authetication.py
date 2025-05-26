import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.exceptions.exceptions import BadRequestException


client = TestClient(app)


@pytest.fixture
def register_payload():
    return {
        "email": "test@example.com",
        "password": "strongpassword",
        "name": "Test",
        "surname": "User",
        "mobile_number": "11999999999",
    }


@pytest.fixture
def login_payload():
    return {"email": "test@example.com", "password": "strongpassword"}


def test_register_user_success(register_payload):
    with patch("app.routes.authetication.UserService") as mock_user_service_class:
        mock_user_service = mock_user_service_class.return_value
        mock_user = MagicMock()
        mock_user.id = 123
        mock_user_service.create_user.return_value = mock_user

        response = client.post("/api/auth/register", json=register_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Usuário registrado com sucesso"
        assert data["user_id"] == 123


def test_register_user_email_exists(register_payload):
    with patch("app.routes.authetication.UserService") as mock_user_service_class:
        mock_user_service = mock_user_service_class.return_value
        mock_user_service.create_user.side_effect = BadRequestException(
            "Email já está em uso"
        )

        response = client.post("/api/auth/register", json=register_payload)
        assert response.status_code == 400
        assert "Email já está em uso" in response.text


def test_login_success(login_payload):
    with (
        patch("app.routes.authetication.authenticate_user") as mock_auth_user,
        patch("app.routes.authetication.create_access_token", return_value="token123"),
    ):
        mock_user = MagicMock()
        mock_user.email = login_payload["email"]
        mock_auth_user.return_value = mock_user

        response = client.post("/api/auth/login", json=login_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "token123"
        assert data["token_type"] == "bearer"


def test_login_invalid_credentials(login_payload):
    with patch("app.routes.authetication.authenticate_user", return_value=None):
        response = client.post("/api/auth/login", json=login_payload)
        assert response.status_code == 401
        assert "Credenciais inválidas" in response.text


def test_get_current_user_success():
    mock_token = MagicMock()
    mock_token.credentials = "valid_token"
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.email = "test@example.com"
    mock_user.name = "Test"
    mock_user.surname = "User"
    mock_user.mobile_number = "11999999999"

    with (
        patch(
            "app.routes.authetication.decode_access_token",
            return_value="test@example.com",
        ),
        patch("app.routes.authetication.UserService") as mock_user_service_class,
    ):
        mock_user_service = mock_user_service_class.return_value
        mock_user_service.get_user_by_email.return_value = mock_user

        response = client.get(
            "/api/auth/me", headers={"Authorization": "Bearer valid_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test"
        assert data["surname"] == "User"
        assert data["mobile_number"] == "11999999999"


def test_get_current_user_invalid_token():
    mock_token = MagicMock()
    mock_token.credentials = "invalid_token"

    with patch("app.routes.authetication.decode_access_token", return_value=None):
        response = client.get(
            "/api/auth/me", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401
        assert "Could not validate credentials" in response.text


def test_get_current_user_not_found():
    mock_token = MagicMock()
    mock_token.credentials = "valid_token"

    with (
        patch(
            "app.routes.authetication.decode_access_token",
            return_value="test@example.com",
        ),
        patch("app.routes.authetication.UserService") as mock_user_service_class,
    ):
        mock_user_service = mock_user_service_class.return_value
        mock_user_service.get_user_by_email.return_value = None

        response = client.get(
            "/api/auth/me", headers={"Authorization": "Bearer valid_token"}
        )

        assert response.status_code == 401
        assert "Could not validate credentials" in response.text
