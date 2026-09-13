# AgroField AI — Día 20: Integración de Datos y Análisis Estadístico

## Objetivo
Implementar una capa intermedia funcional, reproducible y rigurosa compuesta por un **Data Agent** y un **Statistics Agent**, logrando la consolidación de tres fuentes inconexas (satélite, clima y suelo) en un único dataset analítico que permita la ejecución de procedimientos paramétricos unificados.

## Fuentes de Datos Integradas
1. **Satélite (Sentinel-2):** Observaciones fenológicas extraídas mediante Google Earth Engine (`EarthEngineExtractor`). Naturaleza: temporal esporádica (dependiente del paso del satélite y cobertura de nubes). Variables clave: `NDVI`, `NDWI`.
2. **Clima (NASA POWER):** Mediciones diarias históricas climáticas procesadas del cantón Colta. Naturaleza: temporal continua. Variables clave: `T2M`, `PRECTOTCORR`, `VPD`.
3. **Suelo (SoilGrids / ISRIC):** Propiedades edafológicas extraídas por coordenada de área. Naturaleza: espacial constante (asumidas estáticas a corto o mediano plazo para una profundidad específica de 15-30cm). Variables clave: `pH`, `SOC`, texturas.

## Unidad de Observación
Una fila (observación) en el dataset integrado representa:
> **Un día calendario específico en el que existió un paso útil del satélite Sentinel-2**, complementado transversalmente con la climatología exacta ocurrida durante esas mismas 24 horas (`Exact Date`), e incluyendo el contexto base del suelo de la sub-región evaluada.

## Estrategia de Integración
La estrategia implementada en el `Data Agent` sigue un enfoque relacional "Left Join" anclado al satélite:
1. **Temporalidad Base:** Se asume el calendario de Sentinel-2 como el *master index*, debido a que tiene la menor frecuencia (es el dato limitante).
2. **Merge Climático:** Se interceptan mediante cruce por fecha exacta las métricas diarias de precipitaciones y temperaturas de NASA POWER correspondientes intrínsecamente.
3. **Broadcast Espacial:** Las propiedades del SoilGrids se proyectan como variables estáticas/constantes aplicadas a lo largo de toda la matriz, asumiendo su invariabilidad a escala interanual para el propósito.

## Data Agent
Reside en `agents/data_agent.py`.
- **Inputs:** `satellite_df`, `climate_df`, `soil_data` (diccionario).
- **Tratamiento temporal:** Remueve horas utilizando `dt.normalize()` sobre la variable `fecha`/'date' asegurando una correspondencia fiel del día. Previene duplicados.
- **Output:** Devuelve una tupla que contiene el dataset integrado `(DataFrame)` más un reporte de calidad `(QA Report)` dictando colisiones o NaNs surgidos post-cruce.

## Statistics Agent
Reside en `agents/statistics_agent.py`.
- Recibe el dataset ensamblado del Data Agent.
- Filtra algorítmicamente y elimina las variables **constantes** (por ejemplo, los valores fijos del suelo inyectados por el Data Agent) advirtiendo sobre ello, a fin de evitar divisiones por cero (`NaN`) al aplicar varianzas.
- Calcula estadísticas descriptivas agrupadas (mean, std, ranges).
- Procesa una Matriz de Correlación cruzada mediante **Pearson (r)**.

### Advertencia Fundamental de Causalidad
La documentación y la salida del propio script incorporan proactivamente:
> **Correlación no implica causalidad.** Una fuerte métrica de Pearson ($r$) no demuestra que el evento A determine biológicamente el evento B. Las correlaciones solo descubren la fuerza o debilidad de la asociación lineal, y sirven como hipótesis de entrada para que futuros agentes de evaluación profunda las contrasten agronómicamente (ej., Math Agent / Validation Agent).

## Resultados y Validación con Datos Reales
A través del test `tests/test_day20_integration.py` se validó el pipeline:
- **Periodo:** Se forzó desde `2025-08-23` hasta `2026-08-22`.
- **Flexibilización de umbrales:** A causa de la altísima cobertura global de nubes en la zona interandina de Ecuador, Sentinel-2 arroja una nulidad de variables útiles (cero filas) al aplicar un filtro $<20\%$. Se ajustó a $90\%$ para capturar observaciones limitadas.
- **Filas integradas:** 53 observaciones coincidentes.
- **Columnas:** 17.
- **Correlación de referencia hallada:** $NDVI \leftrightarrow T2M$ produjo $\approx 0.178$ con data real.

## Testing
- Se ejecutó `python tests/test_day20_integration.py`.
- Posee 3 bloques funcionales de aserción (Mock Data Agent, Mock Stats Agent para exactitud 1.0 (Pearson manual = Pearson Algorítmico), Data Real Automática con GEE).
- No se han encontrado incompatibilidades en tipos ni en operaciones matriciales. 

## Limitaciones
* El actual Statistics Agent **no evalúa correlaciones con delays temporales (Lags)**. Para el crecimiento de tubérculos, el pico de follaje visible vía NDVI probablemente responde a precipitaciones de "N" semanas en el pasado, no a la lluvia de la exacta fecha de observación.
* La exclusión de SoilGrids del motor estadístico descarta análisis comparativos. Hasta que el análisis no aborde multi-parcelas (diferentes zonas en un mismo CSV), el suelo seguirá aportando varianza nula.
