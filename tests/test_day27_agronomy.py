"""
tests/test_day27_agronomy.py
============================
Día 27 — Tests del Agronomy Agent

Verifican:
  1.  El agente recibe datos válidos y produce estructura de salida válida.
  2.  Puede interpretar NDVI.
  3.  Puede interpretar información climática.
  4.  Puede interpretar información de suelo.
  5.  Puede interpretar resultados estadísticos.
  6.  Puede interpretar resultados del ML Agent.
  7.  Maneja ausencia completa de datos.
  8.  No genera recomendaciones prescriptivas peligrosamente específicas.
  9.  Mantiene limitaciones en la salida.
  10. No interpreta correlación como causalidad en el texto de output.
  11. No interpreta R² negativo como prueba de ausencia de relación.
  12. No falla cuando faltan componentes opcionales.
  13. La nota terminológica está presente y contiene las aclaraciones clave.
  14. "rendimiento" no aparece en salidas de interpretación de NDVI ni ML.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import agents.agronomy_agent as agronomy_agent


# ---------------------------------------------------------------------------
# Fixtures de datos de prueba (sintéticos, basados en la estructura real)
# ---------------------------------------------------------------------------

SAMPLE_NDVI_VALUES = [0.35, 0.40, 0.38, 0.42, 0.30, 0.28, 0.45]

SAMPLE_CLIMATE_RESULT = {
    "summary": "Análisis climático completado para 365 días.",
    "temperature_interpretation": "Temperatura óptima (11.0°C) para tuberización y desarrollo.",
    "precipitation_interpretation": "Humedad adecuada (3.2 mm/día). Muy favorable para el cultivo en secano.",
    "vpd_interpretation": "VPD dentro del rango de referencia utilizado por AgroField AI (0.18 kPa).",
    "agronomic_notes": [
        "Rango de temperatura: de 9.3°C a 13.6°C",
        "Precipitación acumulada: 1170.3 mm en 365 días",
        "VPD promedio: 0.18 kPa, máximo: 0.28 kPa",
        "Humedad Relativa promedio: 87.1%",
    ],
}

SAMPLE_SOIL_RESULT = {
    "summary": "Análisis de suelo completado para la capa 0–30 cm.",
    "ph_interpretation": "Óptimo para cultivo de papa. Buena disponibilidad de nutrientes.",
    "organic_carbon_interpretation": "Contenido medio a adecuado de materia orgánica.",
    "texture_interpretation": "Textura equilibrada a pesada. Monitorear el drenaje.",
    "agronomic_notes": [
        "pH actual: 5.90 - Óptimo para cultivo de papa.",
        "Carbono orgánico: 3.20% - Contenido medio a adecuado.",
        "Textura (Arena: 35%, Limo: 40%, Arcilla: 25%) - Textura franca.",
    ],
}

SAMPLE_STATS_RESULT = {
    "summary": "Análisis estadístico completado.",
    "correlations": {
        "ndvi": {
            "ndvi": 1.0,
            "T2M": 0.21,
            "PRECTOTCORR": -0.05,
            "VPD": 0.18,
            "RH2M": -0.14,
            "ALLSKY_SFC_SW_DWN": 0.09,
        }
    },
    "data_quality": {"total_rows": 53, "numeric_columns_analyzed": ["ndvi", "T2M", "RH2M"]},
    "warnings": [
        "LIMITACIÓN ESTADÍSTICA: Correlación no implica causalidad."
    ],
}

SAMPLE_ML_RESULT = {
    "status": "OK",
    "target": "ndvi",
    "features": ["T2M", "RH2M", "PRECTOTCORR", "ALLSKY_SFC_SW_DWN", "VPD"],
    "n_observaciones_totales": 53,
    "n_train": 42,
    "n_test": 11,
    "estrategia_split": "Temporal (80% pasado -> train, 20% futuro -> test)",
    "modelo": "Linear Regression (Baseline)",
    "metricas_test": {"MAE": 0.076, "RMSE": 0.084, "R2": -0.852},
    "advertencias": [
        "R2 negativo en Test: El baseline rinde peor que predecir simplemente la media esperada global."
    ],
    "limitaciones": [
        "Un baseline no representa todavía un modelo productivo.",
    ],
}

SAMPLE_ML_RESULT_BLOCKED = {
    "status": "FALLO - BLOCKED",
    "target": "ndvi",
    "features": [],
    "n_observaciones_totales": 0,
    "n_train": 0,
    "n_test": 0,
    "metricas_test": {},
    "advertencias": ["ML baseline = BLOCKED. No existe el target supervisado 'ndvi'."],
    "limitaciones": [],
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestAgronomyAgentStructure(unittest.TestCase):
    """Verifica estructura del output cuando se pasan todos los inputs."""

    def setUp(self):
        self.result = agronomy_agent.run(
            ndvi_values=SAMPLE_NDVI_VALUES,
            climate_result=SAMPLE_CLIMATE_RESULT,
            soil_result=SAMPLE_SOIL_RESULT,
            stats_result=SAMPLE_STATS_RESULT,
            ml_result=SAMPLE_ML_RESULT,
        )

    def test_output_is_dict(self):
        """1. El agente produce una estructura de salida válida (dict)."""
        self.assertIsInstance(self.result, dict)

    def test_required_keys_present(self):
        """1. La salida contiene todas las claves requeridas."""
        required_keys = [
            "summary", "ndvi_section", "climate_section", "soil_section",
            "stats_section", "ml_section", "risk_indicators",
            "monitoring_actions", "global_limitations", "terminology_note",
        ]
        for key in required_keys:
            self.assertIn(key, self.result, f"Falta la clave requerida: '{key}'")

    def test_summary_is_nonempty_string(self):
        """1. El resumen es una cadena no vacía."""
        self.assertIsInstance(self.result["summary"], str)
        self.assertGreater(len(self.result["summary"]), 10)

    def test_global_limitations_is_list(self):
        """9. Las limitaciones globales están presentes como lista."""
        self.assertIsInstance(self.result["global_limitations"], list)
        self.assertGreater(len(self.result["global_limitations"]), 0)

    def test_terminology_note_present(self):
        """13. La nota terminológica está presente."""
        note = self.result["terminology_note"]
        self.assertIn("NDVI", note)
        self.assertIn("rendimiento", note.lower())  # debe MENCIONAR para aclarar, no usar como sinónimo


class TestNDVIInterpretation(unittest.TestCase):
    """2. Puede interpretar NDVI."""

    def test_ndvi_mean_computed(self):
        result = agronomy_agent.run(ndvi_values=SAMPLE_NDVI_VALUES)
        ndvi_sec = result["ndvi_section"]
        self.assertIn("ndvi_mean", ndvi_sec)
        expected = round(sum(SAMPLE_NDVI_VALUES) / len(SAMPLE_NDVI_VALUES), 4)
        self.assertAlmostEqual(ndvi_sec["ndvi_mean"], expected, places=3)

    def test_ndvi_section_has_limitation(self):
        result = agronomy_agent.run(ndvi_values=SAMPLE_NDVI_VALUES)
        self.assertIn("limitation", result["ndvi_section"])
        self.assertGreater(len(result["ndvi_section"]["limitation"]), 20)

    def test_ndvi_high_value_range(self):
        result = agronomy_agent.run(ndvi_values=[0.70, 0.72, 0.68])
        obs = result["ndvi_section"].get("observation", "")
        self.assertIn("alto", obs.lower())

    def test_ndvi_low_value_range(self):
        result = agronomy_agent.run(ndvi_values=[0.10, 0.12, 0.08])
        obs = result["ndvi_section"].get("observation", "")
        self.assertIn("bajo", obs.lower())

    def test_ndvi_interpretation_no_rendimiento_word(self):
        """14. La sección NDVI no llama al NDVI 'rendimiento'."""
        result = agronomy_agent.run(ndvi_values=SAMPLE_NDVI_VALUES)
        obs = result["ndvi_section"].get("observation", "").lower()
        # "rendimiento" no debe aparecer como descriptor de ndvi en la observación directa
        self.assertNotIn("rendimiento agrícola", obs)


class TestClimateInterpretation(unittest.TestCase):
    """3. Puede interpretar información climática."""

    def test_climate_section_has_observations(self):
        result = agronomy_agent.run(climate_result=SAMPLE_CLIMATE_RESULT)
        climate_sec = result["climate_section"]
        self.assertIsInstance(climate_sec.get("observations"), list)
        self.assertGreater(len(climate_sec["observations"]), 0)

    def test_climate_section_has_limitation(self):
        result = agronomy_agent.run(climate_result=SAMPLE_CLIMATE_RESULT)
        self.assertIn("limitation", result["climate_section"])
        self.assertGreater(len(result["climate_section"]["limitation"]), 20)

    def test_empty_climate_handled(self):
        result = agronomy_agent.run(climate_result={})
        self.assertIn("climate_section", result)
        # no debe lanzar excepción


class TestSoilInterpretation(unittest.TestCase):
    """4. Puede interpretar información de suelo."""

    def test_soil_section_has_observations(self):
        result = agronomy_agent.run(soil_result=SAMPLE_SOIL_RESULT)
        soil_sec = result["soil_section"]
        self.assertIsInstance(soil_sec.get("observations"), list)
        self.assertGreater(len(soil_sec["observations"]), 0)

    def test_soil_section_has_limitation(self):
        result = agronomy_agent.run(soil_result=SAMPLE_SOIL_RESULT)
        self.assertIn("limitation", result["soil_section"])

    def test_no_specific_fertilizer_prescription(self):
        """8. No genera recomendaciones prescriptivas específicas (fertilizante)."""
        result = agronomy_agent.run(soil_result=SAMPLE_SOIL_RESULT)
        all_text = str(result["soil_section"]).lower()
        # Forbidden prescriptive terms
        for forbidden in ["aplique", "kg de fertilizante", "aplique fungicida"]:
            self.assertNotIn(forbidden, all_text,
                             f"Término prescriptivo prohibido encontrado: '{forbidden}'")


class TestStatisticsInterpretation(unittest.TestCase):
    """5. Puede interpretar resultados estadísticos."""

    def test_stats_section_has_correlations(self):
        result = agronomy_agent.run(stats_result=SAMPLE_STATS_RESULT)
        stats_sec = result["stats_section"]
        self.assertIn("pearson_correlations_with_target", stats_sec)
        self.assertIsInstance(stats_sec["pearson_correlations_with_target"], dict)

    def test_stats_correlation_not_called_causality(self):
        """10. No interpreta correlación como causalidad en el texto producido."""
        result = agronomy_agent.run(stats_result=SAMPLE_STATS_RESULT)
        all_text = str(result["stats_section"]).lower()
        # Las observaciones deben usar "asociación" no "causa" como afirmación directa
        self.assertNotIn("demuestra que causa", all_text)
        self.assertNotIn("provoca directamente", all_text)

    def test_stats_section_has_limitation(self):
        result = agronomy_agent.run(stats_result=SAMPLE_STATS_RESULT)
        self.assertIn("limitation", result["stats_section"])
        self.assertIn("causal", result["stats_section"]["limitation"].lower())


class TestMLInterpretation(unittest.TestCase):
    """6. Puede interpretar resultados del ML Agent."""

    def test_ml_section_has_metrics(self):
        result = agronomy_agent.run(ml_result=SAMPLE_ML_RESULT)
        ml_sec = result["ml_section"]
        self.assertIn("metrics", ml_sec)
        metrics = ml_sec["metrics"]
        self.assertAlmostEqual(metrics["MAE"], 0.076, places=3)
        self.assertAlmostEqual(metrics["RMSE"], 0.084, places=3)
        self.assertAlmostEqual(metrics["R2"], -0.852, places=3)

    def test_negative_r2_interpretation_is_prudent(self):
        """11. No interpreta R² negativo como prueba de ausencia de relación."""
        result = agronomy_agent.run(ml_result=SAMPLE_ML_RESULT)
        observations_text = " ".join(result["ml_section"].get("observations", [])).lower()
        # Must NOT say the climate has no relationship with vegetation
        self.assertNotIn("no existe relación", observations_text)
        self.assertNotIn("demuestra que el clima no afecta", observations_text)
        # MUST acknowledge the model's limitation explicitly
        self.assertIn("no consiguió explicar", observations_text)

    def test_ml_not_called_yield_prediction(self):
        """14. Las predicciones no se llaman 'predicción de rendimiento'."""
        result = agronomy_agent.run(ml_result=SAMPLE_ML_RESULT)
        ml_text = str(result["ml_section"]).lower()
        self.assertNotIn("predicción de rendimiento", ml_text)
        self.assertNotIn("predice el rendimiento", ml_text)

    def test_ml_section_has_limitation(self):
        result = agronomy_agent.run(ml_result=SAMPLE_ML_RESULT)
        self.assertIn("limitation", result["ml_section"])

    def test_ml_blocked_status_handled(self):
        """El agente maneja correctamente un ML Agent en estado BLOCKED."""
        result = agronomy_agent.run(ml_result=SAMPLE_ML_RESULT_BLOCKED)
        self.assertIn("ml_section", result)
        self.assertIsInstance(result["ml_section"], dict)


class TestMissingInputs(unittest.TestCase):
    """7. Maneja ausencia de datos. 12. No falla cuando faltan componentes."""

    def test_all_none_inputs_no_crash(self):
        """7/12. El agente NO falla si todos los inputs son None o vacíos."""
        result = agronomy_agent.run()
        self.assertIsInstance(result, dict)
        self.assertIn("summary", result)

    def test_only_ndvi_no_crash(self):
        result = agronomy_agent.run(ndvi_values=[0.35, 0.40])
        self.assertIsInstance(result, dict)

    def test_only_ml_no_crash(self):
        result = agronomy_agent.run(ml_result=SAMPLE_ML_RESULT)
        self.assertIsInstance(result, dict)

    def test_empty_ndvi_list_no_crash(self):
        result = agronomy_agent.run(ndvi_values=[])
        self.assertIn("ndvi_section", result)
        obs = result["ndvi_section"].get("observation", "")
        self.assertGreater(len(obs), 0)

    def test_ndvi_with_none_values_no_crash(self):
        result = agronomy_agent.run(ndvi_values=[None, None])
        self.assertIn("ndvi_section", result)

    def test_climate_error_dict_handled(self):
        result = agronomy_agent.run(climate_result={"error": "Sin datos climáticos"})
        self.assertIsInstance(result, dict)

    def test_soil_error_dict_handled(self):
        result = agronomy_agent.run(soil_result={"error": "Sin datos de suelo"})
        self.assertIsInstance(result, dict)


class TestMonitoringActionsNotPrescriptive(unittest.TestCase):
    """8. Acciones de monitoreo no son prescripciones."""

    def test_no_chemical_prescriptions(self):
        result = agronomy_agent.run(
            ndvi_values=SAMPLE_NDVI_VALUES,
            climate_result=SAMPLE_CLIMATE_RESULT,
            soil_result=SAMPLE_SOIL_RESULT,
            ml_result=SAMPLE_ML_RESULT,
        )
        actions_text = " ".join(result["monitoring_actions"]).lower()
        forbidden = [
            "aplique", "fertilizante", "herbicida", "fungicida",
            "riegue exactamente", "kg de", "litros de",
        ]
        for term in forbidden:
            self.assertNotIn(term, actions_text,
                             f"Término prescriptivo prohibido en monitoring_actions: '{term}'")

    def test_monitoring_actions_is_list(self):
        result = agronomy_agent.run()
        self.assertIsInstance(result["monitoring_actions"], list)


class TestRiskIndicators(unittest.TestCase):
    """Indicadores de riesgo: contextuales, no diagnósticos."""

    def test_risk_indicators_is_list(self):
        result = agronomy_agent.run(
            ndvi_values=SAMPLE_NDVI_VALUES,
            climate_result=SAMPLE_CLIMATE_RESULT,
            soil_result=SAMPLE_SOIL_RESULT,
        )
        self.assertIsInstance(result["risk_indicators"], list)
        self.assertGreater(len(result["risk_indicators"]), 0)

    def test_low_ndvi_triggers_indicator(self):
        result = agronomy_agent.run(ndvi_values=[0.10, 0.12])
        indicators_text = str(result["risk_indicators"]).lower()
        self.assertIn("ndvi", indicators_text)

    def test_no_disease_diagnosis_from_ndvi(self):
        """No diagnostica enfermedades sólo con NDVI."""
        result = agronomy_agent.run(ndvi_values=[0.05, 0.08])
        all_text = str(result).lower()
        self.assertNotIn("enfermedad confirmada", all_text)
        self.assertNotIn("estrés confirmado", all_text)


class TestConfidenceLevels(unittest.TestCase):
    """Verifica que el sistema de confianza funciona y usa los valores esperados."""

    def test_ndvi_confidence_is_high(self):
        """El NDVI observado tiene confianza ALTA."""
        result = agronomy_agent.run(ndvi_values=SAMPLE_NDVI_VALUES)
        self.assertEqual(result["ndvi_section"]["confidence"], agronomy_agent.CONFIDENCE_HIGH)

    def test_ml_confidence_is_low_when_r2_negative(self):
        """Con R²<0 la confianza del ML debe ser BAJA."""
        result = agronomy_agent.run(ml_result=SAMPLE_ML_RESULT)
        self.assertEqual(result["ml_section"]["confidence"], agronomy_agent.CONFIDENCE_LOW)

    def test_climate_confidence_is_medium(self):
        result = agronomy_agent.run(climate_result=SAMPLE_CLIMATE_RESULT)
        self.assertEqual(result["climate_section"]["confidence"], agronomy_agent.CONFIDENCE_MEDIUM)


if __name__ == "__main__":
    unittest.main(verbosity=2)
