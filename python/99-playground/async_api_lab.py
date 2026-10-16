from __future__ import annotations

import asyncio
import time
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.testclient import TestClient
import httpx
from pydantic import BaseModel, Field

"""
🌐 LABORATORIO ASYNC, HTTPX Y FASTAPI (`99-playground/async_api_lab.py`)
===============================================================================
Usa este laboratorio para practicar y prototipar en segundos:
1. Corrutinas y concurrencia con `asyncio` (`gather`, `TaskGroup`, `Semaphore`).
2. Clientes HTTP simulados 100% offline con `httpx.MockTransport`.
3. Endpoints `FastAPI` + esquemas `Pydantic v2` probados en vivo con `TestClient`.
===============================================================================
"""

# ─── Mini App FastAPI para experimentar ──────────────────────────────────────
app = FastAPI(title="Playground API Lab")


class NotaCreate(BaseModel):
    titulo: str = Field(..., min_length=2)
    tags: list[str] = Field(default_factory=list)


NOTAS_MEMORIA: list[dict[str, Any]] = []


@app.post("/notas", status_code=status.HTTP_201_CREATED)
def crear_nota(payload: NotaCreate) -> dict[str, Any]:
    nueva = {"id": len(NOTAS_MEMORIA) + 1, "titulo": payload.titulo.strip(), "tags": payload.tags}
    NOTAS_MEMORIA.append(nueva)
    return nueva


@app.get("/notas")
def listar_notas(tag: str | None = Query(default=None)) -> list[dict[str, Any]]:
    if tag is None:
        return NOTAS_MEMORIA
    return [n for n in NOTAS_MEMORIA if tag in n["tags"]]


# ==============================================================================
# 👇 EXPERIMENTA CON ASYNCIO, HTTPX Y FASTAPI AQUÍ ABAJO 👇
# ==============================================================================
async def probar_corrutinas() -> list[str]:
    # BEGIN_SOLUTION
    async def tarea_simulada(nombre: str, demora: float) -> str:
        await asyncio.sleep(demora)
        return f"{nombre}:ok"

    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(tarea_simulada("auth", 0.002))
        t2 = tg.create_task(tarea_simulada("pagos", 0.001))

    return [t1.result(), t2.result()]
    # END_SOLUTION


def probar_endpoints_fastapi() -> None:
    NOTAS_MEMORIA.clear()
    client = TestClient(app)

    r1 = client.post("/notas", json={"titulo": "Repasar descriptores", "tags": ["python", "oop"]})
    print(f"🚀 POST /notas -> status={r1.status_code}, body={r1.json()}")

    r2 = client.get("/notas", params={"tag": "python"})
    print(f"📥 GET  /notas?tag=python -> {r2.json()}")


if __name__ == "__main__":
    print("=" * 72)
    print("🌐 LABORATORIO ASYNC & FASTAPI (async_api_lab.py)")
    print("=" * 72)
    t0 = time.perf_counter()
    res_async = asyncio.run(probar_corrutinas())
    print(f"⚡ Resultado asyncio.TaskGroup: {res_async}")
    probar_endpoints_fastapi()
    print("-" * 72)
    print(f"✔ Laboratorio ejecutado en {(time.perf_counter() - t0) * 1000:.2f} ms")
    print("=" * 72)
