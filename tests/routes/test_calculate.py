import io
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.core import auth

client = TestClient(app)


def override_get_current_user():
    return {"email": "test@example.com"}


app.dependency_overrides[auth.get_current_user] = override_get_current_user


@pytest.fixture
def csv_file():
    return ("test.csv", io.BytesIO(b"col1,col2\n1,2\n3,4"), "text/csv")


@pytest.fixture
def fake_result():
    return {
        "emergy": {
            "F": {"value": "1.05E+04", "unit": "sej"},
            "R": {"value": "8.43E+07", "unit": "sej"},
            "Total": {"value": "8.43E+07", "unit": "sej"},
        },
        "sustainability": {
            "EYR": 8029.57,
            "ELR": 0,
            "ESI": 64465987.76,
            "classification": "Altamente Sustentável",
        },
    }


def test_calculate_emergy_by_file_success(csv_file, fake_result):
    with (
        patch("app.routes.calculate.validate_file_mime", return_value=True),
        patch("app.routes.calculate.temporary_upload_file") as mock_temp_file,
        patch("app.routes.calculate.EmergyService") as mock_emergy_service,
    ):
        mock_temp_file.return_value.__enter__.return_value = "fake_path"
        mock_emergy = MagicMock()
        mock_emergy.calculate.return_value = fake_result
        mock_emergy_service.return_value = mock_emergy

        response = client.post("/api/calculate/by-file", files={"file": csv_file})
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.csv"
        assert data["emergy"] == fake_result["emergy"]
        assert data["sustainability"] == fake_result["sustainability"]


def test_calculate_emergy_by_file_invalid_type(csv_file):
    with patch("app.routes.calculate.validate_file_mime", return_value=False):
        response = client.post("/api/calculate/by-file", files={"file": csv_file})
        assert response.status_code == 400
        assert "Tipo de arquivo não suportado" in response.text


def test_calculate_emergy_by_file_internal_error(csv_file):
    with (
        patch("app.routes.calculate.validate_file_mime", return_value=True),
        patch("app.routes.calculate.temporary_upload_file") as mock_temp_file,
        patch("app.routes.calculate.EmergyService") as mock_emergy_service,
    ):
        mock_temp_file.return_value.__enter__.return_value = "fake_path"
        mock_emergy_service.side_effect = Exception("Unexpected error")

        response = client.post("/api/calculate/by-file", files={"file": csv_file})
        assert response.status_code == 500
        assert "Internal Server Error" in response.text


def test_calculate_emergy_by_lci_success(fake_result):
    with patch("app.routes.calculate.EmergyService") as mock_emergy_service:
        mock_emergy = MagicMock()
        mock_emergy.calculate.return_value = fake_result
        mock_emergy_service.return_value = mock_emergy

        response = client.get("/api/calculate/by-lci/1")
        assert response.status_code == 200
        data = response.json()
        assert data["product_id: "] == 1
        assert data["emergy"] == fake_result["emergy"]
        assert data["sustainability"] == fake_result["sustainability"]


def test_calculate_emergy_by_lci_internal_error():
    with patch("app.routes.calculate.EmergyService") as mock_emergy_service:
        mock_emergy_service.side_effect = Exception("Unexpected error")

        response = client.get("/api/calculate/by-lci/1")
        assert response.status_code == 500
        assert "Internal Server Error" in response.text
