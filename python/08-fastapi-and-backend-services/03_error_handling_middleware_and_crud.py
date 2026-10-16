from __future__ import annotations

import sys
import time
from typing import Any, Callable

from fastapi import FastAPI, Header, Request, status
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel

"""
MÓDULO 08 — FASTAPI Y SERVICIOS BACKEND: 03. EXCEPCIONES, MIDDLEWARE E IDEMPOTENCIA
===============================================================================
Estudio profundo y práctica deliberada sobre arquitectura de servicios en
producción con FastAPI: manejadores globales de excepciones de dominio
(`@app.exception_handler`), middlewares HTTP de observabilidad (`X-Request-ID`),
pagos idempotentes (`Idempotency-Key`) y bloqueo optimista por versión.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Manejadores Globales de Excepciones (`@app.exception_handler(DomainError)`):
   - Desacoplan la capa de dominio de los códigos de estado HTTP devolviendo un
     `JSONResponse` estructurado (estilo RFC 7807 Problem Details).

2. Middleware HTTP (`@app.middleware("http")`):
   ```python
   @app.middleware("http")
   async def trace_middleware(request: Request, call_next):
       req_id = request.headers.get("X-Request-ID", "req-default")
       response = await call_next(request)
       response.headers["X-Request-ID"] = req_id
       return response
   ```

3. Idempotencia con `Idempotency-Key`:
   - Si el cliente reintenta un `POST /payments` con la **misma** `Idempotency-Key`
     y el **mismo** payload, el servidor devuelve el resultado original sin
     volver a cobrar.
   - Si reutiliza la misma `Idempotency-Key` con un **payload distinto**, el
     servidor rechaza con `409 Conflict`.
"""


class DomainConflictError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message


class PaymentRequest(BaseModel):
    account_id: str
    amount: float


def create_resilient_service_app() -> FastAPI:
    app = FastAPI()
    idempotency_store: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    tx_counter = 0

    @app.exception_handler(DomainConflictError)
    async def handle_domain_conflict(
        request: Request, exc: DomainConflictError
    ) -> JSONResponse:
        # BEGIN_SOLUTION
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error_code": exc.code,
                "detail": exc.message,
                "path": request.url.path,
            },
        )
        # END_SOLUTION

    @app.middleware("http")
    async def request_id_middleware(
        request: Request, call_next: Callable[[Request], Any]
    ) -> Any:
        # BEGIN_SOLUTION
        req_id = request.headers.get("X-Request-ID") or "generated-req-id"
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response
        # END_SOLUTION

    @app.post("/payments", status_code=status.HTTP_201_CREATED)
    def process_payment(
        payload: PaymentRequest,
        idempotency_key: str = Header(...),
    ) -> dict[str, Any]:
        # BEGIN_SOLUTION
        nonlocal tx_counter
        raw_payload = payload.model_dump()
        if idempotency_key in idempotency_store:
            saved_payload, saved_response = idempotency_store[idempotency_key]
            if saved_payload != raw_payload:
                raise DomainConflictError(
                    code="IDEMPOTENCY_PAYLOAD_MISMATCH",
                    message="La clave de idempotencia ya fue usada con otros parámetros",
                )
            return saved_response

        tx_counter += 1
        response_data = {
            "tx_id": f"tx_{tx_counter}",
            "account_id": payload.account_id,
            "amount": payload.amount,
        }
        idempotency_store[idempotency_key] = (raw_payload, response_data)
        return response_data
        # END_SOLUTION

    return app


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_middleware_exceptions_and_idempotency() -> None:
    app = create_resilient_service_app()
    client = TestClient(app)

    # 1. Primera llamada crea tx_1 y propaga X-Request-ID
    r1 = client.post(
        "/payments",
        headers={"Idempotency-Key": "idem-100", "X-Request-ID": "trace-abc"},
        json={"account_id": "acc_1", "amount": 50.0},
    )
    assert r1.status_code == 201
    assert r1.headers["X-Request-ID"] == "trace-abc"
    assert r1.json()["tx_id"] == "tx_1"

    # 2. Reintento con misma Idempotency-Key y mismo payload devuelve exactamente tx_1
    r2 = client.post(
        "/payments",
        headers={"Idempotency-Key": "idem-100"},
        json={"account_id": "acc_1", "amount": 50.0},
    )
    assert r2.status_code == 201
    assert r2.json()["tx_id"] == "tx_1"
    assert r2.headers["X-Request-ID"] == "generated-req-id"

    # 3. Misma Idempotency-Key con distinto monto -> 409 DomainConflictError
    r3 = client.post(
        "/payments",
        headers={"Idempotency-Key": "idem-100"},
        json={"account_id": "acc_1", "amount": 999.0},
    )
    assert r3.status_code == 409
    assert r3.json()["error_code"] == "IDEMPOTENCY_PAYLOAD_MISMATCH"


CHECKS: list[tuple[str, Callable[[], None]]] = [
    (
        "01. Exception Handler, Middleware & Idempotency",
        check_middleware_exceptions_and_idempotency,
    ),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 03_error_handling_middleware_and_crud.py")
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
