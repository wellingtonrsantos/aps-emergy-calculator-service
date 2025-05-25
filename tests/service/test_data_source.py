import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from app.service.data_source import FileDataSource, APIDataSource
from app.exceptions.exceptions import LCIServiceException


def test_file_data_source_fetch_data():
    fake_path = "fake/path/to/file.csv"
    fake_df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    with patch(
        "app.service.data_source.parse_file_to_dataframe", return_value=fake_df
    ) as mock_parse:
        ds = FileDataSource(fake_path)
        df = ds.fetch_data()
        mock_parse.assert_called_once_with(fake_path)
        pd.testing.assert_frame_equal(df, fake_df)


def test_api_data_source_fetch_data_success():
    fake_product_id = 123
    fake_flows = [
        MagicMock(model_dump=MagicMock(return_value={"x": 1, "y": 2})),
        MagicMock(model_dump=MagicMock(return_value={"x": 3, "y": 4})),
    ]
    mock_lci_service = MagicMock()
    mock_lci_service.get_flows_by_product_id.return_value = fake_flows

    ds = APIDataSource(fake_product_id, mock_lci_service)
    df = ds.fetch_data()
    mock_lci_service.get_flows_by_product_id.assert_called_once_with(fake_product_id)
    pd.testing.assert_frame_equal(
        df, pd.DataFrame([{"x": 1, "y": 2}, {"x": 3, "y": 4}])
    )


def test_api_data_source_fetch_data_lci_service_exception():
    fake_product_id = 123
    mock_lci_service = MagicMock()
    mock_lci_service.get_flows_by_product_id.side_effect = LCIServiceException(
        "Erro LCI"
    )

    ds = APIDataSource(fake_product_id, mock_lci_service)
    with pytest.raises(LCIServiceException) as exc:
        ds.fetch_data()
    assert "Erro LCI" in str(exc.value)
