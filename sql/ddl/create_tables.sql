-- FINDASENSE | CRICKS MÉXICO
-- PostgreSQL - Estructura analítica
-- Fuente: FileLoader.COLUMNS

CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.cricks_casos (
    "Número del caso" TEXT PRIMARY KEY,
    "Categoría" TEXT,
    "Subcategoría" TEXT,
    "Estado" TEXT,
    "Estado (campo salesforce)" TEXT,
    "Fecha_Apertura_Analitica" DATE,
    "Anio_Apertura" INTEGER,
    "Mes_Apertura" INTEGER,
    "Dia_Apertura" INTEGER,
    "Trimestre_Apertura" INTEGER,
    "Periodo_Apertura" TEXT,
    "Fecha_Apertura_Valida" BOOLEAN,
    "Es_Queja_Servicio_Ventas" BOOLEAN,
    "Estado_Clasificacion" TEXT,
    "Estado_Homologacion" TEXT,
    "Ceve_Homologado" TEXT,
    "Canal_Maestro" TEXT,
    "Region_Homologada" TEXT,
    "Gerencia_Homologada" TEXT,
    "Division_Supervisor_Limpia" TEXT,
    "Canal_Original_Limpio" TEXT,
    "Ceve_Original_Limpio" TEXT,
    "Gerencia_Ventas_Limpia" TEXT,
    "Region_Supervisor_Limpia" TEXT,
    "Gerencia_Supervisor_Limpia" TEXT
);

CREATE INDEX IF NOT EXISTS idx_cricks_fecha
ON analytics.cricks_casos ("Fecha_Apertura_Analitica");

CREATE INDEX IF NOT EXISTS idx_cricks_homologacion
ON analytics.cricks_casos ("Estado_Homologacion");

CREATE INDEX IF NOT EXISTS idx_cricks_categoria
ON analytics.cricks_casos ("Categoría");

CREATE INDEX IF NOT EXISTS idx_cricks_canal
ON analytics.cricks_casos ("Canal_Maestro");
