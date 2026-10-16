# 02. Atlas de Funciones Built-in y Librería Estándar (`stdlib`)

> **Objetivo:** Dominar las herramientas en C incluidas en la librería estándar de Python para no reinventar la rueda durante katas, entrevistas técnicas o desarrollo de sistemas.

---

## 1. Funciones Built-in Esenciales

| Función | Firma / Uso Idiomático | Descripción y Complejidad |
| :--- | :--- | :--- |
| `enumerate` | `for i, val in enumerate(seq, start=0):` | Empareja índice y valor sin usar `range(len(seq))`. $O(1)$ memoria. |
| `zip` | `for a, b in zip(seq1, seq2, strict=True):` | Itera en paralelo. `zip(*matriz)` transpone filas $\leftrightarrow$ columnas. |
| `sorted` | `sorted(seq, key=lambda x: ..., reverse=False)` | Timsort estable en $O(n \log n)$. Devuelve una **nueva** lista. |
| `reversed` | `for x in reversed(seq):` | Iterador inverso en $O(1)$ memoria (requiere secuencia o `__reversed__`). |
| `any` / `all` | `any(x > 0 for x in seq)` | Cortocircuito inmediato al encontrar el primer `True` (`any`) o `False` (`all`). |
| `min` / `max` | `max(palabras, key=len, default="")` | Aceptan `key=` y `default=` (evita `ValueError` en secuencias vacías). |
| `sum` | `sum(valores, start=0)` | Suma rápida en C (para listas de listas o strings prefiere `chain` / `"".join`). |
| `iter` / `next` | `next(it, valor_por_defecto)` | Extrae el siguiente elemento de un iterador sin lanzar `StopIteration`. |
| `isinstance` | `isinstance(obj, (int, float))` | Verifica tipo o tupla de tipos (respeta herencia y `Protocol` runtime). |
| `getattr` | `getattr(obj, "nombre_attr", default)` | Acceso dinámico seguro a atributos de objetos. |

---

## 2. `collections` — Estructuras de Datos Especializadas

### 2.1 `Counter` (Multiconjunto / Mapa de Frecuencias)
```python
from collections import Counter

c = Counter("abracadabra")          # Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
c["z"]                              # 0 (¡No lanza KeyError si la clave no existe!)
c.most_common(2)                    # [('a', 5), ('b', 2)] -> Top K en O(n log k)
c.total()                           # 11 -> Suma total de conteos (Python 3.10+)

# Aritmética de multiconjuntos (descarta conteos <= 0 automáticamente)
c1 = Counter(a=3, b=1)
c2 = Counter(a=1, b=2)
c1 + c2                             # Counter({'a': 4, 'b': 3})
c1 - c2                             # Counter({'a': 2})
c1 & c2                             # Intersección (mínimos): Counter({'a': 1, 'b': 1})
c1 | c2                             # Unión (máximos): Counter({'a': 3, 'b': 2})
c1 <= c2                            # Inclusión de multiconjuntos (¿c2 cubre todo c1?)
```

### 2.2 `defaultdict` (Diccionario con Inicialización Automática)
```python
from collections import defaultdict

# Agrupación en listas: O(1) sin verificar `if k not in d`
grupos: defaultdict[str, list[str]] = defaultdict(list)
for depto, empleado in registros:
    grupos[depto].append(empleado)

# Conteo o acumulación numérica
saldos: defaultdict[str, float] = defaultdict(float)

# Grafos con conjuntos de adyacencia
grafo: defaultdict[int, set[int]] = defaultdict(set)
```

### 2.3 `deque` (Cola de Doble Extremo $O(1)$)
En una `list` normal, `pop(0)` o `insert(0, x)` cuesta $O(n)$ porque desplaza todos los elementos en memoria. `deque` garantiza **$O(1)$ en ambos extremos**:
```python
from collections import deque

q = deque([1, 2, 3])
q.append(4)         # [1, 2, 3, 4] -> O(1) derecha
q.appendleft(0)     # [0, 1, 2, 3, 4] -> O(1) izquierda
q.pop()             # 4 -> O(1) derecha
q.popleft()         # 0 -> O(1) izquierda (¡Úsalo siempre para colas BFS!)
q.rotate(1)         # Rotación circular a la derecha (negativo = izquierda)

# Ventana deslizante automática de tamaño fijo:
ventana = deque(maxlen=3)
for x in [10, 20, 30, 40]:
    ventana.append(x)  # Al entrar el 40, descarta automáticamente el 10
```

### 2.4 `ChainMap` (Vistas Jerárquicas de Diccionarios)
```python
from collections import ChainMap

# Busca de izquierda a derecha sin copiar ni fusionar diccionarios en memoria
config = ChainMap(cli_overrides, env_vars, default_settings)
puerto = config["PORT"]
```

---

## 3. `itertools` — Álgebra de Iteradores en Tiempo C

```python
import itertools

# 1. Aplanar un nivel de listas anidadas en O(1) memoria
plano = list(itertools.chain.from_iterable([[1, 2], [3, 4], [5]]))  # [1, 2, 3, 4, 5]

# 2. Slicing sobre cualquier generador/iterador sin materializarlo
pagina = list(itertools.islice(generador_infinito(), 10, 20))  # índices 10..19

# 3. Sumas/productos prefijos acumulados
prefijos = list(itertools.accumulate([1, 2, 3, 4]))            # [1, 3, 6, 10]
prefijos_con_cero = list(itertools.accumulate([1, 2, 3], initial=0))  # [0, 1, 3, 6]

# 4. Agrupación de elementos CONSECUTIVOS (⚠️ Ordena primero si quieres agrupar globales)
datos = sorted(usuarios, key=lambda u: u["rol"])
por_rol = {
    rol: list(grupo)
    for rol, grupo in itertools.groupby(datos, key=lambda u: u["rol"])
}

# 5. Pares adyacentes y lotes (Python 3.10+ / 3.12+)
pares = list(itertools.pairwise([10, 20, 30, 40]))  # [(10, 20), (20, 30), (30, 40)]
lotes = list(itertools.batched([1, 2, 3, 4, 5], 2)) # [(1, 2), (3, 4), (5,)]

# 6. Combinatoria
list(itertools.product([0, 1], repeat=3))      # Producto cartesiano (todas las tuplas binarias de len 3)
list(itertools.permutations("ABC", 2))         # Permutaciones (importa el orden)
list(itertools.combinations([1, 2, 3, 4], 2))  # Combinaciones sin reemplazo (no importa el orden)
```

---

## 4. `functools` — Programación Funcional y Memoización

```python
from functools import cache, lru_cache, partial, reduce, singledispatch, total_ordering, wraps

# 1. Memoización instantánea (Programación Dinámica Top-Down)
@cache  # Equivalente a @lru_cache(maxsize=None)
def escaleras(n: int) -> int:
    if n <= 2:
        return n
    return escaleras(n - 1) + escaleras(n - 2)

# 2. Aplicación parcial de argumentos
 base_2 = partial(int, base=2)
 base_2("1010")  # 10

# 3. Preservación de metadatos en decoradores
def mi_decorador(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper
```

---

## 5. `heapq` y `bisect` — Colas de Prioridad y Búsqueda Binaria

### 5.1 `heapq` (Min-Heap sobre una `list` estándar)
Python implementa un **Min-Heap** (el elemento en `heap[0]` es siempre el **menor**).
- **Truco para Max-Heap:** Guarda los números **negados** (`-valor`) o tuplas `(-prioridad, item)`.
```python
import heapq

nums = [5, 1, 8, 3]
heapq.heapify(nums)             # Convierte lista in-place en heap en tiempo O(n) -> [1, 3, 8, 5]
heapq.heappush(nums, 0)         # Inserta en O(log n)
menor = heapq.heappop(nums)     # Extrae el mínimo (0) en O(log n)
 peek = nums[0]                 # Consulta el mínimo sin extraer en O(1)

# Top-K y fusión de streams ordenados:
top_3_caros = heapq.nlargest(3, productos, key=lambda p: p["precio"])
 fusionados = list(heapq.merge(stream_ordenado_1, stream_ordenado_2))
```

### 5.2 `bisect` (Búsqueda Binaria en $O(\log n)$ sobre listas ordenadas)
```python
import bisect

arr = [10, 20, 20, 20, 30, 40]

# bisect_left: primer índice donde se puede insertar `x` manteniendo orden (primer >= x)
idx_izq = bisect.bisect_left(arr, 20)   # 1

# bisect_right: índice justo después de todas las ocurrencias de `x` (primer > x)
idx_der = bisect.bisect_right(arr, 20)  # 4

# Cantidad de ocurrencias de 20 en O(log n):
ocurrencias = bisect.bisect_right(arr, 20) - bisect.bisect_left(arr, 20)  # 4 - 1 = 3
```

---

## 6. `re` — Expresiones Regulares Esenciales

| Patrón | Significado | Ejemplo |
| :--- | :--- | :--- |
| `\d` / `\D` | Dígito `[0-9]` / No dígito | `r"\d{4}-\d{2}-\d{2}"` (Fecha ISO) |
| `\w` / `\W` | Alfanumérico + `_` / No palabra | `r"\w+"` |
| `\s` / `\S` | Espacio en blanco / No espacio | `r"\s+"` |
| `\b` | Límite de palabra (word boundary) | `r"\bcat\b"` (coincide con `"cat"`, no con `"category"`) |
| `(?P<nombre>...)` | Grupo con nombre (`m.group("nombre")` / `m.groupdict()`) | `r"(?P<anio>\d{4})-(?P<mes>\d{2})"` |
| `(?:...)` | Grupo de no-captura (agrupa sin alterar `findall`) | `r"(?:http|https)://"` |
| `(?=...)` / `(?!...)` | Lookahead positivo / negativo (verifica qué sigue sin consumir) | `r"\w+(?=@)"` (usuario antes de `@`) |
| `(?<=...)` / `(?<!...)` | Lookbehind positivo / negativo (verifica qué precede) | `r"(?<=\$)\d+"` (monto después de `$`) |
| `*?`, `+?` | Cuantificadores **no codiciosos (lazy)** | `r"<.+?>"` (captura un solo tag HTML, no hasta el último `>`) |
