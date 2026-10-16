from __future__ import annotations

import csv
from datetime import date, datetime, timedelta, timezone
import io
import json
from pathlib import PurePath
import sys
import time
from typing import Any, Callable

"""
MÓDULO 02 — MANIPULACIÓN DE DATOS Y STDLIB: 05. FECHAS, ARCHIVOS Y SERIALIZACIÓN
===============================================================================
Estudio profundo y práctica deliberada sobre manejo de fechas con zona horaria
(`datetime`, `timezone.utc`, `timedelta`), rutas multiplataforma (`pathlib`),
procesamiento de CSV en memoria (`csv.DictReader`, `io.StringIO`) y
serialización JSON personalizada (`json.dumps`).

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Fechas ISO-8601 y Zonas Horarias (`datetime`):
   - `datetime.fromisoformat(s)`: Parsea cadenas ISO-8601 (incluyendo sufijo `Z`
     en Python 3.11+).
   - `dt.astimezone(timezone.utc)`: Convierte un `datetime` con zona horaria a UTC.
   - `dt.weekday()`: `0` = Lunes ... `4` = Viernes, `5` = Sábado, `6` = Domingo.
   - `timedelta(days=1, hours=2, minutes=30)`: Aritmética exacta de tiempo.

2. Procesamiento de CSV en Memoria (`csv` + `io.StringIO`):
   - `reader = csv.DictReader(io.StringIO(raw_csv))`: Itera cada fila como `dict[str, str]`.
   - `buf = io.StringIO()`, `writer = csv.DictWriter(buf, fieldnames=..., lineterminator="\\n")`.

3. Serialización JSON Extendida (`json`):
   - `json.dumps(obj, default=custom_serializer, sort_keys=True)`: La función
     `default(o)` es invocada para tipos que JSON no soporta nativamente
     (como `datetime`, `date`, `set`).

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- ❌ `datetime.utcnow()` está deprecado porque produce un `datetime` *naive*
  (sin información de zona horaria). Usa siempre `datetime.now(timezone.utc)`.
- En Windows, escribir un CSV sin `newline=""` (o `lineterminator="\n"` en
  `StringIO`) inserta `\r\r\n`. Especifica siempre `lineterminator="\n"` cuando
  generes CSV deterministas en memoria.
"""


def normalize_iso_to_utc(iso_timestamp: str) -> str:
    """Convierte cualquier timestamp ISO-8601 a UTC con formato `'YYYY-MM-DDTHH:MM:SSZ'`.

    Si el timestamp de entrada no tiene zona horaria (`tzinfo is None`), asume que
    ya está en UTC.

    Ejemplo:
        >>> normalize_iso_to_utc("2026-10-16T09:30:00-05:00")
        '2026-10-16T14:30:00Z'

    Complejidad objetivo:
        Tiempo: O(1) | Espacio: O(1)

    Pista:
        Usa `datetime.fromisoformat(iso_timestamp)`. Si `dt.tzinfo is None`, usa
        `dt.replace(tzinfo=timezone.utc)`, de lo contrario `dt.astimezone(timezone.utc)`.
    """
    # BEGIN_SOLUTION
    dt = datetime.fromisoformat(iso_timestamp)
    if dt.tzinfo is None:
        dt_utc = dt.replace(tzinfo=timezone.utc)
    else:
        dt_utc = dt.astimezone(timezone.utc)
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    # END_SOLUTION


def add_business_days(start_date: date, business_days: int) -> date:
    """Suma `business_days` días hábiles (lunes a viernes) a `start_date`.

    Si `business_days < 0`, lanza `ValueError`. Los sábados (`weekday() == 5`) y
    domingos (`weekday() == 6`) no cuentan como días hábiles.

    Ejemplo:
        >>> add_business_days(date(2026, 10, 16), 3)  # Viernes + 3 días hábiles -> Miércoles
        datetime.date(2026, 10, 21)

    Complejidad objetivo:
        Tiempo: O(business_days) | Espacio: O(1)

    Pista:
        Avanza de a `timedelta(days=1)` y descuenta `remaining` solo cuando `current.weekday() < 5`.
    """
    # BEGIN_SOLUTION
    if business_days < 0:
        raise ValueError("business_days no puede ser negativo")
    current = start_date
    remaining = business_days
    while remaining > 0:
        current += timedelta(days=1)
        if current.weekday() < 5:
            remaining -= 1
    return current
    # END_SOLUTION


def summarize_csv_expenses(csv_content: str) -> dict[str, float]:
    """Lee un CSV en memoria con columnas `category,amount,status` y suma montos `APPROVED`.

    Ignora filas cuyo `status` (limpiando espacios y en mayúsculas) no sea `"APPROVED"`.
    Redondea los totales por categoría a 2 decimales.

    Ejemplo:
        >>> raw = "category,amount,status\\nCloud,100.5,APPROVED\\nCloud,50,REJECTED\\nCloud,20.25,APPROVED"
        >>> summarize_csv_expenses(raw)
        {'Cloud': 120.75}

    Complejidad objetivo:
        Tiempo: O(filas) | Espacio: O(categorias)

    Pista:
        Usa `csv.DictReader(io.StringIO(csv_content.strip()))`.
    """
    # BEGIN_SOLUTION
    if not csv_content.strip():
        return {}
    reader = csv.DictReader(io.StringIO(csv_content.strip()))
    totals: dict[str, float] = {}
    for row in reader:
        status = (row.get("status") or "").strip().upper()
        if status != "APPROVED":
            continue
        category = (row.get("category") or "").strip()
        amount = float(row.get("amount") or 0.0)
        totals[category] = round(totals.get(category, 0.0) + amount, 2)
    return totals
    # END_SOLUTION


def serialize_domain_payload(payload: dict[str, Any]) -> str:
    """Serializa un diccionario a JSON compacto con claves ordenadas soportando tipos extendidos.

    El serializador personalizado `default` debe convertir:
    - `datetime` o `date` -> su representación `.isoformat()`
    - `set` o `frozenset` -> una lista ordenada `sorted(obj)`
    - Cualquier otro tipo no soportado -> lanzar `TypeError`.

    Usa `separators=(",", ":")` y `sort_keys=True` para salida determinista.

    Ejemplo:
        >>> serialize_domain_payload({"tags": {"b", "a"}, "day": date(2026, 10, 16)})
        '{"day":"2026-10-16","tags":["a","b"]}'

    Complejidad objetivo:
        Tiempo: O(n log n) | Espacio: O(n)

    Pista:
        Define `def _default(obj: Any) -> Any:` y pásalo a `json.dumps(..., default=_default)`.
    """
    # BEGIN_SOLUTION
    def _default(obj: Any) -> Any:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, (set, frozenset)):
            return sorted(obj)
        raise TypeError(f"Tipo no serializable: {type(obj).__name__}")

    return json.dumps(payload, default=_default, sort_keys=True, separators=(",", ":"))
    # END_SOLUTION


def group_files_by_extension(paths: list[str]) -> dict[str, list[str]]:
    """Agrupa nombres base (`name`) por su extensión en minúsculas sin punto usando `PurePath`.

    Archivos sin extensión (ej. `"Dockerfile"`) se agrupan bajo la clave `"no_ext"`.
    Ordena alfabéticamente las listas de nombres de archivo de cada extensión.

    Ejemplo:
        >>> group_files_by_extension(["src/app.PY", "README.md", "Dockerfile", "tests/test_a.py"])
        {'no_ext': ['Dockerfile'], 'md': ['README.md'], 'py': ['app.PY', 'test_a.py']}

    Complejidad objetivo:
        Tiempo: O(n log n) | Espacio: O(n)

    Pista:
        Instancia `p = PurePath(raw_path)`, obtén `p.suffix.lstrip(".").lower() or "no_ext"`
        y guarda `p.name`.
    """
    # BEGIN_SOLUTION
    groups: dict[str, list[str]] = {}
    for raw in paths:
        p = PurePath(raw)
        ext = p.suffix.lstrip(".").lower() or "no_ext"
        groups.setdefault(ext, []).append(p.name)
    return {ext: sorted(names) for ext, names in groups.items()}
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_normalize_iso_to_utc() -> None:
    assert normalize_iso_to_utc("2026-10-16T09:30:00-05:00") == "2026-10-16T14:30:00Z"
    assert normalize_iso_to_utc("2026-10-16T14:30:00") == "2026-10-16T14:30:00Z"


def check_add_business_days() -> None:
    # 2026-10-16 es viernes -> +1 día hábil = lunes 19; +3 días hábiles = miércoles 21
    assert add_business_days(date(2026, 10, 16), 1) == date(2026, 10, 19)
    assert add_business_days(date(2026, 10, 16), 3) == date(2026, 10, 21)
    assert add_business_days(date(2026, 10, 16), 0) == date(2026, 10, 16)


def check_summarize_csv_expenses() -> None:
    csv_text = (
        "category,amount,status\n"
        "Cloud,100.50,APPROVED\n"
        "Cloud,50.00,REJECTED\n"
        "Food,30.25,approved\n"
        "Cloud,19.50,APPROVED\n"
    )
    assert summarize_csv_expenses(csv_text) == {"Cloud": 120.0, "Food": 30.25}


def check_serialize_domain_payload() -> None:
    out = serialize_domain_payload({"tags": {"py", "ai"}, "day": date(2026, 10, 16)})
    assert out == '{"day":"2026-10-16","tags":["ai","py"]}'


def check_group_files_by_extension() -> None:
    files = ["src/app.PY", "README.md", "Dockerfile", "tests/test_a.py"]
    assert group_files_by_extension(files) == {
        "no_ext": ["Dockerfile"],
        "md": ["README.md"],
        "py": ["app.PY", "test_a.py"],
    }


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. normalize_iso_to_utc", check_normalize_iso_to_utc),
    ("02. add_business_days", check_add_business_days),
    ("03. summarize_csv_expenses", check_summarize_csv_expenses),
    ("04. serialize_domain_payload", check_serialize_domain_payload),
    ("05. group_files_by_extension", check_group_files_by_extension),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 05_dates_files_and_serialization.py")
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
