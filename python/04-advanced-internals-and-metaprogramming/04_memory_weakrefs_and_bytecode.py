from __future__ import annotations

import dis
import gc
import sys
import time
from typing import Any, Callable
import weakref

"""
MÓDULO 04 — INTERNALS Y METAPROGRAMACIÓN: 04. MEMORIA, WEAKREFS Y BYTECODE
===============================================================================
Estudio profundo y práctica deliberada sobre gestión de referencias débiles
(`weakref`) para evitar ciclos y fugas de memoria en cachés y árboles, e
inspección de instrucciones de la Máquina Virtual de CPython (`dis`).

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Referencias Débiles (`weakref`):
   - Una referencia normal incrementa `ob_refcnt` e impide que el objeto sea
     recolectado por el Garbage Collector.
   - `r = weakref.ref(obj)` crea un puntero débil que NO incrementa `ob_refcnt`.
     Al llamar `r()`, devuelve el `obj` si sigue vivo en memoria, o `None` si
     ya fue destruido.
   - `weakref.WeakValueDictionary()`: Diccionario cuyas entradas desaparecen
     automáticamente cuando ninguna otra parte del programa referencia al valor.

2. Desensamblado de Bytecode (`dis`):
   - `dis.get_instructions(fn)`: Iterador de objetos `dis.Instruction` con
     `instr.opname`, `instr.argval`, `instr.offset`.
   - `fn.__code__.co_consts`, `fn.__code__.co_varnames`: Tuplas de constantes y
     variables locales compiladas en el objeto de código.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- En árboles doblemente enlazados (`padre.children` apunta al hijo y `hijo.parent`
  apunta al padre), se forma un ciclo de referencias. Si `hijo._parent_ref = weakref.ref(padre)`,
  el árbol se libera instantáneamente por conteo de referencias al soltar la raíz.
"""


class HeavyResource:
    """Objeto personalizable que soporta `weakref`."""

    def __init__(self, resource_id: str) -> None:
        self.resource_id = resource_id


class LiveObjectRegistry:
    """Registro de instancias vivas respaldado por `weakref.WeakValueDictionary`."""

    def __init__(self) -> None:
        # BEGIN_SOLUTION
        self._cache: weakref.WeakValueDictionary[str, HeavyResource] = (
            weakref.WeakValueDictionary()
        )
        # END_SOLUTION

    def register(self, resource: HeavyResource) -> None:
        # BEGIN_SOLUTION
        self._cache[resource.resource_id] = resource
        # END_SOLUTION

    def get(self, resource_id: str) -> HeavyResource | None:
        # BEGIN_SOLUTION
        return self._cache.get(resource_id)
        # END_SOLUTION

    def active_count(self) -> int:
        # BEGIN_SOLUTION
        return len(self._cache)
        # END_SOLUTION


class WeakParentTreeNode:
    """Nodo de árbol que guarda una referencia fuerte a sus hijos y débil (`weakref.ref`) a su padre."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.children: list[WeakParentTreeNode] = []
        self._parent_ref: weakref.ReferenceType[WeakParentTreeNode] | None = None

    def add_child(self, child: WeakParentTreeNode) -> None:
        # BEGIN_SOLUTION
        self.children.append(child)
        child._parent_ref = weakref.ref(self)
        # END_SOLUTION

    @property
    def parent(self) -> WeakParentTreeNode | None:
        # BEGIN_SOLUTION
        return self._parent_ref() if self._parent_ref is not None else None
        # END_SOLUTION


def inspect_function_bytecode(fn: Callable[..., Any]) -> dict[str, Any]:
    """Extrae metadatos del bytecode de `fn` usando `dis.get_instructions` y `__code__`.

    Devuelve un diccionario con:
    - `"opnames"`: lista de `instr.opname` en orden.
    - `"varnames"`: tupla `fn.__code__.co_varnames`.
    - `"has_loop_or_jump"`: `True` si algún `opname` contiene `"JUMP"` o `"FOR_ITER"`.
    """
    # BEGIN_SOLUTION
    instructions = list(dis.get_instructions(fn))
    opnames = [ins.opname for ins in instructions]
    has_jump = any("JUMP" in op or op == "FOR_ITER" for op in opnames)
    return {
        "opnames": opnames,
        "varnames": fn.__code__.co_varnames,
        "has_loop_or_jump": has_jump,
    }
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_live_object_registry() -> None:
    reg = LiveObjectRegistry()
    r1 = HeavyResource("res-1")
    reg.register(r1)
    assert reg.get("res-1") is r1
    assert reg.active_count() == 1
    del r1
    gc.collect()
    assert reg.get("res-1") is None
    assert reg.active_count() == 0


def check_weak_parent_tree_node() -> None:
    root = WeakParentTreeNode("root")
    child = WeakParentTreeNode("child")
    root.add_child(child)
    assert child.parent is root
    del root
    gc.collect()
    assert child.parent is None


def check_inspect_function_bytecode() -> None:
    def sample_loop(n: int) -> int:
        acc = 0
        for i in range(n):
            acc += i
        return acc

    info = inspect_function_bytecode(sample_loop)
    assert "n" in info["varnames"] and "acc" in info["varnames"]
    assert info["has_loop_or_jump"] is True
    assert len(info["opnames"]) > 0


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. LiveObjectRegistry (WeakValueDictionary)", check_live_object_registry),
    ("02. WeakParentTreeNode (weakref.ref)", check_weak_parent_tree_node),
    ("03. inspect_function_bytecode (dis)", check_inspect_function_bytecode),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 04_memory_weakrefs_and_bytecode.py")
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
