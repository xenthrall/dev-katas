from __future__ import annotations

from collections import deque
import sys
import time
from typing import Callable

"""
MÓDULO 06 — ALGORITMOS Y PATRONES: 03. PILAS, COLAS Y ESTRUCTURAS MONÓTONAS
===============================================================================
Estudio profundo y práctica deliberada sobre Pilas LIFO (`list`), `MinStack` en
O(1), Pila Monótona (Next Greater Element / Temperaturas) y Cola Monótona con
`collections.deque` (Sliding Window Maximum en O(n)).

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Pila Monótona Decreciente (Next Greater Element en O(n)):
   - La pila almacena **índices** cuyos valores aún esperan encontrar un
     elemento mayor a su derecha.
   - Al llegar `nums[i]`, mientras `stack` no esté vacía y `nums[i] > nums[stack[-1]]`:
     extraemos `prev_idx = stack.pop()` y sabemos que su próximo mayor es `nums[i]`.

2. Cola Monótona (`collections.deque`) para Máximo en Ventana Deslizante O(n):
   - Guarda índices en orden decreciente de valor:
     1. Si `dq[0] <= i - k`, expulsa `dq.popleft()` (salió de la ventana).
     2. Mientras `dq` y `nums[dq[-1]] <= nums[i]`, expulsa `dq.pop()`.
     3. Inserta `dq.append(i)`. El máximo de la ventana actual está siempre en `nums[dq[0]]`.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- Guarda **índices** en la pila/cola monótona en vez de solo valores; con el
  índice puedes tanto calcular distancias (`i - prev_idx`) como consultar el
  valor (`nums[idx]`).
"""


def is_valid_brackets(expr: str) -> bool:
    """Verifica si los paréntesis, corchetes y llaves están balanceados en O(n)."""
    # BEGIN_SOLUTION
    pairs = {")": "(", "]": "[", "}": "{"}
    openers = set(pairs.values())
    stack: list[str] = []
    for ch in expr:
        if ch in openers:
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return len(stack) == 0
    # END_SOLUTION


class MinStack:
    """Pila que soporta `push`, `pop`, `top` y `get_min` en tiempo constante O(1)."""

    def __init__(self) -> None:
        # BEGIN_SOLUTION
        self._stack: list[tuple[int, int]] = []
        # END_SOLUTION

    def push(self, val: int) -> None:
        # BEGIN_SOLUTION
        current_min = val if not self._stack else min(val, self._stack[-1][1])
        self._stack.append((val, current_min))
        # END_SOLUTION

    def pop(self) -> int:
        # BEGIN_SOLUTION
        return self._stack.pop()[0]
        # END_SOLUTION

    def top(self) -> int:
        # BEGIN_SOLUTION
        return self._stack[-1][0]
        # END_SOLUTION

    def get_min(self) -> int:
        # BEGIN_SOLUTION
        return self._stack[-1][1]
        # END_SOLUTION


def days_until_warmer_temperature(temperatures: list[int]) -> list[int]:
    """Para cada día, devuelve cuántos días faltan para una temperatura mayor (Pila Monótona O(n))."""
    # BEGIN_SOLUTION
    ans = [0] * len(temperatures)
    stack: list[int] = []  # Índices con temperaturas decrecientes
    for i, temp in enumerate(temperatures):
        while stack and temp > temperatures[stack[-1]]:
            prev_idx = stack.pop()
            ans[prev_idx] = i - prev_idx
        stack.append(i)
    return ans
    # END_SOLUTION


def sliding_window_maximum(nums: list[int], k: int) -> list[int]:
    """Devuelve el máximo de cada ventana deslizante de tamaño `k` en O(n) usando `deque` monótona."""
    # BEGIN_SOLUTION
    if not nums or k <= 0:
        return []
    dq: deque[int] = deque()
    result: list[int] = []
    for i, val in enumerate(nums):
        if dq and dq[0] <= i - k:
            dq.popleft()
        while dq and nums[dq[-1]] <= val:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
    # END_SOLUTION


def largest_rectangle_in_histogram(heights: list[int]) -> int:
    """Calcula el área del mayor rectángulo en un histograma en O(n) con pila monótona creciente."""
    # BEGIN_SOLUTION
    stack: list[int] = []
    max_area = 0
    extended = heights + [0]
    for i, h in enumerate(extended):
        while stack and extended[stack[-1]] > h:
            height = extended[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)
    return max_area
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_is_valid_brackets() -> None:
    assert is_valid_brackets("{[()()]}") is True
    assert is_valid_brackets("([)]") is False
    assert is_valid_brackets("((") is False


def check_min_stack() -> None:
    ms = MinStack()
    ms.push(-2)
    ms.push(0)
    ms.push(-3)
    assert ms.get_min() == -3
    ms.pop()
    assert ms.top() == 0
    assert ms.get_min() == -2


def check_days_until_warmer_temperature() -> None:
    temps = [73, 74, 75, 71, 69, 72, 76, 73]
    assert days_until_warmer_temperature(temps) == [1, 1, 4, 2, 1, 1, 0, 0]


def check_sliding_window_maximum() -> None:
    assert sliding_window_maximum([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]


def check_largest_rectangle_in_histogram() -> None:
    assert largest_rectangle_in_histogram([2, 1, 5, 6, 2, 3]) == 10


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. is_valid_brackets", check_is_valid_brackets),
    ("02. MinStack", check_min_stack),
    ("03. days_until_warmer_temperature", check_days_until_warmer_temperature),
    ("04. sliding_window_maximum", check_sliding_window_maximum),
    ("05. largest_rectangle_in_histogram", check_largest_rectangle_in_histogram),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 03_stacks_queues_and_monotonic.py")
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
