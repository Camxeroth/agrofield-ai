import ee
import pandas as pd

class EarthEngineExtractor:
    def __init__(self, project='agrofield-ai-chimborazo'):
        """
        Inicializa la conexión con Earth Engine utilizando credenciales locales.
        Si la inicialización falla por falta de proyecto, lanza una advertencia.
        """
        try:
            if project:
                ee.Initialize(project=project)
            else:
                ee.Initialize()
        except ee.EEException as e:
            print(f"Error de inicialización de Earth Engine: {e}")
            print("Por favor, asegúrate de tener un proyecto configurado o pasa el 'project' al inicializar.")
            print("Para solucionarlo localmente, ejecuta: earthengine set_project <tu-proyecto-gcp>")
            raise

    def get_sentinel2_timeseries(self, lon, lat, start_date, end_date):
        """
        Extrae la serie temporal de NDVI y NDWI para un punto dado.
        
        Args:
            lon (float): Longitud del punto.
            lat (float): Latitud del punto.
            start_date (str): Fecha de inicio en formato 'YYYY-MM-DD'.
            end_date (str): Fecha de fin en formato 'YYYY-MM-DD'.
            
        Returns:
            pd.DataFrame: DataFrame con las observaciones ordenadas por fecha.
        """
        point = ee.Geometry.Point([lon, lat])
        
        # Filtramos por nuestra área de estudio, tiempo y una tolerancia razonable de nubes
        collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                      .filterBounds(point)
                      .filterDate(start_date, end_date)
                      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))
                      
        def extract_point(image):
            date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd')
            cloud = image.get('CLOUDY_PIXEL_PERCENTAGE')
            
            # Cálculos directos usando operaciones vectorizadas en GEE
            # NDVI = (B8 - B4) / (B8 + B4)
            ndvi = image.normalizedDifference(['B8', 'B4']).rename('ndvi')
            # NDWI = (B3 - B8) / (B3 + B8)
            ndwi = image.normalizedDifference(['B3', 'B8']).rename('ndwi')
            
            img_indices = image.addBands([ndvi, ndwi])
            
            # Extracción del valor del pixel correspondiente al punto
            stats = img_indices.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point,
                scale=10,
                maxPixels=1e9
            )
            
            return ee.Feature(None, {
                'date': date,
                'cloud_percentage': cloud,
                'ndvi': stats.get('ndvi'),
                'ndwi': stats.get('ndwi'),
                'B4': stats.get('B4'),
                'B8': stats.get('B8'),
                'B3': stats.get('B3')
            })
            
        # Ejecución coordinada (evaluación perezosa materializada aquí)
        features = collection.map(extract_point).getInfo()['features']
        
        records = []
        for f in features:
            props = f['properties']
            records.append({
                'date': props.get('date'),
                'ndvi': props.get('ndvi'),
                'ndwi': props.get('ndwi'),
                'cloud_percentage': props.get('cloud_percentage'),
                'B3': props.get('B3'),
                'B4': props.get('B4'),
                'B8': props.get('B8')
            })
            
        df = pd.DataFrame(records)
        if not df.empty:
            df = df.sort_values('date').reset_index(drop=True)
            
        return df
