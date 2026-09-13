# AgroField AI — Chimborazo

AgroField AI es un sistema de análisis agrícola avanzado, centrado en cultivos de papa en el cantón Colta, Provincia de Chimborazo, Ecuador. Este sistema busca cruzar información procedente de variables satelitales, climáticas y edafológicas, construyendo interpretaciones prudentes basadas en datos objetivos para asistir en el entendimiento fenológico y riesgos del cultivo.

## Problema que Aborda
La limitada capacidad de conectar datos climáticos (temperatura, déficit de presión de vapor, precipitación) con observaciones satelitales periódicas (NDVI) y condiciones de suelo estáticas (pH, carbono orgánico, texturas) para crear perfiles analíticos rigurosos en la sierra ecuatoriana, particularmente lidiando con la alta nubosidad y escasez de datos limpios.

## Objetivo
Implementar un *Pipeline* de datos integrado gobernado por un Sistema Multi-Agente capaz de limpiar, cruzar, validar y emitir observaciones heurísticas de rigor estadístico sobre factores climáticos, edáficos y satelitales sin emitir causalidades infundadas ni prescripciones químicas, priorizando la reproducibilidad y el tratamiento anti-*data-leakage*.

## Fuentes de Datos Utilizadas
* **NASA POWER**: Mediciones continuas históricas climáticas estimadas (~0.5° resolución) (ex: `T2M`, `PRECTOTCORR`, `ALLSKY_SFC_SW_DWN`, `VPD`).
* **Sentinel-2 / Google Earth Engine**: Observaciones satelitales multiespectrales esporádicas. Índices extraídos: `NDVI`, `NDWI`.
* **SoilGrids / ISRIC**: Base de datos edafológica global. Extrae parámetros estáticos como `pH`, `SOC` y `Texturas` a profundidad del sistema radicular.
* **SIPA/ESPAC**: Contexto agronómico general publico ecuatoriano (anclaje teórico).

## Arquitectura Multi-Agente
AgroField AI usa una partición estricta entre la recolección de los datos y el raciocinio/evaluación. Los componentes de extracción están desplegados en `src/data/`, mientras que todo raciocinio heurístico ocurre exclusivamente en `agents/`. Las interacciones ocurren de forma modular entre diccionarios JSON aislados.

### Descripción de los Agentes Implementados (Completados):
1. **Climate Agent**: Recibe series temporales climáticas de NASA POWER. Emite evaluaciones sobre el déficit hídrico, estrés térmico, y vigor esperado (confianza media).
2. **Soil Agent**: Analiza propiedades físicas y químicas (ej: de SoilGrids). Transforma valores en clasificaciones agronómicas contextuales (confianza media).
3. **Data Agent**: Motor relacional. Efectúa un *Left Join* temporal usando el paso de Sentinel-2 como índice pivot, inyectando variables continuas (clima) y fijas (suelo) en un solo DataSet Unificado de observaciones coincidentes.
4. **Statistics Agent**: Procesa estadísticas rigurosas correlacionales paramétricas (Pearson $r$) en el dataset, indicando magnitudes limitables explícitamente sin afirmar dependencia biológica determinista (confianza alta).
5. **ML Agent**: Entrena y valida un modelo Baseline Supervisado (Regresión Lineal Simple) prediciendo $NDVI$ basado en clima, utilizando split 80/20 puramente cronológico y evitando contaminación (leakage).
6. **Agronomy Agent**: Orquestador interpretativo o evaluador final. Reúne las conclusiones independientes de TODOS los demás agentes y dictamina observaciones integradas, indicadores de riesgo agronómico y acciones de monitoreo sin extralimitar la evidencia provista.

## Estructura Real del Repositorio
```text
agrofield-ai/
├── agents/             # Lógica interpretativa (Climate, Soil, Data, Statistics, ML, Agronomy)
├── data/
│   ├── processed/      # Archivos CSV consolidados (Ej. NASA POWER diarios procesados)
│   └── raw/            # Descargas en crudo JSON/metadatos
├── docs/               # Documentación y trazabilidad de los 28 Días de desarrollo
├── notebooks/          # Exploración interactiva y construcción inicial de Dataframes
├── src/
│   ├── data/           # Clientes API extractores (ee_extractor.py, soilgrids_client.py)
│   ├── features/       # Operaciones de algebra de índices (NDVI/NDWI)
│   ├── models/         # (Reservado para exportaciones serielizadas futuras de esquemas)
│   └── utils/
├── tests/              # Pruebas automatizadas (Agents, Integration, Matrices, Math)
├── config.py           # Variables globales de zona (Colta, Chimborazo)
├── requirements.txt    # Dependencias estrictas necesarias para reproducir
└── run_agronomy_e2e.py # Prueba del Agronomy Agent que orquesta un reporte completo E2E
```

## Reproducibilidad y Ejecución

Las etapas se encuentran listas para su configuración bajo un flujo de python estándar. Para ejecutar la demostración final, proceda en un entorno limpio de Python 3.9+:

1. **Clonar el Repositorio e Inicializar entorno:**
```bash
git clone https://github.com/usuario/agrofield-ai.git
cd agrofield-ai
python -m venv .venv

# En Windows:
.venv\Scripts\activate
# En Linux/Mac:
source .venv/bin/activate
```

2. **Instalar Dependencias:**
```bash
pip install -r requirements.txt
```

3. **Autenticación (Solo si pretende extender/re-ejecutar las descargas de Earth Engine localmente)**:
El módulo de `ee_extractor.py` necesita acceso de Google Earth Engine. Utilice la línea de comandos autenticada de `earthengine-api` instalada en su entorno:
```bash
earthengine authenticate
earthengine set_project <SU_ID_DE_PROYECTO_GCP>
```

4. **Ejecución de Pruebas Unitarias/Integración (Opcional pero Recomendado)**:
Verifican el rigor estadístico de Pearson, los límites umbrales del Climate Agent y la robustez del Split del ML Agent.
```bash
python -m pytest tests/
```

5. **Prueba End-to-End Integrada**:
```bash
python run_agronomy_e2e.py
```
Esta validación emite una interfaz de terminal profesional e interactiva soportada por `rich`, presentando paneles independientes por cada bloque del sistema multi-agente, previniendo el truncamiento de descripciones extensas y facilitando el escrutinio estadístico de manera humana.

### ¿Qué demuestra el run_agronomy_e2e.py?
El script simula la ejecución de orquestación de **todos los agentes** usando flujos de datos reales pero mockeados o pre-calculados, como arrays de NDVI representacionales y DataFrames históricos de NASA POWER purificados, logrando emitir el *Reporte Integral Agronómico final*. Demuestra la coherencia estructural y sintáctica de procesamiento integral sin lanzar descargas asíncronas costosas (GCP) en tiempo de ejecución de prueba. El pipeline completamente automático y sin fallas desde 0 en ambiente Cloud *sigue en calidad de prototipo.*

## Resultados del Baseline de Machine Learning
El ML Agent aborda la regresión continua para predecir **NDVI espectral**. Debido al estricto apego para mitigar *Data Leakage*, excluyendo atributos de reflejo futuro y asumiendo un tamaño de muestra reducido de *N = 53 observaciones válidas sin nubes*, el Baseline Linear Classifier arrojó:

* **MAE (Error Absoluto Medio):** ≈ 0.076
* **RMSE:** ≈ 0.084
* **$R^2$:** ≈ -0.852

**Interpretación Metodológica:**
Este $R^2$ negativo declara honestamente y de manera transparente que un modelo lineal estricto sin retrasos temporales *Lags* (predecir vigor utilizando clima estrictamente de hoy) predice la reacción fisiológica de forma inferior a lo que lo haría adivinando meramente una media global. Todo esto declara que **La biología vegetal manifiesta demoras sistémicas no predecibles instantáneamente de forma lineal**. No afirmamos ninguna causalidad inventada o falsificada. 

## Limitaciones

1. **Datos de Muestra**: Observaciones limitadas a interceptaciones válidas del Sentinel-2, enormemente disminuidas por el alto índice de nubosidad continuo interandino. Las métricas del modelo (N=53) deben leerse con cuidado y considerarse prototipos.
2. **Estimaciones Generales**: El clima derivado de reanálisis satelital (NASA POWER) estima celdas de un 0.5°, por ende, no capta con fidelidad altísima el comportamiento microclimático a nivel de lote.
3. **Ausencia de Fenología Botánica Empírica**: Los agentes heurísticos asumen un cultivo general constante, omitiendo si la papa en un periodo de baja humedad/VPD se encuentra en desarrollo vegetativo o germinación.
4. **Heurísticas No Prescriptivas**: Los agentes emiten lecturas agronómicas basadas en literatura teórica y *nunca recomiendan ni diagnostican oficialmente*. 

## Trabajo Futuro
* **Windowing Agents**: Expansión a predicciones *Lagged Features*, arrastrando ventanas de temperaturas pasadas (ej. 15-30 días de suma térmica) para justificar fenológicamente el resultado fototrópico de NDVI visualizado.
* **Integración del Orquestador Dinámico**: Abstraer y poner todas las descargas API online, transformando el `run_agronomy_e2e.py` en una ejecución dinámica para nuevos cantones bajo demanda.
