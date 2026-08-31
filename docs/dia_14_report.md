# Día 14 - Cierre de Semana: Gráfico Temporal

## Construcción del Gráfico
Basándonos estrictamente en los datos del extractor automatizado real de Earth Engine (Sentinel-2, `CLOUDY_PIXEL_PERCENTAGE < 20`, Punto 0), hemos generado la proyección temporal del `NDVI(t)`. 
* **Ubicación del Gráfico**: `docs/ndvi_temporal.png`.

## Análisis Estadístico Observado
* **Total de observaciones válidas procesadas**: 1 
* **Fecha de observación**: 2026-07-29
* **Valor NDVI observado**: 0.1918 (0.191791)
* **Comportamiento**: Un gráfico de un solo punto en el tiempo correspondiente al final de Julio de 2026.

## Interpretación Agronómica y Conclusiones Precisas
El NDVI de 0.191791 indica una señal de vegetación relativamente baja en el píxel/área analizada, pero este valor por sí solo no permite identificar si corresponde a suelo desnudo, vegetación escasa, cultivo u otra cobertura. Se requiere información espacial y temporal adicional para realizar una interpretación agronómica confiable.

### Lo que los datos PERMITEN afirmar:
* Durante el 29 de Julio, el nivel de verdor y vigor fotosintético en la parcela era bajo de forma objetiva (`~0.19`).

### Lo que los datos NO PERMITEN afirmar (Limitaciones Cruciales):
* Por tratarse empíricamente de **una única observación temporal aislada**, no es posible derivar ningún tipo de métrica dinámica agrícola. 
* No podemos afirmar si la vegetación está creciendo, si ya fue cosechada, o si hay un estrés hídrico súbito interrumpiendo el desarrollo. Carecemos de un gradiente de evolución o análisis fenológico.
* Las curvas temporales interpoladas con 1 solo punto carecen de validez estadística, no se puede plantear una regresión vegetal en estas condiciones.

## Siguiente Mejora Recomendada
Como descubrimos en la auditoría del Día 12.5, la extrema nubología paramera de la zona andina ecuatoriana destruye el muestreo usando el umbral general del 20%. Para las siguientes etapas de modelado y recolección se debe obligatoriamente:
1. Implementar la extracción satelital basada en **composiciones de máscara por píxel** (`Cloud Score+` o `QA60/SCL`). 
2. Fusionar observaciones con el radar **Sentinel-1**, para romper la barrera de nubes del muestreo.
