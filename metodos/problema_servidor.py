"""Ejercicio oficial: datos transferidos por un servidor web."""

from __future__ import annotations

import math

from .trapecio import desarrollar_trapecio_compuesto, trapecio_compuesto
from .validaciones import entero_positivo, validar_intervalo


N_CONVERGENCIA = (4, 10, 50, 100, 1000)


def tasa_transferencia(t: float) -> float:
    """R(t) en Mbps."""
    return 10.0 + 5.0 * math.sin(math.pi * t / 4.0) + math.exp(0.15 * t)


def primitiva_tasa(t: float) -> float:
    return 10.0 * t - (20.0 / math.pi) * math.cos(math.pi * t / 4.0) + math.exp(0.15 * t) / 0.15


def integral_exacta(a: float, b: float) -> float:
    a, b = validar_intervalo(a, b)
    return primitiva_tasa(b) - primitiva_tasa(a)


def tabla_convergencia(a: float, b: float, valores_n=None) -> list[dict]:
    a, b = validar_intervalo(a, b)
    valores = N_CONVERGENCIA if valores_n is None else tuple(valores_n)
    exacta = integral_exacta(a, b)
    filas = []
    for valor_n in valores:
        n = entero_positivo(valor_n)
        aproximacion = trapecio_compuesto(tasa_transferencia, a, b, n)
        error_absoluto = abs(exacta - aproximacion)
        error_porcentual = 0.0 if exacta == 0 and error_absoluto == 0 else (
            math.inf if exacta == 0 else error_absoluto / abs(exacta) * 100.0
        )
        filas.append({
            "n": n,
            "aproximacion": aproximacion,
            "error_absoluto": error_absoluto,
            "error_porcentual": error_porcentual,
        })
    return filas


def resolver_servidor(a: float, b: float, n: int) -> dict:
    a, b = validar_intervalo(a, b)
    n = entero_positivo(n)
    desarrollo = desarrollar_trapecio_compuesto(tasa_transferencia, a, b, n)
    exacta = integral_exacta(a, b)
    error_absoluto = abs(exacta - desarrollo["aproximacion"])
    error_porcentual = 0.0 if exacta == 0 and error_absoluto == 0 else (
        math.inf if exacta == 0 else error_absoluto / abs(exacta) * 100.0
    )
    ns = list(N_CONVERGENCIA)
    if n not in ns:
        ns.insert(0, n)
    convergencia = tabla_convergencia(a, b, ns)
    errores_estandar = [fila["error_absoluto"] for fila in convergencia if fila["n"] in N_CONVERGENCIA]
    error_disminuye = all(
        errores_estandar[i + 1] < errores_estandar[i]
        for i in range(len(errores_estandar) - 1)
    ) if a < b else None
    cantidad_muestras = 241
    grafica_funcion = [
        {"x": a + (b - a) * i / (cantidad_muestras - 1),
         "y": tasa_transferencia(a + (b - a) * i / (cantidad_muestras - 1))}
        for i in range(cantidad_muestras)
    ]
    return {
        **desarrollo,
        "funcion": "R(t) = 10 + 5 sin(pi t / 4) + e^(0.15 t)",
        "unidad_x": "segundos",
        "unidad_funcion": "Mbps",
        "unidad_integral": "Megabits",
        "exacta": exacta,
        "formula_exacta": "[10t - (20/pi)cos(pi t/4) + e^(0.15t)/0.15]_a^b",
        "error_absoluto": error_absoluto,
        "error_porcentual": error_porcentual,
        "convergencia": convergencia,
        "error_disminuye": error_disminuye,
        "grafica_funcion": grafica_funcion,
    }


__all__ = [
    "N_CONVERGENCIA", "tasa_transferencia", "primitiva_tasa", "integral_exacta",
    "tabla_convergencia", "resolver_servidor",
]
