from __future__ import annotations

"""
================================================================================
KATA 05.01: CORRUTINAS, TAREAS Y CONCURRENCIA ESTRUCTURADA CON ASYNCIO
================================================================================

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
--------------------------------------------------------------------------------
1. Corrutinas y el Event Loop (`async def`, `await`, `asyncio.run`):
   ```python
   import asyncio

   async def fetch_data(item_id: int) -> dict[str, int]:
       await asyncio.sleep(0.01)  # Cede el control al Event Loop (I/O no bloqueante)
       return {"id": item_id}

   # Punto de entrada desde código síncrono:
   resultado = asyncio.run(fetch_data(42))
   ```

2. Ejecución Concurrente (`asyncio.gather` vs `asyncio.TaskGroup`):
   ```python
   # gather: ejecuta múltiples awaitables concurrentemente y preserva el orden
   resultados = await asyncio.gather(
       fetch_data(1),
       fetch_data(2),
       return_exceptions=False,  # Si True, devuelve la excepción en la lista en vez de propagarla
   )

   # TaskGroup (Python 3.11+ - Concurrencia Estructurada):
   # Si una tarea falla, cancela automáticamente las demás del grupo al salir del bloque.
   async with asyncio.TaskGroup() as tg:
       t1 = tg.create_task(fetch_data(1))
       t2 = tg.create_task(fetch_data(2))
   total = t1.result()["id"] + t2.result()["id"]
   ```

3. Control de Concurrencia (`asyncio.Semaphore`) y Timeouts (`asyncio.wait_for`):
   ```python
   sem = asyncio.Semaphore(5)  # Máximo 5 corrutinas dentro del bloque al mismo tiempo

   async def bounded_worker(x: int) -> int:
       async with sem:
           return await operación_lenta(x)

   try:
       res = await asyncio.wait_for(operación_lenta(1), timeout=0.5)
   except TimeoutError:
       res = -1  # Valor de respaldo (fallback)
   ```

4. Colas Asíncronas (`asyncio.Queue`) - Patrón Productor/Consumidor:
   ```python
   queue: asyncio.Queue[int] = asyncio.Queue()
   await queue.put(10)
   item = await queue.get()
   queue.task_done()     # Notifica que el ítem fue procesado
   await queue.join()    # Bloquea hasta que todos los ítems hayan llamado a task_done()
   ```

5. Carreras y Cancelación Limpia (`asyncio.wait` / `FIRST_COMPLETED`):
   ```python
   tasks = [asyncio.create_task(fn()) for fn in competidores]
   done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
   for p in pending:
       p.cancel()
   ```

🧠 MODELO MENTAL Y TRAMPAS COMUNES
--------------------------------------------------------------------------------
- Cooperación en un solo hilo: `asyncio` corre en UN SOLO HILO (single-threaded
  cooperative multitasking). Si llamas a `time.sleep(1)` o haces cálculo intensivo
  de CPU sin hacer `await`, congelas TODO el Event Loop.
- Llamar a `coro()` NO ejecuta la corrutina; solo crea el objeto corrutina. Para
  programarla inmediatamente en el loop necesitas `asyncio.create_task(coro())`
  o `tg.create_task(coro())`.
- Siempre limpia las tareas pendientes (`task.cancel()`) cuando hagas carreras
  (`FIRST_COMPLETED`) para evitar fugas de recursos o warnings de tareas huérfanas.
================================================================================
"""

import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

T = TypeVar("T")


# ==============================================================================
# EJERCICIO 1: Concurrencia acotada con Semaphore y gather
# ==============================================================================
async def fetch_all_bounded(
    ids: list[int],
    worker_fn: Callable[[int], Awaitable[dict[str, Any]]],
    max_concurrency: int,
) -> list[dict[str, Any]]:
    """
    Ejecuta `worker_fn(item_id)` para cada ID en `ids` de forma concurrente,
    garantizando que NUNCA haya más de `max_concurrency` llamadas activas
    simultáneamente.

    Requisitos:
    - Si `max_concurrency <= 0`, lanza `ValueError`.
    - Usa `asyncio.Semaphore(max_concurrency)` y `asyncio.gather`.
    - Debe preservar el orden exacto correspondiente a la lista `ids` de entrada.
    """
    # BEGIN_SOLUTION
    if max_concurrency <= 0:
        raise ValueError("max_concurrency must be greater than 0")

    semaphore = asyncio.Semaphore(max_concurrency)

    async def _bounded_call(item_id: int) -> dict[str, Any]:
        async with semaphore:
            return await worker_fn(item_id)

    return list(await asyncio.gather(*(_bounded_call(i) for i in ids)))
    # END_SOLUTION


# ==============================================================================
# EJERCICIO 2: Timeout con valor de respaldo (Fallback)
# ==============================================================================
async def fetch_with_timeout_fallback(
    coro: Awaitable[T],
    timeout: float,
    fallback: T,
) -> T:
    """
    Espera la ejecución de `coro` con un tiempo límite máximo de `timeout` segundos.
    Si la operación excede el tiempo límite (`TimeoutError`), devuelve `fallback`.
    """
    # BEGIN_SOLUTION
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except TimeoutError:
        return fallback
    # END_SOLUTION


# ==============================================================================
# EJERCICIO 3: Concurrencia estructurada con asyncio.TaskGroup
# ==============================================================================
async def run_task_group_pipeline(
    tasks_fns: list[Callable[[], Awaitable[int]]],
) -> int:
    """
    Recibe una lista de funciones sin argumentos que devuelven corrutinas con un `int`.
    Programa todas las tareas dentro de un bloque `async with asyncio.TaskGroup() as tg:`
    y retorna la suma total de sus resultados.
    """
    # BEGIN_SOLUTION
    if not tasks_fns:
        return 0

    created_tasks: list[asyncio.Task[int]] = []
    async with asyncio.TaskGroup() as tg:
        for fn in tasks_fns:
            created_tasks.append(tg.create_task(fn()))

    return sum(task.result() for task in created_tasks)
    # END_SOLUTION


# ==============================================================================
# EJERCICIO 4: Cola Productor-Consumidor con asyncio.Queue
# ==============================================================================
async def run_producer_consumer_queue(
    items: list[int],
    num_workers: int,
) -> list[int]:
    """
    Procesa los elementos de `items` usando una `asyncio.Queue` y `num_workers`
    trabajadores concurrentes.

    Cada trabajador debe:
    - Extraer un número `x` de la cola.
    - Simular un micro-trabajo asíncrono (`await asyncio.sleep(0.001)`).
    - Guardar `x * x` (el cuadrado) en una colección de resultados.
    - Marcar la tarea como completada con `queue.task_done()`.

    Espera a que la cola se vacíe con `await queue.join()`, cancela los workers
    y devuelve la lista de resultados ordenada de menor a mayor.
    """
    # BEGIN_SOLUTION
    if num_workers <= 0:
        raise ValueError("num_workers must be positive")
    if not items:
        return []

    queue: asyncio.Queue[int] = asyncio.Queue()
    results: list[int] = []

    for item in items:
        queue.put_nowait(item)

    async def _worker() -> None:
        while True:
            val = await queue.get()
            try:
                await asyncio.sleep(0.001)
                results.append(val * val)
            finally:
                queue.task_done()

    workers = [asyncio.create_task(_worker()) for _ in range(num_workers)]
    await queue.join()

    for w in workers:
        w.cancel()
    await asyncio.gather(*workers, return_exceptions=True)

    return sorted(results)
    # END_SOLUTION


# ==============================================================================
# EJERCICIO 5: Carrera al primer éxito con cancelación limpia
# ==============================================================================
async def race_first_successful(
    competitors: list[Callable[[], Awaitable[str]]],
) -> str:
    """
    Ejecuta todas las funciones competidoras en paralelo y devuelve el primer
    resultado exitoso (`str`), cancelando inmediatamente todas las tareas restantes.

    Requisitos:
    - Si `competitors` está vacío, o si TODAS las tareas lanzan excepción,
      debe lanzar `RuntimeError("All competitors failed")`.
    - Todas las tareas que sigan pendientes cuando se encuentre la ganadora
      deben ser canceladas limpiamente (`task.cancel()`).
    """
    # BEGIN_SOLUTION
    if not competitors:
        raise RuntimeError("All competitors failed")

    pending: set[asyncio.Task[str]] = {
        asyncio.create_task(fn()) for fn in competitors
    }

    try:
        while pending:
            done, pending = await asyncio.wait(
                pending, return_when=asyncio.FIRST_COMPLETED
            )
            for task in done:
                exc = task.exception()
                if exc is None:
                    return task.result()
    finally:
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)

    raise RuntimeError("All competitors failed")
    # END_SOLUTION


# ==============================================================================
# TESTS Y VERIFICACIÓN
# ==============================================================================
def _verify_bounded() -> None:
    active = 0
    max_seen = 0

    async def mock_worker(item_id: int) -> dict[str, Any]:
        nonlocal active, max_seen
        active += 1
        max_seen = max(max_seen, active)
        await asyncio.sleep(0.004)
        active -= 1
        return {"id": item_id, "val": item_id * 10}

    res = asyncio.run(fetch_all_bounded([1, 2, 3, 4, 5, 6], mock_worker, max_concurrency=2))
    assert [r["id"] for r in res] == [1, 2, 3, 4, 5, 6]
    assert max_seen <= 2, f"Se excedió max_concurrency: {max_seen}"


def _verify_timeout() -> None:
    async def fast_op() -> str:
        await asyncio.sleep(0.002)
        return "ok"

    async def slow_op() -> str:
        await asyncio.sleep(0.05)
        return "too_late"

    assert asyncio.run(fetch_with_timeout_fallback(fast_op(), 0.02, "fallback")) == "ok"
    assert asyncio.run(fetch_with_timeout_fallback(slow_op(), 0.005, "fallback")) == "fallback"


def _verify_task_group() -> None:
    async def make_val(v: int) -> int:
        await asyncio.sleep(0.002)
        return v

    fns = [lambda v=i: make_val(v) for i in (10, 20, 30, 40)]
    total = asyncio.run(run_task_group_pipeline(fns))
    assert total == 100
    assert asyncio.run(run_task_group_pipeline([])) == 0


def _verify_queue() -> None:
    res = asyncio.run(run_producer_consumer_queue([5, 1, 4, 2, 3], num_workers=3))
    assert res == [1, 4, 9, 16, 25]
    assert asyncio.run(run_producer_consumer_queue([], num_workers=2)) == []


def _verify_race() -> None:
    cancelled_slow = False

    async def failing_fast() -> str:
        await asyncio.sleep(0.001)
        raise ValueError("boom")

    async def winner() -> str:
        await asyncio.sleep(0.004)
        return "ganador"

    async def slow_loser() -> str:
        nonlocal cancelled_slow
        try:
            await asyncio.sleep(0.1)
            return "perdedor"
        except asyncio.CancelledError:
            cancelled_slow = True
            raise

    ans = asyncio.run(race_first_successful([failing_fast, winner, slow_loser]))
    assert ans == "ganador"
    assert cancelled_slow is True

    try:
        asyncio.run(race_first_successful([failing_fast]))
        raise AssertionError("Debió lanzar RuntimeError")
    except RuntimeError:
        pass


def test_kata() -> None:
    _verify_bounded()
    _verify_timeout()
    _verify_task_group()
    _verify_queue()
    _verify_race()


def run_verification() -> None:
    checks = [
        ("Ejercicio 1: fetch_all_bounded", _verify_bounded),
        ("Ejercicio 2: fetch_with_timeout_fallback", _verify_timeout),
        ("Ejercicio 3: run_task_group_pipeline", _verify_task_group),
        ("Ejercicio 4: run_producer_consumer_queue", _verify_queue),
        ("Ejercicio 5: race_first_successful", _verify_race),
    ]
    print("=" * 72)
    print("⚡ VERIFICACIÓN: KATA 05.01 - ASYNCIO COROUTINES AND TASKS")
    print("=" * 72)
    passed = 0
    for title, fn in checks:
        t0 = time.perf_counter()
        try:
            fn()
            ms = (time.perf_counter() - t0) * 1000
            print(f"✅ [PASS] {title} ({ms:.2f} ms)")
            passed += 1
        except NotImplementedError:
            print(f"⏳ [PENDIENTE] {title}")
        except Exception as exc:
            print(f"❌ [FAIL] {title} -> {type(exc).__name__}: {exc}")
    print("-" * 72)
    print(f"Resultado final: {passed}/{len(checks)} ejercicios superados.")
    if passed < len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    run_verification()
