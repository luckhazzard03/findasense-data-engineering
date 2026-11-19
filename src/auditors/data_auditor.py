import json
from pathlib import Path
import pandas as pd


class DataAuditor:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def normalize(series: pd.Series) -> pd.Series:
        values = series.astype("string").str.strip()
        return values.replace({
            "": pd.NA, "nan": pd.NA,
            "None": pd.NA, "null": pd.NA
        })

    def profile(self, df: pd.DataFrame, name: str) -> dict:
        report = pd.DataFrame({
            "columna": df.columns,
            "tipo": [str(x) for x in df.dtypes],
            "nulos": df.isna().sum().to_numpy(),
            "valores_unicos": df.nunique(dropna=True).to_numpy(),
        })
        report["porcentaje_nulos"] = (
            report["nulos"] / len(df) * 100
            if len(df) else 0.0
        )
        report.to_csv(
            self.output_dir / f"{name}_perfil.csv",
            index=False, encoding="utf-8-sig"
        )
        return {
            "filas": int(len(df)),
            "columnas": int(len(df.columns)),
            "duplicados_exactos": int(df.duplicated().sum())
        }

    def audit_cases(self, df: pd.DataFrame) -> dict:
        ids = self.normalize(df["Número del caso"])
        ceves = self.normalize(df["Código de Ceve"])
        categories = self.normalize(df["Categoría"])

        category_counts = (
            categories.fillna("SIN CATEGORÍA")
            .value_counts()
            .rename_axis("categoria")
            .reset_index(name="cantidad")
        )
        category_counts.to_csv(
            self.output_dir / "categorias.csv",
            index=False, encoding="utf-8-sig"
        )

        repeated = ids.notna() & ids.duplicated(keep=False)

        return {
            "total_casos": int(len(df)),
            "ids_nulos": int(ids.isna().sum()),
            "filas_con_id_repetido": int(repeated.sum()),
            "ceves_nulos": int(ceves.isna().sum()),
            "categorias_nulas": int(categories.isna().sum())
        }

    def audit_master(self, df: pd.DataFrame) -> dict:
        attributes = [
            "CeVeHomo", "CanalHomo",
            "RegionHomo", "GerenciaHomo"
        ]
        data = df[["Código de Ceve", *attributes]].copy()
        for col in data.columns:
            data[col] = self.normalize(data[col])

        valid = data.dropna(subset=["Código de Ceve"])
        combinations = valid.drop_duplicates()

        counts = (
            combinations.groupby("Código de Ceve")
            .size().rename("combinaciones")
        )
        conflicts = counts[counts > 1]
        conflicts.to_csv(
            self.output_dir / "ceve_conflictos.csv",
            encoding="utf-8-sig"
        )

        return {
            "filas": int(len(df)),
            "ceves_unicos": int(
                valid["Código de Ceve"].nunique()
            ),
            "ceves_con_multiples_combinaciones": int(
                len(conflicts)
            ),
            "filas_sin_ceve": int(
                data["Código de Ceve"].isna().sum()
            )
        }

    def audit_channels(self, df: pd.DataFrame) -> dict:
        data = df[[
            "Canal de Venta", "Homologación Canal"
        ]].copy()
        for col in data.columns:
            data[col] = self.normalize(data[col])

        valid = data.dropna(subset=["Canal de Venta"])
        combinations = valid.drop_duplicates()

        counts = (
            combinations.groupby("Canal de Venta")
            .size().rename("combinaciones")
        )
        conflicts = counts[counts > 1]
        conflicts.to_csv(
            self.output_dir / "canal_conflictos.csv",
            encoding="utf-8-sig"
        )

        return {
            "filas": int(len(df)),
            "filas_sin_canal": int(
                data["Canal de Venta"].isna().sum()
            ),
            "canales_unicos": int(
                valid["Canal de Venta"].nunique()
            ),
            "canales_con_multiples_homologaciones": int(
                len(conflicts)
            )
        }

    def save(self, summary: dict) -> None:
        with (
            self.output_dir / "resumen_auditoria.json"
        ).open("w", encoding="utf-8") as file:
            json.dump(
                summary, file,
                indent=2, ensure_ascii=False
            )
