import unittest
import sys
import os

# Asegurar que se puede importar desde src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.features.indices import calculate_ndvi, calculate_ndwi

class TestIndices(unittest.TestCase):
    def test_calculate_ndvi_normal(self):
        # Valores de prueba provistos para validación
        nir = 0.2352
        red = 0.1595
        
        expected_ndvi = 0.1918
        
        result_ndvi = calculate_ndvi(nir, red)
        
        # Validar con un margen de error (aproximación a 4 decimales)
        self.assertAlmostEqual(result_ndvi, expected_ndvi, places=4)

    def test_calculate_ndvi_zero_division(self):
        # Caso donde nir + red = 0
        nir = 0.0
        red = 0.0
        self.assertEqual(calculate_ndvi(nir, red), 0.0)

    def test_calculate_ndwi_normal(self):
        # Prueba estructural para NDWI
        green = 0.2000
        nir = 0.1000
        # NDWI = (0.2000 - 0.1000) / (0.2000 + 0.1000) = 0.1 / 0.3 = 0.3333
        result_ndwi = calculate_ndwi(green, nir)
        self.assertAlmostEqual(result_ndwi, 0.3333, places=4)

    def test_calculate_ndwi_zero_division(self):
        # Caso donde green + nir = 0
        green = 0.0
        nir = 0.0
        self.assertEqual(calculate_ndwi(green, nir), 0.0)

if __name__ == '__main__':
    unittest.main()
