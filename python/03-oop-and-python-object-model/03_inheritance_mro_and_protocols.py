from __future__ import annotations

from abc import ABC, abstractmethod
import sys
import time
from typing import Callable, Protocol, runtime_checkable

"""
MÓDULO 03 — POO Y MODELO DE OBJETOS: 03. HERENCIA, MRO C3, ABC Y PROTOCOL
===============================================================================
Estudio profundo y práctica deliberada sobre herencia múltiple cooperativa con
`super()`, el Orden de Resolución de Métodos (MRO C3), Clases Base Abstractas
(`abc.ABC`) y subtipado estructural (Duck Typing estático y en runtime) con
`typing.Protocol`.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. `super()` y el Algoritmo de Linealización C3 (`cls.__mro__`):
   - `super().metodo()` NO llama necesariamente a la clase padre directa; llama
     a la **siguiente clase en la lista `self.__class__.__mro__`**.
   - Permite componer Mixins cooperativos en cadena sin duplicar llamadas a la
     clase raíz en una jerarquía diamante.

2. Clases Base Abstractas (`abc.ABC` y `@abstractmethod` — Tipado Nominal):
   - Impiden instanciar la clase base directamente (`TypeError`).
   - Obligan a las subclases concretas a implementar todos los métodos decorados
     con `@abstractmethod`.

3. `typing.Protocol` y `@runtime_checkable` (Tipado Estructural):
   - No requiere que la clase herede explícitamente del protocolo. Si el objeto
     tiene los métodos/atributos requeridos, cumple el contrato.
   - Decorar el `Protocol` con `@runtime_checkable` permite usar `isinstance(obj, MiProtocolo)`.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- En jerarquías de Mixins (`class Servicio(AuthMixin, LogMixin, BaseService)`),
  el orden de las bases va de **más específico (izquierda)** a **más general (derecha)**.
"""


class BaseProcessor:
    def process(self, text: str) -> str:
        return text.strip()


class UppercaseMixin(BaseProcessor):
    def process(self, text: str) -> str:
        # BEGIN_SOLUTION
        return super().process(text).upper()
        # END_SOLUTION


class BracketWrapperMixin(BaseProcessor):
    def process(self, text: str) -> str:
        # BEGIN_SOLUTION
        return f"[{super().process(text)}]"
        # END_SOLUTION


class PipelineProcessor(BracketWrapperMixin, UppercaseMixin, BaseProcessor):
    """Combina los mixins cooperativamente mediante el MRO C3."""


def inspect_mro_class_names(cls: type) -> list[str]:
    """Devuelve la lista de nombres (`__name__`) en el `__mro__` de `cls` excluyendo `'object'`.

    Ejemplo:
        >>> inspect_mro_class_names(PipelineProcessor)
        ['PipelineProcessor', 'BracketWrapperMixin', 'UppercaseMixin', 'BaseProcessor']
    """
    # BEGIN_SOLUTION
    return [c.__name__ for c in cls.__mro__ if c is not object]
    # END_SOLUTION


class StorageBackend(ABC):
    """Contrato nominal abstracto para motores de almacenamiento."""

    @abstractmethod
    def save(self, key: str, value: str) -> None:
        """Guarda un valor asociado a `key`."""

    @abstractmethod
    def load(self, key: str) -> str | None:
        """Recupera el valor asociado a `key` o `None`."""


class InMemoryStorage(StorageBackend):
    """Implementación concreta en memoria de `StorageBackend`."""

    def __init__(self) -> None:
        # BEGIN_SOLUTION
        self._store: dict[str, str] = {}
        # END_SOLUTION

    def save(self, key: str, value: str) -> None:
        # BEGIN_SOLUTION
        self._store[key] = value
        # END_SOLUTION

    def load(self, key: str) -> str | None:
        # BEGIN_SOLUTION
        return self._store.get(key)
        # END_SOLUTION


@runtime_checkable
class HealthCheckable(Protocol):
    """Protocolo estructural verificable en runtime."""

    def health_status(self) -> tuple[bool, str]:
        ...


def collect_unhealthy_components(components: list[object]) -> list[str]:
    """Filtra objetos que cumplen `HealthCheckable` y devuelve los mensajes de los no saludables.

    Ignora cualquier objeto en `components` que no implemente `HealthCheckable`
    (verificado con `isinstance(comp, HealthCheckable)`).
    Si `comp.health_status()` devuelve `(False, reason)`, incluye `reason` en la salida.
    """
    # BEGIN_SOLUTION
    unhealthy: list[str] = []
    for comp in components:
        if isinstance(comp, HealthCheckable):
            ok, reason = comp.health_status()
            if not ok:
                unhealthy.append(reason)
    return unhealthy
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_cooperative_mro() -> None:
    proc = PipelineProcessor()
    assert proc.process("  hola mundo  ") == "[HOLA MUNDO]"
    assert inspect_mro_class_names(PipelineProcessor) == [
        "PipelineProcessor",
        "BracketWrapperMixin",
        "UppercaseMixin",
        "BaseProcessor",
    ]


def check_abc_storage() -> None:
    try:
        StorageBackend()  # type: ignore[abstract]
        raise AssertionError("No se debe poder instanciar una clase ABC abstracta")
    except TypeError:
        pass

    store = InMemoryStorage()
    store.save("k1", "v1")
    assert store.load("k1") == "v1"
    assert store.load("missing") is None


def check_structural_protocol() -> None:
    class RedisNode:
        def health_status(self) -> tuple[bool, str]:
            return (True, "redis:ok")

    class BrokenDB:
        def health_status(self) -> tuple[bool, str]:
            return (False, "postgres:connection_refused")

    class UnrelatedObject:
        pass

    items = [RedisNode(), BrokenDB(), UnrelatedObject()]
    assert collect_unhealthy_components(items) == ["postgres:connection_refused"]


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. Cooperative MRO & Mixins", check_cooperative_mro),
    ("02. Abstract Base Class (StorageBackend)", check_abc_storage),
    ("03. Runtime Protocol (HealthCheckable)", check_structural_protocol),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 03_inheritance_mro_and_protocols.py")
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
