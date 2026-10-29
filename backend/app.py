"""API Flask para la Regla del Trapecio Compuesto."""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import BadRequest

from metodos.problema_servidor import resolver_servidor
from metodos.validaciones import ErrorValidacion, entero_positivo, validar_intervalo


app = Flask(__name__)


def _leer_json() -> dict:
    if not request.is_json:
        raise ErrorValidacion("La solicitud debe usar JSON con Content-Type application/json.")
    try:
        datos = request.get_json(silent=False)
    except BadRequest as exc:
        raise ErrorValidacion("El cuerpo contiene JSON inválido.") from exc
    if not isinstance(datos, dict):
        raise ErrorValidacion("El cuerpo JSON debe ser un objeto.")
    return datos


@app.get("/")
def inicio():
    return render_template("index.html")


@app.get("/favicon.ico")
def favicon():
    return "", 204


@app.post("/api/trapecio")
def api_trapecio():
    try:
        datos = _leer_json()
        a, b = validar_intervalo(datos.get("a"), datos.get("b"))
        n = entero_positivo(datos.get("n"))
        return jsonify({"ok": True, **resolver_servidor(a, b, n)})
    except ErrorValidacion as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5003, debug=False)

