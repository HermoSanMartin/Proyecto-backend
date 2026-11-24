# Seguimiento de las entregas I y II

La matriz inicial del equipo, incorporada en [`4fde057`](https://github.com/HermoSanMartin/Proyecto-backend/commit/4fde057), registra dos asuntos generales. El material disponible para esta revisión contiene la pauta final y la matriz del equipo. La atribución a una entrega concreta y la resolución de los comentarios del docente quedan pendientes de cotejar con las devoluciones originales.

## Evidencia de los asuntos registrados por el equipo

| ID y asunto original | Implementación y revisión trazable | Comprobación reproducible | Estado |
| --- | --- | --- | --- |
| **R-01. Dominio base y persistencia.** Cuatro entidades, relaciones y reglas de negocio. | La [migración inicial](../migrations/versions/d66bea12c491_crea_tablas_iniciales.py) define artistas, obras, exposiciones y solicitudes. El [servicio de préstamos](../app/application/services/solicitud_service.py) gestiona la aprobación y la disponibilidad. Los [diagramas](diagramas.md) identifican las relaciones. Migración en [`879aa6a`](https://github.com/HermoSanMartin/Proyecto-backend/commit/879aa6a). | En la [suite de integración](../tests/integration/test_repositorios_y_auth.py), `test_integracion_solicitud_prestamo_aprobacion_y_disponibilidad` comprueba el cambio de estado y la disponibilidad de la obra en la base de prueba migrada. | Caso técnico comprobado. Pendiente la correspondencia con la devolución original. |
| **R-02. Errores uniformes y consulta de obras.** Filtro, orden y paginación. | El [router de obras](../app/presentation/routers/obra.py) admite estilo, campo de orden, dirección, página y límite. Los [manejadores HTTP](../app/presentation/error_handlers.py) forman las respuestas de error. La suite externa de [`4c3f91a`](https://github.com/HermoSanMartin/Proyecto-backend/commit/4c3f91a) prueba el contrato HTTP. | `test_integracion_obras_filtro_orden_y_paginacion` verifica la consulta. En la [suite E2E](../tests/e2e/test_flujos_api.py), `test_e2e_escenario_3_permisos_diferenciados_401_vs_403` verifica los códigos HTTP y los identificadores de error de la API. | Casos técnicos comprobados. Pendiente la correspondencia con la devolución original. |

Para repetir estas comprobaciones desde la raíz, sigue la [preparación del entorno de pruebas](../README.md) y ejecuta:

```sh
python -m pytest tests/integration -k "aprobacion_y_disponibilidad or filtro_orden_y_paginacion"
python -m pytest tests/e2e -k permisos_diferenciados
```

## Contraste pendiente con el docente

Para cada entrega, incorporar la devolución original o su referencia, registrar cada observación por separado y asociarla con el archivo, el commit o PR y la prueba que la comprueba. Si alguna observación queda parcialmente resuelta, identificar la parte pendiente. La fuente permite distinguir entre una entrega sin observaciones correctivas y una devolución que aún falta recopilar.
