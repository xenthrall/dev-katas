from __future__ import annotations

import bisect
import heapq
import sys
import time
from typing import Any, Callable

"""
MÓDULO 02 — MANIPULACIÓN DE DATOS Y STDLIB: 03. SORTING, BISECT Y HEAPQ
===============================================================================
Estudio profundo y práctica deliberada sobre el algoritmo Timsort de Python
(`sorted`), búsqueda binaria en arreglos ordenados (`bisect`) y colas de
prioridad / montículos binarios (`heapq`).

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Ordenamiento Estable Multi-Criterio (`sorted` — Timsort O(n log n)):
   - Usa una tupla como clave de ordenamiento `key=lambda x: (...)`.
   - Para ordenar números en orden **descendente** y texto en orden **ascendente**
     simultáneamente: `sorted(items, key=lambda x: (-x["score"], x["name"]))`.

2. Búsqueda Binaria con `bisect` (O(log n) sobre secuencias ordenadas):
   - `bisect.bisect_left(a, x)`: Primer índice donde insertar `x` para mantener
     el orden (a la izquierda de elementos iguales a `x`).
   - `bisect.bisect_right(a, x)`: Índice de inserción a la derecha de elementos
     iguales a `x`.
   - Contar cuántos elementos están en el rango cerrado `[low, high]` en O(log n):
     `bisect_right(arr, high) - bisect_left(arr, low)`

3. Colas de Prioridad con `heapq` (Min-Heap sobre una `list` estándar):
   - `heapq.heapify(lista)`: Transforma una lista en un min-heap in-place en **O(n)**.
   - `heapq.heappush(heap, item)` / `heapq.heappop(heap)`: O(log n).
   - `heap[0]`: Consulta el elemento mínimo en O(1) sin extraerlo.
   - **Max-Heap en Python:** Invierte el signo numérico (`-valor`) al insertar y extraer.
   - `heapq.nlargest(k, iterable, key=...)` / `nsmallest(...)`: O(n log k).
   - `heapq.merge(*sorted_iterables)`: Fusiona perezosamente múltiples flujos ya
     ordenados en O(N log M).

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- Si guardas tuplas `(prioridad, objeto)` en un `heapq` y dos elementos empatan
  en `prioridad`, Python intentará comparar `objeto_1 < objeto_2`. Si `objeto` es
  un `dict` o una clase sin `__lt__`, lanzará `TypeError`. Solución: usa una
  3-tupla `(prioridad, contador_desempate, objeto)`.
"""


def rank_candidates(candidates: list[dict[str, Any]]) -> list[str]:
    """Ordena candidatos multi-criterio y devuelve la lista de sus nombres.

    Criterios de prioridad en orden:
    1. Mayor puntaje técnico (`"tech_score"`, descendente).
    2. Menor tiempo de entrega en minutos (`"minutes"`, ascendente).
    3. Nombre en orden alfabético ignorando mayúsculas (`"name".lower()`, ascendente).

    Ejemplo:
        >>> cands = [
        ...     {"name": "Luis", "tech_score": 90, "minutes": 45},
        ...     {"name": "Ana", "tech_score": 90, "minutes": 30},
        ...     {"name": "Beto", "tech_score": 95, "minutes": 50},
        ... ]
        >>> rank_candidates(cands)
        ['Beto', 'Ana', 'Luis']

    Complejidad objetivo:
        Tiempo: O(n log n) | Espacio: O(n)

    Pista:
        Usa `sorted(candidates, key=lambda c: (-c["tech_score"], c["minutes"], c["name"].lower()))`.
    """
    # BEGIN_SOLUTION
    ordered = sorted(
        candidates,
        key=lambda c: (-int(c["tech_score"]), int(c["minutes"]), str(c["name"]).lower()),
    )
    return [str(c["name"]) for c in ordered]
    # END_SOLUTION


def count_in_closed_range(sorted_nums: list[int], low: int, high: int) -> int:
    """Cuenta cuántos elementos de `sorted_nums` cumplen `low <= x <= high` en O(log n).

    Si `low > high`, devuelve `0`.

    Ejemplo:
        >>> count_in_closed_range([1, 2, 4, 4, 4, 7, 9], 4, 7)
        4

    Complejidad objetivo:
        Tiempo: O(log n) | Espacio: O(1)

    Pista:
        Resta `bisect.bisect_right(sorted_nums, high) - bisect.bisect_left(sorted_nums, low)`.
    """
    # BEGIN_SOLUTION
    if low > high:
        return 0
    return bisect.bisect_right(sorted_nums, high) - bisect.bisect_left(sorted_nums, low)
    # END_SOLUTION


def assign_latency_tier(
    latency_ms: float,
    thresholds: list[float],
    tiers: list[str],
) -> str:
    """Clasifica una latencia en su categoría usando `bisect.bisect_right`.

    Por ejemplo, si `thresholds = [50.0, 150.0, 500.0]` y
    `tiers = ["FAST", "NORMAL", "SLOW", "CRITICAL"]`:
    - `< 50.0` -> `"FAST"`
    - `50.0 <= x < 150.0` -> `"NORMAL"`
    - `150.0 <= x < 500.0` -> `"SLOW"`
    - `>= 500.0` -> `"CRITICAL"`

    Ejemplo:
        >>> assign_latency_tier(150.0, [50.0, 150.0, 500.0], ["FAST", "NORMAL", "SLOW", "CRITICAL"])
        'SLOW'

    Complejidad objetivo:
        Tiempo: O(log k) | Espacio: O(1)

    Pista:
        El índice en `tiers` es directamente `bisect.bisect_right(thresholds, latency_ms)`.
    """
    # BEGIN_SOLUTION
    idx = bisect.bisect_right(thresholds, latency_ms)
    return tiers[idx]
    # END_SOLUTION


def kth_largest_stream_element(nums: list[int], k: int) -> int:
    """Encuentra el k-ésimo elemento más grande manteniendo un Min-Heap de tamaño `k`.

    Si `k <= 0` o `k > len(nums)`, lanza `ValueError`.

    Ejemplo:
        >>> kth_largest_stream_element([3, 2, 1, 5, 6, 4], k=2)
        5

    Complejidad objetivo:
        Tiempo: O(n log k) | Espacio: O(k)

    Pista:
        Mantén un min-heap con los primeros `k` elementos; para cada nuevo elemento
        mayor que `heap[0]`, usa `heapq.heapreplace(heap, x)`. Al final devuelve `heap[0]`.
    """
    # BEGIN_SOLUTION
    if k <= 0 or k > len(nums):
        raise ValueError("k fuera de rango válido")
    min_heap = nums[:k]
    heapq.heapify(min_heap)
    for num in nums[k:]:
        if num > min_heap[0]:
            heapq.heapreplace(min_heap, num)
    return min_heap[0]
    # END_SOLUTION


def merge_k_sorted_logs(
    log_streams: list[list[tuple[int, str]]],
) -> list[tuple[int, str]]:
    """Fusiona `k` listas de logs ya ordenadas por timestamp `(ts, msg)` usando `heapq.merge`.

    Ejemplo:
        >>> s1 = [(1, "boot"), (4, "ready")]
        >>> s2 = [(2, "auth"), (3, "db")]
        >>> merge_k_sorted_logs([s1, s2])
        [(1, 'boot'), (2, 'auth'), (3, 'db'), (4, 'ready')]

    Complejidad objetivo:
        Tiempo: O(N log k) | Espacio: O(N)

    Pista:
        Pasa todas las secuencias desempaquetadas a `heapq.merge(*log_streams, key=lambda x: x[0])`.
    """
    # BEGIN_SOLUTION
    return list(heapq.merge(*log_streams, key=lambda item: item[0]))
    # END_SOLUTION


class RunningMedianTracker:
    """Calculador de mediana en tiempo real usando dos heaps (Max-Heap inferior y Min-Heap superior)."""

    def __init__(self) -> None:
        # BEGIN_SOLUTION
        self._low_max_heap: list[int] = []  # Guarda valores negados (-x)
        self._high_min_heap: list[int] = []
        # END_SOLUTION

    def add_number(self, num: int) -> None:
        """Inserta `num` en O(log n) manteniendo los dos heaps balanceados."""
        # BEGIN_SOLUTION
        heapq.heappush(self._low_max_heap, -num)
        largest_low = -heapq.heappop(self._low_max_heap)
        heapq.heappush(self._high_min_heap, largest_low)

        if len(self._high_min_heap) > len(self._low_max_heap):
            smallest_high = heapq.heappop(self._high_min_heap)
            heapq.heappush(self._low_max_heap, -smallest_high)
        # END_SOLUTION

    def get_median(self) -> float:
        """Devuelve la mediana actual en O(1). Lanza `ValueError` si no hay datos."""
        # BEGIN_SOLUTION
        if not self._low_max_heap:
            raise ValueError("No se han insertado números.")
        if len(self._low_max_heap) > len(self._high_min_heap):
            return float(-self._low_max_heap[0])
        return (-self._low_max_heap[0] + self._high_min_heap[0]) / 2.0
        # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_rank_candidates() -> None:
    cands = [
        {"name": "Luis", "tech_score": 90, "minutes": 45},
        {"name": "ana", "tech_score": 90, "minutes": 30},
        {"name": "Beto", "tech_score": 95, "minutes": 50},
        {"name": "Carlos", "tech_score": 90, "minutes": 30},
    ]
    assert rank_candidates(cands) == ["Beto", "ana", "Carlos", "Luis"]


def check_count_in_closed_range() -> None:
    arr = [1, 2, 4, 4, 4, 7, 9, 12]
    assert count_in_closed_range(arr, 4, 7) == 4
    assert count_in_closed_range(arr, 5, 6) == 0
    assert count_in_closed_range(arr, 10, 2) == 0


def check_assign_latency_tier() -> None:
    thresholds = [50.0, 150.0, 500.0]
    tiers = ["FAST", "NORMAL", "SLOW", "CRITICAL"]
    assert assign_latency_tier(10.0, thresholds, tiers) == "FAST"
    assert assign_latency_tier(50.0, thresholds, tiers) == "NORMAL"
    assert assign_latency_tier(150.0, thresholds, tiers) == "SLOW"
    assert assign_latency_tier(800.0, thresholds, tiers) == "CRITICAL"


def check_kth_largest_stream_element() -> None:
    assert kth_largest_stream_element([3, 2, 1, 5, 6, 4], 2) == 5
    assert kth_largest_stream_element([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4


def check_merge_k_sorted_logs() -> None:
    s1 = [(1, "boot"), (4, "ready")]
    s2 = [(2, "auth"), (3, "db")]
    assert merge_k_sorted_logs([s1, s2]) == [
        (1, "boot"),
        (2, "auth"),
        (3, "db"),
        (4, "ready"),
    ]


def check_running_median_tracker() -> None:
    tracker = RunningMedianTracker()
    tracker.add_number(10)
    assert tracker.get_median() == 10.0
    tracker.add_number(20)
    assert tracker.get_median() == 15.0
    tracker.add_number(12)
    assert tracker.get_median() == 12.0


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. rank_candidates", check_rank_candidates),
    ("02. count_in_closed_range", check_count_in_closed_range),
    ("03. assign_latency_tier", check_assign_latency_tier),
    ("04. kth_largest_stream_element", check_kth_largest_stream_element),
    ("05. merge_k_sorted_logs", check_merge_k_sorted_logs),
    ("06. RunningMedianTracker", check_running_median_tracker),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 03_sorting_bisect_and_heapq.py")
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
