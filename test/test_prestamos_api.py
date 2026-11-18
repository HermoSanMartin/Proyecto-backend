def test_obtener_prestamos_endpoint(client):
    """Verifica la respuesta al consultar el historial de prestamos de obras."""
    response = client.get("/prestamos")
    assert response.status_code in [200, 404]


def test_solicitar_prestamo_datos_invalidos(client):
    """Verifica que una solicitud de prestamo sin datos retorne error de validacion."""
    response = client.post("/prestamos", json={})
    assert response.status_code in [400, 422]