# 🧪 `99-playground/` — Zona de Práctica Libre y Simulacros

> **Tu laboratorio personal dentro de `python/` para experimentar, medir rendimiento, simular entrevistas en vivo y probar código asíncrono o APIs sin restricciones.**

---

## 📂 Qué incluye tu Zona de Práctica

| Archivo | Propósito | Cómo ejecutarlo |
| :--- | :--- | :--- |
| **[`../playground.py`](../playground.py)** | **Pizarrón Rápido (10 seg):** En la raíz de `python/`. Trae toda la `stdlib` importada y los helpers `ver()` y `medir()`. | Presiona **`X`** (y **`R`**) en `uv run katas`, o `python python/playground.py` |
| **[`sandbox.py`](sandbox.py)** | **Laboratorio de Internals y Rendimiento:** Compara dos algoritmos cara a cara (`comparar_rendimiento`), inspecciona el Bytecode de CPython (`ver_bytecode`) y mide bytes en RAM (`ver_memoria`). | Ábrelo en `uv run katas` y presiona **`R`** |
| **[`interview_sim.py`](interview_sim.py)** | **Simulador de Entrevista Técnica (UMPIRE):** Plantilla lista con tabla de casos de prueba `(entrada, esperado)` para practicar cualquier problema de LeetCode/HackerRank o inventado por ti sin IA. | Edita `resolver()`, define tus `CASOS` y presiona **`R`** |
| **[`async_api_lab.py`](async_api_lab.py)** | **Laboratorio de `asyncio`, `httpx` y `FastAPI`:** Espacio listo con un servidor `FastAPI` + `TestClient` en memoria y un cliente `httpx.MockTransport` para experimentar con endpoints, Pydantic v2 y corrutinas. | Ábrelo en `uv run katas` y presiona **`R`** |

---

## 💡 Ventajas de Diseño

1. **Aislamiento Total de la Auditoría:** Ninguno de los archivos del playground empieza con el prefijo `[0-9][0-9]_`, por lo que puedes dejar código experimental o a medio terminar sin que `pytest` ni `uv run katas --test` fallen.
2. **Integración Nativa con `DEV-KATAS STUDIO`:** Todos los archivos aparecen en el panel izquierdo de `uv run katas`. Puedes seleccionarlos, ejecutarlos con **`R`**, vaciar su bloque de trabajo con **`P`** y restaurar su plantilla inicial con **`S`**.
