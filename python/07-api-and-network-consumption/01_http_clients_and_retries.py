from __future__ import annotations

import asyncio
import sys
import time
from typing import Any, Callable

import httpx

"""
MÓDULO 07 — CONSUMO DE APIS Y RED: 01. CLIENTES HTTP Y REINTENTOS RESILIENTES
===============================================================================
Estudio profundo y práctica deliberada sobre clientes HTTP modernos con `httpx`,
pruebas 100% deterministas y offline mediante `httpx.MockTransport`,
clasificación de fallos transitorios vs fatales y Exponential Backoff.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. `httpx.Client` y `httpx.MockTransport` (Testing sin red):
   ```python
   def handler(request: httpx.Request) -> httpx.Response:
       return httpx.Response(200, json={"ok": True})

   transport = httpx.MockTransport(handler)
   with httpx.Client(transport=transport, base_url="https://api.test") as client:
       resp = client.get("/v1/users", params={"active": "true"})
       resp.raise_for_status()
       data = resp.json()
   ```

2. Errores Transitorios (Reintentables) vs Fatales:
   - **Reintentables:** `408 Request Timeout`, `429 Too Many Requests`,
     `500`, `502 Bad Gateway`, `503 Service Unavailable`, `504 Gateway Timeout`
     y excepciones de red `httpx.TransportError`.
   - **Fatales (NO reintentar):** `400 Bad Request`, `401 Unauthorized`,
     `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- Reutiliza siempre una instancia de `httpx.Client` o `httpx.AsyncClient` dentro
  de un bloque `with` / `async with` para aprovechar el *Connection Pooling*
  (keep-alive TCP/TLS) en vez de abrir un socket nuevo por cada petición.
"""

RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}


def is_retryable_status(status_code: int) -> bool:
    """Devuelve `True` si el código HTTP amerita un reintento automático."""
    # BEGIN_SOLUTION
    return status_code in RETRYABLE_STATUS_CODES
    # END_SOLUTION


def compute_exponential_backoff(
    attempt: int, base_delay: float = 0.1, max_delay: float = 5.0
) -> float:
    """Calcula el tiempo de espera `min(max_delay, base_delay * (2 ** attempt))` para `attempt >= 0`."""
    # BEGIN_SOLUTION
    if attempt < 0:
        raise ValueError("attempt no puede ser negativo")
    return round(min(max_delay, base_delay * (2**attempt)), 4)
    # END_SOLUTION


def fetch_json_with_retries(
    client: httpx.Client,
    url: str,
    max_attempts: int = 3,
) -> dict[str, Any]:
    """Realiza un `GET` con hasta `max_attempts` intentos ante códigos reintentables o `TransportError`."""
    # BEGIN_SOLUTION
    if max_attempts <= 0:
        raise ValueError("max_attempts debe ser positivo")

    for attempt in range(max_attempts):
        try:
            response = client.get(url)
        except httpx.TransportError:
            if attempt == max_attempts - 1:
                raise
            continue

        if is_retryable_status(response.status_code) and attempt < max_attempts - 1:
            continue

        response.raise_for_status()
        return dict(response.json())

    raise RuntimeError("Unreachable")
    # END_SOLUTION


async def fetch_batch_async(
    transport: httpx.AsyncBaseTransport,
    paths: list[str],
    concurrency: int = 3,
) -> list[dict[str, Any]]:
    """Descarga concurrentemente múltiples rutas usando `httpx.AsyncClient` y `asyncio.Semaphore`."""
    # BEGIN_SOLUTION
    sem = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(
        transport=transport, base_url="https://api.internal"
    ) as client:

        async def _get_one(path: str) -> dict[str, Any]:
            async with sem:
                resp = await client.get(path)
                resp.raise_for_status()
                return dict(resp.json())

        return list(await asyncio.gather(*(_get_one(p) for p in paths)))
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_status_and_backoff() -> None:
    assert is_retryable_status(503) is True
    assert is_retryable_status(429) is True
    assert is_retryable_status(404) is False
    assert compute_exponential_backoff(0, 0.1, 2.0) == 0.1
    assert compute_exponential_backoff(3, 0.1, 2.0) == 0.8
    assert compute_exponential_backoff(10, 0.1, 2.0) == 2.0


def check_fetch_json_with_retries() -> None:
    calls = 0

    def _handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls < 3:
            return httpx.Response(503, json={"error": "unavailable"})
        return httpx.Response(200, json={"status": "ok", "attempts": calls})

    with httpx.Client(
        transport=httpx.MockTransport(_handler), base_url="https://api.test"
    ) as client:
        data = fetch_json_with_retries(client, "/health", max_attempts=3)
        assert data == {"status": "ok", "attempts": 3}


def check_fetch_batch_async() -> None:
    def _handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"path": request.url.path})

    transport = httpx.MockTransport(_handler)
    res = asyncio.run(fetch_batch_async(transport, ["/a", "/b", "/c"], concurrency=2))
    assert res == [{"path": "/a"}, {"path": "/b"}, {"path": "/c"}]


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. Status & Exponential Backoff", check_status_and_backoff),
    ("02. fetch_json_with_retries (MockTransport)", check_fetch_json_with_retries),
    ("03. fetch_batch_async (AsyncClient)", check_fetch_batch_async),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 01_http_clients_and_retries.py")
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
