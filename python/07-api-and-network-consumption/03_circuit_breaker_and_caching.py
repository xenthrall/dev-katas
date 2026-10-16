from __future__ import annotations

import hashlib
import hmac
import sys
import time
from typing import Any, Callable

import httpx

"""
MÓDULO 07 — CONSUMO DE APIS Y RED: 03. CIRCUIT BREAKER, CACHÉ ETAG Y HMAC
===============================================================================
Estudio profundo y práctica deliberada sobre patrones de resiliencia en
sistemas distribuidos: máquina de estados **Circuit Breaker**, revalidación de
caché HTTP con `ETag` (`If-None-Match` / `304 Not Modified`) y verificación de
integridad de Webhooks con **HMAC-SHA256** en tiempo constante.

📚 GUÍA DE SINTAXIS Y REFERENCIA RÁPIDA
-------------------------------------------------------------------------------
1. Máquina de Estados del Circuit Breaker:
   - `CLOSED`: Las llamadas pasan normalmente. Si acumula `failure_threshold`
     fallos consecutivos, transiciona a `OPEN`.
   - `OPEN`: Corta inmediatamente lanzando `CircuitOpenError` sin golpear al
     servicio caído. Cuando pasan `recovery_timeout` segundos, pasa a `HALF_OPEN`.
   - `HALF_OPEN`: Permite una llamada de prueba; si tiene éxito vuelve a `CLOSED`
     (reiniciando fallos a 0), si falla regresa a `OPEN`.

2. Caché Condicional HTTP con `ETag`:
   - Si tenemos en caché `(etag, payload)`, enviamos la cabecera
     `If-None-Match: <etag>`. Si el servidor responde `304 Not Modified`,
     devolvemos el `payload` en caché sin descargar el cuerpo de nuevo.

3. Verificación Segura de Webhooks (`hmac.compare_digest`):
   - ❌ Nunca compares firmas criptográficas con `==` (vulnerable a Timing Attacks).
   - ✅ Usa siempre `hmac.compare_digest(firma_calculada, firma_recibida)`.
"""


class CircuitOpenError(RuntimeError):
    """Lanzada cuando el Circuit Breaker está abierto."""


class CircuitBreaker:
    """Implementación determinista del patrón Circuit Breaker."""

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float = 10.0,
        clock_fn: Callable[[], float] = time.monotonic,
    ) -> None:
        # BEGIN_SOLUTION
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.clock_fn = clock_fn
        self._state = "CLOSED"
        self._failures = 0
        self._opened_at = 0.0
        # END_SOLUTION

    @property
    def state(self) -> str:
        # BEGIN_SOLUTION
        if (
            self._state == "OPEN"
            and (self.clock_fn() - self._opened_at) >= self.recovery_timeout
        ):
            self._state = "HALF_OPEN"
        return self._state
        # END_SOLUTION

    def call(self, fn: Callable[[], Any]) -> Any:
        # BEGIN_SOLUTION
        current_state = self.state
        if current_state == "OPEN":
            raise CircuitOpenError("Circuito abierto")

        try:
            result = fn()
        except Exception:
            self._failures += 1
            if current_state == "HALF_OPEN" or self._failures >= self.failure_threshold:
                self._state = "OPEN"
                self._opened_at = self.clock_fn()
            raise

        self._failures = 0
        self._state = "CLOSED"
        return result
        # END_SOLUTION


class ETagHttpClient:
    """Cliente HTTP que almacena respuestas por URL con su `ETag` y envía `If-None-Match`."""

    def __init__(self, client: httpx.Client) -> None:
        self.client = client
        self._cache: dict[str, tuple[str, dict[str, Any]]] = {}

    def get_json(self, url: str) -> dict[str, Any]:
        # BEGIN_SOLUTION
        headers: dict[str, str] = {}
        if url in self._cache:
            etag, _ = self._cache[url]
            headers["If-None-Match"] = etag

        resp = self.client.get(url, headers=headers)
        if resp.status_code == 304 and url in self._cache:
            return self._cache[url][1]

        resp.raise_for_status()
        data = dict(resp.json())
        new_etag = resp.headers.get("ETag")
        if new_etag:
            self._cache[url] = (new_etag, data)
        return data
        # END_SOLUTION


def verify_webhook_hmac_sha256(
    secret: str, payload_bytes: bytes, signature_header: str
) -> bool:
    """Verifica una cabecera `sha256=<hex_digest>` usando HMAC-SHA256 y `hmac.compare_digest`."""
    # BEGIN_SOLUTION
    expected_mac = hmac.new(
        secret.encode("utf-8"), payload_bytes, hashlib.sha256
    ).hexdigest()
    expected_header = f"sha256={expected_mac}"
    return hmac.compare_digest(expected_header, signature_header.strip())
    # END_SOLUTION


# ===============================================================================
# ARNESES DE VERIFICACIÓN Y PRUEBAS
# ===============================================================================


def check_circuit_breaker() -> None:
    now = 0.0
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=5.0, clock_fn=lambda: now)

    def _fail() -> None:
        raise ConnectionError("down")

    for _ in range(2):
        try:
            cb.call(_fail)
        except ConnectionError:
            pass

    assert cb.state == "OPEN"
    try:
        cb.call(lambda: "ok")
        raise AssertionError("Debió lanzar CircuitOpenError")
    except CircuitOpenError:
        pass

    now += 6.0
    assert cb.state == "HALF_OPEN"
    assert cb.call(lambda: "recovered") == "recovered"
    assert cb.state == "CLOSED"


def check_etag_http_client() -> None:
    def _handler(request: httpx.Request) -> httpx.Response:
        if request.headers.get("If-None-Match") == '"v1"':
            return httpx.Response(304)
        return httpx.Response(200, headers={"ETag": '"v1"'}, json={"price": 99})

    with httpx.Client(
        transport=httpx.MockTransport(_handler), base_url="https://api.test"
    ) as raw_client:
        etag_client = ETagHttpClient(raw_client)
        assert etag_client.get_json("/item") == {"price": 99}
        assert etag_client.get_json("/item") == {"price": 99}


def check_verify_webhook_hmac_sha256() -> None:
    secret = "whsec_test_key"
    body = b'{"event":"invoice.paid"}'
    valid_sig = (
        "sha256="
        + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    )
    assert verify_webhook_hmac_sha256(secret, body, valid_sig) is True
    assert verify_webhook_hmac_sha256(secret, body, "sha256=deadbeef") is False


CHECKS: list[tuple[str, Callable[[], None]]] = [
    ("01. CircuitBreaker (State Machine)", check_circuit_breaker),
    ("02. ETagHttpClient (304 Not Modified)", check_etag_http_client),
    ("03. verify_webhook_hmac_sha256 (HMAC)", check_verify_webhook_hmac_sha256),
]


def test_kata() -> None:
    for _, check_fn in CHECKS:
        check_fn()


def run_verification() -> None:
    print("=" * 72)
    print("🧪 VERIFICACIÓN: 03_circuit_breaker_and_caching.py")
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
