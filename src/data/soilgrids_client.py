import requests

def get_soil_data(lat, lon, depth="15-30cm"):
    """
    Consulta SoilGrids V2.0 REST API para obtener propiedades del suelo en una 
    ubicación específica (latitud y longitud) y profundidad.
    
    Variables extraídas:
    - phh2o: pH del suelo
    - soc: Carbono Orgánico del Suelo (convertido a %)
    - sand: Textura - Arena (convertido a %)
    - silt: Textura - Limo (convertido a %)
    - clay: Textura - Arcilla (convertido a %)
    
    Args:
        lat (float): Latitud.
        lon (float): Longitud.
        depth (str): Profundidad a consultar. Opciones: "0-5cm", "5-15cm", "15-30cm", 
                     "30-60cm", "60-100cm", "100-200cm". Recomendado: "15-30cm" 
                     para la zona radicular principal de la papa.
                     
    Returns:
        dict: Diccionario con los valores convertidos a sus unidades finales.
    """
    # Endpoint oficial de ISRIC para SoilGrids V2.0 Puntos
    base_url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    
    # Parámetros de la consulta
    params = {
        "lat": lat,
        "lon": lon,
        "property": ["phh2o", "soc", "sand", "silt", "clay"],
        "depth": depth,
        "value": "mean" # Se pide explicitamente el promedio p/ la distribución espacial
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=15)
        response.raise_for_status() # Lanza excepción para códigos 4xx o 5xx
        data = response.json()
        
        # Estructuramos los resultados
        results = {
            "latitud": lat,
            "longitud": lon,
            "profundidad": depth
        }
        
        layers = data.get("properties", {}).get("layers", [])
        
        if not layers:
            raise ValueError("No se encontraron capas (layers) en la respuesta de SoilGrids.")
            
        for layer in layers:
            name = layer.get("name")
            unit_measure = layer.get("unit_measure", {})
            d_factor = unit_measure.get("d_factor", 10)
            
            # Buscar el valor de la profundidad seleccionada
            depths_info = layer.get("depths", [])
            for d in depths_info:
                if d.get("label") == depth:
                    values = d.get("values", {})
                    mean_val = values.get("mean")
                    
                    if mean_val is not None:
                        # Conversión a unidades interpretables:
                        # - pH: factor 10, de pH*10 -> pH
                        # - texturas (sand, silt, clay): g/kg a % (se divide por 10)
                        # - carbono orgánico (soc): dg/kg a %, 10 dg = 1g -> g/kg a % -> factor total 100
                        if name == "soc":
                            converted_val = mean_val / 100.0 # dg/kg a %
                            unit_final = "% (peso)"
                        else:
                            converted_val = mean_val / float(d_factor)
                            if name in ["sand", "silt", "clay"]:
                                unit_final = "%"
                            elif name == "phh2o":
                                unit_final = "pH"
                            else:
                                unit_final = unit_measure.get("target_units")
                        
                        results[name] = {
                            "valor": converted_val,
                            "unidad": unit_final,
                        }
                    break
        
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con SoilGrids: {e}")
        return None
    except Exception as e:
        print(f"Error al procesar los datos de SoilGrids: {e}")
        return None

if __name__ == "__main__":
    from config import STUDY_ZONE
    lat = STUDY_ZONE["latitud"]
    lon = STUDY_ZONE["longitud"]
    
    print("=== DÍA 16: PRUEBA DE get_soil_data() ===")
    print(f"Consultando coordenadas: Lat {lat}, Lon {lon}")
    data = get_soil_data(lat, lon, depth="15-30cm")
    
    import json
    print(json.dumps(data, indent=2, ensure_ascii=False))
