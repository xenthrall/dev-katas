from __future__ import annotations

from collections.abc import Generator
import sys
import time
from typing import Any, Callable

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.testclient import TestClient

"""
MÓDULO 08 — FASTAPI Y SERVICIOS BACKEND: 02. INYECCIÓN DE DEPENDENCIAS Y AUTH
===============================================================================
Estudio profundo y práctica deliberada sobre el motor de Inyección de
Dependencias (`Depends`) de FastAPI: extracción de credenciales Bearer,
guardias de autorización parametrizados mediante clases invocables (`RoleGuard`),
dependencias con ciclo de vida (`yield`) y reemplazo en tests con
`app.dependency_overrides`.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Dependencias Encadenadas (`Depends`):
   - Una función de dependencia puede depender a su vez de otra dependencia:
     `def require_admin(user: dict = Depends(get_current_user)): ...`

2. Dependencias Parametrizadas con Clases Invocables (`__call__`):
   - `Depends(RoleGuard({"admin", "ops"}))` instancia la clase con los roles
     permitidos y FastAPI invoca su método `__call__` en cada request.

3. Dependencias con `yield` (Teardown garantizado):
   - El código previo al `yield` se ejecuta antes del endpoint; el bloque
     `finally:` posterior al `yield` se ejecuta siempre al terminar la request.

4. Aislamiento en Tests (`app.dependency_overrides`):
   - `app.dependency_overrides[get_db] = get_mock_db` sustituye cualquier
     dependencia en producción sin modificar el código de los endpoints.
"""

TOKENS_DB: dict[str, dict[str, Any]] = {
    "tok_admin": {"username": "ada", "role": "admin"},
    "tok_viewer": {"username": "bob", "role": "viewer"},
}


def get_current_user(
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    """Valida cabecera `Authorization: Bearer <token>` o lanza `401 Unauthorized`."""
    # BEGIN_SOLUTION
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta token Bearer",
        )
    token = authorization.removeprefix("Bearer ").strip()
    user = TOKENS_DB.get(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
    return user
    # END_SOLUTION


class RoleGuard:
    """Dependencia invocable que exige que `user['role']` esté en `allowed_roles` (`403 Forbidden`)."""

    def __init__(self, allowed_roles: set[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(
        self, user: dict[str, Any] = Depends(get_current_user)
    ) -> dict[str, Any]:
        # BEGIN_SOLUTION
        if user.get("role") not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes",
            )
        return user
        # END_SOLUTION


def build_auth_app(lifecycle_events: list[str]) -> FastAPI:
    """Crea una app FastAPI con sesión gestionada por `yield` y rutas protegidas por `RoleGuard`."""
    app = FastAPI()

    def get_managed_session() -> Generator[str, None, None]:
        # BEGIN_SOLUTION
        lifecycle_events.append("SESSION_OPEN")
        try:
            yield "db_conn_active"
        finally:
            lifecycle_events.append("SESSION_CLOSE")
        # END_SOLUTION

    @app.get("/admin/metrics")
    def admin_metrics(
        user: dict[str, Any] = Depends(RoleGuard({"admin"})),
        session: str = Depends(get_managed_session),
    ) -> dict[str, str]:
        return {"user": str(user["username"]), "session": session}

    return app


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_di_and_auth_guards() -> None:
    events: list[str] = []
    app = build_auth_app(events)
    client = TestClient(app)

    # 1. Sin token -> 401
    assert client.get("/admin/metrics").status_code == 401

    # 2. Con rol viewer -> 403
    r_forbidden = client.get(
        "/admin/metrics", headers={"Authorization": "Bearer tok_viewer"}
    )
    assert r_forbidden.status_code == 403

    # 3. Con rol admin -> 200 y ciclo de vida SESSION_OPEN / SESSION_CLOSE ejecutado
    r_ok = client.get(
        "/admin/metrics", headers={"Authorization": "Bearer tok_admin"}
    )
    assert r_ok.status_code == 200
    assert r_ok.json() == {"user": "ada", "session": "db_conn_active"}
    assert events == ["SESSION_OPEN", "SESSION_CLOSE"]

    # 4. Verificar dependency_overrides
    app.dependency_overrides[get_current_user] = lambda: {
        "username": "override_root",
        "role": "admin",
    }
    r_override = client.get("/admin/metrics")
    assert r_override.status_code == 200
    assert r_override.json()["user"] == "override_root"


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. FastAPI Depends, RoleGuard & Yield Session", check_di_and_auth_guards),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 02_dependency_injection_and_auth.py")
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
