from __future__ import annotations

from collections import Counter
import pickle
import sys
import time
from typing import Any, Callable

"""
MÓDULO 05 — CONCURRENCIA Y ASYNC: 04. MULTIPROCESSING Y CARGAS CPU-BOUND
===============================================================================
Estudio profundo y práctica deliberada sobre cómputo paralelo para tareas
intensivas de CPU (evitando el cuello de botella del GIL), particionado
equilibrado de lotes (*chunking*), reglas de serialización con `pickle` y
arquitectura Map-Reduce paralela.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. ¿Por qué `multiprocessing` para tareas CPU-Bound?
   - Cada proceso en `ProcessPoolExecutor` tiene su propio espacio de memoria y
     su propio GIL, ejecutándose en paralelo real en múltiples núcleos físicos.
   - Sin embargo, enviar datos entre procesos requiere **serializarlos (`pickle`)**
     a través de tuberías IPC. Por eso conviene enviar **lotes (chunks)** en vez
     de millones de elementos sueltos.

2. Reglas de `pickle` (Qué se puede enviar entre procesos):
   - ✅ Funciones definidas en el nivel superior del módulo (`top-level def`),
     clases top-level, tipos nativos (`int`, `str`, `list`, `dict`, `tuple`).
   - ❌ Lambdas (`lambda x: ...`), funciones anidadas/closures locales, sockets
     o generadores abiertos NO son serializables por `pickle` estándar.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- En Windows (`spawn`), el módulo hijo se importa desde cero al crear procesos;
  nunca lances procesos fuera del bloque `if __name__ == "__main__":`.
"""


def partition_into_balanced_chunks(items: list[Any], num_chunks: int) -> list[list[Any]]:
    """Divide `items` en hasta `num_chunks` lotes contiguos de tamaño equilibrado.

    Si `num_chunks <= 0`, lanza `ValueError`. Si `items` está vacío, devuelve `[]`.
    No debe devolver sublistas vacías.

    Ejemplo:
        >>> partition_into_balanced_chunks([1, 2, 3, 4, 5, 6, 7], 3)
        [[1, 2, 3], [4, 5], [6, 7]]
    """
    # BEGIN_SOLUTION
    if num_chunks <= 0:
        raise ValueError("num_chunks debe ser positivo")
    if not items:
        return []
    n = len(items)
    k = min(n, num_chunks)
    base_size, remainder = divmod(n, k)
    chunks: list[list[Any]] = []
    start = 0
    for i in range(k):
        end = start + base_size + (1 if i < remainder else 0)
        chunks.append(items[start:end])
        start = end
    return chunks
    # END_SOLUTION


def is_ipc_picklable(obj: Any) -> bool:
    """Verifica si un objeto o función puede serializarse con `pickle.dumps` para IPC."""
    # BEGIN_SOLUTION
    try:
        pickle.dumps(obj)
        return True
    except Exception:
        return False
    # END_SOLUTION


def _cpu_sum_of_squares_chunk(chunk: list[int]) -> int:
    """Función top-level (picklable) para el paso Map de suma de cuadrados."""
    return sum(x * x for x in chunk)


def map_reduce_sum_of_squares(numbers: list[int], num_workers: int = 4) -> int:
    """Ejecuta un pipeline Map-Reduce dividiendo `numbers` en lotes y reduciendo las sumas."""
    # BEGIN_SOLUTION
    if not numbers:
        return 0
    chunks = partition_into_balanced_chunks(numbers, num_workers)
    partial_sums = [_cpu_sum_of_squares_chunk(c) for c in chunks]
    return sum(partial_sums)
    # END_SOLUTION


def map_reduce_word_frequencies(documents: list[str]) -> dict[str, int]:
    """Implementa Map-Reduce para contar frecuencias de palabras a través de documentos."""
    # BEGIN_SOLUTION
    total_counts: Counter[str] = Counter()
    for doc in documents:
        words = [w.strip(".,!?;:").lower() for w in doc.split()]
        total_counts.update(w for w in words if w)
    return dict(total_counts)
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_partition_into_balanced_chunks() -> None:
    assert partition_into_balanced_chunks([1, 2, 3, 4, 5, 6, 7], 3) == [
        [1, 2, 3],
        [4, 5],
        [6, 7],
    ]
    assert partition_into_balanced_chunks([1, 2], 5) == [[1], [2]]
    assert partition_into_balanced_chunks([], 3) == []


def check_is_ipc_picklable() -> None:
    assert is_ipc_picklable({"a": [1, 2, 3]}) is True
    assert is_ipc_picklable(_cpu_sum_of_squares_chunk) is True
    assert is_ipc_picklable(lambda x: x + 1) is False


def check_map_reduce_sum_of_squares() -> None:
    nums = list(range(1, 101))
    assert map_reduce_sum_of_squares(nums, num_workers=4) == sum(x * x for x in nums)


def check_map_reduce_word_frequencies() -> None:
    docs = ["Python rápido, Python limpio!", "Código limpio y rápido."]
    assert map_reduce_word_frequencies(docs) == {
        "python": 2,
        "rápido": 2,
        "limpio": 2,
        "código": 1,
        "y": 1,
    }


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. partition_into_balanced_chunks", check_partition_into_balanced_chunks),
    ("02. is_ipc_picklable (pickle validation)", check_is_ipc_picklable),
    ("03. map_reduce_sum_of_squares", check_map_reduce_sum_of_squares),
    ("04. map_reduce_word_frequencies", check_map_reduce_word_frequencies),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 04_multiprocessing_and_cpu_bound.py")
    print("=" * 72)
    passed = 0
    failed = 0
    pending = 0

    for name, check_fn in CHECKS:
        start = time.perf_counter()
        try:
            check_fn()
            elapsed_ms = (time.perf_counter() - start) * 1000
            print(f"✅ [PASS]      {name:<35} ({elapsed_ms:.2f} ms)")
            passed += 1
        except NotImplementedError:
            print(f"⏳ [PENDIENTE] {name}")
            pending += 1
        except Exception as exc:
            print(f"❌ [FAIL]      {name}: {type(exc).__name__}: {exc}")
            failed += 1

    print("-" * 72)
    print(f"Resumen: {passed} pasadas | {pending} pendientes | {failed} fallidas")
    print("=" * 72)
    if failed > 0 or pending > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_verification()
