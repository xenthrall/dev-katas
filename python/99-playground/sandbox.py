from __future__ import annotations

from collections import Counter, defaultdict, deque
import dis
import sys
import time
from typing import Any, Callable

"""
🔬 LABORATORIO DE INTERNALS, MEMORIA Y BENCHMARKS (`99-playground/sandbox.py`)
===============================================================================
Usa este archivo cuando quieras responder preguntas como:
- "¿Qué es más rápido en Python: opción A u opción B?" -> usa `comparar_rendimiento()`
- "¿Qué instrucciones de bytecode genera esta función?" -> usa `ver_bytecode()`
- "¿Cuánta memoria RAM ocupa esta estructura?"          -> usa `ver_memoria()`
===============================================================================
"""


def comparar_rendimiento(
    fn_a: Callable[[], Any],
    fn_b: Callable[[], Any],
    iteraciones: int = 5_000,
) -> None:
    """Compara el tiempo de ejecución de dos funciones y verifica que den el mismo resultado."""
    res_a = fn_a()
    res_b = fn_b()

    t0 = time.perf_counter()
    for _ in range(iteraciones):
        fn_a()
    ms_a = (time.perf_counter() - t0) * 1000

    t1 = time.perf_counter()
    for _ in range(iteraciones):
        fn_b()
    ms_b = (time.perf_counter() - t1) * 1000

    ganador = fn_a.__name__ if ms_a <= ms_b else fn_b.__name__
    ratio = max(ms_a, ms_b) / max(min(ms_a, ms_b), 1e-9)

    print(f"🏁 Benchmark ({iteraciones:,} iteraciones):")
    print(f"   • {fn_a.__name__:<25}: {ms_a:>8.2f} ms")
    print(f"   • {fn_b.__name__:<25}: {ms_b:>8.2f} ms")
    print(f"   🏆 Más rápida: {ganador} ({ratio:.2f}x) | ¿Resultados iguales?: {res_a == res_b}")


def ver_bytecode(fn: Callable[..., Any]) -> None:
    """Desensambla y muestra las instrucciones de la Máquina Virtual de CPython para `fn`."""
    print(f"\n🧬 Bytecode de `{fn.__name__}`:")
    for ins in dis.get_instructions(fn):
        print(f"   {ins.offset:>4}  {ins.opname:<22} {ins.argrepr}")


def ver_memoria(etiqueta: str, obj: Any) -> None:
    """Muestra el tamaño superficial en bytes (`sys.getsizeof`) de un objeto."""
    print(f"📦 Memoria [{etiqueta}] ({type(obj).__name__}): {sys.getsizeof(obj):,} bytes")


# ==============================================================================
# 👇 ZONA DE EXPERIMENTACIÓN DE RENDIMIENTO E INTERNALS 👇
# ==============================================================================
def ejecutar_sandbox() -> None:
    # BEGIN_SOLUTION
    datos = list(range(200))

    def con_comprehension() -> list[int]:
        return [x * 2 for x in datos if x % 2 == 0]

    def con_bucle_append() -> list[int]:
        out: list[int] = []
        for x in datos:
            if x % 2 == 0:
                out.append(x * 2)
        return out

    comparar_rendimiento(con_comprehension, con_bucle_append, iteraciones=3_000)
    ver_memoria("list de 1000 ints", list(range(1000)))
    ver_memoria("tuple de 1000 ints", tuple(range(1000)))
    ver_bytecode(con_comprehension)
    # END_SOLUTION


if __name__ == "__main__":
    print("=" * 72)
    print("🔬 SANDBOX DE RENDIMIENTO, MEMORIA Y BYTECODE")
    print("=" * 72)
    ejecutar_sandbox()
    print("=" * 72)
