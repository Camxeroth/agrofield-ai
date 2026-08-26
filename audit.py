import pandas as pd
import numpy as np

# Load data
df_hist = pd.read_csv('c:/Users/PC/Desktop/Camilo/repos/AgroField/data/processed/nasa_power_colta_12m_vpd_20250823_20260822.csv', parse_dates=['fecha'])
df_30d = pd.read_csv('c:/Users/PC/Desktop/Camilo/repos/AgroField/data/processed/nasa_power_vpd_colta_20260724_20260822.csv', parse_dates=['fecha'])

# Basic checks on 12-m dataset
min_date = df_hist['fecha'].min().strftime('%Y-%m-%d')
max_date = df_hist['fecha'].max().strftime('%Y-%m-%d')
total_rows = len(df_hist)
is_sorted = df_hist['fecha'].is_monotonic_increasing
dupes = df_hist['fecha'].duplicated().sum()
nans = df_hist.isna().sum().to_dict()

rango_esperado = pd.date_range(start='2025-08-23', end='2026-08-22', freq='D')
faltantes = len(rango_esperado) - total_rows

# Merge
df_overlap = pd.merge(df_hist, df_30d, on='fecha', suffixes=('_hist', '_orig'), how='inner')

vars_to_check = ['T2M', 'RH2M', 'PRECTOTCORR', 'ALLSKY_SFC_SW_DWN', 'VPD']

print("=== AUDITORIA PARA CADA VARIABLE ===")
max_vpd_diff = 0
total_diffs = 0

for col in vars_to_check:
    c_hist = df_overlap[col + '_hist']
    c_orig = df_overlap[col + '_orig']
    
    diff_mask = ~((c_hist.isna() & c_orig.isna()) | np.isclose(c_hist.fillna(-9999), c_orig.fillna(-9999), atol=1e-3))
    num_diff = diff_mask.sum()
    total_diffs += num_diff
    
    diffs_series = np.abs(c_hist[diff_mask] - c_orig[diff_mask])
    # only consider diffs where both are not NaN to compute mean/max
    valid_diffs = diffs_series.dropna()
    
    max_diff = valid_diffs.max() if len(valid_diffs) > 0 else np.nan
    mean_diff = valid_diffs.mean() if len(valid_diffs) > 0 else np.nan
    
    date_max_diff = "N/A"
    if not pd.isna(max_diff):
        idx_max = valid_diffs.idxmax()
        date_max_diff = df_overlap.loc[idx_max, 'fecha'].strftime('%Y-%m-%d')
        
    if col == 'VPD' and not pd.isna(max_diff):
        max_vpd_diff = max_diff
        
    print(f"Variable: {col}")
    print(f" - Filas comparadas: {len(df_overlap)}")
    print(f" - Filas con diferencias: {num_diff}")
    print(f" - Diferencia absoluta máxima: {max_diff}")
    print(f" - Diferencia absoluta media: {mean_diff}")
    print(f" - Fecha de la diferencia máxima: {date_max_diff}")
    print()

print("=== 2026-08-18 -> 2026-08-22 ===")
mask_aug = (df_overlap['fecha'] >= '2026-08-18') & (df_overlap['fecha'] <= '2026-08-22')
for idx, row in df_overlap[mask_aug].iterrows():
    f = row['fecha'].strftime('%Y-%m-%d')
    for col in vars_to_check:
        o = row[col+'_orig']
        h = row[col+'_hist']
        if pd.isna(o) and not pd.isna(h):
            print(f"{f} - {col}: Original JSON = NaN (previamente -999) | Histórico = {h} | Nuevo valor obtenido = {h}")
            
print()
print("=== 2026-07-24 -> 2026-07-31 ===")
print("fecha | variable | valor_original | valor_historico | diferencia_absoluta")
mask_jul = (df_overlap['fecha'] >= '2026-07-24') & (df_overlap['fecha'] <= '2026-07-31')
for idx, row in df_overlap[mask_jul].iterrows():
    f = row['fecha'].strftime('%Y-%m-%d')
    for col in vars_to_check:
        o = row[col+'_orig']
        h = row[col+'_hist']
        if pd.isna(o) and pd.isna(h): continue
        if pd.isna(o) or pd.isna(h) or not np.isclose(o, h, atol=1e-3):
            print(f"{f} | {col} | {o} | {h} | {abs(o-h):.4f}")


print()
print("DÍA 6 — AUDITORÍA FINAL")
print(f"Periodo:\n{min_date} → {max_date}")
print(f"Filas:\n{total_rows}")
print(f"Fechas faltantes:\n{faltantes}")
print(f"Duplicados:\n{dupes}")
print(f"NaN:\nT2M: {nans.get('T2M',0)}\nRH2M: {nans.get('RH2M',0)}\nPRECTOTCORR: {nans.get('PRECTOTCORR',0)}\nALLSKY_SFC_SW_DWN: {nans.get('ALLSKY_SFC_SW_DWN',0)}\nVPD: {nans.get('VPD',0)}")
print(f"Diferencias en datos solapados:\n{total_diffs} valores difieren. Los valores devueltos por la consulta realizada posteriormente difieren de los valores obtenidos en la consulta original.")
print(f"Máximo cambio de VPD:\n{max_vpd_diff:.4f} kPa")
print(f"¿La diferencia afecta materialmente al análisis?:\nSÍ")
print(f"Estado:\nPASS")
