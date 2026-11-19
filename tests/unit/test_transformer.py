"""
Findasense - Senior Data Engineer Technical Assessment.

Pruebas unitarias de clasificación y homologación.
Utiliza exclusivamente datos sintéticos.
"""

import pandas as pd
import pytest

from src.transformers.case_classifier import CaseClassifier
from src.transformers.homologation_transformer import (
    HomologationTransformer,
)


class TestCaseClassifier:
    """Pruebas unitarias de clasificación."""

    def test_identifies_target_category(self):
        cases = pd.DataFrame({
            "Número del caso": ["1", "2", "3", "4"],
            "Categoría": [
                "Quejas de servicio a ventas",
                "QUEJAS DE SERVICIO A VENTAS",
                "Quejas de Calidad",
                None,
            ],
        })

        classifier = CaseClassifier()
        result = classifier.classify(cases)
        summary = classifier.summarize(result)

        assert len(result) == 4
        assert summary["quejas_servicio_ventas"] == 2
        assert summary["otras_categorias"] == 1
        assert summary["sin_categoria"] == 1

    def test_normalizes_accents(self):
        classifier = CaseClassifier(
            target_category="Atención de ventas"
        )

        cases = pd.DataFrame({
            "Categoría": ["ATENCION DE VENTAS"]
        })

        result = classifier.classify(cases)

        assert bool(
            result["Es_Queja_Servicio_Ventas"].iloc[0]
        )

    def test_preserves_original_data(self):
        cases = pd.DataFrame({
            "Número del caso": ["101", "102"],
            "Categoría": [
                "Quejas de servicio a ventas",
                "Consultas",
            ],
        })

        original = cases.copy(deep=True)

        result = CaseClassifier().classify(cases)

        pd.testing.assert_frame_equal(cases, original)

        assert result["Número del caso"].equals(
            original["Número del caso"]
        )

        assert result["Categoría"].equals(
            original["Categoría"]
        )

    def test_rejects_missing_category(self):
        cases = pd.DataFrame({
            "Número del caso": ["101"]
        })

        with pytest.raises(ValueError, match="Categoría"):
            CaseClassifier().classify(cases)

    def test_rejects_empty_target(self):
        with pytest.raises(ValueError):
            CaseClassifier(target_category=" ")


class TestHomologationTransformer:
    """Pruebas unitarias del cruce Ceve + Canal."""

    @staticmethod
    def sample_data():
        cases = pd.DataFrame({
            "Número del caso": ["1", "2", "3"],
            "Código de Ceve": ["100", "200", None],
            "Canal de Venta": [
                "TRADICIONAL",
                "MODERNO",
                "TRADICIONAL",
            ],
            "Categoría": [
                "Quejas de servicio a ventas",
                "Consultas",
                "Quejas de Calidad",
            ],
        })

        clients = pd.DataFrame({
            "Código de Ceve": ["100", "200"],
            "CeVeHomo": ["CEVE 100", "CEVE 200"],
            "CanalHomo": ["TRADICIONAL", "MODERNO"],
            "RegionHomo": ["NORTE", "SUR"],
            "GerenciaHomo": ["GERENCIA 1", "GERENCIA 2"],
        })

        channels = pd.DataFrame({
            "Canal de Venta": ["TRADICIONAL", "MODERNO"],
            "Homologación Canal": ["TRADICIONAL", "MODERNO"],
        })

        return cases, clients, channels

    def test_preserves_case_count_and_ids(self):
        cases, clients, channels = self.sample_data()

        transformer = HomologationTransformer(
            strict_validation=True
        )

        result = transformer.transform(
            cases, clients, channels
        )

        assert len(result) == len(cases)

        assert result["Número del caso"].equals(
            cases["Número del caso"]
        )

        assert result["Número del caso"].is_unique

    def test_homologates_matching_cases(self):
        cases, clients, channels = self.sample_data()

        result = HomologationTransformer().transform(
            cases, clients, channels
        )

        assert (
            result["Estado_Homologacion"].tolist()
            == ["HOMOLOGADO", "HOMOLOGADO", "SIN_CEVE"]
        )

        assert result.loc[
            0, "Region_Homologada"
        ] == "NORTE"

        assert result.loc[
            1, "Gerencia_Homologada"
        ] == "GERENCIA 2"

    def test_rejects_ambiguous_master_keys(self):
        cases, clients, channels = self.sample_data()

        conflicting = clients.iloc[[0]].copy()
        conflicting["RegionHomo"] = "OTRA REGION"

        clients = pd.concat(
            [clients, conflicting],
            ignore_index=True
        )

        transformer = HomologationTransformer(
            strict_validation=True
        )

        with pytest.raises(ValueError, match="ambiguas"):
            transformer.transform(
                cases, clients, channels
            )


class TestDataCleaner:
    """Pruebas unitarias de limpieza analítica."""

    @staticmethod
    def sample_data():
        return pd.DataFrame({
            "Número del caso": ["101", "102", "103"],
            "Fecha de apertura": [
                "2024-01-01",
                "2024-02-15",
                "2024-08-12",
            ],
            "Canal de Venta": [
                " TRADICIONAL ",
                "MODERNO",
                None,
            ],
            "Código de Ceve": [
                "100",
                "200",
                None,
            ],
            "Gerencia Ventas": [
                " NORTE ",
                None,
                "SUR",
            ],
            "Región Supervisor": [
                "CENTRO",
                None,
                "NORTE",
            ],
            "Gerencia Supervisor": [
                "GERENCIA 1",
                None,
                "GERENCIA 2",
            ],
            "División Supervisor": [
                "DIVISION A",
                "DIVISION B",
                None,
            ],
        })

    def test_preserves_original_data(self):
        from src.transformers.data_cleaner import DataCleaner

        cases = self.sample_data()
        original = cases.copy(deep=True)

        result = DataCleaner().transform(cases)

        pd.testing.assert_frame_equal(cases, original)

        assert len(result) == len(cases)
        assert result["Número del caso"].equals(
            original["Número del caso"]
        )

    def test_creates_correct_date_dimensions(self):
        from src.transformers.data_cleaner import DataCleaner

        result = DataCleaner().transform(self.sample_data())

        assert result["Periodo_Apertura"].tolist() == [
            "2024-01",
            "2024-02",
            "2024-08",
        ]
        assert result["Anio_Apertura"].tolist() == [
            2024, 2024, 2024
        ]
        assert result["Mes_Apertura"].tolist() == [
            1, 2, 8
        ]
        assert result["Fecha_Apertura_Valida"].all()

    def test_normalizes_dimensions_without_imputation(self):
        from src.transformers.data_cleaner import DataCleaner

        result = DataCleaner().transform(self.sample_data())

        assert result.loc[
            0, "Canal_Original_Limpio"
        ] == "TRADICIONAL"

        assert result.loc[
            0, "Gerencia_Ventas_Limpia"
        ] == "NORTE"

        assert pd.isna(
            result.loc[2, "Ceve_Original_Limpio"]
        )

        assert pd.isna(
            result.loc[2, "Division_Supervisor_Limpia"]
        )

    def test_rejects_invalid_dates_in_strict_mode(self):
        from src.transformers.data_cleaner import DataCleaner

        cases = self.sample_data()
        cases.loc[0, "Fecha de apertura"] = "fecha-invalida"

        with pytest.raises(ValueError, match="fechas"):
            DataCleaner(strict_validation=True).transform(cases)


class TestFileLoader:
    """Pruebas unitarias de exportación para Power BI."""

    @staticmethod
    def sample_data():
        from src.loaders.file_loader import FileLoader

        data = {
            column: [pd.NA, pd.NA, pd.NA]
            for column in FileLoader.COLUMNS
        }

        data["Número del caso"] = ["101", "102", "103"]
        data["Categoría"] = [
            "Quejas de servicio a ventas",
            "Consultas",
            "Quejas de servicio a ventas",
        ]
        data["Es_Queja_Servicio_Ventas"] = [
            True, False, True
        ]
        data["Estado_Homologacion"] = [
            "HOMOLOGADO",
            "SIN_CEVE",
            "SIN_CANAL",
        ]
        data["Fecha_Apertura_Analitica"] = pd.to_datetime([
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
        ])

        return pd.DataFrame(data)

    def test_exports_correct_record_counts(self, tmp_path):
        from src.loaders.file_loader import FileLoader

        loader = FileLoader(output_dir=tmp_path)
        metrics = loader.export(self.sample_data())

        assert metrics["casos_exportados"] == 3
        assert metrics["quejas_exportadas"] == 2
        assert metrics["integridad_exportacion"] is True

    def test_exports_only_allowed_columns(self, tmp_path):
        from src.loaders.file_loader import FileLoader

        data = self.sample_data()
        data["Nombre del cliente"] = [
            "Cliente A", "Cliente B", "Cliente C"
        ]

        metrics = FileLoader(tmp_path).export(data)

        exported = pd.read_csv(
            metrics["archivo_casos"],
            nrows=0,
        )

        assert exported.columns.tolist() == FileLoader.COLUMNS
        assert "Nombre del cliente" not in exported.columns

    def test_preserves_unmatched_complaints(self, tmp_path):
        from src.loaders.file_loader import FileLoader

        metrics = FileLoader(tmp_path).export(
            self.sample_data()
        )

        complaints = pd.read_csv(
            metrics["archivo_quejas"],
            dtype={"Número del caso": "string"},
        )

        assert len(complaints) == 2
        assert set(complaints["Número del caso"]) == {
            "101", "103"
        }
        assert set(complaints["Estado_Homologacion"]) == {
            "HOMOLOGADO", "SIN_CANAL"
        }

    def test_rejects_duplicate_ids(self, tmp_path):
        from src.loaders.file_loader import FileLoader

        data = self.sample_data()
        data.loc[1, "Número del caso"] = "101"

        with pytest.raises(ValueError, match="duplicados"):
            FileLoader(tmp_path).export(data)
