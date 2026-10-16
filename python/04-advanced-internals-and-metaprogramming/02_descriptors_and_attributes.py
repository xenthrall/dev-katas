from __future__ import annotations

import sys
import time
from typing import Any, Callable

"""
MÓDULO 04 — INTERNALS Y METAPROGRAMACIÓN: 02. DESCRIPTORES Y BÚSQUEDA DE ATRIBUTOS
===============================================================================
Estudio profundo y práctica deliberada sobre el protocolo Descriptor
(`__set_name__`, `__get__`, `__set__`), la cadena de prioridad en la búsqueda
de atributos (`obj.attr`), propiedades perezosas (`LazyProperty`) y los hooks
`__getattr__` vs `__getattribute__`.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Protocolo Descriptor (La base de `@property`, métodos, `classmethod` y ORMs):
   - **Data Descriptor** (define `__get__` y `__set__`): Tiene **MÁXIMA prioridad**
     (incluso por encima de `instance.__dict__`).
   - **Non-Data Descriptor** (solo define `__get__`): Tiene **MENOR prioridad**
     que `instance.__dict__`. Esto permite crear un `@LazyProperty` que calcula
     el valor la primera vez y lo guarda en `instance.__dict__[self.name]`, de
     modo que las lecturas futuras van directo al diccionario en O(1).

2. Cadena de Resolución de `obj.x` en CPython (`object.__getattribute__`):
   1. Data Descriptors en `type(obj).__mro__`.
   2. Diccionario de la instancia `obj.__dict__["x"]`.
   3. Non-Data Descriptors y atributos de clase en `type(obj).__mro__`.
   4. Fallback `__getattr__(self, name)` (solo se invoca si todo lo anterior falló).

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- ❌ Nunca guardes el valor de una instancia en `self.value` dentro del propio
  Descriptor, porque el descriptor es un atributo de CLASE compartido por todas
  las instancias. Guárdalo en `instance.__dict__[self.storage_name]`.
- En `__getattribute__`, usar `self.x` provoca recursión infinita (`RecursionError`).
  Delega siempre a `super().__getattribute__(name)`.
"""


class BoundedNumber:
    """Data Descriptor que valida que un atributo numérico esté en `[min_val, max_val]`."""

    def __init__(self, min_val: float, max_val: float) -> None:
        self.min_val = float(min_val)
        self.max_val = float(max_val)
        self.attr_name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        # BEGIN_SOLUTION
        self.attr_name = name
        # END_SOLUTION

    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        # BEGIN_SOLUTION
        if instance is None:
            return self
        return instance.__dict__.get(self.attr_name)
        # END_SOLUTION

    def __set__(self, instance: Any, value: float | int) -> None:
        # BEGIN_SOLUTION
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError(f"{self.attr_name} debe ser numérico")
        val = float(value)
        if not (self.min_val <= val <= self.max_val):
            raise ValueError(
                f"{self.attr_name} debe estar entre {self.min_val} y {self.max_val}"
            )
        instance.__dict__[self.attr_name] = val
        # END_SOLUTION


class LazyProperty:
    """Non-Data Descriptor que evalúa `fn(instance)` una sola vez y cachea en `__dict__`."""

    def __init__(self, fn: Callable[[Any], Any]) -> None:
        self.fn = fn
        self.attr_name = fn.__name__

    def __set_name__(self, owner: type, name: str) -> None:
        # BEGIN_SOLUTION
        self.attr_name = name
        # END_SOLUTION

    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        # BEGIN_SOLUTION
        if instance is None:
            return self
        value = self.fn(instance)
        instance.__dict__[self.attr_name] = value
        return value
        # END_SOLUTION


class DynamicConfigNode:
    """Permite leer claves de un diccionario interno como atributos vía `__getattr__`."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def __getattr__(self, name: str) -> Any:
        """Devuelve `self._data[name]` o lanza `AttributeError` si no existe."""
        # BEGIN_SOLUTION
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"Atributo {name!r} no encontrado")
        # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_bounded_number_descriptor() -> None:
    class ServerConfig:
        cpu_Target = BoundedNumber(0.0, 100.0)

        def __init__(self, cpu: float) -> None:
            self.cpu_Target = cpu

    s1 = ServerConfig(75.0)
    s2 = ServerConfig(20.0)
    assert s1.cpu_Target == 75.0
    assert s2.cpu_Target == 20.0
    try:
        s1.cpu_Target = 150.0
        raise AssertionError("Debió lanzar ValueError por exceder 100.0")
    except ValueError:
        pass


def check_lazy_property() -> None:
    eval_count = 0

    class Report:
        @LazyProperty
        def heavy_summary(self) -> str:
            nonlocal eval_count
            eval_count += 1
            return "RESUMEN_CALCULADO"

    rep = Report()
    assert rep.heavy_summary == "RESUMEN_CALCULADO"
    assert rep.heavy_summary == "RESUMEN_CALCULADO"
    assert eval_count == 1
    assert "heavy_summary" in rep.__dict__


def check_dynamic_config_node() -> None:
    node = DynamicConfigNode({"host": "db.local", "port": 5432})
    assert node.host == "db.local"
    assert node.port == 5432
    try:
        _ = node.missing_key
        raise AssertionError("Debió lanzar AttributeError")
    except AttributeError:
        pass


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. BoundedNumber (Data Descriptor)", check_bounded_number_descriptor),
    ("02. LazyProperty (Non-Data Descriptor)", check_lazy_property),
    ("03. DynamicConfigNode (__getattr__)", check_dynamic_config_node),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 02_descriptors_and_attributes.py")
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
