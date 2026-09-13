# Data Provenance y Trazabilidad — AgroField AI

## 1. Procedencia de Datos (Data Provenance)

¿De dónde salió cada dato utilizado por AgroField AI?

### Fuente 1: NASA POWER
* **Institución/Proveedor:** NASA Langley Research Center (POWER Project)
* **Tipo de datos:** Series temporales meteorológicas y de radiación solar.
* **Variables utilizadas:** 
  * `T2M` (Temperatura a 2m, °C)
  * `PRECTOTCORR` (Precipitación Corregida, mm/día)
  * `RH2M` (Humedad Relativa a 2m, %)
  * `ALLSKY_SFC_SW_DWN` (Insolación Incidente, MJ/m²/día)
* **Resolución espacial:** Resolución global nativa satelital (0.5° x 0.5°).
* **Resolución temporal:** Diaria.
* **Periodo utilizado:** 2025-08-23 a 2026-08-22 (12 meses).
* **Formato original:** JSON (API REST).
* **Módulo responsable:** `pipeline_dia6.py`
* **Transformación y Unidad:** 
  * Se calcularon índices derivados locales como Déficit de Presión de Vapor (VPD) en `kPa`.
  * Los NaNs (originalmente `-999.0`) se transformaron a `np.nan`.
* **Limitaciones:** Datos derivados por asimilación de modelos globales y observaciones por satélite; no corresponden a una estación meteorológica física estática instalada en la parcela.
* **Uso:** Construir el historial de temperatura, humedad disponible, y demanda atmosférica de la zona del cultivo de referencia.

### Fuente 2: Sentinel-2
* **Institución/Proveedor:** Agencia Espacial Europea (ESA) / Copernicus — a través de Google Earth Engine (GEE).
* **Tipo de datos:** Observaciones satelitales multiespectrales (SR - Surface Reflectance).
* **Variables utilizadas:** 
  * Banda `B4` (Red)
  * Banda `B8` (NIR)
  * Banda `B3` (Green)
* **Resolución espacial:** 10 metros por píxel.
* **Resolución temporal:** Revisita nominal ~5 días (condicionado a la ausencia de nubes).
* **Periodo utilizado:** Intervalo estacional (ej. Junio a Agosto 2026) dependiente de la limitación temporal ingresada y las tolerancias a nubes (hasta 90% para captura).
* **Formato original:** ImageCollection (Cloud API/GEE).
* **Módulo responsable:** `src/data/ee_extractor.py`.
* **Transformación y Unidad:** 
  * Bandas pasadas a índices vegetales espectrales normalizados calculados en GEE: `NDVI` y `NDWI` (adimensionales, escala de -1 a 1).
* **Limitaciones:** En zonas interandinas como Colta, la cobertura nubosa descarta hasta el 80% o 90% de las visitas, provocando vacíos de información o baja disponibilidad de observaciones puras utilizables en cortos rangos.
* **Uso:** Determinar el vigor fotosintético foliar (NDVI) y estrés hídrico de la canopia (NDWI).

### Fuente 3: SoilGrids v2.0
* **Institución/Proveedor:** ISRIC - World Soil Information.
* **Tipo de datos:** Propiedades físicas y químicas predictivas espaciales edafológicas.
* **Variables utilizadas:** 
  * `phh2o` (pH en H2O)
  * `soc` (Carbono Orgánico del Suelo)
  * `sand` (Fracción de Arena)
  * `silt` (Fracción de Limo)
  * `clay` (Fracción de Arcilla)
* **Resolución espacial:** 250 metros.
* **Resolución temporal:** Modelos espaciales estáticos basados en machine learning sobre perfiles recolectados globalmente.
* **Profundidad/Capa (Periodo utilizado):** Capa "15-30cm", aproximando las raíces principales de la papa.
* **Formato original:** JSON (REST API `rest.isric.org`).
* **Módulo responsable:** `src/data/soilgrids_client.py`.
* **Transformación y Unidad:** 
  * pH escalado de vuelta a unidades base pH estandar (factor de 10).
  * Carbono transformado de `dg/kg` a % (peso).
  * Texturas transformadas de gramos por kilo a porcentajes purificados (%), manteniendo aproximaciones del total de la materia mineral al 100%.
* **Limitaciones:** Modelos globales que suavizan la heterogeneidad a nivel de lote. Falta de validación y variabilidad intra-parcela. La API tiene eventuales demoras y timeouts.
* **Uso:** Identificar barreras texturales abióticas o de fertilidad de materia orgánica en el lote.

*(Notas institucionales como SIPA o ESPAC fueron exploradas teóricamente para contextualizar a la zona, pero la implementación final se sustenta sobre ejes climáticos/satelitales/SoilGrids).*

---

## 2. Mapa de Trazabilidad de los Datos

La arquitectura mantiene el principio de que los módulos intermedios purifican los datos antes de inyectarlos a los agentes:

### Suelo
```text
(ISRIC) SoilGrids API
         ↓
get_soil_data() [src/data/soilgrids_client.py]
         ↓
soil_data (Diccionario unificado tipificado)
         ↓
Soil Agent [agents/soil_agent.py]
         ↓
Interpretación heurística simplificada
```

### Clima
```text
(NASA POWER REST)
         ↓
pipeline_dia6.py
         ↓
nasa_power_colta_12m_vpd_20250823_20260822.csv (Archivo local cacheado)
         ↓
pd.DataFrame()
         ↓
Climate Agent [agents/climate_agent.py]
         ↓
Promedios climáticos y heurística de temperatura/demanda evaporativa
```

### Satélite + Integración de la Trazabilidad Final (Día 20)
```text
Sentinel-2 (Copernicus / GEE)
         ↓
EarthEngineExtractor [src/data/ee_extractor.py]
         ↓
sat_df (DataFrame)
         ↓
Data Agent [agents/data_agent.py] ← ( + climate_df + soil_data )
         ↓
merged_df (Dataset integrado con 'date' como índice maestro cruzado)
         ↓
Statistics Agent [agents/statistics_agent.py]
         ↓
Correlación de Pearson y Estadísticas.
```
