from __future__ import annotations

from collections import OrderedDict, defaultdict
import sys
import time
from typing import Callable

"""
MÓDULO 06 — ALGORITMOS Y PATRONES: 02. HASHING, PREFIX SUMS Y LRU CACHE
===============================================================================
Estudio profundo y práctica deliberada sobre reducción de complejidad temporal
de O(n²) a O(n) mediante tablas hash, sumas prefijas acumuladas (`prefix_sum - k`),
secuencias consecutivas en conjuntos y caché LRU en O(1) con `OrderedDict`.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Sumas Prefijas + Hash Map (`subarray_sum_equals_k` en O(n)):
   - La suma del subarreglo `nums[i..j]` es `prefix[j] - prefix[i - 1]`.
   - Para que esa suma valga `k`, buscamos cuántas veces apareció antes
     un prefijo igual a `current_sum - k`.
   - Inicializa siempre el mapa de frecuencias con `{0: 1}` para cubrir
     subarreglos que empiezan desde el índice `0`.

2. `LRUCache` en O(1) con `collections.OrderedDict`:
   - `od.move_to_end(key)`: Marca `key` como recientemente usada en O(1).
   - `od.popitem(last=False)`: Expulsa la entrada menos recientemente usada
     (la primera en orden FIFO) en O(1).

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- En `longest_consecutive_sequence`, para lograr O(n) real, SOLO debes iniciar
  el conteo `while curr + 1 in num_set` cuando `num - 1 not in num_set` (es decir,
  cuando `num` es el inicio real de una racha).
"""


def subarray_sum_equals_k(nums: list[int], k: int) -> int:
    """Cuenta cuántos subarreglos contiguos suman exactamente `k` en tiempo O(n)."""
    # BEGIN_SOLUTION
    prefix_counts: dict[int, int] = {0: 1}
    current_sum = 0
    total_subarrays = 0
    for x in nums:
        current_sum += x
        total_subarrays += prefix_counts.get(current_sum - k, 0)
        prefix_counts[current_sum] = prefix_counts.get(current_sum, 0) + 1
    return total_subarrays
    # END_SOLUTION


def longest_consecutive_sequence(nums: list[int]) -> int:
    """Encuentra la longitud de la secuencia de enteros consecutivos más larga en O(n)."""
    # BEGIN_SOLUTION
    num_set = set(nums)
    best = 0
    for x in num_set:
        if (x - 1) not in num_set:
            length = 1
            while (x + length) in num_set:
                length += 1
            best = max(best, length)
    return best
    # END_SOLUTION


class RangeSumQuery:
    """Estructura de sumas prefijas para responder `sum_range(left, right)` en O(1)."""

    def __init__(self, nums: list[int]) -> None:
        # BEGIN_SOLUTION
        self._prefix = [0] * (len(nums) + 1)
        for i, val in enumerate(nums):
            self._prefix[i + 1] = self._prefix[i] + val
        # END_SOLUTION

    def sum_range(self, left: int, right: int) -> int:
        # BEGIN_SOLUTION
        return self._prefix[right + 1] - self._prefix[left]
        # END_SOLUTION


def group_anagrams(words: list[str]) -> list[list[str]]:
    """Agrupa anagramas usando la tupla ordenada de caracteres como clave hashable."""
    # BEGIN_SOLUTION
    groups: defaultdict[tuple[str, ...], list[str]] = defaultdict(list)
    for w in words:
        key = tuple(sorted(w))
        groups[key].append(w)
    return list(groups.values())
    # END_SOLUTION


class LRUCache:
    """Caché Least Recently Used en O(1) respaldado por `OrderedDict`."""

    def __init__(self, capacity: int) -> None:
        # BEGIN_SOLUTION
        if capacity <= 0:
            raise ValueError("capacity debe ser mayor a 0")
        self.capacity = capacity
        self._store: OrderedDict[int, int] = OrderedDict()
        # END_SOLUTION

    def get(self, key: int) -> int:
        # BEGIN_SOLUTION
        if key not in self._store:
            return -1
        self._store.move_to_end(key)
        return self._store[key]
        # END_SOLUTION

    def put(self, key: int, value: int) -> None:
        # BEGIN_SOLUTION
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = value
        if len(self._store) > self.capacity:
            self._store.popitem(last=False)
        # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_subarray_sum_equals_k() -> None:
    assert subarray_sum_equals_k([1, 1, 1], 2) == 2
    assert subarray_sum_equals_k([1, 2, 3, -1, 1], 3) == 3


def check_longest_consecutive_sequence() -> None:
    assert longest_consecutive_sequence([100, 4, 200, 1, 3, 2]) == 4
    assert longest_consecutive_sequence([]) == 0


def check_range_sum_query() -> None:
    rsq = RangeSumQuery([-2, 0, 3, -5, 2, -1])
    assert rsq.sum_range(0, 2) == 1
    assert rsq.sum_range(2, 5) == -1


def check_group_anagrams() -> None:
    res = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    normalized = sorted(sorted(g) for g in res)
    assert normalized == [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]


def check_lru_cache() -> None:
    cache = LRUCache(2)
    cache.put(1, 10)
    cache.put(2, 20)
    assert cache.get(1) == 10
    cache.put(3, 30)  # Expulsa la clave 2
    assert cache.get(2) == -1
    assert cache.get(3) == 30


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. subarray_sum_equals_k", check_subarray_sum_equals_k),
    ("02. longest_consecutive_sequence", check_longest_consecutive_sequence),
    ("03. RangeSumQuery", check_range_sum_query),
    ("04. group_anagrams", check_group_anagrams),
    ("05. LRUCache (OrderedDict)", check_lru_cache),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 02_hashing_and_prefix_sums.py")
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
