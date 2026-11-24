import re
from uuid import uuid4

from httpx import Client

from app.infrastructure.models import UsuarioORM


def _login(client: Client, email: str, password: str) -> dict:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()


def test_e2e_escenario_1_acceso_negocio_logout_y_refresh_rechazado(
    client: Client, admin_creado: UsuarioORM
):
    salud = client.get("/api/v1/salud")
    assert salud.status_code == 200
    assert salud.json() == {"estado": "ok"}

    reg_corto = client.post(
        "/api/v1/auth/registro",
        json={"nombre": "Lucas", "email": "lucas@galeria.cl", "password": "Corta1!"},
    )
    assert reg_corto.status_code in (400, 422)

    reg_ok = client.post(
        "/api/v1/auth/registro",
        json={"nombre": "Lucas", "email": "lucas@galeria.cl", "password": "LucasPassword2026!"},
    )
    assert reg_ok.status_code == 201
    cuerpo_reg = reg_ok.json()
    assert cuerpo_reg["rol"] == "usuario"
    assert "password" not in cuerpo_reg
    assert "password_hash" not in cuerpo_reg

    login_mal = client.post(
        "/api/v1/auth/login",
        json={"email": "lucas@galeria.cl", "password": "PasswordIncorrecta2026!"},
    )
    assert login_mal.status_code == 401

    tokens_lucas = _login(client, "lucas@galeria.cl", "LucasPassword2026!")
    headers_lucas = {"Authorization": f"Bearer {tokens_lucas['access_token']}"}

    me = client.get("/api/v1/auth/me", headers=headers_lucas)
    assert me.status_code == 200
    assert me.json()["email"] == "lucas@galeria.cl"

    tokens_admin = _login(client, admin_creado.email, "AdminClaveSegura2026!")
    headers_admin = {"Authorization": f"Bearer {tokens_admin['access_token']}"}

    art = client.post(
        "/api/v1/artistas",
        headers=headers_admin,
        json={
            "nombre_artistico": "Nemesio Antunez",
            "email": "nemesio@galeria.cl",
            "nacionalidad": "Chilena",
            "biografia": "Pintor y grabador.",
        },
    ).json()
    obra = client.post(
        "/api/v1/obras",
        headers=headers_admin,
        json={
            "titulo": "Cordillera",
            "precio_estimado": 7500,
            "anio_creacion": 1970,
            "estilo": "Surrealismo",
            "artista_id": art["id"],
        },
    ).json()
    expo = client.post(
        "/api/v1/exposiciones",
        headers=headers_admin,
        json={
            "nombre_evento": "Retrospectiva",
            "lugar": "Temuco",
            "fecha_inicio": "2026-12-01",
            "fecha_fin": "2026-12-15",
        },
    ).json()

    sol_resp = client.post(
        "/api/v1/solicitudes-prestamo",
        headers=headers_lucas,
        json={"obra_id": obra["id"], "exposicion_id": expo["id"], "dias_prestamo": 12},
    )
    assert sol_resp.status_code == 201
    lista_sol = client.get("/api/v1/solicitudes-prestamo", headers=headers_lucas)
    assert lista_sol.status_code == 200
    assert len(lista_sol.json()) == 1

    logout_resp = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": tokens_lucas["refresh_token"]},
    )
    assert logout_resp.status_code == 200

    refresh_post_logout = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens_lucas["refresh_token"]},
    )
    assert refresh_post_logout.status_code == 401


def test_e2e_escenario_2_recuperacion_uso_unico_e_invalidacion_sesiones(
    client: Client, mailpit: Client
):
    destinatario = f"sofia-{uuid4().hex}@example.com"
    client.post(
        "/api/v1/auth/registro",
        json={
            "nombre": "Sofia Vera",
            "email": destinatario,
            "password": "SofiaClaveOriginal2026!",
        },
    )
    sesion_previa = _login(client, destinatario, "SofiaClaveOriginal2026!")
    headers_previos = {"Authorization": f"Bearer {sesion_previa['access_token']}"}

    rec_inexistente = client.post(
        "/api/v1/auth/solicitar-recuperacion",
        json={"email": "nadie@galeria.cl"},
    )
    assert rec_inexistente.status_code == 200

    rec_ok = client.post(
        "/api/v1/auth/solicitar-recuperacion",
        json={"email": destinatario},
    )
    assert rec_ok.status_code == 200
    repetida = client.post("/api/v1/auth/solicitar-recuperacion", json={"email": destinatario})
    assert repetida.status_code == 200
    assert repetida.json() == rec_ok.json() == rec_inexistente.json()
    _login(client, destinatario, "SofiaClaveOriginal2026!")
    busqueda = mailpit.get("/api/v1/search", params={"query": f"to:{destinatario}"})
    busqueda.raise_for_status()
    mensajes = busqueda.json()["messages"]
    assert len(mensajes) == 1
    mensaje = mailpit.get(f"/api/v1/message/{mensajes[0]['ID']}")
    mensaje.raise_for_status()
    contenido = mensaje.json()
    assert contenido["To"][0]["Address"] == destinatario
    enlace = re.search(r"token=([\w.-]+)", contenido["Text"])
    assert enlace is not None
    token_recuperacion = enlace.group(1)

    reset_invalido = client.post(
        "/api/v1/auth/restablecer-password",
        json={
            "token": sesion_previa["access_token"],
            "nueva_password": "SofiaNuevaClave2026!",
        },
    )
    assert reset_invalido.status_code == 401

    reset_ok = client.post(
        "/api/v1/auth/restablecer-password",
        json={
            "token": token_recuperacion,
            "nueva_password": "SofiaNuevaClave2026!",
        },
    )
    assert reset_ok.status_code == 200

    reset_reuso = client.post(
        "/api/v1/auth/restablecer-password",
        json={
            "token": token_recuperacion,
            "nueva_password": "SofiaTerceraClave2026!",
        },
    )
    assert reset_reuso.status_code == 401

    assert client.get("/api/v1/auth/me", headers=headers_previos).status_code == 401
    assert (
        client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": sesion_previa["refresh_token"]},
        ).status_code
        == 401
    )

    login_vieja = client.post(
        "/api/v1/auth/login",
        json={"email": destinatario, "password": "SofiaClaveOriginal2026!"},
    )
    assert login_vieja.status_code == 401

    login_nueva = _login(client, destinatario, "SofiaNuevaClave2026!")
    assert login_nueva["usuario"]["email"] == destinatario


def test_e2e_escenario_3_permisos_diferenciados_401_vs_403(
    client: Client, admin_creado: UsuarioORM
):
    payload_artista = {
        "nombre_artistico": "Matilde Perez",
        "email": "matilde@galeria.cl",
        "nacionalidad": "Chilena",
        "biografia": "Arte cinetico.",
    }

    sin_token = client.post("/api/v1/artistas", json=payload_artista)
    assert sin_token.status_code == 401
    assert sin_token.json()["error"]["code"] == "UNAUTHORIZED"

    client.post(
        "/api/v1/auth/registro",
        json={
            "nombre": "Visitante",
            "email": "visitante.perm@galeria.cl",
            "password": "VisitanteClave2026!",
        },
    )
    tokens_user = _login(client, "visitante.perm@galeria.cl", "VisitanteClave2026!")
    headers_user = {"Authorization": f"Bearer {tokens_user['access_token']}"}

    sin_permiso = client.post("/api/v1/artistas", headers=headers_user, json=payload_artista)
    assert sin_permiso.status_code == 403
    assert sin_permiso.json()["error"]["code"] == "FORBIDDEN"

    tokens_admin = _login(client, admin_creado.email, "AdminClaveSegura2026!")
    headers_admin = {"Authorization": f"Bearer {tokens_admin['access_token']}"}

    con_permiso = client.post("/api/v1/artistas", headers=headers_admin, json=payload_artista)
    assert con_permiso.status_code == 201
    artista_id = con_permiso.json()["id"]

    consulta_publica = client.get(f"/api/v1/artistas/{artista_id}")
    assert consulta_publica.status_code == 200
    assert consulta_publica.json()["nombre_artistico"] == "Matilde Perez"

    no_existe = client.get("/api/v1/artistas/999999")
    assert no_existe.status_code == 404
    assert no_existe.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_e2e_escenario_4_crud_completo_y_rechazo_solicitud(
    client: Client, admin_creado: UsuarioORM
):
    tokens_admin = _login(client, admin_creado.email, "AdminClaveSegura2026!")
    headers_admin = {"Authorization": f"Bearer {tokens_admin['access_token']}"}

    art = client.post(
        "/api/v1/artistas",
        headers=headers_admin,
        json={
            "nombre_artistico": "Roberto Matta",
            "email": "matta@galeria.cl",
            "nacionalidad": "Chilena",
            "biografia": "Referente del surrealismo.",
        },
    ).json()
    assert len(client.get("/api/v1/artistas").json()) >= 1

    art_upd = client.patch(
        f"/api/v1/artistas/{art['id']}",
        headers=headers_admin,
        json={"nacionalidad": "Chilena-Francesa"},
    )
    assert art_upd.status_code == 200
    assert art_upd.json()["nacionalidad"] == "Chilena-Francesa"

    obra = client.post(
        "/api/v1/obras",
        headers=headers_admin,
        json={
            "titulo": "El Vertigo de Eros",
            "precio_estimado": 15000,
            "anio_creacion": 1944,
            "estilo": "Surrealismo",
            "artista_id": art["id"],
        },
    ).json()
    assert client.get("/api/v1/obras").status_code == 200
    assert client.get(f"/api/v1/obras/{obra['id']}").status_code == 200

    obra_upd = client.patch(
        f"/api/v1/obras/{obra['id']}",
        headers=headers_admin,
        json={"precio_estimado": 18000},
    )
    assert obra_upd.status_code == 200
    assert obra_upd.json()["precio_estimado"] == 18000

    expo = client.post(
        "/api/v1/exposiciones",
        headers=headers_admin,
        json={
            "nombre_evento": "Surrealismo Latinoamericano",
            "lugar": "Museo Nacional",
            "fecha_inicio": "2026-12-05",
            "fecha_fin": "2026-12-28",
        },
    ).json()
    assert len(client.get("/api/v1/exposiciones").json()) >= 1
    assert client.get(f"/api/v1/exposiciones/{expo['id']}").status_code == 200

    sol = client.post(
        "/api/v1/solicitudes-prestamo",
        headers=headers_admin,
        json={"obra_id": obra["id"], "exposicion_id": expo["id"], "dias_prestamo": 7},
    ).json()
    assert (
        client.get(f"/api/v1/solicitudes-prestamo/{sol['id']}", headers=headers_admin).status_code
        == 200
    )

    sol_rech = client.patch(
        f"/api/v1/solicitudes-prestamo/{sol['id']}/rechazar",
        headers=headers_admin,
    )
    assert sol_rech.status_code == 200
    assert sol_rech.json()["estado_solicitud"] == "RECHAZADO"

    del_resp = client.delete(f"/api/v1/obras/{obra['id']}", headers=headers_admin)
    assert del_resp.status_code == 204
    assert client.get(f"/api/v1/obras/{obra['id']}").status_code == 404


def test_contrato_error_validacion_y_openapi(client: Client):
    respuesta = client.post("/api/v1/auth/login", json={})
    assert respuesta.status_code == 422
    error = respuesta.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert {detalle["campo"] for detalle in error["details"]} == {"email", "password"}

    contrato = client.get("/openapi.json").json()
    respuestas = contrato["paths"]["/api/v1/auth/login"]["post"]["responses"]
    for estado in ("401", "422"):
        esquema = respuestas[estado]["content"]["application/json"]["schema"]
        assert esquema["$ref"] == "#/components/schemas/RespuestaError"
