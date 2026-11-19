import json
from pathlib import Path

from src.config.settings import Settings
from src.extractors.excel_extractor import ExcelExtractor
from src.auditors.homologation_analyzer import (
    HomologationAnalyzer
)


def main():
    settings = Settings()
    extractor = ExcelExtractor()

    cases = extractor.extract(
        settings.cases_path,
        settings.cases_sheet,
        "casos"
    )

    clients = extractor.extract(
        settings.master_path,
        settings.clients_sheet,
        "clientes"
    )

    channels = extractor.extract(
        settings.master_path,
        settings.channels_sheet,
        "canales"
    )

    analyzer = HomologationAnalyzer(
        Path("reports/audits")
    )

    result = analyzer.analyze(
        cases, clients, channels
    )

    print(json.dumps(
        result, indent=2, ensure_ascii=False
    ))


if __name__ == "__main__":
    main()
