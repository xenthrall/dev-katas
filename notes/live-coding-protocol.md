# Protocolo de Ejecución para Práctica Deliberada y Live-Coding (Sin IA)

> Este protocolo de 4 fases está diseñado para entrenar la resolución autónoma de problemas y el dominio de la sintaxis nativa de Python bajo presión.

---

## Las 4 Fases del Protocolo UMPIRE / Kata

### Fase 1: Entender y Acotar (2–4 minutos)
Antes de escribir una sola línea de código:
1. **Entradas y Salidas:** Define la firma exacta y los tipos (`def resolver(nums: list[int], k: int) -> int:`).
2. **Invariantes y Restricciones:**
   - ¿El arreglo está ordenado? ¿Contiene negativos o duplicados?
   - ¿Cuál es el tamaño máximo de $N$? (Esto dicta si una solución $O(N^2)$ fallará por tiempo y necesitas $O(N \log N)$ u $O(N)$).
3. **Casos Borde (Edge Cases):**
   - Colección vacía `[]` o `""`
   - Un solo elemento `[x]`
   - Todos los elementos iguales `[5, 5, 5, 5]`
   - Valores extremos o nulos

### Fase 2: Trazar el Modelo Mental y Complejidad (3–5 minutos)
1. **Fuerza Bruta Base:** Enuncia en 10 segundos la solución ingenua y su coste (ej. *"Dos bucles anidados serían $O(N^2)$ tiempo y $O(1)$ espacio"*).
2. **Optimización Estructural:** ¿Qué estructura o patrón elimina el trabajo repetido?
   - ¿Necesito búsqueda instantánea? $\rightarrow$ `dict` / `set` ($O(1)$).
   - ¿Hay monotonicidad? $\rightarrow$ Dos punteros, ventana deslizante o búsqueda binaria.
3. **Traza Manual en Seco:** Corre un ejemplo pequeño de 4 elementos a mano antes de codificar.

### Fase 3: Implementación Idiomática en Python (10–15 minutos)
1. Aprovecha las primitivas en C de Python (`enumerate`, `zip`, `collections.Counter`, `defaultdict`, `deque`, `heapq`, `bisect`, comprehensions).
2. Usa nombres de variables que expresen su rol invariante: `left`, `right`, `window_sum`, `seen_indices`, `best_len`.
3. Mantén las funciones enfocadas y modulares.

### Fase 4: Verificación y Autopsia de Complejidad (3–5 minutos)
1. **Dry Run línea por línea** con tu caso normal y un caso borde (ej. entrada vacía).
2. **Ejecuta la suite de pruebas (`R` en Dev-Katas Studio)** y analiza cualquier fallo leyendo el traceback sin adivinar al azar.
3. **Repetición Espaciada:** Si necesitaste consultar una pista o la solución de referencia, usa el **Modo Práctica (`P`)** al día siguiente para volver a implementarlo desde cero de memoria.
