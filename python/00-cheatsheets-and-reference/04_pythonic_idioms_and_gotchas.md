# 04. Patrones Idiomáticos (Pythonic) y Trampas Clásicas (Gotchas)

> **Objetivo:** Escribir código limpio, expresivo y libre de los bugs silenciosos más frecuentes de Python.

---

## 1. Las 7 Trampas Clásicas de Python (Gotchas) y Cómo Evitarlas

### Trampa 1: Argumentos por Defecto Mutables
Los valores por defecto en `def fn(items=[])` se evalúan **una única vez cuando se define la función (`def`)**, NO en cada llamada. Todas las llamadas compartirán la misma lista en memoria.
```python
# ❌ INCORRECTO: la lista persiste y acumula datos entre llamadas
def agregar_tag_malo(tag: str, tags: list[str] = []) -> list[str]:
    tags.append(tag)
    return tags

# ✅ CORRECTO: usa `None` como centinela y crea la lista dentro de la función
def agregar_tag(tag: str, tags: list[str] | None = None) -> list[str]:
    if tags is None:
        tags = []
    tags.append(tag)
    return tags
```

### Trampa 2: Multiplicación de Listas Anidadas (`[[0] * m] * n`)
Multiplicar una lista de listas replica **referencias a la misma sublista**, no copias independientes.
```python
# ❌ INCORRECTO: las 3 filas apuntan al mismo objeto lista en memoria
matriz_mala = [[0] * 3] * 3
matriz_mala[0][0] = 99  # ¡Ahora matriz_mala es [[99, 0, 0], [99, 0, 0], [99, 0, 0]]!

# ✅ CORRECTO: usa una list comprehension para instanciar una nueva lista por cada fila
matriz = [[0] * 3 for _ in range(3)]
```

### Trampa 3: Late-Binding en Closures dentro de Bucles
Las funciones/lambdas capturan la **variable** `i` por referencia (su valor al momento de *ejecutarse* la lambda), no el valor que tenía en esa iteración.
```python
# ❌ INCORRECTO: todas las funciones devuelven 4 (el último valor de `i`)
callbacks_malos = [lambda x: x * i for i in range(5)]

# ✅ CORRECTO: enlaza el valor actual como argumento por defecto `factor=i`
callbacks_buenos = [lambda x, factor=i: x * factor for i in range(5)]
```

### Trampa 4: Copia Superficial (`copy`) vs Copia Profunda (`deepcopy`)
`lista.copy()`, `lista[:]` y `dict.copy()` solo copian el contenedor externo. Los diccionarios o listas internos siguen compartiendo la misma referencia en memoria.
```python
import copy

original = [{"id": 1, "roles": ["user"]}]
superficial = original.copy()
profunda = copy.deepcopy(original)

# Si modificas `superficial[0]["roles"].append("admin")`, ¡también mutas `original`!
# Con `copy.deepcopy(original)` todo el árbol de objetos queda desacoplado.
```

### Trampa 5: Mutar una Colección Mientras se Itera Sobre Ella
Eliminar elementos de una `list` mientras la recorres con `for x in lista:` salta elementos porque los índices se desplazan; mutar claves de un `dict` o `set` lanza `RuntimeError: dictionary changed size during iteration`.
```python
# ✅ CORRECTO para listas: filtra con una list comprehension (o itera sobre una copia `lista[:]`)
nums = [x for x in nums if x >= 0]

# ✅ CORRECTO para dicts: itera sobre `list(d.keys())` o construye un nuevo dict
d = {k: v for k, v in d.items() if v is not None}
```

### Trampa 6: Agotamiento Silencioso de Iteradores y Generadores
Un generador o el resultado de `map()`, `filter()`, `zip()` solo puede recorrerse **una vez**. La segunda vez estará vacío `[]`.
```python
gen = (x * 2 for x in [1, 2, 3])
primera_pasada = list(gen)  # [2, 4, 6]
segunda_pasada = list(gen)  # [] -> ¡Ya se consumió!
```

### Trampa 7: Concatenación de Strings con `+=` o `sum()` de Listas
```python
# ❌ O(n^2) en general:
resultado = ""
for fragmento in miles_de_fragmentos:
    resultado += fragmento

# ✅ O(n) garantizado:
resultado = "".join(miles_de_fragmentos)
```

---

## 2. Patrones Idiomáticos (El Estilo Pythonic)

### 2.1 EAFP (*Easier to Ask for Forgiveness than Permission*) vs LBYL (*Look Before You Leap*)
En Python, acceder directamente o usar métodos con valor por defecto suele ser más rápido, limpio y seguro frente a condiciones de carrera que hacer múltiples verificaciones previas:
```python
# En lugar de verificar `if k in conteo:` en cada paso:
conteo[k] = conteo.get(k, 0) + 1

# En lugar de `if clave in grupos: grupos[clave].append(x) else: ...`:
grupos.setdefault(clave, []).append(x)  # O usa collections.defaultdict(list)
```

### 2.2 Uso de Tuplas en `key=` para Ordenamientos Multicriterio
Las tuplas en Python se comparan elemento por elemento de izquierda a derecha (orden lexicográfico).
```python
# Ordenar empleados por:
# 1) Departamento ascendente (A -> Z)
# 2) Salario descendente (mayor a menor -> negamos con `-`)
# 3) Nombre ascendente (desempate)
ordenados = sorted(
    empleados,
    key=lambda e: (e["departamento"], -e["salario"], e["nombre"]),
)
```

### 2.3 Context Managers (`with`) para Garantizar Limpieza de Recursos
Cualquier recurso que requiera abrir/cerrar, bloquear/desbloquear o iniciar/revertir debe usar `with`:
```python
from contextlib import contextmanager

@contextmanager
def temporizador(etiqueta: str):
    inicio = time.perf_counter()
    try:
        yield
    finally:
        ms = (time.perf_counter() - inicio) * 1000
        print(f"[{etiqueta}] {ms:.2f} ms")
```
