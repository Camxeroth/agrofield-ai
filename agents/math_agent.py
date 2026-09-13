import pandas as pd
import numpy as np
from typing import Dict, Any

def interpret_pearson(r: float) -> str:
    """Interpreta matemáticamente el coeficiente de Pearson."""
    if np.isnan(r):
        return "No se pudo calcular la correlación (r es NaN)."
        
    abs_r = abs(r)
    sign_str = "positiva" if r > 0 else "negativa"
    
    if abs_r < 0.2:
        strength = "muy débil o nula"
    elif 0.2 <= abs_r < 0.4:
        strength = "débil"
    elif 0.4 <= abs_r < 0.6:
        strength = "moderada"
    elif 0.6 <= abs_r < 0.8:
        strength = "fuerte"
    else:
        strength = "muy fuerte"
        
    explanation = f"Existe una asociación lineal {sign_str} {strength} entre las variables."
    return explanation

def run(df: pd.DataFrame, col_x: str, col_y: str) -> Dict[str, Any]:
    """
    Explica paso a paso el cálculo matemático del coeficiente de correlación de Pearson.
    """
    output = {
        "status": "success",
        "variables": [col_x, col_y],
        "n_observaciones": 0,
        "medias": {},
        "sumatorias": {},
        "resultado_r": None,
        "interpretacion": "",
        "advertencia_causalidad": "IMPORTANTE: Pearson mide asociación lineal y no demuestra causalidad. Un valor alto de r no comprueba que una variable cause la otra."
    }
    
    # 1. Validaciones básicas
    if df is None or df.empty:
        output["status"] = "error"
        output["error"] = "DataFrame vacío o nulo."
        return output
        
    if col_x not in df.columns or col_y not in df.columns:
        output["status"] = "error"
        output["error"] = f"Las columnas {col_x} y/o {col_y} no existen."
        return output
        
    # Filtrar NaNs para estas dos columnas puntuales
    clean_df = df[[col_x, col_y]].dropna()
    n = len(clean_df)
    output["n_observaciones"] = n
    
    if n < 2:
        output["status"] = "error"
        output["error"] = "Datos insuficientes (se requieren al menos 2 observaciones sin NaN)."
        return output
        
    x = clean_df[col_x].astype(float).values
    y = clean_df[col_y].astype(float).values
    
    # 2. Medias
    x_mean = float(np.mean(x))
    y_mean = float(np.mean(y))
    output["medias"][col_x] = x_mean
    output["medias"][col_y] = y_mean
    
    # 3. Desviaciones y Productos
    x_dev = x - x_mean
    y_dev = y - y_mean
    
    sum_prod_dev = float(np.sum(x_dev * y_dev))
    sum_sq_x = float(np.sum(x_dev ** 2))
    sum_sq_y = float(np.sum(y_dev ** 2))
    
    output["sumatorias"]["sum_prod_desviaciones_xy"] = sum_prod_dev
    output["sumatorias"]["sum_cuadrados_x"] = sum_sq_x
    output["sumatorias"]["sum_cuadrados_y"] = sum_sq_y
    
    # Verificación de constante
    if sum_sq_x == 0 or sum_sq_y == 0:
        output["status"] = "error"
        output["error"] = "Variable constante (varianza 0). No se puede calcular Pearson."
        return output
        
    # 4. Cálculo final
    r = sum_prod_dev / np.sqrt(sum_sq_x * sum_sq_y)
    output["resultado_r"] = r
    
    # 5. Interpretación
    output["interpretacion"] = interpret_pearson(r)
    
    return output
