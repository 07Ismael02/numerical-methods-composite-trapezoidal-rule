import math
import unittest

from metodos.trapecio import desarrollar_trapecio_compuesto, trapecio_compuesto
from metodos.validaciones import ErrorValidacion


class TrapecioCompuestoTests(unittest.TestCase):
    def test_funcion_lineal_es_exacta(self):
        self.assertAlmostEqual(trapecio_compuesto(lambda x: x, 0, 1, 7), 0.5)

    def test_traza_pesos_y_malla(self):
        resultado = desarrollar_trapecio_compuesto(lambda x: x * x, 0, 2, 4)
        self.assertEqual(resultado["h"], 0.5)
        self.assertEqual(resultado["malla"], [0, 0.5, 1, 1.5, 2])
        self.assertEqual([p["peso"] for p in resultado["puntos"]], [0.5, 1, 1, 1, 0.5])
        self.assertAlmostEqual(resultado["aproximacion"], 2.75)

    def test_intervalo_invertido_conserva_orientacion(self):
        self.assertAlmostEqual(trapecio_compuesto(lambda x: x, 1, 0, 8), -0.5)

    def test_rechaza_n_invalido(self):
        for n in (0, -1, 2.5, "4", True):
            with self.subTest(n=n), self.assertRaises(ErrorValidacion):
                trapecio_compuesto(lambda x: x, 0, 1, n)

    def test_rechaza_limites_y_evaluaciones_invalidas(self):
        with self.assertRaises(ErrorValidacion):
            trapecio_compuesto(lambda x: x, 1, 1, 4)
        with self.assertRaises(ErrorValidacion):
            trapecio_compuesto(lambda x: math.inf, 0, 1, 4)
        with self.assertRaises(ErrorValidacion):
            trapecio_compuesto(None, 0, 1, 4)


if __name__ == "__main__":
    unittest.main()

