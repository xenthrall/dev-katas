from __future__ import annotations

import sys
import time
from typing import Callable

"""
MÓDULO 01 — SINTAXIS Y PRIMITIVAS: 01. STRINGS Y SLICING
===============================================================================
Estudio profundo y práctica deliberada sobre manipulación de cadenas de texto
(`str`), indexación, slicing avanzado, métodos nativos de búsqueda/partición,
codificación de puntos de código Unicode (`ord`/`chr`) y formateo moderno con
f-strings en Python.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Indexación y Slicing (`s[start:stop:step]`):
   - Índices positivos (`0` a `len(s)-1`) y negativos (`-1` es el último carácter).
   - `s[start:stop:step]`: extrae desde `start` (inclusivo) hasta `stop` (exclusivo)
     avanzando de a `step` posiciones. Complejidad: O(k) donde k es la longitud
     de la subcadena resultante.
   - Atajos idiomáticos:
     * `s[::-1]`   -> Invierte la cadena completa (O(n)).
     * `s[:k]`     -> Primeros `k` caracteres.
     * `s[-k:]`    -> Últimos `k` caracteres.
     * `s[::2]`    -> Caracteres en índices pares.

2. Inmutabilidad de `str`:
   - Los objetos `str` en Python son estrictamente inmutables. Cualquier operación
     de transformación produce un nuevo objeto en memoria.
   - ❌ ANTI-PATRÓN: Concatenar en un bucle `res += char` puede degradar a O(n²)
     si existen referencias adicionales.
   - ✅ IDIOMÁTICO: Acumular en una `list[str]` y unir al final con `"".join(partes)`
     garantiza tiempo y memoria lineal O(n).

3. Métodos Esenciales de `str` (Todos operan en O(n)):
   - `s.split(sep=None, maxsplit=-1)`:
     * Sin argumentos (`s.split()`): divide por cualquier secuencia de espacios en
       blanco consecutivos y descarta extremos vacíos.
     * Con `sep` explícito (`s.split(",")`): divide exactamente por el delimitador
       (preserva cadenas vacías entre delimitadores contiguos).
   - `sep.join(iterable)`: concatena un iterable de strings usando `sep`.
   - `s.strip(chars=None)` / `lstrip()` / `rstrip()`: elimina caracteres de los bordes.
   - `s.partition(sep)` / `rpartition(sep)`:
     * Devuelve siempre una 3-tupla `(head, sep, tail)`. Si `sep` no aparece,
       devuelve `(s, "", "")`. Más seguro y expresivo que `.find()` + slicing.
   - `s.replace(old, new, count=-1)`: reemplaza ocurrencias de `old` por `new`.
   - `str.maketrans(x, y, z)` + `s.translate(table)`:
     * Reemplazo o eliminación masiva de caracteres en una sola pasada C-level O(n).

4. Puntos de Código Unicode (`ord` y `chr`):
   - `ord(char) -> int`: punto de código Unicode (ej. `ord('A') == 65`, `ord('a') == 97`).
   - `chr(code) -> str`: carácter correspondiente al entero (ej. `chr(65) == 'A'`).
   - Aritmética modular para alfabeto ASCII:
     `nuevo_idx = (ord(c) - base + shift) % 26 + base`

5. Mini-lenguaje de Formato en f-strings (`{valor:especificador}`):
   - Decimales fijos: `{val:.2f}` (2 decimales), `{val:+.2f}` (fuerza signo `+` o `-`).
   - Separador de miles: `{val:,.2f}` (ej. `1,234,567.89`).
   - Alineación y relleno:
     * `{texto:<15}` -> Alineado a la izquierda en ancho 15.
     * `{texto:>10}` -> Alineado a la derecha en ancho 10.
     * `{texto:^12}` -> Centrado en ancho 12.
     * `{num:0>5}`   -> Relleno con ceros a la izquierda.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- `s.split()` vs `s.split(" ")`: `"a   b".split()` produce `["a", "b"]`, mientras
  que `"a   b".split(" ")` produce `["a", "", "", "b"]`. Para limpiar texto humano,
  prefiere siempre `s.split()` sin argumentos.
- `.partition(sep)` nunca lanza `ValueError` (a diferencia de `.index(sep)` cuando
  el separador no existe), lo que evita bloques `try/except` o chequeos `if sep in s`.
- El slicing fuera de rango (`"hola"[0:999]`) nunca lanza `IndexError`; trunca
  silenciosamente al límite válido.
"""


def reverse_words(sentence: str) -> str:
    """Invierte el orden de las palabras eliminando espacios múltiples o extremos.

    Ejemplo:
        >>> reverse_words("  el   código   limpio  ")
        'limpio código el'
        >>> reverse_words("   ")
        ''

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Combina `.split()` sin argumentos (que colapsa espacios múltiples) con
        slicing inverso `[::-1]` y `" ".join(...)`.
    """
    # BEGIN_SOLUTION
    return " ".join(sentence.split()[::-1])
    # END_SOLUTION


def is_palindrome_clean(text: str) -> bool:
    """Verifica si una cadena es un palíndromo ignorando mayúsculas y no-alfanuméricos.

    Ejemplo:
        >>> is_palindrome_clean("Anita lava la tina!")
        True
        >>> is_palindrome_clean("Python 3.12")
        False

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Filtra solo caracteres donde `c.isalnum()` sea verdadero convirtiéndolos
        con `.lower()`, y compara la secuencia con su reverso `[::-1]`.
    """
    # BEGIN_SOLUTION
    cleaned = "".join(ch.lower() for ch in text if ch.isalnum())
    return cleaned == cleaned[::-1]
    # END_SOLUTION


def run_length_encode(text: str) -> str:
    """Comprime una cadena mediante Run-Length Encoding (RLE) consecutivo.

    Cada grupo de caracteres idénticos consecutivos se codifica como `<char><conteo>`.
    Si la cadena está vacía, devuelve `""`.

    Ejemplo:
        >>> run_length_encode("aaabbc")
        'a3b2c1'
        >>> run_length_encode("aabbaa")
        'a2b2a2'
        >>> run_length_encode("")
        ''

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Recorre la cadena llevando el carácter actual y su contador; acumula los
        fragmentos `f"{actual}{conteo}"` en una lista y únelos al final con `"".join()`.
    """
    # BEGIN_SOLUTION
    if not text:
        return ""

    parts: list[str] = []
    current_char = text[0]
    count = 1

    for ch in text[1:]:
        if ch == current_char:
            count += 1
        else:
            parts.append(f"{current_char}{count}")
            current_char = ch
            count = 1

    parts.append(f"{current_char}{count}")
    return "".join(parts)
    # END_SOLUTION


def caesar_cipher(text: str, shift: int) -> str:
    """Aplica el cifrado César a las letras ASCII preservando mayúsculas y signos.

    Solo rota letras en el rango ASCII `'a'-'z'` y `'A'-'Z'`. Cualquier otro
    carácter (espacios, dígitos, puntuación, acentos) permanece intacto.
    Soporta desplazamientos positivos, negativos o mayores a 26.

    Ejemplo:
        >>> caesar_cipher("Hola, Mundo! 123", 3)
        'Krod, Pxqgr! 123'
        >>> caesar_cipher("Krod, Pxqgr! 123", -3)
        'Hola, Mundo! 123'

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Usa `ord(c)` y `chr(...)` con aritmética modular `(ord(c) - base + shift) % 26 + base`,
        donde `base` es `ord('A')` o `ord('a')`.
    """
    # BEGIN_SOLUTION
    out: list[str] = []
    for ch in text:
        if "a" <= ch <= "z":
            base = ord("a")
            out.append(chr((ord(ch) - base + shift) % 26 + base))
        elif "A" <= ch <= "Z":
            base = ord("A")
            out.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            out.append(ch)
    return "".join(out)
    # END_SOLUTION


def extract_slug_and_query(url: str) -> tuple[str, dict[str, str]]:
    """Extrae el último segmento del path (slug) y el diccionario de query params.

    Reglas:
    - Ignora cualquier fragmento `#...` al final de la URL.
    - Separa la ruta principal de la query string usando `?`.
    - El `slug` es el último segmento no vacío de la ruta (después del último `/`,
      ignorando barras finales `/`).
    - Cada parámetro en la query string tiene forma `clave=valor` separado por `&`.
      Recorta espacios alrededor de claves y valores con `.strip()`. Si un parámetro
      no contiene `=`, su valor es `""`. Ignora segmentos vacíos.

    Ejemplo:
        >>> extract_slug_and_query("https://api.dev/v1/katas/python-strings/?lang=es&level=2#top")
        ('python-strings', {'lang': 'es', 'level': '2'})
        >>> extract_slug_and_query("/blog/clean-code")
        ('clean-code', {})

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Usa `.partition("#")` para descartar el fragmento, luego `.partition("?")`
        para dividir path y query, `.rstrip("/")` + `.rpartition("/")` para el slug,
        y `.partition("=")` para cada par clave-valor.
    """
    # BEGIN_SOLUTION
    without_fragment, _, _ = url.strip().partition("#")
    path_part, _, query_part = without_fragment.partition("?")

    clean_path = path_part.rstrip("/")
    _, _, slug = clean_path.rpartition("/")

    params: dict[str, str] = {}
    if query_part:
        for pair in query_part.split("&"):
            pair = pair.strip()
            if not pair:
                continue
            key, sep, val = pair.partition("=")
            params[key.strip()] = val.strip() if sep else ""

    return slug, params
    # END_SOLUTION


def format_financial_table(rows: list[tuple[str, float, float]]) -> str:
    """Genera una tabla financiera alineada con variación porcentual.

    Cada tupla de entrada contiene `(ticker, precio_anterior, precio_actual)`.
    Cada línea de salida debe tener exactamente el formato:
    `"{ticker:<8} | {actual:>10,.2f} | {delta_pct:>+7.2f}%"`
    donde `delta_pct = ((actual - anterior) / anterior) * 100`.
    Une las filas con saltos de línea `\\n`. Si `rows` está vacío, devuelve `""`.

    Ejemplo:
        >>> print(format_financial_table([("NVDA", 100.0, 125.5), ("AAPL", 200.0, 190.0)]))
        NVDA     |     125.50 |  +25.50%
        AAPL     |     190.00 |   -5.00%

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Usa especificadores de formato en f-strings: `:<8` (izquierda), `:>10,.2f`
        (derecha con separador de miles y 2 decimales) y `:>+7.2f` (signo forzado).
    """
    # BEGIN_SOLUTION
    lines: list[str] = []
    for ticker, prev_price, curr_price in rows:
        delta_pct = ((curr_price - prev_price) / prev_price) * 100.0
        lines.append(f"{ticker:<8} | {curr_price:>10,.2f} | {delta_pct:>+7.2f}%")
    return "\n".join(lines)
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_reverse_words() -> None:
    assert reverse_words("  el   código   limpio  ") == "limpio código el"
    assert reverse_words("python") == "python"
    assert reverse_words("   \t\n  ") == ""
    assert reverse_words("uno dos tres cuatro") == "cuatro tres dos uno"


def check_is_palindrome_clean() -> None:
    assert is_palindrome_clean("Anita lava la tina!") is True
    assert is_palindrome_clean("A man, a plan, a canal: Panama") is True
    assert is_palindrome_clean("12321") is True
    assert is_palindrome_clean("Python 3.12") is False
    assert is_palindrome_clean("   !!!  ") is True


def check_run_length_encode() -> None:
    assert run_length_encode("") == ""
    assert run_length_encode("a") == "a1"
    assert run_length_encode("aaabbc") == "a3b2c1"
    assert run_length_encode("aabbaa") == "a2b2a2"
    assert run_length_encode("xyz") == "x1y1z1"


def check_caesar_cipher() -> None:
    assert caesar_cipher("Hola, Mundo! 123", 3) == "Krod, Pxqgr! 123"
    assert caesar_cipher("Krod, Pxqgr! 123", -3) == "Hola, Mundo! 123"
    assert caesar_cipher("xyz XYZ", 2) == "zab ZAB"
    assert caesar_cipher("AbC", 52) == "AbC"
    assert caesar_cipher("¡Canción!", 13) == "¡Pnapvóa!"


def check_extract_slug_and_query() -> None:
    slug, q = extract_slug_and_query(
        "https://api.dev/v1/katas/python-strings/?lang=es&level=2#top"
    )
    assert slug == "python-strings"
    assert q == {"lang": "es", "level": "2"}

    slug2, q2 = extract_slug_and_query("/blog/clean-code")
    assert slug2 == "clean-code"
    assert q2 == {}

    slug3, q3 = extract_slug_and_query(
        "https://example.com/items/42?debug&env = prod #section"
    )
    assert slug3 == "42"
    assert q3 == {"debug": "", "env": "prod"}


def check_format_financial_table() -> None:
    assert format_financial_table([]) == ""
    report = format_financial_table(
        [
            ("NVDA", 100.0, 125.5),
            ("AAPL", 200.0, 190.0),
            ("BRK.A", 1000.0, 1250.75),
        ]
    )
    expected = (
        "NVDA     |     125.50 |  +25.50%\n"
        "AAPL     |     190.00 |   -5.00%\n"
        "BRK.A    |   1,250.75 |  +25.07%"
    )
    assert report == expected


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. reverse_words", check_reverse_words),
    ("02. is_palindrome_clean", check_is_palindrome_clean),
    ("03. run_length_encode", check_run_length_encode),
    ("04. caesar_cipher", check_caesar_cipher),
    ("05. extract_slug_and_query", check_extract_slug_and_query),
    ("06. format_financial_table", check_format_financial_table),
]


def test_kata() -> None:
    """Punto de entrada compatible con pytest."""
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 01_strings_and_slicing.py")
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