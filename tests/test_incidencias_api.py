"""Tests del caso de uso: Gestion de Incidencias."""


def test_registrar_incidencia(client, token_operador, auth_header, pedido_payload):
    # Crear pedido primero
    response = client.post(
        "/pedidos", json=pedido_payload(), headers=auth_header(token_operador)
    )
    pid = response.json()["pedido_id"]

    # Registrar incidencia
    response = client.post(
        "/incidencias",
        json={
            "pedido_id": pid,
            "tipo": "producto_no_recibido",
            "descripcion": "Cliente reporta que no llego el paquete",
        },
        headers=auth_header(token_operador),
    )
    assert response.status_code == 201
    body = response.json()
    assert body["estado"] == "Abierta"
    assert body["tipo"] == "producto_no_recibido"


def test_registrar_incidencia_pedido_inexistente(
    client, token_operador, auth_header
):
    response = client.post(
        "/incidencias",
        json={
            "pedido_id": "no-existe",
            "tipo": "retraso",
            "descripcion": "x",
        },
        headers=auth_header(token_operador),
    )
    assert response.status_code == 404


def test_flujo_incidencia_completo(
    client, token_operador, auth_header, pedido_payload
):
    response = client.post(
        "/pedidos", json=pedido_payload(), headers=auth_header(token_operador)
    )
    pid = response.json()["pedido_id"]

    response = client.post(
        "/incidencias",
        json={
            "pedido_id": pid,
            "tipo": "producto_danado",
            "descripcion": "Llego dañado",
        },
        headers=auth_header(token_operador),
    )
    iid = response.json()["incidencia_id"]

    response = client.post(
        f"/incidencias/{iid}/analizar", headers=auth_header(token_operador)
    )
    assert response.json()["estado"] == "En analisis"

    response = client.post(
        f"/incidencias/{iid}/resolver-iniciar",
        headers=auth_header(token_operador),
    )
    assert response.json()["estado"] == "En resolucion"

    response = client.put(
        f"/incidencias/{iid}/resolver",
        json={
            "descripcion_resolucion": "Se confirmo el dano y se compensara",
            "accion_tomada": "Reembolso al cliente",
            "requiere_reenvio": False,
        },
        headers=auth_header(token_operador),
    )
    assert response.json()["estado"] == "Resuelta"
    assert response.json()["resolucion"] is not None


def test_resolver_incidencia_sin_haber_iniciado_resolucion_falla(
    client, token_operador, auth_header, pedido_payload
):
    response = client.post(
        "/pedidos", json=pedido_payload(), headers=auth_header(token_operador)
    )
    pid = response.json()["pedido_id"]

    response = client.post(
        "/incidencias",
        json={"pedido_id": pid, "tipo": "retraso", "descripcion": "x"},
        headers=auth_header(token_operador),
    )
    iid = response.json()["incidencia_id"]

    # Intentar resolver sin pasar por En analisis -> En resolucion
    response = client.put(
        f"/incidencias/{iid}/resolver",
        json={
            "descripcion_resolucion": "x",
            "accion_tomada": "x",
            "requiere_reenvio": False,
        },
        headers=auth_header(token_operador),
    )
    assert response.status_code == 409
