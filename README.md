# AgroField AI
<img width="1920" height="1080" alt="miniaturas japonesas" src="https://github.com/user-attachments/assets/72b51ee2-b374-4c09-b7e8-c5397dd21a63" />

**Sistema Multi-Agente de Análisis Agrícola para Cultivos de Papa — Cantón Colta, Chimborazo, Ecuador**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://agrofield-ai.streamlit.app/)
![Status](https://img.shields.io/badge/status-prototype-yellow)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-not--specified-lightgrey)

**Demo en vivo:** [https://agrofield-ai.streamlit.app/](https://agrofield-ai.streamlit.app/)

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Problema que Aborda](#problema-que-aborda)
3. [Objetivo del Sistema](#objetivo-del-sistema)
4. [Arquitectura Multi-Agente](#arquitectura-multi-agente)
5. [Fuentes de Datos](#fuentes-de-datos)
6. [Estructura del Repositorio](#estructura-del-repositorio)
7. [Aplicación Web (Streamlit)](#aplicación-web-streamlit)
8. [Instalación y Ejecución Local](#instalación-y-ejecución-local)
9. [Despliegue en Streamlit Community Cloud](#despliegue-en-streamlit-community-cloud)
10. [Pruebas Automatizadas](#pruebas-automatizadas)
11. [Resultados del Baseline de Machine Learning](#resultados-del-baseline-de-machine-learning)
12. [Limitaciones Conocidas](#limitaciones-conocidas)
13. [Hoja de Ruta](#hoja-de-ruta)
14. [Principios de Diseño](#principios-de-diseño)
15. [Contribuciones](#contribuciones)

---

## Resumen Ejecutivo

AgroField AI es un sistema de análisis agrícola que integra datos satelitales, climáticos y edafológicos para generar observaciones agronómicas objetivas sobre cultivos de papa en la sierra ecuatoriana. El sistema está diseñado alrededor de una arquitectura multi-agente donde cada agente resuelve una responsabilidad acotada (clima, suelo, integración de datos, estadística, machine learning y síntesis agronómica), priorizando la reproducibilidad, la trazabilidad de las conclusiones y la ausencia de prescripciones no fundamentadas.

La plataforma está disponible como aplicación web mediante Streamlit, permitiendo que técnicos y agrónomos de campo obtengan un reporte agronómico traducido a lenguaje humano sin necesidad de interactuar con código o líneas de comando.

## Problema que Aborda

Existe una limitada capacidad operativa para cruzar datos climáticos (temperatura, déficit de presión de vapor, precipitación), observaciones satelitales periódicas (NDVI) y condiciones estáticas de suelo (pH, carbono orgánico, texturas) en perfiles analíticos rigurosos aplicados a la sierra ecuatoriana. Esta región presenta dos restricciones estructurales relevantes:

- Alta nubosidad persistente, que reduce la disponibilidad de observaciones satelitales limpias.
- Escasez de infraestructura de datos agronómicos locales consolidados y accesibles para personal técnico no especializado en ciencia de datos.

## Objetivo del Sistema

Implementar un pipeline de datos integrado, gobernado por un sistema multi-agente, capaz de:

- Limpiar, cruzar y validar variables climáticas, edáficas y satelitales.
- Emitir observaciones heurísticas con rigor estadístico sobre dichos factores.
- Evitar causalidades infundadas o prescripciones químicas no respaldadas por evidencia.
- Priorizar la reproducibilidad y el tratamiento explícito contra la fuga de datos (*data leakage*).

## Arquitectura Multi-Agente

El sistema aplica una separación estricta entre la recolección de datos y el razonamiento/evaluación. Los componentes de extracción residen en `src/data/`, mientras que todo el razonamiento heurístico ocurre exclusivamente en `agents/`. La comunicación entre componentes se realiza mediante diccionarios JSON aislados, sin acoplamiento directo entre módulos.

### Agentes Implementados

| Agente | Responsabilidad | Nivel de Confianza |
|---|---|---|
| **Climate Agent** | Procesa series temporales de NASA POWER y evalúa déficit hídrico, estrés térmico y vigor esperado. | Media |
| **Soil Agent** | Traduce propiedades físico-químicas del suelo (ej. SoilGrids) en clasificaciones agronómicas contextuales. | Media |
| **Data Agent** | Motor relacional. Ejecuta un *left join* temporal usando el paso de Sentinel-2 como índice pivote, unificando variables continuas (clima) y fijas (suelo) en un dataset consolidado. | — |
| **Statistics Agent** | Calcula correlaciones paramétricas (Pearson r), acotando explícitamente las magnitudes sin afirmar dependencia biológica determinista. | Alta |
| **ML Agent** | Entrena y valida un modelo baseline supervisado (regresión lineal) para predecir NDVI a partir de variables climáticas, usando una partición 80/20 estrictamente cronológica. | — |
| **Agronomy Agent** | Orquestador final. Integra las conclusiones de todos los agentes y emite el reporte agronómico consolidado, con indicadores de riesgo y acciones de monitoreo, sin extralimitar la evidencia disponible. | — |

## Fuentes de Datos

| Fuente | Tipo de Dato | Variables Extraídas |
|---|---|---|
| **NASA POWER** | Series climáticas históricas (resolución ~0.5°) | `T2M`, `PRECTOTCORR`, `ALLSKY_SFC_SW_DWN`, `VPD` |
| **Sentinel-2 / Google Earth Engine** | Observaciones satelitales multiespectrales esporádicas | `NDVI`, `NDWI` |
| **SoilGrids / ISRIC** | Base edafológica global estática | `pH`, `SOC` (carbono orgánico), texturas |
| **SIPA / ESPAC** | Contexto agronómico público ecuatoriano | Anclaje teórico y de referencia |

## Estructura del Repositorio

```
agrofield-ai/
├── agents/               # Lógica interpretativa (Climate, Soil, Data, Statistics, ML, Agronomy)
├── data/
│   ├── processed/        # Archivos CSV consolidados (ej. NASA POWER procesado)
│   └── raw/               # Descargas en crudo (JSON / metadatos)
├── docs/                 # Documentación y trazabilidad del desarrollo
├── notebooks/            # Exploración interactiva y construcción inicial de dataframes
├── src/
│   ├── data/              # Clientes de extracción (ee_extractor.py, soilgrids_client.py)
│   ├── features/          # Álgebra de índices espectrales (NDVI / NDWI)
│   ├── models/            # Reservado para exportaciones serializadas futuras
│   └── utils/
├── tests/                # Pruebas automatizadas (agentes, integración, matrices, estadística)
├── app.py                # Aplicación web (Streamlit)
├── config.py             # Variables globales de zona (Colta, Chimborazo)
├── requirements.txt      # Dependencias necesarias para reproducir el entorno
└── run_agronomy_e2e.py   # Prueba end-to-end del Agronomy Agent
```

## Aplicación Web (Streamlit)

La interfaz productiva del sistema está disponible en:

**[https://agrofield-ai.streamlit.app/](https://agrofield-ai.streamlit.app/)**

Esta interfaz permite que personal técnico y agrónomos ejecuten los agentes del sistema sin ver código fuente ni usar la terminal.

Flujo de uso:

1. Ingresar el nombre referencial de la parcela y sus coordenadas geográficas (latitud, longitud).
2. Seleccionar el tipo de cultivo a evaluar.
3. Ejecutar el análisis mediante el botón **Analizar Parcela**.
4. Revisar el reporte generado, organizado en pestañas de Clima, Suelo y Vegetación.
5. Descargar el reporte final en formato PDF si se requiere.

Toda la complejidad de extracción de datos y modelado queda oculta detrás de la interfaz.

## Instalación y Ejecución Local

Requiere Python 3.9 o superior.

```bash
git clone https://github.com/Camxeroth/agrofield-ai.git
cd agrofield-ai
python -m venv .venv
```

Activar el entorno virtual:

```bash
# Windows
.venv\Scripts\activate

# Linux / Mac
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar la aplicación web localmente:

```bash
streamlit run app.py
```

### Autenticación de Google Earth Engine (opcional)

Necesaria únicamente si se requiere re-ejecutar o extender las descargas satelitales localmente:

```bash
earthengine authenticate
earthengine set_project <ID_DE_PROYECTO_GCP>
```

### Ejecución End-to-End por Consola

```bash
python run_agronomy_e2e.py
```

Este script orquesta todos los agentes usando flujos de datos reales pero pre-calculados (arrays de NDVI representativos y series históricas de NASA POWER ya purificadas), generando el reporte agronómico integral sin disparar descargas asíncronas costosas contra servicios en la nube durante la prueba. Presenta paneles independientes por cada bloque del sistema mediante `rich`, evitando el truncamiento de descripciones extensas.

## Despliegue en Streamlit Community Cloud

Para publicar una instancia propia del sistema:

1. Subir el repositorio a GitHub.
2. Acceder a [Streamlit Community Cloud](https://share.streamlit.io/) e iniciar sesión con GitHub.
3. Crear una nueva app ("New app").
4. Seleccionar el repositorio, la rama (`main`) y definir `app.py` como archivo principal.
5. Desplegar. Streamlit instalará las dependencias declaradas en `requirements.txt` y generará un enlace público en pocos minutos.

## Pruebas Automatizadas

```bash
python -m pytest tests/
```

Las pruebas verifican, entre otros aspectos:

- El rigor estadístico del cálculo de correlación de Pearson.
- Los límites y umbrales definidos en el Climate Agent.
- La robustez de la partición cronológica utilizada por el ML Agent.

## Resultados del Baseline de Machine Learning

El ML Agent aborda una regresión continua para predecir el índice NDVI espectral. Bajo un estricto control contra fuga de datos (excluyendo atributos de reflejo futuro) y con una muestra reducida de N = 53 observaciones válidas sin cobertura de nubes, el modelo lineal baseline obtuvo:

| Métrica | Valor |
|---|---|
| MAE (Error Absoluto Medio) | ≈ 0.076 |
| RMSE | ≈ 0.084 |
| R² | ≈ -0.852 |

**Interpretación metodológica:** un R² negativo indica, de forma transparente, que un modelo lineal estricto sin variables rezagadas (*lags*) predice la respuesta fisiológica del cultivo peor de lo que lo haría estimar simplemente la media global. Esto sugiere que la biología vegetal presenta demoras sistémicas que no son capturadas por una relación lineal instantánea. El sistema no afirma ninguna causalidad no respaldada por los datos.

## Limitaciones Conocidas

1. **Tamaño de muestra:** las observaciones están limitadas a intercepciones válidas de Sentinel-2, reducidas de forma significativa por la alta nubosidad interandina persistente. Las métricas del modelo (N=53) deben interpretarse como resultado de un prototipo.
2. **Resolución climática:** los datos de NASA POWER estiman celdas de aproximadamente 0.5° de resolución, por lo que no capturan con precisión el comportamiento microclimático a nivel de lote individual.
3. **Ausencia de fenología botánica empírica:** los agentes heurísticos asumen un estado de cultivo general constante, sin diferenciar si el cultivo se encuentra en desarrollo vegetativo, floración o germinación durante periodos de baja humedad o VPD.
4. **Heurísticas no prescriptivas:** los agentes emiten lecturas agronómicas fundamentadas en literatura teórica y en ningún caso constituyen un diagnóstico o recomendación oficial de manejo agrícola.

## Hoja de Ruta

- **Agentes con ventanas temporales (windowing):** incorporar variables rezagadas (por ejemplo, sumas térmicas de 15 a 30 días) para justificar fenológicamente la respuesta fototrópica observada en el NDVI.
- **Orquestador dinámico:** llevar todas las descargas de API a modo en línea, transformando `run_agronomy_e2e.py` en un flujo de ejecución bajo demanda para nuevos cantones o zonas geográficas.

## Principios de Diseño

- Separación estricta entre recolección de datos y razonamiento interpretativo.
- Comunicación entre agentes mediante estructuras de datos aisladas (JSON), sin acoplamiento directo de código.
- Control explícito de fuga de datos en cualquier evaluación predictiva.
- Transparencia metodológica: los resultados, incluidos los negativos, se reportan sin distorsión.
- Ninguna salida del sistema constituye una recomendación agronómica oficial ni una prescripción de insumos.

## Contribuciones

Este proyecto se encuentra en fase de prototipo activo. Sugerencias, reportes de incidencias y propuestas de extensión pueden canalizarse mediante issues o pull requests en el repositorio.
