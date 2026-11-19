import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    root: Path = ROOT

    @property
    def cases_path(self) -> Path:
        return self.root / os.getenv(
            "BASE_CASOS_FILE", "data/raw/Base Casos.xlsx"
        )

    @property
    def master_path(self) -> Path:
        return self.root / os.getenv(
            "MAESTRO_CLIENTES_FILE", "data/raw/MaestroClientes.xlsx"
        )

    @property
    def cases_sheet(self) -> str:
        return os.getenv("BASE_CASOS_SHEET", "Sheet1")

    @property
    def clients_sheet(self) -> str:
        return os.getenv(
            "MAESTRO_CLIENTES_SHEET", "Maestro de Clientes"
        )

    @property
    def channels_sheet(self) -> str:
        return os.getenv(
            "HOMOLOGACION_CANAL_SHEET", "Homologación Canal"
        )

    @property
    def audit_dir(self) -> Path:
        return self.root / os.getenv(
            "AUDIT_DIR", "reports/audits"
        )
