"""Validaciones comunes para integración numérica."""

from __future__ import annotations

import math


class ErrorValidacion(ValueError):
    """Entrada inválida que puede mostrarse directamente al usuario."""


def numero_finito(valor: object, nombre: str) -> float:
    if isinstance(valor, bool):
        raise ErrorValidacion(f"{nombre} debe ser un número real.")
    try:
        numero = float(valor)
    except (TypeError, ValueError) as exc:
        raise ErrorValidacion(f"{nombre} debe ser un número real.") from exc
    if not math.isfinite(numero):
        raise ErrorValidacion(f"{nombre} debe ser finito.")
    return numero


def entero_positivo(valor: object, nombre: str = "n") -> int:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ErrorValidacion(f"{nombre} debe ser un entero positivo.")
    if valor <= 0:
        raise ErrorValidacion(f"{nombre} debe ser mayor que cero.")
    return valor


def validar_intervalo(a: object, b: object) -> tuple[float, float]:
    limite_a = numero_finito(a, "El límite a")
    limite_b = numero_finito(b, "El límite b")
    if limite_a == limite_b:
        raise ErrorValidacion("Los límites a y b deben ser diferentes.")
    return limite_a, limite_b


__all__ = ["ErrorValidacion", "numero_finito", "entero_positivo", "validar_intervalo"]

