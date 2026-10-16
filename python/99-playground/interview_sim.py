from __future__ import annotations

import bisect
from collections import Counter, defaultdict, deque
import heapq
import itertools
import sys
import time
from typing import Any

"""
🎯 SIMULADOR DE ENTREVISTA EN VIVO — PROTOCOLO UMPIRE (`99-playground/interview_sim.py`)
===============================================================================
Usa esta plantilla cuando quieras resolver un reto algorítmico desde cero
(de LeetCode, HackerRank o inventado por ti) aplicando el protocolo de 4 fases:

1. [U] Understand: Anota entradas, salidas y casos borde (vacío, 1 elem, duplicados).
2. [M] Match & Plan: Elige la estructura/patrón (Hash Map, Two Pointers, Sliding Window,
   Heap, BFS/DFS, DP) y escribe tu complejidad objetivo Tiempo/Espacio.
3. [I] Implement: Programa tu solución en `resolver(...)` sin autocompletado de IA.
4. [R/E] Review & Evaluate: Agrega tus casos en `CASOS_DE_PRUEBA` y presiona `R`.
===============================================================================
"""


# ==============================================================================
# 1. TU SOLUCIÓN (Modifica la firma y el cuerpo libremente)
# ==============================================================================
def resolver(nums: list[int], k: int) -> list[int]:
    """
    Problema de ejemplo (puedes borrarlo y poner el reto que quieras practicar):
    Dados una lista de enteros `nums` y un entero `k`, devuelve los `k` elementos
    más frecuentes ordenados de mayor a menor frecuencia.

    Complejidad objetivo:
        Tiempo: O(n log k) | Espacio: O(n)
    """
    # BEGIN_SOLUTION
    conteo = Counter(nums)
    return [num for num, _ in conteo.most_common(k)]
    # END_SOLUTION


# ==============================================================================
# 2. TUS CASOS DE PRUEBA: ((arg1, arg2, ...), resultado_esperado)
# ==============================================================================
CASOS_DE_PRUEBA: list[tuple[tuple[Any, ...], Any]] = [
    (([1, 1, 1, 2, 2, 3], 2), [1, 2]),
    (([4], 1), [4]),
    (([5, 3, 5, 2, 3, 5, 3, 3], 1), [3]),
]


def ejecutar_simulacro() -> None:
    print("=" * 72)
    print("🎯 SIMULADOR DE ENTREVISTA TÉCNICA (interview_sim.py)")
    print("=" * 72)

    pasados = 0
    for idx, (args, esperado) in enumerate(CASOS_DE_PRUEBA, start=1):
        t0 = time.perf_counter()
        try:
            obtenido = resolver(*args)
            ms = (time.perf_counter() - t0) * 1000
            if obtenido == esperado:
                print(f"  ✅ Caso #{idx}: PASS ({ms:.2f} ms) | args={args} -> {obtenido!r}")
                pasados += 1
            else:
                print(
                    f"  ❌ Caso #{idx}: FAIL ({ms:.2f} ms)\n"
                    f"     Entrada : {args}\n"
                    f"     Esperado: {esperado!r}\n"
                    f"     Obtenido: {obtenido!r}"
                )
        except Exception as exc:
            print(f"  💥 Caso #{idx}: EXCEPCIÓN -> {type(exc).__name__}: {exc}")

    print("-" * 72)
    print(f"Resultado del Simulacro: {pasados}/{len(CASOS_DE_PRUEBA)} casos superados.")
    print("=" * 72)
    if pasados < len(CASOS_DE_PRUEBA):
        sys.exit(1)


if __name__ == "__main__":
    ejecutar_simulacro()
