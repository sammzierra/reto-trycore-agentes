import unittest
from main import ejecutar_diagnostico, calcular_puntaje_exito, cargar_configuracion

class TestSistemaTrycore(unittest.TestCase):

    def setUp(self):
        self.config, self.ventana = cargar_configuracion()

    # Prueba 1: Diagnóstico detecta productos vigentes
    def test_productos_vigentes(self):
        texto = "Optimizamos procesos con ORIUNO y Docfly en la empresa."
        diag = ejecutar_diagnostico(texto, self.config)
        self.assertIn("ORIUNO", diag["indicadores"]["productos_vigentes_detectados"])

    # Prueba 2: Diagnóstico alerta sobre términos prohibidos reales
    def test_termino_prohibido(self):
        termino_prohibido = self.config.get("terminos_prohibidos", [{}])[0].get("termino", "barato")
        texto = f"Este producto es muy {termino_prohibido} para la empresa."
        diag = ejecutar_diagnostico(texto, self.config)
        self.assertGreater(len(diag["alertas"]), 0)

    # Prueba 3: Diagnóstico detecta nombres confidenciales reales
    def test_nombre_confidencial(self):
        nombre_conf = self.config.get("nombres_confidenciales", ["Cliente X"])[0]
        texto = f"Este es un informe confidencial sobre {nombre_conf}."
        diag = ejecutar_diagnostico(texto, self.config)
        self.assertFalse(diag["apto_para_transformacion"])

    # Prueba 4: El puntaje de éxito calcula correctamente
    def test_puntaje_exito(self):
        pieza_post = {
            "formato": "post_linkedin", 
            "gancho": "Un gancho llamativo de más de 20 caracteres para el post", 
            "utm_link": "https://trycore.com?utm_source=linkedin"
        }
        score = calcular_puntaje_exito(pieza_post)
        self.assertGreaterEqual(score, 80)

    # Prueba 5: El puntaje de éxito no supera los 100 puntos
    def test_puntaje_maximo(self):
        pieza_post = {
            "formato": "carrusel_linkedin", 
            "gancho": "Un gancho muy largo para sumar la máxima cantidad de puntos", 
            "utm_link": "https://trycore.com?utm_source=linkedin"
        }
        score = calcular_puntaje_exito(pieza_post)
        self.assertLessEqual(score, 100)

if __name__ == '__main__':
    unittest.main()
