# ⚡ dev-katas — Estudio Central y Práctica Deliberada de Python (Sin IA)

> **Tu centro de entrenamiento integral para dominar la sintaxis, la librería estándar, los internos de CPython, algoritmos y arquitectura backend en Python de principio a fin.**

---

## 🎯 Filosofía del Proyecto

1. **Encontrar la Sintaxis al Instante:** Consulta hojas de referencia rápidas (`00-cheatsheets-and-reference/`), guías integradas en la cabecera de cada archivo `.py` o usa el buscador interactivo de conceptos (`/` en la TUI o `--search` en CLI).
2. **Estudiar en Profundidad:** Desde primitivas nativas hasta descriptores, metaclases, bytecode, `asyncio`, estructuras de datos avanzadas y servicios con FastAPI.
3. **Practicar de Memoria Sin IA:** Cambia cualquier kata a **Modo Práctica (`P`)** para vaciar las soluciones (`NotImplementedError`), resuélvelo en tu editor sin autocompletado de IA, ejecuta los tests en tiempo real (`R`), consulta pistas (`H`) si te atascas y compara tu código con la solución idiomática (`V` / `S`).

---

## 🚀 Inicio Rápido (TUI Interactiva y CLI)

### 1. Abrir el Estudio Interactivo (TUI)
```powershell
uv run katas
# o directamente con el entorno virtual:
.\.venv\Scripts\python.exe runner.py
```

#### Atajos dentro de `DEV-KATAS STUDIO`:
| Tecla | Acción |
| :---: | :--- |
| **`Enter` / Clic** | Abre un manual `.md` o carga y ejecuta un archivo de kata `.py` |
| **`X`** | Abre y ejecuta al instante tu **Playground Rápido** (`python/playground.py`) |
| **`/`** | Enfoca el **Buscador Rápido de Sintaxis y Conceptos** (`Escape` para limpiar) |
| **`R`** | Re-ejecuta el kata o playground actual y muestra métricas en tiempo real |
| **`P`** | **Modo Práctica:** Vacía las soluciones del kata actual (`TODO` / `NotImplementedError`) para resolverlo desde cero |
| **`H`** | Muestra solo la **Guía de Sintaxis y Pistas** de cada ejercicio (sin spoilers de código) |
| **`V`** | **Espiar Solución:** Muestra las soluciones de referencia en pantalla sin sobrescribir tu archivo |
| **`S`** | **Restaurar Solución:** Restaura las soluciones oficiales (o plantilla base) en el archivo `.py` |
| **`A`** | Ejecuta la **Auditoría Global** de todos los módulos y muestra tu progreso |
| **`C`** | Limpia la consola de salida |
| **`Q`** | Salir |

### 2. Comandos Rápidos por Terminal (CLI)
```powershell
# Buscar dónde se explica o practica cualquier sintaxis o método (ej. "slice", "heapq", "decorator", "async"):
uv run katas --search heapq

# Ejecutar el dashboard global de pruebas de los 38 katas:
uv run katas --test

# Poner un kata específico (o todos con `all`) en Modo Práctica (en blanco para resolver):
uv run katas --practice python/01-syntax-and-primitives/01_strings_and_slicing.py

# Restaurar las soluciones oficiales de un kata (o todos con `all`):
uv run katas --restore python/01-syntax-and-primitives/01_strings_and_slicing.py

# Ejecutar tu Playground libre o cualquier kata individual:
.\.venv\Scripts\python.exe python/playground.py
.\.venv\Scripts\pytest.exe
```

---

## 🗺️ Estructura del Proyecto

```text
dev-katas/
├── runner.py                                      # Motor TUI & CLI (Buscador, Modo Práctica, Pistas y Runner)
├── pyproject.toml                                 # Configuración de dependencias, pytest y comando `katas`
├── notes/
│   ├── big-o-cheatsheet.md                        # Presupuesto de tiempo Big-O y mapa Problema -> Algoritmo
│   └── live-coding-protocol.md                    # Protocolo de 4 fases para resolver problemas sin IA
│
├── python/
│   ├── README.md                                  # Arquitectura de Python, CPython Internals, Memoria y GIL
│   ├── playground.py                              # 🧪 Pizarrón rápido de 10s con stdlib importada (Atajo 'X')
│   ├── 00-cheatsheets-and-reference/              # 📖 Enciclopedia rápida de sintaxis y librería estándar
│   │   ├── 01_syntax_and_operators_guide.md       # Operadores, slicing, unpacking, f-strings, match/case, ámbitos
│   │   ├── 02_builtins_and_stdlib_atlas.md        # Built-ins, collections, itertools, functools, heapq, bisect, re
│   │   ├── 03_data_structures_and_big_o.md        # Complejidad real en CPython y árbol de decisión de estructuras
│   │   ├── 04_pythonic_idioms_and_gotchas.md      # Las 7 trampas clásicas de Python y patrones idiomáticos
│   │   └── 05_syntax_search_index.md              # Índice maestro: "¿En qué archivo practico el concepto X?"
│   │
│   ├── 01-syntax-and-primitives/                  # 🧱 Bloque 1: Sintaxis base y estructuras nativas (6 katas)
│   ├── 02-data-manipulation-and-stdlib/           # 🛠️ Bloque 2: Manipulación de datos y stdlib (6 katas)
│   ├── 03-oop-and-python-object-model/            # 🏛️ Bloque 3: POO profunda, dunders, ABC, Protocol, with (4 katas)
│   ├── 04-advanced-internals-and-metaprogramming/ # 🔬 Bloque 4: Decoradores, descriptores, metaclases, typing (5 katas)
│   ├── 05-concurrency-and-async/                  # ⚡ Bloque 5: Asyncio, streams, threading y multiprocessing (4 katas)
│   ├── 06-algorithms-and-patterns/                # 🧠 Bloque 6: Patrones algorítmicos y diseño Pythonic (7 katas)
│   ├── 07-api-and-network-consumption/            # 🌐 Bloque 7: Clientes HTTP offline, resiliencia y cachés (3 katas)
│   ├── 08-fastapi-and-backend-services/           # 🚀 Bloque 8: FastAPI, Pydantic v2, DI, Auth y CRUD (3 katas)
│   └── 99-playground/                             # 🎯 Zona de Simulacros (sandbox, interview_sim, async_api_lab)
│
├── php/                                           # Espacio reservado para katas de PHP
└── frontend-quick/                                # Espacio reservado para retos frontend rápidos
```