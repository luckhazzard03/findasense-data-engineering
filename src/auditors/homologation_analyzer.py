from pathlib import Path
import pandas as pd


class HomologationAnalyzer:
    """Analiza posibles claves de homologación."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def normalize(series: pd.Series) -> pd.Series:
        return (
            series.astype("string")
            .str.strip()
            .str.upper()
            .replace({"": pd.NA, "NAN": pd.NA, "NONE": pd.NA, "NULL": pd.NA})
        )

    def analyze(
        self, cases: pd.DataFrame, clients: pd.DataFrame, channels: pd.DataFrame
    ) -> dict:

        cases = cases.copy()
        clients = clients.copy()
        channels = channels.copy()

        cases["_ceve"] = self.normalize(cases["Código de Ceve"])
        cases["_canal"] = self.normalize(cases["Canal de Venta"])

        clients["_ceve"] = self.normalize(clients["Código de Ceve"])
        clients["_canal_homo"] = self.normalize(clients["CanalHomo"])

        channels["_canal"] = self.normalize(channels["Canal de Venta"])
        channels["_canal_homo"] = self.normalize(channels["Homologación Canal"])

        # Mantener solo homologaciones de canal inequívocas.
        channel_map = channels.dropna(subset=["_canal"])[
            ["_canal", "_canal_homo"]
        ].drop_duplicates()

        valid_channels = channel_map.groupby("_canal", dropna=False).size()
        valid_channels = valid_channels[valid_channels == 1].index

        channel_map = channel_map[channel_map["_canal"].isin(valid_channels)]

        # m:1 impide multiplicar registros.
        enriched = cases.merge(
            channel_map,
            on="_canal",
            how="left",
            validate="m:1",
            indicator="_estado_canal",
        )

        # Combinaciones distintas del maestro.
        attrs = ["CeVeHomo", "CanalHomo", "RegionHomo", "GerenciaHomo"]

        master = clients[["_ceve", "_canal_homo", *attrs]].drop_duplicates()

        # Evaluar clave compuesta Ceve + Canal homologado.
        counts = (
            master.dropna(subset=["_ceve", "_canal_homo"])
            .groupby(["_ceve", "_canal_homo"])
            .size()
            .rename("combinaciones")
            .reset_index()
        )

        counts.to_csv(
            self.output_dir / "claves_compuestas.csv", index=False, encoding="utf-8-sig"
        )

        unique_keys = counts[counts["combinaciones"] == 1][["_ceve", "_canal_homo"]]

        # Verificar cobertura de la clave compuesta.
        coverage = enriched.merge(
            unique_keys.assign(clave_compuesta_valida=True),
            on=["_ceve", "_canal_homo"],
            how="left",
            validate="m:1",
        )

        summary = {
            "casos_originales": len(cases),
            "casos_tras_homologar_canal": len(enriched),
            "casos_tras_validar_clave": len(coverage),
            "casos_con_canal_homologado": int(enriched["_canal_homo"].notna().sum()),
            "casos_con_clave_compuesta_unica": int(
                coverage["clave_compuesta_valida"].eq(True).sum()
            ),
            "claves_compuestas_ambiguas": int((counts["combinaciones"] > 1).sum()),
        }

        return summary
