import re
import unicodedata

import pandas as pd


class CaseClassifier:
    """Clasifica los casos sin modificar las categorías originales."""

    DEFAULT_TARGET = "Quejas de servicio a ventas"

    def __init__(self, target_category: str = DEFAULT_TARGET):
        self.target_category = target_category
        self.target_normalized = self.normalize(target_category)

        if not self.target_normalized:
            raise ValueError(
                "La categoría objetivo no puede estar vacía."
            )

    @staticmethod
    def normalize(value: object) -> str | None:
        if pd.isna(value):
            return None

        text = str(value).strip()

        if not text:
            return None

        text = unicodedata.normalize("NFKD", text)
        text = "".join(char for char in text if not unicodedata.combining(char))

        text = re.sub(r"\s+", " ", text)
        return text.casefold()

    def classify(self, cases: pd.DataFrame) -> pd.DataFrame:
        if "Categoría" not in cases.columns:
            raise ValueError("Falta la columna 'Categoría'.")

        result = cases.copy()

        result["Categoria_Normalizada"] = (
            result["Categoría"].map(self.normalize).astype("string")
        )

        result["Es_Queja_Servicio_Ventas"] = (
            result["Categoria_Normalizada"]
            .eq(self.target_normalized)
            .fillna(False)
            .astype(bool)
        )

        result["Estado_Clasificacion"] = "OTRA_CATEGORIA"

        result.loc[
            result["Categoria_Normalizada"].isna(),
            "Estado_Clasificacion",
        ] = "SIN_CATEGORIA"

        result.loc[
            result["Es_Queja_Servicio_Ventas"],
            "Estado_Clasificacion",
        ] = "QUEJA_SERVICIO_VENTAS"

        if len(result) != len(cases):
            raise AssertionError("La clasificación modificó el total de casos.")

        return result

    def summarize(self, cases: pd.DataFrame) -> dict:
        return {
            "total_casos": int(len(cases)),
            "quejas_servicio_ventas": int(cases["Es_Queja_Servicio_Ventas"].sum()),
            "sin_categoria": int(
                cases["Estado_Clasificacion"].eq("SIN_CATEGORIA").sum()
            ),
            "otras_categorias": int(
                cases["Estado_Clasificacion"].eq("OTRA_CATEGORIA").sum()
            ),
        }
