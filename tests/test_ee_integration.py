import unittest
import ee
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.ee_extractor import EarthEngineExtractor

class TestEEIntegration(unittest.TestCase):
    def setUp(self):
        try:
            self.extractor = EarthEngineExtractor()
            self.can_init = True
        except ee.EEException:
            # We don't have a configured project or credentials in this environment
            self.can_init = False
            
    def test_ee_initialization(self):
        """
        Prueba de integración real con Earth Engine.
        Solo se ejecuta si el analista tiene configurado un GCP project subyacente de forma correcta.
        """
        if not self.can_init:
            self.skipTest("Earth Engine GCP project no configurado en este entorno. Ejecute 'earthengine set_project'.")
            return
            
        # Prueba real a EE con un rango de tiempo que incluya el 29 de Julio
        df = self.extractor.get_sentinel2_timeseries(-78.65, -1.63, '2026-07-01', '2026-07-31')
        self.assertIsNotNone(df)
        self.assertTrue('ndvi' in df.columns)
        self.assertTrue('ndwi' in df.columns)
        
        # Validar la observación específica del 29/07/2026
        val_date = df[df['date'] == '2026-07-29']
        self.assertEqual(len(val_date), 1, "Debería haber exactamente 1 observación en esta fecha")
        
        row = val_date.iloc[0]
        # Validación de bandas
        self.assertAlmostEqual(row['B3'], 1320, delta=1)
        self.assertAlmostEqual(row['B4'], 1595, delta=1)
        self.assertAlmostEqual(row['B8'], 2352, delta=1)
        # Validación de índices calculados en EE usando nuestro módulo base como comparativa de tolerancia
        self.assertAlmostEqual(row['ndvi'], 0.191791, places=4)
        self.assertAlmostEqual(row['ndwi'], -0.281046, places=4)

if __name__ == '__main__':
    unittest.main()
