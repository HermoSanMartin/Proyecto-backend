def test_obtener_exposiciones_endpoint(client):
    """Verifica la respuesta al consultar la lista general de exposiciones."""
    response = client.get("/exposiciones")
    assert response.status_code in [200, 404]


def test_obtener_exposicion_inexistente(client):
    """Verifica que buscar una exposicion inexistente retorne 404 u otro error controlado."""
    response = client.get("/exposiciones/999999")
    assert response.status_code in [404, 422]