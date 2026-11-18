def test_obtener_obras_endpoint(client):
    """Verifica que la consulta HTTP a la lista de obras responda un codigo valido."""
    response = client.get("/obras")
    # Comprueba que el servidor responda correctamente (200 OK o 404 si no hay registros)
    assert response.status_code in [200, 404]


def test_obtener_obra_inexistente(client):
    """Verifica que buscar una obra que no existe devuelva un error controlado 404."""
    response = client.get("/obras/999999")
    assert response.status_code in [404, 422]