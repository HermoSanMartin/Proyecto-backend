# Seguimiento de observaciones docentes y continuidad del proyecto

## Fuentes y alcance

- **Primera devolución aportada por el equipo.** Transcripción con tres criterios (Git, estandarización y API), 5/9 puntos y nota 3,8. El texto recibido no identifica el título formal de la actividad.
- **Taller Evaluado II.** Revisión del Grupo 7, Universidad Católica de Temuco, ICINF1108, archivo `g7.pdf` proporcionado por el equipo. Se evaluó `HermoSanMartin/TALLER-2` y se asignaron 2/9 puntos y nota 2,1.

La siguiente comparación identifica el comportamiento de **Proyecto-backend** frente a cada comentario. Las observaciones y calificaciones corresponden a las actividades originales. Los estados describen la evidencia disponible en el repositorio actual.

| Fuente y observación docente | Evidencia actual y comprobación | Estado |
| --- | --- | --- |
| Primera · **Git (2 puntos).** El trabajo de la rama `felipe` quedó fuera de la principal y `FABIAN-NEIRA` permaneció en la base. | En el historial de la rama principal del proyecto actual aparecen el [PR #6 de Fabian](https://github.com/HermoSanMartin/Proyecto-backend/pull/6) y el [PR #9 de Felipe](https://github.com/HermoSanMartin/Proyecto-backend/pull/9). Se comprueba con `git log main --merges --oneline`. | **Parcial para la entrega final.** Hay aportes integrados de ambos. Falta comprobar la integración de la revisión definitiva y los aportes de cada integrante al cerrar la entrega. |
| Primera · **Estandarización (1 punto).** El constructor de respuestas devolvía un diccionario y faltaba un tipo compartido. | Los éxitos tienen DTO por recurso, como [ArtistaRespuesta](../app/presentation/schemas/artista_schema.py). El [manejador común](../app/presentation/error_handlers.py) construye el cuerpo de error con un diccionario. | **Pendiente respecto al comentario original.** Hay esquemas por recurso y una estructura de error uniforme, pero falta el tipo de respuesta compartido solicitado en el taller. |
| Primera · **API (2 puntos).** Los errores de validación 422 quedaban fuera del formato empleado para otros errores. | [Manejador de validación](../app/presentation/error_handlers.py), registrado en [main.py](../app/main.py), revisión `253fe9a`. Se comprobó `POST /api/v1/auth/login` con JSON `{}`: devolvió HTTP 422, `error.code = VALIDATION_ERROR` y detalles para los campos email y password. | **Comprobada para 422.** Este resultado es independiente del tipo compartido de la fila anterior. |
| Taller II · **Git (1 punto).** La rama principal del taller conservó commits directos y dejó fuera los PR fusionados. | En la copia local de `main`, `git log main --merges --oneline` incluye, entre otros, los PR #6, #7, #8 y #9. | **Flujo integrado comprobado en el historial actual.** Verificar el SHA final en main y el tag de entrega después de fusionar los cambios pendientes. |
| Taller II · **Docker (1 punto).** La API reiniciaba por apuntar a `main:app`; el ejemplo de entorno estaba vacío. | [Dockerfile](../Dockerfile) y [Compose](../docker-compose.yml) arrancan `uvicorn app.main:app`. La [plantilla](../.env.example) contiene las variables de BD, JWT, correo y cuentas demo. El [README](../README.md) documenta el arranque y la comprobación de salud. Commits `8ead3b7` y `711c17d`. | **Ambos defectos corregidos en los archivos.** Compose validó la configuración desde una copia limpia. El arranque completo desde cero queda pendiente de repetir con acceso al motor Docker. |
| Taller II · **ORM y transacciones (0 puntos).** Repositorios en memoria, sin ORM, driver, revisiones ni transacciones. | [Dependencias](../requirements.txt) con SQLAlchemy y psycopg, [modelos](../app/infrastructure/models/), [repositorios](../app/infrastructure/repositories/) y [dos revisiones Alembic](../migrations/versions/). La prueba de aprobación y disponibilidad pasó sobre una base migrada. En [aprobar](../app/application/services/solicitud_service.py) se actualiza la obra y luego la solicitud; cada repositorio confirma su propia escritura. | **Parcial.** Hay persistencia, migraciones y commits a la base. Falta una transacción única para que, si falla la segunda escritura, también se revierta la primera. |

## Evidencia de los asuntos registrados por el equipo

| ID y asunto original | Implementación y revisión trazable | Comprobación reproducible | Estado |
| --- | --- | --- | --- |
| **R-01. Dominio base y persistencia.** Cuatro entidades, relaciones y reglas de negocio. | La [migración inicial](../migrations/versions/d66bea12c491_crea_tablas_iniciales.py) define artistas, obras, exposiciones y solicitudes. El [servicio de préstamos](../app/application/services/solicitud_service.py) gestiona la aprobación y la disponibilidad. Los [diagramas](diagramas.md) identifican las relaciones. Migración en [`879aa6a`](https://github.com/HermoSanMartin/Proyecto-backend/commit/879aa6a). | En la [suite de integración](../tests/integration/test_repositorios_y_auth.py), `test_integracion_solicitud_prestamo_aprobacion_y_disponibilidad` comprueba el cambio de estado y la disponibilidad de la obra en la base de prueba migrada. | Caso técnico comprobado. Seguimiento interno de continuidad. |
| **R-02. Errores uniformes y consulta de obras.** Filtro, orden y paginación. | El [router de obras](../app/presentation/routers/obra.py) admite estilo, campo de orden, dirección, página y límite. Los [manejadores HTTP](../app/presentation/error_handlers.py) forman las respuestas de error. La suite externa de [`4c3f91a`](https://github.com/HermoSanMartin/Proyecto-backend/commit/4c3f91a) prueba el contrato HTTP. | `test_integracion_obras_filtro_orden_y_paginacion` verifica la consulta. En la [suite E2E](../tests/e2e/test_flujos_api.py), `test_e2e_escenario_3_permisos_diferenciados_401_vs_403` verifica los códigos HTTP y los identificadores de error de la API. | Casos técnicos comprobados. Seguimiento interno de continuidad. |

Para repetir estas comprobaciones desde la raíz, sigue la [preparación del entorno de pruebas](../README.md) y ejecuta:

```sh
python -m pytest tests/integration -k "aprobacion_y_disponibilidad or filtro_orden_y_paginacion"
python -m pytest tests/e2e -k permisos_diferenciados
```
