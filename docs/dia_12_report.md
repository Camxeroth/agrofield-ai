# Día 12 - Automatizar serie temporal NDVI/NDWI con Earth Engine

## Implementación

Se ha creado la clase `EarthEngineExtractor` en `src/data/ee_extractor.py` para automatizar la extracción de datos satelitales.

### Detalles de la Extracción
* **Fuente Satelital**: `COPERNICUS/S2_SR_HARMONIZED` (Sentinel-2 Surface Reflectance Harmonized).
* **Período Analizado**: Implementado dinámicamente, con expectativas normales de cubrir los últimos 3 meses (ej. 2026-05-01 a 2026-08-31).
* **Filtro de Nubosidad**: Seleccionamos imágenes con `CLOUDY_PIXEL_PERCENTAGE < 20`.
* **Punto Utilizado**: Las coordenadas `(-78.65, -1.63)` de Cajabamba, manejado como un objeto `ee.Geometry.Point`.
* **Método de Extracción**: Se utilizó `reduceRegion` con el reductor `ee.Reducer.mean()` en escala 10m para obtener los valores del pixel sobre el punto exacto.
* **Estructura del Dataset**: Generamos un `pandas.DataFrame` tabular con: `date`, `ndvi`, `ndwi`, `cloud_percentage`, `B3`, `B4` y `B8`.

### Cálculo de Índices
Para optimizar el uso de Google Earth Engine, hemos decidido aplicar el cálculo de los índices a través de operaciones matriciales/nativas de nube espacial en lugar de extraer todas las bandas brutas y mandarlas por la red para que Python local `calculate_ndvi` las calcule:
- `image.normalizedDifference(['B8', 'B4'])`
- `image.normalizedDifference(['B3', 'B8'])`
Esto reduce drásticamente el peso de las comunicaciones y mantiene la eficiencia del procesamiento en la nube, entregando valores pre-computados muy rápidos (solo recibimos el valor final un punto).

### Validación (Reporte de Problema)

Durante la validación de Earth Engine detectamos un problema de configuración de cuenta:
```text
ee.EEException: ee.Initialize: no project found. Call with project= or see http://goo.gle/ee-auth.
```
**Problema encontrado**: La API de EE ahora requiere firmemente que las llamadas estén asociadas con un proyecto activo de GCloud (GCP project). La configuración local actual tiene tokens guardados, pero carece del proyecto asignado. 

**Solución aplicada a la arquitectura**: 
Hemos modificado el código para manejar el error graciosamente y alertar al usuario antes del colapso, solicitándole especificar el proyecto en el inicializador o en el entorno de Google CLI.
**Acción requerida del analista humano**:
Debes ejecutar el siguiente comando en consola remplazando con el ID de tu proyecto Google Cloud activo:
```bash
earthengine set_project <tu-proyecto-gcp>
```

Por lo tanto, la ejecución real queda pendiente a que se asocie el proyecto en el CLI y luego extraiga la tabla para la validación exacta de las fechas. Ninguna credencial ni ID de proyecto sensible fue expuesta o incluida en el repositorio (.gitignore y código están limpios).
