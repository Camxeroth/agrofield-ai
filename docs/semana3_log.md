# Bitácora de la Semana 3 — AgroField AI

## Semana 3 — Suelo + Estadística + Ecuador

### Día 15
* **Objetivo:** Investigación teórica y diseño de extracción sobre bases de datos espaciales orientadas a la edafología y al contexto agrícola de Ecuador.
* **Qué se hizo:** Exploración inicial de SoilGrids (ISRIC).
* **Resultado:** Se establecieron los endpoints correspondientes para Colta y el mecanismo principal utilizando una representación REST.
* **Archivos relevantes:** Documentación inicial.
* **Aprendizaje:** Mapeo de perfiles de suelo requiere lidiar con la distribución espacial suavizada en resoluciones de 250m, dictando conversiones precisas operando los _d_factors_ (factores de división).
* **Limitaciones:** Los datos espaciales estáticos carecen de series temporales; un suelo hoy es modelado igual que hace un año en la matriz.

### Día 16
* **Objetivo:** Obtención programática de parámetros de suelo relevantes limitados a la altitud de la capa de siembra (papa).
* **Qué se hizo:** Implementación de la captura computacional mediante Python y Requests a ISRIC.
* **Resultado:** Función `get_soil_data()` completada y validada en el script cliente.
* **Archivos relevantes:** `src/data/soilgrids_client.py`
* **Aprendizaje:** El valor bruto devuelto necesita conversiones químicas importantes (ex. Materia Orgánica a escala de %, y las diferentes granulometrías estandarizadas a suma $100\%$).
* **Limitaciones:** Vulnerabilidad operativa por tiempos de latencia o fallos de red externos al consultar la base de datos REST.

### Día 17
* **Objetivo:** Adición del marco contextual de agronomía pública nacional en Ecuador.
* **Qué se hizo:** Estudio de reportes operativos agronómicos desde los repositorios web nacionales de SIPA (Sistema de Información Pública Agropecuaria) y ESPAC.
* **Resultado:** Establecidos y estudiados documentalmente los promedios esperados de las regiones productoras, que enmarcan estadísticamente la viabilidad del cantón Colta para el cultivo de papa.
* **Limitaciones:** Estos datos no poseen APIs granulares por coordenadas, limitando su automatización de extracción paralela en CSV o JSON. Sirven como anclaje teórico.

### Día 18
* **Objetivo:** Diseño, verificación y comprensión del cálculo matemático que emparejará a los factores satelitales con las métricas meteorológicas y del ambiente.
* **Qué se hizo:** Un repaso del Coeficiente de Correlación de Pearson ($r$). Comprobación manual.
* **Resultado:** Cálculo exacto ejecutado verificando cómo las covarianzas se relacionan.
* **Archivos relevantes:** Anclaje metodológico que luego dio vida matemática a `agents/statistics_agent.py`.
* **Aprendizaje:** Si la varianza de una métrica dada en toda la sección transversal evaluada es 0, Pearson es incalculable (devuelve error matemático).

### Día 19
* **Objetivo:** Encapsular la lógica interpretativa en la nueva capa estructural del proyecto: **Los Agentes**.
* **Qué se hizo:** Creación de `Soil Agent` y `Climate Agent`. Estos agentes aíslan el procesamiento del raciocinio heurístico inicial.
* **Resultado:** Scripts de Python expuestos mediante funciones principales `run(data)` que documentan explícitamente sus valoraciones frente a una lluvia moderada o a un nivel de texturas.
* **Archivos relevantes:** `agents/soil_agent.py`, `agents/climate_agent.py`, `docs/dia19_agents.md`.
* **Aprendizaje:** La separación imperativa: las transformaciones API no pertenecen al _Agent_. El agente solo raciocina métricas puras y devuelve objetos que encapsulan hallazgos y variables.
* **Limitaciones:** Las reglas codificadas constituyen deducciones heurísticas muy tempranas de una tabla genérica; esto no conforma algoritmos profundos fenológicos para la papa, no predice enfermedades y emite "Notas", no juicios sentenciados.

### Día 20
* **Objetivo:** Interceptar las mediciones a lo largo de las capas heterogéneas, consolidar el _Data Lake_ y emitir validación técnica pura.
* **Qué se hizo:** Desarrollo del `Data Agent` (que utiliza un barrido espacial/temporal para alinear el satélite intermitente Sentinel-2 a la cuadrícula temporal estricta de NASA POWER, inyectando las constantes estáticas de SoilGrids). Y del `Statistics Agent` (validador paramétrico excluyente).
* **Resultado:** Matriz de datos única transversal (53 observaciones útiles anuales) + Matriz de Correlación. Pearson fue implementaron Python por completo (Pandas iterando el $r$ manual del Día 18).
* **Archivos relevantes:** `agents/data_agent.py`, `agents/statistics_agent.py`, `docs/dia20_data_statistics.md`.
* **Aprendizaje:** La escasez de las visitas libres de nube en el sur de Chimborazo en Sentinel-2 dictamina el nivel de registros totales. Para no generar series temporales vacías (NaNs inútiles) el dataset final se accla al satélite y se arrastra el clima a él (*Left Join* puro).
* **Limitaciones:** Un estudio de retraso temporal (Lags biológicas). No se midió cómo el clima de 1 mes previo impacta, solo el paralelo diario directo. La correlación obtenida asiste biológicamente pero no concluye causalidad final agronómica. SoilGrids posee varianza nula localmente.

### Día 21
* **Objetivo:** Cierre documental contundente, trazar la procedencia de datos global en un punto de verificación y delinear los pilares de limitación.
* **Qué se hizo:** Creación de la Bitácora Semanal 3, trazabilidad `docs/data_provenance.md` detallando las fuentes, mapeo exhaustivo de lo investigado (SIPA, NASA, Earth Engine, SoilGrids). 
* **Resultado:** Auditoría formal y refinamiento de `README.md`.
* **Archivos relevantes:** Documentación integral, bitácoras.

---

## Hallazgos Preliminares (Semana 3)

### Observaciones Directas (Lo observable local)
* En Colta (coordenadas: -1.718, -78.764) existen vacíos masivos temporales en la reflectancia multiespectral del Satélite Sentinel-2 en los meses de lluvias cerradas debido a persistente cobertura nubosa densa.
* La precipitación diaria acumulada por NASA POWER en los rangos recientes anuales muestra un comportamiento elevado con alta presencia de picos (>5 mm diarios distribuidos).

### Interpretaciones Heurísticas
* El `Climate Agent` clasifica las franjas térmicas promedio registradas (aprox. 11.4 °C) dentro de su índice computado como **óptimas** o cercanas al óptimo para la fenología natural de la tuberización en cultivos interandinos; un frío que previene brotaciones prematuras o acorta ciclo pero provee vigor sin quemaduras masivas (estrés por calor).
* El pH arrojado por SoilGrids sobre los 15-30cm es consistentemente reportado por la heurística inicial del `Soil Agent` en un registro aceptativamente inclinado hacia la alcalinidad ($pH \sim 6.6$), sugiriendo atenta suplementación focal si los fertilizantes aplicados exudan alcalinidad reaccionante.
* El perfil del VPD computado marca recurrentes bajadas pronunciadas por alta presión hídrica de nube, interpretado tempranamente como **limitante a la transpiración local**.

### Hallazgos Estadísticos
* Utilizando un _sample size_ final de $N=53$ observaciones resultantes útiles tras cruzar las fuentes en el Data Agent para un periodo continuo estipulado interanual, el `Statistics Agent` procesó los índices por correlación bivariada de *Pearson*.
* Se observó una asociación lineal débil-positiva unificada en el mismo escalón de día cruzando foliaje frente a demanda climática $NDVI \leftrightarrow T2M$ revelando una $r \approx 0.178$. (Asociación validada computacionalmente sin ruido de _NaN_ estáticos).

### Limitaciones Sistémicas Aclaradas 
La validación oficial en el Día 21 dictamina formalmente para todo usuario del sistema que:
* **Correlación $\ne$ Causalidad.** Ninguna estadística del Día 20 afirma "X causa Y". Todas las derivaciones de `r` se presentan bajo la advertencia de que la asociación lineal paramétrica calculada en el proyecto describe correlación sin atribuir todavía dependencia biológica exclusiva. La continuidad del Día 18 al Día 20 está cumplida.
* **Heurísticas.** Todos los "mensajes" dictados hoy en día por el SoilAgent y ClimateAgent sobre la "Idoneidad para papa" son interpretaciones heurísticas simplificadas propias a *AgroField* y no sentencian recomendaciones absolutas. (Carencias: Triángulo de texturas oficial estricto o un modelado integral de enfermedades como tízón o sarna originada estrictamente en el suelo medido por satélite).
* **Ausencias estructurales actuales:** Aún no subsisten predicciones de _Machine Learning_, un _Orchestrator_ que encadena conversacionalmente estas salidas crudas, algoritmos cognitivos generativos de resúmenes textuales de contexto agronómico humano real _RAG_. Todo corresponde a proyecciones futuras (Semana 4 y adelante). Las interrupciones intermitentes de APIs como ISRIC o fallos geodésicos en NASA POWER son variables posibles fuera de tolerancia por el script. Tamaño de la muestra dictado fuertemente por días nublados de Ecuador que estrangulan observaciones Sentinel-2.

---
_Bitácora generada durante el Cierre de la Semana 3 de Desarrollo de AgroField AI_
