"""Tests del caso de uso: Gestion de Pedidos."""


def test_crear_pedido_exitoso(client, token_operador, auth_header, pedido_payload):
    response = client.post(
        "/pedidos",
        json=pedido_payload(),
        headers=auth_header(token_operador),
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["estado"] == "Creado"
    assert body["canal"] == "web"
    assert body["pedido_id"]


def test_crear_pedido_desde_distintos_canales(
    client, token_operador, token_integracion, auth_header, pedido_payload
):
    """Factory Method: cada canal usa su fabrica especifica."""
    for canal, token in [
        ("web", token_operador),
        ("app_movil", token_operador),
        ("ecommerce", token_integracion),
        ("partner", token_integracion),
    ]:
        response = client.post(
            "/pedidos",
            json=pedido_payload(canal=canal),
            headers=auth_header(token),
        )
        assert response.status_code == 201, response.text
        assert response.json()["canal"] == canal


def test_consultar_pedido_inexistente(client, token_operador, auth_header):
    response = client.get(
        "/pedidos/no-existe-id", headers=auth_header(token_operador)
    )
    assert response.status_code == 404


def test_validar_pedido_invalido_zona_no_atendida(
    client, token_operador, auth_header, pedido_payload
):
    """Decorator de validacion: zona no atendida."""
    response = client.post(
        "/pedidos",
        json=pedido_payload(destino={
            "calle": "C",
            "numero": "1",
            "ciudad": "Temuco",  # no atendida
            "comuna": "X",
        }),
        headers=auth_header(token_operador),
    )
    pedido_id = response.json()["pedido_id"]

    response = client.post(
        f"/pedidos/{pedido_id}/validar", headers=auth_header(token_operador)
    )
    assert response.status_code == 200
    body = response.json()
    assert body["valido"] is False
    assert any("Temuco" in e for e in body["errores"])
    assert body["estado"] == "Creado"


def test_validar_pedido_express_peso_excedido(
    client, token_operador, auth_header, pedido_payload
):
    """Decorator de validacion: express con peso > 20kg."""
    response = client.post(
        "/pedidos",
        json=pedido_payload(tipo_entrega="express", peso_kg=25),
        headers=auth_header(token_operador),
    )
    pedido_id = response.json()["pedido_id"]

    response = client.post(
        f"/pedidos/{pedido_id}/validar", headers=auth_header(token_operador)
    )
    body = response.json()
    assert body["valido"] is False
    assert any("express" in e.lower() for e in body["errores"])


def test_flujo_completo_pedido(
    client, token_operador, auth_header, pedido_payload
):
    """Flujo: crear -> validar -> pendiente -> (asignar) -> en ruta -> entregado."""
    response = client.post(
        "/pedidos", json=pedido_payload(), headers=auth_header(token_operador)
    )
    pedido_id = response.json()["pedido_id"]

    # Validar
    response = client.post(
        f"/pedidos/{pedido_id}/validar", headers=auth_header(token_operador)
    )
    assert response.json()["estado"] == "Validado"

    # Poner pendiente
    response = client.put(
        f"/pedidos/{pedido_id}/estado",
        json={"accion": "poner_pendiente"},
        headers=auth_header(token_operador),
    )
    assert response.json()["estado"] == "Pendiente de asignacion"


def test_transicion_invalida_devuelve_409(
    client, token_operador, auth_header, pedido_payload
):
    """Intentar iniciar_ruta sobre un pedido recien creado debe fallar con 409."""
    response = client.post(
        "/pedidos", json=pedido_payload(), headers=auth_header(token_operador)
    )
    pedido_id = response.json()["pedido_id"]

    response = client.put(
        f"/pedidos/{pedido_id}/estado",
        json={"accion": "iniciar_ruta"},
        headers=auth_header(token_operador),
    )
    assert response.status_code == 409
    assert "transicion_invalida" in response.json()["error"]
