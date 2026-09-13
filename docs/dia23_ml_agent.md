# AgroField AI — Día 23: Baseline ML Agent

## Objetivo
Implementar el primer Agente de Machine Learning (Supervisado) mediante un baseline riguroso, priorizando la reproducibilidad, control metodológico y detección de filtración de datos (data leakage), antes que la búsqueda artificial de hiperparámetros. 

El ML Agent se concibe para consumirse a través del _pipeline_ integrado gestionado por el Data Agent.

## Problema Supervisado 
* **Target:** `ndvi` (Índice de Diferencia Normalizada de Vegetación).
* **Justificación:** NDVI es la aproximación derivada más legítima disponible y fundamentada de nuestra serie satelital, funcionando como _proxy_ para el vigor vegetativo real y biomasa superficial temporal sin la necesidad de forzar clases o targets falsos.
* **Features Analizadas:** `['T2M', 'RH2M', 'PRECTOTCORR', 'ALLSKY_SFC_SW_DWN', 'VPD']`.
* **Descarte Anti-Leakage y Constantes:** Se excluyeron del dataset predictor las derivadas del suelo (puesto que todas ostentan varianza nula al estar ancladas a una sola región local de la parcela). También se excluyeron `[B3, B4, B8, cloud_percentage]` ya que el paso multiespectral y las bandas Red/NIR contienen la información exacta (trampa del futuro) para calcular retrospectivamente el target `ndvi`.
* **Problema:** Regresión Continua Supervisada.

## Estrategia de División y Control (Train/Test Split)
* **Separación Manual Temporal:** 
En los marcos de tiempo, los eventos biológicos y estacionales siguen dependencias. Si barajáramos aleatoriamente con `train_test_split()`, datos calurosos del futuro podrían empujar al modelo, quebrando la validación progresiva. 
* El ML Agent realiza una separación cronológica al **80% (Entrenamiento)** / **20% (Evaluación-Test)**.
* Los escalamientos computacionales `StandardScaler` aplican *fit* exclusivo en los lotes de Entrenamiento mitigando el riesgo de contaminación estadística hacia la validación de prueba.

## Modelo Baseline Resultante
Se ha desplegado una `Regresión Lineal Simple`. Con 5 variables predictoras, la arquitectura lineal mitiga grandemente la memorización masiva (overfitting colosal) que presentaría por ejemplo un _RandomForest_ entrenado sobre la actual escasa varianza satelital libre de nubes local.

## Métricas
Tres métricas globales explícitas calculadas exclusivamente sobre el subconjunto independiente de Prueba (20% del futuro).
* **MAE (Mean Absolute Error):** Magnitud lineal absoluta del desvío sin castigar outliers de vigor.
* **RMSE (Root Mean Square Error):** Grado de dispersión donde los errores severos castigan mayoritariamente la predicción.
* **R² (R-Cuadrado):** Bondad de ajuste. El nivel de variabilidad vegetativa que logramos justificar con el clima del modelo.

## Resultados Obtenidos con Datas Real
Ejecutando el `test_day23_ml.py` bajo el pipeline del `Data Agent` (Sentinel + Clima de NASA Power):

* **Dataset total:** 53 observaciones coincidentes limpias (nubes < 90%).
* **Train / Test**: 42 Entrenamiento / 11 Pruebas
* **Target:** `ndvi`
* **Resultados arrojados en Predicción (20% invisible):**
  * **MAE**: `0.076`
  * **RMSE**: `0.084`
  * **R²**: `-0.852`

### Interpretación de los hallazgos
La obtención de un **$R^2$ negativo** confirma la estricta hipótesis de rigurosidad abordada en días pasados: Predecir la reacción fototrópica y vigor (*NDVI*) de una planta en función estricta del clima de ese *mismo único día*, arroja un modelo peor que adivinar una línea recta promedio global. 

Las plantas manifiestan respuestas fenotípicas semanas **después** de lluvias o estrés (Time Delays / Lags). No hay correlación lineal biológica predictible instantánea, lo cual demuestra que el sistema es matemáticamente sano y sincero al no arrojar métricas infladas.

## Limitaciones y Mejoras Futuras
* **Escasez de Datos (Muestra $n < 60$)**: Reducciones en la capacidad de observar la franja andina libre de nube fuerzan al ML Agent a extrapolar poco. No compensa actualmente forzar arquitecturas Profundas (Deep Learning) sin incorporar antes Time-Series CV multi-sitio.
* **Falta de Variables Retrasadas (Lagged Features)**: La primera gran mejora productiva futura consistiría en generar un `Windowing Agent` que suministre métricas de climas *semanas atrás* (ej., precipitaciones en L-15 días, VPD acumulado 3 semanas).
* **Resolución Espacial Desemparejada**: NDVI mide $\approx 10x10m$. NASA Clima estima para un lote inmenso de 0.5°. El ruido espacial penaliza severamente el modelo. No hay correlación local extrema todavía.
* **El ML Agent ES UN BASELINE, no diagnostica**. Sus responsabilidades no recomiendan intervenciones. Representa un punto de arranque técnico supervisado de AgroField AI.
