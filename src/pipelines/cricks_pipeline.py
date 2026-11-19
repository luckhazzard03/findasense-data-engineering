"""
Findasense - Senior Data Engineer Technical Assessment.

Pipeline de auditoría, transformación y validación
de casos Cricks México.
"""

from src.config.settings import Settings
from src.extractors.excel_extractor import ExcelExtractor
from src.auditors.data_auditor import DataAuditor
from src.transformers.homologation_transformer import (
    HomologationTransformer,
)
from src.transformers.case_classifier import CaseClassifier
from src.transformers.data_cleaner import DataCleaner
from src.validators.data_validator import DataValidator
from src.auditors.quality_report import QualityReport


class CricksPipeline:
    def __init__(self):
        self.settings = Settings()
        self.extractor = ExcelExtractor()
        self.auditor = DataAuditor(self.settings.audit_dir)

        self.homologator = HomologationTransformer(
            strict_validation=True
        )
        self.classifier = CaseClassifier()
        self.cleaner = DataCleaner(strict_validation=True)
        self.validator = DataValidator()

    def extract_sources(self):
        """Extrae las tres fuentes requeridas."""
        s = self.settings

        cases = self.extractor.extract(
            s.cases_path, s.cases_sheet, "casos"
        )
        clients = self.extractor.extract(
            s.master_path, s.clients_sheet, "clientes"
        )
        channels = self.extractor.extract(
            s.master_path, s.channels_sheet, "canales"
        )

        return cases, clients, channels

    def run_audit(self) -> dict:
        """Ejecuta la auditoría existente."""
        cases, clients, channels = self.extract_sources()

        results = {
            "perfil_casos": self.auditor.profile(cases, "casos"),
            "perfil_clientes": self.auditor.profile(
                clients, "clientes"
            ),
            "perfil_canales": self.auditor.profile(
                channels, "canales"
            ),
            "casos": self.auditor.audit_cases(cases),
            "maestro_clientes": self.auditor.audit_master(
                clients
            ),
            "homologacion_canal": self.auditor.audit_channels(
                channels
            ),
        }

        self.auditor.save(results)
        return results

    def run_etl(self, generate_report: bool = True):
        """
        Ejecuta el ETL completo.

        Orden:
        1. Extracción.
        2. Homologación.
        3. Clasificación.
        4. Limpieza.
        5. Validación de integridad.

        Returns:
            tuple: (DataFrame transformado, métricas)
        """

        cases, clients, channels = self.extract_sources()

        # 1. Homologación Ceve + Canal.
        transformed = self.homologator.transform(
            cases, clients, channels
        )

        # 2. Clasificación de quejas.
        transformed = self.classifier.classify(transformed)

        # 3. Preparación de dimensiones y fechas.
        transformed = self.cleaner.transform(transformed)

        # 4. Validación de integridad.
        metrics = self.validator.validate(
            cases, transformed
        )

        # 5. Métricas adicionales de clasificación.
        classification = self.classifier.summarize(
            transformed
        )

        # 6. Métricas de calidad temporal.
        date_quality = self.cleaner.summarize(
            transformed
        )

        metrics["clasificacion"] = classification
        metrics["calidad_fechas"] = date_quality

        # 7. Comprobación del total clasificado.
        if (
            classification["quejas_servicio_ventas"]
            + classification["sin_categoria"]
            + classification["otras_categorias"]
            != len(cases)
        ):
            raise AssertionError(
                "La clasificación no cubre todos los casos."
            )

        # Generación automática de hallazgos.
        # Las pruebas pueden desactivar la escritura en disco.
        if generate_report:
            quality_report = QualityReport(output_dir="docs")
            report = quality_report.generate(
                cases, transformed, metrics
            )
            paths = quality_report.save(report)

            print("\n[QUALITY] Hallazgos actualizados:")
            print(f"[QUALITY] Markdown: {paths['markdown']}")
            print(f"[QUALITY] JSON: {paths['json']}")

        return transformed, metrics
