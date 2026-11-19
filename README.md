# Findasense | Senior Data Engineer Technical Assessment

Proyecto de ingeniería de datos desarrollado para la prueba técnica de Findasense.

## Descripción

Implementación de un pipeline ETL en Python para procesar casos de Cricks México, homologar dimensiones comerciales, clasificar quejas, validar integridad y generar datasets analíticos.

El proyecto contempla también visualización en Power BI y una propuesta de arquitectura de datos en Microsoft Azure.

## Tecnologías

- Python 3.11
- Pandas
- Pytest
- Excel como fuente de datos
- CSV UTF-8 para integración con Power BI
- Power BI (fase de visualización)
- Microsoft Azure (fase de arquitectura propuesta)

## Arquitectura del proyecto

- **Extracción:** `src/extractors/` — Implementado
- **Auditoría:** `src/auditors/` — Implementado
- **Transformación:** `src/transformers/` — Implementado
- **Validación:** `src/validators/` — Implementado
- **Carga y exportación:** `src/loaders/` — Implementado
- **Orquestación:** `src/pipelines/` — Implementado

## Estructura del repositorio

```text
findasense-data-engineering/
- src/
  - auditors
    - __init__.py
    - data_auditor.py
    - homologation_analyzer.py
    - quality_report.py
  - config
    - __init__.py
    - settings.py
  - extractors
    - __init__.py
    - excel_extractor.py
  - loaders
    - __init__.py
    - file_loader.py
    - postgres_loader.py
  - models
    - __init__.py
    - data_models.py
  - pipelines
    - __init__.py
    - cricks_pipeline.py
  - transformers
    - __init__.py
    - case_classifier.py
    - data_cleaner.py
    - homologation_transformer.py
  - utils
    - __init__.py
    - exceptions.py
    - logger.py
  - validators
    - __init__.py
    - data_validator.py
    - schema_validator.py
  - __init__.py
- tests/
  - integration
    - __init__.py
    - test_homologation.py
    - test_pipeline.py
  - unit
    - __init__.py
    - test_auditor.py
    - test_extractor.py
    - test_transformer.py
    - test_validator.py
  - __init__.py
- scripts/
  - analyze_coverage.py
  - analyze_homologation.py
  - generate_readme.py
- docs/
  - data_dictionary.md
  - etl_rules.md
  - execution_guide.md
- powerbi/
  - dax
    - medidas.dax
  - models
    - modelo_estrella.md
- architecture/
  - diagrams
  - documentation
- sql/
  - ddl
    - create_tables.sql
  - queries
    - quality_checks.sql
```

## Instalación

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Las fuentes Excel se configuran mediante las variables de entorno definidas en `.env.example`. El archivo `.env` y los datos originales no deben incorporarse al repositorio público.

## Ejecución del pipeline

### Auditoría de fuentes

```bash
python main.py --stage audit
```

### Transformación y validación

```bash
python main.py --stage etl
```

### Exportación analítica

```bash
python main.py --stage export
```

La etapa de exportación ejecuta el ETL, genera hallazgos de calidad y produce dos vistas CSV en `data/processed/`.

## Controles de calidad

- Conservación del número de registros.
- Validación de identificadores únicos.
- Homologación mediante Ceve y Canal.
- Clasificación de quejas de servicio a ventas.
- Validación de fechas y dimensiones.
- Seguimiento de registros no homologados.
- Generación automática de hallazgos Markdown y JSON.
- Exclusión de datos personales innecesarios en las vistas analíticas.

Los informes detallados se generan localmente en `docs/` y no se publican por defecto.

## Pruebas automatizadas

```bash
python -m pytest tests/ -q
```

Las pruebas cubren clasificación, homologación, limpieza, validación de integridad y exportación.

Las pruebas de integración requieren las fuentes Excel originales configuradas localmente.

## Estado de los entregables

- **Ejecución del ETL:** Implementado
- **Generador de hallazgos:** Implementado
- **Exportador Power BI:** Implementado
- **Dashboard Power BI:** En desarrollo.
- **Diagrama de arquitectura Azure:** Pendiente.
- **Informe formal de inconsistencias:** Pendiente.

## Actualizar esta documentación

```bash
python scripts/generate_readme.py
```

El README se regenera a partir de la estructura y los componentes del repositorio. No incluye métricas confidenciales del negocio.
