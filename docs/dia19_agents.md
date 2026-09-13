# AgroField AI — Día 19: Primeros agentes especializados

## Soil Agent (`agents/soil_agent.py`)

* **Propósito**: Recibir datos crudos de propiedades físicas y químicas del suelo e interpretar su viabilidad para el cultivo de papa, transformando variables numéricas en recomendaciones agronómicas.
* **Entrada**: Diccionario de datos retornado por `get_soil_data()` (ej. `phh2o`, `soc`, `sand`, `silt`, `clay`).
* **Procesamiento**:
  * Interpreta el pH, recomendando encalado si es necesario.
  * Interpreta el Carbono Orgánico del Suelo (SOC) para valorar materia orgánica.
  * Clasifica la textura del suelo basada en los porcentajes de Arena, Limo y Arcilla.
  * Consolida hallazgos en notas agronómicas.
* **Salida**: Un diccionario JSON con resumen textual (`summary`), y las interpretaciones por cada variable junto con recomendaciones genéricas (`agronomic_notes`).
* **Fuente de datos**: Función conectada a SoilGrids (`src/data/soilgrids_client.py`).

### Ejemplo de ejecución real:
```json
{
  "summary": "Análisis de suelo completado para la capa 15-30cm. Evaluadas 3 variables. Las condiciones generales deben interpretarse junto con el régimen climático para decisiones de abonado.",
  "ph_interpretation": "Ligeramente alcalino. Aceptable pero vigilar la disponibilidad de micronutrientes.",
  "organic_carbon_interpretation": "Contenido medio a adecuado de materia orgánica.",
  "texture_interpretation": "Textura franca a franco-arenosa. Ideal para el desarrollo radicular y expansión de tubérculos de papa.",
  "agronomic_notes": [
    "pH actual: 6.60 - Ligeramente alcalino. Aceptable pero vigilar la disponibilidad de micronutrientes.",
    "Carbono orgánico: 3.19% - Contenido medio a adecuado de materia orgánica.",
    "Textura (Arena: 48.5%, Limo: 33.2%, Arcilla: 18.3%) - Textura franca a franco-arenosa. Ideal para el desarrollo radicular y expansión de tubérculos de papa."
  ]
}
```

## Climate Agent (`agents/climate_agent.py`)

* **Propósito**: Evaluar las condiciones climáticas históricas utilizando los datos recogidos de NASA POWER para establecer el favor o los riesgos climáticos en un periodo o contexto.
* **Entrada**: Un `pandas.DataFrame` con variables como `T2M`, `PRECTOTCORR`, `VPD` (y opcional `RH2M`).
* **Procesamiento**:
  * Resume estadísticas climáticas ignorando valores faltantes.
  * Interpreta el rango promedio de T2M (Temperatura).
  * Evalúa el déficit o exceso de lluvia promediando `PRECTOTCORR`.
  * Interpreta el Déficit de Presión de Vapor (VPD) en torno al comportamiento estomático de la planta.
* **Salida**: Un diccionario JSON con resúmenes por cada factor e información agronómica de riesgos (ej. Tizón tardío por humedad).
* **Fuente de datos**: Módulo `pipeline_dia6.py` y archivos de origen generados en `data/processed/nasa_power_colta_12m_vpd_20250823_20260822.csv`.

### Ejemplo de ejecución real:
```json
{
  "summary": "Análisis climático completado para 365 días (desde 2025-08-23 hasta 2026-08-22).",
  "temperature_interpretation": "Temperatura óptima (11.4°C) para tuberización y desarrollo. Buen vigor esperado.",
  "precipitation_interpretation": "Exceso de lluvias (5.0 mm/día). Riesgo de encharcamiento y proliferación de Tizón tardío.",
  "vpd_interpretation": "VPD muy bajo (0.17 kPa). Transpiración limitada, alta humedad propicia para enfermedades.",
  "agronomic_notes": [
    "Rango de temperatura: de 9.3°C a 13.7°C",
    "Precipitación acumulada: 1835.2 mm en 365 días",
    "VPD promedio: 0.17 kPa, máximo: 0.28 kPa",
    "Humedad Relativa promedio: 87.1%"
  ]
}
```

## Decisiones Arquitectónicas (Día 19)

1. **Separación de precesamiento técnico vs interpretativo:** Los algoritmos de extracción (ej. EE/SoilGrids) se mantienen en `src/data/`, mientras que la interpretación holística es responsabilidad exclusiva de la carpeta `agents/`.
2. **Entradas adaptables:** Para la capa de Soil, el agente lee un diccionario debido a que son datos puntuales (`lat/lon`). Para Climate, se usa un `pandas.DataFrame` dado el enfoque como datos en serie temporal.
3. Se han respetado estrictamente las funciones de validación previas sin duplicar lógica base como el cálculo de VPD de un `DataFrame`.
