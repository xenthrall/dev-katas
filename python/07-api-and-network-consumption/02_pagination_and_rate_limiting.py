from __future__ import annotations

from collections.abc import Generator
import sys
import time
from typing import Any, Callable

import httpx

"""
MÓDULO 07 — CONSUMO DE APIS Y RED: 02. PAGINACIÓN Y RATE LIMITING (TOKEN BUCKET)
===============================================================================
Estudio profundo y práctica deliberada sobre consumo perezoso de APIs paginadas
por cursor (`next_cursor`), paginación `offset`/`limit` y control de tasa de
peticiones mediante el algoritmo **Token Bucket** con reloj inyectable.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Paginación por Cursor con Generadores (`yield from`):
   - En lugar de cargar 100 páginas en memoria antes de procesar el primer ítem,
     un generador pide la página actual, emite sus ítems (`yield from items`)
     y sigue pidiendo mientras `next_cursor` no sea `None`.

2. Algoritmo Token Bucket (Cubeta de Tokens):
   - Capacidad máxima `capacity` y velocidad de recarga `refill_rate` (tokens/seg).
   - Al llegar una petición en `now = clock_fn()`:
     1. Recarga `elapsed = max(0.0, now - last_time)` ->
        `tokens = min(capacity, tokens + elapsed * refill_rate)`.
     2. Si `tokens >= requested`, descuenta `tokens -= requested` y permite (`True`).
     3. De lo contrario, rechaza (`False`).

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- Inyectar `clock_fn: Callable[[], float] = time.monotonic` permite probar
  algoritmos dependientes del tiempo de forma instantánea sin usar `time.sleep()`.
"""


def iterate_cursor_pages(
    client: httpx.Client,
    endpoint: str,
) -> Generator[dict[str, Any], None, None]:
    """Itera perezosamente sobre todas las páginas de un endpoint con `next_cursor`."""
    # BEGIN_SOLUTION
    cursor: str | None = None
    while True:
        params = {"cursor": cursor} if cursor is not None else {}
        resp = client.get(endpoint, params=params)
        resp.raise_for_status()
        payload = resp.json()
        for item in payload.get("items", []):
            yield item
        cursor = payload.get("next_cursor")
        if not cursor:
            break
    # END_SOLUTION


def harvest_offset_pages(
    client: httpx.Client,
    endpoint: str,
    page_size: int,
    max_items: int,
) -> list[dict[str, Any]]:
    """Descarga páginas usando `offset` y `limit` hasta alcanzar `max_items` o una página vacía."""
    # BEGIN_SOLUTION
    collected: list[dict[str, Any]] = []
    offset = 0
    while len(collected) < max_items:
        resp = client.get(endpoint, params={"offset": offset, "limit": page_size})
        resp.raise_for_status()
        batch = resp.json().get("items", [])
        if not batch:
            break
        remaining = max_items - len(collected)
        collected.extend(batch[:remaining])
        if len(batch) < page_size:
            break
        offset += page_size
    return collected
    # END_SOLUTION


class TokenBucketRateLimiter:
    """Rate Limiter basado en el algoritmo Token Bucket con reloj inyectable."""

    def __init__(
        self,
        capacity: float,
        refill_rate_per_sec: float,
        clock_fn: Callable[[], float] = time.monotonic,
    ) -> None:
        # BEGIN_SOLUTION
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate_per_sec)
        self.clock_fn = clock_fn
        self.tokens = float(capacity)
        self.last_refill = self.clock_fn()
        # END_SOLUTION

    def allow_request(self, cost: float = 1.0) -> bool:
        """Recarga tokens según el tiempo transcurrido y consume `cost` si hay saldo suficiente."""
        # BEGIN_SOLUTION
        now = self.clock_fn()
        elapsed = max(0.0, now - self.last_refill)
        self.last_refill = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False
        # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_iterate_cursor_pages() -> None:
    pages = {
        None: {"items": [{"id": 1}, {"id": 2}], "next_cursor": "cur_2"},
        "cur_2": {"items": [{"id": 3}], "next_cursor": None},
    }

    def _handler(request: httpx.Request) -> httpx.Response:
        cur = request.url.params.get("cursor")
        return httpx.Response(200, json=pages[cur])

    with httpx.Client(
        transport=httpx.MockTransport(_handler), base_url="https://api.test"
    ) as client:
        items = list(iterate_cursor_pages(client, "/events"))
        assert items == [{"id": 1}, {"id": 2}, {"id": 3}]


def check_harvest_offset_pages() -> None:
    all_rows = [{"id": i} for i in range(1, 10)]

    def _handler(request: httpx.Request) -> httpx.Response:
        offset = int(request.url.params["offset"])
        limit = int(request.url.params["limit"])
        return httpx.Response(200, json={"items": all_rows[offset : offset + limit]})

    with httpx.Client(
        transport=httpx.MockTransport(_handler), base_url="https://api.test"
    ) as client:
        res = harvest_offset_pages(client, "/rows", page_size=3, max_items=5)
        assert res == [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}]


def check_token_bucket_rate_limiter() -> None:
    fake_now = 100.0
    limiter = TokenBucketRateLimiter(
        capacity=2.0, refill_rate_per_sec=1.0, clock_fn=lambda: fake_now
    )
    assert limiter.allow_request(1.0) is True
    assert limiter.allow_request(1.0) is True
    assert limiter.allow_request(1.0) is False
    fake_now += 1.5  # Se recargan 1.5 tokens
    assert limiter.allow_request(1.0) is True


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. iterate_cursor_pages (Cursor Generator)", check_iterate_cursor_pages),
    ("02. harvest_offset_pages (Offset/Limit)", check_harvest_offset_pages),
    ("03. TokenBucketRateLimiter", check_token_bucket_rate_limiter),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 02_pagination_and_rate_limiting.py")
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
