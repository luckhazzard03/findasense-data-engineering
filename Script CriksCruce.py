"""
Findasense - Prueba Técnica Senior Data Engineer.

Caso: Cricks México.

Etapas:
    audit: auditoría de fuentes.
    etl: transformación, validación e informe de calidad.
    export: ETL completo y exportación para Power BI.
"""

import argparse
import json

from src.pipelines.cricks_pipeline import CricksPipeline
from src.loaders.file_loader import FileLoader


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline Cricks México"
    )

    parser.add_argument(
        "--stage",
        choices=["audit", "etl", "export"],
        default="audit",
        help="Etapa del procesamiento",
    )

    args = parser.parse_args()
    pipeline = CricksPipeline()

    if args.stage == "audit":
        results = pipeline.run_audit()
        print("\nAUDITORÍA FINALIZADA\n")

    elif args.stage == "etl":
        _, results = pipeline.run_etl()
        print("\nETL FINALIZADO Y VALIDADO\n")

    else:
        data, etl_metrics = pipeline.run_etl()

        loader = FileLoader()
        export_metrics = loader.export(data)

        results = {
            "etl": etl_metrics,
            "exportacion": export_metrics,
        }

        print("\nEXPORTACIÓN FINALIZADA Y VALIDADA\n")

    print(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
