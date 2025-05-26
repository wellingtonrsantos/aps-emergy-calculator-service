import pytest
import requests
from unittest.mock import patch, MagicMock
from app.service.lci_service import LCIService
from app.models.lci_models import LCIProduct, LCIFlow
from app.exceptions.exceptions import LCIServiceException


def test_list_products_success():
    fake_products = [
        {"id": 1, "name": "Produto A", "description": "Descricao A"},
        {"id": 2, "name": "Produto B", "description": "Descricao B"},
    ]
    with patch("app.service.lci_service.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = fake_products
        mock_get.return_value = mock_response

        service = LCIService()
        result = service.list_products()
        assert isinstance(result, list)
        assert all(isinstance(p, LCIProduct) for p in result)
        assert result[0].id == 1
        assert result[0].name == "Produto A"


def test_list_products_http_error():
    with patch("app.service.lci_service.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("HTTP error")
        mock_get.return_value = mock_response

        service = LCIService()
        with pytest.raises(LCIServiceException):
            service.list_products()


def test_get_flows_by_product_id_success():
    fake_flows = [
        {
            "Flow Name": "Eletricidade (hidrelétrica)",
            "Amount": 0.1,
            "Unit": "MJ",
            "Flow Direction": "Input",
            "UEV": 123,
            "Category": "F",
        },
        {
            "Flow Name": "Cavacos de madeira",
            "Amount": 0.2,
            "Unit": "ton",
            "Flow Direction": "Input",
            "UEV": 456,
            "Category": "R",
        },
    ]
    with patch("app.service.lci_service.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = fake_flows
        mock_get.return_value = mock_response

        service = LCIService()
        result = service.get_flows_by_product_id(1)
        assert isinstance(result, list)
        assert all(isinstance(f, LCIFlow) for f in result)
        assert result[0].flow_name == "Eletricidade (hidrelétrica)"
        assert result[1].amount == 0.2


def test_get_flows_by_product_id_http_error():
    with patch("app.service.lci_service.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("HTTP error")
        mock_get.return_value = mock_response

        service = LCIService()
        with pytest.raises(LCIServiceException):
            service.get_flows_by_product_id(1)
