import pandas as pd
from pathlib import Path
import csv
from app.exceptions.exceptions import BadRequestException

REQUIRED_COLUMNS = {"Flow Name", "Amount", "Unit", "Flow Direction", "UEV", "Category"}


def detect_delimiter(file_path: Path) -> str:
    with open(file_path, "r") as file:
        sample = file.readline()
        sniffer = csv.Sniffer()
        return sniffer.sniff(sample).delimiter


def resolve_dataframe(file_path: Path) -> pd.DataFrame:
    file_extension = file_path.suffix.lower()

    if file_extension == ".csv":
        delimiter = detect_delimiter(file_path)
        return pd.read_csv(file_path, sep=delimiter)

    if file_extension in {".xls", ".xlsx"}:
        return pd.read_excel(file_path)

    raise BadRequestException("Extensão de arquivo não suportada.")


def parse_file_to_dataframe(file_path: Path) -> pd.DataFrame:
    df = resolve_dataframe(file_path)

    df.columns = [col.strip() for col in df.columns]

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise BadRequestException(
            f"Colunas obrigatórias ausentes: {', '.join(missing_columns)}"
        )

    try:
        df["Amount"] = pd.to_numeric(df["Amount"])
    except ValueError:
        raise BadRequestException("Valores inválidos encontrados na coluna 'Amount'.")

    input_rows = df[df["Flow Direction"] != "Output"].copy()
    try:
        input_rows["UEV"] = pd.to_numeric(input_rows["UEV"])
        if input_rows["UEV"].isna().any():
            null_rows = input_rows[input_rows["UEV"].isna()]
            row_numbers = [str(int(idx) + 2) for idx in null_rows.index]
            raise BadRequestException(
                f"Valores de UEV ausentes para entradas nas linhas: {', '.join(row_numbers)}"
            )
    except ValueError:
        raise BadRequestException(
            "Valores inválidos encontrados na coluna 'UEV' para as entradas."
        )

    return df
