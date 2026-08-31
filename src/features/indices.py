def calculate_ndvi(nir, red):
    """
    Calcula el Índice de Vegetación de Diferencia Normalizada (NDVI).
    
    Args:
        nir (float): Valor de la banda infrarroja cercana (NIR, ej. B8).
        red (float): Valor de la banda roja (RED, ej. B4).
        
    Returns:
        float: Valor de NDVI, o 0.0 si nir + red == 0.
    """
    nir = float(nir)
    red = float(red)
    
    denominator = nir + red
    if denominator == 0:
        return 0.0
        
    return (nir - red) / denominator


def calculate_ndwi(green, nir):
    """
    Calcula el Índice Diferencial de Agua Normalizado (NDWI).
    
    Args:
        green (float): Valor de la banda verde (GREEN, ej. B3).
        nir (float): Valor de la banda infrarroja cercana (NIR, ej. B8).
        
    Returns:
        float: Valor de NDWI, o 0.0 si green + nir == 0.
    """
    green = float(green)
    nir = float(nir)
    
    denominator = green + nir
    if denominator == 0:
        return 0.0
        
    return (green - nir) / denominator
