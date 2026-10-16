# 01. Diccionario Maestro de Sintaxis, Operadores y Estructuras de Control en Python

> **Objetivo:** Referencia rápida y profunda para consultar cualquier construcción sintáctica de Python 3.12+ sin depender de buscadores ni asistentes de IA.

---

## 1. Primitivos, Operadores y Evaluación de Verdad (Truthiness)

### 1.1 Valores "Falsy" (Evalúan a `False` en un `if` o `bool()`)
Cualquier objeto en Python es **Truthy** salvo los siguientes casos exactos:
- `None` y `False`
- Ceros numéricos: `0`, `0.0`, `0j`, `Decimal(0)`, `Fraction(0, 1)`
- Colecciones y secuencias vacías: `""`, `()`, `[]`, `{}`, `set()`, `range(0)`
- Objetos cuya clase define `__bool__(self) -> False` o `__len__(self) -> 0`

### 1.2 Cortocircuito Lógico (`and`, `or`, `not`)
`and` y `or` **no devuelven necesariamente un booleano**; devuelven el **último operando evaluado**:
```python
# `x or default`: devuelve `x` si es Truthy; de lo contrario evalúa y devuelve `default`
nombre = input_usuario or "Anónimo"

# ⚠️ CUIDADO cuando `0` o `""` son valores válidos: usa `is not None`
timeout = config_timeout if config_timeout is not None else 30.0

# `a and b`: si `a` es Falsy devuelve `a` inmediatamente; si es Truthy evalúa y devuelve `b`
primero_en_mayus = items and items[0].upper()
```

### 1.3 Operadores Numéricos, Bitwise y de Identidad
| Operador | Descripción | Ejemplo / Caso de uso clave |
| :--- | :--- | :--- |
| `/` | División flotante real | `7 / 2 -> 3.5` |
| `//` | División entera (floor division hacia $-\infty$) | `7 // 2 -> 3`, `-7 // 2 -> -4` (para truncar hacia 0 usa `int(-7 / 2) -> -3`) |
| `%` | Módulo (resto) | `x % 2 == 0` (par), rotación circular `(idx + shift) % n` |
| `divmod(a, b)` | Cociente y resto simultáneos `(a // b, a % b)` | `horas, mins = divmod(135, 60) -> (2, 15)` |
| `**` | Exponenciación (`pow(a, b, mod)` para exp. modular $O(\log b)$) | `2 ** 10 -> 1024`, `pow(2, 1000, 10**9 + 7)` |
| `==` vs `is` | Igualdad de **valor** (`__eq__`) vs **identidad en memoria** (`id(a) == id(b)`) | Siempre usa `x is None` / `x is not None` |
| `&`, `\|`, `^`, `~` | AND, OR, XOR, NOT a nivel de bits (o conjuntos) | `x ^ x == 0` (encontrar elemento único en array) |
| `<<`, `>>` | Desplazamiento de bits izq/der ($\times 2^k$, $\div 2^k$) | `1 << k` ($2^k$), `(left + right) >> 1` |

---

## 2. Slicing (`[inicio:fin:paso]`) y Desempaquetado (`*`, `**`)

### 2.1 Anatomía del Slicing
La sintaxis `seq[start:stop:step]` extrae desde `start` (inclusivo) hasta `stop` (exclusivo) avanzando de a `step`:
```python
s = "ABCDEFGHIJ"
s[2:6]      # "CDEF"       -> índices 2, 3, 4, 5
s[:4]       # "ABCD"       -> primeros 4 elementos
s[-3:]      # "HIJ"        -> últimos 3 elementos
s[:-2]      # "ABCDEFGH"   -> todo excepto los últimos 2
s[::2]      # "ACEGI"      -> posiciones pares (0, 2, 4...)
s[1::2]     # "BDFHJ"      -> posiciones impares (1, 3, 5...)
s[::-1]     # "JIHGFEDCBA" -> inversión completa en O(n)

# Asignación por slice en listas (mutación in-place):
nums = [1, 2, 3, 4, 5]
nums[1:4] = [20, 30]       # nums -> [1, 20, 30, 5]
nums[:] = [9, 8]           # reemplaza el contenido de la misma lista en memoria (mismo id)
```

### 2.2 Unpacking Avanzado (Starred Expressions)
```python
# Captura flexible con *
primero, *medio, ultimo = [10, 20, 30, 40, 50]
# primero = 10, medio = [20, 30, 40], ultimo = 50

cabeza, *cola = [1]
# cabeza = 1, cola = []

# Intercambio de variables sin variable temporal (crea y desempaqueta tupla)
a, b = b, a

# Fusión de iterables y diccionarios
lista_combinada = [*lista_a, 0, *lista_b]
dict_combinado = {**defaults, **overrides}  # o `defaults | overrides` (Python 3.9+)
```

---

## 3. Strings y Formateo Moderno (f-strings)

### 3.1 Especificadores de Formato en f-strings (`{valor:formato}`)
```python
precio = 1234567.891
ratio = 0.856
n = 42

f"{precio:,.2f}"     # "1,234,567.89" (separador de miles y 2 decimales)
f"{ratio:.1%}"       # "85.6%"        (formato porcentaje)
f"{n:05d}"           # "00042"        (zero-padding a 5 dígitos)
f"{n:b} / {n:x}"     # "101010 / 2a"  (binario / hexadecimal)
f"{'texto':>10}"     # "     texto"   (alineado a la derecha, ancho 10)
f"{'texto':<10}"     # "texto     "   (alineado a la izquierda, ancho 10)
f"{'texto':^10}"     # "  texto   "   (centrado, ancho 10)
f"{'titulo':*^12}"   # "***titulo***" (relleno con '*' y centrado)
f"{precio=}"         # "precio=1234567.891" (debugging instantáneo de variable/expresión)
```

### 3.2 Métodos de `str` Imprescindibles para Katas
- **División y unión:**
  - `s.split()` (sin args: divide por cualquier secuencia de espacios/saltos y descarta extremos vacíos).
  - `s.split(sep, maxsplit=-1)` (con sep explícito: `"a,,b".split(",") -> ['a', '', 'b']`).
  - `s.splitlines()` (divide por líneas `\n`, `\r\n`).
  - `s.partition(sep)` -> siempre devuelve una 3-tupla `(antes, sep, despues)`. Si no existe `sep`, devuelve `(s, "", "")`. ¡Mucho más seguro que `.split(sep, 1)`!
  - `"".join(iterable_de_strings)` -> concatenación lineal $O(n)$. **Nunca** uses `s += char` dentro de un bucle grande.
- **Limpieza:**
  - `s.strip(chars)`, `s.lstrip(chars)`, `s.rstrip(chars)` (ojo: elimina un *conjunto* de caracteres, no un prefijo).
  - `s.removeprefix(prefix)` y `s.removesuffix(suffix)` (Python 3.9+: elimina el prefijo/sufijo exacto).
- **Búsqueda y validación:**
  - `s.startswith(("http://", "https://"))`, `s.endswith((".py", ".md"))` (aceptan una **tupla** de opciones).
  - `s.find(sub)` (devuelve índice o `-1`) vs `s.index(sub)` (lanza `ValueError` si no existe).
  - `s.isalnum()`, `s.isalpha()`, `s.isdigit()`, `s.isspace()`, `s.islower()`, `s.isupper()`.
- **Transformación rápida:**
  - `tabla = str.maketrans({"a": "4", "e": "3"}, ".,!")` (3er argumento = caracteres a eliminar).
  - `s.translate(tabla)` -> reemplazo y limpieza de caracteres a velocidad C.
  - `ord('a') -> 97`, `chr(97) -> 'a'`. Posición en alfabeto: `ord(c) - ord('a')`.

---

## 4. Comprehensions y Expresiones Generadoras

```python
# 1. List comprehension con filtro (el `if` va AL FINAL)
cuadrados_pares = [x * x for x in nums if x % 2 == 0]

# 2. List comprehension con ternario (transformación condicional: `if/else` va ANTES del `for`)
etiquetas = ["par" if x % 2 == 0 else "impar" for x in nums]

# 3. Nested comprehension (se lee en el MISMO orden que los bucles `for` anidados tradicionales)
# Equivalente a: for fila in matriz: for val in fila: ...
plana = [val for fila in matriz for val in fila if val > 0]

# 4. Dict comprehension
indice_por_nombre = {nombre.lower(): idx for idx, nombre in enumerate(nombres)}

# 5. Set comprehension
extensiones_unicas = {p.split(".")[-1].lower() for p in archivos if "." in p}

# 6. Generator expression (O(1) memoria extra, evaluación perezosa)
suma_cuadrados = sum(x * x for x in range(1_000_000))
hay_negativos = any(x < 0 for x in datos)
todos_validos = all(len(s) >= 3 for s in codigos)
primer_admin = next((u for u in usuarios if u["role"] == "admin"), None)
```

---

## 5. Control de Flujo Avanzado

### 5.1 Structural Pattern Matching (`match` / `case` - Python 3.10+)
A diferencia de un `switch` tradicional, `match` desestructura secuencias, diccionarios y objetos:
```python
match evento:
    # Coincidencia literal o múltiple (|)
    case "ping" | "heartbeat":
        return "pong"

    # Desestructuración de secuencias de longitud exacta o variable (*rest)
    case ["MOVE", int(x), int(y)] if x >= 0 and y >= 0:  # Con guarda `if`
        return f"Moviendo a ({x}, {y})"

    case ["BATCH", primero, *resto]:
        return f"Primero={primero}, restantes={len(resto)}"

    # Desestructuración de diccionarios (ignora claves extra automáticamente; `**rest` las captura)
    case {"type": "payment", "amount": (int() | float()) as monto} if monto > 0:
        return f"Pago de {monto}"

    # Wildcard (default)
    case _:
        raise ValueError(f"Evento no reconocido: {evento!r}")
```

### 5.2 Cláusula `else` en Bucles (`for...else` / `while...else`)
El bloque `else` de un bucle se ejecuta **únicamente si el bucle terminó de forma natural sin ejecutar `break`**:
```python
for candidato in elementos:
    if es_objetivo(candidato):
        resultado = candidato
        break
else:
    # Se ejecuta solo si NUNCA se disparó el `break`
    raise LookupError("Elemento objetivo no encontrado")
```

### 5.3 Operador Walrus (`:=` - Assignment Expression)
Asigna y devuelve el valor dentro de una misma expresión:
```python
# 1. En bucles while de lectura por bloques o regex
while (linea := stream.readline()):
    procesar(linea)

# 2. En comprehensions para evitar calcular una función costosa dos veces
resultados = [
    limpio
    for crudo in entradas
    if (limpio := normalizar_costoso(crudo)) is not None
]
```

---

## 6. Funciones, Firma Estricta y Ámbitos (Regla LEGB)

### 6.1 Anatomía Completa de Parámetros
```python
def configurar_endpoint(
    metodo: str,          # Solo posicional (antes de `/`)
    ruta: str,            # Solo posicional (antes de `/`)
    /,
    version: int = 1,     # Posicional O por nombre (estándar)
    *middlewares: str,    # Tupla con posicionales adicionales variables
    timeout: float = 5.0, # Solo por nombre / keyword-only (después de `*` o `*args`)
    estricto: bool = True,# Solo por nombre / keyword-only
    **metadatos: Any,     # Diccionario con argumentos keyword adicionales
) -> dict[str, Any]:
    ...
```

### 6.2 Regla LEGB y Modificadores de Ámbito
Python resuelve nombres buscando en 4 niveles en orden:
1. **L (Local):** Variables definidas dentro de la función actual.
2. **E (Enclosing):** Ámbito de funciones contenedoras (closures). Para **reasignar** una variable del ámbito envolvente usa `nonlocal contador`.
3. **G (Global):** Nivel de módulo actual. Para **reasignar** una global usa `global CONFIG`.
4. **B (Built-in):** Nombres predefinidos de Python (`len`, `sum`, `Exception`, etc.).

---

## 7. Manejo de Excepciones y Context Managers

```python
class ErrorDeDominio(Exception):
    """Excepción personalizada base."""

try:
    valor = int(entrada_cruda)
    resultado = 100 / valor
except ValueError as err:
    # Encadenamiento explícito: preserva el traceback original en `__cause__`
    raise ErrorDeDominio(f"Entrada no numérica: {entrada_cruda!r}") from err
except ZeroDivisionError:
    resultado = float("inf")
else:
    # Se ejecuta SOLO si el bloque `try` NO lanzó ninguna excepción
    registrar_exito(resultado)
finally:
    # Se ejecuta SIEMPRE (haya éxito, excepción o incluso un `return` previo)
    liberar_recursos()
```
