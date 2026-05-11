"""Tests de autenticacion y autorizacion."""


def test_login_credenciales_correctas(client):
    response = client.post(
        "/auth/login", json={"username": "operador1", "password": "op123"}
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["role"] == "operador"
    assert body["token_type"] == "bearer"


def test_login_credenciales_invalidas(client):
    response = client.post(
        "/auth/login", json={"username": "operador1", "password": "WRONG"}
    )
    assert response.status_code == 401


def test_endpoint_sin_token_devuelve_401(client):
    response = client.post("/pedidos", json={})
    assert response.status_code == 401


def test_endpoint_con_rol_incorrecto_devuelve_403(
    client, token_repartidor, auth_header, pedido_payload
):
    # POST /pedidos requiere operador o integracion; repartidor no debe poder
    response = client.post(
        "/pedidos",
        json=pedido_payload(),
        headers=auth_header(token_repartidor),
    )
    assert response.status_code == 403


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
