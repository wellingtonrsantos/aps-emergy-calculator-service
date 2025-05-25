import uuid
from pathlib import Path
from fastapi import UploadFile
import shutil
from app.core.logger import logger
from contextlib import contextmanager

UPLOAD_DIR = Path("tmp/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_temp_file(file: UploadFile) -> Path:
    file_extension = file.filename.split(".")[-1].lower()
    unique_name = f"{uuid.uuid4()}.{file_extension}"
    temp_path = UPLOAD_DIR / unique_name

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    logger.info(f"Arquivo[{file.filename}] temporário salvo em: {temp_path}")
    return temp_path


@contextmanager
def temporary_upload_file(file: UploadFile):
    path = save_temp_file(file)
    try:
        yield path
    finally:
        if path.exists():
            path.unlink()
            logger.info(f"Arquivo temporário removido: {path}")
        else:
            logger.warning(f"Tentativa de remover arquivo que não existe: {path}")
