# CI/CD y operación en Kuberos UCT

## Evidencias disponibles

| Revisión | Evidencia | Alcance |
| --- | --- | --- |
| `f92f4301986aecdd9e18122a530756d6a651511a` | [Actions, push en main](https://github.com/HermoSanMartin/Proyecto-backend/actions/runs/44630597930) | Control de calidad y construcción de imagen aprobados. |
| `69a1a876163d05a80733a000746e1f972631af25` | [Actions, pull request](https://github.com/HermoSanMartin/Proyecto-backend/actions/runs/45450075344) | Ejecución exitosa para la rama del PR. |

En la revisión de evidencias del 24 de noviembre de 2026, las cinco ejecuciones disponibles en Actions eran exitosas. El repositorio no tenía registros de despliegue en la API de GitHub. Kuberos puede gestionar despliegues por separado. Aún se desconoce la URL institucional y el SHA en ejecución. Los enlaces de la tabla corresponden a versiones anteriores al cambio de exportación de imagen.

## Demostrar que CI bloquea un fallo

Una vez integrado el workflow en la rama principal, abre **Actions → CI - Calidad, Pruebas y Contenedor → Run workflow**. Usa la misma revisión de main en ambas ejecuciones.

1. Activa `simular_fallo`. El runner añade un archivo temporal con un nombre indefinido. Ruff debe señalar `F821`, el trabajo de calidad debe fallar y el de construcción debe quedar omitido. Guarda el enlace a la ejecución y el log del control fallido.
2. Repite con la opción desactivada. El checkout limpio retira el defecto temporal. Guarda el enlace donde pasan los controles, se construye la imagen y aparece el artefacto. Comprueba el SHA en ambos enlaces.
3. Registra ambos enlaces como **simulación controlada**. No representan una reparación histórica de un defecto de producción.

## Promoción de una revisión aprobada

1. Solicita al responsable de Kuberos UCT el nombre de la aplicación, el acceso autorizado y el mecanismo institucional de publicación. Conserva los secretos en la plataforma. Configura PostgreSQL persistente, un correo de prueba restringido, secreto JWT propio, orígenes CORS explícitos, HTTPS y `COOKIE_SECURE=true`. Configura `URL_RECUPERACION_BASE` según la URL institucional.
2. Selecciona una ejecución exitosa de **main**. Guarda el enlace y el SHA completo. Descarga y extrae el artefacto `galeria-api-<SHA>`. Contiene la imagen comprimida, `revision.txt` y el checksum. En PowerShell, desde la carpeta extraída:

   ```powershell
   $revision = (Get-Content revision.txt).Trim()
   $esperado = ((Get-Content SHA256SUMS) -split '\s+')[0]
   if ((Get-FileHash galeria-api.tar.gz -Algorithm SHA256).Hash -ne $esperado) { throw 'Checksum incorrecto' }
   docker load -i galeria-api.tar.gz
   docker image inspect "galeria-arte-api:$revision" --format '{{index .Config.Labels "org.opencontainers.image.revision"}}'
   ```

3. Contrasta la etiqueta con el SHA de Actions. Si la institución usa un registro, publica la imagen validada mediante ese registro autorizado y selecciona su digest en Kuberos. Si la institución despliega desde Git, fija el commit aprobado y conserva el registro del build institucional asociado a ese SHA. Configura la promoción para que sólo seleccione revisiones aprobadas. Documenta el mecanismo efectivamente utilizado.
4. Antes de actualizar, registra la revisión en servicio y la revisión Alembic actual, revisa las migraciones y prepara una copia recuperable de PostgreSQL. El comando de inicio aplica `alembic upgrade head` y ejecuta el seeder. Coordina estos pasos para que una sola instancia inicialice la base durante la actualización.

## Comprobar salud y persistencia

Desde un equipo autorizado, asigna a `$url` la URL **HTTPS** real y a `$id` el ID de un artista de demostración existente. Si se necesita crear uno, usa una cuenta de prueba autorizada y conserva el ID devuelto.

```powershell
$salud = Invoke-WebRequest "$url/api/v1/salud" -UseBasicParsing
$salud.StatusCode
$salud.Content
$antes = Invoke-RestMethod "$url/api/v1/artistas/$id"
$antes | Select-Object id,nombre_artistico
```

Reinicia únicamente la instancia de la API desde la plataforma. Registra la hora y el identificador de la nueva instancia o el evento de reinicio. Espera a que salud devuelva HTTP 200 con `{"estado":"ok"}`. En la misma consola:

```powershell
$despues = Invoke-RestMethod "$url/api/v1/artistas/$id"
if ($antes.id -ne $despues.id -or $antes.nombre_artistico -ne $despues.nombre_artistico) { throw 'Registro diferente tras el reinicio' }
$despues | Select-Object id,nombre_artistico
```

La respuesta de salud verifica disponibilidad. El historial de despliegues de la plataforma establece qué revisión respondió. Guarda ambos junto con la comparación del registro y un fragmento de logs sin credenciales, tokens ni datos personales.

## Reversión

Localiza la última revisión saludable aprobada por CI y su digest o SHA. Compara las migraciones entre ambas revisiones y comprueba que la aplicación anterior es compatible con el esquema actual. Si es compatible, selecciona la revisión anterior en Kuberos, espera el arranque y repite salud y lectura del mismo artista. Registra qué revisión salió y cuál quedó en servicio. Si hay incompatibilidad de esquema, detén la promoción y acuerda con quien administra la BD la recuperación desde la copia verificada o una migración correctiva antes de cambiar el tráfico. Una reversión de imagen por sí sola conserva el esquema aplicado.

## Registro de la entrega

| Evidencia por vincular | Estado |
| --- | --- |
| Dos enlaces de Actions para fallo controlado y ejecución corregida | Pendiente de ejecutar el workflow integrado |
| Ejecución aprobada de main para el commit final y artefacto o digest | Pendiente de la integración final |
| Nombre en Kuberos UCT, URL HTTPS, historial de despliegue y SHA servido | Pendiente de acceso institucional |
| HTTP 200, hora, logs y registro antes y después del reinicio | Pendiente de comprobación institucional |
| Revisión anterior compatible y resultado del ensayo de reversión | Pendiente de comprobación institucional |

Si el equipo carece de permisos o la plataforma está indisponible, registra la fecha, la solicitud de acceso y la respuesta del responsable. Corresponde al docente autorizar una comprobación equivalente.
