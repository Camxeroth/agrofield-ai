import pandas as pd
from typing import Dict, Any, Tuple

def run(satellite_df: pd.DataFrame, climate_df: pd.DataFrame, soil_data: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Integra datos satelitales, climáticos y de suelo en un único dataset analítico.
    
    Estrategia de integración:
    - Se toma como base temporal el satélite (fechas específicas de paso/observación).
    - Se cruza (Left Join) con los datos climáticos usando la fecha exacta.
    - Se incorporan los datos del suelo como constantes espaciales para la zona.
    
    Args:
        satellite_df: DataFrame con series temporales satelitales (date, ndvi, ndwi, etc.)
        climate_df: DataFrame con series climáticas diarias (fecha, T2M, PRECTOTCORR, VPD, etc.)
        soil_data: Diccionario con variables de suelo constantes.
        
    Returns:
        Tupla con:
        1. DataFrame integrado.
        2. Diccionario con metadatos y calidad de datos.
    """
    quality_report = {
        "warnings": [],
        "missing_values": {}
    }
    
    if satellite_df is None or satellite_df.empty:
        quality_report["warnings"].append("Dataset satelital vacío o nulo.")
        return pd.DataFrame(), quality_report
        
    if climate_df is None or climate_df.empty:
        quality_report["warnings"].append("Dataset climático vacío o nulo.")
        return pd.DataFrame(), quality_report
        
    # Copiar para no mutar originales
    sat_df = satellite_df.copy()
    clim_df = climate_df.copy()
    
    # Normalizar fechas a datetime para integración segura
    if 'date' in sat_df.columns:
        sat_df['date'] = pd.to_datetime(sat_df['date']).dt.normalize()
    else:
        quality_report["warnings"].append("La columna 'date' no existe en satellite_df.")
        return pd.DataFrame(), quality_report
        
    if 'fecha' in clim_df.columns:
        clim_df['fecha'] = pd.to_datetime(clim_df['fecha']).dt.normalize()
    else:
        quality_report["warnings"].append("La columna 'fecha' no existe en climate_df.")
        return pd.DataFrame(), quality_report
        
    # Validar duplicados temporales en el satélite
    dup_sat = sat_df['date'].duplicated().sum()
    if dup_sat > 0:
        quality_report["warnings"].append(f"Se encontraron {dup_sat} fechas duplicadas en satellite_df. Mantenemos la primera ocurrencia.")
        sat_df = sat_df.drop_duplicates(subset=['date'], keep='first')
        
    # Integración temporal: Satélite Left Join Clima (Exact Date)
    integrated = pd.merge(
        sat_df, 
        clim_df, 
        left_on='date', 
        right_on='fecha', 
        how='left'
    )
    
    # Eliminar columna redundante 'fecha'
    if 'fecha' in integrated.columns:
        integrated = integrated.drop(columns=['fecha'])
        
    # Agregar variables de suelo como características estáticas
    if isinstance(soil_data, dict):
        integrated['soil_ph'] = soil_data.get('phh2o', {}).get('valor', pd.NA) if isinstance(soil_data.get('phh2o'), dict) else pd.NA
        integrated['soil_soc'] = soil_data.get('soc', {}).get('valor', pd.NA) if isinstance(soil_data.get('soc'), dict) else pd.NA
        integrated['soil_sand'] = soil_data.get('sand', {}).get('valor', pd.NA) if isinstance(soil_data.get('sand'), dict) else pd.NA
        integrated['soil_silt'] = soil_data.get('silt', {}).get('valor', pd.NA) if isinstance(soil_data.get('silt'), dict) else pd.NA
        integrated['soil_clay'] = soil_data.get('clay', {}).get('valor', pd.NA) if isinstance(soil_data.get('clay'), dict) else pd.NA
    else:
        quality_report["warnings"].append("soil_data no es un diccionario válido o está vacío. Valores insertados como NA.")
        cols = ['soil_ph', 'soil_soc', 'soil_sand', 'soil_silt', 'soil_clay']
        for c in cols:
            integrated[c] = pd.NA
            
    # Calcular y registrar calidad
    nans = integrated.isna().sum()
    missing_dict = nans[nans > 0].to_dict()
    quality_report["missing_values"] = missing_dict
    
    if len(missing_dict) > 0:
        quality_report["warnings"].append(f"Valores faltantes introducidos durante integración en: {list(missing_dict.keys())}")
        
    return integrated, quality_report
