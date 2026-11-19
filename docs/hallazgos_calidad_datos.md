# Informe automático de calidad de datos

**Caso:** Cricks México

**Generado (UTC):** 2026-11-19T13:41:08.931554+00:00

**Registros analizados:** 104,675

Este documento se genera automáticamente a partir del ETL.

## Hallazgos

### H-001. Cobertura insuficiente de homologación

**Severidad:** ALTA

**Registros:** 54,001

**Porcentaje:** 51.59%

**Evidencia:** Estados sin homologación: SIN_CEVE: 48,891, SIN_CANAL: 4,925, SIN_COINCIDENCIA: 180, CANAL_NO_HOMOLOGADO: 5.

**Impacto:** Limita el análisis por dimensiones homologadas.

**Recomendación:** Corregir datos de Ceve y Canal y revisar las correspondencias faltantes.

### H-002. Categorías no informadas

**Severidad:** ALTA

**Registros:** 28,054

**Porcentaje:** 26.8%

**Evidencia:** Casos con Categoría vacía o no informada.

**Impacto:** No pueden clasificarse con certeza en la categoría objetivo.

**Recomendación:** Validar la captura de categorías y revisar los registros históricos.

### H-003. Cobertura temporal del dataset

**Severidad:** INFORMATIVA

**Registros:** 5,005

**Porcentaje:** 4.78%

**Evidencia:** Primera fecha: 2024-01-01 00:00:00; última fecha: 2024-08-12 00:00:00. Los registros contabilizados corresponden al último mes observado, que termina antes del último día calendario; no representan fechas inválidas.

**Impacto:** La cobertura disponible no debe interpretarse automáticamente como un año completo.

**Recomendación:** Mostrar el rango de fechas disponible y señalar el último mes como parcial cuando corresponda.

### H-004. Valores faltantes en dimensiones

**Severidad:** ALTA

**Registros:** 80,375

**Porcentaje:** 76.79%

**Evidencia:** Casos con al menos una dimensión faltante. Código de Ceve: 48,891 (46.71%); Canal de Venta: 52,322 (49.99%); Gerencia Ventas: 77,485 (74.02%); Región Supervisor: 49,170 (46.97%); Gerencia Supervisor: 49,177 (46.98%); División Supervisor: 52,883 (50.52%)

**Impacto:** Reduce la cobertura de segmentaciones.

**Recomendación:** Implementar controles de obligatoriedad y completitud por dimensión.

### H-005. Fechas de cierre no informadas

**Severidad:** POR_EVALUAR

**Registros:** 60,948

**Porcentaje:** 58.23%

**Evidencia:** Casos sin fecha de cierre.

**Impacto:** No se puede calcular el tiempo de resolución para todos los casos. No implica por sí solo que estén abiertos.

**Recomendación:** Contrastar con el estado de los casos.

### H-006. Quejas objetivo sin homologación

**Severidad:** MEDIA

**Registros:** 10,379

**Porcentaje:** 17.84%

**Evidencia:** Quejas de servicio a ventas sin homologación completa.

**Impacto:** Las segmentaciones homologadas no cubren todas las quejas objetivo.

**Recomendación:** Mostrar cobertura de homologación en Power BI y conservar los casos sin correspondencia.

## Controles del ETL

```json
{
  "total_original": 104675,
  "total_transformado": 104675,
  "ids_unicos": 104675,
  "homologados": 50674,
  "no_homologados": 54001,
  "integridad_validada": true,
  "clasificacion": {
    "total_casos": 104675,
    "quejas_servicio_ventas": 58183,
    "sin_categoria": 28054,
    "otras_categorias": 18438
  },
  "calidad_fechas": {
    "total_casos": 104675,
    "fechas_validas": 104675,
    "fechas_invalidas_o_nulas": 0,
    "fecha_minima": "2024-01-01",
    "fecha_maxima": "2024-08-12"
  }
}
```
