# CI/CD y operación en Kuberos UCT

## Evidencias disponibles

| Revisión | Evidencia | Alcance |
| --- | --- | --- |
| `f92f4301986aecdd9e18122a530756d6a651511a` | [Actions, push en main](https://github.com/HermoSanMartin/Proyecto-backend/actions/runs/44630597930) | Control de calidad y construcción de imagen aprobados. |
| `69a1a876163d05a80733a000746e1f972631af25` | [Actions, pull request](https://github.com/HermoSanMartin/Proyecto-backend/actions/runs/45450075344) | Ejecución exitosa para la rama del PR. |

El 26 de noviembre se confirmó el acceso del grupo ICINF1108-S1-G7 al [pipeline institucional galeria-arte-g7](https://kubero.inf.uct.cl/pipeline/galeria-arte-g7/apps). La aplicación de producción usa la imagen del commit integrado y atiende en [salud de la API](https://galeria-arte-g7.inf.uct.cl/api/v1/salud). El [PR #11](https://github.com/HermoSanMartin/Proyecto-backend/pull/11) quedó integrado en main en `a5c77f0ae7e5e18981946b043e84d826f516f764`. Los [controles del PR](https://github.com/HermoSanMartin/Proyecto-backend/actions/runs/45728759884) aprobaron la revisión que incorpora la publicación en GHCR.

## Demostrar que CI bloquea un fallo

Una vez integrado el workflow en la rama principal, abre **Actions → CI - Calidad, Pruebas y Contenedor → Run workflow**. Usa la misma revisión de main en ambas ejecuciones.

1. Activa `simular_fallo`. El runner añade un archivo temporal con un nombre indefinido. Ruff debe señalar `F821`, el trabajo de calidad debe fallar y el de construcción debe quedar omitido. Guarda el enlace a la ejecución y el log del control fallido.
2. Repite con la opción desactivada. El checkout limpio retira el defecto temporal. Guarda el enlace donde pasan los controles, se construye la imagen y aparece el artefacto. Comprueba el SHA en ambos enlaces.
3. Registra ambos enlaces como **simulación controlada**. No representan una reparación histórica de un defecto de producción.

## Promoción de una revisión aprobada

1. Abre el pipeline galeria-arte-g7 y selecciona Production. Conserva los secretos en la plataforma. Configura PostgreSQL persistente, un correo de prueba restringido, secreto JWT propio, orígenes CORS explícitos, HTTPS y `COOKIE_SECURE=true`. Configura `URL_RECUPERACION_BASE` según la URL institucional.
2. Selecciona una ejecución exitosa de **main**. Guarda el enlace y el SHA completo. Descarga y extrae el artefacto `galeria-api-<SHA>`. Contiene la imagen comprimida, `revision.txt` y el checksum. En PowerShell, desde la carpeta extraída:

   ```powershell
   $revision = (Get-Content revision.txt).Trim()
   $esperado = ((Get-Content SHA256SUMS) -split '\s+')[0]
   if ((Get-FileHash galeria-api.tar.gz -Algorithm SHA256).Hash -ne $esperado) { throw 'Checksum incorrecto' }
   docker load -i galeria-api.tar.gz
   docker image inspect "galeria-arte-api:$revision" --format '{{index .Config.Labels "org.opencontainers.image.revision"}}'
   ```

3. Tras integrar el PR, abre el resumen de la ejecución exitosa de main y copia la referencia completa de GHCR en **Imagen de contenedor**. Su formato es `ghcr.io/hermosanmartin/galeria-arte-api:<SHA completo>`. Usa el valor real que emitió Actions. Verifica que Kubero puede descargar la imagen, configura el puerto interno 8000 y conserva el digest mostrado al publicarla.
4. Antes de actualizar, registra la revisión en servicio y la revisión Alembic actual, revisa las migraciones y prepara una copia recuperable de PostgreSQL. El comando de inicio aplica `alembic upgrade head` y ejecuta el seeder. Coordina estos pasos para que una sola instancia inicialice la base durante la actualización.

## Comprobar salud y persistencia

Desde un equipo autorizado, asigna a `$url` la URL **HTTPS** real y a `$id` el ID de un artista creado para esta prueba mediante una cuenta administradora autorizada. Conserva el ID devuelto y usa un nombre único para distinguir el registro de los que genera el seeder en cada arranque.

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
| Ejecución aprobada de main para el commit final y artefacto o digest | [CI aprobada de main](https://github.com/HermoSanMartin/Proyecto-backend/actions/runs/45752614780) · [Reportes de pruebas y cobertura](https://github.com/HermoSanMartin/Proyecto-backend/actions/runs/45752614780/artifacts/15085852592) · Revisión integrada `a5c77f0` |
| Nombre en Kuberos UCT, URL HTTPS, historial de despliegue y SHA servido | [Aplicación y eventos de producción](https://kubero.inf.uct.cl/pipeline/galeria-arte-g7/production/galeria-arte-g7/detail) · imagen GHCR etiquetada con el SHA completo de main indicado arriba |
| Salud y persistencia (26 de noviembre de 2026, hora de Chile) | HTTPS 200, `{"estado":"ok"}`. Alta de usuario de prueba 201, ID 3. Tras reiniciar la API desde Kubero, login 200 con el mismo ID 3. PostgreSQL usa un volumen persistente CephFS de 1 GiB. |
| Revisión anterior compatible y resultado del ensayo de reversión | Pendiente de comprobación institucional |

Si el equipo carece de permisos o la plataforma está indisponible, registra la fecha, la solicitud de acceso y la respuesta del responsable. Corresponde al docente autorizar una comprobación equivalente.

En los registros del contenedor web, Uvicorn completó el arranque a la 01:11:30. Kubero reemplazó el pod web terminado en 448h4 por el terminado en 59pgs. El DNS público resolvió el subdominio mediante proxy.inf.uct.cl. Durante la comprobación, el resolvedor local devolvía NXDOMAIN, por lo que se consultó el ingreso institucional manteniendo el nombre HTTPS y la validación del certificado. El correo de recuperación aún requiere un servicio SMTP accesible desde producción.
