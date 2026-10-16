from __future__ import annotations

import functools
import sys
import time
from typing import Any, Callable

"""
MÓDULO 03 — POO Y MODELO DE OBJETOS: 02. MÉTODOS MÁGICOS (DUNDERS)
===============================================================================
Estudio profundo y práctica deliberada sobre el modelo de datos de Python
(Data Model): representación (`__repr__`, `__str__`), igualdad y hashing
(`__eq__`, `__hash__`), ordenamiento total (`@functools.total_ordering`),
sobrecarga de operadores (`__add__`, `__mul__`), contenedores indexables
(`__len__`, `__getitem__`, `__contains__`) y objetos invocables (`__call__`).

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Representación e Igualdad/Hash:
   - `__repr__(self) -> str`: Representación inequívoca para desarrolladores/logs.
   - `__eq__(self, other: object) -> bool`: Si `other` no es del tipo compatible,
     devuelve `NotImplemented` (NO `False` directamente, para permitir que Python
     intente el método reflejado del otro operando).
   - `__hash__(self) -> int`: Si defines `__eq__`, Python desactiva `__hash__`
     (`__hash__ = None`) a menos que lo implementes explícitamente (solo en
     objetos inmutables) usando `hash((self.a, self.b))`.

2. Ordenamiento Total (`@functools.total_ordering`):
   - Si implementas `__eq__` y UN método de orden (`__lt__`), el decorador
     `@functools.total_ordering` genera automáticamente `<=`, `>`, `>=`.

3. Protocolo de Secuencia (`__len__`, `__getitem__`, `__contains__`):
   - `__getitem__(self, index: int | slice)` puede recibir un `int` o un objeto
     `slice(start, stop, step)` cuando el usuario hace `contenedor[1:4]`.

4. Objetos Invocables (`__call__`):
   - Definir `__call__(self, ...)` permite usar una instancia como si fuera una
     función con estado propio.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- Contrato Hash/Igualdad: Si `a == b`, es OBLIGATORIO que `hash(a) == hash(b)`.
  Nunca incluyas atributos mutables en el cálculo de `__hash__`.
"""


@functools.total_ordering
class SemanticVersion:
    """Versión semántica `major.minor.patch` inmutable, ordenable y hashable."""

    def __init__(self, major: int, minor: int, patch: int) -> None:
        # BEGIN_SOLUTION
        if major < 0 or minor < 0 or patch < 0:
            raise ValueError("Los componentes de versión no pueden ser negativos")
        self.major = int(major)
        self.minor = int(minor)
        self.patch = int(patch)
        # END_SOLUTION

    def __repr__(self) -> str:
        # BEGIN_SOLUTION
        return f"SemanticVersion({self.major}, {self.minor}, {self.patch})"
        # END_SOLUTION

    def __str__(self) -> str:
        # BEGIN_SOLUTION
        return f"{self.major}.{self.minor}.{self.patch}"
        # END_SOLUTION

    def __eq__(self, other: object) -> bool:
        # BEGIN_SOLUTION
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return (self.major, self.minor, self.patch) == (
            other.major,
            other.minor,
            other.patch,
        )
        # END_SOLUTION

    def __lt__(self, other: object) -> bool:
        # BEGIN_SOLUTION
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )
        # END_SOLUTION

    def __hash__(self) -> int:
        # BEGIN_SOLUTION
        return hash((self.major, self.minor, self.patch))
        # END_SOLUTION


class Vector2D:
    """Vector matemático 2D con sobrecarga de suma (`+`), escalado (`*`) y verdad (`bool`)."""

    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other: object) -> Vector2D:
        # BEGIN_SOLUTION
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x + other.x, self.y + other.y)
        # END_SOLUTION

    def __mul__(self, scalar: float | int) -> Vector2D:
        # BEGIN_SOLUTION
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector2D(self.x * scalar, self.y * scalar)
        # END_SOLUTION

    def __rmul__(self, scalar: float | int) -> Vector2D:
        # BEGIN_SOLUTION
        return self.__mul__(scalar)
        # END_SOLUTION

    def __bool__(self) -> bool:
        # BEGIN_SOLUTION
        return self.x != 0.0 or self.y != 0.0
        # END_SOLUTION

    def __eq__(self, other: object) -> bool:
        # BEGIN_SOLUTION
        if not isinstance(other, Vector2D):
            return NotImplemented
        return self.x == other.x and self.y == other.y
        # END_SOLUTION


class PlaylistContainer:
    """Contenedor indexable que soporta `len()`, indexación, slicing (`[:]`) e `in`."""

    def __init__(self, tracks: list[str]) -> None:
        self._tracks = list(tracks)

    def __len__(self) -> int:
        # BEGIN_SOLUTION
        return len(self._tracks)
        # END_SOLUTION

    def __getitem__(self, index: int | slice) -> str | PlaylistContainer:
        """Si `index` es `slice`, devuelve un nuevo `PlaylistContainer`; si es `int`, el `str`."""
        # BEGIN_SOLUTION
        if isinstance(index, slice):
            return PlaylistContainer(self._tracks[index])
        return self._tracks[index]
        # END_SOLUTION

    def __contains__(self, item: object) -> bool:
        """Búsqueda case-insensitive por título de canción."""
        # BEGIN_SOLUTION
        if not isinstance(item, str):
            return False
        target = item.strip().lower()
        return any(t.strip().lower() == target for t in self._tracks)
        # END_SOLUTION


class StatefulThresholdFilter:
    """Objeto invocable (`__call__`) que filtra números >= `threshold` y cuenta cuántos aceptó."""

    def __init__(self, threshold: float) -> None:
        # BEGIN_SOLUTION
        self.threshold = float(threshold)
        self.accepted_count = 0
        # END_SOLUTION

    def __call__(self, value: float) -> bool:
        # BEGIN_SOLUTION
        if value >= self.threshold:
            self.accepted_count += 1
            return True
        return False
        # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_semantic_version() -> None:
    v1 = SemanticVersion(1, 2, 0)
    v2 = SemanticVersion(1, 10, 0)
    v3 = SemanticVersion(1, 2, 0)
    assert str(v1) == "1.2.0"
    assert repr(v1) == "SemanticVersion(1, 2, 0)"
    assert v1 == v3
    assert v1 < v2
    assert v2 >= v1
    assert len({v1, v2, v3}) == 2


def check_vector_2d() -> None:
    a = Vector2D(2, 3)
    b = Vector2D(4, -1)
    assert (a + b) == Vector2D(6, 2)
    assert (a * 3) == Vector2D(6, 9)
    assert (3 * a) == Vector2D(6, 9)
    assert bool(a) is True
    assert bool(Vector2D(0, 0)) is False


def check_playlist_container() -> None:
    pl = PlaylistContainer(["Intro", "Climax", "Outro"])
    assert len(pl) == 3
    assert pl[1] == "Climax"
    sub = pl[:2]
    assert isinstance(sub, PlaylistContainer) and len(sub) == 2
    assert "climax" in pl
    assert "Unknown" not in pl


def check_stateful_threshold_filter() -> None:
    f = StatefulThresholdFilter(10.0)
    kept = [x for x in [4.0, 10.0, 15.5, 2.0, 20.0] if f(x)]
    assert kept == [10.0, 15.5, 20.0]
    assert f.accepted_count == 3


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. SemanticVersion", check_semantic_version),
    ("02. Vector2D", check_vector_2d),
    ("03. PlaylistContainer", check_playlist_container),
    ("04. StatefulThresholdFilter", check_stateful_threshold_filter),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 02_dunder_magic_methods.py")
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
