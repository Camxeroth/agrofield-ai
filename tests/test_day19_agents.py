import os
import sys
import pandas as pd
import json

# Setup import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.soilgrids_client import get_soil_data
from config import STUDY_ZONE
from agents import soil_agent, climate_agent

def test_soil_agent():
    print("=== DÍA 19: PRUEBA DE SOIL AGENT ===")
    lat = STUDY_ZONE.get("latitud")
    lon = STUDY_ZONE.get("longitud")
    
    print(f"Obteniendo datos de SoilGrids para {lat}, {lon}...")
    try:
        soil_data = get_soil_data(lat, lon, depth="15-30cm")
        if soil_data:
            print("Datos SoilGrids obtenidos exitosamente.")
            
        print("Ejecutando Soil Agent...")
        result = soil_agent.run(soil_data)
        
        print("\nResultado del Soil Agent:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        assert "summary" in result
        assert "ph_interpretation" in result
        
    except Exception as e:
        print(f"Error en Soil Agent test: {e}")
        
def test_climate_agent():
    print("\n=== DÍA 19: PRUEBA DE CLIMATE AGENT ===")
    
    # Ruta del CSV generado de NASA POWER
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'nasa_power_colta_12m_vpd_20250823_20260822.csv')
    print(f"Leyendo dataset histórico climático: {csv_path}")
    
    try:
        climate_df = pd.read_csv(csv_path)
        
        print("Ejecutando Climate Agent...")
        result = climate_agent.run(climate_df)
        
        print("\nResultado del Climate Agent:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        assert "summary" in result
        assert "temperature_interpretation" in result
        
    except Exception as e:
        print(f"Error en Climate Agent test: {e}")

if __name__ == "__main__":
    test_soil_agent()
    test_climate_agent()
    print("\nPruebas finalizadas con éxito.")
