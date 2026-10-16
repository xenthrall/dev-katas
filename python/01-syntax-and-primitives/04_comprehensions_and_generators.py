from __future__ import annotations

from collections.abc import Generator, Iterable, Iterator
import sys
import time
from typing import Callable, TypeVar

"""
MÓDULO 01 — SINTAXIS Y PRIMITIVAS: 04. COMPREHENSIONS Y GENERADORES
===============================================================================
Estudio profundo y práctica deliberada sobre comprensiones de listas, sets y
diccionarios, evaluación perezosa con expresiones generadoras, funciones
generadoras (`yield`) y cuantificadores en cortocircuito (`any`, `all`, `next`).

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Comprehensions (List, Dict, Set):
   - Sintaxis general con filtrado:
     `[expr for item in iterable if condicion]`
   - Comprensión anidada (el orden de los `for` es idéntico al de los bucles
     anidados tradicionales: de afuera hacia adentro):
     `plano = [x for fila in matriz for x in fila if x > 0]`
   - Dict comprehension:
     `{k: v for k, v in pares if v is not None}`

2. Expresiones Generadoras y Funciones con `yield` (Memoria O(1)):
   - Una expresión `(x * x for x in range(10**7))` NO construye una lista en RAM;
     produce valores bajo demanda uno por uno.
   - Una función que contiene `yield` devuelve un objeto `Generator`:
     pausa su estado local en cada `yield` y lo reanuda cuando se invoca `next()`.

3. Evaluación en Cortocircuito (`any`, `all`, `next`):
   - `any(pred(x) for x in seq)`: Devuelve `True` en cuanto encuentra el PRIMER
     elemento verdadero (sin evaluar el resto).
   - `all(pred(x) for x in seq)`: Devuelve `False` en cuanto encuentra el PRIMER
     elemento falso. Nota: `all([]) == True` (verdad vacua).
   - `next((x for x in seq if pred(x)), valor_por_defecto)`: Encuentra la primera
     coincidencia en O(1) memoria extra sin lanzar `StopIteration`.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- ❌ Filtro vs Expresión Ternaria en Comprehensions:
  * Filtrar elementos (van al final): `[x for x in nums if x > 0]`
  * Transformar elementos (va al principio): `[x if x > 0 else 0 for x in nums]`
- ❌ Agotamiento de Generadores: Un generador solo se puede recorrer UNA vez.
  Si llamas a `sum(gen)` y luego `list(gen)`, la segunda llamada devolverá `[]`.
"""

T = TypeVar("T")


def flatten_positive_evens(matrix: list[list[int]]) -> list[int]:
    """Aplana una matriz 2D extrayendo únicamente los números positivos pares.

    Ejemplo:
        >>> flatten_positive_evens([[-2, 4, 3], [0, 6, 8], [1, -4, 10]])
        [4, 6, 8, 10]

    Complejidad objetivo:
        Tiempo: O(filas * cols) | Espacio: O(k) elementos filtrados

    Pista:
        Usa una list comprehension anidada: `[x for row in matrix for x in row if ...]`.
    """
    # BEGIN_SOLUTION
    return [x for row in matrix for x in row if x > 0 and x % 2 == 0]
    # END_SOLUTION


def build_normalized_score_map(
    raw_scores: list[tuple[str, int]], min_passing: int = 60
) -> dict[str, str]:
    """Construye un diccionario `{nombre_normalizado: estado}` usando dict comprehension.

    Reglas:
    - Normaliza el nombre con `.strip().lower()`.
    - Ignora registros cuyo nombre normalizado esté vacío.
    - Si `score >= min_passing`, el valor es `"APROBADO"`, de lo contrario `"REPROBADO"`.

    Ejemplo:
        >>> build_normalized_score_map([(" Ana ", 85), ("Luis", 40), ("   ", 90)])
        {'ana': 'APROBADO', 'luis': 'REPROBADO'}

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Combina expresión ternaria en el valor con filtro `if name.strip()` al final.
    """
    # BEGIN_SOLUTION
    return {
        name.strip().lower(): ("APROBADO" if score >= min_passing else "REPROBADO")
        for name, score in raw_scores
        if name.strip()
    }
    # END_SOLUTION


def chunked_stream(iterable: Iterable[T], batch_size: int) -> Generator[list[T], None, None]:
    """Generador que divide cualquier iterable en listas de tamaño máximo `batch_size`.

    Si `batch_size <= 0`, lanza `ValueError`. El último lote puede tener menos
    de `batch_size` elementos si el iterable no es múltiplo exacto.

    Ejemplo:
        >>> list(chunked_stream([1, 2, 3, 4, 5], batch_size=2))
        [[1, 2], [3, 4], [5]]

    Complejidad objetivo:
        Tiempo: O(n) | Espacio auxiliar: O(batch_size)

    Pista:
        Acumula elementos en una lista `batch`; cuando `len(batch) == batch_size`,
        haz `yield batch` y reinicia `batch = []`. No olvides emitir el resto final.
    """
    # BEGIN_SOLUTION
    if batch_size <= 0:
        raise ValueError("batch_size debe ser mayor a 0")

    batch: list[T] = []
    for item in iterable:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
    # END_SOLUTION


def fibonacci_up_to(limit: int) -> Iterator[int]:
    """Generador perezoso que produce números de Fibonacci menores o iguales a `limit`.

    La secuencia comienza en `0, 1, 1, 2, 3, 5, 8...`. Si `limit < 0`, no produce nada.

    Ejemplo:
        >>> list(fibonacci_up_to(10))
        [0, 1, 1, 2, 3, 5, 8]

    Complejidad objetivo:
        Tiempo: O(k) pasos | Espacio: O(1)

    Pista:
        Mantén `a, b = 0, 1` y mientras `a <= limit`, emite `yield a` y actualiza `a, b = b, a + b`.
    """
    # BEGIN_SOLUTION
    a, b = 0, 1
    while a <= limit:
        yield a
        a, b = b, a + b
    # END_SOLUTION


def first_valid_transaction(
    transactions: Iterable[dict[str, int | str | bool]],
    min_amount: int,
) -> dict[str, int | str | bool] | None:
    """Devuelve la primera transacción verificada con monto >= `min_amount` en O(1) memoria.

    Una transacción es válida si `tx.get("verified") is True` y
    `int(tx.get("amount", 0)) >= min_amount`. Si ninguna cumple, devuelve `None`.

    Ejemplo:
        >>> txs = [{"id": "t1", "amount": 500, "verified": False}, {"id": "t2", "amount": 300, "verified": True}]
        >>> first_valid_transaction(txs, min_amount=200)
        {'id': 't2', 'amount': 300, 'verified': True}

    Complejidad objetivo:
        Tiempo: O(n) en el peor caso (cortocircuito) | Espacio: O(1)

    Pista:
        Usa `next((tx for tx in transactions if ...), None)`.
    """
    # BEGIN_SOLUTION
    return next(
        (
            tx
            for tx in transactions
            if tx.get("verified") is True and int(tx.get("amount", 0)) >= min_amount
        ),
        None,
    )
    # END_SOLUTION


def validate_password_batch(passwords: list[str]) -> tuple[bool, bool]:
    """Evalúa un lote de contraseñas con `all()` y `any()` en cortocircuito.

    Devuelve una tupla `(todas_tienen_al_menos_8_chars, alguna_contiene_digito)`:
    1. `True` si TODAS las contraseñas tienen longitud `>= 8` (si la lista está
       vacía, devuelve `False`).
    2. `True` si ALGUNA contraseña contiene al menos un carácter numérico (`ch.isdigit()`).

    Ejemplo:
        >>> validate_password_batch(["secreto123", "clave_larga"])
        (True, True)

    Complejidad objetivo:
        Tiempo: O(total_caracteres) | Espacio: O(1)

    Pista:
        Combina `all(len(p) >= 8 for p in passwords)` y
        `any(any(ch.isdigit() for ch in p) for p in passwords)`.
    """
    # BEGIN_SOLUTION
    if not passwords:
        return (False, False)
    all_long_enough = all(len(p) >= 8 for p in passwords)
    any_has_digit = any(any(ch.isdigit() for ch in p) for p in passwords)
    return (all_long_enough, any_has_digit)
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_flatten_positive_evens() -> None:
    assert flatten_positive_evens([[-2, 4, 3], [0, 6, 8], [1, -4, 10]]) == [4, 6, 8, 10]
    assert flatten_positive_evens([[], [-1, 3]]) == []


def check_build_normalized_score_map() -> None:
    res = build_normalized_score_map([(" Ana ", 85), ("LUIS", 59), ("  ", 100), ("Eva", 60)])
    assert res == {"ana": "APROBADO", "luis": "REPROBADO", "eva": "APROBADO"}


def check_chunked_stream() -> None:
    gen = chunked_stream((x for x in range(1, 8)), batch_size=3)
    assert list(gen) == [[1, 2, 3], [4, 5, 6], [7]]
    assert list(chunked_stream([], batch_size=4)) == []
    try:
        list(chunked_stream([1, 2], batch_size=0))
        raise AssertionError("Debió lanzar ValueError")
    except ValueError:
        pass


def check_fibonacci_up_to() -> None:
    assert list(fibonacci_up_to(10)) == [0, 1, 1, 2, 3, 5, 8]
    assert list(fibonacci_up_to(0)) == [0]
    assert list(fibonacci_up_to(-5)) == []


def check_first_valid_transaction() -> None:
    txs = [
        {"id": "t1", "amount": 500, "verified": False},
        {"id": "t2", "amount": 100, "verified": True},
        {"id": "t3", "amount": 350, "verified": True},
        {"id": "t4", "amount": 900, "verified": True},
    ]
    assert first_valid_transaction(txs, 200) == {"id": "t3", "amount": 350, "verified": True}
    assert first_valid_transaction(txs, 1000) is None


def check_validate_password_batch() -> None:
    assert validate_password_batch(["secreto123", "clave_larga"]) == (True, True)
    assert validate_password_batch(["solo_letras", "otra_larga"]) == (True, False)
    assert validate_password_batch(["corta1", "clave_larga9"]) == (False, True)
    assert validate_password_batch([]) == (False, False)


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. flatten_positive_evens", check_flatten_positive_evens),
    ("02. build_normalized_score_map", check_build_normalized_score_map),
    ("03. chunked_stream", check_chunked_stream),
    ("04. fibonacci_up_to", check_fibonacci_up_to),
    ("05. first_valid_transaction", check_first_valid_transaction),
    ("06. validate_password_batch", check_validate_password_batch),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 04_comprehensions_and_generators.py")
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
