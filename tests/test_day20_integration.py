import os
import sys
import pandas as pd
import json

# Setup import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.ee_extractor import EarthEngineExtractor
from agents import data_agent, statistics_agent
from config import STUDY_ZONE

def _create_mock_sat_data():
    return pd.DataFrame({
        'date': ['2026-01-01', '2026-01-05', '2026-01-10'],
        'ndvi': [0.12, 0.45, 0.55]
    })

def _create_mock_clim_data():
    return pd.DataFrame({
        'fecha': ['2026-01-01', '2026-01-05', '2026-01-10', '2026-01-11'],
        'T2M': [14.1, 15.2, 11.5, 12.0],
        'PRECTOTCORR': [0.0, 5.0, 10.0, 2.0]
    })

def test_data_agent_mock():
    sat = _create_mock_sat_data()
    clim = _create_mock_clim_data()
    soil = {"phh2o": {"valor": 6.0}, "sand": {"valor": 45}}
    
    integrated, qual = data_agent.run(sat, clim, soil)
    
    # Assert proper output
    assert not integrated.empty
    assert len(integrated) == 3 # Left join preserves sat dates
    assert 'date' in integrated.columns
    assert 'ndvi' in integrated.columns
    assert 'T2M' in integrated.columns
    assert 'soil_ph' in integrated.columns
    # Check constants
    assert all(integrated['soil_ph'] == 6.0)
    
def test_statistics_agent_mock():
    # Correlación matemática exacta manual test
    # x = [1, 2, 3], y = [2, 4, 6] -> correlación perfecta 1.0
    mock_integrated = pd.DataFrame({
        'date': pd.to_datetime(['2026-01-01', '2026-01-02', '2026-01-03']),
        'var_x': [1.0, 2.0, 3.0],
        'var_y': [2.0, 4.0, 6.0],
        'const_soil': [5.0, 5.0, 5.0]
    })
    
    res = statistics_agent.run(mock_integrated)
    
    assert "correlations" in res
    assert "var_x" in res["correlations"]
    
    corr_x_y = res["correlations"]["var_x"]["var_y"]
    # Debería ser 1.0 (o aproximadamente 1.0)
    assert abs(corr_x_y - 1.0) < 0.0001
    
    # const_soil debería haber sido excluida por varianza 0
    assert "const_soil" not in res["correlations"]
    assert "const_soil" in str(res["warnings"])

def test_pipeline_with_real_data():
    print("\n--- INICIANDO TEST PIPELINE CON DATOS REALES (DÍA 20) ---")
    
    # 1. CLIMA 
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'nasa_power_colta_12m_vpd_20250823_20260822.csv')
    assert os.path.exists(csv_path), "Falta el dataset climático base"
    climate_df = pd.read_csv(csv_path)
    
    # 2. SATELITE
    try:
        extractor = EarthEngineExtractor()
        # Traeremos 3 meses para ser rápidos pero usar datos vivos
        print("Trayendo datos satelitales (Earth Engine)... tardará un momento.")
        sat_df = extractor.get_sentinel2_timeseries(
            lon=STUDY_ZONE['longitud'], 
            lat=STUDY_ZONE['latitud'], 
            start_date='2025-08-23', 
            end_date='2026-08-22',
            max_clouds=90
        )
    except Exception as e:
        print(f"Error al traer datos satelitales: {e}")
        assert False, "Fallo en conexión EE"
        
    assert not sat_df.empty, "Se obtuvo un DataFrame satelital vacío."
    
    # 3. SUELO (simularemos la variable estática desde dict para no depender del timeout de API de ISRIC en el test)
    soil_data = {
        "phh2o": {"valor": 6.6},
        "soc": {"valor": 3.19},
        "sand": {"valor": 48.5},
        "silt": {"valor": 33.2},
        "clay": {"valor": 18.3}
    }
    
    # 4. DATOS -> DATA AGENT
    print("Integrando datos...")
    integrated_df, quality_report = data_agent.run(sat_df, climate_df, soil_data)
    
    assert not integrated_df.empty
    print(f"\nResultados de Integración:\nFilas: {len(integrated_df)}, Columnas: {len(integrated_df.columns)}")
    print(f"Warnings calidad: {quality_report['warnings']}")
    
    # 5. DATASET INTEGRADO -> STATISTICS AGENT
    print("\nEjecutando Statistics Agent...")
    stats_output = statistics_agent.run(integrated_df)
    
    assert "summary" in stats_output
    assert "descriptive_statistics" in stats_output
    assert "correlations" in stats_output
    
    print(f"Análisis estadístico advertencias: {stats_output['warnings']}")
    if "ndvi" in stats_output["correlations"] and "T2M" in stats_output["correlations"]["ndvi"]:
        print(f"Correlación NDVI <-> T2M : {stats_output['correlations']['ndvi']['T2M']}")
        
    print("\n[OK] PIPELINE DÍA 20 REALIZADO CON DATOS REALES")

if __name__ == "__main__":
    test_data_agent_mock()
    test_statistics_agent_mock()
    test_pipeline_with_real_data()
