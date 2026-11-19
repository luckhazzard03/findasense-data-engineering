from pathlib import Path
import pandas as pd


class ExcelExtractor:
    REQUIRED = {
        "casos": [
            "Número del caso", "Categoría",
            "Código de Ceve", "Canal de Venta",
            "Fecha de apertura"
        ],
        "clientes": [
            "Código de Ceve", "CeVeHomo",
            "CanalHomo", "RegionHomo", "GerenciaHomo"
        ],
        "canales": [
            "Canal de Venta", "Homologación Canal"
        ],
    }

    def extract(
        self, path: Path, sheet: str, source: str
    ) -> pd.DataFrame:
        if not path.is_file():
            raise FileNotFoundError(f"Archivo no encontrado: {path}")

        with pd.ExcelFile(path, engine="openpyxl") as book:
            if sheet not in book.sheet_names:
                raise ValueError(
                    f"Hoja '{sheet}' inexistente. "
                    f"Disponibles: {book.sheet_names}"
                )

            df = pd.read_excel(
                book, sheet_name=sheet,
                dtype={
                    "Código de Ceve": "string",
                    "Número del caso": "string",
                    "Canal de Venta": "string",
                }
            )

        df.columns = df.columns.astype(str).str.strip()

        missing = [
            col for col in self.REQUIRED[source]
            if col not in df.columns
        ]
        if missing:
            raise ValueError(
                f"Columnas faltantes en {source}: {missing}"
            )

        print(
            f"[EXTRACT] {source}: "
            f"{len(df):,} filas, {len(df.columns)} columnas"
        )
        return df
