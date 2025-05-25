import pandas as pd
from abc import ABC, abstractmethod
from pathlib import Path
from app.service.file.file_parser import parse_file_to_dataframe
from app.exceptions.exceptions import LCIServiceException
from app.service.lci_service import LCIService


class DataSource(ABC):
    @abstractmethod
    def fetch_data(self) -> pd.DataFrame:
        """Método para buscar dados e retornar um DataFrame."""
        pass


class FileDataSource(DataSource):
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def fetch_data(self) -> pd.DataFrame:
        return parse_file_to_dataframe(self.file_path)


class APIDataSource(DataSource):
    def __init__(self, product_id: int, lci_service: LCIService):
        self.product_id = product_id
        self.lci_service = lci_service

    def fetch_data(self) -> pd.DataFrame:
        try:
            flows = self.lci_service.get_flows_by_product_id(self.product_id)
            data = [flow.model_dump() for flow in flows]
            df = pd.DataFrame(data)

            column_mapping = {
                "flow_name": "Flow Name",
                "amount": "Amount",
                "unit": "Unit",
                "flow_direction": "Flow Direction",
                "uev": "UEV",
                "category": "Category",
            }

            df = df.rename(columns=column_mapping)

            return df
        except LCIServiceException:
            raise
