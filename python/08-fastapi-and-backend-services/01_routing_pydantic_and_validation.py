from __future__ import annotations

import sys
import time
from typing import Callable

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field, field_validator, model_validator

"""
MÓDULO 08 — FASTAPI Y SERVICIOS BACKEND: 01. ROUTING, PYDANTIC V2 Y VALIDACIÓN
===============================================================================
Estudio profundo y práctica deliberada sobre diseño de contratos de API con
**Pydantic v2** (`@field_validator`, `@model_validator`), endpoints RESTful en
**FastAPI** (`POST 201`, `GET` con `Query`, `PATCH` parcial con `exclude_unset`)
y pruebas de integración rápidas con `TestClient`.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Validadores en Pydantic v2:
   - `@field_validator("sku")` + `@classmethod`: Normaliza o valida un campo individual.
   - `@model_validator(mode="after")`: Valida invariantes cruzadas entre varios
     campos de la instancia (`self`) ya construida.

2. Actualizaciones Parciales (`PATCH`):
   - `payload.model_dump(exclude_unset=True)` devuelve únicamente los campos que
     el cliente envió explícitamente en el JSON, evitando sobrescribir con `None`
     los campos omitidos.

🧠 MODELO MENTAL Y TRAMPAS COMUNES
-------------------------------------------------------------------------------
- Usa siempre un esquema de salida (`response_model=ProductOut`) separado del
  esquema de entrada (`ProductCreate`) para no filtrar costos internos, hashes
  o secretos en las respuestas HTTP.
"""


class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=3)
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    discount_price: float | None = Field(default=None, gt=0)
    internal_supplier_secret: str = Field(default="internal-only")

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str) -> str:
        # BEGIN_SOLUTION
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("SKU no puede estar vacío")
        return cleaned
        # END_SOLUTION

    @model_validator(mode="after")
    def check_discount_below_price(self) -> ProductCreate:
        # BEGIN_SOLUTION
        if self.discount_price is not None and self.discount_price >= self.price:
            raise ValueError("discount_price debe ser estrictamente menor que price")
        return self
        # END_SOLUTION


class ProductOut(BaseModel):
    id: int
    sku: str
    name: str
    price: float
    discount_price: float | None = None


class ProductPatch(BaseModel):
    name: str | None = None
    price: float | None = Field(default=None, gt=0)


def create_catalog_app() -> FastAPI:
    """Construye una aplicación FastAPI con `POST /products`, `GET /products` y `PATCH /products/{id}`."""
    app = FastAPI()
    db: dict[int, dict[str, object]] = {}
    seq = 0

    @app.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
    def create_product(payload: ProductCreate) -> dict[str, object]:
        # BEGIN_SOLUTION
        nonlocal seq
        seq += 1
        record: dict[str, object] = {
            "id": seq,
            "sku": payload.sku,
            "name": payload.name.strip(),
            "price": payload.price,
            "discount_price": payload.discount_price,
            "internal_supplier_secret": payload.internal_supplier_secret,
        }
        db[seq] = record
        return record
        # END_SOLUTION

    @app.get("/products", response_model=list[ProductOut])
    def list_products(min_price: float = Query(default=0.0, ge=0.0)) -> list[dict[str, object]]:
        # BEGIN_SOLUTION
        return [
            item
            for item in db.values()
            if float(item["price"]) >= min_price  # type: ignore[arg-type]
        ]
        # END_SOLUTION

    @app.patch("/products/{product_id}", response_model=ProductOut)
    def patch_product(product_id: int, patch: ProductPatch) -> dict[str, object]:
        # BEGIN_SOLUTION
        if product_id not in db:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        updates = patch.model_dump(exclude_unset=True)
        db[product_id].update(updates)
        return db[product_id]
        # END_SOLUTION

    return app


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_pydantic_validation_and_routes() -> None:
    app = create_catalog_app()
    client = TestClient(app)

    # 1. Crear producto válido y verificar que internal_supplier_secret no se filtra
    r1 = client.post(
        "/products",
        json={"sku": " gpu-4090 ", "name": "RTX 4090", "price": 1600.0, "discount_price": 1499.0},
    )
    assert r1.status_code == 201
    body1 = r1.json()
    assert body1["sku"] == "GPU-4090"
    assert "internal_supplier_secret" not in body1

    # 2. Rechazar discount_price >= price con 422
    r_bad = client.post(
        "/products",
        json={"sku": "bad-01", "name": "Item", "price": 50.0, "discount_price": 60.0},
    )
    assert r_bad.status_code == 422

    # 3. Filtrar por min_price y actualizar parcialmente con PATCH
    r_patch = client.patch("/products/1", json={"price": 1550.0})
    assert r_patch.status_code == 200
    assert r_patch.json()["price"] == 1550.0
    assert r_patch.json()["name"] == "RTX 4090"

    r_list = client.get("/products", params={"min_price": 1500.0})
    assert len(r_list.json()) == 1


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. Pydantic v2 & FastAPI Catalog Routes", check_pydantic_validation_and_routes),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 01_routing_pydantic_and_validation.py")
    print("=" * 72)
    passed = 0
    failed = 0
    pending = 0

    for name, check_fn in CHECKS:
        start = time.perf_counter()
        try:
            check_fn()
            elapsed_ms = (time.perf_counter() - start) * 1000
            print(f"✅ [PASS]      {name:<35} ({elapsed_ms:.2f} ms)")
            passed += 1
        except NotImplementedError:
            print(f"⏳ [PENDIENTE] {name}")
            pending += 1
        except Exception as exc:
            print(f"❌ [FAIL]      {name}: {type(exc).__name__}: {exc}")
            failed += 1

    print("-" * 72)
    print(f"Resumen: {passed} pasadas | {pending} pendientes | {failed} fallidas")
    print("=" * 72)
    if failed > 0 or pending > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_verification()
