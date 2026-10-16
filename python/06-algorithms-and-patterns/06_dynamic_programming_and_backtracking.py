from __future__ import annotations

import sys
import time
from typing import Callable

"""
MÓDULO 06 — ALGORITMOS Y PATRONES: 06. PROGRAMACIÓN DINÁMICA Y BACKTRACKING
===============================================================================
Estudio profundo y práctica deliberada sobre Programación Dinámica 1D/2D con
optimización de espacio y exploración exhaustiva con poda mediante Backtracking
(`elegir -> explorar -> deshacer`).

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Programación Dinámica (DP):
   - **1D con Espacio O(1):** Cuando `dp[i]` solo depende de `dp[i-1]` y `dp[i-2]`,
     basta mantener dos variables escalares `prev2, prev1 = prev1, nuevo`.
   - **Cambio de Monedas (`coin_change_min`):**
     `dp = [0] + [amount + 1] * amount`. Para cada monto `a` y moneda `c <= a`:
     `dp[a] = min(dp[a], dp[a - c] + 1)`.
   - **Subsecuencia Común Más Larga (LCS 2D):**
     Si `s1[i] == s2[j]` -> `1 + dp[i+1][j+1]`, sino `max(dp[i+1][j], dp[i][j+1])`.

2. Plantilla de Backtracking:
   ```python
   def backtrack(start_idx: int, path: list[int], remaining: int) -> None:
       if remaining == 0:
           results.append(path.copy())  # ¡Siempre haz .copy() de la ruta actual!
           return
       for i in range(start_idx, len(candidates)):
           path.append(candidates[i])
           backtrack(i, path, remaining - candidates[i])
           path.pop()                   # Deshacer la decisión
   ```

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- ❌ Trampa de Backtracking: Hacer `results.append(path)` sin `.copy()` guarda
  múltiples referencias a la MISMA lista que al final del backtracking termina
  vacía `[]`.
"""


def house_robber_max_loot(houses: list[int]) -> int:
    """Calcula el máximo botín sin robar dos casas adyacentes en O(n) tiempo y O(1) espacio."""
    # BEGIN_SOLUTION
    prev2, prev1 = 0, 0
    for val in houses:
        prev2, prev1 = prev1, max(prev1, prev2 + val)
    return prev1
    # END_SOLUTION


def coin_change_min_coins(coins: list[int], amount: int) -> int:
    """Devuelve el mínimo número de monedas para sumar `amount`, o `-1` si es imposible."""
    # BEGIN_SOLUTION
    if amount < 0:
        return -1
    inf = amount + 1
    dp = [0] + [inf] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] <= amount else -1
    # END_SOLUTION


def longest_common_subsequence(text1: str, text2: str) -> int:
    """Calcula la longitud de la Subsecuencia Común Más Larga (LCS) entre `text1` y `text2`."""
    # BEGIN_SOLUTION
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            if text1[i] == text2[j]:
                dp[i][j] = 1 + dp[i + 1][j + 1]
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])
    return dp[0][0]
    # END_SOLUTION


def generate_power_set(nums: list[int]) -> list[list[int]]:
    """Genera todos los subconjuntos posibles de `nums` mediante Backtracking."""
    # BEGIN_SOLUTION
    results: list[list[int]] = []
    path: list[int] = []

    def _backtrack(idx: int) -> None:
        if idx == len(nums):
            results.append(path.copy())
            return
        _backtrack(idx + 1)
        path.append(nums[idx])
        _backtrack(idx + 1)
        path.pop()

    _backtrack(0)
    return sorted(results)
    # END_SOLUTION


def combination_sum_target(candidates: list[int], target: int) -> list[list[int]]:
    """Encuentra todas las combinaciones con repetición de `candidates` que suman `target`."""
    # BEGIN_SOLUTION
    arr = sorted(set(candidates))
    results: list[list[int]] = []
    path: list[int] = []

    def _dfs(start: int, remaining: int) -> None:
        if remaining == 0:
            results.append(path.copy())
            return
        for i in range(start, len(arr)):
            val = arr[i]
            if val > remaining:
                break
            path.append(val)
            _dfs(i, remaining - val)
            path.pop()

    _dfs(0, target)
    return results
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_house_robber_max_loot() -> None:
    assert house_robber_max_loot([2, 7, 9, 3, 1]) == 12
    assert house_robber_max_loot([]) == 0


def check_coin_change_min_coins() -> None:
    assert coin_change_min_coins([1, 2, 5], 11) == 3
    assert coin_change_min_coins([2], 3) == -1


def check_longest_common_subsequence() -> None:
    assert longest_common_subsequence("abcde", "ace") == 3
    assert longest_common_subsequence("abc", "def") == 0


def check_generate_power_set() -> None:
    res = generate_power_set([1, 2])
    assert sorted(res) == sorted([[], [1], [2], [1, 2]])


def check_combination_sum_target() -> None:
    assert combination_sum_target([2, 3, 6, 7], 7) == [[2, 2, 3], [7]]


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. house_robber_max_loot (1D O(1) Space)", check_house_robber_max_loot),
    ("02. coin_change_min_coins (1D DP)", check_coin_change_min_coins),
    ("03. longest_common_subsequence (2D DP)", check_longest_common_subsequence),
    ("04. generate_power_set (Backtracking)", check_generate_power_set),
    ("05. combination_sum_target (Pruning)", check_combination_sum_target),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 06_dynamic_programming_and_backtracking.py")
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
