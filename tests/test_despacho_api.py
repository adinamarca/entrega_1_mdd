"""Tests del caso de uso: Asignacion y Despacho."""


def _crear_y_preparar_pedido(client, token_operador, auth_header, pedido_payload) -> str:
    """Helper: crea un pedido y lo deja en 'Pendiente de asignacion'."""
    r = client.post("/pedidos", json=pedido_payload(), headers=auth_header(token_operador))
    pid = r.json()["pedido_id"]
    client.post(f"/pedidos/{pid}/validar", headers=auth_header(token_operador))
    client.put(
        f"/pedidos/{pid}/estado",
        json={"accion": "poner_pendiente"},
        headers=auth_header(token_operador),
    )
    return pid


def _registrar_repartidor(client, token_admin, auth_header) -> str:
    response = client.post(
        "/repartidores",
        json={
            "nombre": "Carlos Gomez",
            "max_pedidos": 3,
            "max_peso_kg": 50.0,
            "latitud": -33.45,
            "longitud": -70.65,
        },
        headers=auth_header(token_admin),
    )
    return response.json()["repartidor_id"]


def test_registrar_repartidor(client, token_admin, auth_header):
    response = client.post(
        "/repartidores",
        json={
            "nombre": "Maria Lopez",
            "max_pedidos": 2,
            "max_peso_kg": 30.0,
            "latitud": -33.42,
            "longitud": -70.60,
        },
        headers=auth_header(token_admin),
    )
    assert response.status_code == 201
    body = response.json()
    assert body["nombre"] == "Maria Lopez"
    assert body["disponible"] is True


def test_listar_repartidores_disponibles(client, token_admin, token_operador, auth_header):
    _registrar_repartidor(client, token_admin, auth_header)
    response = client.get("/repartidores/disponibles", headers=auth_header(token_operador))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_asignar_pedido_exitoso(
    client, token_operador, token_admin, auth_header, pedido_payload
):
    _registrar_repartidor(client, token_admin, auth_header)
    pid = _crear_y_preparar_pedido(client, token_operador, auth_header, pedido_payload)

    response = client.post(
        f"/pedidos/{pid}/asignar",
        json={"estrategia": "proximidad"},
        headers=auth_header(token_operador),
    )
    assert response.status_code == 201
    body = response.json()
    assert body["pedido_id"] == pid
    assert body["activa"] is True


def test_asignar_pedido_sin_repartidores_falla(
    client, token_operador, auth_header, pedido_payload
):
    pid = _crear_y_preparar_pedido(client, token_operador, auth_header, pedido_payload)
    response = client.post(
        f"/pedidos/{pid}/asignar",
        json={"estrategia": "proximidad"},
        headers=auth_header(token_operador),
    )
    assert response.status_code == 422  # regla de negocio


def test_asignar_pedido_no_pendiente_falla(
    client, token_operador, token_admin, auth_header, pedido_payload
):
    _registrar_repartidor(client, token_admin, auth_header)
    # Crear pedido pero NO ponerlo pendiente (queda en 'Creado')
    r = client.post("/pedidos", json=pedido_payload(), headers=auth_header(token_operador))
    pid = r.json()["pedido_id"]

    response = client.post(
        f"/pedidos/{pid}/asignar", headers=auth_header(token_operador)
    )
    assert response.status_code == 422


def test_cambio_estrategia_runtime(
    client, token_operador, token_admin, auth_header, pedido_payload
):
    """Strategy pattern: la estrategia es intercambiable por request."""
    _registrar_repartidor(client, token_admin, auth_header)
    pid = _crear_y_preparar_pedido(client, token_operador, auth_header, pedido_payload)

    response = client.post(
        f"/pedidos/{pid}/asignar",
        json={"estrategia": "round_robin"},
        headers=auth_header(token_operador),
    )
    assert response.status_code == 201
    assert response.json()["estrategia_usada"] == "round_robin"
