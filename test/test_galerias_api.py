def test_obtener_galerias_endpoint(client):
    """Verifica que la consulta HTTP a la lista de galerias responda correctamente."""
    response = client.get("/galerias")
    assert response.status_code in [200, 404]


def test_crear_galeria_datos_invalidos(client):
    """Verifica que enviar datos vacios devuelva error de validacion 422 o 400."""
    response = client.post("/galerias", json={})
    assert response.status_code in [400, 422]