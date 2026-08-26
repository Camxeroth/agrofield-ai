import pandas as pd, numpy as np

df_hist = pd.read_csv('c:/Users/PC/Desktop/Camilo/repos/AgroField/data/processed/nasa_power_colta_12m_vpd_20250823_20260822.csv', parse_dates=['fecha'])
df_30d = pd.read_csv('c:/Users/PC/Desktop/Camilo/repos/AgroField/data/processed/nasa_power_vpd_colta_20260724_20260822.csv', parse_dates=['fecha'])
df_overlap = pd.merge(df_hist, df_30d, on='fecha', suffixes=('_hist', '_orig'), how='inner')

for col in ['T2M', 'RH2M', 'PRECTOTCORR', 'ALLSKY_SFC_SW_DWN']:
    c1, c2 = df_overlap[col + '_hist'], df_overlap[col + '_orig']
    mask = ~((c1.isna() & c2.isna()) | (np.isclose(c1.fillna(-9999), c2.fillna(-9999))))
    if mask.sum() > 0:
        for idx, row in df_overlap[mask].iterrows():
            print(f"Variable: {col} | Fecha: {row['fecha'].date()} | Original: {row[col+'_orig']} | Histórico: {row[col+'_hist']} | Diff: {abs(row[col+'_orig'] - row[col+'_hist'])}")

