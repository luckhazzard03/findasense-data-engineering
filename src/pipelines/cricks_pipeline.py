from src.config.settings import Settings
from src.extractors.excel_extractor import ExcelExtractor
from src.auditors.data_auditor import DataAuditor


class CricksPipeline:
    def __init__(self):
        self.settings = Settings()
        self.extractor = ExcelExtractor()
        self.auditor = DataAuditor(self.settings.audit_dir)

    def run_audit(self) -> dict:
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
            )
        }

        self.auditor.save(results)
        return results
