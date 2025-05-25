import pytest
from fastapi import UploadFile
from app.service.file.file_storage import save_temp_file, temporary_upload_file


@pytest.fixture
def mock_upload_file(tmp_path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("This is a test file.")
    with file_path.open("rb") as file:
        yield UploadFile(filename="test_file.txt", file=file)


def test_save_temp_file(mock_upload_file):
    temp_path = save_temp_file(mock_upload_file)
    assert temp_path.exists(), "Temporary file should exist."
    assert temp_path.suffix == ".txt", "File extension should match the original file."
    temp_path.unlink()


def test_temporary_upload_file(mock_upload_file):
    with temporary_upload_file(mock_upload_file) as temp_path:
        assert temp_path.exists(), "Temporary file should exist within the context."
    assert not temp_path.exists(), "Temporary file should be deleted after the context."
