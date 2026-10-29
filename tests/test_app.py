import unittest

from backend.app import app


class AppTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_inicio(self):
        respuesta = self.client.get("/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("Trapecio Compuesto".encode(), respuesta.data)

    def test_api_caso_oficial(self):
        respuesta = self.client.post("/api/trapecio", json={"a": 0, "b": 12, "n": 4})
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.get_json()
        self.assertTrue(datos["ok"])
        self.assertAlmostEqual(datos["aproximacion"], 160.443697114248, places=11)
        self.assertEqual(len(datos["convergencia"]), 5)

    def test_api_parametros_dinamicos(self):
        respuesta = self.client.post("/api/trapecio", json={"a": 1, "b": 5, "n": 7})
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.get_json()
        self.assertEqual(datos["n"], 7)
        self.assertAlmostEqual(datos["h"], 4 / 7)
        self.assertEqual(datos["convergencia"][0]["n"], 7)

    def test_api_rechaza_json_y_n_invalidos(self):
        respuesta = self.client.post("/api/trapecio", data="{}", content_type="text/plain")
        self.assertEqual(respuesta.status_code, 400)
        for n in (0, -2, 2.5, "4", True):
            with self.subTest(n=n):
                respuesta = self.client.post("/api/trapecio", json={"a": 0, "b": 12, "n": n})
                self.assertEqual(respuesta.status_code, 400)


if __name__ == "__main__":
    unittest.main()

