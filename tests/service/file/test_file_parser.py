import pytest
import pandas as pd
from pathlib import Path
from app.service.file.file_parser import (
    detect_delimiter,
    resolve_dataframe,
    parse_file_to_dataframe,
)
from app.exceptions.exceptions import BadRequestException

VALID_CSV_CONTENT = """Flow Name,Amount,Unit,Flow Direction,UEV,Category
Água,100,L,Input,2.5,R
Energia,200,kWh,Input,1.2,F
"""

INVALID_CSV_CONTENT = """Flow Name,Amount,Unit,Flow Direction
Água,100,L,Input
"""

INVALID_AMOUNT_CSV_CONTENT = """Flow Name,Amount,Unit,Flow Direction,UEV,Category
Água,invalid_value,L,Input,2.5,R
Energia,200,kWh,Input,1.2,F
"""

MISSING_UEV_CSV_CONTENT = """Flow Name,Amount,Unit,Flow Direction,UEV,Category
Água,100,L,Input,,R
Energia,200,kWh,Input,1.2,F
"""

INVALID_UEV_CSV_CONTENT = """Flow Name,Amount,Unit,Flow Direction,UEV,Category
Água,100,L,Input,invalid_value,R
Energia,200,kWh,Input,1.2,F
"""


@pytest.fixture
def valid_csv_file(tmp_path) -> Path:
    file = tmp_path / "valid_file.csv"
    file.write_text(VALID_CSV_CONTENT)
    return file


@pytest.fixture
def invalid_csv_file(tmp_path) -> Path:
    file = tmp_path / "invalid_file.csv"
    file.write_text(INVALID_CSV_CONTENT)
    return file


@pytest.fixture
def unsupported_file(tmp_path) -> Path:
    file = tmp_path / "unsupported_file.txt"
    file.write_text("Unsupported content")
    return file


@pytest.fixture
def invalid_amount_csv_file(tmp_path) -> Path:
    file = tmp_path / "invalid_amount_file.csv"
    file.write_text(INVALID_AMOUNT_CSV_CONTENT)
    return file


@pytest.fixture
def missing_uev_csv_file(tmp_path) -> Path:
    file = tmp_path / "missing_uev_file.csv"
    file.write_text(MISSING_UEV_CSV_CONTENT)
    return file


@pytest.fixture
def invalid_uev_csv_file(tmp_path) -> Path:
    file = tmp_path / "invalid_uev_file.csv"
    file.write_text(INVALID_UEV_CSV_CONTENT)
    return file


def test_detect_delimiter(valid_csv_file):
    delimiter = detect_delimiter(valid_csv_file)
    assert delimiter == ",", f"Expected delimiter to be ',', but got '{delimiter}'"


def test_resolve_dataframe_csv(valid_csv_file):
    df = resolve_dataframe(valid_csv_file)
    assert isinstance(df, pd.DataFrame), "Expected a DataFrame"
    assert not df.empty, "DataFrame should not be empty"
    assert df.shape[0] == 2, "Expected 2 lines in the DataFrame"
    assert df.shape[1] == 6, "Expected 6 columns in the DataFrame"


def test_parse_file_to_dataframe_valid(valid_csv_file):
    df = parse_file_to_dataframe(valid_csv_file)
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 2


def test_parse_file_to_dataframe_missing_columns(invalid_csv_file):
    with pytest.raises(BadRequestException) as exc:
        parse_file_to_dataframe(invalid_csv_file)
    assert "Colunas obrigatórias ausentes" in str(exc.value.detail)


def test_resolve_dataframe_unsupported_format(unsupported_file):
    with pytest.raises(BadRequestException) as exc:
        resolve_dataframe(unsupported_file)
    assert "Extensão de arquivo não suportada" in str(exc.value.detail)


def test_parse_file_to_dataframe_invalid_amount(invalid_amount_csv_file):
    with pytest.raises(BadRequestException) as exc:
        parse_file_to_dataframe(invalid_amount_csv_file)
    assert "Valores inválidos encontrados na coluna 'Amount'" in str(exc.value.detail)


def test_parse_file_to_dataframe_missing_uev(missing_uev_csv_file):
    with pytest.raises(BadRequestException) as exc:
        parse_file_to_dataframe(missing_uev_csv_file)
    assert "Valores de UEV ausentes para entradas nas linhas" in str(exc.value.detail)
    assert "2" in str(exc.value.detail), "A linha 2 deve ser mencionada como ausente."


def test_parse_file_to_dataframe_invalid_uev(invalid_uev_csv_file):
    with pytest.raises(BadRequestException) as exc:
        parse_file_to_dataframe(invalid_uev_csv_file)
    assert "Valores inválidos encontrados na coluna 'UEV' para as entradas" in str(
        exc.value.detail
    )
