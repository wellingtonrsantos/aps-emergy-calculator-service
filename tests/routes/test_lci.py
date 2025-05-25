from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.core import auth
import requests

client = TestClient(app)


def override_get_current_user():
    return {"email": "test@example.com"}


app.dependency_overrides[auth.get_current_user] = override_get_current_user


def test_list_lci_products_success():
    fake_products = [
        {"id": 1, "name": "Produto A"},
        {"id": 2, "name": "Produto B"},
    ]
    with patch("app.service.lci_service.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = fake_products
        mock_get.return_value = mock_response

        response = client.get("/api/lci/products")
        assert response.status_code == 200
        assert response.json() == fake_products


def test_list_lci_products_http_error():
    with patch("app.service.lci_service.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            response=MagicMock(status_code=502, text="Erro HTTP")
        )
        mock_get.return_value = mock_response

        response = client.get("/api/lci/products")
        assert response.status_code == 502


def test_list_lci_products_request_exception():
    with patch(
        "app.service.lci_service.requests.get",
        side_effect=requests.RequestException("Connection error"),
    ):
        response = client.get("/api/lci/products")
        assert response.status_code == 502
        assert "Erro ao buscar produtos LCI" in response.text
