from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

"""
================================================================================
MÓDULO 03: POO Y EL MODELO DE OBJETOS DE PYTHON
Kata 01: Clases, Dataclasses y Optimización con __slots__
================================================================================

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
--------------------------------------------------------------------------------
1. Anatomía de una Clase Moderna:
   - `__init__(self, ...)`: Inicializador de estado de instancia.
   - Atributos de Clase vs Instancia:
     * Definidos en el cuerpo de la clase -> compartidos por todas las instancias.
     * Definidos en `self.attr = val` -> viven en `self.__dict__` de cada objeto.
   - `@property` y `@x.setter`: Encapsulamiento Pythonico (getters/setters sin
     cambiar la interfaz pública de acceso por atributo `obj.x`).
   - `@classmethod`: Recibe `cls` (la clase misma). Ideal para constructores
     alternativos (`from_dict`, `from_json`, factorías).
   - `@staticmethod`: Función utilitaria agrupada dentro del namespace de la
     clase; no recibe ni `self` ni `cls`.

2. `@dataclass` (PEP 557 - Objetos de Datos y Valor):
   - Genera automáticamente `__init__`, `__repr__`, `__eq__` (y opcionalmente
     `__lt__`, `__hash__`).
   - Parámetros clave del decorador:
     * `@dataclass(frozen=True)`: Inmutabilidad simulada (lanza `FrozenInstanceError`
       al intentar reasignar atributos). Permite que la instancia sea hashable.
     * `@dataclass(order=True)`: Genera `__lt__`, `__le__`, `__gt__`, `__ge__`
       comparando la tupla de campos en orden de definición.
     * `@dataclass(kw_only=True)`: Obliga a pasar los argumentos por nombre.
     * `@dataclass(slots=True)` (Python 3.10+): Genera `__slots__` automáticamente.
   - Configuración de campos con `field(...)`:
     * `items: list[str] = field(default_factory=list)` -> Evita la trampa de
       valores mutables por defecto compartidos.
     * `total: float = field(init=False, default=0.0)` -> Campo calculado que no
       se pide en `__init__`.
     * `secret: str = field(repr=False, compare=False)` -> Excluido de logs e igualdad.
   - `__post_init__(self)`: Hook ejecutado inmediatamente después del `__init__`
     generado. En clases `frozen=True`, para normalizar un campo dentro de
     `__post_init__`, se debe usar `object.__setattr__(self, "campo", valor)`.

3. `__slots__` (Optimización de Layout en Memoria):
   - Por defecto, cada instancia en Python almacena sus atributos en un
     diccionario dinámico (`self.__dict__`), lo cual consume mucha RAM cuando se
     instancian millones de objetos.
   - Definir `__slots__ = ("sensor_id", "timestamp", "value")` reemplaza el
     `__dict__` dinámico por un array compacto de descriptores a nivel de C:
     * Ahorra entre 40% y 60% de memoria RAM por instancia.
     * Impide agregar atributos arbitrarios en tiempo de ejecución (`AttributeError`).

🧠 MODELO MENTAL Y TRAMPAS COMUNES
--------------------------------------------------------------------------------
- Trampa del Shadowing de Atributos de Clase: Si defines `count = 0` en la clase
  y luego haces `self.count += 1` en un método, Python crea un atributo de
  instancia `self.__dict__["count"]` ocultando el de la clase. Para mutar un
  contador global de clase usa `type(self).count += 1` o `NombreClase.count += 1`.
- Trampa de Mutables en Dataclasses: Python prohíbe `items: list = []` en una
  dataclass lanzando `ValueError: mutable default <class 'list'> is not allowed`.
  Siempre usa `field(default_factory=list)`.
================================================================================
"""


# ==============================================================================
# EJERCICIO 1: Encapsulamiento con @property y @classmethod (BankAccount)
# ==============================================================================
class BankAccount:
    """
    Cuenta bancaria con validación estricta de saldo y constructor alternativo.

    Reglas:
    - `__init__(self, owner: str, initial_balance: float = 0.0)`:
      * `owner` no puede estar vacío tras `.strip()` (lanzar `ValueError`).
      * `initial_balance` no puede ser negativo (lanzar `ValueError`).
      * Almacenar saldo en atributo privado `self._balance = float(initial_balance)`.
    - `@property def balance(self) -> float`: Devuelve `self._balance`.
    - `deposit(self, amount: float) -> float`:
      * Si `amount <= 0`, lanzar `ValueError`.
      * Suma `amount` a `self._balance` y devuelve el nuevo saldo.
    - `withdraw(self, amount: float) -> float`:
      * Si `amount <= 0`, lanzar `ValueError`.
      * Si `amount > self._balance`, lanzar `ValueError("Fondos insuficientes")`.
      * Resta `amount` y devuelve el nuevo saldo.
    - `@classmethod def from_dict(cls, data: dict[str, Any]) -> BankAccount`:
      * Construye y retorna una instancia extrayendo `"owner"` y `"balance"`
        (con default `0.0` si `"balance"` no existe en el diccionario).
    """

    def __init__(self, owner: str, initial_balance: float = 0.0) -> None:
        # BEGIN_SOLUTION
        cleaned_owner = owner.strip()
        if not cleaned_owner:
            raise ValueError("El titular de la cuenta no puede estar vacío.")
        if initial_balance < 0:
            raise ValueError("El saldo inicial no puede ser negativo.")
        self.owner: str = cleaned_owner
        self._balance: float = float(initial_balance)
        # END_SOLUTION

    @property
    def balance(self) -> float:
        # BEGIN_SOLUTION
        return self._balance
        # END_SOLUTION

    def deposit(self, amount: float) -> float:
        # BEGIN_SOLUTION
        if amount <= 0:
            raise ValueError("El monto a depositar debe ser positivo.")
        self._balance += float(amount)
        return self._balance
        # END_SOLUTION

    def withdraw(self, amount: float) -> float:
        # BEGIN_SOLUTION
        if amount <= 0:
            raise ValueError("El monto a retirar debe ser positivo.")
        if amount > self._balance:
            raise ValueError("Fondos insuficientes")
        self._balance -= float(amount)
        return self._balance
        # END_SOLUTION

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BankAccount:
        # BEGIN_SOLUTION
        return cls(
            owner=str(data["owner"]),
            initial_balance=float(data.get("balance", 0.0)),
        )
        # END_SOLUTION


# ==============================================================================
# EJERCICIO 2: Value Object Inmutable con @dataclass(frozen=True, order=True)
# ==============================================================================
@dataclass(frozen=True, order=True)
class ImmutableMoney:
    """
    Representa un valor monetario inmutable y ordenable.
    Nota: `currency` va primero para que el ordenamiento agrupe por divisa y luego por monto,
    o si queremos ordenar solo cuando son comparables, sigue el orden de campos `(currency, amount)`.

    En `__post_init__`:
    1. Normaliza `currency` a mayúsculas sin espacios (`currency.strip().upper()`).
       Si la longitud resultante no es exactamente 3 caracteres, lanza `ValueError`.
    2. Redondea `amount` a 2 decimales (`round(float(self.amount), 2)`).
    3. Como la dataclass es `frozen=True`, usa `object.__setattr__(self, ...)`
       para guardar los valores normalizados.
    """

    currency: str
    amount: float

    def __post_init__(self) -> None:
        # BEGIN_SOLUTION
        normalized_currency = self.currency.strip().upper()
        if len(normalized_currency) != 3 or not normalized_currency.isalpha():
            raise ValueError(f"Código de divisa inválido: {self.currency!r}")
        rounded_amount = round(float(self.amount), 2)
        object.__setattr__(self, "currency", normalized_currency)
        object.__setattr__(self, "amount", rounded_amount)
        # END_SOLUTION


# ==============================================================================
# EJERCICIO 3: Dataclass con default_factory y campos calculados (OrderAggregate)
# ==============================================================================
@dataclass
class OrderAggregate:
    """
    Agregado de pedido que gestiona una lista de precios de ítems y mantiene
    el total actualizado.

    Campos:
    - `order_id`: `str`
    - `items`: `list[tuple[str, float]]` (usa `field(default_factory=list)`)
    - `total`: `float` (usa `field(init=False, default=0.0)`)

    En `__post_init__`:
    - Recalcula `self.total` sumando los precios de `self.items` por si se
      pasaron ítems iniciales al constructor.

    Método `add_item(self, name: str, price: float) -> None`:
    - Si `price < 0`, lanza `ValueError`.
    - Añade `(name, float(price))` a `self.items` y actualiza `self.total`
      (redondeado a 2 decimales).
    """

    order_id: str
    items: list[tuple[str, float]] = field(default_factory=list)
    total: float = field(init=False, default=0.0)

    def __post_init__(self) -> None:
        # BEGIN_SOLUTION
        self.total = round(sum(price for _, price in self.items), 2)
        # END_SOLUTION

    def add_item(self, name: str, price: float) -> None:
        # BEGIN_SOLUTION
        if price < 0:
            raise ValueError("El precio del ítem no puede ser negativo.")
        self.items.append((name, float(price)))
        self.total = round(sum(p for _, p in self.items), 2)
        # END_SOLUTION


# ==============================================================================
# EJERCICIO 4: Optimización de Memoria con __slots__ (CompactTelemetryPoint)
# ==============================================================================
class CompactTelemetryPoint:
    """
    Punto de telemetría diseñado para instanciarse millones de veces con bajo
    consumo de memoria usando `__slots__`.
    """

    __slots__ = ("sensor_id", "timestamp", "value")

    def __init__(self, sensor_id: str, timestamp: int, value: float) -> None:
        # BEGIN_SOLUTION
        self.sensor_id = sensor_id
        self.timestamp = timestamp
        self.value = value
        # END_SOLUTION


def verify_slots_behavior(point: CompactTelemetryPoint) -> dict[str, bool]:
    """
    Inspecciona una instancia de `CompactTelemetryPoint` y verifica:
    1. `"has_dict"`: `True` si el objeto tiene atributo `__dict__`, `False` en caso contrario.
    2. `"rejects_dynamic_attr"`: `True` si intentar asignar `point.extra_field = 123`
       lanza `AttributeError`, `False` si lo permite.
    """
    # BEGIN_SOLUTION
    has_dict = hasattr(point, "__dict__")
    rejects_dynamic = False
    try:
        point.extra_field = 123  # type: ignore[attr-defined]
    except AttributeError:
        rejects_dynamic = True
    return {
        "has_dict": has_dict,
        "rejects_dynamic_attr": rejects_dynamic,
    }
    # END_SOLUTION


# ==============================================================================
# EJERCICIO 5: Atributos de Clase vs Instancia sin Shadowing (RegistryCounter)
# ==============================================================================
class RegistryCounter:
    """
    Demuestra la diferencia entre estado compartido de clase y estado propio
    de cada instancia sin caer en el bug de shadowing (`self.active_instances += 1`).

    - Atributo de clase `active_instances: int = 0`
    - En `__init__(self, name: str)`:
      * Guarda `self.name = name`
      * Incrementa `RegistryCounter.active_instances` en 1 y asigna a
        `self.instance_number` el valor actual de `RegistryCounter.active_instances`.
    - `@classmethod def reset_counter(cls) -> None`:
      * Reinicia `cls.active_instances = 0`.
    """

    active_instances: int = 0

    def __init__(self, name: str) -> None:
        # BEGIN_SOLUTION
        self.name = name
        type(self).active_instances += 1
        self.instance_number: int = type(self).active_instances
        # END_SOLUTION

    @classmethod
    def reset_counter(cls) -> None:
        # BEGIN_SOLUTION
        cls.active_instances = 0
        # END_SOLUTION


# ==============================================================================
# SUITE DE VERIFICACIÓN Y TESTS
# ==============================================================================
def test_kata() -> None:
    # 1. BankAccount
    acc = BankAccount.from_dict({"owner": "  Ada Lovelace ", "balance": 100.0})
    assert acc.owner == "Ada Lovelace"
    assert acc.balance == 100.0
    assert acc.deposit(50.5) == 150.5
    assert acc.withdraw(20.5) == 130.0
    try:
        acc.withdraw(500.0)
        assert False, "Debió lanzar ValueError por fondos insuficientes"
    except ValueError:
        pass

    # 2. ImmutableMoney
    m1 = ImmutableMoney(" usd ", 10.556)
    m2 = ImmutableMoney("USD", 20.0)
    assert m1.currency == "USD"
    assert m1.amount == 10.56
    assert m1 < m2
    assert len({m1, ImmutableMoney("USD", 10.56)}) == 1

    # 3. OrderAggregate
    order = OrderAggregate("ORD-01", [("Teclado", 49.99)])
    assert order.total == 49.99
    order.add_item("Mouse", 25.01)
    assert order.total == 75.0
    assert len(order.items) == 2

    # 4. CompactTelemetryPoint (__slots__)
    pt = CompactTelemetryPoint("temp-01", 1700000000, 23.5)
    check = verify_slots_behavior(pt)
    assert check == {"has_dict": False, "rejects_dynamic_attr": True}

    # 5. RegistryCounter
    RegistryCounter.reset_counter()
    r1 = RegistryCounter("worker-a")
    r2 = RegistryCounter("worker-b")
    assert r1.instance_number == 1
    assert r2.instance_number == 2
    assert RegistryCounter.active_instances == 2
    assert "active_instances" not in r1.__dict__


def run_verification() -> None:
    import time

    print("=" * 72)
    print("🚀 VERIFICANDO MÓDULO 03 - KATA 01: Clases, Dataclasses y __slots__")
    print("=" * 72)

    checks = [
        ("Ej 1: BankAccount (@property y @classmethod)", lambda: _check_ej1()),
        ("Ej 2: ImmutableMoney (@dataclass frozen & order)", lambda: _check_ej2()),
        ("Ej 3: OrderAggregate (default_factory y post_init)", lambda: _check_ej3()),
        ("Ej 4: CompactTelemetryPoint (__slots__ layout)", lambda: _check_ej4()),
        ("Ej 5: RegistryCounter (Class vs Instance attrs)", lambda: _check_ej5()),
    ]

    passed = 0
    for title, fn in checks:
        t0 = time.perf_counter()
        try:
            fn()
            ms = (time.perf_counter() - t0) * 1000
            print(f"  ✅ [PASS] {title} ({ms:.2f} ms)")
            passed += 1
        except NotImplementedError:
            print(f"  ⏳ [PENDIENTE] {title}")
        except Exception as exc:
            print(f"  ❌ [FAIL] {title} -> {type(exc).__name__}: {exc}")

    print("-" * 72)
    print(f"Resultado final: {passed}/{len(checks)} ejercicios superados.")
    if passed < len(checks):
        raise SystemExit(1)


def _check_ej1() -> None:
    acc = BankAccount.from_dict({"owner": " Grace Hopper ", "balance": 200.0})
    assert acc.owner == "Grace Hopper"
    assert acc.deposit(50.0) == 250.0
    assert acc.withdraw(100.0) == 150.0


def _check_ej2() -> None:
    m1 = ImmutableMoney(" eur ", 15.999)
    m2 = ImmutableMoney("EUR", 25.0)
    assert m1.currency == "EUR" and m1.amount == 16.0
    assert m1 < m2


def _check_ej3() -> None:
    o1 = OrderAggregate("ORD-1")
    o2 = OrderAggregate("ORD-2")
    o1.add_item("Libro", 30.0)
    assert o1.total == 30.0
    assert o2.total == 0.0 and len(o2.items) == 0


def _check_ej4() -> None:
    pt = CompactTelemetryPoint("s1", 100, 1.5)
    assert verify_slots_behavior(pt) == {"has_dict": False, "rejects_dynamic_attr": True}


def _check_ej5() -> None:
    RegistryCounter.reset_counter()
    a = RegistryCounter("a")
    b = RegistryCounter("b")
    assert a.instance_number == 1 and b.instance_number == 2
    assert RegistryCounter.active_instances == 2
    assert "active_instances" not in a.__dict__


if __name__ == "__main__":
    run_verification()
