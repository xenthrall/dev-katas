from __future__ import annotations

import sys
import time
from typing import Any, Callable

"""
MÓDULO 01 — SINTAXIS Y PRIMITIVAS: 06. FUNCIONES, ÁMBITOS (LEGB) Y CLOSURES
===============================================================================
Estudio profundo y práctica deliberada sobre el diseño de firmas de funciones
modernas (`/`, `*`, `*args`, `**kwargs`), la regla de resolución de nombres
LEGB, clausuras con estado encapsulado (`nonlocal`) y cómo evitar las trampas
clásicas de argumentos mutables por defecto y *late-binding* en bucles.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Anatomía Completa de una Firma en Python 3.8+:
   ```python
   def endpoint(pos1, pos2, /, estandar, *, kw_only1, kw_only2=True, **extras):
       ...
   ```
   - Antes de `/`: **Positional-only** (no pueden pasarse por nombre `pos1=...`).
   - Entre `/` y `*`: Pueden pasarse por posición o por palabra clave.
   - Después de `*`: **Keyword-only** (obligatorio pasarlos como `kw_only1=...`).
   - `*args`: Empaqueta argumentos posicionales adicionales en una `tuple`.
   - `**kwargs`: Empaqueta argumentos por nombre adicionales en un `dict[str, Any]`.

2. Regla de Resolución de Ámbitos LEGB:
   Python busca cualquier identificador en este orden estricto:
   - **L (Local):** Variables definidas dentro de la función actual.
   - **E (Enclosing):** Ámbito de funciones contenedoras (closures). Para
     reasignar una variable del ámbito envolvente se requiere `nonlocal var`.
   - **G (Global):** Nivel de módulo actual (`global var`).
   - **B (Built-in):** Nombres predefinidos de Python (`len`, `sum`, `ValueError`).

3. Closures (Clausuras Léxicas):
   - Una función interna que recuerda las variables libres de su ámbito
     envolvente (`__closure__`) incluso después de que la función externa ya
     terminó de ejecutarse.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- ❌ Trampa de Argumentos Mutables por Defecto:
  `def append_item(x, bucket=[]):` evalúa `[]` UNA sola vez al definir la función.
  ✅ Usa siempre `bucket: list | None = None` y crea la lista dentro con
  `if bucket is None: bucket = []`.
- ❌ Trampa de Late-Binding en Bucles:
  `[lambda x: x * i for i in range(4)]` captura la variable `i`, no su valor en
  cada paso; al final todas multiplican por `3`.
  ✅ Fija el valor de la iteración como default: `[lambda x, i=i: x * i for i in range(4)]`.
"""


def format_api_request(
    method: str,
    path: str,
    /,
    *,
    timeout: float = 5.0,
    retries: int = 0,
    **headers: str,
) -> dict[str, Any]:
    """Construye un descriptor de petición HTTP con firma estricta (`/`, `*`, `**headers`).

    - `method` y `path` deben ser **estrictamente posicionales** (`/`).
    - `timeout` y `retries` deben ser **estrictamente keyword-only** (`*`).
    - Cualquier keyword adicional en `**headers` se normaliza reemplazando `_`
      por `-` en el nombre de la cabecera y pasando a minúsculas.

    Ejemplo:
        >>> format_api_request("post", "/v1/orders", timeout=2.5, x_api_key="secret")
        {'endpoint': 'POST /v1/orders', 'timeout': 2.5, 'retries': 0, 'headers': {'x-api-key': 'secret'}}

    Complejidad objetivo:
        Tiempo: O(h) cabeceras | Espacio: O(h)

    Pista:
        Normaliza `method.strip().upper()` y transforma las claves de `headers`
        con `k.lower().replace("_", "-")`.
    """
    # BEGIN_SOLUTION
    normalized_headers = {k.lower().replace("_", "-"): v for k, v in headers.items()}
    return {
        "endpoint": f"{method.strip().upper()} {path.strip()}",
        "timeout": float(timeout),
        "retries": int(retries),
        "headers": normalized_headers,
    }
    # END_SOLUTION


def append_audit_event(
    event: str,
    history: list[str] | None = None,
) -> list[str]:
    """Agrega un evento a `history` evitando la trampa del argumento mutable por defecto.

    Si no se proporciona `history` (es `None`), debe crear y devolver una nueva
    lista con `event`. Si se proporciona una lista existente, muta y devuelve esa lista.

    Ejemplo:
        >>> append_audit_event("LOGIN")
        ['LOGIN']
        >>> append_audit_event("LOGOUT")
        ['LOGOUT']

    Complejidad objetivo:
        Tiempo: O(1) | Espacio: O(1)

    Pista:
        Verifica `if history is None: history = []` antes de hacer `.append(event)`.
    """
    # BEGIN_SOLUTION
    if history is None:
        history = []
    history.append(event)
    return history
    # END_SOLUTION


def make_stateful_accumulator(initial: int = 0) -> Callable[[int], tuple[int, int]]:
    """Crea una clausura con `nonlocal` que mantiene el total acumulado y el conteo de llamadas.

    Cada vez que se invoca la función retornada con `delta`:
    - Incrementa el contador de llamadas en 1.
    - Suma `delta` al total acumulado.
    - Devuelve la tupla `(total_actual, llamadas_totales)`.

    Ejemplo:
        >>> acc = make_stateful_accumulator(10)
        >>> acc(5)
        (15, 1)
        >>> acc(-3)
        (12, 2)

    Complejidad objetivo:
        Tiempo: O(1) por llamada | Espacio: O(1)

    Pista:
        Declara `total = initial` y `calls = 0` en la función externa, y usa
        `nonlocal total, calls` en la función interna.
    """
    # BEGIN_SOLUTION
    total = initial
    calls = 0

    def _step(delta: int) -> tuple[int, int]:
        nonlocal total, calls
        calls += 1
        total += delta
        return (total, calls)

    return _step
    # END_SOLUTION


def build_multiplier_pipeline(factors: list[int]) -> list[Callable[[int], int]]:
    """Crea una lista de funciones multiplicadoras evitando el bug de late-binding.

    La función en el índice `k` debe multiplicar su entrada `x` por `factors[k]`.

    Ejemplo:
        >>> fns = build_multiplier_pipeline([2, 5, 10])
        >>> [fn(3) for fn in fns]
        [6, 15, 30]

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Enlaza el factor de cada iteración como valor por defecto de la lambda:
        `lambda x, f=factor: x * f`.
    """
    # BEGIN_SOLUTION
    return [lambda x, f=factor: x * f for factor in factors]
    # END_SOLUTION


def compose_functions(*functions: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Compone un número arbitrario de funciones aplicándolas de izquierda a derecha (pipeline).

    Si no se pasan funciones, devuelve la función identidad `lambda x: x`.

    Ejemplo:
        >>> pipe = compose_functions(str.strip, str.upper, lambda s: f"[{s}]")
        >>> pipe("  hola  ")
        '[HOLA]'

    Complejidad objetivo:
        Tiempo: O(k) funciones por llamada | Espacio: O(1)

    Pista:
        Define una función interna `_pipeline(value)` que recorra `for fn in functions:`
        reasignando `value = fn(value)`.
    """
    # BEGIN_SOLUTION
    def _pipeline(value: Any) -> Any:
        result = value
        for fn in functions:
            result = fn(result)
        return result

    return _pipeline
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_format_api_request() -> None:
    res = format_api_request(
        "post",
        "/v1/orders",
        timeout=2.5,
        retries=3,
        x_api_key="abc",
        content_type="application/json",
    )
    assert res == {
        "endpoint": "POST /v1/orders",
        "timeout": 2.5,
        "retries": 3,
        "headers": {"x-api-key": "abc", "content-type": "application/json"},
    }
    # Verificar que method y path son estrictamente posicionales
    try:
        format_api_request(method="GET", path="/")  # type: ignore[misc]
        raise AssertionError("method y path deben ser positional-only (/)")
    except TypeError:
        pass


def check_append_audit_event() -> None:
    first = append_audit_event("START")
    second = append_audit_event("STOP")
    assert first == ["START"]
    assert second == ["STOP"]
    assert first is not second

    custom = ["INIT"]
    assert append_audit_event("NEXT", custom) == ["INIT", "NEXT"]


def check_make_stateful_accumulator() -> None:
    acc1 = make_stateful_accumulator(100)
    acc2 = make_stateful_accumulator(0)
    assert acc1(20) == (120, 1)
    assert acc1(-50) == (70, 2)
    assert acc2(5) == (5, 1)


def check_build_multiplier_pipeline() -> None:
    fns = build_multiplier_pipeline([2, 5, 10])
    assert [fn(4) for fn in fns] == [8, 20, 40]


def check_compose_functions() -> None:
    pipe = compose_functions(str.strip, str.upper, lambda s: f"<{s}>")
    assert pipe("  python ") == "<PYTHON>"
    identity = compose_functions()
    assert identity(99) == 99


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. format_api_request", check_format_api_request),
    ("02. append_audit_event", check_append_audit_event),
    ("03. make_stateful_accumulator", check_make_stateful_accumulator),
    ("04. build_multiplier_pipeline", check_build_multiplier_pipeline),
    ("05. compose_functions", check_compose_functions),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 06_functions_scopes_and_closures.py")
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
