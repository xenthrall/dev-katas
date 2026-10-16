from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
import heapq
import sys
import time
from typing import Callable

"""
MÓDULO 06 — ALGORITMOS Y PATRONES: 05. ÁRBOLES Y GRAFOS (BFS, DFS, KAHN, DIJKSTRA)
===============================================================================
Estudio profundo y práctica deliberada sobre recorridos en árboles binarios
(BFS por niveles, validación de BST), componentes conexas en grillas 2D,
Ordenamiento Topológico (Algoritmo de Kahn) y caminos mínimos con **Dijkstra**.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. BFS por Niveles con `collections.deque`:
   - En cada iteración del `while queue:`, captura `level_size = len(queue)`
     y haz exactamente `level_size` extracciones con `queue.popleft()` para
     procesar un nivel completo del árbol o grafo.

2. Ordenamiento Topológico — Algoritmo de Kahn (`O(V + E)`):
   - Calcula `in_degree[u]` (número de aristas entrantes) para cada nodo.
   - Encola todos los nodos con `in_degree == 0`.
   - Si al terminar `len(orden) < total_nodos`, el grafo dirigido **contiene un ciclo**.

3. Algoritmo de Dijkstra con `heapq` (`O((V + E) log V)`):
   - Cola de prioridad de tuplas `(distancia_acumulada, nodo)`.
   - Descarta entradas obsoletas con `if d > dist[u]: continue`.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- Al validar un Árbol Binario de Búsqueda (`is_valid_bst`), NO basta con
  verificar `left.val < node.val < right.val`; debes propagar el intervalo
  estricto `(low_limit, high_limit)` a todos los descendientes.
"""


@dataclass
class TreeNode:
    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None


def level_order_traversal(root: TreeNode | None) -> list[list[int]]:
    """Recorre un árbol binario nivel por nivel (BFS) usando `collections.deque`."""
    # BEGIN_SOLUTION
    if root is None:
        return []
    levels: list[list[int]] = []
    queue: deque[TreeNode] = deque([root])
    while queue:
        level_vals: list[int] = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level_vals.append(node.val)
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        levels.append(level_vals)
    return levels
    # END_SOLUTION


def is_valid_bst(root: TreeNode | None) -> bool:
    """Verifica si un árbol binario cumple la propiedad estricta de BST en O(n)."""
    # BEGIN_SOLUTION
    def _validate(node: TreeNode | None, low: float, high: float) -> bool:
        if node is None:
            return True
        if not (low < node.val < high):
            return False
        return _validate(node.left, low, float(node.val)) and _validate(
            node.right, float(node.val), high
        )

    return _validate(root, float("-inf"), float("inf"))
    # END_SOLUTION


def count_islands_grid(grid: list[list[str]]) -> int:
    """Cuenta el número de islas de `'1'` conectadas ortogonalmente en una matriz 2D."""
    # BEGIN_SOLUTION
    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])
    visited: set[tuple[int, int]] = set()
    islands = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in visited:
                islands += 1
                q: deque[tuple[int, int]] = deque([(r, c)])
                visited.add((r, c))
                while q:
                    cr, cc = q.popleft()
                    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        nr, nc = cr + dr, cc + dc
                        if (
                            0 <= nr < rows
                            and 0 <= nc < cols
                            and grid[nr][nc] == "1"
                            and (nr, nc) not in visited
                        ):
                            visited.add((nr, nc))
                            q.append((nr, nc))
    return islands
    # END_SOLUTION


def topological_sort_kahn(
    num_nodes: int, prerequisites: list[tuple[int, int]]
) -> list[int]:
    """Devuelve un orden topológico para nodos `0..num_nodes-1` donde `(u, v)` significa `u -> v`.

    Si existe un ciclo, devuelve `[]`.
    """
    # BEGIN_SOLUTION
    adj: defaultdict[int, list[int]] = defaultdict(list)
    in_degree = [0] * num_nodes
    for u, v in prerequisites:
        adj[u].append(v)
        in_degree[v] += 1

    queue: deque[int] = deque(i for i in range(num_nodes) if in_degree[i] == 0)
    order: list[int] = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for nxt in adj[u]:
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                queue.append(nxt)

    return order if len(order) == num_nodes else []
    # END_SOLUTION


def dijkstra_shortest_paths(
    n: int, edges: list[tuple[int, int, int]], source: int
) -> dict[int, int]:
    """Calcula la distancia mínima desde `source` a cada nodo alcanzable usando `heapq`.

    Cada arista dirigida es `(u, v, peso)` con `peso >= 0`.
    """
    # BEGIN_SOLUTION
    adj: defaultdict[int, list[tuple[int, int]]] = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w))

    dist: dict[int, int] = {source: 0}
    pq: list[tuple[int, int]] = [(0, source)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, sys.maxsize):
            continue
        for v, weight in adj[u]:
            nd = d + weight
            if nd < dist.get(v, sys.maxsize):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_level_order_traversal() -> None:
    root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    assert level_order_traversal(root) == [[3], [9, 20], [15, 7]]
    assert level_order_traversal(None) == []


def check_is_valid_bst() -> None:
    valid = TreeNode(5, TreeNode(3), TreeNode(8, TreeNode(6), TreeNode(10)))
    invalid = TreeNode(5, TreeNode(3), TreeNode(8, TreeNode(4), TreeNode(10)))
    assert is_valid_bst(valid) is True
    assert is_valid_bst(invalid) is False


def check_count_islands_grid() -> None:
    grid = [
        ["1", "1", "0", "0"],
        ["1", "0", "0", "1"],
        ["0", "0", "1", "1"],
    ]
    assert count_islands_grid(grid) == 2


def check_topological_sort_kahn() -> None:
    order = topological_sort_kahn(4, [(0, 1), (0, 2), (1, 3), (2, 3)])
    assert order in ([0, 1, 2, 3], [0, 2, 1, 3])
    assert topological_sort_kahn(2, [(0, 1), (1, 0)]) == []


def check_dijkstra_shortest_paths() -> None:
    edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5)]
    assert dijkstra_shortest_paths(4, edges, 0) == {0: 0, 2: 1, 1: 3, 3: 4}


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. level_order_traversal (BFS)", check_level_order_traversal),
    ("02. is_valid_bst (DFS Range)", check_is_valid_bst),
    ("03. count_islands_grid (Grid BFS)", check_count_islands_grid),
    ("04. topological_sort_kahn (Kahn's Algorithm)", check_topological_sort_kahn),
    ("05. dijkstra_shortest_paths (Min-Heap)", check_dijkstra_shortest_paths),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 05_trees_and_graphs_traversal.py")
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
