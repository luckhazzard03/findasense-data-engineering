"""
Findasense - Senior Data Engineer Technical Assessment

Archivo: test_homologation_run.py
Objetivo:
    Ejecutar y validar la homologación de clientes y canales.

Etapas:
    1. Extracción de fuentes Excel.
    2. Homologación de Ceve y Canal.
    3. Validación de integridad.
    4. Presentación de resultados.

Este script no modifica los archivos originales.
"""

from src.config.settings import Settings
from src.extractors.excel_extractor import ExcelExtractor
from src.transformers.homologation_transformer import (
    HomologationTransformer,
)
from src.validators.data_validator import DataValidator


def main() -> None:
    """Ejecuta la homologación y sus validaciones."""

    # ---------------------------------------------------------
    # 1. CONFIGURACIÓN
    # ---------------------------------------------------------
    settings = Settings()
    extractor = ExcelExtractor()

    # ---------------------------------------------------------
    # 2. EXTRACCIÓN DE DATOS
    # ---------------------------------------------------------
    print("\n[1/4] EXTRACCIÓN DE DATOS")
    print("-" * 50)

    cases = extractor.extract(
        settings.cases_path,
        settings.cases_sheet,
        "casos",
    )

    clients = extractor.extract(
        settings.master_path,
        settings.clients_sheet,
        "clientes",
    )

    channels = extractor.extract(
        settings.master_path,
        settings.channels_sheet,
        "canales",
    )

    # ---------------------------------------------------------
    # 3. HOMOLOGACIÓN
    # ---------------------------------------------------------
    print("\n[2/4] HOMOLOGACIÓN DE CLIENTES Y CANALES")
    print("-" * 50)

    transformer = HomologationTransformer(
        strict_validation=True,
    )

    result = transformer.transform(
        cases,
        clients,
        channels,
    )

    print(f"Casos originales: {len(cases):,}")
    print(f"Casos transformados: {len(result):,}")

    print("\nDistribución por estado:")
    print(result["Estado_Homologacion"].value_counts(dropna=False).to_string())

    # ---------------------------------------------------------
    # 4. VALIDACIÓN DE INTEGRIDAD
    # ---------------------------------------------------------
    print("\n[3/4] VALIDACIÓN DE INTEGRIDAD")
    print("-" * 50)

    validator = DataValidator()

    validation = validator.validate(
        original=cases,
        transformed=result,
    )

    for metric, value in validation.items():
        if isinstance(value, int) and not isinstance(value, bool):
            print(f"{metric}: {value:,}")
        else:
            print(f"{metric}: {value}")

    # ---------------------------------------------------------
    # 5. RESUMEN
    # ---------------------------------------------------------
    print("\n[4/4] RESULTADO FINAL")
    print("-" * 50)

    total = len(result)
    homologated = int(result["Estado_Homologacion"].eq("HOMOLOGADO").sum())

    coverage = homologated / total * 100 if total > 0 else 0.0

    print(f"Total de casos: {total:,}")
    print(f"Casos homologados: {homologated:,}")
    print(f"Cobertura de homologación: {coverage:.2f}%")

    print("\n[OK] Homologación y validaciones completadas.")


if __name__ == "__main__":
    main()
