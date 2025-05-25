import pytest
from io import BytesIO
from app.service.file.file_validator import validate_file_mime


class MockUploadFile:
    """Classe mock para simular o comportamento do UploadFile do FastAPI."""

    def __init__(self, filename, content, content_type):
        self.filename = filename
        self.file = BytesIO(content)
        self.content_type = content_type


@pytest.fixture
def mock_csv_file():
    file_content = b"name,age\nJohn,30\nDoe,25"
    return MockUploadFile("test_file.csv", file_content, "text/csv")


@pytest.fixture
def mock_excel_file():
    file_content = b"This is a mock Excel file."
    return MockUploadFile(
        "test_file.xlsx",
        file_content,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@pytest.fixture
def mock_invalid_file():
    file_content = b"This is a text file."
    return MockUploadFile("test_file.txt", file_content, "text/plain")


def test_validate_file_mime_csv(mock_csv_file):
    assert validate_file_mime(mock_csv_file) is True, "CSV file should be valid."


def test_validate_file_mime_excel(mock_excel_file):
    assert validate_file_mime(mock_excel_file) is True, "Excel file should be valid."


def test_validate_file_mime_invalid(mock_invalid_file):
    assert validate_file_mime(mock_invalid_file) is False, (
        "Invalid file should not be valid."
    )
