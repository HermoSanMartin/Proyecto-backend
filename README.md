# API de gestión de galerías de arte

La API permite registrar artistas y obras, organizar exposiciones y gestionar solicitudes de préstamo. Los visitantes pueden consultar el catálogo. El backend verifica la identidad y el rol para las operaciones protegidas. El proyecto usa FastAPI, SQLAlchemy, PostgreSQL 16 y migraciones Alembic.

## Levantar la API desde una copia limpia

Se necesita Git y Docker con el complemento Compose y soporte para contenedores Linux. Para ejecutar pytest en el equipo se necesita además Python 3.13. Los comandos siguientes usan PowerShell desde la raíz del clon. Para reproducir una revisión concreta, selecciona la rama o el commit de entrega antes de construir.

```powershell
git clone https://github.com/HermoSanMartin/Proyecto-backend.git
cd Proyecto-backend
Copy-Item .env.example .env
```

Edita el archivo local `.env` antes del primer arranque.

| Variables | Configuración inicial |
| --- | --- |
| `POSTGRES_USER`, `POSTGRES_DB`, `POSTGRES_PASSWORD` | Elige una contraseña privada. Usa caracteres seguros para URL, ya que Compose forma la conexión con estos valores. Si ejecutas herramientas desde el host, actualiza también `DATABASE_URL` con las mismas credenciales y el host `localhost`. |
| `JWT_SECRET_KEY` | Genera un secreto aleatorio de al menos 32 bytes. Con Python puedes obtener uno con `py -3.13 -c "import secrets; print(secrets.token_urlsafe(32))"`. Guárdalo únicamente en la configuración privada. |
| `PGADMIN_EMAIL`, `PGADMIN_PASSWORD` | Define el acceso local a pgAdmin. Usa un correo aceptado por pgAdmin, por ejemplo `operador@example.com`, y una contraseña propia. |
| `DEMO_ADMIN_PASSWORD`, `DEMO_VISITANTE_PASSWORD` | Para la demostración configura dos claves distintas, de al menos 12 caracteres, con mayúscula, minúscula y número. El seeder crea respectivamente `admin@galeria.cl` y `visitante@galeria.cl`. Cada variable vacía omite la creación de esa cuenta. Una cuenta existente conserva su contraseña. |
| Correo y transporte | Compose conecta la API a `mailpit:1025`. Para desarrollo local HTTP, la plantilla usa `COOKIE_SECURE=false`. En el despliegue HTTPS configura cookies seguras y los orígenes CORS autorizados. |

```powershell
docker compose config --quiet
docker compose up -d --build
docker compose ps
Invoke-RestMethod http://localhost:8000/api/v1/salud
```

Cuando la API esté lista, salud devuelve `estado = ok`. En el primer arranque puede tardar mientras PostgreSQL inicializa el volumen. Consulta `docker compose logs --tail=80 api db` si todavía no responde.

| Servicio | Acceso local | Qué comprobar |
| --- | --- | --- |
| FastAPI | [Swagger UI](http://localhost:8000/docs) · [OpenAPI JSON](http://localhost:8000/openapi.json) | DTO de entrada y salida, rutas de autenticación y respuestas de las operaciones de negocio. |
| PostgreSQL | `localhost:5432` | Datos de la galería en el volumen `galeria_datos`. |
| pgAdmin | [Consola](http://localhost:5050) | Para registrar PostgreSQL desde pgAdmin, usa el host `db`, puerto `5432` y los valores `POSTGRES_*` del entorno. |
| Mailpit | [Buzón](http://localhost:8025) | Recibe los mensajes de recuperación enviados por la API. Usa este buzón en un entorno restringido. |

La API ejecuta `alembic upgrade head` y `python -m app.infrastructure.seeders.seed` antes de iniciar Uvicorn. Para consultar la revisión aplicada o repetir la carga de ejemplo:

```powershell
docker compose exec api alembic current
docker compose exec api alembic upgrade head
docker compose exec api python -m app.infrastructure.seeders.seed
```

Para detener el conjunto y conservar el volumen de PostgreSQL, usa `docker compose down`. Para arrancar de nuevo, usa `docker compose up -d`.

## Demostración y recorrido de una petición

Importa [la colección de Postman](tests_manual/Galeria.postman_collection.json). Selecciona un entorno de Postman y define como valores privados locales `visitante_password` y `admin_password`. Ejecuta las cinco peticiones en orden, manualmente o desde el Runner. Espera 401 en el alta sin token, 200 en el login de visitante, 403 en su intento de alta, 200 en el login de administrador y 201 en el alta final. La última respuesta contiene el ID del artista creado.

El JWT de acceso caduca por defecto a los 15 minutos. El refresh es opaco, se guarda como hash y rota al renovar. La reutilización revoca la familia. Logout revoca la renovación y el access ya emitido puede durar hasta su expiración. Para recuperación, el backend envía un JWT de propósito exclusivo por correo. Restablecer la contraseña consume el permiso e invalida sesiones previas.

La API admite un correo de recuperación por cuenta cada 60 segundos. Repetir la solicitud devuelve la misma respuesta genérica y permite seguir iniciando sesión.

Los [diagramas de arquitectura y datos](docs/diagramas.md) siguen la creación de un artista hasta PostgreSQL. La [matriz de retroalimentación](docs/retroalimentacion.md) identifica las pruebas que respaldan los requisitos de continuidad.

## Preparar el entorno de pruebas en Windows

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\Activate.ps1
ruff check app tests
ruff format --check app tests
```

Si la consola restringe la activación, usa directamente `.\.venv\Scripts\python.exe` en lugar de `python` y `.\.venv\Scripts\ruff.exe` en lugar de `ruff` en los comandos de pruebas y calidad.

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

## CI y despliegue

[El workflow de GitHub Actions](.github/workflows/ci.yml) ejecuta Ruff y pytest antes de construir la imagen identificada con el SHA del commit. Los reportes se descargan en **Actions → ejecución del commit → Artifacts → reportes-pruebas**. Para comprobarlos localmente, abre `reportes/pruebas.xml` y `reportes/cobertura.xml` después del comando anterior.

El [procedimiento de CI/CD y operación en Kuberos UCT](docs/despliegue.md) vincula las ejecuciones verificadas y describe la promoción, el bloqueo de fallos, las comprobaciones de salud y persistencia y la reversión. Incluye un registro de evidencias pendientes.

### Cookies, HTTPS y demostración de recuperación

La cookie de renovación usa `HttpOnly`, se limita a `/api/v1/auth` y emplea `SameSite=Lax` para el cliente web previsto en el mismo sitio. En HTTPS establece `COOKIE_SECURE=true`. Cuando el navegador usa esa cookie para renovar o cerrar sesión, debe enviar `X-CSRF-Protection: 1`. Un formulario HTML de otro sitio no puede añadir esa cabecera. Una solicitud de JavaScript entre orígenes requiere que la comprobación previa de CORS autorice el origen. Configura `CORS_ORIGINS` con los orígenes exactos de los clientes de confianza. El cliente que envía explícitamente el refresh en el JSON sigue usando ese flujo.

Para la defensa, registra una cuenta desechable con `POST /api/v1/auth/registro` y abre una sesión. Solicita el correo con `POST /api/v1/auth/solicitar-recuperacion`, abre el mensaje en Mailpit y toma el parámetro `token` del enlace. Desde Postman envía `POST /api/v1/auth/restablecer-password` con los campos `token` y `nueva_password`: el primer envío devuelve 200 y el segundo, con el mismo token, devuelve 401. Comprueba que la sesión anterior ya no permite consultar `GET /api/v1/auth/me` y que sólo la nueva contraseña permite iniciar sesión. Muestra los estados HTTP y oculta los secretos. El ensayo automatizado se ejecuta con `python -m pytest tests/e2e -k recuperacion_uso_unico`.

El [guion de defensa](docs/defensa.md) reúne el ensayo de diez minutos, los puntos P1–P7 y las evidencias de participación.
