from __future__ import annotations

import sys
import time
from typing import Callable

"""
MÓDULO 06 — ALGORITMOS Y PATRONES: 04. VARIACIONES DE BÚSQUEDA BINARIA
===============================================================================
Estudio profundo y práctica deliberada sobre búsqueda binaria de bordes
izquierdo/derecho, arreglos ordenados rotados y **Búsqueda Binaria en el
Espacio de Respuestas** (problemas de optimización Min-Max / Max-Min).

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Plantilla Universal de Búsqueda Binaria en Espacio de Respuestas:
   Cuando una propiedad `es_factible(capacidad)` es **monótona** (si se puede
   con `C`, también se puede con `C + 1`), podemos hacer búsqueda binaria sobre
   el rango `[min_posible, max_posible]`:
   ```python
   low, high = min_posible, max_posible
   while low < high:
       mid = (low + high) // 2
       if es_factible(mid):
           high = mid      # Buscamos el mínimo valor factible
       else:
           low = mid + 1
   return low
   ```

2. Arreglo Ordenado Rotado (`[4, 5, 6, 7, 0, 1, 2]`):
   - Al partir en `mid`, **al menos una de las dos mitades (`[low..mid]` o
     `[mid..high]`) está garantizada de estar estrictamente ordenada**.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- Cuando busques el **máximo** valor factible (`low = mid`), calcula la mitad
  redondeando hacia arriba `mid = (low + high + 1) // 2` para evitar un bucle
  infinito cuando `high == low + 1`.
"""


def find_first_and_last_position(nums: list[int], target: int) -> tuple[int, int]:
    """Encuentra el primer y último índice de `target` en `nums` ordenado en O(log n).

    Si `target` no existe, devuelve `(-1, -1)`.
    """
    # BEGIN_SOLUTION
    def _find_bound(is_first: bool) -> int:
        low, high = 0, len(nums) - 1
        bound = -1
        while low <= high:
            mid = (low + high) // 2
            if nums[mid] == target:
                bound = mid
                if is_first:
                    high = mid - 1
                else:
                    low = mid + 1
            elif nums[mid] < target:
                low = mid + 1
            else:
                high = mid - 1
        return bound

    first = _find_bound(True)
    if first == -1:
        return (-1, -1)
    return (first, _find_bound(False))
    # END_SOLUTION


def search_in_rotated_sorted_array(nums: list[int], target: int) -> int:
    """Busca `target` en un arreglo ordenado rotado sin duplicados en O(log n).

    Devuelve su índice o `-1` si no se encuentra.
    """
    # BEGIN_SOLUTION
    low, high = 0, len(nums) - 1
    while low <= high:
        mid = (low + high) // 2
        if nums[mid] == target:
            return mid
        if nums[low] <= nums[mid]:
            if nums[low] <= target < nums[mid]:
                high = mid - 1
            else:
                low = mid + 1
        else:
            if nums[mid] < target <= nums[high]:
                low = mid + 1
            else:
                high = mid - 1
    return -1
    # END_SOLUTION


def min_ship_capacity_within_days(weights: list[int], days: int) -> int:
    """Calcula la capacidad mínima diaria de un barco para enviar `weights` en orden en `days` días.

    Búsqueda binaria en `[max(weights), sum(weights)]`.
    """
    # BEGIN_SOLUTION
    low, high = max(weights), sum(weights)

    def _can_ship(capacity: int) -> bool:
        used_days = 1
        current_load = 0
        for w in weights:
            if current_load + w > capacity:
                used_days += 1
                current_load = w
            else:
                current_load += w
        return used_days <= days

    while low < high:
        mid = (low + high) // 2
        if _can_ship(mid):
            high = mid
        else:
            low = mid + 1
    return low
    # END_SOLUTION


def max_min_magnetic_distance(positions: list[int], m: int) -> int:
    """Coloca `m` elementos en `positions` maximizando la distancia mínima entre cualesquiera dos."""
    # BEGIN_SOLUTION
    arr = sorted(positions)
    low, high = 1, arr[-1] - arr[0]

    def _can_place(min_dist: int) -> bool:
        count = 1
        last_pos = arr[0]
        for pos in arr[1:]:
            if pos - last_pos >= min_dist:
                count += 1
                last_pos = pos
                if count >= m:
                    return True
        return False

    while low < high:
        mid = (low + high + 1) // 2
        if _can_place(mid):
            low = mid
        else:
            high = mid - 1
    return low
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_find_first_and_last_position() -> None:
    assert find_first_and_last_position([5, 7, 7, 8, 8, 10], 8) == (3, 4)
    assert find_first_and_last_position([5, 7, 7, 8, 8, 10], 6) == (-1, -1)


def check_search_in_rotated_sorted_array() -> None:
    assert search_in_rotated_sorted_array([4, 5, 6, 7, 0, 1, 2], 0) == 4
    assert search_in_rotated_sorted_array([4, 5, 6, 7, 0, 1, 2], 3) == -1


def check_min_ship_capacity_within_days() -> None:
    assert min_ship_capacity_within_days([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5) == 15
    assert min_ship_capacity_within_days([3, 2, 2, 4, 1, 4], 3) == 6


def check_max_min_magnetic_distance() -> None:
    assert max_min_magnetic_distance([1, 2, 3, 4, 7], 3) == 3


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. find_first_and_last_position", check_find_first_and_last_position),
    ("02. search_in_rotated_sorted_array", check_search_in_rotated_sorted_array),
    ("03. min_ship_capacity_within_days", check_min_ship_capacity_within_days),
    ("04. max_min_magnetic_distance", check_max_min_magnetic_distance),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 04_binary_search_variations.py")
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
