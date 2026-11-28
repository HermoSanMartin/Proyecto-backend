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
| 8:30–10:00 | Del commit a la entrega | Abrir la [salud institucional](https://galeria-arte-g7.inf.uct.cl/api/v1/salud) y la [entrega v1.0](https://github.com/HermoSanMartin/Proyecto-backend/releases/tag/v1.0). Mostrar el SHA 52823c3 y explicar cómo el artista con ID 3 conservó su nombre tras el reemplazo del pod en v1.0. |

Antes de ensayar, abrir Postman, el buzón de pruebas, los [diagramas](diagramas.md), la [matriz de correcciones](retroalimentacion.md) y la ejecución de CI para la revisión que se presenta. Para la exposición institucional, usar la [API desplegada](https://galeria-arte-g7.inf.uct.cl/docs) y el [registro de la entrega](https://github.com/HermoSanMartin/Proyecto-backend/releases/tag/v1.0). La recuperación se verificó en el clúster leyendo el mensaje desde el buzón privado de Mailpit. El primer restablecimiento devolvió 200 y el segundo uso del mismo enlace devolvió 401. Cualquier integrante debe poder realizar todo el recorrido y repetir una prueba.

## Problemática P1–P7 reconstruida desde la implementación

Esta síntesis se puede defender con el historial del proyecto. El 29 de octubre se incorporaron las entidades [artista](https://github.com/HermoSanMartin/Proyecto-backend/commit/004523a), [obra](https://github.com/HermoSanMartin/Proyecto-backend/commit/8a789f5), [exposición](https://github.com/HermoSanMartin/Proyecto-backend/commit/fe3fc9e) y [solicitud de préstamo](https://github.com/HermoSanMartin/Proyecto-backend/commit/0f52d67). Las [reglas de préstamo](https://github.com/HermoSanMartin/Proyecto-backend/commit/1f3f406) permiten reconstruir el problema operativo. Los criterios finales se verifican con las [pruebas de integración](https://github.com/HermoSanMartin/Proyecto-backend/blob/v1.0/tests/integration/test_repositorios_y_auth.py) y las [pruebas E2E](https://github.com/HermoSanMartin/Proyecto-backend/blob/v1.0/tests/e2e/test_flujos_api.py).

| Punto | Qué se puede demostrar |
| --- | --- |
| P1 · Situación | La galería necesita coordinar qué obra pertenece a cada artista y si está disponible para una exposición. |
| P2 · Actores | El visitante consulta el catálogo, el usuario autenticado gestiona solicitudes según sus permisos y el administrador registra artistas y resuelve préstamos. |
| P3 · Consecuencias | Reservar una obra sin confirmar la solicitud deja el catálogo y los préstamos en estados incompatibles. |
| P4 · Información | Artistas, obras, exposiciones, fechas, duración y estado de solicitudes; usuarios y sesiones para autorizar cambios. |
| P5 · Acciones | Consultar y filtrar obras, gestionar el catálogo, solicitar un préstamo y aprobarlo o rechazarlo. |
| P6 · Exclusiones observables | El contrato de esta API cubre la gestión de galería. Pagos, ventas y transporte físico quedan fuera del contrato publicado. |
| P7 · Aceptación | Una obra aprobada queda reservada; una aprobación fallida conserva su disponibilidad. Crear un artista devuelve 401 sin credencial, 403 con rol visitante y 201 con rol administrador. |

## Contraste de P1–P7 con los antecedentes

El README de la evaluación E01 identifica el proyecto como una galería de arte de lujo con coleccionistas y ventas. La revisión integrada del PR #8 ya implementaba exposiciones y préstamos. La comparación recoge lo que cada repositorio documenta. [README de E01](https://github.com/HermoSanMartin/CRUD-BACKEND/blob/80e16598e052dd0e3607019a9d1c28760c56bab7/README.md) · [Código anterior al tramo de seguridad](https://github.com/HermoSanMartin/Proyecto-backend/tree/6da7900) · [Versión evaluada](https://github.com/HermoSanMartin/Proyecto-backend/tree/v1.0)

| Punto | Continuidad o cambio comprobable |
| --- | --- |
| P1 · Situación | Se conserva el catálogo artístico. E01 describe la gestión de ventas de alto valor. El historial del proyecto actual ya incluye préstamos y exposiciones desde el 29 de octubre. El motivo de la diferencia entre repositorios queda sin documentar. |
| P2 · Actores | E01 identifica al coleccionista y al artista. En v1.0 el artista es una entidad del catálogo. Las solicitudes requieren autenticación y su aprobación requiere rol administrador. |
| P3 · Consecuencias | El README de E01 no detalla las consecuencias de un fallo. En préstamos, una aprobación parcial podría reservar una obra sin confirmar la solicitud. La prueba de rollback comprueba este riesgo. |
| P4 · Información | Obras y artistas aparecen en ambos proyectos. Coleccionistas y transacciones de venta figuran en E01. Exposiciones y solicitudes ya existen en el PR #8. v1.0 añade usuarios y sesiones. |
| P5 · Acciones | E01 describe gestión de catálogo y ventas. El servicio anterior al tramo final ya permitía crear, aprobar y rechazar préstamos. v1.0 restringe esas operaciones según el rol. |
| P6 · Exclusiones | Las ventas eran parte explícita de E01 y están fuera del contrato de v1.0. La exclusión actual no puede presentarse como una exclusión original. |
| P7 · Aceptación | El servicio anterior comprobaba disponibilidad y cupo. v1.0 prueba además permisos, recuperación de un solo uso y rollback. |

El informe docente g7.pdf evalúa Git, Docker y ORM en el taller II. Sirve para la matriz de correcciones. La formulación P1–P7 de esta guía es una reconstrucción técnica basada en las revisiones citadas.

## Participación en la entrega

Para hacer reproducible el recuento se tomó como base el PR #8, integrado el 18 de noviembre, y como cierre el commit de v1.0. **El comienzo del intervalo es una hipótesis de trabajo** que el grupo debe contrastar con la fecha de cierre oficial de la Entrega II. Se contaron commits integrados con un único padre y se comprobó por separado la autoría de los PR. [Comparación del tramo](https://github.com/HermoSanMartin/Proyecto-backend/compare/6da7900...52823c3)

| Cuenta | Evidencia de autoría en el tramo | PR y evidencia anterior |
| --- | --- | --- |
| felipelienlaf | 25 commits. Cinco cambios verificables son la [configuración privada de credenciales](https://github.com/HermoSanMartin/Proyecto-backend/commit/711c17d), las [pruebas HTTP y Mailpit](https://github.com/HermoSanMartin/Proyecto-backend/commit/4c3f91a), la [aprobación transaccional](https://github.com/HermoSanMartin/Proyecto-backend/commit/e21c9d4), la [protección CSRF](https://github.com/HermoSanMartin/Proyecto-backend/commit/a53d634) y la [publicación en GHCR](https://github.com/HermoSanMartin/Proyecto-backend/commit/98f6228). | Autor de los PR integrados [#9](https://github.com/HermoSanMartin/Proyecto-backend/pull/9), [#10](https://github.com/HermoSanMartin/Proyecto-backend/pull/10), [#11](https://github.com/HermoSanMartin/Proyecto-backend/pull/11) y [#12](https://github.com/HermoSanMartin/Proyecto-backend/pull/12). |
| HermoSanMartin | 0 commits de autoría en el intervalo elegido. | El [PR #8](https://github.com/HermoSanMartin/Proyecto-backend/pull/8) acredita trabajo previo en contenedores. Es el límite inicial de la comparación. |
| F4b1anxx | 0 commits de autoría en el intervalo elegido. | El [PR #6](https://github.com/HermoSanMartin/Proyecto-backend/pull/6) acredita trabajo previo en pruebas, reportes y datos iniciales. |

En las páginas de los cuatro PR del intervalo (#9–#12), GitHub muestra un participante y ninguna revisión registrada. En los cuatro casos figura felipelienlaf como autor de la fusión. Estos PR acreditan la participación de Felipe. Para atribuir participación a otra persona en este tramo se necesita una evidencia adicional. Los enlaces de cada PR están en la fila de Felipe.

Las filas identifican cuentas observadas en el historial integrado. Para cerrar la sección hacen falta la nómina del grupo, la fecha oficial de corte y, cuando corresponda, enlaces a aportes o revisiones de PR que el recuento de autoría no refleje. El reparto de las cinco áreas debe confirmarse con quienes realizaron el trabajo.

## Reparto de la validación de v1.0

| Responsable | Trabajo asignado | Evidencia para el grupo | Estado |
| --- | --- | --- | --- |
| Codex, a solicitud de Felipe | Calidad y permisos. Ejecutar los tres casos de alta de artista. | SHA desplegado, hora, rol, estado HTTP observado e ID del artista creado. | Verificado el 27 de noviembre de 2026 |
| Sebastián (HermoSanMartin) | Dominio, datos y operación. Verificar la persistencia del artista después del reinicio. | SHA de la imagen, pods anterior y nuevo, salud, ID y nombre antes y después. | Verificado por Codex a solicitud de Felipe. Sebastián puede repetir el procedimiento. |
| Felipe (felipelienlaf) | Coordinación, documentación e integración. Revisar las evidencias y organizar el ensayo. | Enlaces a los PR de cada autor, revisión y resultado del ensayo. | Espera las evidencias |

### Permisos de alta de artista en producción

El 27 de noviembre de 2026, Codex ejecutó la prueba a solicitud de Felipe con HTTPX desde el pod `galeria-arte-g7-kuberoapp-web-7c5c64ffcc-fqwff`, contra la API en ejecución por loopback. Kubero mostraba la imagen con SHA `52823c3c3c14e9d4d9c4c445bb4c2e04a433390d`. Se envió el mismo cuerpo en los tres casos.

| Credencial | Login | Alta de artista |
| --- | --- | --- |
| Sin token | — | 401 Unauthorized |
| Usuario visitante | 200 OK | 403 Forbidden |
| Administrador | 200 OK | 201 Created |

La consulta posterior por ID devolvió 200. También se abrió el registro por HTTPS público y se comprobó el ID **3**, el nombre **Permisos G7 e1dd40a6** y el estado activo. Esta lectura sirve como referencia previa al reinicio. [Consultar artista en Kubero](https://galeria-arte-g7.inf.uct.cl/api/v1/artistas/3)

### Cómo repetir los tres casos en Postman

La colección de la revisión 6327339 se ejecutó completa con Newman 6.2.3 contra Uvicorn por HTTP en el equipo local, con SQLite temporal migrado por Alembic y las cuentas del seeder. En orden, devolvió 401, 200, 403, 200 y 201. Pasaron las seis aserciones. La prueba institucional descrita arriba se hizo con HTTPX.

Importa la [colección de Postman](../tests_manual/Galeria.postman_collection.json). La colección usa `http://127.0.0.1:8000` por defecto. Para probar Kubero, crea y selecciona un entorno de Postman con `base_url` igual a `https://galeria-arte-g7.inf.uct.cl` (sin barra final). Selecciona un entorno de Postman y define como valores privados locales `visitante_password` y `admin_password`. Ejecuta las cinco peticiones en orden, manualmente o desde el Runner. Espera 401 en el alta sin token, 200 en el login de visitante, 403 en su intento de alta, 200 en el login de administrador y 201 en el alta final. La última respuesta contiene el ID del artista creado. Guarda el ID y el nombre devueltos para la comprobación de persistencia.

### Persistencia del artista · Procedimiento para Sebastián

Codex ejecutó la comprobación a solicitud de Felipe el 27 de noviembre de 2026. En producción se usó **Acciones → Reiniciar** sobre la API. La imagen conservó el SHA `52823c3c3c14e9d4d9c4c445bb4c2e04a433390d`.

| Observación | Antes | Después |
| --- | --- | --- |
| Pod web listo | `galeria-arte-g7-kuberoapp-web-7c5c64ffcc-fqwff` | `galeria-arte-g7-kuberoapp-web-7f8cd99649-mwpw2` |
| Artista consultado por ID | 3 · Permisos G7 e1dd40a6 · activo | 3 · Permisos G7 e1dd40a6 · activo |

Cuando Kubero mostró únicamente el nuevo pod y «1 de 1 listos», ambos GET por HTTPS devolvieron 200. La ruta de salud respondió `{"estado":"ok"}`. [Consultar artista](https://galeria-arte-g7.inf.uct.cl/api/v1/artistas/3) · [Consultar salud](https://galeria-arte-g7.inf.uct.cl/api/v1/salud)

Para repetir la prueba durante la defensa:

1. En el [panel de producción](https://kubero.inf.uct.cl/pipeline/galeria-arte-g7/apps), registra el SHA de la API y el nombre del pod web. Consulta `GET /api/v1/artistas/{id}` con el ID 3 y guarda el estado HTTP, ID y nombre.
2. Reinicia únicamente la aplicación `galeria-arte-g7`. Espera a que salga el pod anterior y el nuevo esté listo. Registra el nuevo pod y la respuesta de [salud](https://galeria-arte-g7.inf.uct.cl/api/v1/salud).
3. Repite la consulta por ID. Registra si el estado es 200 y si el ID y el nombre coinciden. Si difieren, documenta la diferencia. Conserva el artista para el ensayo.

### Felipe · Revisión y ensayo

Cada responsable sube sus resultados desde su rama y abre un PR con su cuenta. Felipe verifica que las dos pruebas usan el mismo artista y la misma revisión desplegada. Fabián y Sebastián revisan los pasos del otro y los ensayan para la defensa. Al terminar, Felipe incorpora los enlaces y actualiza los estados de la tabla según los resultados reales.

En la preparación se utilizó Codex para apoyar la implementación, pruebas y documentación. El equipo debe revisar el material y explicar las decisiones que presente.
