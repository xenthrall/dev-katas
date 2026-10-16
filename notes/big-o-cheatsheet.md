# Guía de Complejidad Algorítmica (Big-O Cheatsheet)

> Referencia rápida para estimar al instante qué algoritmo es viable según el tamaño de entrada $N$ en entrevistas técnicas y sistemas reales.

---

## 1. Presupuesto de Tiempo según Tamaño de Entrada ($N$)

En Python (CPython), una regla práctica segura es asumir que el intérprete puede ejecutar alrededor de **$10^7$ operaciones simples por segundo**.

| Tamaño de entrada $N$ | Complejidad Máxima Viable | Patrones y Algoritmos Típicos |
| :--- | :--- | :--- |
| $N \le 11$ | $O(N!)$ | Permutaciones completas (`itertools.permutations`), Fuerza bruta factorial. |
| $N \le 20$ | $O(2^N)$ | Backtracking de subconjuntos, Bitmask DP. |
| $N \le 400$ | $O(N^3)$ | Floyd-Warshall, multiplicación de matrices, 3 bucles anidados. |
| $N \le 3,000$ | $O(N^2)$ | Programación Dinámica 2D, 3Sum ($O(N^2)$), comparación de todos los pares. |
| $N \le 10^5$ | $O(N \log N)$ | Ordenamiento (`sorted`), Heap (`heapq`), Divide y Vencerás, Dijkstra. |
| $N \le 10^6$ | $O(N)$ | Two Pointers, Sliding Window, Hash Map (`dict`/`set`/`Counter`), Pila Monótona, DFS/BFS. |
| $N > 10^8$ | $O(\log N)$ o $O(1)$ | Búsqueda Binaria (`bisect`), Matemáticas directas, Exponenciación rápida. |

---

## 2. Reconocimiento de Patrones: Del Problema al Algoritmo

| Si el enunciado pide... | Piensa inmediatamente en... | Complejidad |
| :--- | :--- | :---: |
| Subarreglo/subcadena contigua más larga o corta que cumple condición | **Sliding Window** (Ventana Deslizante dinámica con `left` y `right`) | $O(N)$ |
| Pares o tripletas en un arreglo **ordenado** (o que puedes ordenar) | **Two Pointers** (Punteros en extremos opuestos `left < right`) | $O(N)$ / $O(N^2)$ |
| Cantidad de subarreglos cuya suma es exactamente $K$ | **Prefix Sums + Hash Map** (`conteo_prefijos[suma_actual - K]`) | $O(N)$ |
| Próximo elemento mayor o menor a la derecha/izquierda | **Monotonic Stack** (Pila monótona de índices) | $O(N)$ |
| Máximo/mínimo en cada ventana deslizante de tamaño fijo $K$ | **Monotonic Deque** (`collections.deque` de índices) | $O(N)$ |
| Los $K$ elementos más grandes, más pequeños o más frecuentes | **Heap (`heapq`)** o `Counter.most_common(k)` | $O(N \log K)$ |
| Mínima velocidad/capacidad/tiempo que permite cumplir una tarea | **Búsqueda Binaria en el Espacio de Respuestas** (`[min_posible, max_posible]`) | $O(N \log(\text{rango}))$ |
| Camino más corto en grafo **sin pesos** (o pesos iguales a 1) | **BFS** con `collections.deque` | $O(V + E)$ |
| Camino más corto en grafo con **pesos positivos** | **Dijkstra** con `heapq` | $O((V + E) \log V)$ |
| Ordenar tareas con dependencias o detectar ciclos dirigidos | **Topological Sort** (Algoritmo de Kahn con `in_degree` + `deque`) | $O(V + E)$ |
| Número de formas de llegar / Coste mínimo con decisiones solapadas | **Programación Dinámica** (`@functools.cache` o tabulación 1D/2D) | $O(\text{estados} \times \text{transiciones})$ |
| Generar todas las configuraciones válidas (combinaciones, tableros) | **Backtracking** (`elegir -> explorar -> deshacer`) | Exponencial podado |

---

## 3. Complejidad Espacial (Memoria Auxiliar)

- **$O(1)$ Espacio:** Solo variables escalares (`left`, `right`, `acumulador`, `prev1`, `prev2`).
- **$O(N)$ Espacio:** Tablas hash (`dict`, `set`), listas de salida, colas BFS.
- **Pila de Recursión:** Una función recursiva de profundidad $D$ consume **$O(D)$ memoria en el call stack**. En CPython el límite por defecto es `sys.getrecursionlimit() == 1000`. Para árboles sesgados o grafos profundos, prefiere DFS/BFS iterativo con una `list` o `deque`.
