# Defensa de la galería

## Guion de 10 minutos

| Tiempo | Diapositiva | Acción o explicación |
| --- | --- | --- |
| 0:00–0:40 | Galería de arte | Grupo 7   ·   Desarrollo de Backend   ·   UCT |
| 0:40–1:30 | Una solicitud conecta tres decisiones | La aprobación cambia dos registros: el estado de la solicitud y la disponibilidad de la obra. PostgreSQL confirma ambos en una transacción. |
| 1:30–2:25 | Dos correcciones que se pueden probar | Un JSON inválido devuelve 422 con un error tipado. El contrato OpenAPI y el cuerpo de la respuesta coinciden. |
| 2:25–3:25 | El recorrido de una petición | El DTO valida los campos. La dependencia comprueba el JWT y el rol. ArtistaService comprueba el correo. El repositorio guarda el artista y devuelve su ID. |
| 3:25–5:10 | Una ruta, tres resultados | En Postman, autenticar al administrador y crear un artista. Mostrar el estado HTTP y el ID generado. Ocultar las credenciales. |
| 5:10–7:15 | Recuperar una cuenta | Mailpit recibe el JWT de recuperación. El cambio invalida las sesiones anteriores. Repetir la solicitud antes de 60 segundos mantiene una respuesta genérica. |
| 7:15–8:30 | Qué comprueban las pruebas | En la revisión local con CSRF pasaron 22 pruebas con 92,21 % de cobertura. Las E2E usan Uvicorn por HTTP, una base migrada y correo SMTP real. |
| 8:30–10:00 | Del commit a la entrega | Para acreditar Kuberos faltan la URL HTTPS y el SHA servido. La comprobación final debe mostrar salud y el mismo registro después de reiniciar la API. |

Antes de ensayar, abrir Postman, el buzón de pruebas, los [diagramas](diagramas.md), la [matriz de correcciones](retroalimentacion.md) y la ejecución de CI para la revisión que se presenta. Para la exposición institucional, sustituir la demostración local por la URL y la evidencia reales del [registro de despliegue](despliegue.md). Cualquier integrante debe poder realizar todo el recorrido y repetir una prueba.

## Problemática P1–P7 reconstruida desde la implementación

Esta versión describe el alcance observable del backend. El cotejo literal con las entregas I y II requiere los documentos originales del equipo.

| Punto | Qué se puede demostrar |
| --- | --- |
| P1 · Situación | La galería necesita coordinar qué obra pertenece a cada artista y si está disponible para una exposición. |
| P2 · Actores | El visitante consulta el catálogo, el usuario autenticado gestiona solicitudes según sus permisos y el administrador registra artistas y resuelve préstamos. |
| P3 · Consecuencias | Reservar una obra sin confirmar la solicitud deja el catálogo y los préstamos en estados incompatibles. |
| P4 · Información | Artistas, obras, exposiciones, fechas, duración y estado de solicitudes; usuarios y sesiones para autorizar cambios. |
| P5 · Acciones | Consultar y filtrar obras, gestionar el catálogo, solicitar un préstamo y aprobarlo o rechazarlo. |
| P6 · Exclusiones observables | El contrato de esta API cubre la gestión de galería. Pagos, ventas y transporte físico quedan fuera del contrato publicado. |
| P7 · Aceptación | Una obra aprobada queda reservada; una aprobación fallida conserva su disponibilidad. Crear un artista devuelve 401 sin credencial, 403 con rol visitante y 201 con rol administrador. |

## Participación y cierre

En el historial de main aparecen los PR [#6 de Fabian](https://github.com/HermoSanMartin/Proyecto-backend/pull/6), [#8 de HermoSanMartin](https://github.com/HermoSanMartin/Proyecto-backend/pull/8) y [#9 de Felipe](https://github.com/HermoSanMartin/Proyecto-backend/pull/9). Son referencias del proyecto acumulado. Para acreditar esta entrega se debe acordar el intervalo evaluado y vincular por persona cinco cambios significativos y un PR integrado en ese tramo. El reparto de coordinación, dominio y datos, API, calidad y documentación debe confirmarlo el grupo.

En la preparación se utilizó Codex para apoyar la implementación, pruebas y documentación. El equipo debe revisar el material y explicar las decisiones que presente.
