"""
agents/agronomy_agent.py
========================
Día 27 — AgroField AI

Rol dentro de la arquitectura:
    Satellite/Climate/Soil → Data Agent → Statistics Agent → Math Agent
    → Validation Agent → ML Agent → **Agronomy Agent**

El Agronomy Agent es un intérprete, NO un entrenador de modelos.

Responsabilidades:
  * Consumir outputs estructurados de los agentes anteriores.
  * Separar explícitamente:
      - dato observado
      - resultado estadístico
      - resultado del modelo ML
      - interpretación agronómica
      - limitación
  * Asignar un nivel de confianza a cada interpretación.
  * Generar observaciones de monitoreo (no recomendaciones prescriptivas).
  * NO afirmar causalidad.
  * NO diagnosticar enfermedades sólo con NDVI.
  * NO emitir recomendaciones químicas o agronómicas específicas sin datos suficientes.
  * NO llamar al NDVI "rendimiento agrícola".
  * NO llamar a las predicciones "predicción de rendimiento".

Confianza:
  ALTA   — dato directamente observado o cálculo matemático validado.
  MEDIA  — interpretación agronómica razonable y dependiente del contexto.
  BAJA   — múltiples explicaciones posibles o muestra pequeña.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Constantes de confianza
# ---------------------------------------------------------------------------

CONFIDENCE_HIGH = "ALTA"
CONFIDENCE_MEDIUM = "MEDIA"
CONFIDENCE_LOW = "BAJA"


# ---------------------------------------------------------------------------
# Funciones de interpretación de componentes individuales
# ---------------------------------------------------------------------------

def _interpret_ndvi(ndvi_values: List[float]) -> Dict[str, Any]:
    """
    Interpreta una lista de valores de NDVI observados.

    El NDVI (Normalized Difference Vegetation Index) es un indicador espectral
    de la densidad y vigor de la cubierta vegetal. No es equivalente a
    rendimiento agrícola, biomasa cosechable ni estado sanitario del cultivo.
    """
    if not ndvi_values:
        return {
            "observation": "No se proporcionaron valores de NDVI.",
            "confidence": CONFIDENCE_HIGH,
            "limitation": "Sin datos de NDVI no es posible caracterizar el estado espectral de la vegetación.",
        }

    valid = [v for v in ndvi_values if v is not None]
    if not valid:
        return {
            "observation": "Los valores de NDVI recibidos no contienen datos válidos.",
            "confidence": CONFIDENCE_HIGH,
            "limitation": "Sin valores válidos de NDVI no es posible caracterizar la cobertura vegetal.",
        }

    ndvi_mean = sum(valid) / len(valid)
    ndvi_min = min(valid)
    ndvi_max = max(valid)
    n = len(valid)

    # Categorización prudente — sin afirmar diagnóstico
    if ndvi_mean < 0.2:
        category = (
            "Los valores promedio de NDVI (≈ {:.3f}) se ubican en un rango muy bajo, "
            "lo cual puede asociarse con suelo desnudo, cobertura vegetal escasa o "
            "condiciones de estrés severo."
        ).format(ndvi_mean)
    elif ndvi_mean < 0.4:
        category = (
            "Los valores promedio de NDVI (≈ {:.3f}) se ubican en un rango bajo a moderado. "
            "Puede corresponder a vegetación esparsa, fases fenológicas tempranas o "
            "condiciones limitantes no identificadas en este análisis."
        ).format(ndvi_mean)
    elif ndvi_mean < 0.6:
        category = (
            "Los valores promedio de NDVI (≈ {:.3f}) sugieren una cobertura vegetal "
            "moderada a considerable. Este rango es consistente con cultivos en desarrollo "
            "activo en condiciones de Chimborazo."
        ).format(ndvi_mean)
    else:
        category = (
            "Los valores promedio de NDVI (≈ {:.3f}) se ubican en un rango alto, "
            "indicando una cobertura vegetal densa y/o alta actividad fotosintética."
        ).format(ndvi_mean)

    return {
        "n_observations": n,
        "ndvi_mean": round(ndvi_mean, 4),
        "ndvi_min": round(ndvi_min, 4),
        "ndvi_max": round(ndvi_max, 4),
        "observation": category,
        "confidence": CONFIDENCE_HIGH,
        "limitation": (
            "El NDVI es un indicador espectral de vegetación, no una medición directa de "
            "rendimiento, biomasa cosechable ni estado fitosanitario. Múltiples condiciones "
            "agronómicas, climáticas y de suelo pueden producir valores similares de NDVI."
        ),
    }


def _interpret_climate_result(climate_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Consume el output del Climate Agent y genera observaciones agronómicas
    contextuales, sin afirmar causalidad.
    """
    if not climate_result or "error" in climate_result:
        return {
            "observation": "No se pudo obtener interpretación climática (datos ausentes o error en Climate Agent).",
            "confidence": CONFIDENCE_HIGH,
            "limitation": "Sin contexto climático no es posible analizar condiciones agroclimáticas.",
        }

    observations: List[str] = []

    temp_interp = climate_result.get("temperature_interpretation", "")
    precip_interp = climate_result.get("precipitation_interpretation", "")
    vpd_interp = climate_result.get("vpd_interpretation", "")
    notes = climate_result.get("agronomic_notes", [])

    if temp_interp:
        observations.append(f"[Temperatura] {temp_interp}")
    if precip_interp:
        observations.append(f"[Precipitación] {precip_interp}")
    if vpd_interp and "no disponible" not in vpd_interp.lower():
        observations.append(f"[VPD] {vpd_interp}")

    return {
        "summary": climate_result.get("summary", ""),
        "observations": observations,
        "agronomic_notes": notes,
        "confidence": CONFIDENCE_MEDIUM,
        "limitation": (
            "Las interpretaciones climáticas son heurísticas de referencia del proyecto "
            "AgroField AI y no reemplazan un modelo fenológico formal ni una evaluación de campo. "
            "Valores promedio pueden ocultar variabilidad diaria relevante."
        ),
    }


def _interpret_soil_result(soil_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Consume el output del Soil Agent y genera observaciones sobre el
    contexto edáfico, sin emitir recomendaciones de fertilización específicas.
    """
    if not soil_result or "error" in soil_result:
        return {
            "observation": "No se pudo obtener interpretación edáfica (datos ausentes o error en Soil Agent).",
            "confidence": CONFIDENCE_HIGH,
            "limitation": "Sin datos de suelo no es posible contextualizar la fertilidad edáfica.",
        }

    observations: List[str] = []
    ph_interp = soil_result.get("ph_interpretation", "")
    soc_interp = soil_result.get("organic_carbon_interpretation", "")
    tex_interp = soil_result.get("texture_interpretation", "")
    notes = soil_result.get("agronomic_notes", [])

    if ph_interp and "no disponible" not in ph_interp.lower():
        observations.append(f"[pH] {ph_interp}")
    if soc_interp and "no disponible" not in soc_interp.lower():
        observations.append(f"[Carbono Orgánico] {soc_interp}")
    if tex_interp and "incompletos" not in tex_interp.lower():
        observations.append(f"[Textura] {tex_interp}")

    return {
        "summary": soil_result.get("summary", ""),
        "observations": observations,
        "agronomic_notes": notes,
        "confidence": CONFIDENCE_MEDIUM,
        "limitation": (
            "Los datos de suelo provienen de SoilGrids (estimaciones a escala regional). "
            "No sustituyen análisis de suelo en campo. Las interpretaciones son heurísticas "
            "iniciales y no determinan prescripciones específicas de enmiendas o fertilización."
        ),
    }


def _interpret_statistics_result(stats_result: Dict[str, Any], target: str = "ndvi") -> Dict[str, Any]:
    """
    Consume el output del Statistics Agent y genera una lectura prudente
    de las correlaciones de Pearson relevantes para el target.

    IMPORTANTE: correlación ≠ causalidad. Esto se declara explícitamente.
    """
    if not stats_result:
        return {
            "observation": "No se proporcionaron resultados estadísticos.",
            "confidence": CONFIDENCE_HIGH,
            "limitation": "Sin análisis estadístico no es posible cuantificar asociaciones lineales.",
        }

    correlations: Dict[str, Any] = stats_result.get("correlations", {})
    warnings: List[str] = stats_result.get("warnings", [])
    observations: List[str] = []

    # Extrae correlaciones con el target
    target_corrs: Dict[str, float] = {}
    if target in correlations:
        raw = correlations[target]
        for var, r_val in raw.items():
            if var != target and r_val is not None:
                try:
                    target_corrs[var] = float(r_val)
                except (TypeError, ValueError):
                    pass

    if target_corrs:
        sorted_corrs = sorted(target_corrs.items(), key=lambda x: abs(x[1]), reverse=True)
        obs_lines = []
        for var, r in sorted_corrs[:5]:  # top 5 más fuertes
            direction = "positiva" if r >= 0 else "negativa"
            strength = (
                "fuerte" if abs(r) >= 0.6 else
                "moderada" if abs(r) >= 0.3 else
                "débil"
            )
            obs_lines.append(
                f"{var}: r = {r:.3f} (asociación lineal {direction} {strength} con {target})"
            )
        observations.append(
            "Correlaciones de Pearson entre variables y el NDVI (indicador espectral): "
            + " | ".join(obs_lines)
        )

    return {
        "observations": observations,
        "pearson_correlations_with_target": target_corrs,
        "statistical_warnings": warnings,
        "confidence": CONFIDENCE_HIGH,   # el cálculo matemático es determinista
        "limitation": (
            "Las correlaciones de Pearson describen asociación lineal, no relaciones causales. "
            "Un valor alto de |r| no implica que una variable climática o edáfica determine "
            "biológicamente el NDVI. El tamaño de muestra (N ≈ 53) limita la robustez "
            "estadística de estas estimaciones."
        ),
    }


def _interpret_ml_result(ml_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Interpreta los resultados del ML Agent de forma rigurosa:
    - Un R² negativo NO significa que no existe relación entre clima y vegetación.
    - El modelo evalúa únicamente la capacidad predictiva lineal bajo un split temporal.
    - No se convierte el resultado en predicción de rendimiento.
    """
    if not ml_result:
        return {
            "observation": "No se proporcionaron resultados del ML Agent.",
            "confidence": CONFIDENCE_HIGH,
            "limitation": "Sin resultados del ML no es posible evaluar la capacidad predictiva.",
        }

    status = ml_result.get("status", "DESCONOCIDO")
    metrics = ml_result.get("metricas_test", {})
    advertencias = ml_result.get("advertencias", [])
    n_total = ml_result.get("n_observaciones_totales", 0)
    n_train = ml_result.get("n_train", 0)
    n_test = ml_result.get("n_test", 0)
    model_name = ml_result.get("modelo", "LinearRegression (Baseline)")
    features = ml_result.get("features", [])

    if status in ("FALLO", "FALLO - BLOCKED"):
        return {
            "observation": f"El ML Agent reportó un fallo: {advertencias}",
            "metrics": {},
            "confidence": CONFIDENCE_HIGH,
            "limitation": "No se dispone de métricas válidas del modelo.",
        }

    mae = metrics.get("MAE")
    rmse = metrics.get("RMSE")
    r2 = metrics.get("R2")

    # Interpretación rigurosa del R²
    if r2 is not None:
        if r2 < 0:
            r2_interp = (
                f"R² = {r2:.3f} (negativo). El modelo lineal evaluado no consiguió explicar "
                "la variabilidad del NDVI en el conjunto de prueba mejor que el predictor "
                "de referencia basado en la media del conjunto de entrenamiento. "
                "Este resultado no permite establecer ausencia de relación entre clima y vegetación; "
                "únicamente indica que la combinación lineal de las features seleccionadas no "
                "fue suficiente bajo el split temporal utilizado y con el tamaño de muestra disponible."
            )
        elif r2 < 0.3:
            r2_interp = (
                f"R² = {r2:.3f} (bajo). El modelo lineal explica una fracción pequeña de la "
                "variabilidad del NDVI. La capacidad predictiva es limitada."
            )
        elif r2 < 0.6:
            r2_interp = (
                f"R² = {r2:.3f} (moderado). El modelo captura parte de la variabilidad del NDVI, "
                "aunque hay un margen considerable de variación no explicada."
            )
        else:
            r2_interp = (
                f"R² = {r2:.3f} (alto). El modelo explica una fracción importante de la "
                "variabilidad del NDVI bajo el split temporal evaluado."
            )
    else:
        r2_interp = "R² no disponible."

    observations = [
        f"Modelo: {model_name}",
        f"Features usadas: {features}",
        f"Muestras — Total: {n_total} | Train: {n_train} | Test: {n_test}",
        f"MAE = {mae:.4f}" if mae is not None else "MAE no disponible.",
        f"RMSE = {rmse:.4f}" if rmse is not None else "RMSE no disponible.",
        r2_interp,
    ]

    return {
        "observations": observations,
        "metrics": {"MAE": mae, "RMSE": rmse, "R2": r2},
        "model_warnings": advertencias,
        "confidence": CONFIDENCE_LOW,  # capacidad predictiva baja confirmada
        "limitation": (
            "El modelo es un baseline de regresión lineal evaluado con N ≈ 53 observaciones "
            "satelitales (una por paso de satélite, no una por día). "
            "Las predicciones se refieren al NDVI (indicador espectral), NO al rendimiento agrícola. "
            "Un R² negativo no implica ausencia de relación causal entre las variables climáticas "
            "y la vegetación. El modelo podría mejorarse con: más observaciones, variables adicionales, "
            "información temporal (lags), o modelos no lineales con la muestra apropiada."
        ),
    }


# ---------------------------------------------------------------------------
# Función principal del agente
# ---------------------------------------------------------------------------

def run(
    ndvi_values: Optional[List[float]] = None,
    climate_result: Optional[Dict[str, Any]] = None,
    soil_result: Optional[Dict[str, Any]] = None,
    stats_result: Optional[Dict[str, Any]] = None,
    ml_result: Optional[Dict[str, Any]] = None,
    target: str = "ndvi",
) -> Dict[str, Any]:
    """
    Agronomy Agent — Punto de entrada principal.

    Parámetros
    ----------
    ndvi_values : lista de floats con los valores NDVI observados (opcional).
    climate_result : dict con el output del Climate Agent (opcional).
    soil_result : dict con el output del Soil Agent (opcional).
    stats_result : dict con el output del Statistics Agent (opcional).
    ml_result : dict con el output del ML Agent (opcional).
    target : nombre de la variable objetivo del ML Agent (por defecto 'ndvi').

    Retorna
    -------
    dict con claves:
      summary          — resumen general
      ndvi_section     — interpretación espectral de NDVI
      climate_section  — interpretación climática
      soil_section     — interpretación edáfica
      stats_section    — interpretación estadística (correlaciones)
      ml_section       — interpretación del modelo ML
      risk_indicators  — indicadores contextuales de riesgo (no diagnósticos)
      monitoring_actions — acciones de monitoreo sugeridas
      global_limitations — limitaciones del análisis completo
      terminology_note — nota terminológica obligatoria
    """
    # Secciones de análisis
    ndvi_section = _interpret_ndvi(ndvi_values or [])
    climate_section = _interpret_climate_result(climate_result or {})
    soil_section = _interpret_soil_result(soil_result or {})
    stats_section = _interpret_statistics_result(stats_result or {}, target=target)
    ml_section = _interpret_ml_result(ml_result or {})

    # Indicadores contextuales de riesgo (NOT diagnoses)
    risk_indicators = _build_risk_indicators(ndvi_section, climate_section, soil_section)

    # Acciones de monitoreo
    monitoring_actions = _build_monitoring_actions(ndvi_section, ml_section, risk_indicators)

    # Resumen general
    n_inputs_available = sum([
        ndvi_values is not None and len(ndvi_values) > 0,
        bool(climate_result),
        bool(soil_result),
        bool(stats_result),
        bool(ml_result),
    ])
    summary = (
        f"Agronomy Agent completó el análisis utilizando {n_inputs_available}/5 fuentes de información "
        f"disponibles (NDVI, Climate Agent, Soil Agent, Statistics Agent, ML Agent). "
        "Todas las interpretaciones son observaciones contextuales; "
        "ninguna constituye un diagnóstico agronómico definitivo ni una prescripción."
    )

    return {
        "summary": summary,
        "ndvi_section": ndvi_section,
        "climate_section": climate_section,
        "soil_section": soil_section,
        "stats_section": stats_section,
        "ml_section": ml_section,
        "risk_indicators": risk_indicators,
        "monitoring_actions": monitoring_actions,
        "global_limitations": [
            "El análisis se basa en N ≈ 53 observaciones satelitales (Sentinel-2) con cobertura "
            "nubosa reducida disponible para Colta, Chimborazo. El tamaño de muestra limita la "
            "robustez estadística de todas las inferencias.",
            "Los datos climáticos provienen de NASA POWER (estimaciones de reanálisis, escala ~0.5°). "
            "Pueden no representar exactamente las condiciones microclimáticas de la parcela.",
            "Los datos de suelo provienen de SoilGrids (estimaciones a escala regional). No "
            "sustituyen análisis de suelo in situ.",
            "Ninguna interpretación de este agente establece causalidad entre las variables "
            "observadas y el estado fitosanitario o el rendimiento del cultivo.",
            "Las reglas de interpretación agronómica son heurísticas iniciales del proyecto "
            "AgroField AI y deben validarse con expertos agronómicos en campo.",
        ],
        "terminology_note": (
            "NOTA TERMINOLÓGICA OBLIGATORIA: En este sistema, 'NDVI' se refiere exclusivamente "
            "al Normalized Difference Vegetation Index, un indicador espectral de densidad de "
            "vegetación. No es equivalente a 'rendimiento agrícola', 'producción', 'biomasa "
            "cosechable' ni 'estado sanitario del cultivo'. Las predicciones del ML Agent "
            "predicen NDVI (valor espectral), no rendimiento."
        ),
    }


# ---------------------------------------------------------------------------
# Funciones auxiliares de síntesis
# ---------------------------------------------------------------------------

def _build_risk_indicators(
    ndvi_section: Dict,
    climate_section: Dict,
    soil_section: Dict,
) -> List[Dict[str, str]]:
    """
    Genera una lista de indicadores contextuales de riesgo.
    Son observaciones, no diagnósticos.
    """
    indicators = []

    # NDVI bajo
    ndvi_mean = ndvi_section.get("ndvi_mean")
    if ndvi_mean is not None and ndvi_mean < 0.3:
        indicators.append({
            "indicator": "NDVI bajo observado",
            "context": (
                f"El NDVI promedio observado (≈ {ndvi_mean:.3f}) se ubica en un rango bajo. "
                "Podría asociarse con cobertura vegetal escasa, fase fenológica temprana, "
                "condiciones de estrés o limitaciones no identificadas. "
                "Se requiere análisis de campo para establecer la causa."
            ),
            "confidence": CONFIDENCE_LOW,
        })

    # VPD potencialmente elevado desde notas climáticas
    climate_notes = climate_section.get("agronomic_notes", [])
    for note in climate_notes:
        if "VPD" in note and ("alto" in note.lower() or "kpa" in note.lower()):
            indicators.append({
                "indicator": "VPD potencialmente indicativo de mayor demanda evaporativa",
                "context": (
                    "Se observó VPD con valores que pueden indicar incremento en la "
                    "demanda evaporativa atmosférica. Si la disponibilidad hídrica del "
                    "suelo es limitada, esto puede representar un factor contextual de estrés."
                ),
                "confidence": CONFIDENCE_LOW,
            })
            break

    # Suelo ácido
    soil_notes = soil_section.get("agronomic_notes", [])
    for note in soil_notes:
        if "pH" in note and ("ácido" in note.lower() or "require encalado" in note.lower()):
            indicators.append({
                "indicator": "pH potencialmente subóptimo",
                "context": (
                    "El pH edáfico observado se ubica en un rango que puede limitar la "
                    "disponibilidad de nutrientes para el cultivo de papa según las heurísticas "
                    "de referencia del proyecto. Se sugiere verificar con análisis de campo."
                ),
                "confidence": CONFIDENCE_LOW,
            })
            break

    if not indicators:
        indicators.append({
            "indicator": "Sin indicadores de riesgo destacables con los datos actuales",
            "context": (
                "Los indicadores revisados no muestran señales de alerta claras con la "
                "información disponible. Esto no excluye la existencia de condiciones "
                "no capturadas por las fuentes de datos del proyecto."
            ),
            "confidence": CONFIDENCE_LOW,
        })

    return indicators


def _build_monitoring_actions(
    ndvi_section: Dict,
    ml_section: Dict,
    risk_indicators: List[Dict],
) -> List[str]:
    """
    Genera acciones de monitoreo. Nunca prescripciones químicas/agronómicas específicas.
    """
    actions = [
        "Monitorear la evolución temporal del NDVI con las siguientes imágenes Sentinel-2 "
        "disponibles para evaluar tendencias de la cobertura vegetal.",
        "Comparar los valores de NDVI con el calendario fenológico del cultivo de papa "
        "establecido en la zona de Colta, Chimborazo, para contextualizar los valores espectrales.",
        "Revisar la disponibilidad de observaciones satelitales sin nubosidad en los "
        "próximos meses para ampliar la serie temporal y mejorar la robustez del análisis.",
    ]

    ndvi_mean = ndvi_section.get("ndvi_mean")
    if ndvi_mean is not None and ndvi_mean < 0.3:
        actions.append(
            "Verificar en campo las condiciones de la parcela ante el NDVI bajo observado "
            "(posibles causas: cobertura escasa, estrés hídrico, fase fenológica temprana, "
            "u otras condiciones no capturadas por las fuentes de datos remotas)."
        )

    r2 = ml_section.get("metrics", {}).get("R2")
    if r2 is not None and r2 < 0:
        actions.append(
            "El modelo baseline no consiguió superar el predictor de media. "
            "Considerar: ampliar la serie temporal de observaciones, incorporar "
            "información climática histórica (lags), o explorar modelos no lineales "
            "cuando la muestra sea suficiente."
        )

    return actions
