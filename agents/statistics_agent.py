import pandas as pd
import numpy as np
from typing import Dict, Any

def run(integrated_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Realiza estadística descriptiva y cálculos de correlación en un dataset integrado.
    
    Responsabilidades:
    - Identificar variables numéricas válidas.
    - Calcular estadísticas descriptivas básicas (media, std, min, max).
    - Calcular matriz de correlación de Pearson (r).
    
    Limitación declarada: Correlación no implica causalidad. Los valores r
    calculados solo representan asociación lineal entre variables.
    
    Args:
        integrated_df: DataFrame creado típicamente por el Data Agent.
        
    Returns:
        Diccionario con estadísticas, correlaciones y advertencias.
    """
    output = {
        "summary": "Análisis estadístico completado.",
        "descriptive_statistics": {},
        "correlations": {},
        "data_quality": {},
        "warnings": [
            "LIMITACIÓN ESTADÍSTICA: Correlación no implica causalidad. "
            "Una alta correlación de Pearson ('r') describe una asociación lineal, "
            "pero no demuestra que una variable de origen determine biológicamente "
            "el comportamiento de la otra."
        ]
    }
    
    if integrated_df is None or integrated_df.empty:
        output["warnings"].append("Dataset proporcionado está vacío o es nulo. Análisis abortado.")
        output["summary"] = "Análisis fallido (DataFrame vacío)."
        return output
        
    df = integrated_df.copy()
    
    # Identificar numéricas excluyendo identificadores si los hay o constantes absolutas de metadatos
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        output["warnings"].append("No se encontraron columnas numéricas analizables.")
        return output
        
    # Descriptivas
    try:
        desc = numeric_df.describe().to_dict()
        output["descriptive_statistics"] = desc
    except Exception as e:
        output["warnings"].append(f"Error calculando descriptivas: {e}")
        
    output["data_quality"]["total_rows"] = len(df)
    output["data_quality"]["numeric_columns_analyzed"] = list(numeric_df.columns)
    
    # Filtro de variables constantes (varianza 0). Ejemplo: las estáticas del suelo
    # No es un error, pero forzar un Pearson sobre una constante da NaN.
    # Registramos cuáles son constantes y luego las excluimos para Pearson
    nunique = numeric_df.nunique()
    constant_cols = nunique[nunique <= 1].index.tolist()
    
    if constant_cols:
        output["warnings"].append(f"Las siguientes variables son constantes y fueron excluidas del cálculo de correlación: {constant_cols}")
        pearson_df = numeric_df.drop(columns=constant_cols)
    else:
        pearson_df = numeric_df
        
    # Calcular Pearson
    if len(pearson_df.columns) > 1 and len(pearson_df.dropna()) > 1:
        try:
            corr_matrix = pearson_df.corr(method='pearson')
            # Limpiar matriz para el JSON (evitar multi index o object jsonification issue)
            output["correlations"] = corr_matrix.replace({np.nan: None}).to_dict()
        except Exception as e:
            output["warnings"].append(f"Fallo al calcular matriz de correlación: {e}")
    else:
        output["warnings"].append("No hay suficiente varianza, número de columnas o muestras (sin NaN) para calcular correlaciones.")
        
    return output
