-- FINDASENSE | CRICKS MÉXICO
-- Consultas de calidad para PostgreSQL
-- Ejecutar después de cargar el dataset analítico.

-- Q01. Total de registros
SELECT COUNT(*) AS total_casos
FROM analytics.cricks_casos;

-- Q02. Integridad de identificadores
SELECT
    COUNT(*) AS total_registros,
    COUNT(DISTINCT "Número del caso") AS ids_unicos,
    COUNT(*) FILTER (
        WHERE "Número del caso" IS NULL
    ) AS ids_nulos
FROM analytics.cricks_casos;

-- Q03. Distribución de homologación
SELECT
    "Estado_Homologacion",
    COUNT(*) AS casos,
    ROUND(
        100.0 * COUNT(*) / NULLIF(
            (SELECT COUNT(*) FROM analytics.cricks_casos), 0
        ), 2
    ) AS porcentaje
FROM analytics.cricks_casos
GROUP BY "Estado_Homologacion"
ORDER BY casos DESC;

-- Q04. Casos homologados y no homologados
SELECT
    COUNT(*) FILTER (
        WHERE "Estado_Homologacion" = 'HOMOLOGADO'
    ) AS homologados,
    COUNT(*) FILTER (
        WHERE "Estado_Homologacion" IS DISTINCT FROM 'HOMOLOGADO'
    ) AS no_homologados
FROM analytics.cricks_casos;

-- Q05. Categorías faltantes
SELECT COUNT(*) AS casos_sin_categoria
FROM analytics.cricks_casos
WHERE "Categoría" IS NULL
   OR TRIM("Categoría") = '';

-- Q06. Quejas de servicio a ventas
SELECT COUNT(*) AS quejas_servicio_ventas
FROM analytics.cricks_casos
WHERE "Es_Queja_Servicio_Ventas" IS TRUE;

-- Q07. Quejas objetivo sin homologación
SELECT COUNT(*) AS quejas_sin_homologacion
FROM analytics.cricks_casos
WHERE "Es_Queja_Servicio_Ventas" IS TRUE
  AND "Estado_Homologacion" IS DISTINCT FROM 'HOMOLOGADO';

-- Q08. Calidad de fechas de apertura
SELECT
    MIN("Fecha_Apertura_Analitica") AS primera_fecha,
    MAX("Fecha_Apertura_Analitica") AS ultima_fecha,
    COUNT(*) FILTER (
        WHERE "Fecha_Apertura_Analitica" IS NULL
           OR "Fecha_Apertura_Valida" IS NOT TRUE
    ) AS fechas_invalidas
FROM analytics.cricks_casos;

-- Q09. Completitud de dimensiones comerciales
SELECT
    COUNT(*) FILTER (
        WHERE NULLIF(TRIM("Ceve_Original_Limpio"), '') IS NULL
    ) AS sin_ceve,
    COUNT(*) FILTER (
        WHERE NULLIF(TRIM("Canal_Original_Limpio"), '') IS NULL
    ) AS sin_canal,
    COUNT(*) FILTER (
        WHERE NULLIF(TRIM("Gerencia_Ventas_Limpia"), '') IS NULL
    ) AS sin_gerencia_ventas,
    COUNT(*) FILTER (
        WHERE NULLIF(TRIM("Region_Supervisor_Limpia"), '') IS NULL
    ) AS sin_region_supervisor,
    COUNT(*) FILTER (
        WHERE NULLIF(TRIM("Gerencia_Supervisor_Limpia"), '') IS NULL
    ) AS sin_gerencia_supervisor,
    COUNT(*) FILTER (
        WHERE NULLIF(TRIM("Division_Supervisor_Limpia"), '') IS NULL
    ) AS sin_division_supervisor
FROM analytics.cricks_casos;

-- Q10. Distribución mensual
SELECT
    "Anio_Apertura",
    "Mes_Apertura",
    COUNT(*) AS total_casos
FROM analytics.cricks_casos
GROUP BY "Anio_Apertura", "Mes_Apertura"
ORDER BY "Anio_Apertura", "Mes_Apertura";
