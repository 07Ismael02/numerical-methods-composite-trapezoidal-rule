"""Regla del Trapecio Compuesto implementada mediante sumas explícitas."""

from __future__ import annotations

import math
from collections.abc import Callable

from .validaciones import ErrorValidacion, entero_positivo, validar_intervalo


def _evaluar(f: Callable[[float], float], x: float) -> float:
    try:
        valor = f(x)
    except Exception as exc:
        raise ErrorValidacion(f"La función no pudo evaluarse en x={x:.12g}.") from exc
    if isinstance(valor, bool):
        raise ErrorValidacion(f"La función no devolvió un número real en x={x:.12g}.")
    try:
        numero = float(valor)
    except (TypeError, ValueError) as exc:
        raise ErrorValidacion(f"La función no devolvió un número real en x={x:.12g}.") from exc
    if not math.isfinite(numero):
        raise ErrorValidacion(f"La función devolvió un valor no finito en x={x:.12g}.")
    return numero


def trapecio_compuesto(f: Callable[[float], float], a: float, b: float, n: int) -> float:
    """Aproxima integral_a^b f(x) dx sin usar rutinas externas de integración."""
    if not callable(f):
        raise ErrorValidacion("f debe ser una función invocable.")
    a, b = validar_intervalo(a, b)
    n = entero_positivo(n)
    h = (b - a) / n
    suma = 0.5 * _evaluar(f, a) + 0.5 * _evaluar(f, b)
    for i in range(1, n):
        suma += _evaluar(f, a + i * h)
    return h * suma


def desarrollar_trapecio_compuesto(
    f: Callable[[float], float], a: float, b: float, n: int
) -> dict:
    """Devuelve la aproximación y una traza académica de todos los términos."""
    if not callable(f):
        raise ErrorValidacion("f debe ser una función invocable.")
    a, b = validar_intervalo(a, b)
    n = entero_positivo(n)
    h = (b - a) / n
    puntos: list[dict] = []
    suma_ponderada = 0.0
    for i in range(n + 1):
        x_i = a + i * h
        f_i = _evaluar(f, x_i)
        peso = 0.5 if i in (0, n) else 1.0
        aporte = peso * f_i
        suma_ponderada += aporte
        puntos.append(
            {"i": i, "x": x_i, "fx": f_i, "peso": peso, "aporte": aporte}
        )
    aproximacion = h * suma_ponderada
    interior = sum(punto["fx"] for punto in puntos[1:-1])
    return {
        "a": a,
        "b": b,
        "n": n,
        "h": h,
        "puntos": puntos,
        "suma_interior": interior,
        "suma_ponderada": suma_ponderada,
        "aproximacion": aproximacion,
        "formula": "T_n = h [f(x_0)/2 + sum_{i=1}^{n-1} f(x_i) + f(x_n)/2]",
        "calculo_h": f"h = ({b:.12g} - {a:.12g}) / {n} = {h:.12g}",
        "malla": [punto["x"] for punto in puntos],
    }


__all__ = ["trapecio_compuesto", "desarrollar_trapecio_compuesto"]

