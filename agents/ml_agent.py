import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def run(df: pd.DataFrame, target_col: str = 'ndvi', feature_cols: List[str] = None) -> Dict[str, Any]:
    """
    Agente de Machine Learning (Baseline Supervisado).
    
    Responsabilidad: Entrenar y evaluar un modelo base para un target y features dadas, 
    respetando el rigor metodológico (separación train/test, data leakage).
    """
    output = {
        "status": "",
        "target": target_col,
        "features": feature_cols if feature_cols else [],
        "n_observaciones_totales": 0,
        "n_train": 0,
        "n_test": 0,
        "estrategia_split": "Temporal (80% pasado -> train, 20% futuro -> test)",
        "modelo": "Linear Regression (Baseline)",
        "metricas_test": {},
        "advertencias": [],
        "limitaciones": [
            "Un baseline no representa todavía un modelo productivo.",
            "Ausencia de Lags: El clima actual impacta poco el NDVI del mismo instante.",
            "Región interandina: Observaciones satelitales bajas limitan el muestreo drásticamente."
        ]
    }
    
    if df is None or df.empty:
        output["status"] = "FALLO"
        output["advertencias"].append("DataFrame vacío.")
        return output
        
    if target_col not in df.columns:
        output["status"] = "FALLO - BLOCKED"
        output["advertencias"].append(f"ML baseline = BLOCKED. No existe el target supervisado '{target_col}'.")
        return output
        
    if feature_cols is None:
        # Default de características atmosféricas que no leak-ean el target (B4 y B8 construyen NDVI, no se usan)
        feature_cols = ['T2M', 'RH2M', 'PRECTOTCORR', 'ALLSKY_SFC_SW_DWN', 'VPD']
        
    missing_features = [col for col in feature_cols if col not in df.columns]
    if missing_features:
        output["status"] = "FALLO"
        output["advertencias"].append(f"Faltan features en el dataset: {missing_features}")
        return output
        
    # Ordenamiento temporal estricto
    if 'date' in df.columns:
        df = df.sort_values(by='date').reset_index(drop=True)
    else:
        output["advertencias"].append("No existe columna 'date'. Se asume que el índice ya está ordenado temporalmente, riesgo de _data leakage_ si no lo está.")
        
    # Filtrar NaNs para Target y Features
    clean_df = df[feature_cols + [target_col]].dropna()
    n_total = len(clean_df)
    output["n_observaciones_totales"] = n_total
    
    # Evaluar suficiencia de datos (Regla general simple empírica p ej. min 15)
    if n_total < 10:
        output["status"] = "FALLO"
        output["advertencias"].append(f"Muestra muy baja ({n_total} filas) para separar train/test e inferir modelo.")
        return output
        
    # Split Temporal 80/20 manual sin aleatoriedad para no mezclar futuro con pasado
    split_idx = int(n_total * 0.8)
    
    train_df = clean_df.iloc[:split_idx]
    test_df = clean_df.iloc[split_idx:]
    
    output["n_train"] = len(train_df)
    output["n_test"] = len(test_df)
    
    X_train = train_df[feature_cols]
    y_train = train_df[target_col]
    
    X_test = test_df[feature_cols]
    y_test = test_df[target_col]
    
    # Preprocesamiento seguro (Fit solo en train)
    scaler = StandardScaler()
    try:
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
    except Exception as e:
        output["status"] = "FALLO"
        output["advertencias"].append(f"Error en scaling: {e}")
        return output
        
    # Baseline
    model = LinearRegression()
    try:
        model.fit(X_train_scaled, y_train)
        preds = model.predict(X_test_scaled)
    except Exception as e:
        output["status"] = "FALLO"
        output["advertencias"].append(f"Error entrenando modelo base: {e}")
        return output
        
    # Evaluación
    mae = mean_absolute_error(y_test, preds)
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    r2 = r2_score(y_test, preds)
    
    output["metricas_test"] = {
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2
    }
    
    if r2 < 0:
        output["advertencias"].append("R2 negativo en Test: El baseline rinde peor que predecir simplemente la media esperada global. Confirmación de bajo poder predictivo de los features climáticos sin Lag temporal.")
        
    output["status"] = "OK"
    return output
