import pandas as pd


class DataValidationError(Exception):
    """Error de integridad en el proceso ETL."""


class DataValidator:
    """Valida integridad, unicidad y calidad de homologaciones."""

    REQUIRED_COLUMNS = [
        "Número del caso",
        "Categoría",
        "Fecha de apertura",
        "Estado_Homologacion",
        "Region_Homologada",
        "Gerencia_Homologada",
    ]

    def validate(
        self,
        original: pd.DataFrame,
        transformed: pd.DataFrame,
    ) -> dict:

        missing = [
            column for column in self.REQUIRED_COLUMNS
            if column not in transformed.columns
        ]

        if missing:
            raise DataValidationError(
                f"Columnas faltantes: {missing}"
            )

        if len(original) != len(transformed):
            raise DataValidationError(
                "La transformación modificó el número de casos."
            )

        original_ids = (
            original["Número del caso"]
            .astype("string")
            .reset_index(drop=True)
        )
        transformed_ids = (
            transformed["Número del caso"]
            .astype("string")
            .reset_index(drop=True)
        )

        if not original_ids.equals(transformed_ids):
            raise DataValidationError(
                "Los identificadores u orden de los casos cambiaron."
            )

        if transformed_ids.isna().any():
            raise DataValidationError(
                "Existen identificadores nulos."
            )

        if transformed_ids.duplicated().any():
            raise DataValidationError(
                "Existen identificadores duplicados."
            )

        statuses = transformed["Estado_Homologacion"]

        if statuses.isna().any():
            raise DataValidationError(
                "Existen casos sin estado de homologación."
            )

        matched = statuses.eq("HOMOLOGADO")

        required_homologation = [
            "Ceve_Homologado",
            "Canal_Maestro",
            "Region_Homologada",
            "Gerencia_Homologada",
        ]

        incomplete = (
            transformed.loc[
                matched, required_homologation
            ].isna().any(axis=1)
        )

        if incomplete.any():
            raise DataValidationError(
                "Existen casos HOMOLOGADO con atributos nulos."
            )

        return {
            "total_original": int(len(original)),
            "total_transformado": int(len(transformed)),
            "ids_unicos": int(transformed_ids.nunique()),
            "homologados": int(matched.sum()),
            "no_homologados": int((~matched).sum()),
            "integridad_validada": True,
        }
