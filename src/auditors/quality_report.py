"""
Generación automática de hallazgos de calidad de datos.

Produce informes Markdown y JSON a partir del ETL.
No utiliza cantidades fijas ni modifica el dataset.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


class QualityReport:
    """Construye hallazgos reproducibles desde los datos."""

    def __init__(self, output_dir="docs"):
        self.output_dir = Path(output_dir)

    @staticmethod
    def _percentage(value, total):
        return round(value / total * 100, 2) if total else 0.0

    @staticmethod
    def _missing(series):
        text = series.astype("string").str.strip()
        return int(
            (
                text.isna()
                | text.str.casefold()
                .isin(["", "nan", "none", "null", "nat"])
                .fillna(False)
            ).sum()
        )

    def generate(self, original, transformed, metrics):
        total = len(original)

        if len(transformed) != total:
            raise ValueError(
                "No se puede generar el informe: "
                "los totales originales y transformados difieren."
            )

        findings = []

        def add(code, title, severity, count, description,
                impact, recommendation):
            findings.append({
                "codigo": code,
                "titulo": title,
                "severidad": severity,
                "casos": int(count),
                "porcentaje": self._percentage(count, total),
                "descripcion": description,
                "impacto": impact,
                "recomendacion": recommendation,
            })

        # H-001: Estados excluyentes de homologación.
        statuses = (
            transformed["Estado_Homologacion"]
            .value_counts(dropna=False)
            .to_dict()
        )

        unmatched = int(
            transformed["Estado_Homologacion"]
            .ne("HOMOLOGADO")
            .sum()
        )

        detail = ", ".join(
            f"{key}: {value:,}"
            for key, value in statuses.items()
            if key != "HOMOLOGADO"
        )

        add(
            "H-001",
            "Cobertura insuficiente de homologación",
            "ALTA" if unmatched / max(total, 1) > 0.2 else "MEDIA",
            unmatched,
            f"Estados sin homologación: {detail}.",
            "Limita el análisis por dimensiones homologadas.",
            "Corregir datos de Ceve y Canal y revisar "
            "las correspondencias faltantes.",
        )

        # H-002: Categorías faltantes.
        missing_category = self._missing(original["Categoría"])

        add(
            "H-002",
            "Categorías no informadas",
            "ALTA" if missing_category / max(total, 1) > 0.1
            else "MEDIA",
            missing_category,
            "Casos con Categoría vacía o no informada.",
            "No pueden clasificarse con certeza en "
            "la categoría objetivo.",
            "Validar la captura de categorías y revisar "
            "los registros históricos.",
        )

        # H-003: Cobertura temporal.
        dates = pd.to_datetime(
            transformed["Fecha_Apertura_Analitica"],
            errors="coerce",
        )

        first = dates.min()
        last = dates.max()

        partial_month = 0
        if pd.notna(last):
            last_day = last.days_in_month
            if last.day < last_day:
                partial_month = int(
                    dates.dt.to_period("M")
                    .eq(last.to_period("M"))
                    .sum()
                )

        add(
            "H-003",
            "Cobertura temporal del dataset",
            "INFORMATIVA",
            partial_month,
            f"Primera fecha: {first}; última fecha: {last}. "
            "Los registros contabilizados corresponden "
            "al último mes observado, que termina antes "
            "del último día calendario; no representan "
            "fechas inválidas."
            if partial_month else
            f"Primera fecha: {first}; última fecha: {last}.",
            "La cobertura disponible no debe interpretarse "
            "automáticamente como un año completo.",
            "Mostrar el rango de fechas disponible "
            "y señalar el último mes como parcial "
            "cuando corresponda.",
        )

        # H-004: Completitud de dimensiones originales.
        dimensions = [
            "Código de Ceve",
            "Canal de Venta",
            "Gerencia Ventas",
            "Región Supervisor",
            "Gerencia Supervisor",
            "División Supervisor",
        ]

        dimension_quality = {}

        for column in dimensions:
            if column not in original.columns:
                raise ValueError(
                    f"Falta la dimensión requerida: {column}"
                )

            count = self._missing(original[column])
            dimension_quality[column] = {
                "nulos": count,
                "porcentaje": self._percentage(count, total),
            }

        missing_masks = []

        for column in dimensions:
            values = original[column].astype("string").str.strip()
            missing_masks.append(
                values.isna()
                | values.str.casefold()
                .isin(["", "nan", "none", "null", "nat"])
                .fillna(False)
            )

        any_dimension_missing = int(
            pd.concat(missing_masks, axis=1)
            .any(axis=1)
            .sum()
        )

        detail_dimensions = "; ".join(
            f"{name}: {info['nulos']:,} "
            f"({info['porcentaje']}%)"
            for name, info in dimension_quality.items()
        )

        add(
            "H-004",
            "Valores faltantes en dimensiones",
            "ALTA" if any_dimension_missing / max(total, 1) > 0.2
            else "MEDIA",
            any_dimension_missing,
            "Casos con al menos una dimensión faltante. "
            + detail_dimensions,
            "Reduce la cobertura de segmentaciones.",
            "Implementar controles de obligatoriedad "
            "y completitud por dimensión.",
        )

        # H-005: Fecha de cierre faltante.
        missing_close = self._missing(
            original["Fecha de cierre"]
        )

        add(
            "H-005",
            "Fechas de cierre no informadas",
            "POR_EVALUAR",
            missing_close,
            "Casos sin fecha de cierre.",
            "No se puede calcular el tiempo de resolución "
            "para todos los casos. No implica por sí solo "
            "que estén abiertos.",
            "Contrastar con el estado de los casos.",
        )

        # H-006: Cobertura de homologación en quejas objetivo.
        target = transformed["Es_Queja_Servicio_Ventas"].fillna(
            False
        ).astype(bool)

        target_total = int(target.sum())
        target_unmatched = int(
            (
                target
                & transformed["Estado_Homologacion"]
                .ne("HOMOLOGADO")
            ).sum()
        )

        findings.append({
            "codigo": "H-006",
            "titulo": "Quejas objetivo sin homologación",
            "severidad": "ALTA"
            if target_unmatched / max(target_total, 1) > 0.2
            else "MEDIA",
            "casos": target_unmatched,
            "porcentaje": self._percentage(
                target_unmatched, target_total
            ),
            "denominador": target_total,
            "descripcion": (
                "Quejas de servicio a ventas sin homologación "
                "completa."
            ),
            "impacto": (
                "Las segmentaciones homologadas no cubren "
                "todas las quejas objetivo."
            ),
            "recomendacion": (
                "Mostrar cobertura de homologación en Power BI "
                "y conservar los casos sin correspondencia."
            ),
        })

        report = {
            "generado_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "total_casos": total,
            "metricas_etl": metrics,
            "estados_homologacion": {
                str(k): int(v)
                for k, v in statuses.items()
            },
            "completitud_dimensiones": dimension_quality,
            "hallazgos": findings,
        }

        return report

    def save(self, report):
        self.output_dir.mkdir(
            parents=True, exist_ok=True
        )

        json_path = (
            self.output_dir / "hallazgos_calidad_datos.json"
        )
        md_path = (
            self.output_dir / "hallazgos_calidad_datos.md"
        )

        json_path.write_text(
            json.dumps(
                report,
                ensure_ascii=False,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        lines = [
            "# Informe automático de calidad de datos",
            "",
            "**Caso:** Cricks México",
            "",
            f"**Generado (UTC):** {report['generado_utc']}",
            "",
            f"**Registros analizados:** "
            f"{report['total_casos']:,}",
            "",
            "Este documento se genera automáticamente "
            "a partir del ETL.",
            "",
            "## Hallazgos",
            "",
        ]

        for finding in report["hallazgos"]:
            lines.extend([
                f"### {finding['codigo']}. "
                f"{finding['titulo']}",
                "",
                f"**Severidad:** {finding['severidad']}",
                "",
                f"**Registros:** {finding['casos']:,}",
                "",
                f"**Porcentaje:** {finding['porcentaje']}%",
                "",
                f"**Evidencia:** {finding['descripcion']}",
                "",
                f"**Impacto:** {finding['impacto']}",
                "",
                f"**Recomendación:** "
                f"{finding['recomendacion']}",
                "",
            ])

        lines.extend([
            "## Controles del ETL",
            "",
            "```json",
            json.dumps(
                report["metricas_etl"],
                ensure_ascii=False,
                indent=2,
                default=str,
            ),
            "```",
            "",
        ])

        md_path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        return {
            "markdown": str(md_path),
            "json": str(json_path),
        }
