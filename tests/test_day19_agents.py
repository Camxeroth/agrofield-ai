import os
import sys
import pandas as pd
import json

# Setup import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.soilgrids_client import get_soil_data
from config import STUDY_ZONE
from agents import soil_agent, climate_agent

def test_soil_thresholds():
    # pH tests
    assert "encalado" in soil_agent.interpret_ph(4.9).lower()
    assert "óptimo" in soil_agent.interpret_ph(6.0).lower()
    assert "aceptable" in soil_agent.interpret_ph(7.0).lower()
    assert "sarna común" in soil_agent.interpret_ph(8.0).lower()
    
    # SOC tests
    assert "bajo" in soil_agent.interpret_soc(1.5).lower()
    assert "medio" in soil_agent.interpret_soc(3.0).lower()
    assert "alto" in soil_agent.interpret_soc(5.0).lower()

def test_climate_thresholds():
    # VPD tests
    assert "bajo" in climate_agent.interpret_vpd(0.4).lower()
    assert "rango de referencia" in climate_agent.interpret_vpd(0.8).lower()
    assert "alto" in climate_agent.interpret_vpd(1.5).lower()
    
    # Temp tests
    assert "muy fría" in climate_agent.interpret_temperature(7.0, 5, 10).lower()
    assert "óptima" in climate_agent.interpret_temperature(12.0, 10, 15).lower()
    assert "moderadamente altas" in climate_agent.interpret_temperature(18.0, 10, 20).lower()
    assert "excesivas" in climate_agent.interpret_temperature(25.0, 10, 30).lower()

def test_soil_agent_real_data():
    lat = STUDY_ZONE.get("latitud")
    lon = STUDY_ZONE.get("longitud")
    soil_data = get_soil_data(lat, lon, depth="15-30cm")
    
    assert isinstance(soil_data, dict), "soil_data debe ser un diccionario"
    
    result = soil_agent.run(soil_data)
    
    assert isinstance(result, dict)
    assert "summary" in result
    assert isinstance(result["summary"], str)
    
    assert "ph_interpretation" in result
    assert isinstance(result["ph_interpretation"], str)
    
    assert "organic_carbon_interpretation" in result
    assert isinstance(result["organic_carbon_interpretation"], str)
    
    assert "texture_interpretation" in result
    assert isinstance(result["texture_interpretation"], str)
    
    assert "agronomic_notes" in result
    assert isinstance(result["agronomic_notes"], list)
    
    print("\n[OK] Soil Agent testeado exitosamente con datos reales.")

def test_climate_agent_real_data():
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'nasa_power_colta_12m_vpd_20250823_20260822.csv')
    assert os.path.exists(csv_path), f"El archivo dataset no existe: {csv_path}"
    
    climate_df = pd.read_csv(csv_path)
    assert not climate_df.empty, "El DataFrame crudo está vacío"
    
    result = climate_agent.run(climate_df)
    
    assert isinstance(result, dict)
    assert "summary" in result
    assert isinstance(result["summary"], str)
    
    assert "temperature_interpretation" in result
    assert isinstance(result["temperature_interpretation"], str)
    
    assert "precipitation_interpretation" in result
    assert isinstance(result["precipitation_interpretation"], str)
    
    assert "vpd_interpretation" in result
    assert isinstance(result["vpd_interpretation"], str)
    
    assert "agronomic_notes" in result
    assert isinstance(result["agronomic_notes"], list)
    
    print("\n[OK] Climate Agent testeado exitosamente con datos reales.")

if __name__ == "__main__":
    test_soil_thresholds()
    test_climate_thresholds()
    test_soil_agent_real_data()
    test_climate_agent_real_data()
    print("\n=== TODOS LOS TESTS PASARON EXITOSAMENTE ===")
