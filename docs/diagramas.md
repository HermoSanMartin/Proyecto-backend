# Arquitectura y modelo de datos

## Alta de un artista

```mermaid
sequenceDiagram
    actor C as Cliente HTTP
    participant P as FastAPI y dependencias
    participant A as AuthService
    participant S as ArtistaService
    participant R as Repositorios SQLAlchemy
    participant D as PostgreSQL
    C->>P: POST /api/v1/artistas con JSON y Bearer
    P->>A: Resolver identidad desde el JWT
    A->>A: Validar firma, propósito y caducidad
    A->>R: Obtener usuario y comprobar versión del token
    R->>D: Consultar usuario
    alt Credencial ausente o inválida
        P-->>C: 401 Unauthorized
    else Usuario sin permiso
        P-->>C: 403 Forbidden
    else Administrador con DTO válido
        P->>S: Crear entidad Artista
        S->>R: Buscar correo y crear si está disponible
        R->>D: Insertar artista y confirmar transacción
        R-->>S: Artista con ID
        S-->>P: Entidad creada
        P-->>C: 201 Created con ArtistaRespuesta
    end
```

La ausencia de Bearer se detecta en las dependencias antes de consultar al usuario. Para un token válido, el backend consulta la identidad persistida antes de autorizar la operación.

| Responsabilidad | Implementación |
| --- | --- |
| Recibir el JSON, validar campos y formar la respuesta | [Router de artistas](../app/presentation/routers/artistas.py) y [DTO](../app/presentation/schemas/artista_schema.py) |
| Extraer la credencial y exigir rol de administrador | [Dependencias HTTP](../app/presentation/dependencies.py) |
| Validar identidad, estado de cuenta y versión de sesión | [Servicio de autenticación](../app/application/services/auth_service.py) y [validación criptográfica](../app/infrastructure/security/jwt_manager.py) |
| Representar el artista y comprobar duplicados | [Entidad de dominio](../app/domain/artista.py) y [servicio](../app/application/services/artista_service.py) |
| Convertir entre entidad y registro, escribir y leer el ID | [Mapper](../app/infrastructure/mappers/artista_mapper.py) y [repositorio SQLAlchemy](../app/infrastructure/repositories/artista_repository.py) |
| Convertir errores de aplicación en respuestas HTTP | [Manejadores de errores](../app/presentation/error_handlers.py) |

## Entidades y relaciones

El diagrama muestra las siete tablas de negocio y seguridad y sus relaciones por clave foránea. Cada tabla tiene una clave primaria `id`. En una relación uno a muchos, el lado derecho puede tener cero o más filas.

```mermaid
erDiagram
    artistas ||--o{ obras : crea
    obras ||--o{ solicitudes_prestamo : recibe
    exposiciones ||--o{ solicitudes_prestamo : motiva
    usuarios ||--o{ refresh_tokens : mantiene
    usuarios ||--o{ tokens_recuperacion : solicita
    artistas {
        int id PK
        string nombre_artistico
        string email
        string nacionalidad
        string biografia
    }
    obras {
        int id PK
        int artista_id FK
        string titulo
        int anio_creacion
        boolean disponible
    }
    exposiciones {
        int id PK
        string nombre_evento
        string lugar
        date fecha_inicio
        date fecha_fin
    }
    solicitudes_prestamo {
        int id PK
        int obra_id FK
        int exposicion_id FK
        date fecha_solicitud
        int dias_prestamo
        string estado_solicitud
    }
    usuarios {
        int id PK
        string email
        string rol
        string password_hash
        int token_version
    }
    refresh_tokens {
        int id PK
        int usuario_id FK
        string token_hash
        string familia_id
        boolean revocado
    }
    tokens_recuperacion {
        int id PK
        int usuario_id FK
        string jti
        datetime expira_en
        boolean usado
    }
```

Los atributos mostrados permiten seguir los flujos de creación, préstamo y seguridad. Los tipos y restricciones completos están en los [modelos ORM](../app/infrastructure/models/) y en las [migraciones Alembic](../migrations/versions/).
