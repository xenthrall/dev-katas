from __future__ import annotations

import sys
import time
from typing import Any, Callable, Hashable

"""
MÓDULO 01 — SINTAXIS Y PRIMITIVAS: 03. DICCIONARIOS, SETS Y HASHING
===============================================================================
Estudio profundo y práctica deliberada sobre tablas hash en Python (`dict`,
`set`, `frozenset`), acceso seguro, agrupación con `.setdefault()`, álgebra de
conjuntos, preservación del orden de inserción y requisitos de hashabilidad.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Operaciones Clave en `dict` (Complejidad O(1) amortizada):
   - `d.get(clave, default=None)`: Lee sin lanzar `KeyError`.
   - `d.setdefault(clave, default)`: Si `clave` no existe, inserta `d[clave] = default`
     y devuelve el valor asociado. Ideal para agrupar en listas:
     `grupos.setdefault(categoria, []).append(item)`
   - Fusión moderna (Python 3.9+):
     * `d_nuevo = d_base | d_prioritario` (las claves de la derecha ganan).
     * `d_base |= d_actualizacion` (actualización in-place).
   - `dict.fromkeys(iterable, valor=None)`: Crea un diccionario con claves únicas
     respetando el orden de primera aparición.
     * Idiomático para deduplicar preservando el orden en O(n):
       `unicos = list(dict.fromkeys(secuencia))`

2. Álgebra de Conjuntos con `set` (O(1) pertenencia, O(len) operaciones):
   - Unión (en A o en B):                  `a | b`  o `a.union(b)`
   - Intersección (en A y en B):           `a & b`  o `a.intersection(b)`
   - Diferencia (en A pero no en B):       `a - b`  o `a.difference(b)`
   - Diferencia Simétrica (en uno u otro): `a ^ b`  o `a.symmetric_difference(b)`
   - Subconjunto / Superconjunto:          `a <= b`, `a < b`, `a >= b`

3. `frozenset` y Hashabilidad:
   - Un `set` es mutable y por tanto NO es hashable (`unhashable type: 'set'`).
   - `frozenset(iterable)` es un conjunto inmutable y **hashable**: puede usarse
     como clave de un `dict` o como elemento dentro de otro `set` (ej. para
     representar aristas no dirigidas `{u, v}` o firmas de conjuntos sin orden).

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- ❌ `{}` crea un `dict` vacío, NUNCA un `set` vacío. Para un conjunto vacío usa
  siempre `set()`.
- En Python (`True == 1` y `hash(True) == hash(1)`), por lo que en un diccionario
  `{1: "uno", True: "verdadero"}` solo existe UNA clave (`1`) cuyo valor es
  sobrescrito por `"verdadero"`.
- Desde Python 3.7+, los diccionarios garantizan por especificación del lenguaje
  conservar el **orden de inserción** de las claves (mientras que `set` NO garantiza
  orden de inserción).
"""


def invert_mapping_grouped(mapping: dict[str, str]) -> dict[str, list[str]]:
    """Invierte un diccionario `clave -> valor` agrupando las claves con el mismo valor.

    Las listas de claves para cada valor deben preservar el orden en que aparecieron
    en `mapping`.

    Ejemplo:
        >>> invert_mapping_grouped({"ana": "backend", "luis": "data", "eva": "backend"})
        {'backend': ['ana', 'eva'], 'data': ['luis']}

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Recorre `mapping.items()` y usa `resultado.setdefault(valor, []).append(clave)`.
    """
    # BEGIN_SOLUTION
    inverted: dict[str, list[str]] = {}
    for key, val in mapping.items():
        inverted.setdefault(val, []).append(key)
    return inverted
    # END_SOLUTION


def deduplicate_preserve_order(items: list[Hashable]) -> list[Hashable]:
    """Elimina elementos duplicados de `items` manteniendo el orden de primera aparición.

    Ejemplo:
        >>> deduplicate_preserve_order(["py", "go", "py", "rust", "go", "zig"])
        ['py', 'go', 'rust', 'zig']

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Aprovecha que `dict.fromkeys(items)` preserva el orden de inserción en C.
    """
    # BEGIN_SOLUTION
    return list(dict.fromkeys(items))
    # END_SOLUTION


def merge_and_sum_inventories(
    inv_a: dict[str, int], inv_b: dict[str, int]
) -> dict[str, int]:
    """Combina dos inventarios sumando las cantidades de productos comunes.

    Descarta del resultado cualquier producto cuya suma total sea `<= 0`.

    Ejemplo:
        >>> merge_and_sum_inventories({"ssd": 4, "ram": 2}, {"ram": 3, "gpu": 1, "ssd": -4})
        {'ram': 5, 'gpu': 1}

    Complejidad objetivo:
        Tiempo: O(n + m) | Espacio: O(n + m)

    Pista:
        Obtén todas las claves con `inv_a.keys() | inv_b.keys()` y suma usando
        `inv_a.get(k, 0) + inv_b.get(k, 0)`.
    """
    # BEGIN_SOLUTION
    all_keys = inv_a.keys() | inv_b.keys()
    merged: dict[str, int] = {}
    for k in all_keys:
        total = inv_a.get(k, 0) + inv_b.get(k, 0)
        if total > 0:
            merged[k] = total
    return merged
    # END_SOLUTION


def analyze_permissions_diff(
    current_roles: set[str], target_roles: set[str]
) -> dict[str, set[str]]:
    """Calcula la auditoría de cambios entre los roles actuales y los roles objetivo.

    Devuelve un diccionario con cuatro conjuntos:
    - `"unchanged"`: roles presentes en ambos conjuntos (`&`).
    - `"added"`: roles que están en `target_roles` pero no en `current_roles` (`-`).
    - `"removed"`: roles que están en `current_roles` pero no en `target_roles` (`-`).
    - `"changed"`: todos los roles que fueron añadidos o eliminados (`^`).

    Ejemplo:
        >>> diff = analyze_permissions_diff({"read", "write"}, {"read", "admin"})
        >>> diff["added"], diff["removed"], diff["unchanged"], diff["changed"]
        ({'admin'}, {'write'}, {'read'}, {'admin', 'write'})

    Complejidad objetivo:
        Tiempo: O(n + m) | Espacio: O(n + m)

    Pista:
        Aplica directamente los operadores de conjuntos `&`, `-` y `^`.
    """
    # BEGIN_SOLUTION
    return {
        "unchanged": current_roles & target_roles,
        "added": target_roles - current_roles,
        "removed": current_roles - target_roles,
        "changed": current_roles ^ target_roles,
    }
    # END_SOLUTION


def count_unique_undirected_edges(edges: list[tuple[str, str]]) -> int:
    """Cuenta cuántas conexiones únicas sin dirección existen entre nodos.

    Una arista `("A", "B")` es equivalente a `("B", "A")`. Ignora auto-bucles
    donde `u == v`.

    Ejemplo:
        >>> count_unique_undirected_edges([("A", "B"), ("B", "A"), ("A", "C"), ("D", "D")])
        2

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Representa cada arista válida con `frozenset((u, v))` y guárdala en un `set`.
    """
    # BEGIN_SOLUTION
    unique_edges: set[frozenset[str]] = {
        frozenset((u, v)) for u, v in edges if u != v
    }
    return len(unique_edges)
    # END_SOLUTION


def deep_get(data: dict[str, Any], path: str, default: Any = None) -> Any:
    """Navega de forma segura un diccionario anidado usando una ruta separada por puntos.

    Si cualquier clave intermedia no existe o el valor intermedio no es un `dict`,
    devuelve `default` sin lanzar excepciones.

    Ejemplo:
        >>> cfg = {"db": {"primary": {"host": "10.0.0.1"}}}
        >>> deep_get(cfg, "db.primary.host")
        '10.0.0.1'
        >>> deep_get(cfg, "db.replica.port", default=5432)
        5432

    Complejidad objetivo:
        Tiempo: O(k) donde k es la profundidad de la ruta | Espacio: O(k)

    Pista:
        Itera sobre `path.split(".")` verificando `isinstance(actual, dict)` y `k in actual`.
    """
    # BEGIN_SOLUTION
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_invert_mapping_grouped() -> None:
    src = {"ana": "backend", "luis": "data", "eva": "backend", "sol": "infra"}
    assert invert_mapping_grouped(src) == {
        "backend": ["ana", "eva"],
        "data": ["luis"],
        "infra": ["sol"],
    }
    assert invert_mapping_grouped({}) == {}


def check_deduplicate_preserve_order() -> None:
    assert deduplicate_preserve_order([3, 1, 2, 3, 2, 4, 1]) == [3, 1, 2, 4]
    assert deduplicate_preserve_order(["a", "b", "a"]) == ["a", "b"]
    assert deduplicate_preserve_order([]) == []


def check_merge_and_sum_inventories() -> None:
    res = merge_and_sum_inventories(
        {"ssd": 4, "ram": 2, "mouse": 1},
        {"ram": 3, "gpu": 1, "ssd": -4, "mouse": -5},
    )
    assert res == {"ram": 5, "gpu": 1}


def check_analyze_permissions_diff() -> None:
    res = analyze_permissions_diff({"read", "write"}, {"read", "admin"})
    assert res == {
        "unchanged": {"read"},
        "added": {"admin"},
        "removed": {"write"},
        "changed": {"admin", "write"},
    }


def check_count_unique_undirected_edges() -> None:
    edges = [("A", "B"), ("B", "A"), ("A", "C"), ("C", "A"), ("D", "D"), ("B", "C")]
    assert count_unique_undirected_edges(edges) == 3
    assert count_unique_undirected_edges([]) == 0


def check_deep_get() -> None:
    cfg = {"db": {"primary": {"host": "10.0.0.1", "port": 5432}}, "debug": False}
    assert deep_get(cfg, "db.primary.host") == "10.0.0.1"
    assert deep_get(cfg, "debug") is False
    assert deep_get(cfg, "db.primary.host.sub", default="N/A") == "N/A"
    assert deep_get(cfg, "db.replica.host", default="localhost") == "localhost"


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. invert_mapping_grouped", check_invert_mapping_grouped),
    ("02. deduplicate_preserve_order", check_deduplicate_preserve_order),
    ("03. merge_and_sum_inventories", check_merge_and_sum_inventories),
    ("04. analyze_permissions_diff", check_analyze_permissions_diff),
    ("05. count_unique_undirected_edges", check_count_unique_undirected_edges),
    ("06. deep_get", check_deep_get),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 03_dicts_sets_and_hashing.py")
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
