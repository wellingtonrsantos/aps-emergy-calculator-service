from typing import List
import requests
from app.models.lci_models import LCIProduct, LCIFlow
from app.core.logger import logger
from app.core.config import Settings
from functools import lru_cache
from app.exceptions.exceptions import LCIServiceException


@lru_cache
def get_settings():
    return Settings()


class LCIService:
    def __init__(self):
        self.api_url = get_settings().lci_service_api_url

    def list_products(self) -> List[LCIProduct]:
        try:
            response = requests.get(f"{self.api_url}/products")
            response.raise_for_status()
            products = response.json()
            return [LCIProduct(**item) for item in products]
        except requests.HTTPError as e:
            logger.error("Erro na chamada a API externa: ", exc_info=True)
            detail = (
                e.response.text if e.response else "Erro desconhecido na API externa."
            )
            raise LCIServiceException(
                detail, status_code=e.response.status_code if e.response else 502
            )
        except requests.RequestException:
            logger.error(
                "Erro ao buscar produtos LCI no serviço externo: ", exc_info=True
            )
            raise LCIServiceException("Erro ao buscar produtos LCI no serviço externo.")

    def get_flows_by_product_id(self, product_id: int) -> List[LCIFlow]:
        try:
            response = requests.get(f"{self.api_url}/products/{product_id}")
            response.raise_for_status()
            flows = response.json()
            return [
                LCIFlow(
                    **{
                        "flow_name": f["Flow Name"],
                        "amount": f["Amount"],
                        "unit": f["Unit"],
                        "flow_direction": f["Flow Direction"],
                        "uev": f["UEV"],
                        "category": f["Category"],
                    }
                )
                for f in flows
            ]
        except requests.HTTPError as e:
            logger.error("Erro ao buscar flows do produto LCI: ", exc_info=True)
            detail = (
                e.response.text if e.response else "Erro desconhecido na API externa."
            )
            raise LCIServiceException(
                detail, status_code=e.response.status_code if e.response else 502
            )
        except requests.RequestException:
            logger.error(
                "Erro ao buscar flows do produto LCI no serviço externo: ",
                exc_info=True,
            )
            raise LCIServiceException(
                "Erro ao buscar flows do produto LCI no serviço externo.",
            )
