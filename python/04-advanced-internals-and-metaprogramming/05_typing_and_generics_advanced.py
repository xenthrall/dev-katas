from __future__ import annotations

import sys
import time
from typing import (
    Annotated,
    Any,
    Callable,
    Generic,
    TypedDict,
    TypeGuard,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
)

"""
MÓDULO 04 — INTERNALS Y METAPROGRAMACIÓN: 05. TIPADO AVANZADO Y GENÉRICOS
===============================================================================
Estudio profundo y práctica deliberada sobre el sistema de tipos gradual de
Python (`Generic[T]`, `TypeVar`, `TypedDict`, `TypeGuard` y metadatos en
tiempo de ejecución con `Annotated` + `get_type_hints`).

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Contenedores Genéricos (`Generic[T, E]`):
   - Permiten parametrizar clases de dominio como `Result[T, E]` o `Page[T]`
     manteniendo seguridad de tipos extremo a extremo.

2. Estrechamiento de Tipos con `TypeGuard[T]` (PEP 647):
   - Una función `def is_str_list(val: list[object]) -> TypeGuard[list[str]]:`
     le indica al analizador estático que, dentro del bloque `if is_str_list(x):`,
     el tipo de `x` pasa a ser `list[str]`.

3. Metadatos en Runtime con `Annotated[Tipo, meta1, ...]` (PEP 593):
   - Base arquitectónica de **FastAPI (`Query`, `Depends`)** y **Pydantic v2**.
   - Se inspecciona en runtime con `get_type_hints(cls, include_extras=True)`,
     `get_origin(hint) is Annotated` y `get_args(hint)`.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- Con `from __future__ import annotations`, todas las anotaciones se guardan
  como cadenas en `__annotations__`. Usa siempre `typing.get_type_hints(obj, include_extras=True)`
  para resolverlas a objetos de tipo reales en runtime.
"""

T = TypeVar("T")
U = TypeVar("U")


class ResultBox(Generic[T]):
    """Mónada/Contenedor genérico `ResultBox[T]` que encapsula un valor exitoso o un error."""

    def __init__(self, value: T | None, error: str | None = None) -> None:
        self._value = value
        self._error = error

    @classmethod
    def ok(cls, value: T) -> ResultBox[T]:
        # BEGIN_SOLUTION
        return cls(value=value, error=None)
        # END_SOLUTION

    @classmethod
    def err(cls, error: str) -> ResultBox[Any]:
        # BEGIN_SOLUTION
        return cls(value=None, error=error)
        # END_SOLUTION

    @property
    def is_ok(self) -> bool:
        # BEGIN_SOLUTION
        return self._error is None
        # END_SOLUTION

    def map(self, fn: Callable[[T], U]) -> ResultBox[U]:
        """Si `is_ok`, transforma el valor con `fn`; si es error, propaga el mismo error."""
        # BEGIN_SOLUTION
        if not self.is_ok:
            return ResultBox.err(self._error or "error")
        return ResultBox.ok(fn(self._value))  # type: ignore[arg-type]
        # END_SOLUTION

    def unwrap_or(self, default: T) -> T:
        # BEGIN_SOLUTION
        if self.is_ok and self._value is not None:
            return self._value
        return default
        # END_SOLUTION


class UserPayloadDict(TypedDict):
    id: int
    username: str
    roles: list[str]


def is_valid_user_payload(data: dict[str, Any]) -> TypeGuard[UserPayloadDict]:
    """Verifica en runtime si un diccionario cumple exactamente el esquema `UserPayloadDict`."""
    # BEGIN_SOLUTION
    return (
        isinstance(data.get("id"), int)
        and not isinstance(data.get("id"), bool)
        and isinstance(data.get("username"), str)
        and bool(data["username"].strip())
        and isinstance(data.get("roles"), list)
        and all(isinstance(r, str) for r in data["roles"])
    )
    # END_SOLUTION


class MaxLen:
    """Metadato para usar dentro de `Annotated[str, MaxLen(10)]`."""

    def __init__(self, limit: int) -> None:
        self.limit = limit


def validate_annotated_max_lengths(instance: Any) -> list[str]:
    """Inspecciona los campos `Annotated[..., MaxLen(k)]` de `instance` y devuelve los nombres que exceden `k`."""
    # BEGIN_SOLUTION
    hints = get_type_hints(type(instance), include_extras=True)
    violations: list[str] = []
    for field_name, hint in hints.items():
        if get_origin(hint) is Annotated:
            _, *metadata = get_args(hint)
            val = getattr(instance, field_name, None)
            if isinstance(val, str):
                for meta in metadata:
                    if isinstance(meta, MaxLen) and len(val) > meta.limit:
                        violations.append(field_name)
    return violations
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_result_box_generic() -> None:
    r_ok = ResultBox.ok(10).map(lambda x: x * 3)
    assert r_ok.is_ok is True
    assert r_ok.unwrap_or(0) == 30

    r_err: ResultBox[int] = ResultBox.err("db_down").map(lambda x: x * 3)
    assert r_err.is_ok is False
    assert r_err.unwrap_or(99) == 99


def check_type_guard_user_payload() -> None:
    valid = {"id": 1, "username": "ada", "roles": ["admin", "dev"]}
    invalid_bool = {"id": True, "username": "ada", "roles": []}
    invalid_roles = {"id": 2, "username": "bob", "roles": [123]}
    assert is_valid_user_payload(valid) is True
    assert is_valid_user_payload(invalid_bool) is False
    assert is_valid_user_payload(invalid_roles) is False


def check_annotated_metadata_validation() -> None:
    class ProfileSchema:
        handle: Annotated[str, MaxLen(5)]
        bio: Annotated[str, MaxLen(12)]

        def __init__(self, handle: str, bio: str) -> None:
            self.handle = handle
            self.bio = bio

    ok_prof = ProfileSchema("ada", "Ingeniera")
    bad_prof = ProfileSchema("nombre_muy_largo", "Bio corta")
    assert validate_annotated_max_lengths(ok_prof) == []
    assert validate_annotated_max_lengths(bad_prof) == ["handle"]


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. ResultBox (Generic[T])", check_result_box_generic),
    ("02. is_valid_user_payload (TypeGuard)", check_type_guard_user_payload),
    ("03. validate_annotated_max_lengths (Annotated)", check_annotated_metadata_validation),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 05_typing_and_generics_advanced.py")
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
