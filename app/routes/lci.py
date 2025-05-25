from fastapi import APIRouter, Depends
from app.models.lci_models import LCIProduct
from app.service.lci_service import LCIService
from app.core.auth import get_current_user
from app.exceptions.exceptions import LCIServiceException

router = APIRouter(
    dependencies=[Depends(get_current_user)],
)


lci_service = LCIService()


@router.get("/products", response_model=list[LCIProduct])
async def list_lci_products():
    try:
        return lci_service.list_products()
    except LCIServiceException:
        raise
