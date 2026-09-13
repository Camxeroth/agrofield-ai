from typing import Dict, Any, List

def interpret_ph(ph: float) -> str:
    """Interpreta el nivel de pH para el cultivo de papa."""
    if ph < 5.0:
        return "Muy ácido. Requiere encalado intenso para cultivo de papa."
    elif 5.0 <= ph < 5.5:
        return "Ácido. Tolera la papa, pero el rendimiento puede mejorar con enmiendas."
    elif 5.5 <= ph <= 6.5:
        return "Óptimo para cultivo de papa. Buena disponibilidad de nutrientes."
    elif 6.5 < ph <= 7.3:
        return "Ligeramente alcalino. Aceptable pero vigilar la disponibilidad de micronutrientes."
    else:
        return "Alcalino. Condiciones desfavorables, alto riesgo de sarna común en la papa."

def interpret_soc(soc: float) -> str:
    """Interpreta el carbono orgánico del suelo."""
    if soc < 2.0:
        return "Bajo contenido de materia orgánica. Se sugiere incorporar abonos orgánicos."
    elif 2.0 <= soc <= 4.0:
        return "Contenido medio a adecuado de materia orgánica."
    else:
        return "Alto contenido de materia orgánica. Excelente fertilidad potencial."

def interpret_texture(sand: float, silt: float, clay: float) -> str:
    """Interpreta la textura del suelo."""
    if sand > 65:
        return "Textura arenosa. Alto drenaje, baja retención de humedad, riesgo de lavado de nutrientes."
    elif clay > 40:
        return "Textura arcillosa. Riesgo de encharcamiento y compactación, dificulta el desarrollo de tubérculos."
    elif 30 <= sand <= 50 and 30 <= silt <= 50 and 10 <= clay <= 30:
        return "Textura franca a franco-arenosa. Ideal para el desarrollo radicular y expansión de tubérculos de papa."
    else:
        return "Textura equilibrada a pesada. Monitorear el drenaje para evitar asfixia radicular en lluvias intensas."

def run(soil_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recibe los datos crudos de SoilGrids y devuelve una interpretación agronómica.
    
    Args:
        soil_data: Diccionario con los datos del suelo, como los generados por get_soil_data()
        
    Returns:
        Diccionario con la interpretación del suelo y notas agronómicas.
    """
    if not soil_data:
        return {"error": "No se proporcionaron datos de suelo para procesar."}
        
    ph_data = soil_data.get("phh2o")
    soc_data = soil_data.get("soc")
    sand_data = soil_data.get("sand")
    silt_data = soil_data.get("silt")
    clay_data = soil_data.get("clay")
    depth = soil_data.get("profundidad", "No informada")
    
    agronomic_notes: List[str] = []
    
    # Interpretación pH
    ph_interp = "Dato de pH no disponible."
    if ph_data and "valor" in ph_data:
        ph_val = ph_data["valor"]
        ph_interp = interpret_ph(ph_val)
        agronomic_notes.append(f"pH actual: {ph_val:.2f} - {ph_interp}")
        
    # Interpretación SOC
    soc_interp = "Dato de carbono orgánico no disponible."
    if soc_data and "valor" in soc_data:
        soc_val = soc_data["valor"]
        soc_interp = interpret_soc(soc_val)
        agronomic_notes.append(f"Carbono orgánico: {soc_val:.2f}% - {soc_interp}")
        
    # Interpretación Textura
    texture_interp = "Datos de textura incompletos."
    if sand_data and silt_data and clay_data:
        sand_val = sand_data.get("valor", 0)
        silt_val = silt_data.get("valor", 0)
        clay_val = clay_data.get("valor", 0)
        texture_interp = interpret_texture(sand_val, silt_val, clay_val)
        agronomic_notes.append(f"Textura (Arena: {sand_val:.1f}%, Limo: {silt_val:.1f}%, Arcilla: {clay_val:.1f}%) - {texture_interp}")
        
    summary = f"Análisis de suelo completado para la capa {depth}. Evaluadas {len(agronomic_notes)} variables. Las condiciones generales deben interpretarse junto con el régimen climático para decisiones de abonado."
    
    return {
        "summary": summary,
        "ph_interpretation": ph_interp,
        "organic_carbon_interpretation": soc_interp,
        "texture_interpretation": texture_interp,
        "agronomic_notes": agronomic_notes
    }
