from __future__ import annotations

from collections.abc import Generator, Iterator
import contextlib
import sys
import time
from types import TracebackType
from typing import Any, Callable

"""
MÓDULO 03 — POO Y MODELO DE OBJETOS: 04. ITERADORES Y CONTEXT MANAGERS
===============================================================================
Estudio profundo y práctica deliberada sobre el protocolo Iterador (`__iter__`,
`__next__`), delegación recursiva de generadores (`yield from`) y gestores de
contexto (`with`, `__enter__`/`__exit__`, `@contextlib.contextmanager`).

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Iterable vs Iterador:
   - **Iterable:** Objeto con `__iter__()` que devuelve un **nuevo** iterador
     cada vez que se recorre (ej. `list`, `range`).
   - **Iterador:** Objeto con `__iter__()` (devuelve `self`) y `__next__()`
     que avanza el cursor y lanza `StopIteration` al terminar.

2. Delegación con `yield from`:
   - `yield from sub_generador` delega directamente la iteración al generador
     interno sin necesidad de escribir un bucle `for x in sub: yield x`.

3. Protocolo Context Manager (`with recurso as r:`):
   - `__enter__(self)`: Adquiere el recurso y devuelve el objeto ligado a `as`.
   - `__exit__(self, exc_type, exc_val, exc_tb) -> bool`:
     * Si retorna `True`, **suprime** la excepción ocurrida dentro del bloque `with`.
     * Si retorna `False` o `None`, la excepción se propaga normalmente tras limpiar.
   - `@contextlib.contextmanager`: Convierte un generador con un único `yield`
     en un Context Manager (`try: yield recurso finally: limpieza()`).

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- Cuando uses `@contextmanager`, envuelve SIEMPRE el `yield` en un bloque
  `try: ... finally: ...` porque si ocurre una excepción dentro del bloque `with`,
  Python la inyecta en el punto del `yield` mediante `gen.throw(exc)`.
"""


class CountdownIterator:
    """Iterador personalizado que cuenta hacia atrás desde `start` hasta `stop` inclusive."""

    def __init__(self, start: int, stop: int = 0) -> None:
        self.current = start
        self.stop = stop

    def __iter__(self) -> CountdownIterator:
        # BEGIN_SOLUTION
        return self
        # END_SOLUTION

    def __next__(self) -> int:
        # BEGIN_SOLUTION
        if self.current < self.stop:
            raise StopIteration
        val = self.current
        self.current -= 1
        return val
        # END_SOLUTION


def flatten_nested_iterables(nested: list[Any]) -> Generator[Any, None, None]:
    """Aplana recursivamente listas o tuplas arbitrariamente anidadas usando `yield from`.

    No debe desglosar cadenas `str` ni `bytes` (trátalos como valores atómicos).

    Ejemplo:
        >>> list(flatten_nested_iterables([1, [2, (3, 4), []], "hola", [5]]))
        [1, 2, 3, 4, 'hola', 5]
    """
    # BEGIN_SOLUTION
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from flatten_nested_iterables(list(item))
        else:
            yield item
    # END_SOLUTION


class AtomicDictTransaction:
    """Context manager que hace commit sobre `target` al salir sin errores, o rollback si falla."""

    def __init__(self, target: dict[str, Any]) -> None:
        self.target = target
        self._working_copy: dict[str, Any] = {}

    def __enter__(self) -> dict[str, Any]:
        # BEGIN_SOLUTION
        self._working_copy = self.target.copy()
        return self._working_copy
        # END_SOLUTION

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        # BEGIN_SOLUTION
        if exc_type is None:
            self.target.clear()
            self.target.update(self._working_copy)
        return False
        # END_SOLUTION


@contextlib.contextmanager
def temporary_config_override(
    config: dict[str, Any], **overrides: Any
) -> Iterator[dict[str, Any]]:
    """Sobrescribe temporalmente claves en `config` y restaura el estado exacto en `finally`."""
    # BEGIN_SOLUTION
    snapshot = config.copy()
    config.update(overrides)
    try:
        yield config
    finally:
        config.clear()
        config.update(snapshot)
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_countdown_iterator() -> None:
    assert list(CountdownIterator(4, 1)) == [4, 3, 2, 1]
    assert list(CountdownIterator(0, 5)) == []


def check_flatten_nested_iterables() -> None:
    data = [1, [2, (3, [4, 5]), []], "py", [6]]
    assert list(flatten_nested_iterables(data)) == [1, 2, 3, 4, 5, "py", 6]


def check_atomic_dict_transaction() -> None:
    state = {"balance": 100}
    with AtomicDictTransaction(state) as tx:
        tx["balance"] = 150
        tx["status"] = "ok"
    assert state == {"balance": 150, "status": "ok"}

    try:
        with AtomicDictTransaction(state) as tx:
            tx["balance"] = 0
            raise RuntimeError("Fallo simulado")
    except RuntimeError:
        pass
    assert state == {"balance": 150, "status": "ok"}


def check_temporary_config_override() -> None:
    cfg = {"env": "prod", "debug": False}
    try:
        with temporary_config_override(cfg, debug=True, region="eu") as active:
            assert active == {"env": "prod", "debug": True, "region": "eu"}
            raise ValueError("Error dentro del bloque")
    except ValueError:
        pass
    assert cfg == {"env": "prod", "debug": False}


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. CountdownIterator", check_countdown_iterator),
    ("02. flatten_nested_iterables (yield from)", check_flatten_nested_iterables),
    ("03. AtomicDictTransaction (__enter__/__exit__)", check_atomic_dict_transaction),
    ("04. temporary_config_override (@contextmanager)", check_temporary_config_override),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 04_iterators_and_context_managers.py")
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
