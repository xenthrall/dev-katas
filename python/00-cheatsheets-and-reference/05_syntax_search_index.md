# 05. Índice Rápido de Sintaxis y Mapa de Katas ("¿Dónde practico X?")

> Usa este índice (o presiona `/` en `uv run katas` para filtrar en tiempo real) cuando quieras encontrar al instante dónde estudiar y practicar un concepto específico de Python.

---

## Tabla de Búsqueda Rápida: Concepto $\rightarrow$ Sintaxis $\rightarrow$ Archivo de Kata

| Concepto / Tema | Sintaxis Clave / Primitiva | Archivo de Práctica en `python/` |
| :--- | :--- | :--- |
| **Slicing e inversión** | `s[start:stop:step]`, `s[::-1]` | `01-syntax-and-primitives/01_strings_and_slicing.py` |
| **Métodos de Strings y ASCII** | `.split()`, `.join()`, `.partition()`, `ord()`, `chr()`, `f"{v:,.2f}"` | `01-syntax-and-primitives/01_strings_and_slicing.py` |
| **Desempaquetado (`*`) y Tuplas** | `primero, *medio, ultimo = seq` | `01-syntax-and-primitives/02_lists_tuples_and_unpacking.py` |
| **Transposición de Matrices** | `[list(col) for col in zip(*matriz)]` | `01-syntax-and-primitives/02_lists_tuples_and_unpacking.py` |
| **Copia Superficial vs Profunda** | `lista.copy()` vs `copy.deepcopy(obj)` | `01-syntax-and-primitives/02_lists_tuples_and_unpacking.py` |
| **Diccionarios y Sets ($O(1)$)** | `d.get()`, `d.setdefault()`, `d1 \| d2`, `set` (`\|`, `&`, `-`, `^`), `frozenset` | `01-syntax-and-primitives/03_dicts_sets_and_hashing.py` |
| **Deduplicación con orden** | `list(dict.fromkeys(items))` | `01-syntax-and-primitives/03_dicts_sets_and_hashing.py` |
| **Comprehensions y Generadores** | `[x for r in mat for x in r if x > 0]`, `any()`, `all()`, `next()` | `01-syntax-and-primitives/04_comprehensions_and_generators.py` |
| **Pattern Matching (`match`/`case`)** | `match obj: case {"op": op, **rest} if cond:` | `01-syntax-and-primitives/05_control_flow_and_matching.py` |
| **Operador Walrus y `for...else`** | `if (m := parse(x)) is not None:`, `for x in seq: ... else:` | `01-syntax-and-primitives/05_control_flow_and_matching.py` |
| **Excepciones encadenadas** | `try ... except E as err: raise CustomError() from err` | `01-syntax-and-primitives/05_control_flow_and_matching.py` |
| **Firmas (`/`, `*`, `*args`, `**kwargs`)** | `def f(pos, /, std, *, kw_only=1, **kw):` | `01-syntax-and-primitives/06_functions_scopes_and_closures.py` |
| **Closures y `nonlocal`** | `nonlocal estado`, `lambda x, i=i: x * i` | `01-syntax-and-primitives/06_functions_scopes_and_closures.py` |
| **`Counter`, `defaultdict`, `deque`, `ChainMap`** | `Counter.most_common()`, `deque(maxlen=k)`, `defaultdict(list)` | `02-data-manipulation-and-stdlib/01_collections_mastery.py` |
| **`itertools` y `functools`** | `groupby`, `islice`, `accumulate`, `combinations`, `@cache`, `partial` | `02-data-manipulation-and-stdlib/02_itertools_and_functools.py` |
| **Ordenamiento, `bisect` y `heapq`** | `sorted(key=...)`, `bisect_left/right`, `heappush/heappop`, `merge` | `02-data-manipulation-and-stdlib/03_sorting_bisect_and_heapq.py` |
| **Expresiones Regulares (`re`)** | `(?P<name>...)`, `(?=...)`, `(?<=...)`, `re.sub`, `re.finditer` | `02-data-manipulation-and-stdlib/04_regex_and_text_parsing.py` |
| **Fechas, Rutas, JSON y CSV** | `datetime.fromisoformat`, `timezone.utc`, `Path`, `csv.DictReader` | `02-data-manipulation-and-stdlib/05_dates_files_and_serialization.py` |
| **Pipelines ETL y Limpieza** | Normalización, interpolación, tablas pivote, detección IQR | `02-data-manipulation-and-stdlib/06_data_cleaning_pipelines.py` |
| **Clases, `@property`, `@dataclass`, `__slots__`** | `@dataclass(frozen=True, order=True)`, `field(default_factory=...)` | `03-oop-and-python-object-model/01_classes_dataclasses_and_slots.py` |
| **Métodos Mágicos (Dunders)** | `__repr__`, `__eq__`, `__hash__`, `__lt__`, `__getitem__`, `__call__` | `03-oop-and-python-object-model/02_dunder_magic_methods.py` |
| **Herencia, MRO, `ABC` y `Protocol`** | `super()`, `__mro__`, `@abstractmethod`, `@runtime_checkable Protocol` | `03-oop-and-python-object-model/03_inheritance_mro_and_protocols.py` |
| **Iteradores y Context Managers** | `__iter__`/`__next__`, `yield from`, `__enter__`/`__exit__`, `@contextmanager` | `03-oop-and-python-object-model/04_iterators_and_context_managers.py` |
| **Decoradores Avanzados** | `@functools.wraps`, fábricas parametrizadas, `inspect.signature` | `04-advanced-internals-and-metaprogramming/01_decorators_deep_dive.py` |
| **Descriptores y Lookup de Atributos** | `__set_name__`, `__get__`, `__set__`, `__getattr__`, `LazyProperty` | `04-advanced-internals-and-metaprogramming/02_descriptors_and_attributes.py` |
| **Metaclases y `__init_subclass__`** | `class Meta(type): __new__`, `__init_subclass__`, `type(name, bases, ns)` | `04-advanced-internals-and-metaprogramming/03_metaclasses_and_class_hooks.py` |
| **Memoria, `weakref` y Bytecode** | `weakref.WeakValueDictionary`, `dis.get_instructions`, `sys.getsizeof` | `04-advanced-internals-and-metaprogramming/04_memory_weakrefs_and_bytecode.py` |
| **Tipado Avanzado y Genéricos** | `Generic[T]`, `ParamSpec`, `TypedDict`, `TypeGuard`, `Annotated` | `04-advanced-internals-and-metaprogramming/05_typing_and_generics_advanced.py` |
| **`asyncio`: Corrutinas y Tareas** | `gather`, `TaskGroup`, `wait_for`, `Semaphore`, `asyncio.Queue` | `05-concurrency-and-async/01_asyncio_coroutines_and_tasks.py` |
| **Streams e Iteradores Asíncronos** | `__aiter__`/`__anext__`, `async for`, `@asynccontextmanager` | `05-concurrency-and-async/02_async_iterators_and_streams.py` |
| **Hilos (`threading`) y Locks** | `ThreadPoolExecutor`, `Lock`, `RLock`, `Event`, `as_completed` | `05-concurrency-and-async/03_threading_and_synchronization.py` |
| **Multiprocesamiento y Map-Reduce** | Particionado de lotes, `pickle`, reducción paralela CPU-bound | `05-concurrency-and-async/04_multiprocessing_and_cpu_bound.py` |
| **Two Pointers y Sliding Window** | Punteros opuestos, 3Sum, ventana deslizante fija y dinámica | `06-algorithms-and-patterns/01_two_pointers_and_sliding_window.py` |
| **Hashing, Prefix Sums y LRU Cache** | `prefix_sum - k`, `OrderedDict` LRU Cache en $O(1)$ | `06-algorithms-and-patterns/02_hashing_and_prefix_sums.py` |
| **Pilas y Colas Monótonas** | `MinStack`, Next Greater Element, Sliding Window Maximum | `06-algorithms-and-patterns/03_stacks_queues_and_monotonic.py` |
| **Variaciones de Búsqueda Binaria** | Bordes izq/der, arreglo rotado, búsqueda en espacio de respuestas | `06-algorithms-and-patterns/04_binary_search_variations.py` |
| **Árboles y Grafos (DFS, BFS, Dijkstra)** | `TreeNode`, validación BST, LCA, Kahn Topological Sort, Dijkstra | `06-algorithms-and-patterns/05_trees_and_graphs_traversal.py` |
| **Programación Dinámica y Backtracking** | Memoización vs Tabulación 1D/2D, Subconjuntos, Combinaciones | `06-algorithms-and-patterns/06_dynamic_programming_and_backtracking.py` |
| **Patrones de Diseño Pythonic** | Strategy, Registry/Factory, EventBus, Middleware Pipeline, QueryBuilder | `06-algorithms-and-patterns/07_pythonic_design_patterns.py` |
| **Clientes HTTP y Reintentos** | `httpx.Client`, `MockTransport`, backoff exponencial, manejo de errores | `07-api-and-network-consumption/01_http_clients_and_retries.py` |
| **Paginación y Rate Limiting** | Cursores con generadores, Token Bucket, lotes asíncronos | `07-api-and-network-consumption/02_pagination_and_rate_limiting.py` |
| **Circuit Breaker, Caché TTL y HMAC** | Máquina de estados `CircuitBreaker`, `ETag`/`304`, `hmac.compare_digest` | `07-api-and-network-consumption/03_circuit_breaker_and_caching.py` |
| **FastAPI y Validación Pydantic v2** | `@field_validator`, `@model_validator`, `Query`, `TestClient` | `08-fastapi-and-backend-services/01_routing_pydantic_and_validation.py` |
| **Inyección de Dependencias y Auth** | `Depends`, guardias de roles `RoleGuard`, sesiones `yield`, overrides | `08-fastapi-and-backend-services/02_dependency_injection_and_auth.py` |
| **Middlewares, Excepciones y CRUD** | `@app.exception_handler`, `@app.middleware("http")`, Idempotencia | `08-fastapi-and-backend-services/03_error_handling_middleware_and_crud.py` |
