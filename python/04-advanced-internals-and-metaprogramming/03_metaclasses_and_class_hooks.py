from __future__ import annotations

import sys
import time
from typing import Any, Callable

"""
MÓDULO 04 — INTERNALS Y METAPROGRAMACIÓN: 03. METACLASES Y HOOKS DE CLASE
===============================================================================
Estudio profundo y práctica deliberada sobre el modelo de creación de clases
en Python (`type`), el hook moderno `__init_subclass__` (PEP 487), metaclases
personalizadas (`type.__new__`, `type.__call__`) y creación dinámica de clases.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. En Python, las Clases son Objetos Instanciados por `type`:
   - `isinstance(MiClase, type) == True`.
   - Crear una clase dinámicamente sin usar la palabra clave `class`:
     `NuevaClase = type("NuevaClase", (ClaseBase,), {"atributo": 42})`

2. `__init_subclass__(cls, **kwargs)` (PEP 487 — Alternativa limpia a Metaclases):
   - Se ejecuta automáticamente en la clase base cada vez que se define una
     subclase suya. Ideal para auto-registro de plugins y validación de contratos.

3. Metaclases (`class MiMeta(type):`):
   - `__new__(mcls, name, bases, namespace)`: Intercepta la construcción de la
     clase antes de que exista en memoria.
   - `__call__(cls, *args, **kwargs)`: Intercepta la instanciación `MiClase()`
     (ideal para controlar cachés de instancias o Singletons).

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- Regla de Tim Peters sobre Metaclases: Si puedes resolver el problema con
  `__init_subclass__` o un decorador de clase, prefiérelos antes que una
  metaclase completa.
"""


class PluginBase:
    """Clase base que registra automáticamente subclases mediante `__init_subclass__`."""

    registry: dict[str, type[PluginBase]] = {}

    def __init_subclass__(cls, *, plugin_name: str | None = None, **kwargs: Any) -> None:
        # BEGIN_SOLUTION
        super().__init_subclass__(**kwargs)
        key = plugin_name or cls.__name__.lower()
        PluginBase.registry[key] = cls
        # END_SOLUTION


class SingletonMeta(type):
    """Metaclase que garantiza una única instancia por clase interceptando `__call__`."""

    _instances: dict[type, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        # BEGIN_SOLUTION
        if cls not in SingletonMeta._instances:
            SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]
        # END_SOLUTION


class UppercaseConstantsMeta(type):
    """Metaclase que convierte a MAYÚSCULAS todo atributo de clase público no invocable."""

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ) -> UppercaseConstantsMeta:
        # BEGIN_SOLUTION
        transformed: dict[str, Any] = {}
        for attr_name, val in namespace.items():
            if not attr_name.startswith("_") and not callable(val):
                transformed[attr_name.upper()] = val
            else:
                transformed[attr_name] = val
        return super().__new__(mcls, name, bases, transformed)
        # END_SOLUTION


def create_dynamic_record_class(class_name: str, defaults: dict[str, Any]) -> type:
    """Crea dinámicamente una clase con `type(name, bases, namespace)` que inicializa `defaults`."""
    # BEGIN_SOLUTION
    def _init(self: Any, **kwargs: Any) -> None:
        for k, default_val in defaults.items():
            setattr(self, k, kwargs.get(k, default_val))

    namespace = {"__init__": _init, **defaults}
    return type(class_name, (object,), namespace)
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_plugin_init_subclass() -> None:
    PluginBase.registry.clear()

    class StripeGateway(PluginBase, plugin_name="stripe"):
        pass

    class PaypalGateway(PluginBase):
        pass

    assert PluginBase.registry["stripe"] is StripeGateway
    assert PluginBase.registry["paypalgateway"] is PaypalGateway


def check_singleton_meta() -> None:
    class AppState(metaclass=SingletonMeta):
        def __init__(self, env: str) -> None:
            self.env = env

    s1 = AppState("prod")
    s2 = AppState("dev")
    assert s1 is s2
    assert s2.env == "prod"


def check_uppercase_constants_meta() -> None:
    class HttpConfig(metaclass=UppercaseConstantsMeta):
        default_port = 8080
        host = "localhost"

        def ping(self) -> str:
            return "pong"

    assert hasattr(HttpConfig, "DEFAULT_PORT") and HttpConfig.DEFAULT_PORT == 8080
    assert hasattr(HttpConfig, "HOST") and HttpConfig.HOST == "localhost"
    assert not hasattr(HttpConfig, "default_port")
    assert HttpConfig().ping() == "pong"


def check_create_dynamic_record_class() -> None:
    UserRecord = create_dynamic_record_class("UserRecord", {"role": "viewer", "active": True})
    u = UserRecord(role="admin")
    assert type(u).__name__ == "UserRecord"
    assert u.role == "admin"
    assert u.active is True


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. PluginBase (__init_subclass__)", check_plugin_init_subclass),
    ("02. SingletonMeta (Metaclass __call__)", check_singleton_meta),
    ("03. UppercaseConstantsMeta (Metaclass __new__)", check_uppercase_constants_meta),
    ("04. create_dynamic_record_class (type())", check_create_dynamic_record_class),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 03_metaclasses_and_class_hooks.py")
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
