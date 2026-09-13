# AgroField AI — Día 22: Math Agent & Validation Agent

## Objetivo
Implementar una nueva capa de abstracción analítica encargada de explicar de forma verificable los cálculos delegados, validando numéricamente metodologías pasadas y presentes. Este día se focaliza exclusivamente en explicabilidad matemática (White-Box AI) y comprobación cruzada, previniendo alucinaciones analíticas o suposiciones mágicas.

## Arquitectura de Validación
El ecosistema asume la siguiente cadena de custodia metodológica:
> **MANUAL (Cálculo Teórico en Papel/Documentación) → PYTHON (Pandas/Stats) → MATH AGENT (Explicación paso a paso) → VALIDATION AGENT (Cotejado cruzado de tolerancias flotantes)**

Ninguna correlación es presentada sin una base demostrable de covarianzas.

### 1. Math Agent
**(Ruta: `agents/math_agent.py`)**
Su propósito imperativo es el _desglose_:
* Desglosar las Medias ($\bar{x}, \bar{y}$).
* Desglosar las Desviaciones respecto a la media y los productos sumados (covarianza sin escalar). $\sum(x_i-\bar{x})(y_i-\bar{y})$
* Desglosar la sumatoria de desviaciones cuadradas ($\sum(x_i-\bar{x})^2$).
* Producir un resultado computado `r` verificable.
* Contiene el marco de advertencia teórica: **"Pearson mide asociación lineal y no demuestra causalidad."** Prohíbe interpretaciones fenológicas fuera del espectro matemático (evalúa si r > 0.0 o r < 0.0, no si "el clima mejora el follaje").

### 2. Validation Agent
**(Ruta: `agents/validation_agent.py`)**
Un agente dedicado a auditar código y resultados:
* Recibe `manual_r`, `python_r`, `math_agent_r`.
* Aplica un análisis de tolerancia cruzada iterando `abs(origen_A - origen_B)`.
* Emite un dictamen: `VALIDADO`, `DISCREPANCIA` (para hallazgos teóricos diferentes originados en fórmulas erróneas, un GAP importante > 0.001) o _Errores por punto flotante leves_.

## Validación del Resultado Real (Day 20 Pipeline)
Utilizando la metodología estandarizada del sistema, el `Validation Agent` revisó en vivo una conexión a Earth Engine de 1 año frente al Clima de NASA (Extracción: NDVI $\leftrightarrow$ T2M).

* **Variables**: NDVI, T2M
* **Muestra (N)**: 53 Cruces
* **Cálculo Teórico Previo (Día 18/20)**: `0.178398` (Truncado histórico)
* **Cálculo Python Nativo (Statistics Agent)**: `0.1783980734794613`
* **Cálculo Desglosado (Math Agent Numpy)**: `0.1783980734794609` (Diferencia de $\approx 4 \times 10^{-16}$)
* **Dictamen del Validation Agent**: `VALIDADO` (Las discrepancias residuales caen cómodamente en las tolerancias numéricas para exactitud algorítmica humana, confirmando la reproducibilidad metodológica del proyecto).

## Pruebas de Integridad
**(Ruta: `tests/test_day22_math_validation.py`)**
Batería agresiva controlada con resultados explícitos deterministas.
1. `test_pearson_perfecto` (r=1.0)
2. `test_pearson_negativo` (r=-1.0)
3. `test_pearson_cercano_cero` (Sumatoria del producto de desviaciones = 0)
4. `test_variable_constante` (Trampa de Varianza=0 validada, previene divisiones numéricas rotas).
5. `test_datos_insuficientes` (Manejado N < 2).
6. `test_datos_con_nan` (Alineación y purga manual verificada previo al cálculo).

## Discrepancias y Limitaciones
* Se descubrió una discrepancia menor flotante infinitesimal ($4 \times 10^{-16}$) entre el optimizador BLAS utilizado internamente por Pandas `df.corr()` y las multiplicaciones agregadas de NumPy del `Math Agent`. Este umbral numérico natural ha sido manejado exitosamente indicando un `rel_tol=1e-7` biológicamente apto.
* Como limitación extendida: el `Math Agent` se focaliza sobre Pearson. No atiende test de normalidad (Shapiro-Wilk) requeridos teóricamente por la fórmula; esto se considera una limitante del estado actual.

---
_El motor transaccional del proyecto valida rigurosamente sus números. Ningún "Cálculo en Caja Negra" será reportado al Agricultor._
