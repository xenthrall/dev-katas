from __future__ import annotations

import time
from typing import Callable

"""
================================================================================
MÓDULO 06: ALGORITMOS Y PATRONES — 01: TWO POINTERS Y SLIDING WINDOW
================================================================================

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
--------------------------------------------------------------------------------
1. Dos Punteros Opuestos (Opposite-Ends Two Pointers) — O(n) tiempo, O(1) espacio:
   Ideal para arreglos ordenados (búsqueda de pares) o problemas geométricos de
   extremos (como contenedores de agua o verificación de palíndromos).

   ```python
   left, right = 0, len(nums) - 1
   while left < right:
       current = nums[left] + nums[right]
       if current == target:
           return (left, right)
       elif current < target:
           left += 1   # Necesitamos una suma mayor
       else:
           right -= 1  # Necesitamos una suma menor
   ```

2. Dos Punteros Rápido/Lento (Fast/Slow Pointers) — Compactación In-Place:
   `fast` explora todos los elementos; `slow` marca la frontera de elementos válidos.

   ```python
   slow = 0
   for fast in range(len(nums)):
       if es_valido(nums[fast]):
           nums[slow] = nums[fast]
           slow += 1
   ```

3. Ventana Deslizante Fija (Fixed Sliding Window) — Tamaño constante `k`:
   En lugar de recalcular `sum(nums[i:i+k])` en O(k), sumamos el nuevo elemento
   que entra por la derecha y restamos el que sale por la izquierda en O(1).

   ```python
   window_sum = sum(nums[:k])
   max_sum = window_sum
   for right in range(k, len(nums)):
       window_sum += nums[right] - nums[right - k]
       max_sum = max(max_sum, window_sum)
   ```

4. Ventana Deslizante Dinámica (Dynamic Sliding Window) — O(n) amortizado:
   El puntero `right` expande la ventana en cada paso; el bucle interno `while`
   contrae `left` solo cuando la condición de validez se rompe (o mientras ya se
   cumple un mínimo buscado).

   ```python
   left = 0
   for right, val in enumerate(arr):
       agregar_a_ventana(val)
       while ventana_invalida():
           quitar_de_ventana(arr[left])
           left += 1
       actualizar_mejor_respuesta(right - left + 1)
   ```

🧠 MODELO MENTAL Y TRAMPAS COMUNES
--------------------------------------------------------------------------------
- ¿Por qué un `for` con un `while` anidado sigue siendo O(n) y no O(n²)?
  Porque tanto `right` como `left` SOLO avanzan hacia adelante (`+= 1`). Cada
  elemento entra a la ventana como máximo una vez y sale como máximo una vez:
  máximo 2n operaciones en total.
- Trampa en 3Sum (`three_sum_zero`): Al buscar tripletas únicas sin usar `set`
  de tuplas como muleta principal, recuerda saltar duplicados tanto en el índice
  fijo `i` (`if i > 0 and nums[i] == nums[i - 1]: continue`) como después de
  encontrar una tripleta válida en `left` y `right`.
- Trampa en `longest_substring_without_repeating`: Si guardas `last_seen[ch] = idx`,
  cuando encuentras un carácter repetido debes verificar que su última aparición
  esté DENTRO de la ventana actual (`last_seen[ch] >= left`), o actualizar
  `left = max(left, last_seen[ch] + 1)` para nunca retroceder `left`.
================================================================================
"""


# ==============================================================================
# EJERCICIO 1: Two Sum en Arreglo Ordenado (Opposite Pointers)
# ==============================================================================
def two_sum_sorted(nums: list[int], target: int) -> tuple[int, int] | None:
    """
    Dado un arreglo de enteros `nums` ordenado de forma ascendente y un entero
    `target`, encuentra los índices (0-indexed) de los dos números que suman
    exactamente `target`.

    Restricción algorítmica:
    - Complejidad temporal: O(n)
    - Complejidad espacial: O(1) (no uses diccionarios ni conjuntos adicionales).
    - Si no existe ningún par que sume `target`, retorna `None`.
    """
    # BEGIN_SOLUTION
    left = 0
    right = len(nums) - 1
    while left < right:
        current_sum = nums[left] + nums[right]
        if current_sum == target:
            return (left, right)
        if current_sum < target:
            left += 1
        else:
            right -= 1
    return None
    # END_SOLUTION


# ==============================================================================
# EJERCICIO 2: Contenedor con Más Agua (Container With Most Water)
# ==============================================================================
def max_area_container(heights: list[int]) -> int:
    """
    Se te da una lista `heights` donde cada elemento representa la altura de una
    línea vertical en la posición `i`. Encuentra dos líneas que, junto con el
    eje X, formen un contenedor capaz de almacenar la máxima cantidad de agua.

    Fórmula del área entre `left` y `right`:
        area = (right - left) * min(heights[left], heights[right])

    Estrategia O(n):
    - Inicia con el contenedor más ancho posible (`left = 0`, `right = len - 1`).
    - En cada iteración, mueve hacia adentro el puntero que tenga la MENOR altura
      (porque mantener la pared más baja mientras se reduce el ancho jamás podrá
      mejorar el área).
    - Si `len(heights) < 2`, retorna `0`.
    """
    # BEGIN_SOLUTION
    if len(heights) < 2:
        return 0
    left = 0
    right = len(heights) - 1
    best_area = 0
    while left < right:
        width = right - left
        h = min(heights[left], heights[right])
        best_area = max(best_area, width * h)
        if heights[left] <= heights[right]:
            left += 1
        else:
            right -= 1
    return best_area
    # END_SOLUTION


# ==============================================================================
# EJERCICIO 3: Tres Números que Suman Cero (3Sum sin duplicados)
# ==============================================================================
def three_sum_zero(nums: list[int]) -> list[tuple[int, int, int]]:
    """
    Dada una lista de enteros `nums`, devuelve todas las tripletas únicas
    `(a, b, c)` tales que `a + b + c == 0` y `a <= b <= c`.
    La lista resultante no debe contener tripletas duplicadas y debe estar
    ordenada lexicográficamente.

    Estrategia O(n²):
    1. Crea una copia ordenada `arr = sorted(nums)`.
    2. Itera `i` desde `0` hasta `len(arr) - 3`:
       - Si `arr[i] > 0`, puedes terminar temprano (`break`), ya que ningún
         número posterior podrá cancelar un valor positivo en un arreglo ordenado.
       - Si `i > 0` y `arr[i] == arr[i - 1]`, salta (`continue`) para evitar
         duplicados.
       - Usa dos punteros `left = i + 1` y `right = len(arr) - 1` para buscar
         `arr[i] + arr[left] + arr[right] == 0`, saltando valores repetidos en
         `left` y `right` tras cada hallazgo.
    """
    # BEGIN_SOLUTION
    arr = sorted(nums)
    n = len(arr)
    result: list[tuple[int, int, int]] = []

    for i in range(n - 2):
        if arr[i] > 0:
            break
        if i > 0 and arr[i] == arr[i - 1]:
            continue

        left = i + 1
        right = n - 1
        while left < right:
            total = arr[i] + arr[left] + arr[right]
            if total == 0:
                result.append((arr[i], arr[left], arr[right]))
                left += 1
                right -= 1
                while left < right and arr[left] == arr[left - 1]:
                    left += 1
                while left < right and arr[right] == arr[right + 1]:
                    right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1

    return result
    # END_SOLUTION


# ==============================================================================
# EJERCICIO 4: Subcadena Más Larga Sin Caracteres Repetidos
# ==============================================================================
def longest_substring_without_repeating(s: str) -> int:
    """
    Dada una cadena `s`, encuentra la longitud de la subcadena contigua más larga
    que no contenga caracteres repetidos.

    Estrategia O(n) con Ventana Deslizante + Diccionario de último índice:
    - Mantén `left = 0` y un diccionario `last_seen: dict[str, int] = {}`.
    - Al recorrer `for right, ch in enumerate(s):`
      Si `ch` está en `last_seen` y `last_seen[ch] >= left`, mueve `left` a
      `last_seen[ch] + 1`.
    - Registra `last_seen[ch] = right` y actualiza la longitud máxima
      `right - left + 1`.
    """
    # BEGIN_SOLUTION
    last_seen: dict[str, int] = {}
    left = 0
    max_len = 0

    for right, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1
        last_seen[ch] = right
        max_len = max(max_len, right - left + 1)

    return max_len
    # END_SOLUTION


# ==============================================================================
# EJERCICIO 5: Subarreglo Contiguo Más Corto con Suma >= Target
# ==============================================================================
def min_subarray_len_at_least(target: int, nums: list[int]) -> int:
    """
    Dado un arreglo de enteros positivos `nums` y un entero positivo `target`,
    devuelve la longitud mínima de un subarreglo contiguo cuya suma sea mayor o
    igual a `target`. Si no existe tal subarreglo, devuelve `0`.

    Estrategia O(n) con Ventana Deslizante Dinámica:
    - Expande la ventana sumando `nums[right]` a `window_sum`.
    - Mientras `window_sum >= target`:
      1. Actualiza la longitud mínima con `right - left + 1`.
      2. Resta `nums[left]` de `window_sum` e incrementa `left += 1`.
    """
    # BEGIN_SOLUTION
    left = 0
    window_sum = 0
    min_len = len(nums) + 1

    for right, val in enumerate(nums):
        window_sum += val
        while window_sum >= target:
            min_len = min(min_len, right - left + 1)
            window_sum -= nums[left]
            left += 1

    return 0 if min_len > len(nums) else min_len
    # END_SOLUTION


# ==============================================================================
# SUITE DE VERIFICACIÓN Y TESTS
# ==============================================================================
def _check_ex1() -> None:
    assert two_sum_sorted([2, 7, 11, 15], 9) == (0, 1)
    assert two_sum_sorted([1, 3, 4, 5, 7, 10, 11], 9) == (2, 3)
    assert two_sum_sorted([-6, -2, 0, 3, 8], -2) == (1, 2)
    assert two_sum_sorted([1, 2, 3, 4], 100) is None


def _check_ex2() -> None:
    assert max_area_container([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
    assert max_area_container([1, 1]) == 1
    assert max_area_container([4, 3, 2, 1, 4]) == 16
    assert max_area_container([1]) == 0


def _check_ex3() -> None:
    assert three_sum_zero([-1, 0, 1, 2, -1, -4]) == [(-1, -1, 2), (-1, 0, 1)]
    assert three_sum_zero([0, 1, 1]) == []
    assert three_sum_zero([0, 0, 0, 0]) == [(0, 0, 0)]
    assert three_sum_zero([-2, 0, 0, 2, 2]) == [(-2, 0, 2)]


def _check_ex4() -> None:
    assert longest_substring_without_repeating("abcabcbb") == 3
    assert longest_substring_without_repeating("bbbbb") == 1
    assert longest_substring_without_repeating("pwwkew") == 3
    assert longest_substring_without_repeating("") == 0
    assert longest_substring_without_repeating("abba") == 2


def _check_ex5() -> None:
    assert min_subarray_len_at_least(7, [2, 3, 1, 2, 4, 3]) == 2
    assert min_subarray_len_at_least(4, [1, 4, 4]) == 1
    assert min_subarray_len_at_least(11, [1, 1, 1, 1, 1, 1, 1, 1]) == 0
    assert min_subarray_len_at_least(15, [5, 1, 3, 5, 10, 7, 4, 9, 2, 8]) == 2


def test_kata() -> None:
    """Entrypoint para pytest."""
    _check_ex1()
    _check_ex2()
    _check_ex3()
    _check_ex4()
    _check_ex5()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 01_two_pointers_and_sliding_window.py")
    print("=" * 72)
    checks: list[tuple[str, Callable[[], None]]] = [
        ("Ejercicio 1: two_sum_sorted", _check_ex1),
        ("Ejercicio 2: max_area_container", _check_ex2),
        ("Ejercicio 3: three_sum_zero", _check_ex3),
        ("Ejercicio 4: longest_substring_without_repeating", _check_ex4),
        ("Ejercicio 5: min_subarray_len_at_least", _check_ex5),
    ]
    passed = 0
    failed = 0
    pending = 0

    for label, fn in checks:
        t0 = time.perf_counter()
        try:
            fn()
            elapsed = (time.perf_counter() - t0) * 1000
            print(f"✅ [PASS]      {label} ({elapsed:.2f} ms)")
            passed += 1
        except NotImplementedError:
            print(f"⏳ [PENDIENTE] {label}")
            pending += 1
        except Exception as exc:
            print(f"❌ [FAIL]      {label} -> {type(exc).__name__}: {exc}")
            failed += 1

    print("-" * 72)
    print(f"Resumen: {passed} pasados | {pending} pendientes | {failed} fallidos")
    if failed > 0 or pending > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    run_verification()
