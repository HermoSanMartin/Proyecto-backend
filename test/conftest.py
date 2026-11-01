import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Cliente de prueba para simular peticiones HTTP a la API de FastAPI."""
    return TestClient(app)