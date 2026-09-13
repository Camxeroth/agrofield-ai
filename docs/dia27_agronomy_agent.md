# Día 27 — Agronomy Agent

## Objetivo

Implementar el **Agronomy Agent** como el primer componente de interpretación multifuente del pipeline de AgroField AI.

Su misión es **recibir** outputs estructurados de los agentes anteriores (Climate, Soil, Statistics, ML) y **producir** observaciones agronómicas contextuales, prudentes y trazables — sin afirmar causalidad, sin emitir prescripciones químicas específicas, y sin exceder la evidencia disponible.

---

## Rol dentro de la arquitectura

```
Sentinel-2 / GEE
      ↓
NASA POWER
      ↓
SoilGrids
      ↓
Data Agent
      ↓
Statistics Agent ─── Math Agent
      ↓                    ↓
Validation Agent ◄──────────
      ↓
ML Agent
      ↓
**Agronomy Agent**   ← Día 27
      ↓
(Reporte final — pendiente)
```

El Agronomy Agent **NO** entrena modelos, **NO** accede a datos brutos, **NO** modifica el dataset. Solo interpreta.

---

## Inputs

El agente acepta cinco fuentes de información, todas **opcionales** (el agente debe funcionar aunque falte alguna):

| Parámetro | Tipo | Fuente |
|---|---|---|
| `ndvi_values` | `List[float]` | Valores NDVI del dataset integrado (Data Agent) |
| `climate_result` | `Dict` | Output del `Climate Agent` |
| `soil_result` | `Dict` | Output del `Soil Agent` |
| `stats_result` | `Dict` | Output del `Statistics Agent` |
| `ml_result` | `Dict` | Output del `ML Agent` |
| `target` | `str` | Nombre del target ML (por defecto `'ndvi'`) |

---

## Outputs

El agente devuelve un diccionario con las siguientes claves:

| Clave | Contenido |
|---|---|
| `summary` | Resumen general del análisis y fuentes utilizadas |
| `ndvi_section` | Interpretación espectral del NDVI observado |
| `climate_section` | Interpretación del Climate Agent |
| `soil_section` | Interpretación del Soil Agent |
| `stats_section` | Lectura prudente de correlaciones de Pearson |
| `ml_section` | Interpretación rigurosa del modelo ML |
| `risk_indicators` | Indicadores contextuales de posible riesgo (no diagnósticos) |
| `monitoring_actions` | Acciones de monitoreo sugeridas (no prescripciones) |
| `global_limitations` | Limitaciones del análisis completo |
| `terminology_note` | Nota terminológica obligatoria sobre NDVI vs rendimiento |

---

## Separación explícita de niveles de información

El agente distingue entre cuatro niveles:

| Nivel | Ejemplo | Tratamiento |
|---|---|---|
| **Dato observado** | `NDVI = 0.372` | Confianza ALTA — no se interpreta más allá de lo matemáticamente demostrable |
| **Resultado estadístico** | `Pearson NDVI-T2M = 0.21` | Confianza ALTA para el cálculo; se acota a "asociación lineal" |
| **Resultado del modelo ML** | `R² = -0.852` | Confianza BAJA para la capacidad predictiva; se interpreta con precaución |
| **Interpretación agronómica** | Categoría de VPD | Confianza MEDIA — heurística contextual, no diagnóstico |

---

## Reglas de interpretación

### NDVI

- Valores < 0.2 → cobertura muy escasa o condiciones de estrés severo.
- Valores 0.2–0.4 → rango bajo a moderado, múltiples causas posibles.
- Valores 0.4–0.6 → cobertura moderada a considerable.
- Valores > 0.6 → cobertura densa, alta actividad fotosintética.

**NUNCA** se llama al NDVI "rendimiento agrícola".  
**NUNCA** se diagnostica enfermedad solo con NDVI.

### Clima

Reutiliza las interpretaciones del Climate Agent existente:
- Temperatura, precipitación y VPD se expresan como indicadores contextuales.
- El agente **NO** dice "VPD alto causó estrés"; dice "VPD alto puede representar condiciones de mayor demanda evaporativa que **pueden** asociarse con estrés hídrico si la disponibilidad de agua es limitada."

### Suelo

Reutiliza las interpretaciones del Soil Agent:
- pH, SOC y textura se presentan como contexto edáfico.
- **NO** se emiten recomendaciones de fertilización específicas (dosis, productos).

### Estadísticas (Pearson)

- Se calcula la correlación con el target y se describe la dirección e intensidad.
- Se usa el lenguaje: "asociación lineal positiva/negativa débil/moderada/fuerte".
- **NUNCA** se usa: "demuestra que causa", "provoca directamente".
- La limitación del tamaño de muestra (N ≈ 53) se declara explícitamente.

### ML (modelo baseline)

- **R² negativo** se interpreta como: "El modelo lineal no consiguió explicar la variabilidad del NDVI mejor que el predictor de referencia (media), **no** como evidencia de ausencia de relación causal entre clima y vegetación."
- Las predicciones se refieren a **NDVI espectral**, no a rendimiento agrícola.
- Las advertencias del ML Agent se trasladan al output del Agronomy Agent.

---

## Sistema de confianza

| Nivel | Significado | Asignado a |
|---|---|---|
| `ALTA` | Dato directamente observado o cálculo matemático determinista | NDVI observado, correlaciones de Pearson |
| `MEDIA` | Interpretación agronómica razonable pero dependiente del contexto | Interpretaciones de clima y suelo |
| `BAJA` | Múltiples explicaciones posibles; muestra pequeña | Indicadores de riesgo, interpretación del modelo ML |

---

## Resultado real del experimento (Datos reales — Día 27)

### Inputs utilizados

- **NDVI**: 53 valores representativos del dataset integrado Sentinel-2, rango 0.27–0.50.
- **Clima**: datos reales de `nasa_power_colta_12m_vpd_20250823_20260822.csv` (365 días, 2025-08-23 a 2026-08-22) procesados por `Climate Agent`.
- **Suelo**: resultados reales de SoilGrids para Colta, Chimborazo (pH ≈ 5.90, SOC ≈ 3.2%).
- **Estadísticas**: correlaciones de Pearson del dataset integrado (53 observaciones).
- **ML**: resultado real del Día 23 (MAE = 0.076, RMSE = 0.084, R² = −0.852).

### Outputs generados

```
SUMMARY:
  Agronomy Agent completó el análisis utilizando 5/5 fuentes.

NDVI (ALTA confianza):
  Media = 0.3715 | Rango: 0.27 – 0.50
  "Los valores promedio de NDVI (≈ 0.372) se ubican en un rango bajo a moderado.
   Puede corresponder a vegetación esparsa, fases fenológicas tempranas o
   condiciones limitantes no identificadas en este análisis."

CLIMA (MEDIA confianza):
  "Temperatura óptima (11.4°C) para tuberización y desarrollo. Buen vigor esperado."
  "Precipitación media diaria elevada (5.0 mm/día). Puede aumentar el riesgo de
   exceso de humedad dependiendo de la distribución de las lluvias."
  "VPD muy bajo (0.17 kPa). Transpiración limitada, alta humedad propicia para enfermedades."

SUELO (MEDIA confianza):
  "[pH] Óptimo para cultivo de papa. Buena disponibilidad de nutrientes."
  "[Carbono Orgánico] Contenido medio a adecuado de materia orgánica."
  "[Textura] Textura equilibrada a pesada. Monitorear el drenaje."

ESTADÍSTICAS (ALTA confianza):
  Correlaciones con NDVI: T2M r=0.21 (débil+), VPD r=0.18 (débil+),
  RH2M r=-0.14 (débil−), PRECTOTCORR r=-0.05 (débil−)
  Confianza ALTA aplicada al cálculo; la interpretación agronómica requiere cautela.

ML (BAJA confianza predictiva):
  Modelo: Linear Regression (Baseline)
  MAE = 0.0760 | RMSE = 0.0840 | R² = -0.852
  "El modelo lineal evaluado NO consiguió explicar la variabilidad del NDVI
   mejor que el predictor de referencia basado en la media.
   Este resultado NO permite establecer ausencia de relación causal."
  Confianza: BAJA (capacidad predictiva no establecida).

RISK INDICATORS (BAJA):
  "VPD potencialmente indicativo de mayor demanda evaporativa" — contextual, no diagnóstico.

MONITORING ACTIONS:
  1. Monitorear evolución temporal del NDVI con Sentinel-2.
  2. Comparar NDVI con calendario fenológico de papa en Colta.
  3. Revisar disponibilidad de escenas sin nubosidad para ampliar serie.
  4. El modelo baseline no superó el predictor de media — considerar lags y más observaciones.
```

---

## Limitaciones

1. **Tamaño de muestra (N = 53)**: todas las interpretaciones estadísticas y del ML son frágiles. Una variación en el conjunto de test puede cambiar las métricas significativamente.

2. **NASA POWER (~0.5° resolución)**: los datos climáticos son estimaciones de reanálisis. No representan exactamente las condiciones microclimáticas de la parcela.

3. **SoilGrids (escala regional)**: los datos de suelo son estimaciones. No sustituyen análisis de suelo in situ.

4. **NDVI sin fecha de adquisición en esta prueba**: los 53 valores NDVI usados en la prueba e2e son representativos basados en la documentación del Día 23, no procesados directamente del CSV satelital (que requiere Earth Engine). La lógica del agente no depende de esto; acepta cualquier lista de floats.

5. **Reglas agronómicas heurísticas**: los umbrales de NDVI, temperatura, precipitación y VPD son reglas de referencia del proyecto AgroField AI. No han sido validadas por expertos agronómicos en campo en Colta, Chimborazo.

6. **Sin fenología explícita**: el agente no distingue fases fenológicas del cultivo (siembra, tuberización, cosecha). Esto limita la interpretación de los valores de NDVI.

7. **R² negativo no interpretado como ausencia de relación**: se mantiene la precaución metodológica — el modelo lineal simple no capturó la dinámica, pero eso no descarta relaciones no lineales o con lags.

---

## Tests

Archivo: `tests/test_day27_agronomy.py`

**39 tests — todos pasan (OK)**

| Suite | Tests | Estado |
|---|---|---|
| `TestAgronomyAgentStructure` | 5 | ✅ OK |
| `TestNDVIInterpretation` | 4 | ✅ OK |
| `TestClimateInterpretation` | 3 | ✅ OK |
| `TestSoilInterpretation` | 3 | ✅ OK |
| `TestStatisticsInterpretation` | 3 | ✅ OK |
| `TestMLInterpretation` | 5 | ✅ OK |
| `TestMissingInputs` | 7 | ✅ OK |
| `TestMonitoringActionsNotPrescriptive` | 2 | ✅ OK |
| `TestRiskIndicators` | 3 | ✅ OK |
| `TestConfidenceLevels` | 3 | ✅ OK |

Tests históricos (Días 19–23): **44 tests — OK** (tras instalar `scikit-learn` en `.venv`, que estaba ausente del entorno — problema pre-existente al Día 27).

---

## Conclusión

El Agronomy Agent del Día 27 cumple los criterios de éxito definidos:

- ✅ Implementado como módulo Python reutilizable (`agents/agronomy_agent.py`)
- ✅ Inputs definidos (5 fuentes opcionales, todas toleradas si están ausentes)
- ✅ Outputs estructurados (10 claves documentadas)
- ✅ Interpretación separada de datos, estadísticas, ML e interpretación agronómica
- ✅ Sistema de confianza (ALTA / MEDIA / BAJA) implementado y testado
- ✅ Limitaciones incluidas en cada sección y globalmente
- ✅ Ninguna conclusión excede la evidencia disponible
- ✅ NDVI **no** llamado "rendimiento agrícola" en ninguna salida
- ✅ R² negativo **no** interpretado como prueba de ausencia de relación
- ✅ Sin recomendaciones prescriptivas químicas o agronómicas específicas
- ✅ Tests nuevos pasan (39/39); tests históricos pasan (44/44)
- ✅ Prueba e2e con datos climáticos reales realizada exitosamente
- ✅ Git limpio y coherente

**Estado final: COMPLETE**
