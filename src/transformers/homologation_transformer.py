import pandas as pd

from src.auditors.homologation_analyzer import HomologationAnalyzer


class HomologationTransformer:
    """Homologa canales y clientes sin perder ni duplicar casos."""

    MASTER_ATTRIBUTES = [
        "CeVeHomo",
        "CanalHomo",
        "RegionHomo",
        "GerenciaHomo",
    ]

    def __init__(self, strict_validation: bool = True):
        self.strict_validation = strict_validation

    @staticmethod
    def normalize(series: pd.Series) -> pd.Series:
        return HomologationAnalyzer.normalize(series)

    def transform(
        self,
        cases: pd.DataFrame,
        clients: pd.DataFrame,
        channels: pd.DataFrame,
    ) -> pd.DataFrame:

        cases = cases.copy()
        clients = clients.copy()
        channels = channels.copy()

        original_count = len(cases)
        original_ids = cases["Número del caso"].copy()

        # 1. Normalización
        cases["_ceve"] = self.normalize(cases["Código de Ceve"])
        cases["_canal"] = self.normalize(cases["Canal de Venta"])

        clients["_ceve"] = self.normalize(clients["Código de Ceve"])
        clients["_canal_homo"] = self.normalize(clients["CanalHomo"])

        channels["_canal"] = self.normalize(channels["Canal de Venta"])
        channels["_canal_homo"] = self.normalize(
            channels["Homologación Canal"]
        )

        # 2. Homologación de canales
        channel_map = (
            channels[["_canal", "_canal_homo"]]
            .dropna(subset=["_canal"])
            .drop_duplicates()
        )

        channel_counts = channel_map.groupby("_canal").size()
        ambiguous_channels = set(
            channel_counts[channel_counts > 1].index
        )

        if ambiguous_channels and self.strict_validation:
            raise ValueError(
                f"Canales ambiguos: {len(ambiguous_channels)}"
            )

        channel_map = channel_map[
            ~channel_map["_canal"].isin(ambiguous_channels)
        ].dropna(subset=["_canal_homo"])

        # Evitar coincidencias artificiales entre valores nulos.
        cases = cases.merge(
            channel_map,
            on="_canal",
            how="left",
            validate="m:1",
            sort=False,
        )

        # 3. Preparar maestro de clientes
        master = clients[
            ["_ceve", "_canal_homo", *self.MASTER_ATTRIBUTES]
        ].copy()

        master = master.dropna(
            subset=["_ceve", "_canal_homo"]
        )

        # Normalizar atributos antes de detectar conflictos.
        for col in self.MASTER_ATTRIBUTES:
            master[col] = self.normalize(master[col])

        master = master.drop_duplicates()

        key_counts = master.groupby(
            ["_ceve", "_canal_homo"]
        ).size()

        ambiguous_keys = set(
            key_counts[key_counts > 1].index
        )

        # No seleccionar arbitrariamente una homologación.
        if ambiguous_keys:
            if self.strict_validation:
                raise ValueError(
                    "Se detectaron "
                    f"{len(ambiguous_keys)} claves ambiguas "
                    "Ceve + Canal."
                )

            master = master[
                ~pd.MultiIndex.from_frame(
                    master[["_ceve", "_canal_homo"]]
                ).isin(ambiguous_keys)
            ]

        # Nombres exclusivos para no sobrescribir columnas originales.
        master = master.rename(columns={
            "CeVeHomo": "Ceve_Homologado",
            "CanalHomo": "Canal_Maestro",
            "RegionHomo": "Region_Homologada",
            "GerenciaHomo": "Gerencia_Homologada",
        })

        # 4. Cruce de clientes
        result = cases.merge(
            master,
            on=["_ceve", "_canal_homo"],
            how="left",
            validate="m:1",
            indicator="_estado_cruce",
            sort=False,
        )

        # 5. Estados de calidad mutuamente excluyentes
        result["Estado_Homologacion"] = "SIN_COINCIDENCIA"

        result.loc[
            result["_ceve"].isna(),
            "Estado_Homologacion"
        ] = "SIN_CEVE"

        result.loc[
            result["_ceve"].notna()
            & result["_canal"].isna(),
            "Estado_Homologacion"
        ] = "SIN_CANAL"

        result.loc[
            result["_ceve"].notna()
            & result["_canal"].notna()
            & result["_canal_homo"].isna(),
            "Estado_Homologacion"
        ] = "CANAL_NO_HOMOLOGADO"

        matched = result["_estado_cruce"].eq("both")

        result.loc[
            matched, "Estado_Homologacion"
        ] = "HOMOLOGADO"

        incomplete = matched & (
            result[
                [
                    "Ceve_Homologado",
                    "Canal_Maestro",
                    "Region_Homologada",
                    "Gerencia_Homologada",
                ]
            ].isna().any(axis=1)
        )

        result.loc[
            incomplete, "Estado_Homologacion"
        ] = "HOMOLOGACION_INCOMPLETA"

        # 6. Validaciones de integridad
        if len(result) != original_count:
            raise AssertionError(
                "El ETL modificó el número de casos."
            )

        if not result["Número del caso"].reset_index(
            drop=True
        ).equals(original_ids.reset_index(drop=True)):
            raise AssertionError(
                "El ETL alteró el orden o los IDs originales."
            )

        return result
