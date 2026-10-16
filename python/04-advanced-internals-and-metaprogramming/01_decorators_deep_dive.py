from __future__ import annotations

import functools
import inspect
import sys
import time
from typing import Any, Callable, TypeVar

"""
MÓDULO 04 — INTERNALS Y METAPROGRAMACIÓN: 01. DECORADORES A FONDO
===============================================================================
Estudio profundo y práctica deliberada sobre funciones de orden superior,
decoradores que preservan metadatos (`@functools.wraps`), fábricas de
decoradores parametrizados, introspección de argumentos en tiempo de ejecución
(`inspect.signature`) y decoradores basados en clases.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Estructura de un Decorador Estándar:
   ```python
   def mi_decorador(fn: Callable[P, R]) -> Callable[P, R]:
       @functools.wraps(fn)  # Copia __name__, __doc__, __qualname__, __wrapped__
       def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
           return fn(*args, **kwargs)
       return wrapper
   ```

2. Fábrica de Decoradores Parametrizados (3 niveles de funciones):
   - `def retry(max_attempts: int = 3):` -> recibe la configuración y devuelve `decorador(fn)`.
   - `def decorador(fn):` -> recibe la función y devuelve `wrapper(*args, **kwargs)`.

3. Introspección con `inspect.signature`:
   - `sig = inspect.signature(fn)`
   - `bound = sig.bind(*args, **kwargs); bound.apply_defaults()`
   - `bound.arguments` es un diccionario ordenado `{nombre_param: valor}` que
     unifica argumentos posicionales, por nombre y por defecto.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- Si olvidas `@functools.wraps(fn)`, la función decorada pierde su `__name__`
  y `__doc__` originales (pasando a llamarse `"wrapper"`), lo que rompe
  herramientas como FastAPI, Sphinx o pytest.
"""

F = TypeVar("F", bound=Callable[..., Any])


def preserve_and_audit(audit_log: list[str]) -> Callable[[F], F]:
    """Fábrica de decorador que registra `f"{fn.__name__}:called"` y preserva metadatos con `@wraps`."""
    # BEGIN_SOLUTION
    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            audit_log.append(f"{fn.__name__}:called")
            return fn(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
    # END_SOLUTION


def retry_on_exception(
    max_attempts: int = 3,
    allowed_exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[F], F]:
    """Reintenta la función hasta `max_attempts` veces si lanza `allowed_exceptions`.

    Si falla en todos los intentos, relanza la última excepción capturada.
    Si `max_attempts <= 0`, lanza `ValueError`.
    """
    # BEGIN_SOLUTION
    if max_attempts <= 0:
        raise ValueError("max_attempts debe ser mayor a 0")

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: BaseException | None = None
            for _ in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except allowed_exceptions as exc:
                    last_exc = exc
            assert last_exc is not None
            raise last_exc

        return wrapper  # type: ignore[return-value]

    return decorator
    # END_SOLUTION


def enforce_non_negative_args(fn: F) -> F:
    """Valida mediante `inspect.signature` que ningún argumento `int`/`float` sea negativo.

    Inspecciona tanto argumentos posicionales como por nombre o valores por
    defecto (`bound.apply_defaults()`). Si algún argumento numérico (`int` o `float`,
    excluyendo `bool`) es `< 0`, lanza `ValueError(f"Argumento negativo: {name}")`.
    """
    # BEGIN_SOLUTION
    sig = inspect.signature(fn)

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        for name, val in bound.arguments.items():
            if isinstance(val, (int, float)) and not isinstance(val, bool) and val < 0:
                raise ValueError(f"Argumento negativo: {name}")
        return fn(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
    # END_SOLUTION


class CallCounterDecorator:
    """Decorador basado en clase que cuenta invocaciones en `self.call_count`."""

    def __init__(self, fn: Callable[..., Any]) -> None:
        # BEGIN_SOLUTION
        functools.update_wrapper(self, fn)
        self.fn = fn
        self.call_count = 0
        # END_SOLUTION

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        # BEGIN_SOLUTION
        self.call_count += 1
        return self.fn(*args, **kwargs)
        # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_preserve_and_audit() -> None:
    log: list[str] = []

    @preserve_and_audit(log)
    def compute_sum(a: int, b: int) -> int:
        """Suma dos enteros."""
        return a + b

    assert compute_sum(3, 4) == 7
    assert compute_sum.__name__ == "compute_sum"
    assert compute_sum.__doc__ == "Suma dos enteros."
    assert log == ["compute_sum:called"]


def check_retry_on_exception() -> None:
    attempts = 0

    @retry_on_exception(max_attempts=3, allowed_exceptions=(ConnectionError,))
    def flaky_service() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ConnectionError("Fallo temporal")
        return "conectado"

    assert flaky_service() == "conectado"
    assert attempts == 3


def check_enforce_non_negative_args() -> None:
    @enforce_non_negative_args
    def create_box(width: float, height: float = 1.0) -> float:
        return width * height

    assert create_box(5.0, height=2.0) == 10.0
    try:
        create_box(5.0, height=-1.0)
        raise AssertionError("Debió rechazar height negativo")
    except ValueError:
        pass


def check_call_counter_decorator() -> None:
    @CallCounterDecorator
    def greet(name: str) -> str:
        return f"Hola {name}"

    assert greet("Ada") == "Hola Ada"
    assert greet("Alan") == "Hola Alan"
    assert greet.call_count == 2


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. preserve_and_audit (@wraps)", check_preserve_and_audit),
    ("02. retry_on_exception (Parameterized)", check_retry_on_exception),
    ("03. enforce_non_negative_args (inspect.signature)", check_enforce_non_negative_args),
    ("04. CallCounterDecorator (Class Decorator)", check_call_counter_decorator),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 01_decorators_deep_dive.py")
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
