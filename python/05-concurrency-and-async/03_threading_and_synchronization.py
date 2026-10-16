from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import threading
import time
from typing import Callable

"""
MÓDULO 05 — CONCURRENCIA Y ASYNC: 03. THREADING Y SINCRONIZACIÓN
===============================================================================
Estudio profundo y práctica deliberada sobre multihilo en Python (`threading`),
exclusión mutua con `Lock` y `RLock`, ejecución concurrente con
`ThreadPoolExecutor` y aislamiento de estado por hilo con `threading.local()`.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. `threading.Lock` vs `threading.RLock`:
   - `Lock`: Candado básico. Si el MISMO hilo intenta adquirirlo dos veces
     seguidas sin liberarlo, provoca un **Deadlock** (bloqueo infinito).
   - `RLock` (Reentrant Lock): Permite que el mismo hilo propietario vuelva a
     adquirirlo múltiples veces de forma segura (por ejemplo, cuando un método
     público sincronizado llama a otro método público sincronizado de la misma
     instancia).

2. `ThreadPoolExecutor` y `as_completed`:
   ```python
   with ThreadPoolExecutor(max_workers=4) as pool:
       futuros = {pool.submit(fn, item): item for item in items}
       for fut in as_completed(futuros):
           resultado = fut.result()
   ```

3. `threading.local()`:
   - Crea un contenedor cuyos atributos son independientes y privados para cada
     hilo del sistema operativo.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- Incluso con el GIL, operaciones compuestas como `self.balance += x` NO son
  atómicas a nivel de bytecode (`LOAD_ATTR`, `BINARY_OP`, `STORE_ATTR`), por lo
  que el cambio de contexto entre hilos puede ocurrir a mitad de camino. Usa
  siempre `with self._lock:` al mutar estado compartido.
"""


class ThreadSafeCounter:
    """Contador seguro para múltiples hilos protegido por `threading.Lock`."""

    def __init__(self) -> None:
        # BEGIN_SOLUTION
        self._value = 0
        self._lock = threading.Lock()
        # END_SOLUTION

    def increment(self, delta: int = 1) -> int:
        # BEGIN_SOLUTION
        with self._lock:
            self._value += delta
            return self._value
        # END_SOLUTION

    @property
    def value(self) -> int:
        # BEGIN_SOLUTION
        with self._lock:
            return self._value
        # END_SOLUTION


class ReentrantLedger:
    """Libro contable que usa `threading.RLock` para permitir llamadas anidadas en el mismo hilo."""

    def __init__(self) -> None:
        # BEGIN_SOLUTION
        self._rlock = threading.RLock()
        self.entries: list[int] = []
        # END_SOLUTION

    def add_entry(self, amount: int) -> None:
        # BEGIN_SOLUTION
        with self._rlock:
            self.entries.append(amount)
        # END_SOLUTION

    def add_batch_with_bonus(self, amounts: list[int], bonus: int) -> int:
        """Adquiere el `RLock` y llama internamente a `self.add_entry(...)` sin causar deadlock."""
        # BEGIN_SOLUTION
        with self._rlock:
            for amt in amounts:
                self.add_entry(amt)
            self.add_entry(bonus)
            return sum(self.entries)
        # END_SOLUTION


def execute_parallel_io_tasks(
    inputs: list[int],
    worker_fn: Callable[[int], int],
    max_workers: int = 4,
) -> dict[int, int]:
    """Ejecuta `worker_fn(x)` en un `ThreadPoolExecutor` y devuelve `{x: resultado}`."""
    # BEGIN_SOLUTION
    results: dict[int, int] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_input = {executor.submit(worker_fn, x): x for x in inputs}
        for future in as_completed(future_to_input):
            inp = future_to_input[future]
            results[inp] = future.result()
    return results
    # END_SOLUTION


def isolate_thread_context_ids(worker_names: list[str]) -> dict[str, str]:
    """Demuestra aislamiento de `threading.local()` asignando un contexto distinto en cada hilo."""
    # BEGIN_SOLUTION
    local_ctx = threading.local()
    observed: dict[str, str] = {}
    lock = threading.Lock()

    def _run_worker(name: str) -> None:
        local_ctx.request_id = f"REQ-{name}"
        time.sleep(0.002)
        with lock:
            observed[name] = local_ctx.request_id

    threads = [threading.Thread(target=_run_worker, args=(n,)) for n in worker_names]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return observed
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_thread_safe_counter() -> None:
    counter = ThreadSafeCounter()

    def _bump() -> None:
        for _ in range(200):
            counter.increment(1)

    threads = [threading.Thread(target=_bump) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert counter.value == 1000


def check_reentrant_ledger() -> None:
    ledger = ReentrantLedger()
    total = ledger.add_batch_with_bonus([10, 20, 30], bonus=5)
    assert total == 65
    assert ledger.entries == [10, 20, 30, 5]


def check_execute_parallel_io_tasks() -> None:
    def _io_task(x: int) -> int:
        time.sleep(0.001)
        return x * 10

    res = execute_parallel_io_tasks([1, 2, 3, 4], _io_task, max_workers=4)
    assert res == {1: 10, 2: 20, 3: 30, 4: 40}


def check_isolate_thread_context_ids() -> None:
    res = isolate_thread_context_ids(["alpha", "beta", "gamma"])
    assert res == {"alpha": "REQ-alpha", "beta": "REQ-beta", "gamma": "REQ-gamma"}


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. ThreadSafeCounter (Lock)", check_thread_safe_counter),
    ("02. ReentrantLedger (RLock)", check_reentrant_ledger),
    ("03. execute_parallel_io_tasks (ThreadPoolExecutor)", check_execute_parallel_io_tasks),
    ("04. isolate_thread_context_ids (threading.local)", check_isolate_thread_context_ids),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 03_threading_and_synchronization.py")
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
