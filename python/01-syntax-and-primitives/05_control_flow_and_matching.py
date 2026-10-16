from __future__ import annotations

import sys
import time
from typing import Any, Callable

"""
MÓDULO 01 — SINTAXIS Y PRIMITIVAS: 05. CONTROL DE FLUJO Y PATTERN MATCHING
===============================================================================
Estudio profundo y práctica deliberada sobre Structural Pattern Matching
(`match`/`case` - PEP 634), el operador de expresión de asignación Walrus (`:=`),
la cláusula `for...else` y el manejo estructurado de excepciones con
encadenamiento explícito (`raise ... from err`).

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Structural Pattern Matching (`match` / `case` — Python 3.10+):
   - Desestructura secuencias, diccionarios y objetos simultáneamente:
     ```python
     match comando:
         case ["MOVE", int(x), int(y)] if x >= 0 and y >= 0:
             ...
         case {"op": "ADD" | "SUB" as op, "values": [primero, *resto]}:
             ...
         case _:
             ...  # Comodín por defecto (default)
     ```
   - Los patrones de mapeo (`{"k": v}`) hacen coincidencia parcial (ignoran claves
     extra a menos que las captures con `**rest`).

2. Operador Walrus (`:=` — PEP 572):
   - Asigna y devuelve el valor dentro de una misma expresión (`if`, `while`,
     comprehension):
     ```python
     if (n := len(datos)) > 10:
         print(f"Lote grande de {n} elementos")
     ```

3. Cláusula `for ... else` y `while ... else`:
   - El bloque `else:` se ejecuta **SOLO si el bucle terminó de forma natural**
     (es decir, si NUNCA se ejecutó un `break`). Es ideal para búsquedas sin
     variables bandera (`encontrado = False`).

4. Jerarquía y Encadenamiento de Excepciones:
   - `try:` / `except TipoError as err:` / `else:` (corre si no hubo excepción)
     / `finally:` (corre siempre).
   - `raise ConfigError("Fallo al cargar") from err`: Preserva el traceback
     original en ` exc.__cause__`.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- En `match`/`case`, un nombre de variable suelto como `case x:` NO compara con
  una variable externa llamada `x`, sino que **captura cualquier valor** y lo
  asigna a `x` (igual que `_`, pero guardándolo). Para comparar con constantes,
  usa literales o atributos con punto (`Color.RED`).
- El operador Walrus `:=` tiene menor precedencia que los operadores de
  comparación: escribe siempre `if (val := calcular()) > 0:` con paréntesis.
"""


class ConfigurationError(Exception):
    """Error de dominio para configuraciones inválidas."""


def evaluate_command_event(event: Any) -> str:
    """Evalúa un evento heterogéneo usando Structural Pattern Matching (`match`/`case`).

    Reglas de coincidencia en orden:
    1. Diccionario `{"type": "PAYMENT", "amount": int() | float() as amt, "currency": str(curr)}`
       con guarda `if amt > 0`: devuelve `f"PAY:{amt:.2f}:{curr.upper()}"`.
    2. Diccionario `{"type": "PAYMENT", "amount": amt}` con `amt <= 0`:
       devuelve `"INVALID_AMOUNT"`.
    3. Secuencia (lista o tupla) `["SSH" | "RDP" as proto, str(host), int(port)]`
       con guarda `if 1 <= port <= 65535`: devuelve `f"CONNECT:{proto}://{host}:{port}"`.
    4. Secuencia `["PING", *targets]` con al menos 1 destino (`if len(targets) > 0`):
       devuelve `f"PINGING:{len(targets)}"`.
    5. Cualquier otro caso: devuelve `"UNKNOWN_EVENT"`.

    Ejemplo:
        >>> evaluate_command_event({"type": "PAYMENT", "amount": 49.5, "currency": "usd"})
        'PAY:49.50:USD'
        >>> evaluate_command_event(["SSH", "10.0.0.5", 22])
        'CONNECT:SSH://10.0.0.5:22'

    Complejidad objetivo:
        Tiempo: O(1) | Espacio: O(1)

    Pista:
        Usa `match event:` con patrones de diccionario, patrones OR (`|`), captura `as` y guardas `if`.
    """
    # BEGIN_SOLUTION
    match event:
        case {"type": "PAYMENT", "amount": int() | float() as amt, "currency": str(curr)} if amt > 0:
            return f"PAY:{amt:.2f}:{curr.upper()}"
        case {"type": "PAYMENT", "amount": int() | float() as amt} if amt <= 0:
            return "INVALID_AMOUNT"
        case ["SSH" | "RDP" as proto, str(host), int(port)] if 1 <= port <= 65535:
            return f"CONNECT:{proto}://{host}:{port}"
        case ["PING", *targets] if len(targets) > 0:
            return f"PINGING:{len(targets)}"
        case _:
            return "UNKNOWN_EVENT"
    # END_SOLUTION


def filter_and_transform_with_walrus(
    raw_tokens: list[str], min_square: int
) -> list[int]:
    """Limpia cadenas numéricas y devuelve sus cuadrados >= `min_square` usando `:=`.

    Para cada cadena en `raw_tokens`:
    - Quita espacios con `.strip()`.
    - Si representa un entero positivo o negativo válido (opcionalmente precedido por `-`),
      calcula su cuadrado `sq = int(clean) ** 2`.
    - Incluye `sq` solo si `sq >= min_square`.

    Ejemplo:
        >>> filter_and_transform_with_walrus([" 3 ", "-5", "abc", "8", " 2 "], min_square=20)
        [25, 64]

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Usa una list comprehension con `(clean := s.strip())` y `(sq := int(clean) ** 2) >= min_square`.
    """
    # BEGIN_SOLUTION
    return [
        sq
        for s in raw_tokens
        if (clean := s.strip()).lstrip("-").isdigit()
        and (sq := int(clean) ** 2) >= min_square
    ]
    # END_SOLUTION


def classify_numbers_prime_or_factor(numbers: list[int]) -> list[str]:
    """Clasifica cada entero >= 2 como `'PRIMO:<n>'` o `'COMPUESTO:<n>:<menor_divisor>'`.

    Usa la estructura `for divisor in range(2, int(n**0.5) + 1): ... else:`
    para distinguir primos sin emplear variables booleanas auxiliares.
    Ignora números menores a 2.

    Ejemplo:
        >>> classify_numbers_prime_or_factor([2, 9, 13, 15, 1])
        ['PRIMO:2', 'COMPUESTO:9:3', 'PRIMO:13', 'COMPUESTO:15:3']

    Complejidad objetivo:
        Tiempo: O(n * sqrt(max_val)) | Espacio: O(n)

    Pista:
        Si `n % d == 0`, agrega `f"COMPUESTO:{n}:{d}"` y haz `break`. En el `else:`
        del bucle interno, agrega `f"PRIMO:{n}"`.
    """
    # BEGIN_SOLUTION
    results: list[str] = []
    for n in numbers:
        if n < 2:
            continue
        for d in range(2, int(n**0.5) + 1):
            if n % d == 0:
                results.append(f"COMPUESTO:{n}:{d}")
                break
        else:
            results.append(f"PRIMO:{n}")
    return results
    # END_SOLUTION


def parse_port_setting(config: dict[str, str], key: str = "PORT") -> int:
    """Extrae y valida un puerto TCP desde `config` encadenando excepciones de dominio.

    Reglas:
    - Si `key` no existe en `config`, lanza `ConfigurationError(f"Falta la clave {key}")`
      encadenando la `KeyError` original con `from err`.
    - Si el valor no puede convertirse a `int`, lanza `ConfigurationError("Puerto no numérico")`
      encadenando el `ValueError` original con `from err`.
    - Si el entero no está en `1 <= port <= 65535`, lanza
      `ConfigurationError("Puerto fuera de rango")`.

    Ejemplo:
        >>> parse_port_setting({"PORT": "8080"})
        8080

    Complejidad objetivo:
        Tiempo: O(1) | Espacio: O(1)

    Pista:
        Usa `try: raw = config[key]` y `port = int(raw)` capturando `KeyError` y
        `ValueError` por separado y usando `raise ConfigurationError(...) from err`.
    """
    # BEGIN_SOLUTION
    try:
        raw = config[key]
    except KeyError as err:
        raise ConfigurationError(f"Falta la clave {key}") from err

    try:
        port = int(raw)
    except ValueError as err:
        raise ConfigurationError("Puerto no numérico") from err

    if not (1 <= port <= 65535):
        raise ConfigurationError("Puerto fuera de rango")
    return port
    # END_SOLUTION


def simplify_ast_expr(node: Any) -> int:
    """Evalúa recursivamente un árbol de expresión aritmética representado con tuplas/dicts.

    Formatos soportados mediante `match`/`case`:
    - `int(val)`: devuelve `val`.
    - `("NEG", sub)`: devuelve `-simplify_ast_expr(sub)`.
    - `("ADD", left, right)`: devuelve suma de ambos subárboles.
    - `("MUL", left, right)`: devuelve producto de ambos subárboles.
    - Cualquier otro nodo lanza `ValueError("Nodo AST inválido")`.

    Ejemplo:
        >>> simplify_ast_expr(("MUL", ("ADD", 2, 3), ("NEG", 4)))
        -20

    Complejidad objetivo:
        Tiempo: O(nodos) | Espacio: O(altura)

    Pista:
        Usa `match node:` desestructurando recursivamente las tuplas de 2 y 3 elementos.
    """
    # BEGIN_SOLUTION
    match node:
        case int(val):
            return val
        case ("NEG", sub):
            return -simplify_ast_expr(sub)
        case ("ADD", left, right):
            return simplify_ast_expr(left) + simplify_ast_expr(right)
        case ("MUL", left, right):
            return simplify_ast_expr(left) * simplify_ast_expr(right)
        case _:
            raise ValueError(f"Nodo AST inválido: {node!r}")
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_evaluate_command_event() -> None:
    assert evaluate_command_event({"type": "PAYMENT", "amount": 49.5, "currency": "usd"}) == "PAY:49.50:USD"
    assert evaluate_command_event({"type": "PAYMENT", "amount": 0, "currency": "eur"}) == "INVALID_AMOUNT"
    assert evaluate_command_event(["SSH", "10.0.0.5", 22]) == "CONNECT:SSH://10.0.0.5:22"
    assert evaluate_command_event(["RDP", "server.local", 70000]) == "UNKNOWN_EVENT"
    assert evaluate_command_event(["PING", "8.8.8.8", "1.1.1.1"]) == "PINGING:2"
    assert evaluate_command_event(["PING"]) == "UNKNOWN_EVENT"


def check_filter_and_transform_with_walrus() -> None:
    assert filter_and_transform_with_walrus([" 3 ", "-5", "abc", "8", " 2 ", "-10"], 20) == [25, 64, 100]
    assert filter_and_transform_with_walrus(["x", ""], 1) == []


def check_classify_numbers_prime_or_factor() -> None:
    assert classify_numbers_prime_or_factor([0, 1, 2, 9, 13, 15, 29, 49]) == [
        "PRIMO:2",
        "COMPUESTO:9:3",
        "PRIMO:13",
        "COMPUESTO:15:3",
        "PRIMO:29",
        "COMPUESTO:49:7",
    ]


def check_parse_port_setting() -> None:
    assert parse_port_setting({"PORT": "8080"}) == 8080
    try:
        parse_port_setting({})
        raise AssertionError("Debió lanzar ConfigurationError por clave faltante")
    except ConfigurationError as exc:
        assert isinstance(exc.__cause__, KeyError)

    try:
        parse_port_setting({"PORT": "abc"})
        raise AssertionError("Debió lanzar ConfigurationError por valor no numérico")
    except ConfigurationError as exc:
        assert isinstance(exc.__cause__, ValueError)

    try:
        parse_port_setting({"PORT": "99999"})
        raise AssertionError("Debió lanzar ConfigurationError por rango")
    except ConfigurationError:
        pass


def check_simplify_ast_expr() -> None:
    expr = ("MUL", ("ADD", 2, 3), ("NEG", 4))
    assert simplify_ast_expr(expr) == -20
    assert simplify_ast_expr(42) == 42


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. evaluate_command_event", check_evaluate_command_event),
    ("02. filter_and_transform_with_walrus", check_filter_and_transform_with_walrus),
    ("03. classify_numbers_prime_or_factor", check_classify_numbers_prime_or_factor),
    ("04. parse_port_setting", check_parse_port_setting),
    ("05. simplify_ast_expr", check_simplify_ast_expr),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 05_control_flow_and_matching.py")
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
