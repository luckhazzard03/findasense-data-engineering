import pandas as pd

from src.config.settings import Settings
from src.extractors.excel_extractor import ExcelExtractor
from src.auditors.homologation_analyzer import HomologationAnalyzer


settings = Settings()
extractor = ExcelExtractor()

cases = extractor.extract(
    settings.cases_path, settings.cases_sheet, "casos"
)

clients = extractor.extract(
    settings.master_path, settings.clients_sheet, "clientes"
)

channels = extractor.extract(
    settings.master_path, settings.channels_sheet, "canales"
)

normalize = HomologationAnalyzer.normalize

cases["_ceve"] = normalize(cases["Código de Ceve"])
cases["_canal"] = normalize(cases["Canal de Venta"])

clients["_ceve"] = normalize(clients["Código de Ceve"])
clients["_canal_homo"] = normalize(clients["CanalHomo"])

channels["_canal"] = normalize(channels["Canal de Venta"])
channels["_canal_homo"] = normalize(
    channels["Homologación Canal"]
)

# Maestro de canales: solo correspondencias inequívocas.
channel_map = channels[
    ["_canal", "_canal_homo"]
].dropna(subset=["_canal"]).drop_duplicates()

channel_counts = channel_map.groupby(
    "_canal", dropna=False
).size()

valid_channels = channel_counts[
    channel_counts == 1
].index

channel_map = channel_map[
    channel_map["_canal"].isin(valid_channels)
]

cases = cases.merge(
    channel_map,
    on="_canal",
    how="left",
    validate="m:1"
)

# Maestro de clientes con atributos completos.
attributes = [
    "CeVeHomo", "CanalHomo",
    "RegionHomo", "GerenciaHomo"
]

master = clients[
    ["_ceve", "_canal_homo", *attributes]
].drop_duplicates()

master = master.dropna(
    subset=["_ceve", "_canal_homo"]
)

key_counts = master.groupby(
    ["_ceve", "_canal_homo"]
).size()

unique_keys = key_counts[
    key_counts == 1
].index

master = master.set_index(
    ["_ceve", "_canal_homo"]
)

master = master.loc[unique_keys].reset_index()

# Cruce real, no solo validación de existencia.
result = cases.merge(
    master,
    on=["_ceve", "_canal_homo"],
    how="left",
    validate="m:1",
    indicator="_estado_cruce"
)

assert len(result) == len(cases)

print("\nDIAGNÓSTICO DE COBERTURA")
print("-" * 45)

metrics = {
    "Total de casos": len(result),
    "Sin código Ceve": result["_ceve"].isna().sum(),
    "Sin canal original": result["_canal"].isna().sum(),
    "Sin canal homologado": result["_canal_homo"].isna().sum(),
    "Sin coincidencia Ceve + Canal": (
        result["_estado_cruce"] == "left_only"
    ).sum(),
    "Coincidencias con maestro": (
        result["_estado_cruce"] == "both"
    ).sum(),
    "Coincidencias sin región homologada": (
        (result["_estado_cruce"] == "both")
        & result["RegionHomo"].isna()
    ).sum(),
    "Coincidencias sin gerencia homologada": (
        (result["_estado_cruce"] == "both")
        & result["GerenciaHomo"].isna()
    ).sum(),
}

for name, value in metrics.items():
    print(f"{name}: {int(value):,}")

print("\nVALIDACIÓN DE INTEGRIDAD")
print(
    "Registros conservados:",
    len(result) == len(cases)
)
print(
    "IDs únicos conservados:",
    result["Número del caso"].nunique()
    == cases["Número del caso"].nunique()
)
