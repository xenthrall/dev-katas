from __future__ import annotations

import copy
import sys
import time
from typing import Any, Callable, NamedTuple

"""
MÓDULO 01 — SINTAXIS Y PRIMITIVAS: 02. LISTAS, TUPLAS Y UNPACKING
===============================================================================
Estudio profundo y práctica deliberada sobre secuencias mutables (`list`) e
inmutables (`tuple`), desempaquetado con expresiones estrella (`*`), rotación
por slices, transposición matricial con `zip(*matriz)` y copias superficiales
vs profundas (`copy` vs `deepcopy`).

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Desempaquetado Extendido (PEP 3132 - Starred Unpacking):
   - Permite capturar múltiples elementos restantes en una `list`:
     * `primero, *medio, ultimo = [10, 20, 30, 40]` -> `10`, `[20, 30]`, `40`
     * `cabeza, *cola = [99]`                       -> `99`, `[]`
   - Intercambio in-place sin variable temporal:
     * `a, b = b, a`

2. Mutación por Slices y Rotación de Listas:
   - `nums[:] = nuevos_valores` modifica el objeto `list` existente in-place
     (conserva el mismo `id(nums)` en memoria).
   - Rotar a la derecha `k` posiciones (con `k %= len(nums)`):
     `nums[-k:] + nums[:-k]`

3. Transposición e Intercalado con `zip`:
   - `zip(a, b)` empareja elementos posición a posición hasta agotar el más corto.
   - `zip(*matriz)` desempaqueta las filas como argumentos separados, agrupando
     las columnas en tuplas:
     `transpuesta = [list(col) for col in zip(*matriz)]`

4. Tuplas y `NamedTuple`:
   - Una `tuple` es inmutable y consume menos memoria que una `list`.
   - `typing.NamedTuple` permite definir registros inmutables con acceso tanto
     por nombre de atributo (`p.x`) como por índice/desempaquetado (`x, y = p`).

5. Copia Superficial (`copy`) vs Copia Profunda (`copy.deepcopy`):
   - `lista.copy()` o `lista[:]` crea una nueva lista externa, pero las sublistas
     o diccionarios internos siguen apuntando a las mismas referencias.
   - `copy.deepcopy(estructura)` clona recursivamente todos los contenedores
     anidados garantizando aislamiento total.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- ❌ Trampa `[[0] * cols] * rows`: Replica `rows` veces la referencia a la MISMA
  fila. Modificar `mat[0][0] = 1` modifica la columna 0 de todas las filas.
  ✅ Usa siempre `[[0] * cols for _ in range(rows)]`.
- ❌ Trampa `t = (42)`: Esto es el entero `42` entre paréntesis, NO una tupla.
  ✅ Para una tupla de un solo elemento incluye la coma: `t = (42,)`.
- `list.sort()` ordena in-place y devuelve `None`; `sorted(iterable)` crea y
  devuelve una nueva lista ordenada.
"""


class Point3D(NamedTuple):
    x: float
    y: float
    z: float


def trim_extremes_average(values: list[float]) -> tuple[float, float, list[float], float]:
    """Separa el mínimo, el máximo y los elementos centrales tras ordenar.

    Ordena una copia de `values` de menor a mayor, usa desempaquetado con `*`
    (`min_val, *middle, max_val = ...`) y devuelve una 4-tupla:
    `(min_val, max_val, middle, promedio_de_middle_redondeado_a_2_decimales)`.

    Si `len(values) < 3`, lanza `ValueError`.

    Ejemplo:
        >>> trim_extremes_average([10.0, 2.0, 8.0, 6.0, 4.0])
        (2.0, 10.0, [4.0, 6.0, 8.0], 6.0)

    Complejidad objetivo:
        Tiempo: O(n log n) | Espacio: O(n)

    Pista:
        Ordena con `sorted(values)` y desempaqueta con `low, *mid, high = ...`.
    """
    # BEGIN_SOLUTION
    if len(values) < 3:
        raise ValueError("Se requieren al menos 3 valores.")
    low, *mid, high = sorted(values)
    avg = round(sum(mid) / len(mid), 2)
    return (low, high, mid, avg)
    # END_SOLUTION


def rotate_in_place(items: list[Any], k: int) -> None:
    """Rota la lista `items` hacia la derecha `k` pasos modificándola IN-PLACE.

    Soporta `k` positivo, negativo o mayor que `len(items)`. No debe devolver
    una lista nueva, sino mutar el contenido de `items` usando asignación por
    slice `items[:] = ...`.

    Ejemplo:
        >>> data = [1, 2, 3, 4, 5]
        >>> rotate_in_place(data, 2)
        >>> data
        [4, 5, 1, 2, 3]

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Si `items` no está vacía, normaliza `k %= len(items)` y asigna
        `items[:] = items[-k:] + items[:-k]` (cuando `k > 0`).
    """
    # BEGIN_SOLUTION
    if not items:
        return
    n = len(items)
    shift = k % n
    if shift == 0:
        return
    items[:] = items[-shift:] + items[:-shift]
    # END_SOLUTION


def transpose_matrix(matrix: list[list[int]]) -> list[list[int]]:
    """Transpone una matriz rectangular convirtiendo filas en columnas.

    Si `matrix` está vacía o sus filas están vacías, devuelve `[]`.

    Ejemplo:
        >>> transpose_matrix([[1, 2, 3], [4, 5, 6]])
        [[1, 4], [2, 5], [3, 6]]

    Complejidad objetivo:
        Tiempo: O(filas * cols) | Espacio: O(filas * cols)

    Pista:
        Usa `zip(*matrix)` dentro de una list comprehension `[list(col) for col in zip(*matrix)]`.
    """
    # BEGIN_SOLUTION
    if not matrix or not matrix[0]:
        return []
    return [list(col) for col in zip(*matrix)]
    # END_SOLUTION


def interleave_with_remainder(seq_a: list[Any], seq_b: list[Any]) -> list[Any]:
    """Intercala elementos de `seq_a` y `seq_b` alternadamente y añade el sobrante.

    Ejemplo:
        >>> interleave_with_remainder([1, 2, 3], ["a", "b"])
        [1, 'a', 2, 'b', 3]
        >>> interleave_with_remainder(["x"], [10, 20, 30])
        ['x', 10, 20, 30]

    Complejidad objetivo:
        Tiempo: O(n + m) | Espacio: O(n + m)

    Pista:
        Empareja el tramo común con `zip(seq_a, seq_b)` y extiende con el slice
        restante `seq_a[min_len:]` y `seq_b[min_len:]`.
    """
    # BEGIN_SOLUTION
    out: list[Any] = []
    for a, b in zip(seq_a, seq_b):
        out.append(a)
        out.append(b)
    min_len = min(len(seq_a), len(seq_b))
    out.extend(seq_a[min_len:])
    out.extend(seq_b[min_len:])
    return out
    # END_SOLUTION


def clone_and_patch_matrix(
    grid: list[list[int]], row: int, col: int, new_value: int
) -> list[list[int]]:
    """Crea una copia profunda de `grid` y actualiza `(row, col)` sin mutar la original.

    Ejemplo:
        >>> orig = [[1, 2], [3, 4]]
        >>> nueva = clone_and_patch_matrix(orig, 0, 1, 99)
        >>> orig[0][1], nueva[0][1]
        (2, 99)

    Complejidad objetivo:
        Tiempo: O(filas * cols) | Espacio: O(filas * cols)

    Pista:
        Usa `copy.deepcopy(grid)` o `[r.copy() for r in grid]` antes de mutar la celda.
    """
    # BEGIN_SOLUTION
    cloned = copy.deepcopy(grid)
    cloned[row][col] = new_value
    return cloned
    # END_SOLUTION


def bounding_box_3d(points: list[Point3D]) -> tuple[Point3D, Point3D]:
    """Calcula la caja delimitadora `(min_point, max_point)` de una nube de `Point3D`.

    Si `points` está vacía, lanza `ValueError`.

    Ejemplo:
        >>> pts = [Point3D(1, 5, -2), Point3D(-3, 2, 4), Point3D(0, 8, 1)]
        >>> bounding_box_3d(pts)
        (Point3D(x=-3, y=2, z=-2), Point3D(x=1, y=8, z=4))

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Desempaqueta las coordenadas por eje con `xs, ys, zs = zip(*points)` y
        construye los dos `Point3D` con `min(...)` y `max(...)`.
    """
    # BEGIN_SOLUTION
    if not points:
        raise ValueError("La lista de puntos no puede estar vacía.")
    xs, ys, zs = zip(*points)
    return (
        Point3D(min(xs), min(ys), min(zs)),
        Point3D(max(xs), max(ys), max(zs)),
    )
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_trim_extremes_average() -> None:
    assert trim_extremes_average([10.0, 2.0, 8.0, 6.0, 4.0]) == (
        2.0,
        10.0,
        [4.0, 6.0, 8.0],
        6.0,
    )
    assert trim_extremes_average([1.0, 100.0, 5.0]) == (1.0, 100.0, [5.0], 5.0)
    try:
        trim_extremes_average([1.0, 2.0])
        raise AssertionError("Debió lanzar ValueError")
    except ValueError:
        pass


def check_rotate_in_place() -> None:
    arr = [1, 2, 3, 4, 5]
    orig_id = id(arr)
    rotate_in_place(arr, 2)
    assert arr == [4, 5, 1, 2, 3]
    assert id(arr) == orig_id
    rotate_in_place(arr, -2)
    assert arr == [1, 2, 3, 4, 5]
    empty: list[int] = []
    rotate_in_place(empty, 5)
    assert empty == []


def check_transpose_matrix() -> None:
    assert transpose_matrix([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
    assert transpose_matrix([[10]]) == [[10]]
    assert transpose_matrix([]) == []


def check_interleave_with_remainder() -> None:
    assert interleave_with_remainder([1, 2, 3], ["a", "b"]) == [1, "a", 2, "b", 3]
    assert interleave_with_remainder(["x"], [10, 20, 30]) == ["x", 10, 20, 30]
    assert interleave_with_remainder([], [1, 2]) == [1, 2]


def check_clone_and_patch_matrix() -> None:
    orig = [[1, 2], [3, 4]]
    patched = clone_and_patch_matrix(orig, 1, 0, 99)
    assert orig == [[1, 2], [3, 4]]
    assert patched == [[1, 2], [99, 4]]


def check_bounding_box_3d() -> None:
    pts = [Point3D(1, 5, -2), Point3D(-3, 2, 4), Point3D(0, 8, 1)]
    low, high = bounding_box_3d(pts)
    assert low == Point3D(-3, 2, -2)
    assert high == Point3D(1, 8, 4)


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. trim_extremes_average", check_trim_extremes_average),
    ("02. rotate_in_place", check_rotate_in_place),
    ("03. transpose_matrix", check_transpose_matrix),
    ("04. interleave_with_remainder", check_interleave_with_remainder),
    ("05. clone_and_patch_matrix", check_clone_and_patch_matrix),
    ("06. bounding_box_3d", check_bounding_box_3d),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 02_lists_tuples_and_unpacking.py")
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
