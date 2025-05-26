import pytest
import pandas as pd
from app.service.emergy_service import EmergyService
from app.service.data_source import DataSource
from app.exceptions.exceptions import BadRequestException


class DummyDataSource(DataSource):
    def __init__(self, df):
        self.df = df

    def fetch_data(self):
        return self.df


@pytest.fixture
def valid_input_dataframe():
    return pd.DataFrame(
        {
            "Flow Name": ["A", "B", "C"],
            "Amount": [10, 5, 2],
            "Unit": ["kg", "kg", "kg"],
            "Flow Direction": ["Input", "Input", "Input"],
            "UEV": [1e6, 2e6, 1e7],
            "Category": ["R", "F", "N"],
        }
    )


@pytest.fixture
def dataframe_with_inputs_and_outputs():
    data = {
        "Flow Name": ["Electricity", "CO2"],
        "Amount": [10, 20],
        "Unit": ["MJ", "kg"],
        "Flow Direction": ["Input", "Output"],
        "UEV": [1e5, 2e5],
        "Category": ["F", "F"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def dataframe_with_invalid_numeric_data():
    return pd.DataFrame(
        {
            "Flow Name": ["A", "B"],
            "Amount": ["dez", "vinte"],
            "Unit": ["kg", "kg"],
            "Flow Direction": ["Input", "Input"],
            "UEV": [1e6, None],
            "Category": ["R", "F"],
        }
    )


@pytest.fixture
def dataframe_with_only_outputs():
    data = {
        "Flow Name": ["CO2", "Water"],
        "Amount": [20, 30],
        "Unit": ["kg", "kg"],
        "Flow Direction": ["Output", "Output"],
        "UEV": [2e5, 3e5],
        "Category": ["F", "F"],
    }
    return pd.DataFrame(data)


def test_filter_valid_inputs_returns_only_inputs(dataframe_with_inputs_and_outputs):
    service = EmergyService(DummyDataSource(dataframe_with_inputs_and_outputs))
    result = service._filter_valid_inputs(dataframe_with_inputs_and_outputs)

    assert len(result) == 1
    assert result.iloc[0]["Flow Direction"].lower() == "input"


def test_filter_valid_inputs_raises_exception_if_none(dataframe_with_only_outputs):
    service = EmergyService(DummyDataSource(dataframe_with_inputs_and_outputs))
    with pytest.raises(BadRequestException) as exc:
        service._filter_valid_inputs(dataframe_with_only_outputs)
    assert "Nenhuma entrada válida com Flow Direction" in str(exc.value.detail)


def test_calculate_emergy_valid(valid_input_dataframe):
    service = EmergyService(DummyDataSource(valid_input_dataframe))
    result = service.calculate()
    emergy = result["emergy"]

    assert isinstance(emergy, dict)
    assert emergy["R"]["value"] == "1.00E+07"
    assert emergy["F"]["value"] == "1.00E+07"
    assert emergy["N"]["value"] == "2.00E+07"
    assert emergy["Total"]["value"] == "4.00E+07"
    assert emergy["Total"]["unit"] == "sej"


def test_calculate_emergy_with_only_outputs_raises(dataframe_with_only_outputs):
    service = EmergyService(DummyDataSource(dataframe_with_only_outputs))
    with pytest.raises(BadRequestException) as exc:
        service.calculate()
    assert "Nenhuma entrada válida com Flow Direction" in str(exc.value.detail)


def test_calculate_emergy_with_invalid_amounts_raises(
    dataframe_with_invalid_numeric_data,
):
    service = EmergyService(DummyDataSource(dataframe_with_invalid_numeric_data))
    with pytest.raises(BadRequestException) as exc:
        service.calculate()
    assert "Nenhuma linha com Amount e UEV válidos." in str(exc.value.detail)


def test_calculate_sustainability_indicators_valid(valid_input_dataframe):
    emergy_totals = {
        "R": {"value": "1.00E+06", "unit": "sej"},
        "N": {"value": "2.00E+06", "unit": "sej"},
        "F": {"value": "1.00E+06", "unit": "sej"},
        "Total": {"value": "4.00E+06", "unit": "sej"},
    }

    service = EmergyService(DummyDataSource(valid_input_dataframe))
    result = service._calculate_sustainability_indicators(emergy_totals)

    assert result["EYR"] == 4.0
    assert result["ELR"] == 3.0
    assert result["ESI"] == 1.33
    assert result["classification"] == "SUSTAINABLE"


def test_sustainability_indicators_with_zero_R_raises(
    dataframe_with_invalid_numeric_data,
):
    emergy_totals = {
        "R": {"value": "0", "unit": "sej"},
        "N": {"value": "2.00E+06", "unit": "sej"},
        "F": {"value": "1.00E+06", "unit": "sej"},
    }

    service = EmergyService(DummyDataSource(dataframe_with_invalid_numeric_data))

    with pytest.raises(BadRequestException) as exc:
        service._calculate_sustainability_indicators(emergy_totals)
    assert "R ou F igual a 0" in str(exc.value.detail)


def test_sustainability_indicators_with_zero_F_raises(
    dataframe_with_invalid_numeric_data,
):
    emergy_totals = {
        "R": {"value": "1.00E+06", "unit": "sej"},
        "N": {"value": "2.00E+06", "unit": "sej"},
        "F": {"value": "0", "unit": "sej"},
    }

    service = EmergyService(DummyDataSource(dataframe_with_invalid_numeric_data))

    with pytest.raises(BadRequestException) as exc:
        service._calculate_sustainability_indicators(emergy_totals)
    assert "R ou F igual a 0" in str(exc.value.detail)


def test_classification_of_ESI_correctly_returns_category(valid_input_dataframe):
    emergy_totals = {
        "R": {"value": "1.00E+06", "unit": "sej"},
        "N": {"value": "2.00E+06", "unit": "sej"},
        "F": {"value": "1.00E+05", "unit": "sej"},
    }

    service = EmergyService(DummyDataSource(valid_input_dataframe))
    result = service._calculate_sustainability_indicators(emergy_totals)

    assert result["ESI"] > 10
    assert result["classification"] == "HIGHLY_SUSTAINABLE"
