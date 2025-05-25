import pytest
from unittest.mock import patch, MagicMock
from app.service.user_service import UserService
from app.exceptions.exceptions import BadRequestException
from app.models.authentication import RegisterRequest


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def register_request():
    return RegisterRequest(
        name="Test",
        surname="User",
        email="test@example.com",
        password="strongpassword",
        mobile_number="11999999999",
    )


def test_get_user_by_email_found(mock_session):
    fake_user = MagicMock()
    with patch(
        "app.service.user_service.get_user_by_email", return_value=fake_user
    ) as mock_get:
        service = UserService(mock_session)
        user = service.get_user_by_email("test@example.com")
        mock_get.assert_called_once_with(mock_session, "test@example.com")
        assert user == fake_user


def test_get_user_by_email_not_found(mock_session):
    with patch(
        "app.service.user_service.get_user_by_email", return_value=None
    ) as mock_get:
        service = UserService(mock_session)
        user = service.get_user_by_email("notfound@example.com")
        mock_get.assert_called_once_with(mock_session, "notfound@example.com")
        assert user is None


def test_create_user_success(mock_session, register_request):
    with (
        patch("app.service.user_service.get_user_by_email", return_value=None),
        patch(
            "app.service.user_service.create_user", return_value="fake_user"
        ) as mock_create,
    ):
        service = UserService(mock_session)
        user = service.create_user(register_request)
        mock_create.assert_called_once_with(mock_session, register_request)
        assert user == "fake_user"


def test_create_user_email_exists(mock_session, register_request):
    with patch(
        "app.service.user_service.get_user_by_email", return_value="existing_user"
    ):
        service = UserService(mock_session)
        with pytest.raises(BadRequestException) as exc:
            service.create_user(register_request)
        assert "Email já está em uso" in str(exc.value)
