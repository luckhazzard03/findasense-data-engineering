"""
Genera automáticamente el README principal del repositorio.

Documenta la estructura y capacidades del proyecto sin
publicar datos de negocio, archivos privados ni credenciales.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MODULES = {
    "Extracción": "src/extractors",
    "Auditoría": "src/auditors",
    "Transformación": "src/transformers",
    "Validación": "src/validators",
    "Carga y exportación": "src/loaders",
    "Orquestación": "src/pipelines",
}

DELIVERABLES = [
    ("ETL de Cricks México", "src/pipelines/cricks_pipeline.py"),
    ("Generador de hallazgos", "src/auditors/quality_report.py"),
    ("Exportador Power BI", "src/loaders/file_loader.py"),
]

PRIVATE_DIRS = {
    ".git", ".venv", "__pycache__", ".pytest_cache",
    "raw", "processed", "quality", "audits",
}

PRIVATE_FILES = {
    ".env",
    "hallazgos_calidad_datos.json",
    "hallazgos_calidad_datos.md",
}


def tree(directory, depth=0, max_depth=2):
    if depth > max_depth or not directory.exists():
        return []

    result = []

    for path in sorted(
        directory.iterdir(),
        key=lambda p: (p.is_file(), p.name.lower()),
    ):
        if path.name in PRIVATE_DIRS:
            continue

        if path.name in PRIVATE_FILES:
            continue

        if path.name.startswith("."):
            continue

        if path.suffix in {
            ".xlsx", ".xls", ".csv", ".pbix", ".pdf",
            ".json", ".pyc",
        }:
            continue

        prefix = "  " * depth
        result.append(f"{prefix}- {path.name}")

        if path.is_dir():
            result.extend(
                tree(path, depth + 1, max_depth)
            )

    return result


def generate():
    sections = [
        "# Findasense | Senior Data Engineer Technical Assessment",
        "",
        "Proyecto de ingeniería de datos desarrollado para "
        "la prueba técnica de Findasense.",
        "",
        "## Descripción",
        "",
        "Implementación de un pipeline ETL en Python para "
        "procesar casos de Cricks México, homologar "
        "dimensiones comerciales, clasificar quejas, "
        "validar integridad y generar datasets analíticos.",
        "",
        "El proyecto contempla también visualización "
        "en Power BI y una propuesta de arquitectura "
        "de datos en Microsoft Azure.",
        "",
        "## Tecnologías",
        "",
        "- Python 3.11",
        "- Pandas",
        "- Pytest",
        "- Excel como fuente de datos",
        "- CSV UTF-8 para integración con Power BI",
        "- Power BI (fase de visualización)",
        "- Microsoft Azure (fase de arquitectura propuesta)",
        "",
        "## Arquitectura del proyecto",
        "",
    ]

    for label, relative in MODULES.items():
        path = ROOT / relative
        status = "Implementado" if path.exists() else "Pendiente"
        sections.append(
            f"- **{label}:** `{relative}/` — {status}"
        )

    sections.extend([
        "",
        "## Estructura del repositorio",
        "",
        "```text",
        "findasense-data-engineering/",
    ])

    for folder in ["src", "tests", "scripts", "docs",
                   "powerbi", "architecture", "sql"]:
        path = ROOT / folder
        if path.exists():
            sections.append(f"- {folder}/")
            sections.extend(
                tree(path, depth=1, max_depth=2)
            )

    sections.extend([
        "```",
        "",
        "## Instalación",
        "",
        "```bash",
        "python3.11 -m venv .venv",
        "source .venv/bin/activate",
        "pip install -r requirements.txt",
        "```",
        "",
        "Las fuentes Excel se configuran mediante las "
        "variables de entorno definidas en `.env.example`. "
        "El archivo `.env` y los datos originales no "
        "deben incorporarse al repositorio público.",
        "",
        "## Ejecución del pipeline",
        "",
        "### Auditoría de fuentes",
        "",
        "```bash",
        'python "Script CriksCruce.py" --stage audit',
        "```",
        "",
        "### Transformación y validación",
        "",
        "```bash",
        'python "Script CriksCruce.py" --stage etl',
        "```",
        "",
        "### Exportación analítica",
        "",
        "```bash",
        'python "Script CriksCruce.py" --stage export',
        "```",
        "",
        "La etapa de exportación ejecuta el ETL, genera "
        "hallazgos de calidad y produce dos vistas CSV "
        "en `data/processed/`.",
        "",
        "## Controles de calidad",
        "",
        "- Conservación del número de registros.",
        "- Validación de identificadores únicos.",
        "- Homologación mediante Ceve y Canal.",
        "- Clasificación de quejas de servicio a ventas.",
        "- Validación de fechas y dimensiones.",
        "- Seguimiento de registros no homologados.",
        "- Generación automática de hallazgos Markdown y JSON.",
        "- Exclusión de datos personales innecesarios "
        "en las vistas analíticas.",
        "",
        "Los informes detallados se generan localmente "
        "en `docs/` y no se publican por defecto.",
        "",
        "## Pruebas automatizadas",
        "",
        "```bash",
        "python -m pytest tests/ -q",
        "```",
        "",
        "Las pruebas cubren clasificación, homologación, "
        "limpieza, validación de integridad y exportación.",
        "",
        "Las pruebas de integración requieren las fuentes "
        "Excel originales configuradas localmente.",
        "",
        "## Estado de los entregables",
        "",
    ])

    for label, relative in DELIVERABLES:
        status = (
            "Implementado"
            if (ROOT / relative).is_file()
            else "Pendiente"
        )
        sections.append(f"- **{label}:** {status}")

    sections.extend([
        "- **Dashboard Power BI:** En desarrollo.",
        "- **Diagrama de arquitectura Azure:** Pendiente.",
        "- **Informe formal de inconsistencias:** Pendiente.",
        "",
        "## Actualizar esta documentación",
        "",
        "```bash",
        "python scripts/generate_readme.py",
        "```",
        "",
        "El README se regenera a partir de la estructura "
        "y los componentes del repositorio. "
        "No incluye métricas confidenciales del negocio.",
        "",
    ])

    output = ROOT / "README.md"
    output.write_text(
        "\n".join(sections),
        encoding="utf-8",
    )

    print(f"[DOCS] README actualizado: {output}")
    print(f"[DOCS] Secciones generadas: {len(sections)} líneas")


if __name__ == "__main__":
    generate()
