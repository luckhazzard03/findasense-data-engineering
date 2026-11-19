"""
Findasense - Senior Data Engineer Technical Assessment.

Preparación de fechas y dimensiones analíticas.

Reglas:
- No modificar los campos originales.
- No eliminar registros.
- No inventar valores faltantes.
- Registrar fechas inválidas.
- Conservar el orden e identificadores originales.
"""

import pandas as pd


class DataCleaner:
    """Prepara datos para análisis y visualización en Power BI."""

    DATE_COLUMN = "Fecha de apertura"

    DIMENSION_COLUMNS = {
        "Canal de Venta": "Canal_Original_Limpio",
        "Código de Ceve": "Ceve_Original_Limpio",
        "Gerencia Ventas": "Gerencia_Ventas_Limpia",
        "Región Supervisor": "Region_Supervisor_Limpia",
        "Gerencia Supervisor": "Gerencia_Supervisor_Limpia",
        "División Supervisor": "Division_Supervisor_Limpia",
    }

    def __init__(self, strict_validation: bool = True):
        self.strict_validation = strict_validation

    @staticmethod
    def clean_text(series: pd.Series) -> pd.Series:
        """Normaliza espacios y nulos sin cambiar el texto original."""
        values = series.astype("string").str.strip()

        return values.mask(
            values.str.casefold().isin(
                ["", "nan", "none", "null", "nat"]
            )
        )

    def transform(self, cases: pd.DataFrame) -> pd.DataFrame:
        """Agrega columnas analíticas conservando los datos originales."""

        required = [
            "Número del caso",
            self.DATE_COLUMN,
            *self.DIMENSION_COLUMNS.keys(),
        ]

        missing = [
            column for column in required
            if column not in cases.columns
        ]

        if missing:
            raise ValueError(
                f"Columnas requeridas no encontradas: {missing}"
            )

        result = cases.copy(deep=True)
        original_count = len(cases)
        original_ids = (
            cases["Número del caso"]
            .reset_index(drop=True)
        )

        # Fecha principal para contabilizar casos recibidos.
        dates = pd.to_datetime(
            result[self.DATE_COLUMN],
            errors="coerce",
            format="mixed",
        )

        invalid_dates = (
            result[self.DATE_COLUMN].notna()
            & dates.isna()
        )

        if self.strict_validation and invalid_dates.any():
            raise ValueError(
                "Se encontraron "
                f"{int(invalid_dates.sum())} fechas de apertura "
                "no interpretables."
            )

        result["Fecha_Apertura_Analitica"] = dates.dt.normalize()
        result["Fecha_Apertura_Valida"] = dates.notna()

        result["Anio_Apertura"] = dates.dt.year.astype("Int64")
        result["Mes_Apertura"] = dates.dt.month.astype("Int64")
        result["Dia_Apertura"] = dates.dt.day.astype("Int64")
        result["Trimestre_Apertura"] = (
            dates.dt.quarter.astype("Int64")
        )

        # Etiqueta ordenable para gráficos mensuales.
        result["Periodo_Apertura"] = (
            dates.dt.strftime("%Y-%m")
            .astype("string")
        )

        # Dimensiones originales normalizadas en columnas nuevas.
        for source, target in self.DIMENSION_COLUMNS.items():
            result[target] = self.clean_text(result[source])

        # Validaciones de conservación.
        if len(result) != original_count:
            raise AssertionError(
                "La limpieza modificó la cantidad de registros."
            )

        if not (
            result["Número del caso"]
            .reset_index(drop=True)
            .equals(original_ids)
        ):
            raise AssertionError(
                "La limpieza modificó los identificadores "
                "o el orden de los casos."
            )

        return result

    def summarize(self, cases: pd.DataFrame) -> dict:
        """Genera indicadores de calidad temporal."""

        required = [
            "Fecha_Apertura_Analitica",
            "Fecha_Apertura_Valida",
        ]

        missing = [
            column for column in required
            if column not in cases.columns
        ]

        if missing:
            raise ValueError(
                f"Faltan columnas analíticas: {missing}"
            )

        valid_dates = cases["Fecha_Apertura_Analitica"].dropna()

        return {
            "total_casos": int(len(cases)),
            "fechas_validas": int(
                cases["Fecha_Apertura_Valida"].sum()
            ),
            "fechas_invalidas_o_nulas": int(
                (~cases["Fecha_Apertura_Valida"]).sum()
            ),
            "fecha_minima": (
                valid_dates.min().strftime("%Y-%m-%d")
                if not valid_dates.empty else None
            ),
            "fecha_maxima": (
                valid_dates.max().strftime("%Y-%m-%d")
                if not valid_dates.empty else None
            ),
        }
