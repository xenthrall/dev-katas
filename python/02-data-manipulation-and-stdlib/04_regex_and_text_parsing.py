from __future__ import annotations

import re
import sys
import time
from typing import Callable

r"""
MÓDULO 02 — MANIPULACIÓN DE DATOS Y STDLIB: 04. REGEX Y PARSING DE TEXTO
===============================================================================
Estudio profundo y práctica deliberada sobre el motor de expresiones regulares
de Python (`re`), grupos con nombre, aserciones lookaround y sustituciones
dinámicas mediante funciones callback.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Métodos Principales de `re`:
   - `re.search(pattern, text)`: Busca en cualquier parte de la cadena.
   - `re.match(pattern, text)` / `re.fullmatch(pattern, text)`: Al inicio / toda la cadena.
   - `re.findall(pattern, text)`: Lista de strings (¡cuidado si hay grupos de captura!).
   - `re.finditer(pattern, text)`: Iterador perezoso de objetos `re.Match` (preferido).
   - `re.sub(pattern, repl_or_callable, text)`: Reemplaza ocurrencias. `repl` puede ser
     una función `fn(match: re.Match) -> str`.

2. Grupos con Nombre y No-Capturantes:
   - `(?P<nombre>patron)`: Grupo con nombre. Se extrae con `m.group("nombre")` o
     como diccionario completo con `m.groupdict()`.
   - `(?:patron)`: Agrupa sin capturar (evita alterar la salida de `findall`).

3. Lookarounds (Aserciones de Ancho Cero — No consumen caracteres):
   - `(?=...)`: Positive Lookahead (seguido por...).
   - `(?!...)`: Negative Lookahead (NO seguido por...).
   - `(?<=...)`: Positive Lookbehind (precedido por...).
   - `(?<!...)`: Negative Lookbehind (NO precedido por...).

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- Usa siempre **raw strings** `r"..."` para escribir patrones regex y evitar
  que Python interprete `\b` o `\d` como secuencias de escape de string.
- Cuantificadores codiciosos (`*`, `+`) vs perezosos (`*?`, `+?`): `<.+>` sobre
  `"<a>hola</a>"` captura todo el string de extremo a extremo; `<.+?>` se detiene
  en el primer `>`.
"""

LOG_PATTERN = re.compile(
    r"^\[(?P<timestamp>[^\]]+)\]\s+(?P<level>INFO|WARN|ERROR)\s+service=(?P<service>[\w-]+)\s+msg=\"(?P<msg>[^\"]*)\"$"
)


def parse_structured_log_line(line: str) -> dict[str, str] | None:
    """Extrae `timestamp`, `level`, `service` y `msg` de una línea de log estructurada.

    Formato esperado:
        `[2026-10-16T09:00:00Z] ERROR service=auth-api msg="Invalid token"`

    Si la línea no coincide exactamente con el formato, devuelve `None`.

    Ejemplo:
        >>> parse_structured_log_line('[2026-10-16] INFO service=billing msg="Paid"')
        {'timestamp': '2026-10-16', 'level': 'INFO', 'service': 'billing', 'msg': 'Paid'}

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(1)

    Pista:
        Usa `LOG_PATTERN.match(line.strip())` y retorna `m.groupdict()` si existe coincidencia.
    """
    # BEGIN_SOLUTION
    match = LOG_PATTERN.match(line.strip())
    return match.groupdict() if match else None
    # END_SOLUTION


def mask_sensitive_tokens(text: str) -> str:
    r"""Oculta tarjetas de 16 dígitos dejando visibles solo los últimos 4 dígitos.

    Detecta números de tarjeta con formato `XXXX-XXXX-XXXX-XXXX` o `XXXXXXXXXXXXXXXX`
    (16 dígitos separados opcionalmente por guiones) usando `re.sub` con una
    función callback, reemplazándolos por `****-****-****-<ultimos_4>`.

    Ejemplo:
        >>> mask_sensitive_tokens("Pago con 4111-2222-3333-4444 y 5500111122229876.")
        'Pago con ****-****-****-4444 y ****-****-****-9876.'

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Usa el patrón `r"\b(?:\d{4}-){3}(\d{4})\b|\b\d{12}(\d{4})\b"` o extrae
        los últimos 4 dígitos en un callback `lambda m: f"****-****-****-{...}"`.
    """
    # BEGIN_SOLUTION
    pattern = re.compile(r"\b(?:\d{4}-){3}\d{4}\b|\b\d{16}\b")

    def _replacer(match: re.Match[str]) -> str:
        raw = match.group(0)
        last4 = raw[-4:]
        return f"****-****-****-{last4}"

    return pattern.sub(_replacer, text)
    # END_SOLUTION


def camel_to_snake_case(identifier: str) -> str:
    """Convierte un identificador CamelCase o PascalCase a `snake_case` usando lookarounds.

    Maneja siglas consecutivas correctamente: `"HTTPResponseCode"` -> `"http_response_code"`.

    Ejemplo:
        >>> camel_to_snake_case("parseHTTPResponseCode")
        'parse_http_response_code'
        >>> camel_to_snake_case("SimpleXMLParser")
        'simple_xml_parser'

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Inserta `_` entre mayúscula seguida de mayúscula+minúscula `r"([A-Z]+)([A-Z][a-z])"`
        y entre minúscula/dígito seguido de mayúscula `r"([a-z0-9])([A-Z])"`, luego `.lower()`.
    """
    # BEGIN_SOLUTION
    step1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", identifier)
    step2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", step1)
    return step2.lower()
    # END_SOLUTION


def extract_prices_usd(text: str) -> list[float]:
    r"""Extrae todos los montos precedidos por `$` usando lookbehind positivo `(?<=\$)`.

    No debe capturar números que vayan precedidos por otros símbolos como `€` o `£`.
    Soporta enteros o decimales como `$19.99` o `$100`.

    Ejemplo:
        >>> extract_prices_usd("Items: $19.99, €50.00, $100 y £25.50")
        [19.99, 100.0]

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(k)

    Pista:
        Usa `re.findall(r"(?<=\$)\d+(?:\.\d+)?", text)` y convierte cada hallazgo a `float`.
    """
    # BEGIN_SOLUTION
    matches = re.findall(r"(?<=\$)\d+(?:\.\d+)?", text)
    return [float(m) for m in matches]
    # END_SOLUTION


def render_template_placeholders(template: str, context: dict[str, object]) -> str:
    r"""Reemplaza marcadores `{{ variable }}` en `template` consultando `context`.

    Si la clave no existe en `context`, conserva un marcador `[MISSING:<variable>]`.

    Ejemplo:
        >>> render_template_placeholders("Hola {{ user }}, saldo: {{ balance }} ({{ missing }})", {"user": "Ada", "balance": 50})
        'Hola Ada, saldo: 50 ([MISSING:missing])'

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Usa `re.sub(r"\{\{\s*(\w+)\s*\}\}", callback, template)`.
    """
    # BEGIN_SOLUTION
    pattern = re.compile(r"\{\{\s*(?P<key>\w+)\s*\}\}")

    def _replace(match: re.Match[str]) -> str:
        key = match.group("key")
        if key in context:
            return str(context[key])
        return f"[MISSING:{key}]"

    return pattern.sub(_replace, template)
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_parse_structured_log_line() -> None:
    line = '[2026-10-16T09:00:00Z] ERROR service=auth-api msg="Invalid token"'
    assert parse_structured_log_line(line) == {
        "timestamp": "2026-10-16T09:00:00Z",
        "level": "ERROR",
        "service": "auth-api",
        "msg": "Invalid token",
    }
    assert parse_structured_log_line("malformed log line") is None


def check_mask_sensitive_tokens() -> None:
    raw = "Pago con 4111-2222-3333-4444 y 5500111122229876 (ID 1234)."
    assert (
        mask_sensitive_tokens(raw)
        == "Pago con ****-****-****-4444 y ****-****-****-9876 (ID 1234)."
    )


def check_camel_to_snake_case() -> None:
    assert camel_to_snake_case("parseHTTPResponseCode") == "parse_http_response_code"
    assert camel_to_snake_case("SimpleXMLParser") == "simple_xml_parser"
    assert camel_to_snake_case("userID2") == "user_id2"


def check_extract_prices_usd() -> None:
    assert extract_prices_usd("Items: $19.99, €50.00, $100 y £25.50") == [19.99, 100.0]
    assert extract_prices_usd("Sin dolares €10") == []


def check_render_template_placeholders() -> None:
    tpl = "Hola {{ user }}, saldo: {{balance}} ({{ unknown }})"
    assert (
        render_template_placeholders(tpl, {"user": "Ada", "balance": 100})
        == "Hola Ada, saldo: 100 ([MISSING:unknown])"
    )


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. parse_structured_log_line", check_parse_structured_log_line),
    ("02. mask_sensitive_tokens", check_mask_sensitive_tokens),
    ("03. camel_to_snake_case", check_camel_to_snake_case),
    ("04. extract_prices_usd", check_extract_prices_usd),
    ("05. render_template_placeholders", check_render_template_placeholders),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 04_regex_and_text_parsing.py")
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
