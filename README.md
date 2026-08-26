# AgroField AI

## Objetivo
Desarrollar progresivamente un sistema de análisis agrícola utilizando datos climáticos, satelitales y de suelo.

## Zona de Estudio Actual
- **Cantón:** Colta
- **Provincia:** Chimborazo
- **País:** Ecuador
- **Cultivo de referencia:** Papa
- **Latitud:** -1.718
- **Longitud:** -78.764
- **Altitud:** ~3003 m s.n.m. (según consulta a NASA POWER)

## Fuentes de Datos Actuales
- NASA POWER Daily API (Variables: T2M, RH2M, PRECTOTCORR, ALLSKY_SFC_SW_DWN)

## Estructura del Proyecto
```text
agrofield-ai/
│
├── data/
│   ├── raw/
│   │   ├── nasa_power/
│   │   ├── satellite/
│   │   └── soil/
│   │
│   └── processed/
│
├── notebooks/
│
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   └── utils/
│
├── agents/
│
├── docs/
│
├── tests/
│
├── .gitignore
├── README.md
├── requirements.txt
└── config.py
```
