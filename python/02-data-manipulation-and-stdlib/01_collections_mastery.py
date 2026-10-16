"""
================================================================================
MÓDULO 02: MANIPULACIÓN DE DATOS Y LIBRERÍA ESTÁNDAR (STDLIB)
Archivo 01: Dominio de `collections` (Counter, defaultdict, deque, namedtuple, ChainMap)
================================================================================

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
--------------------------------------------------------------------------------
1. `collections.Counter` ( Diccionario de frecuencias de hashables ):
   - Creación:
       c = Counter("abracadabra")          # Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
       c = Counter(["rojo", "azul", "rojo"])
   - Métodos clave:
       c.most_common(k)                    # Top k tuplas (elemento, conteo) ordenadas desc
       c.total()                           # Suma total de todos los conteos (Python 3.10+)
       list(c.elements())                  # Repite cada elemento según su frecuencia (> 0)
   - Álgebra de multiconjuntos (ignora conteos <= 0 en el resultado):
       c1 + c2                             # Suma conteos: c1[x] + c2[x]
       c1 - c2                             # Resta (mantiene solo positivos): max(0, c1[x] - c2[x])
       c1 & c2                             # Intersección (mínimo): min(c1[x], c2[x])
       c1 | c2                             # Unión (máximo): max(c1[x], c2[x])
       c1 <= c2                            # Inclusión de multiconjunto (True si c1[x] <= c2[x] para todo x)

2. `collections.defaultdict` ( Inicialización automática de claves faltantes ):
   - Creación con factory callable (sin paréntesis al pasar la función):
       agrupado = defaultdict(list)
       agrupado["dept"].append("Ana")      # Si "dept" no existe, ejecuta list() -> []
       conteos = defaultdict(int)
       conteos["item"] += 1                # int() devuelve 0 por defecto
   - Árboles o diccionarios anidados:
       matriz = defaultdict(lambda: defaultdict(float))
       matriz["Alimentos"]["2026-01"] += 45.50

3. `collections.deque` ( Cola doblemente enlazada O(1) en ambos extremos ):
   - Creación y ventana deslizante acotada:
        cola = deque([1, 2, 3], maxlen=3)  # Al insertar un 4to elemento, descarta el extremo opuesto
   - Operaciones O(1):
       cola.append(x)                      # Inserta a la derecha
       cola.appendleft(x)                  # Inserta a la izquierda
       cola.pop()                          # Extrae de la derecha
       cola.popleft()                      # Extrae de la izquierda (en list.pop(0) sería O(n))
       cola.rotate(k)                      # Rota k pasos a la derecha (si k < 0, rota a la izquierda)

4. `collections.namedtuple` y `typing.NamedTuple` ( Tuplas ligeras con campos con nombre ):
   - Sintaxis clásica:
       Punto = namedtuple("Punto", ["x", "y"])
       p = Punto(10, 20)
       p.x, p[0], p._asdict(), p._replace(x=99)

5. `collections.ChainMap` ( Vista unificada sobre múltiples diccionarios ):
   - Búsqueda jerárquica sin copiar ni mezclar diccionarios en memoria:
       config = ChainMap(cli_args, env_vars, defaults)
       config["host"]                      # Busca en cli_args -> luego env_vars -> luego defaults

🧠 MODELO MENTAL Y TRAMPAS COMUNES
--------------------------------------------------------------------------------
- `list.pop(0)` vs `deque.popleft()`: Una `list` en Python es un arreglo dinámico
  contiguo en memoria; borrar el índice 0 desplaza `n - 1` punteros (`O(n)`).
  `deque` es una lista doblemente enlazada de bloques de tamaño fijo: insertar o
  quitar por cualquier extremo es `O(1)` garantizado, pero indexar en medio `d[i]` es `O(n)`.
- `Counter.most_common(k)` desempata por orden de primera aparición (orden de inserción
  en el dict subyacente). Si necesitas desempate alfabético estricto, usa `sorted()`
  con clave compuesta `key=lambda par: (-par[1], par[0])`.
- `defaultdict` crea una clave en el diccionario *incluso al solo leerla* con `d[k]`.
  Si quieres consultar sin mutar el `defaultdict`, usa `d.get(k)`.
- `ChainMap` guarda referencias a los diccionarios originales: si un diccionario
  tiene `{"port": None}`, `ChainMap` encontrará la clave `"port"` en la primera capa
  y devolverá `None` en lugar de seguir buscando abajo. Filtra los `None` antes si
  representan argumentos no especificados.
================================================================================
"""

from __future__ import annotations

from collections import ChainMap, Counter, defaultdict, deque, namedtuple
from collections.abc import Iterable
import re
import time
from typing import Any

# Ejemplo de referencia con namedtuple para eventos estructurados
ActivityRecord = namedtuple("ActivityRecord", ["user", "action", "weight"])


# ==============================================================================
# EJERCICIO 1: Top K palabras más frecuentes con desempate alfabético
# ==============================================================================
def top_k_frequent_words(text: str, k: int) -> list[tuple[str, int]]:
    """
    Extrae las palabras del texto (secuencias alfanuméricas pasadas a minúsculas),
    cuenta su frecuencia usando `Counter` y devuelve las `k` palabras más frecuentes.

    Regla de ordenamiento:
    1. Mayor frecuencia primero (descendente).
    2. En caso de empate en frecuencia, orden alfabético (ascendente).
    Si `k <= 0` o el texto no tiene palabras, devuelve `[]`.
    """
    # BEGIN_SOLUTION
    if k <= 0:
        return []
    words = re.findall(r"[a-z0-9]+", text.lower())
    counts = Counter(words)
    sorted_items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return sorted_items[:k]
    # END_SOLUTION


# ==============================================================================
# EJERCICIO 2: Nota de rescate con álgebra de multiconjuntos (Counter)
# ==============================================================================
def can_construct_ransom_note(note: str, magazine: str) -> bool:
    """
    Determina si es posible construir el mensaje `note` recortando letras de
    `magazine`. Cada letra en `magazine` solo puede usarse una vez.
    Ignora los espacios en blanco (`' '`), pero distingue mayúsculas de minúsculas.

    Usa `Counter` (comparación `<=` o resta de multiconjuntos `-`).
    """
    # BEGIN_SOLUTION
    note_counter = Counter(ch for ch in note if ch != " ")
    magazine_counter = Counter(ch for ch in magazine if ch != " ")
    return note_counter <= magazine_counter
    # END_SOLUTION


# ==============================================================================
# EJERCICIO 3: Agrupación jerárquica con `defaultdict` anidado
# ==============================================================================
def group_transactions_by_category_and_month(
    txs: list[dict[str, Any]],
) -> dict[str, dict[str, float]]:
    """
    Recibe una lista de transacciones con el formato:
        {"category": "Food", "date": "2026-03-15", "amount": 25.5}

    Agrupa y suma los montos (`amount`) por `category` y luego por mes (`YYYY-MM`,
    los primeros 7 caracteres de `date`) usando un `defaultdict` anidado.
    Redondea cada suma final a 2 decimales y devuelve diccionarios estándar.
    """
    # BEGIN_SOLUTION
    tree: defaultdict[str, defaultdict[str, float]] = defaultdict(
        lambda: defaultdict(float)
    )
    for tx in txs:
        category = str(tx["category"])
        month = str(tx["date"])[:7]
        amount = float(tx["amount"])
        tree[category][month] += amount

    return {
        cat: {month: round(total, 2) for month, total in months.items()}
        for cat, months in tree.items()
    }
    # END_SOLUTION


# ==============================================================================
# EJERCICIO 4: Promedios de ventana deslizante con `deque(maxlen=...)`
# ==============================================================================
def sliding_window_averages(stream: Iterable[float], maxlen: int) -> list[float]:
    """
    Consume un flujo de números `stream` manteniendo una ventana deslizante de
    tamaño máximo `maxlen` mediante `deque(maxlen=maxlen)`.
    Tras insertar cada elemento, calcula el promedio actual de la ventana
    (redondeado a 2 decimales) y lo agrega a la lista de resultados.

    Levanta `ValueError` si `maxlen <= 0`.
    """
    # BEGIN_SOLUTION
    if maxlen <= 0:
        raise ValueError("maxlen debe ser mayor a 0")

    window: deque[float] = deque(maxlen=maxlen)
    running_sum = 0.0
    averages: list[float] = []

    for value in stream:
        if len(window) == maxlen:
            running_sum -= window[0]
        window.append(value)
        running_sum += value
        averages.append(round(running_sum / len(window), 2))

    return averages
    # END_SOLUTION


# ==============================================================================
# EJERCICIO 5: Rotación circular de turnos con `deque.rotate`
# ==============================================================================
def rotate_schedule_ring(workers: list[str], shifts: int) -> list[str]:
    """
    Rota una lista de trabajadores circularmente usando `deque.rotate(shifts)`.
    - Un valor positivo de `shifts` mueve a los trabajadores del final hacia el inicio.
    - Un valor negativo mueve a los del inicio hacia el final.
    Devuelve la nueva lista rotada sin mutar la lista de entrada.
    """
    # BEGIN_SOLUTION
    ring = deque(workers)
    ring.rotate(shifts)
    return list(ring)
    # END_SOLUTION


# ==============================================================================
# EJERCICIO 6: Resolución de configuración por capas con `ChainMap`
# ==============================================================================
def resolve_layered_config(
    cli_args: dict[str, Any],
    env_vars: dict[str, Any],
    defaults: dict[str, Any],
) -> dict[str, Any]:
    """
    Combina tres niveles de configuración con prioridad:
        1. `cli_args` (mayor prioridad)
        2. `env_vars` (prioridad media)
        3. `defaults` (menor prioridad)

    Regla importante: Si en `cli_args` o `env_vars` una clave tiene valor `None`,
    significa que no fue provista en esa capa y NO debe ocultar el valor inferior.
    Usa `ChainMap` y devuelve un `dict` plano con la configuración efectiva.
    """
    # BEGIN_SOLUTION
    clean_cli = {k: v for k, v in cli_args.items() if v is not None}
    clean_env = {k: v for k, v in env_vars.items() if v is not None}
    layered = ChainMap(clean_cli, clean_env, defaults)
    return dict(layered)
    # END_SOLUTION


# ==============================================================================
# SUITE DE PRUEBAS Y VERIFICACIÓN
# ==============================================================================
def _check_top_k_frequent_words() -> None:
    text = "python data python codigo data rust python Go go data"
    assert top_k_frequent_words(text, 2) == [("data", 3), ("python", 3)]
    assert top_k_frequent_words(text, 3) == [("data", 3), ("python", 3), ("go", 2)]
    assert top_k_frequent_words("", 5) == []
    assert top_k_frequent_words("hola mundo", 0) == []


def _check_can_construct_ransom_note() -> None:
    assert can_construct_ransom_note("paga hoy", "paga ahora mismo y huye") is True
    assert can_construct_ransom_note("aaa", "aab") is False
    assert can_construct_ransom_note("Secreta", "secreta") is False
    assert can_construct_ransom_note("", "cualquier texto") is True


def _check_group_transactions_by_category_and_month() -> None:
    txs = [
        {"category": "Cloud", "date": "2026-01-05", "amount": 120.10},
        {"category": "Cloud", "date": "2026-01-20", "amount": 79.90},
        {"category": "Cloud", "date": "2026-02-01", "amount": 150.00},
        {"category": "Food", "date": "2026-01-11", "amount": 35.55},
    ]
    res = group_transactions_by_category_and_month(txs)
    assert res == {
        "Cloud": {"2026-01": 200.0, "2026-02": 150.0},
        "Food": {"2026-01": 35.55},
    }
    assert type(res) is dict
    assert type(res["Cloud"]) is dict


def _check_sliding_window_averages() -> None:
    assert sliding_window_averages([10.0, 20.0, 30.0, 40.0, 50.0], maxlen=3) == [
        10.0,
        15.0,
        20.0,
        30.0,
        40.0,
    ]
    assert sliding_window_averages([], maxlen=2) == []
    try:
        sliding_window_averages([1.0, 2.0], maxlen=0)
        raise AssertionError("Debió lanzar ValueError para maxlen=0")
    except ValueError:
        pass


def _check_rotate_schedule_ring() -> None:
    original = ["Ana", "Beto", "Carla", "Diego"]
    assert rotate_schedule_ring(original, 1) == ["Diego", "Ana", "Beto", "Carla"]
    assert rotate_schedule_ring(original, -2) == ["Carla", "Diego", "Ana", "Beto"]
    assert original == ["Ana", "Beto", "Carla", "Diego"]


def _check_resolve_layered_config() -> None:
    defaults = {"host": "localhost", "port": 5432, "debug": False, "timeout": 30}
    env_vars = {"host": "db.internal", "port": None, "debug": True}
    cli_args = {"port": 8080, "debug": None}
    resolved = resolve_layered_config(cli_args, env_vars, defaults)
    assert resolved == {
        "host": "db.internal",
        "port": 8080,
        "debug": True,
        "timeout": 30,
    }


def test_kata() -> None:
    _check_top_k_frequent_words()
    _check_can_construct_ransom_note()
    _check_group_transactions_by_category_and_month()
    _check_sliding_window_averages()
    _check_rotate_schedule_ring()
    _check_resolve_layered_config()


def run_verification() -> None:
    checks = [
        ("Ejercicio 1: top_k_frequent_words", _check_top_k_frequent_words),
        ("Ejercicio 2: can_construct_ransom_note", _check_can_construct_ransom_note),
        (
            "Ejercicio 3: group_transactions_by_category_and_month",
            _check_group_transactions_by_category_and_month,
        ),
        ("Ejercicio 4: sliding_window_averages", _check_sliding_window_averages),
        ("Ejercicio 5: rotate_schedule_ring", _check_rotate_schedule_ring),
        ("Ejercicio 6: resolve_layered_config", _check_resolve_layered_config),
    ]

    print("=" * 72)
    print("🧪 VERIFICACIÓN: 01_collections_mastery.py")
    print("=" * 72)

    passed = 0
    for title, check_fn in checks:
        start = time.perf_counter()
        try:
            check_fn()
            elapsed_ms = (time.perf_counter() - start) * 1000
            print(f"✅ [PASS] {title} ({elapsed_ms:.2f} ms)")
            passed += 1
        except NotImplementedError:
            print(f"⏳ [PENDIENTE] {title} (Todavía no implementado)")
        except Exception as exc:
            print(f"❌ [FAIL] {title} -> {type(exc).__name__}: {exc}")

    print("-" * 72)
    print(f"Resultado final: {passed}/{len(checks)} ejercicios superados.")
    if passed < len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    run_verification()
