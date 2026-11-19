"""
Exportación de datasets analíticos para Power BI.

No exporta información personal innecesaria.
Preserva todos los casos y sus estados de calidad.
"""

from pathlib import Path

import pandas as pd


class FileLoader:
    """Exporta vistas analíticas validadas a CSV."""

    COLUMNS = [
        "Número del caso",
        "Categoría",
        "Subcategoría",
        "Estado",
        "Estado (campo salesforce)",
        "Fecha_Apertura_Analitica",
        "Anio_Apertura",
        "Mes_Apertura",
        "Dia_Apertura",
        "Trimestre_Apertura",
        "Periodo_Apertura",
        "Fecha_Apertura_Valida",
        "Es_Queja_Servicio_Ventas",
        "Estado_Clasificacion",
        "Estado_Homologacion",
        "Ceve_Homologado",
        "Canal_Maestro",
        "Region_Homologada",
        "Gerencia_Homologada",
        "Division_Supervisor_Limpia",
        "Canal_Original_Limpio",
        "Ceve_Original_Limpio",
        "Gerencia_Ventas_Limpia",
        "Region_Supervisor_Limpia",
        "Gerencia_Supervisor_Limpia",
    ]

    def __init__(self, output_dir="data/processed"):
        self.output_dir = Path(output_dir)

    def export(self, data: pd.DataFrame) -> dict:
        """Genera y verifica los dos archivos para Power BI."""

        missing = [
            column for column in self.COLUMNS
            if column not in data.columns
        ]

        if missing:
            raise ValueError(
                f"Columnas analíticas faltantes: {missing}"
            )

        if data["Número del caso"].isna().any():
            raise ValueError("Existen identificadores nulos.")

        if data["Número del caso"].duplicated().any():
            raise ValueError("Existen identificadores duplicados.")

        full = data.loc[:, self.COLUMNS].copy()

        target_mask = full[
            "Es_Queja_Servicio_Ventas"
        ].fillna(False).astype(bool)

        complaints = full.loc[target_mask].copy()

        if len(full) != len(data):
            raise AssertionError(
                "Se perdieron registros en la exportación."
            )

        if len(complaints) != int(target_mask.sum()):
            raise AssertionError(
                "El filtro de quejas produjo un total incorrecto."
            )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        full_path = (
            self.output_dir / "cricks_casos_powerbi.csv"
        )
        complaints_path = (
            self.output_dir / "cricks_quejas_ventas_powerbi.csv"
        )

        full.to_csv(
            full_path,
            index=False,
            encoding="utf-8-sig",
            date_format="%Y-%m-%d",
        )

        complaints.to_csv(
            complaints_path,
            index=False,
            encoding="utf-8-sig",
            date_format="%Y-%m-%d",
        )

        # Verificación de los archivos escritos.
        full_check = pd.read_csv(
            full_path,
            usecols=["Número del caso"],
            dtype="string",
        )

        complaints_check = pd.read_csv(
            complaints_path,
            usecols=["Número del caso"],
            dtype="string",
        )

        if len(full_check) != len(full):
            raise AssertionError(
                "El CSV completo no conserva todos los casos."
            )

        if len(complaints_check) != len(complaints):
            raise AssertionError(
                "El CSV de quejas tiene un total incorrecto."
            )

        return {
            "casos_exportados": int(len(full)),
            "quejas_exportadas": int(len(complaints)),
            "columnas_exportadas": len(self.COLUMNS),
            "archivo_casos": str(full_path),
            "archivo_quejas": str(complaints_path),
            "integridad_exportacion": True,
        }
