from __future__ import annotations

from collections.abc import Iterable
import functools
import itertools
import operator
import sys
import time
from typing import Any, Callable

"""
MÓDULO 02 — MANIPULACIÓN DE DATOS Y STDLIB: 02. ITERTOOLS Y FUNCTOOLS
===============================================================================
Estudio profundo y práctica deliberada sobre el álgebra de iteradores en C
(`itertools`) y las utilidades de orden superior y memoización (`functools`).

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. `itertools` — Procesamiento Perezoso en C:
   - `itertools.groupby(iterable, key=fn)`: Agrupa elementos **CONSECUTIVOS**
     con la misma clave. ⚠️ SIEMPRE debes ordenar primero por la misma función
     `key` si quieres agrupar todas las ocurrencias globales.
   - `itertools.islice(iterable, start, stop, step)`: Slicing sobre cualquier
     iterador o generador infinito en O(1) memoria.
   - `itertools.accumulate(iterable, func=operator.add)`: Sumas (o reducciones)
     prefijas acumuladas paso a paso.
   - `itertools.chain.from_iterable(iterables)`: Aplana un nivel de listas/iterables.
   - Combinatoria:
     * `product(A, B, repeat=1)`: Producto cartesiano.
     * `combinations(iterable, r)`: Subconjuntos de tamaño `r` sin importar orden.
     * `permutations(iterable, r)`: Arreglos de tamaño `r` importando el orden.

2. `functools` — Orden Superior, Caché y Polimorfismo:
   - `@functools.cache` / `@functools.lru_cache(maxsize=128)`: Memoiza llamadas
     basándose en los argumentos (los argumentos deben ser hashables).
   - `functools.reduce(fn, iterable, initializer)`: Acumula una secuencia a un
     único valor.
   - `functools.partial(fn, *args, **kwargs)`: Fija ("congela") argumentos de una
     función produciendo un nuevo callable con firma reducida.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- Trampa #1 de `itertools.groupby`: Si pasas `["A", "B", "A"]` sin ordenar antes,
  `groupby` producirá TRES grupos (`A`, `B` y otra vez `A`). Además, el sub-iterador
  ` group` se consume al avanzar al siguiente paso del bucle; materialízalo
  inmediatamente con `list(group)` o `sum(...)`.
- `@functools.cache` lanza `TypeError: unhashable type: 'list'` si pasas listas
  o diccionarios como argumentos; convierte secuencias a `tuple` antes.
"""


def group_sales_by_region(records: list[tuple[str, float]]) -> dict[str, float]:
    """Suma las ventas por región usando `sorted` + `itertools.groupby`.

    Cada registro es `(region, monto)`. Recuerda que `groupby` solo agrupa
    elementos adyacentes, por lo que primero debes ordenar por región.
    Redondea cada suma regional a 2 decimales.

    Ejemplo:
        >>> group_sales_by_region([("Sur", 10.5), ("Norte", 20.0), ("Sur", 4.5)])
        {'Norte': 20.0, 'Sur': 15.0}

    Complejidad objetivo:
        Tiempo: O(n log n) | Espacio: O(n)

    Pista:
        Ordena con `key=operator.itemgetter(0)` y agrupa con `itertools.groupby`.
    """
    # BEGIN_SOLUTION
    sorted_records = sorted(records, key=operator.itemgetter(0))
    totals: dict[str, float] = {}
    for region, group in itertools.groupby(sorted_records, key=operator.itemgetter(0)):
        totals[region] = round(sum(amount for _, amount in group), 2)
    return totals
    # END_SOLUTION


def running_max_and_prefix_sums(nums: list[int]) -> tuple[list[int], list[int]]:
    """Calcula la lista de sumas prefijas y la lista de máximos acumulados con `accumulate`.

    Si `nums` está vacía, devuelve `([], [])`.

    Ejemplo:
        >>> running_max_and_prefix_sums([3, 1, 5, 2, 8])
        ([3, 4, 9, 11, 19], [3, 3, 5, 5, 8])

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Usa `list(itertools.accumulate(nums))` para las sumas y
        `list(itertools.accumulate(nums, max))` para los máximos acumulados.
    """
    # BEGIN_SOLUTION
    return (
        list(itertools.accumulate(nums)),
        list(itertools.accumulate(nums, max)),
    )
    # END_SOLUTION


def paginate_iterator(
    stream: Iterable[Any], page_number: int, page_size: int
) -> list[Any]:
    """Extrae una página (0-indexed) de un iterador arbitrario usando `itertools.islice`.

    Si `page_number < 0` o `page_size <= 0`, lanza `ValueError`.

    Ejemplo:
        >>> paginate_iterator(range(100), page_number=2, page_size=4)
        [8, 9, 10, 11]

    Complejidad objetivo:
        Tiempo: O((page_number + 1) * page_size) | Espacio: O(page_size)

    Pista:
        Calcula `start = page_number * page_size` y `stop = start + page_size`,
        luego aplica `list(itertools.islice(stream, start, stop))`.
    """
    # BEGIN_SOLUTION
    if page_number < 0 or page_size <= 0:
        raise ValueError("page_number debe ser >= 0 y page_size > 0")
    start = page_number * page_size
    stop = start + page_size
    return list(itertools.islice(stream, start, stop))
    # END_SOLUTION


def best_team_combination(
    players: list[tuple[str, int]], team_size: int, max_budget: int
) -> tuple[str, ...]:
    """Encuentra la combinación de `team_size` jugadores con mayor puntaje dentro de `max_budget`.

    Cada elemento en `players` es `(nombre, costo_y_puntaje)`. Evaluando todas las
    combinaciones con `itertools.combinations(players, team_size)`, devuelve una
    tupla con los nombres de la combinación cuya suma sea `<= max_budget` y tenga
    la suma máxima posible. Si ninguna combinación entra en el presupuesto, devuelve `()`.

    Ejemplo:
        >>> best_team_combination([("A", 30), ("B", 40), ("C", 50), ("D", 20)], 2, 75)
        ('A', 'B')

    Complejidad objetivo:
        Tiempo: O(C(n, k)) | Espacio: O(k)

    Pista:
        Recorre `itertools.combinations(players, team_size)` calculando la suma de cada grupo.
    """
    # BEGIN_SOLUTION
    best_score = -1
    best_names: tuple[str, ...] = ()
    for combo in itertools.combinations(players, team_size):
        score = sum(val for _, val in combo)
        if score <= max_budget and score > best_score:
            best_score = score
            best_names = tuple(name for name, _ in combo)
    return best_names
    # END_SOLUTION


def count_grid_paths_memoized(rows: int, cols: int, blocked: set[tuple[int, int]]) -> int:
    """Cuenta cuántos caminos existen de `(0, 0)` a `(rows-1, cols-1)` usando `@functools.cache`.

    Solo puedes moverte hacia abajo `(r + 1, c)` o hacia la derecha `(r, c + 1)`.
    Las celdas en `blocked` no pueden pisarse.

    Ejemplo:
        >>> count_grid_paths_memoized(3, 3, blocked={(1, 1)})
        2

    Complejidad objetivo:
        Tiempo: O(rows * cols) | Espacio: O(rows * cols)

    Pista:
        Define una función interna `@functools.cache def dp(r: int, c: int) -> int:`
        con casos base fuera de límites, en `blocked`, y en la esquina destino.
    """
    # BEGIN_SOLUTION
    if rows <= 0 or cols <= 0:
        return 0

    @functools.cache
    def _dp(r: int, c: int) -> int:
        if r >= rows or c >= cols or (r, c) in blocked:
            return 0
        if r == rows - 1 and c == cols - 1:
            return 1
        return _dp(r + 1, c) + _dp(r, c + 1)

    return _dp(0, 0)
    # END_SOLUTION


def make_tax_calculators(rates: dict[str, float]) -> dict[str, Callable[[float], float]]:
    """Crea funciones especializadas de cálculo de precio con impuesto usando `functools.partial`.

    A partir de una función base `apply_tax(rate: float, amount: float) -> float`
    que devuelve `round(amount * (1.0 + rate), 2)`, construye un diccionario
    `{pais: partial(apply_tax, rate)}`.

    Ejemplo:
        >>> calcs = make_tax_calculators({"ES": 0.21, "US": 0.08})
        >>> calcs["ES"](100.0), calcs["US"](100.0)
        (121.0, 108.0)

    Complejidad objetivo:
        Tiempo: O(k) tasas | Espacio: O(k)

    Pista:
        Usa `functools.partial(_apply_tax, rate)` para fijar el primer argumento `rate`.
    """
    # BEGIN_SOLUTION
    def _apply_tax(rate: float, amount: float) -> float:
        return round(amount * (1.0 + rate), 2)

    return {country: functools.partial(_apply_tax, rate) for country, rate in rates.items()}
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_group_sales_by_region() -> None:
    data = [("Sur", 10.5), ("Norte", 20.0), ("Sur", 4.5), ("Centro", 12.0), ("Norte", 5.25)]
    assert group_sales_by_region(data) == {"Centro": 12.0, "Norte": 25.25, "Sur": 15.0}
    assert group_sales_by_region([]) == {}


def check_running_max_and_prefix_sums() -> None:
    assert running_max_and_prefix_sums([3, 1, 5, 2, 8]) == (
        [3, 4, 9, 11, 19],
        [3, 3, 5, 5, 8],
    )
    assert running_max_and_prefix_sums([]) == ([], [])


def check_paginate_iterator() -> None:
    assert paginate_iterator((x * 2 for x in range(20)), page_number=1, page_size=3) == [6, 8, 10]
    assert paginate_iterator(range(5), page_number=10, page_size=3) == []


def check_best_team_combination() -> None:
    players = [("A", 30), ("B", 40), ("C", 50), ("D", 20)]
    assert best_team_combination(players, 2, 75) == ("A", "B")
    assert best_team_combination(players, 2, 10) == ()


def check_count_grid_paths_memoized() -> None:
    assert count_grid_paths_memoized(3, 3, blocked=set()) == 6
    assert count_grid_paths_memoized(3, 3, blocked={(1, 1)}) == 2
    assert count_grid_paths_memoized(2, 2, blocked={(0, 0)}) == 0


def check_make_tax_calculators() -> None:
    calcs = make_tax_calculators({"ES": 0.21, "MX": 0.16})
    assert calcs["ES"](100.0) == 121.0
    assert calcs["MX"](250.0) == 290.0


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. group_sales_by_region", check_group_sales_by_region),
    ("02. running_max_and_prefix_sums", check_running_max_and_prefix_sums),
    ("03. paginate_iterator", check_paginate_iterator),
    ("04. best_team_combination", check_best_team_combination),
    ("05. count_grid_paths_memoized", check_count_grid_paths_memoized),
    ("06. make_tax_calculators", check_make_tax_calculators),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 02_itertools_and_functools.py")
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
