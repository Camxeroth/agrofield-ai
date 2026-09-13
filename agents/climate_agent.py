from typing import Dict, Any, List
import pandas as pd

def interpret_temperature(t_mean: float, t_min: float, t_max: float) -> str:
    """Interpreta la temperatura para el ciclo del cultivo de papa."""
    if t_mean < 8:
        return f"Muy fría ({t_mean:.1f}°C). Riesgo de heladas crónicas y retraso severo en el desarrollo."
    elif 8 <= t_mean <= 15:
        return f"Temperatura óptima ({t_mean:.1f}°C) para tuberización y desarrollo. Buen vigor esperado."
    elif 15 < t_mean <= 20:
        return f"Temperaturas moderadamente altas ({t_mean:.1f}°C). Desarrollo adelantado, posible reducción de tamaño de tubérculo."
    else:
        return f"Temperaturas excesivas ({t_mean:.1f}°C). Estrés por calor, afecta formación de tubérculos."

def interpret_precipitation(precip_total: float, days_evaluated: int) -> str:
    """Interpreta la precipitación total en el periódo."""
    daily_avg = precip_total / days_evaluated if days_evaluated > 0 else 0
    if daily_avg < 1.0:
        return f"Déficit hídrico severo ({daily_avg:.1f} mm/día). Se requiere riego suplementario intenso."
    elif 1.0 <= daily_avg <= 2.5:
        return f"Humedad moderada ({daily_avg:.1f} mm/día). Puede requerir soporte de riego en fase de floración (papa)."
    elif 2.5 < daily_avg <= 5.0:
        return f"Humedad adecuada ({daily_avg:.1f} mm/día). Muy favorable para el cultivo en secano."
    else:
        return f"Exceso de lluvias ({daily_avg:.1f} mm/día). Riesgo de encharcamiento y proliferación de Tizón tardío."

def interpret_vpd(vpd_mean: float) -> str:
    """Interpreta el Déficit de Presión de Vapor (VPD)."""
    if pd.isna(vpd_mean):
        return "VPD promedio resulta en valor nulo."
    if vpd_mean < 0.5:
        return f"VPD muy bajo ({vpd_mean:.2f} kPa). Transpiración limitada, alta humedad propicia para enfermedades."
    elif 0.5 <= vpd_mean <= 1.2:
        return f"VPD en rango óptimo ({vpd_mean:.2f} kPa). Flujo correcto de nutrientes, estomas saludables."
    else:
        return f"VPD alto ({vpd_mean:.2f} kPa). Estrés hídrico cerrado estomático y déficit fotoasimilados."

def run(climate_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Recibe los datos históricos climáticos y genera un resumen interpretativo para el cultivo.
    
    Args:
        climate_df (pd.DataFrame): DataFrame que debe contener columnas como T2M, PRECTOTCORR, y VPD (opcional RH2M)
        
    Returns:
        Dict: Interpretación general del clima y notas agronómicas sobre disponibilidad.
    """
    if climate_df is None or climate_df.empty:
        return {"error": "El dataset climático está vacío o es nulo."}
        
    required_cols = ['T2M', 'PRECTOTCORR', 'fecha']
    missing = [c for c in required_cols if c not in climate_df.columns]
    
    if missing:
        return {"error": f"Faltan variables climáticas clave en el dataset: {missing}"}
        
    # Cálculos estadísticos básicos omitiendo NaNs
    days = len(climate_df)
    t_mean = float(climate_df['T2M'].mean())
    t_min = float(climate_df['T2M'].min())
    t_max = float(climate_df['T2M'].max())
    precip_total = float(climate_df['PRECTOTCORR'].sum())
    
    agronomic_notes: List[str] = []
    
    # Evaluar la temperatura
    t_interp = interpret_temperature(t_mean, t_min, t_max)
    agronomic_notes.append(f"Rango de temperatura: de {t_min:.1f}°C a {t_max:.1f}°C")
    
    # Evaluar precipitación
    p_interp = interpret_precipitation(precip_total, days)
    agronomic_notes.append(f"Precipitación acumulada: {precip_total:.1f} mm en {days} días")
    
    # Evaluar VPD si existe
    vpd_interp = "Dato de VPD no disponible en este dataset."
    if 'VPD' in climate_df.columns:
        vpd_mean = float(climate_df['VPD'].mean())
        if not pd.isna(vpd_mean):
            vpd_max = float(climate_df['VPD'].max())
            vpd_interp = interpret_vpd(vpd_mean)
            agronomic_notes.append(f"VPD promedio: {vpd_mean:.2f} kPa, máximo: {vpd_max:.2f} kPa")
        
    # Si hay Humedad Relativa
    if 'RH2M' in climate_df.columns:
        rh_mean = float(climate_df['RH2M'].mean())
        if not pd.isna(rh_mean):
            agronomic_notes.append(f"Humedad Relativa promedio: {rh_mean:.1f}%")
        
    # Convert dates to string handling pd.Timestamp explicitly if needed, but min() max() on series gives Timestamp
    min_date = climate_df['fecha'].min()
    max_date = climate_df['fecha'].max()
    date_str_min = str(min_date)[:10] if isinstance(min_date, pd.Timestamp) else str(min_date)
    date_str_max = str(max_date)[:10] if isinstance(max_date, pd.Timestamp) else str(max_date)
    
    summary = f"Análisis climático completado para {days} días (desde {date_str_min} hasta {date_str_max})."
    
    return {
        "summary": summary,
        "temperature_interpretation": t_interp,
        "precipitation_interpretation": p_interp,
        "vpd_interpretation": vpd_interp,
        "agronomic_notes": agronomic_notes
    }
