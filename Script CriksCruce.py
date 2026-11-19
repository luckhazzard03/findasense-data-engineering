"""
Findasense - Prueba Técnica Data Engineer
Caso: Cricks México

Script CriksCruce
Fase 1: Extracción y auditoría de datos.
"""

import argparse
import json

from src.pipelines.cricks_pipeline import CricksPipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage",
        choices=["audit"],
        default="audit"
    )
    args = parser.parse_args()

    pipeline = CricksPipeline()

    if args.stage == "audit":
        results = pipeline.run_audit()
        print("\nAUDITORÍA FINALIZADA\n")
        print(json.dumps(
            results, indent=2, ensure_ascii=False
        ))


if __name__ == "__main__":
    main()
