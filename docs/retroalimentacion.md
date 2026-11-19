# Registro de Retroalimentación y Cumplimiento (Entregas I y II)

Este documento registra las observaciones recibidas en las entregas anteriores y verifica el cumplimiento íntegro de los requisitos base del proyecto antes de integrar el módulo de seguridad y despliegue final.

## Matriz de observaciones y mejoras

| ID / Observación recibida | Cambio y evidencia | Comprobación / estado |
| :--- | :--- | :--- |
| **R-01** Verificación de dominio base y persistencia de Entregas I y II | Mantenimiento de las 4 entidades (`Artista`, `ObraDeArte`, `Exposicion`, `SolicitudPrestamo`), relaciones 1:N, reglas de negocio y validaciones en `app/domain/` y `app/application/services/`. | Verificado mediante migración inicial (`d66bea12c491`) y pruebas automatizadas. **Estado:** Resuelta. |
| **R-02** Manejo de errores uniformes y consulta paginada/filtrada | Estandarización de respuestas de error en `app/presentation/error_handlers.py` y consulta con filtro, orden y paginación en `GET /api/v1/obras`. | Comprobado con suite de integración y E2E. **Estado:** Resuelta. |

## Verificación de continuidad (Sección 5.1)

- **Entidades y relaciones:** `Artista` (1:N `ObraDeArte`), `Exposicion` y `SolicitudPrestamo` implementadas con persistencia en PostgreSQL.
- **Endpoints de negocio:** Más de 15 endpoints activos bajo `/api/v1/`, CRUD completo en obras y listado con filtro, orden y paginación.
- **Arquitectura en capas:** Separación estricta entre `presentation`, `application`, `domain` e `infrastructure`.
