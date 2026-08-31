# Día 13 - Agente + Validación del Pipeline Completo

## Objetivo
Validar formalmente el pipeline completo de datos desde la extracción inicial hasta el dataset:
`Earth Engine → Sentinel-2 → Extraer B3/B4/B8 → Cálculos NDVI/NDWI en la nube → Dataframe tabular pandas`.

## Arquitectura del Pipeline
* **Sistema Principal**: `src/data/ee_extractor.py` usando EE SDK en Python.
* **Procesamiento Espacial**: Utilización de *reducers* vectorizados (`ee.Reducer.mean`) para transformar raster cloud computing puro en datos vectoriales de punto (`(-78.65, -1.63)`).
* **Configuración EE**: Proyecto autenticado exitosamente bajo el ID `agrofield-ai-chimborazo`. Autenticación pasiva local sin credenciales duras.

## Datos Obtenidos y Validaciones
Ejecutando el extractor con filtro de nubes (`< 20%`) sobre el área andina entre `2026-05-01` y `2026-08-31`, filtramos hasta **1 única fecha validada** útil: `2026-07-29`.

### Validación Física (Bandas)
En la comprobación se extrajeron y confirmaron los valores:
* B3 (Verde): 1320
* B4 (Rojo): 1595
* B8 (NIR): 2352
*(Coincidencia 100% con los datos analizados manualmente).*

### Validación Matemática (Índices GEE vs Python)
* NDVI Earth Engine: `0.191791`
* NDWI Earth Engine: `-0.281046`

Se ha verificado que la operación matemática remota de Google Earth Engine procesada por el framework matriz coincide de forma milimétrica (tolerancia de 4 decimales o superior) con la implementación estándar manual de `src/features/indices.py`.

## Pruebas (Tests)
* Hemos expandido los tests de integración en `tests/test_ee_integration.py` con `assertions` muy estrictas respecto a las bandas extraídas y los índices generados. Resultado: **PASSED**.

## Limitaciones Generales Actuales
* **Cantidad de Observaciones**: La colección está reducida a la mínima expresión poblacional por las implacablemente duras condiciones de la cubierta nubosa (Cloud Cover) en esa zona geográfica. Solo un 3% de las imágenes sobrevivió al umbral conservador de `20%` entero.
