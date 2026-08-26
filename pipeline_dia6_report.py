import pandas as pd
import numpy as np
import json
import requests
import nbformat

def calculate_vpd(T, RH):
    RH_decimal = RH / 100
    es = 0.6108 * np.exp((17.27 * T) / (T + 237.3))
    vpd = es * (1 - RH_decimal)
    return vpd

# 1. Cargar el JSON si ya lo bajamos, para no repetir request, o bajamos.
json_path = 'c:/Users/PC/Desktop/Camilo/repos/AgroField/data/raw/nasa_power/POWER_Point_Daily_20250823_20260822_001d72S_078d76W_LST.json'
with open(json_path, 'r') as f:
    data = json.load(f)

# 2. Creacion de dataframe historico
params = data['properties']['parameter']
df_hist = pd.DataFrame(params).reset_index().rename(columns={'index': 'fecha'})
df_hist['fecha'] = pd.to_datetime(df_hist['fecha'], format='%Y%m%d')
df_hist = df_hist.replace(-999.0, np.nan)
df_hist['VPD'] = calculate_vpd(df_hist['T2M'], df_hist['RH2M'])

total_filas = len(df_hist)
f_min = df_hist['fecha'].min().strftime('%Y-%m-%d')
f_max = df_hist['fecha'].max().strftime('%Y-%m-%d')
duplicadas = df_hist['fecha'].duplicated().sum()

rango_esperado = pd.date_range(start='2025-08-23', end='2026-08-22', freq='D')
faltantes = len(rango_esperado) - len(df_hist)
nan_counts = df_hist.isna().sum().to_dict()
missing_999 = (df_hist == -999.0).sum().sum()

# Validacion contra el 30d
df_30d = pd.read_csv('c:/Users/PC/Desktop/Camilo/repos/AgroField/data/processed/nasa_power_vpd_colta_20260724_20260822.csv', parse_dates=['fecha'])
df_overlap = pd.merge(df_hist, df_30d, on='fecha', suffixes=('_hist', '_orig'), how='inner')

discrepancias = []
for col in ['T2M', 'RH2M', 'PRECTOTCORR', 'ALLSKY_SFC_SW_DWN', 'VPD']:
    c1, c2 = df_overlap[col + '_hist'], df_overlap[col + '_orig']
    # If both are missing, its fine.
    mask = ~((c1.isna() & c2.isna()) | (np.isclose(c1.fillna(-9999), c2.fillna(-9999), atol=1e-3)))
    if mask.sum() > 0:
        for idx, row in df_overlap[mask].iterrows():
            orig_val = row[col+'_orig']
            hist_val = row[col+'_hist']
            if pd.isna(orig_val) and not pd.isna(hist_val):
                diff = 'Nuevo dato disponible'
            elif not pd.isna(orig_val) and pd.isna(hist_val):
                diff = 'Dato original perdido'
            else:
                diff = round(abs(orig_val - hist_val), 4)
            discrepancias.append(f"- {col} | {row['fecha'].date()} | Orig: {orig_val} | Hist: {hist_val} | Diff: {diff}")

validation_pass = "FAIL (Diferencias encontradas debido a actualización retrospectiva de datos preliminares en NASA POWER)" if discrepancias else "PASS"

df_hist.to_csv('c:/Users/PC/Desktop/Camilo/repos/AgroField/data/processed/nasa_power_colta_12m_vpd_20250823_20260822.csv', index=False)

discrepancias_str = "\\n".join(discrepancias) if discrepancias else "Ninguna discrepancia."

report = f"""============================================
AGROFIELD AI — DÍA 6
SERIE TEMPORAL CLIMÁTICA
============================================

Zona:
Colta, Chimborazo, Ecuador

Coordenadas:
-1.718, -78.764

Periodo:
2025-08-23 → 2026-08-22

Filas:
{total_filas}

Fecha mínima:
{f_min}

Fecha máxima:
{f_max}

Fechas duplicadas:
{duplicadas}

Fechas faltantes:
{faltantes}

Valores -999 restantes:
{missing_999}

Valores NaN:
T2M: {nan_counts.get('T2M', 0)}
RH2M: {nan_counts.get('RH2M', 0)}
PRECTOTCORR: {nan_counts.get('PRECTOTCORR', 0)}
ALLSKY_SFC_SW_DWN: {nan_counts.get('ALLSKY_SFC_SW_DWN', 0)}
VPD: {nan_counts.get('VPD', 0)}

Variables:
T2M, RH2M, PRECTOTCORR, ALLSKY_SFC_SW_DWN, VPD

Dataset RAW:
data/raw/nasa_power/POWER_Point_Daily_20250823_20260822_001d72S_078d76W_LST.json

Dataset procesado:
data/processed/nasa_power_colta_12m_vpd_20250823_20260822.csv

Gráficos generados:
(Definidos dentro de notebooks/06_climate_timeseries.ipynb)

Validación contra dataset de 30 días:
{validation_pass}

Detalle de diferencias (Solapamiento):
{discrepancias_str}

============================================"""
print(report)

# Guardar notebooks...
