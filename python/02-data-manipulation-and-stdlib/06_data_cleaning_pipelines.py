from __future__ import annotations

import sys
import time
from typing import Any, Callable

r"""
MÓDULO 02 — MANIPULACIÓN DE DATOS Y STDLIB: 06. PIPELINES DE LIMPIEZA DE DATOS (ETL)
===============================================================================
Estudio profundo y práctica deliberada sobre transformación, limpieza,
aplanado recursivo de JSON, imputación de datos faltantes, tablas pivote y
detección estadística de valores atípicos (IQR) usando únicamente Python nativo.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Aplanado Recursivo de Diccionarios (`flatten_json`):
   - Concatena la clave padre con la clave hija usando un separador (`.`).
   - Un diccionario vacío `{}` como hoja no genera sub-claves o se ignora.

2. Imputación Lineal / Forward-Fill:
   - En series temporales con huecos (`None`), un `forward_fill` reemplaza cada
     `None` por el último valor válido observado previamente.

3. Detección de Anomalías mediante Rango Intercuartílico (IQR):
   - Dado un conjunto ordenado:
     * $Q_1$: mediana de la mitad inferior.
     * $Q_3$: mediana de la mitad superior.
     * $\text{IQR} = Q_3 - Q_1$.
     * Límites normales: $[Q_1 - 1.5 \times \text{IQR},\; Q_3 + 1.5 \times \text{IQR}]$.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- En pipelines ETL, diseña cada etapa como una función pura (que reciba registros
  y devuelva nuevos registros limpios sin mutar los diccionarios de entrada).
- Al deduplicar usuarios por email, normaliza siempre `.strip().lower()` antes
  de comparar.
"""


def flatten_nested_json(
    nested: dict[str, Any], parent_key: str = "", sep: str = "."
) -> dict[str, Any]:
    """Aplana recursivamente un diccionario anidado uniendo claves con `sep`.

    Ejemplo:
        >>> flatten_nested_json({"user": {"name": "Ada", "geo": {"country": "UK"}}, "active": True})
        {'user.name': 'Ada', 'user.geo.country': 'UK', 'active': True}

    Complejidad objetivo:
        Tiempo: O(total_claves) | Espacio: O(total_claves)

    Pista:
        Para cada `k, v`, construye `new_key = f"{parent_key}{sep}{k}" if parent_key else k`.
        Si `isinstance(v, dict)` y `v` no está vacío, recurre y usa `.update(...)`.
    """
    # BEGIN_SOLUTION
    flat: dict[str, Any] = {}
    for k, v in nested.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict) and v:
            flat.update(flatten_nested_json(v, new_key, sep=sep))
        else:
            flat[new_key] = v
    return flat
    # END_SOLUTION


def deduplicate_users_keep_latest(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Deduplica registros de usuarios por `email` (case-insensitive) conservando el mayor `updated_at`.

    Devuelve la lista de registros ganadores ordenados por `email` normalizado.
    En el registro devuelto, el campo `"email"` debe quedar normalizado (`.strip().lower()`).

    Ejemplo:
        >>> rows = [
        ...     {"email": "Ada@Dev.io ", "updated_at": 10, "role": "user"},
        ...     {"email": "ada@dev.io", "updated_at": 25, "role": "admin"},
        ... ]
        >>> deduplicate_users_keep_latest(rows)
        [{'email': 'ada@dev.io', 'updated_at': 25, 'role': 'admin'}]

    Complejidad objetivo:
        Tiempo: O(n log n) | Espacio: O(n)

    Pista:
        Guarda en un diccionario `best_by_email[clean_email]` reemplazando solo si
        `row["updated_at"] > actual["updated_at"]`.
    """
    # BEGIN_SOLUTION
    best_by_email: dict[str, dict[str, Any]] = {}
    for row in records:
        clean_email = str(row["email"]).strip().lower()
        normalized_row = {**row, "email": clean_email}
        if (
            clean_email not in best_by_email
            or int(normalized_row["updated_at"]) > int(best_by_email[clean_email]["updated_at"])
        ):
            best_by_email[clean_email] = normalized_row

    return [best_by_email[k] for k in sorted(best_by_email)]
    # END_SOLUTION


def forward_fill_missing(series: list[float | None], default_initial: float = 0.0) -> list[float]:
    """Rellena valores `None` con el último valor numérico válido visto (Forward-Fill).

    Si los primeros elementos son `None`, usa `default_initial`.

    Ejemplo:
        >>> forward_fill_missing([None, 10.0, None, None, 25.0, None], default_initial=0.0)
        [0.0, 10.0, 10.0, 10.0, 25.0, 25.0]

    Complejidad objetivo:
        Tiempo: O(n) | Espacio: O(n)

    Pista:
        Mantén una variable `last_valid = default_initial` y actualízala cuando `val is not None`.
    """
    # BEGIN_SOLUTION
    last_valid = default_initial
    filled: list[float] = []
    for val in series:
        if val is not None:
            last_valid = float(val)
        filled.append(last_valid)
    return filled
    # END_SOLUTION


def build_pivot_table(
    rows: list[dict[str, Any]],
    row_key: str,
    col_key: str,
    val_key: str,
) -> dict[str, dict[str, float]]:
    """Construye una tabla pivote 2D sumando `val_key` agrupado por `(row_key, col_key)`.

    Todas las filas de la tabla resultante deben contener todas las columnas
    descubiertas en el dataset (rellenando con `0.0` las combinaciones ausentes).

    Ejemplo:
        >>> data = [
        ...     {"dept": "IT", "quarter": "Q1", "cost": 100.0},
        ...     {"dept": "HR", "quarter": "Q2", "cost": 50.0},
        ... ]
        >>> build_pivot_table(data, "dept", "quarter", "cost")
        {'HR': {'Q1': 0.0, 'Q2': 50.0}, 'IT': {'Q1': 100.0, 'Q2': 0.0}}

    Complejidad objetivo:
        Tiempo: O(R * C + n) | Espacio: O(R * C)

    Pista:
        Recolecta el conjunto ordenado de `all_rows` y `all_cols`, inicializa la
        matriz en `0.0` y acumula cada registro.
    """
    # BEGIN_SOLUTION
    all_rows = sorted({str(r[row_key]) for r in rows})
    all_cols = sorted({str(r[col_key]) for r in rows})
    pivot: dict[str, dict[str, float]] = {
        r_name: {c_name: 0.0 for c_name in all_cols} for r_name in all_rows
    }
    for r in rows:
        rk = str(r[row_key])
        ck = str(r[col_key])
        pivot[rk][ck] = round(pivot[rk][ck] + float(r[val_key]), 2)
    return pivot
    # END_SOLUTION


def filter_iqr_outliers(values: list[float]) -> list[float]:
    """Filtra valores atípicos fuera de `[Q1 - 1.5 * IQR, Q3 + 1.5 * IQR]`.

    Si `len(values) < 4`, devuelve una copia de `values`.
    Para calcular `Q1` y `Q3`:
    - Ordena una copia `arr = sorted(values)`.
    - Divide en `lower_half = arr[: len(arr) // 2]` y
      `upper_half = arr[(len(arr) + 1) // 2 :]`.
    - La mediana de una mitad `h` de longitud `m` es `h[m // 2]` si `m` es impar,
      o `(h[m // 2 - 1] + h[m // 2]) / 2` si `m` es par.
    Conserva el orden original de `values`.

    Ejemplo:
        >>> filter_iqr_outliers([10.0, 12.0, 11.0, 13.0, 12.0, 11.0, 100.0])
        [10.0, 12.0, 11.0, 13.0, 12.0, 11.0]

    Complejidad objetivo:
        Tiempo: O(n log n) | Espacio: O(n)
    """
    # BEGIN_SOLUTION
    if len(values) < 4:
        return list(values)

    def _median(sorted_slice: list[float]) -> float:
        m = len(sorted_slice)
        mid = m // 2
        if m % 2 == 1:
            return sorted_slice[mid]
        return (sorted_slice[mid - 1] + sorted_slice[mid]) / 2.0

    arr = sorted(values)
    n = len(arr)
    q1 = _median(arr[: n // 2])
    q3 = _median(arr[(n + 1) // 2 :])
    iqr = q3 - q1
    low_bound = q1 - 1.5 * iqr
    high_bound = q3 + 1.5 * iqr
    return [v for v in values if low_bound <= v <= high_bound]
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_flatten_nested_json() -> None:
    nested = {"user": {"name": "Ada", "geo": {"country": "UK"}}, "active": True}
    assert flatten_nested_json(nested) == {
        "user.name": "Ada",
        "user.geo.country": "UK",
        "active": True,
    }


def check_deduplicate_users_keep_latest() -> None:
    rows = [
        {"email": "Ada@Dev.io ", "updated_at": 10, "role": "user"},
        {"email": "bob@dev.io", "updated_at": 5, "role": "user"},
        {"email": "ada@dev.io", "updated_at": 25, "role": "admin"},
    ]
    assert deduplicate_users_keep_latest(rows) == [
        {"email": "ada@dev.io", "updated_at": 25, "role": "admin"},
        {"email": "bob@dev.io", "updated_at": 5, "role": "user"},
    ]


def check_forward_fill_missing() -> None:
    assert forward_fill_missing([None, 10.0, None, None, 25.0, None], 0.0) == [
        0.0,
        10.0,
        10.0,
        10.0,
        25.0,
        25.0,
    ]


def check_build_pivot_table() -> None:
    data = [
        {"dept": "IT", "quarter": "Q1", "cost": 100.0},
        {"dept": "IT", "quarter": "Q1", "cost": 50.0},
        {"dept": "HR", "quarter": "Q2", "cost": 80.0},
    ]
    assert build_pivot_table(data, "dept", "quarter", "cost") == {
        "HR": {"Q1": 0.0, "Q2": 80.0},
        "IT": {"Q1": 150.0, "Q2": 0.0},
    }


def check_filter_iqr_outliers() -> None:
    sample = [10.0, 12.0, 11.0, 13.0, 12.0, 11.0, 100.0, -50.0]
    assert filter_iqr_outliers(sample) == [10.0, 12.0, 11.0, 13.0, 12.0, 11.0]


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. flatten_nested_json", check_flatten_nested_json),
    ("02. deduplicate_users_keep_latest", check_deduplicate_users_keep_latest),
    ("03. forward_fill_missing", check_forward_fill_missing),
    ("04. build_pivot_table", check_build_pivot_table),
    ("05. filter_iqr_outliers", check_filter_iqr_outliers),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 06_data_cleaning_pipelines.py")
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
