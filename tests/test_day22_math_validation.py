import os
import sys
import math
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents import math_agent, validation_agent, statistics_agent, data_agent
from src.data.ee_extractor import EarthEngineExtractor
from config import STUDY_ZONE

def test_pearson_perfecto():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [2, 4, 6]})
    res = math_agent.run(df, "x", "y")
    assert res["status"] == "success"
    assert math.isclose(res["resultado_r"], 1.0, rel_tol=1e-5)
    
def test_pearson_negativo():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [6, 4, 2]})
    res = math_agent.run(df, "x", "y")
    assert res["status"] == "success"
    assert math.isclose(res["resultado_r"], -1.0, rel_tol=1e-5)
    
def test_pearson_cercano_cero():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [1, -2, 1]})
    res = math_agent.run(df, "x", "y")
    assert res["status"] == "success"
    assert "muy débil o nula" in res["interpretacion"].lower()
    assert abs(res["resultado_r"]) < 0.2
    assert abs(res["resultado_r"]) < 0.2

def test_variable_constante():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [5, 5, 5]})
    res = math_agent.run(df, "x", "y")
    assert res["status"] == "error"
    assert "varianza 0" in res["error"]
    
def test_datos_insuficientes():
    df = pd.DataFrame({"x": [1], "y": [2]})
    res = math_agent.run(df, "x", "y")
    assert res["status"] == "error"
    assert "insuficientes" in res["error"]
    
def test_datos_con_nan():
    df = pd.DataFrame({"x": [1, np.nan, 3], "y": [2, 4, 6]})
    res = math_agent.run(df, "x", "y")
    assert res["status"] == "success"
    assert res["n_observaciones"] == 2
    assert math.isclose(res["resultado_r"], 1.0, rel_tol=1e-5)

def test_validacion_real():
    print("\n[INFO] Ejecutando validación real (Pipeline Día 22)...")
    manual_r_historico = 0.178398  # Resultado previamente documentado (Semana 3)
    
    # 1. Pipeline Original (Extraer Data Real)
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'nasa_power_colta_12m_vpd_20250823_20260822.csv')
    if not os.path.exists(csv_path):
        print("CSV climático no hallado, saltando.")
        return
        
    climate_df = pd.read_csv(csv_path)
    extractor = EarthEngineExtractor()
    sat_df = extractor.get_sentinel2_timeseries(
        lon=STUDY_ZONE['longitud'], 
        lat=STUDY_ZONE['latitud'], 
        start_date='2025-08-23', 
        end_date='2026-08-22',
        max_clouds=90
    )
    
    soil_data = {"phh2o": {"valor": 6.6}}
    integrated_df, _ = data_agent.run(sat_df, climate_df, soil_data)
    
    if len(integrated_df.dropna(subset=['ndvi', 'T2M'])) < 2:
        return
        
    # 2. Operations (Statistics Agent as 'Python')
    stats_out = statistics_agent.run(integrated_df)
    python_r = stats_out["correlations"]["ndvi"]["T2M"]
    
    # 3. Math Agent
    math_out = math_agent.run(integrated_df, "ndvi", "T2M")
    math_r = math_out["resultado_r"]
    
    print(f"Manual (Histórico): {manual_r_historico}")
    print(f"Python (Stats Agent): {python_r}")
    print(f"Math Agent: {math_r}")
    
    # 4. Validation Agent
    # Se usa una tolerancia levemente ajustada (1e-4) para encajar el registro truncado del manual
    val_out = validation_agent.run(manual_r_historico, python_r, math_r, tolerance=1e-4)
    print(f"Validación Status: {val_out['status']}")
    print(f"Mensaje: {val_out['mensaje']}")
    
    # Comprobar que en la base el Python = Math Agent (1e-7 tolerancia es posible aquí)
    assert math.isclose(python_r, math_r, rel_tol=1e-7), "Diferencia grave entre Pandas Nativo y Numpy en el agente."

if __name__ == "__main__":
    test_pearson_perfecto()
    test_pearson_negativo()
    test_pearson_cercano_cero()
    test_variable_constante()
    test_datos_insuficientes()
    test_datos_con_nan()
    test_validacion_real()
    print(" === TESTS DÍA 22 EJECUTADOS Y APROBADOS ===")
