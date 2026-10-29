import unittest

from metodos.problema_servidor import integral_exacta, resolver_servidor, tabla_convergencia


class ConvergenciaTests(unittest.TestCase):
    ESPERADOS = {
        4: 160.443697114248,
        10: 165.530824072070,
        50: 166.362626089151,
        100: 166.388194634868,
        1000: 166.396626718217,
    }

    def test_valor_exacto_oficial(self):
        self.assertAlmostEqual(integral_exacta(0, 12), 166.39671187677126, places=12)

    def test_resultados_oficiales_calculados(self):
        filas = tabla_convergencia(0, 12)
        for fila in filas:
            self.assertAlmostEqual(fila["aproximacion"], self.ESPERADOS[fila["n"]], places=11)

    def test_error_disminuye(self):
        filas = tabla_convergencia(0, 12)
        errores = [fila["error_absoluto"] for fila in filas]
        self.assertTrue(all(errores[i + 1] < errores[i] for i in range(len(errores) - 1)))

    def test_resolucion_oficial_incluye_desarrollo_y_graficas(self):
        resultado = resolver_servidor(0, 12, 4)
        self.assertAlmostEqual(resultado["h"], 3)
        self.assertEqual(resultado["malla"], [0, 3, 6, 9, 12])
        self.assertEqual(len(resultado["puntos"]), 5)
        self.assertEqual(len(resultado["grafica_funcion"]), 241)
        self.assertTrue(resultado["error_disminuye"])

    def test_referencia_se_recalcula_para_otro_intervalo(self):
        resultado = resolver_servidor(2, 7, 20)
        self.assertAlmostEqual(resultado["exacta"], integral_exacta(2, 7))
        self.assertNotAlmostEqual(resultado["exacta"], integral_exacta(0, 12))


if __name__ == "__main__":
    unittest.main()

