import pandas as pd
from typing import Dict, Union
from app.service.data_source import DataSource
from app.exceptions.exceptions import BadRequestException
from app.core.logger import logger
from app.models.sustainability_classification import SustainabilityClassification


class EmergyService:
    def __init__(self, data_source: DataSource):
        self.data_source = data_source

    def calculate(self) -> dict:
        df = self.data_source.fetch_data()
        totals = self._calculate_emergy(df)
        indicators = self._calculate_sustainability_indicators(totals)
        return {"emergy": totals, "sustainability": indicators}

    def _filter_valid_inputs(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[df["Flow Direction"].str.strip().str.lower() == "input"].copy()
        if df.empty:
            raise BadRequestException(
                "Nenhuma entrada válida com Flow Direction = 'Input' encontrada."
            )
        return df

    def _calculate_emergy(self, df: pd.DataFrame) -> Dict[str, Dict[str, str]]:
        try:
            df = self._filter_valid_inputs(df)

            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
            df["UEV"] = pd.to_numeric(df["UEV"], errors="coerce")
            df.dropna(subset=["Amount", "UEV"], inplace=True)

            if df.empty:
                raise BadRequestException("Nenhuma linha com Amount e UEV válidos.")

            df["Emergy"] = df["Amount"] * df["UEV"]

            df["Category"] = df["Category"].str.strip().str.upper()
            totals_by_category = df.groupby("Category")["Emergy"].sum().to_dict()
            total_unique = df["Emergy"].sum()

            formatted_totals = {
                category: {"value": f"{value:.2E}", "unit": "sej"}
                for category, value in totals_by_category.items()
            }

            formatted_totals["Total"] = {"value": f"{total_unique:.2E}", "unit": "sej"}

            logger.info(f"Emergia total por categoria: {totals_by_category}")
            return formatted_totals

        except BadRequestException:
            raise
        except Exception:
            logger.error("Erro ao calcular a emergia", exc_info=True)
            raise BadRequestException("Erro ao calcular a emergia.")

    def _calculate_sustainability_indicators(
        self,
        emergy_totals: Dict[str, Dict[str, str]],
    ) -> Dict[str, Union[float, str]]:
        try:

            def parse_value(v: Dict[str, str]) -> float:
                return float(v["value"])

            R = parse_value(emergy_totals.get("R", {"value": "0"}))
            N = parse_value(emergy_totals.get("N", {"value": "0"}))
            F = parse_value(emergy_totals.get("F", {"value": "0"}))

            logger.info(f"Totals de emergia: R: {R}, N: {N}, F: {F}")

            if F == 0 or R == 0:
                raise BadRequestException(
                    "Não é possível calcular EYR/ELR/ESI com R ou F igual a 0."
                )

            EYR = (R + N + F) / F
            ELR = (N + F) / R
            ESI = EYR / ELR

            logger.info(
                f"Indicadores calculados - EYR: {EYR:.2f}, ELR: {ELR:.2f}, ESI: {ESI:.2f}"
            )

            return {
                "EYR": round(EYR, 2),
                "ELR": round(ELR, 2),
                "ESI": round(ESI, 2),
                "classification": self.classify_esi(ESI),
            }

        except BadRequestException:
            raise
        except Exception:
            logger.error(
                "Erro ao calcular os indicadores de sustentabilidade", exc_info=True
            )
            raise BadRequestException(
                "Erro ao calcular os indicadores de sustentabilidade."
            )

    @staticmethod
    def classify_esi(esi: float) -> SustainabilityClassification:
        if esi > 10:
            return SustainabilityClassification.HIGHLY_SUSTAINABLE
        elif esi > 1:
            return SustainabilityClassification.SUSTAINABLE
        elif esi > 0.1:
            return SustainabilityClassification.LOW_SUSTAINABILITY
        else:
            return SustainabilityClassification.UNSUSTAINABLE
