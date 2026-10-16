# 03. Estructuras de Datos Nativas, Complejidad Big-O y Arquitectura en CPython

> **Objetivo:** Elegir siempre la estructura de datos óptima conociendo cómo están implementadas bajo el capó en CPython y cuánto cuesta cada operación en tiempo y memoria.

---

## 1. Matriz Comparativa de Complejidad (CPython)

| Estructura | Implementación en CPython | Acceso por Índice/Clave | Búsqueda (`x in col`) | Inserción/Borrado al Final | Inserción/Borrado al Inicio |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`list`** | Array dinámico de punteros `PyObject*` con sobre-asignación | $O(1)$ | $O(n)$ | $O(1)$ amortizado | **$O(n)$** (desplaza todo) |
| **`tuple`** | Array fijo e inmutable de punteros `PyObject*` | $O(1)$ | $O(n)$ | N/A (Inmutable) | N/A (Inmutable) |
| **`collections.deque`** | Lista doblemente enlazada de bloques de 64 punteros | $O(n)$ en el centro | $O(n)$ | **$O(1)$** | **$O(1)$** |
| **`dict`** | Tabla hash compacta de direccionamiento abierto (preserva orden) | **$O(1)$** amortizado | **$O(1)$** amortizado | **$O(1)$** amortizado | `popitem()` es $O(1)$ |
| **`set` / `frozenset`** | Tabla hash de direccionamiento abierto (solo claves + hashes) | N/A | **$O(1)$** amortizado | **$O(1)$** amortizado | N/A |
| **`heapq` (sobre `list`)** | Árbol binario completo almacenado en array (`2i+1`, `2i+2`) | `heap[0]` (mín) es $O(1)$ | $O(n)$ | `heappush`: $O(\log n)$ | `heappop` (raíz): $O(\log n)$ |
| **`str` / `bytes`** | Buffer contiguo inmutable en memoria | $O(1)$ | $O(n \cdot m)$ / Boyer-Moore | Concatenar `+`: **$O(n)$** | N/A |

---

## 2. Cómo Funcionan por Dentro en CPython

### 2.1 `list`: Por qué `.append()` es $O(1)$ pero `.pop(0)` es $O(n)$
Una `list` en CPython (`PyListObject`) guarda un puntero a un array contiguo de punteros `PyObject** ob_item` y dos enteros: `ob_size` (elementos actuales) y `allocated` (capacidad reservada).
- Cuando haces `.append(x)` y `ob_size == allocated`, CPython redimensiona el buffer pidiendo aproximadamente un **12.5% extra** de capacidad (`new_allocated = newsize + (newsize >> 3) + 6`). Por eso el coste amortizado de `.append()` es $O(1)$.
- Cuando haces `lista.insert(0, x)` o `lista.pop(0)`, CPython tiene que mover en memoria los $n-1$ punteros restantes con `memmove`. Si necesitas una cola FIFO, **usa siempre `collections.deque`**.

### 2.2 `dict`: Tablas Hash Compactas (Python 3.6+)
Antes de Python 3.6, un `dict` era una tabla dispersa donde cada celda ocupaba 24 bytes (hash, puntero a clave, puntero a valor), desperdiciando mucha caché de CPU.
Hoy un `dict` se divide en **dos arrays**:
1. **`dk_indices`:** Una tabla dispersa pequeña de enteros de 1, 2, 4 u 8 bytes que guardan el índice hacia el segundo array.
2. **`dk_entries`:** Un array compacto donde las entradas `(hash, key_ptr, value_ptr)` se agregan secuencialmente en orden de inserción.
- **Resultado:** Menor consumo de RAM, iteración rapidísima (recorre `dk_entries` contiguamente) y **orden de inserción garantizado por especificación del lenguaje** (desde Python 3.7+).

### 2.3 Reglas de Hashabilidad (`__hash__` y `__eq__`)
Para que un objeto pueda ser clave de un `dict` o elemento de un `set`, debe ser **hashable**:
- **Son hashables:** `int`, `float`, `str`, `bytes`, `bool`, `None`, `frozenset`, y una `tuple` **solo si todos sus elementos internos son hashables** (`(1, "a", (2, 3))` es hashable; `(1, [2, 3])` lanza `TypeError: unhashable type: 'list'`).
- **Contrato fundamental:** Si `a == b`, entonces obligatoriamente `hash(a) == hash(b)`.

---

## 3. Árbol de Decisión Rápido para Problemas y Katas

```text
¿Qué operación domina tu algoritmo?
│
├─► "¿Ya vi este elemento antes?" / Deduplicar / Intersección
│     └──► Usa `set` (o `dict.fromkeys(seq)` si necesitas preservar el orden exacto)
│
├─► "Contar frecuencias / Anagramas / Top-K repetidos"
│     └──► Usa `collections.Counter`
│
├─► "Agrupar elementos por categoría / Grafo de lista de adyacencia"
│     └──► Usa `collections.defaultdict(list)` o `defaultdict(set)`
│
├─► "Cola FIFO (BFS en grafos/árboles) o Ventana Deslizante de tamaño fijo"
│     └──► Usa `collections.deque` (`append` + `popleft`, o `deque(maxlen=k)`)
│
├─► "Pila LIFO (Paréntesis, DFS iterativo, Pila Monótona)"
│     └──► Usa `list` estándar (`append` + `pop` al final son O(1))
│
├─► "Extraer repetidamente el mínimo/máximo dinámico o K elementos mayores"
│     └──► Usa `heapq` (`heappush`, `heappop`, `nlargest`, `nsmallest`)
│
├─► "Buscar rangos o umbrales en una colección estática ordenada"
│     └──► Usa `bisect` (`bisect_left`, `bisect_right` en O(log n))
│
└─► "Caché con expulsión del menos recientemente usado (LRU)"
      └──► Usa `@functools.lru_cache` o `collections.OrderedDict` (`move_to_end` + `popitem(last=False)`)
```
