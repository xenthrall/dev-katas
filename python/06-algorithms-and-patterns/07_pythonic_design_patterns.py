from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import sys
import time
from typing import Any, Callable

"""
MÓDULO 06 — ALGORITMOS Y PATRONES: 07. PATRONES DE DISEÑO PYTHONIC
===============================================================================
Estudio profundo y práctica deliberada sobre cómo se implementan los patrones
de diseño de arquitectura en Python moderno sin caer en el "boilerplate" de
Java/C++: Strategy con Callables, Registry/Factory con decoradores, EventBus
(Observer) y Builder fluido.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Patrón Strategy Pythonic:
   - En lugar de crear una interfaz `IStrategy` y 5 subclases con un solo método,
     pasa directamente una función tipada `Callable[[float], float]`.
2. Patrón Registry / Factory:
   - Usa un diccionario `{nombre: funcion_o_clase}` poblado mediante un decorador
     `@register("formato")` eliminando bloques `if/elif/else` gigantes.
3. Patrón Observer / EventBus:
   - Un `defaultdict(list)` de suscriptores por tipo de evento.
4. Patrón Builder Fluido (`QueryBuilder`):
   - Métodos que configuran el estado y retornan `self` (o una nueva copia) para
     encadenar llamadas `.select(...).where(...).limit(...).build()`.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- Las funciones en Python son objetos de primera clase: úsalas como estrategias,
  fábricas y comandos ligeros siempre que no requieran estado complejo.
"""

DiscountStrategy = Callable[[float], float]


@dataclass
class CheckoutOrder:
    subtotal: float
    discount_strategy: DiscountStrategy = lambda amount: amount

    def final_total(self) -> float:
        """Aplica `discount_strategy` al `subtotal` garantizando un mínimo de `0.0`."""
        # BEGIN_SOLUTION
        discounted = self.discount_strategy(self.subtotal)
        return round(max(0.0, discounted), 2)
        # END_SOLUTION


class ExporterRegistry:
    """Registro/Fábrica de exportadores basado en decorador."""

    def __init__(self) -> None:
        self._exporters: dict[str, Callable[[dict[str, Any]], str]] = {}

    def register(
        self, fmt: str
    ) -> Callable[[Callable[[dict[str, Any]], str]], Callable[[dict[str, Any]], str]]:
        # BEGIN_SOLUTION
        def _decorator(
            fn: Callable[[dict[str, Any]], str],
        ) -> Callable[[dict[str, Any]], str]:
            self._exporters[fmt.strip().lower()] = fn
            return fn

        return _decorator
        # END_SOLUTION

    def export(self, fmt: str, data: dict[str, Any]) -> str:
        # BEGIN_SOLUTION
        key = fmt.strip().lower()
        if key not in self._exporters:
            raise KeyError(f"Formato no soportado: {fmt}")
        return self._exporters[key](data)
        # END_SOLUTION


class EventBus:
    """Bus de eventos síncrono (Patrón Observer / Pub-Sub)."""

    def __init__(self) -> None:
        # BEGIN_SOLUTION
        self._subscribers: defaultdict[str, list[Callable[[dict[str, Any]], None]]] = (
            defaultdict(list)
        )
        # END_SOLUTION

    def subscribe(
        self, event_type: str, handler: Callable[[dict[str, Any]], None]
    ) -> None:
        # BEGIN_SOLUTION
        self._subscribers[event_type].append(handler)
        # END_SOLUTION

    def publish(self, event_type: str, payload: dict[str, Any]) -> int:
        """Invoca todos los handlers suscritos a `event_type` y devuelve cuántos se ejecutaron."""
        # BEGIN_SOLUTION
        handlers = self._subscribers.get(event_type, [])
        for h in handlers:
            h(payload)
        return len(handlers)
        # END_SOLUTION


class SQLQueryBuilder:
    """Builder fluido para construir consultas SQL parametrizadas de forma determinista."""

    def __init__(self, table: str) -> None:
        self._table = table
        self._columns: list[str] = []
        self._wheres: list[str] = []
        self._limit_val: int | None = None

    def select(self, *columns: str) -> SQLQueryBuilder:
        # BEGIN_SOLUTION
        self._columns.extend(columns)
        return self
        # END_SOLUTION

    def where(self, condition: str) -> SQLQueryBuilder:
        # BEGIN_SOLUTION
        self._wheres.append(condition)
        return self
        # END_SOLUTION

    def limit(self, count: int) -> SQLQueryBuilder:
        # BEGIN_SOLUTION
        self._limit_val = int(count)
        return self
        # END_SOLUTION

    def build(self) -> str:
        # BEGIN_SOLUTION
        cols = ", ".join(self._columns) if self._columns else "*"
        parts = [f"SELECT {cols} FROM {self._table}"]
        if self._wheres:
            parts.append("WHERE " + " AND ".join(self._wheres))
        if self._limit_val is not None:
            parts.append(f"LIMIT {self._limit_val}")
        return " ".join(parts)
        # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_checkout_strategy() -> None:
    vip_discount: DiscountStrategy = lambda total: total * 0.8
    order = CheckoutOrder(200.0, discount_strategy=vip_discount)
    assert order.final_total() == 160.0


def check_exporter_registry() -> None:
    reg = ExporterRegistry()

    @reg.register("kv")
    def _to_kv(data: dict[str, Any]) -> str:
        return "&".join(f"{k}={v}" for k, v in sorted(data.items()))

    assert reg.export("KV", {"b": 2, "a": 1}) == "a=1&b=2"


def check_event_bus() -> None:
    bus = EventBus()
    received: list[str] = []
    bus.subscribe("USER_CREATED", lambda p: received.append(f"email:{p['user']}"))
    bus.subscribe("USER_CREATED", lambda p: received.append(f"audit:{p['user']}"))
    count = bus.publish("USER_CREATED", {"user": "ada"})
    assert count == 2
    assert received == ["email:ada", "audit:ada"]


def check_sql_query_builder() -> None:
    sql = (
        SQLQueryBuilder("users")
        .select("id", "email")
        .where("active = 1")
        .where("role = 'admin'")
        .limit(25)
        .build()
    )
    assert sql == "SELECT id, email FROM users WHERE active = 1 AND role = 'admin' LIMIT 25"


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. CheckoutOrder (Strategy Pattern)", check_checkout_strategy),
    ("02. ExporterRegistry (Registry/Factory)", check_exporter_registry),
    ("03. EventBus (Observer/PubSub)", check_event_bus),
    ("04. SQLQueryBuilder (Fluent Builder)", check_sql_query_builder),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 07_pythonic_design_patterns.py")
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
