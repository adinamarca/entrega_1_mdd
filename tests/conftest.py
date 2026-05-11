"""Configuracion compartida de pytest.

Provee fixtures comunes:
- client: TestClient de FastAPI con el container reiniciado
- tokens por rol: tokens JWT pre-generados para tests de autorizacion
"""

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.dependencies import get_container
from src.domain.repartidores.pool import DriverPool


@pytest.fixture
def client():
    """Cliente HTTP con estado limpio antes de cada test."""
    # Reset del singleton y del container cached
    DriverPool.reset()
    get_container.cache_clear()
    app = create_app()
    return TestClient(app)


def _login(client: TestClient, username: str, password: str) -> str:
    response = client.post(
        "/auth/login", json={"username": username, "password": password}
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def token_operador(client) -> str:
    return _login(client, "operador1", "op123")


@pytest.fixture
def token_admin(client) -> str:
    return _login(client, "admin1", "admin123")


@pytest.fixture
def token_repartidor(client) -> str:
    return _login(client, "repartidor1", "rep123")


@pytest.fixture
def token_integracion(client) -> str:
    return _login(client, "integracion1", "int123")


@pytest.fixture
def auth_header():
    """Factory para generar el header Authorization Bearer."""
    return lambda token: {"Authorization": f"Bearer {token}"}


def _pedido_payload(**overrides) -> dict:
    base = {
        "canal": "web",
        "origen": {
            "calle": "Av. Principal",
            "numero": "100",
            "ciudad": "Santiago",
            "comuna": "Providencia",
        },
        "punto_origen_id": "BOD-001",
        "destino": {
            "calle": "Calle Destino",
            "numero": "456",
            "ciudad": "Santiago",
            "comuna": "Las Condes",
        },
        "destinatario": {
            "nombre": "Juan Perez",
            "telefono": "+56912345678",
            "email": "juan@example.com",
        },
        "tipo_entrega": "normal",
        "tipo_carga": "estandar",
        "peso_kg": 5.0,
    }
    base.update(overrides)
    return base


@pytest.fixture
def pedido_payload():
    return _pedido_payload
