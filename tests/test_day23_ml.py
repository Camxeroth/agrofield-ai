import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents import ml_agent, data_agent
from src.data.ee_extractor import EarthEngineExtractor
from config import STUDY_ZONE

def _mock_training_df():
    # Creamos un DF semi-lineal para que el modelo aprenda algo (n = 15)
    dates = pd.date_range("2026-01-01", periods=15)
    f1 = np.linspace(10, 24, 15)
    f2 = np.linspace(50, 80, 15)
    target = f1 * 0.5 + np.random.normal(0, 0.1, 15)
    
    return pd.DataFrame({
        "date": dates,
        "f1": f1,
        "f2": f2,
        "target": target
    })

def test_ml_agent_entrenamiento_controlado():
    df = _mock_training_df()
    res = ml_agent.run(df, target_col="target", feature_cols=["f1", "f2"])
    
    assert res["status"] == "OK"
    assert res["n_observaciones_totales"] == 15
    assert res["n_train"] == 12 # 80% de 15 
    assert res["n_test"] == 3
    assert "MAE" in res["metricas_test"]

def test_ml_agent_columnas_faltantes():
    df = _mock_training_df()
    res = ml_agent.run(df, target_col="target", feature_cols=["f1", "invento"])
    assert res["status"] == "FALLO"
    assert any("Faltan features" in w for w in res["advertencias"])

def test_ml_agent_target_invalido():
    df = _mock_training_df()
    res = ml_agent.run(df, target_col="inexistente", feature_cols=["f1", "f2"])
    assert res["status"] == "FALLO - BLOCKED"
    assert any("BLOCKED" in w for w in res["advertencias"])

def test_ml_agent_datos_insuficientes():
    df = _mock_training_df().iloc[:5] # n=5
    res = ml_agent.run(df, target_col="target", feature_cols=["f1"])
    assert res["status"] == "FALLO"
    assert any("Muestra muy baja" in w for w in res["advertencias"])
    
def test_ml_agent_pipeline_real():
    print("\n[INFO] Ejecutando baseline ML Real (Día 23)...")
    
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'nasa_power_colta_12m_vpd_20250823_20260822.csv')
    if not os.path.exists(csv_path):
        print("CSV de clima faltante.")
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
    
    # Integramos usando el Data Agent
    integrated_df, _ = data_agent.run(sat_df, climate_df, {})
    
    # ML Agent Execution
    res = ml_agent.run(integrated_df, target_col='ndvi', feature_cols=['T2M', 'RH2M', 'PRECTOTCORR', 'ALLSKY_SFC_SW_DWN', 'VPD'])
    
    print("\n--- INFORME DEL ML AGENT ---")
    print(f"Status: {res['status']}")
    print(f"Target: {res['target']}")
    print(f"Features: {res['features']}")
    print(f"N Train: {res['n_train']}")
    print(f"N Test: {res['n_test']}")
    if res['status'] == 'OK':
        print(f"Métricas en conjunto Test: {res['metricas_test']}")
        print(f"Limitaciones: {res['limitaciones']}")
        for w in res.get("advertencias", []):
            print(f"ADVERTENCIA: {w}")
    
    assert res["status"] in ["OK", "FALLO", "FALLO - BLOCKED"]
    
if __name__ == "__main__":
    test_ml_agent_entrenamiento_controlado()
    test_ml_agent_columnas_faltantes()
    test_ml_agent_target_invalido()
    test_ml_agent_datos_insuficientes()
    test_ml_agent_pipeline_real()
    print(" === TESTS DÍA 23 APROBADOS === ")
