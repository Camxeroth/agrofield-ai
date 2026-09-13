import math
from typing import Dict, Any

def run(manual_r: float, python_r: float, math_agent_r: float, tolerance: float = 1e-6) -> Dict[str, Any]:
    """
    Comprueba si diferentes fuentes de cálculo de correlación producen el mismo resultado.
    Establece la continuidad algorítmica y evalúa posibles diferencias.
    
    Flujo esperado en el proyecto:
    MANUAL → PYTHON → AGENT → VALIDATION
    
    Args:
        manual_r: Resultado crudo precalculado (esperado teóricamente o del Día 18).
        python_r: Resultado arrojado por Statistics Agent u operación de Pandas nativa.
        math_agent_r: Resultado desagregado del Math Agent usando Numpy explícito.
        tolerance: Margen aceptado de error numérico.
        
    Returns:
        Diccionario con el dictamen de la validación.
    """
    output = {
        "status": "",
        "inputs_recibidos": {
            "manual": manual_r,
            "python_statistics": python_r,
            "math_agent": math_agent_r
        },
        "diferencias_absolutas": {},
        "mensaje": "",
        "recomendacion": ""
    }
    
    # Check nulls (si alguno no se pudo calcular por varianza 0 o insuficiencia de datos)
    if manual_r is None or math.isnan(manual_r) or \
       python_r is None or math.isnan(python_r) or \
       math_agent_r is None or math.isnan(math_agent_r):
        output["status"] = "FALLO"
        output["mensaje"] = "Hay valores faltantes (NaN o None) en las entradas. No se puede validar equidad."
        return output
        
    diff_manual_python = abs(manual_r - python_r)
    diff_python_math = abs(python_r - math_agent_r)
    diff_manual_math = abs(manual_r - math_agent_r)
    
    output["diferencias_absolutas"] = {
        "manual_vs_python": diff_manual_python,
        "python_vs_math_agent": diff_python_math,
        "manual_vs_math_agent": diff_manual_math
    }
    
    diffs = [diff_manual_python, diff_python_math, diff_manual_math]
    
    if all(d <= tolerance for d in diffs):
        output["status"] = "VALIDADO"
        output["mensaje"] = f"Todos los métodos matemáticos y computacionales coinciden con el margen de {tolerance}."
        output["recomendacion"] = "Resultados listos para consumo seguro por agentes biológicos o agronómicos futuros."
    else:
        output["status"] = "DISCREPANCIA"
        
        # Verificar diferencia significativa vs diferencia por error flotante / redondeo menor (1e-3)
        if any(d > 1e-3 for d in diffs):
            output["mensaje"] = "Se detectó una discrepancia severa metodológica entre los cálculos teóricos y computacionales."
            output["recomendacion"] = "Revisar las operaciones o inputs en el Math Agent / Statistics Agent."
        else:
            output["mensaje"] = "Se detectó error leve numérico de redondeo entre entornos/fórmulas."
            output["recomendacion"] = "Tolerable bajo fines biológicos, pero revisar exactitud de punto flotante en producción."
            
    return output
