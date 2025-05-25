from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.service.file.file_validator import validate_file_mime
from app.models.error_response import ErrorResponse
from app.exceptions.exceptions import BadRequestException, LCIServiceException
from app.core.logger import logger
from app.service.file.file_storage import temporary_upload_file
from app.core.auth import get_current_user
from app.service.emergy_service import EmergyService
from app.service.data_source import APIDataSource, FileDataSource
from app.service.lci_service import LCIService


router = APIRouter(
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/by-file",
    responses={
        400: {"description": "Arquivo inválido", "model": ErrorResponse},
    },
)
async def calculate_emergy_by_file(file: UploadFile = File(...)):
    logger.info(f"Validando tipo[{file.content_type}] do arquivo: {file.filename}")
    if not validate_file_mime(file):
        raise BadRequestException(
            "Tipo de arquivo não suportado. Use .csv, .xls ou .xlsx."
        )

    try:
        with temporary_upload_file(file) as path:
            calculator = EmergyService(FileDataSource(path))
            result = calculator.calculate()
            return {"filename": file.filename, **result}

    except BadRequestException:
        raise
    except Exception:
        logger.error(
            f"Erro ao calcular LCI pelo arquivo [{file.filename}] importado: ",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/by-lci/{product_id}")
async def calculate_emergy_by_lci(product_id: int):
    try:
        calculator = EmergyService(APIDataSource(product_id, LCIService()))
        result = calculator.calculate()
        return {"product_id: ": product_id, **result}

    except BadRequestException or LCIServiceException:
        raise
    except Exception:
        logger.error("Erro ao calcular LCI pela base externa: ", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
