from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, AsyncIterator
import contextlib
import sys
import time
from typing import Callable, TypeVar

"""
MÓDULO 05 — CONCURRENCIA Y ASYNC: 02. ITERADORES Y STREAMS ASÍNCRONOS
===============================================================================
Estudio profundo y práctica deliberada sobre el protocolo de iteración
asíncrona (`__aiter__`, `__anext__`, `async for`), generadores asíncronos,
gestores de contexto asíncronos (`@asynccontextmanager`) y sincronización con
`asyncio.Event`.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Protocolo Iterador Asíncrono (`async for x in aiterable:`):
   - `__aiter__(self)` es un método normal (`def`, NO `async def`) que devuelve
     el iterador asíncrono (`self`).
   - `async def __anext__(self)` es una corrutina que devuelve el siguiente
     elemento o lanza `StopAsyncIteration`.

2. Generadores Asíncronos (`async def ... yield`):
   - Una función `async def` que contiene `yield` produce un `AsyncGenerator`.
   - Se consume con `async for item in agen:` o `await anext(agen)`.

3. Gestor de Contexto Asíncrono (`async with`):
   - `@contextlib.asynccontextmanager`: Permite hacer `await` tanto en la fase
     de adquisición previa al `yield` como en el bloque `finally:` de cierre.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- En un iterador asíncrono, el error para detener el bucle es
  `StopAsyncIteration`, NO `StopIteration`.
"""

T = TypeVar("T")


class AsyncRangeStreamer:
    """Iterador asíncrono personalizado que emite enteros en `[start, stop)`."""

    def __init__(self, start: int, stop: int, delay: float = 0.001) -> None:
        self.current = start
        self.stop = stop
        self.delay = delay

    def __aiter__(self) -> AsyncRangeStreamer:
        # BEGIN_SOLUTION
        return self
        # END_SOLUTION

    async def __anext__(self) -> int:
        # BEGIN_SOLUTION
        if self.current >= self.stop:
            raise StopAsyncIteration
        await asyncio.sleep(self.delay)
        val = self.current
        self.current += 1
        return val
        # END_SOLUTION


async def async_batch_stream(
    source: AsyncIterator[T], batch_size: int
) -> AsyncGenerator[list[T], None]:
    """Agrupa un flujo asíncrono `source` en lotes de tamaño máximo `batch_size`."""
    # BEGIN_SOLUTION
    if batch_size <= 0:
        raise ValueError("batch_size debe ser positivo")
    batch: list[T] = []
    async for item in source:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
    # END_SOLUTION


@contextlib.asynccontextmanager
async def managed_async_session(audit_log: list[str]) -> AsyncIterator[str]:
    """Registra `'CONNECT'`, cede `'session_active'` y garantiza `'DISCONNECT'` al salir."""
    # BEGIN_SOLUTION
    await asyncio.sleep(0.001)
    audit_log.append("CONNECT")
    try:
        yield "session_active"
    finally:
        await asyncio.sleep(0.001)
        audit_log.append("DISCONNECT")
    # END_SOLUTION


async def coordinate_with_event() -> list[str]:
    """Sincroniza un worker que espera a que un inicializador active un `asyncio.Event`."""
    # BEGIN_SOLUTION
    ready_event = asyncio.Event()
    timeline: list[str] = []

    async def _worker() -> None:
        timeline.append("worker_waiting")
        await ready_event.wait()
        timeline.append("worker_running")

    async def _initializer() -> None:
        await asyncio.sleep(0.002)
        timeline.append("init_ready")
        ready_event.set()

    await asyncio.gather(_worker(), _initializer())
    return timeline
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_async_range_streamer() -> None:
    async def _run() -> list[int]:
        return [x async for x in AsyncRangeStreamer(10, 14, delay=0.0005)]

    assert asyncio.run(_run()) == [10, 11, 12, 13]


def check_async_batch_stream() -> None:
    async def _run() -> list[list[int]]:
        streamer = AsyncRangeStreamer(1, 6, delay=0.0005)
        return [batch async for batch in async_batch_stream(streamer, batch_size=2)]

    assert asyncio.run(_run()) == [[1, 2], [3, 4], [5]]


def check_managed_async_session() -> None:
    log: list[str] = []

    async def _run() -> None:
        try:
            async with managed_async_session(log) as token:
                log.append(f"USE:{token}")
                raise RuntimeError("boom")
        except RuntimeError:
            pass

    asyncio.run(_run())
    assert log == ["CONNECT", "USE:session_active", "DISCONNECT"]


def check_coordinate_with_event() -> None:
    assert asyncio.run(coordinate_with_event()) == [
        "worker_waiting",
        "init_ready",
        "worker_running",
    ]


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. AsyncRangeStreamer (__aiter__/__anext__)", check_async_range_streamer),
    ("02. async_batch_stream (AsyncGenerator)", check_async_batch_stream),
    ("03. managed_async_session (@asynccontextmanager)", check_managed_async_session),
    ("04. coordinate_with_event (asyncio.Event)", check_coordinate_with_event),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 02_async_iterators_and_streams.py")
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
