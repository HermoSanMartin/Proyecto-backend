# API de gestión de galerías de arte

## Pruebas automatizadas

Desde la raíz del repositorio, con el entorno virtual activo y las dependencias de
`requirements.txt` instaladas, inicia Mailpit para ejecutar las E2E. El servicio
escucha en localhost por SMTP (1025) y HTTP (8025).

```sh
docker compose up -d mailpit
python -m pytest tests/unit
python -m pytest tests/integration
python -m pytest tests/e2e
```

Cada prueba de integración o E2E recibe una copia independiente de una base
SQLite temporal preparada con `alembic upgrade head`. La API de producción usa
PostgreSQL. El conjunto E2E levanta Uvicorn en otro proceso con un puerto local
asignado por el sistema y realiza solicitudes HTTP reales. La recuperación usa
un destinatario único por ejecución y lee el mensaje recibido por SMTP desde la
API de Mailpit. Los mensajes de prueba quedan en el buzón local.

Para ejecutar todos los niveles y generar reportes:

```sh
python -m pytest --junitxml=reportes/pruebas.xml --cov=app --cov-report=term-missing --cov-report=xml:reportes/cobertura.xml --cov-fail-under=85
```

JUnit identifica cada prueba por archivo y nivel. La cobertura incluye el proceso
de Uvicorn. GitHub Actions publica ambos XML en el artefacto `reportes-pruebas`.
