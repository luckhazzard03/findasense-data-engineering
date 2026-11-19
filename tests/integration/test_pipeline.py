"""
Pruebas de integración del pipeline Cricks México.

Estas pruebas utilizan las fuentes Excel reales disponibles
en data/raw y verifican los resultados del proceso ETL.
"""

import pytest

from src.pipelines.cricks_pipeline import CricksPipeline


@pytest.fixture(scope="module")
def etl_result():
    pipeline = CricksPipeline()
    return pipeline.run_etl(generate_report=False)


class TestCricksPipeline:

    def test_preserves_all_records(self, etl_result):
        data, metrics = etl_result

        assert len(data) == 104675
        assert metrics["total_original"] == 104675
        assert metrics["total_transformado"] == 104675
        assert metrics["integridad_validada"] is True

    def test_preserves_unique_ids(self, etl_result):
        data, metrics = etl_result

        assert data["Número del caso"].is_unique
        assert data["Número del caso"].notna().all()
        assert metrics["ids_unicos"] == 104675

    def test_homologation_results(self, etl_result):
        data, metrics = etl_result

        assert metrics["homologados"] == 50674
        assert metrics["no_homologados"] == 54001

        assert (
            data["Estado_Homologacion"]
            .value_counts()
            .sum()
        ) == len(data)

    def test_classification_results(self, etl_result):
        data, metrics = etl_result

        classification = metrics["clasificacion"]

        assert classification["quejas_servicio_ventas"] == 58183
        assert classification["sin_categoria"] == 28054
        assert classification["otras_categorias"] == 18438

        assert int(
            data["Es_Queja_Servicio_Ventas"].sum()
        ) == 58183

    def test_date_quality(self, etl_result):
        data, metrics = etl_result

        quality = metrics["calidad_fechas"]

        assert quality["fechas_validas"] == 104675
        assert quality["fechas_invalidas_o_nulas"] == 0
        assert quality["fecha_minima"] == "2024-01-01"
        assert quality["fecha_maxima"] == "2024-08-12"

        assert data["Fecha_Apertura_Analitica"].notna().all()

    def test_required_analytical_dimensions(self, etl_result):
        data, _ = etl_result

        required = [
            "Estado_Homologacion",
            "Ceve_Homologado",
            "Canal_Maestro",
            "Region_Homologada",
            "Gerencia_Homologada",
            "Division_Supervisor_Limpia",
            "Fecha_Apertura_Analitica",
            "Periodo_Apertura",
            "Es_Queja_Servicio_Ventas",
        ]

        missing = [
            column for column in required
            if column not in data.columns
        ]

        assert not missing, f"Faltan columnas: {missing}"
