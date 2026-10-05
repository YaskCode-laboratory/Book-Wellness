from unittest.mock import MagicMock, patch

from flask import Flask

from routes.objetivos import objetivos_bp


# =============================================================
# CONFIGURACIÓN
# =============================================================

def crear_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test-secret-key"

    app.register_blueprint(objetivos_bp)

    return app


def iniciar_sesion(client, id_usuario=1):
    with client.session_transaction() as sesion:
        sesion["id_usuario"] = id_usuario


# =============================================================
# GET /api/objetivos
# =============================================================

@patch("routes.objetivos.Objetivo")
def test_obtener_objetivos(mock_objetivo):
    app = crear_app()

    objetivos = [
        {
            "id_objetivo": 1,
            "titulo": "Leer 10 libros"
        },
        {
            "id_objetivo": 2,
            "titulo": "Leer 500 páginas"
        }
    ]

    mock_objetivo.obtener_por_usuario.return_value = objetivos

    with app.test_client() as client:
        iniciar_sesion(client, 1)

        respuesta = client.get("/api/objetivos")

    assert respuesta.status_code == 200
    assert respuesta.get_json() == objetivos

    mock_objetivo.obtener_por_usuario.assert_called_once_with(1)


# =============================================================
# POST /api/objetivos
# =============================================================

@patch("routes.objetivos.Objetivo")
def test_crear_objetivo_correctamente(mock_objetivo):
    app = crear_app()

    objetivo = MagicMock()

    objetivo.to_dict.return_value = {
        "id_objetivo": 1,
        "titulo": "Leer 10 libros",
        "tipo": "libros",
        "meta": 10
    }

    mock_objetivo.return_value = objetivo

    with app.test_client() as client:
        iniciar_sesion(client, 1)

        respuesta = client.post(
            "/api/objetivos",
            json={
                "titulo": "Leer 10 libros",
                "descripcion": "Leer durante el mes",
                "tipo": "libros",
                "meta": 10,
                "unidad": "libros",
                "fecha_inicio": "2026-10-01",
                "fecha_fin": "2026-10-31",
                "condicion_tipo": None,
                "condicion_valor": None,
                "frecuencia": "mensual"
            }
        )

    assert respuesta.status_code == 201

    datos = respuesta.get_json()

    assert datos["mensaje"] == "Objetivo creado correctamente."
    assert datos["objetivo"] == {
        "id_objetivo": 1,
        "titulo": "Leer 10 libros",
        "tipo": "libros",
        "meta": 10
    }

    mock_objetivo.assert_called_once_with(
        id_usuario=1,
        titulo="Leer 10 libros",
        descripcion="Leer durante el mes",
        tipo="libros",
        meta=10,
        unidad="libros",
        fecha_inicio="2026-10-01",
        fecha_fin="2026-10-31",
        condicion_tipo=None,
        condicion_valor=None,
        frecuencia="mensual"
    )

    mock_objetivo.crear.assert_called_once_with(objetivo)


@patch("routes.objetivos.Objetivo")
def test_crear_objetivo_sin_titulo(mock_objetivo):
    app = crear_app()

    with app.test_client() as client:
        iniciar_sesion(client)

        respuesta = client.post(
            "/api/objetivos",
            json={
                "tipo": "libros",
                "meta": 10
            }
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == {
        "error": "El título es obligatorio."
    }

    mock_objetivo.assert_not_called()


@patch("routes.objetivos.Objetivo")
def test_crear_objetivo_sin_tipo(mock_objetivo):
    app = crear_app()

    with app.test_client() as client:
        iniciar_sesion(client)

        respuesta = client.post(
            "/api/objetivos",
            json={
                "titulo": "Leer libros",
                "meta": 10
            }
        )

    assert respuesta.status_code == 400
    assert respuesta.get_json() == {
        "error": "El tipo de objetivo es obligatorio."
    }

    mock_objetivo.assert_not_called()


@patch("routes.objetivos.Objetivo")
def test_crear_objetivo_sin_meta(mock_objetivo):
    app = crear_app()

    with app.test_client() as client:
        iniciar_sesion(client)

        respuesta = client.post(
            "/api/objetivos",
            json={
                "titulo": "Leer libros",
                "tipo": "libros"
            }
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == {
        "error": "La meta es obligatoria."
    }

    mock_objetivo.assert_not_called()


@patch("routes.objetivos.Objetivo")
def test_crear_objetivo_meta_no_numerica(mock_objetivo):
    app = crear_app()

    with app.test_client() as client:
        iniciar_sesion(client)

        respuesta = client.post(
            "/api/objetivos",
            json={
                "titulo": "Leer libros",
                "tipo": "libros",
                "meta": "abc"
            }
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == {
        "error": "La meta debe ser numérica."
    }

    mock_objetivo.assert_not_called()


@patch("routes.objetivos.Objetivo")
def test_crear_objetivo_meta_menor_o_igual_a_cero(mock_objetivo):
    app = crear_app()

    with app.test_client() as client:
        iniciar_sesion(client)

        respuesta = client.post(
            "/api/objetivos",
            json={
                "titulo": "Leer libros",
                "tipo": "libros",
                "meta": 0
            }
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == {
        "error": "La meta debe ser mayor que cero."
    }

    mock_objetivo.assert_not_called()


# =============================================================
# PUT /api/objetivos/<id_objetivo>
# =============================================================

@patch("routes.objetivos.Objetivo")
def test_editar_objetivo_correctamente(mock_objetivo):
    app = crear_app()

    objetivo = MagicMock()

    objetivo.progreso_actual = 5
    objetivo.meta = 10

    objetivo.to_dict.return_value = {
        "id_objetivo": 1,
        "titulo": "Leer 20 libros",
        "tipo": "libros",
        "meta": 20,
        "estado": "activo",
        "completado": False
    }

    mock_objetivo.obtener_por_id.return_value = objetivo

    with app.test_client() as client:
        iniciar_sesion(client, 1)

        respuesta = client.put(
            "/api/objetivos/1",
            json={
                "titulo": "Leer 20 libros",
                "descripcion": "Nueva descripción",
                "tipo": "libros",
                "meta": 20,
                "unidad": "libros",
                "fecha_inicio": "2026-10-01",
                "fecha_fin": "2026-12-31",
                "condicion_tipo": None,
                "condicion_valor": None,
                "frecuencia": "mensual"
            }
        )

    assert respuesta.status_code == 200

    datos = respuesta.get_json()

    assert datos["mensaje"] == "Objetivo actualizado correctamente."
    assert datos["objetivo"] == {
        "id_objetivo": 1,
        "titulo": "Leer 20 libros",
        "tipo": "libros",
        "meta": 20,
        "estado": "activo",
        "completado": False
    }

    assert objetivo.titulo == "Leer 20 libros"
    assert objetivo.descripcion == "Nueva descripción"
    assert objetivo.tipo == "libros"
    assert objetivo.meta == 20
    assert objetivo.unidad == "libros"
    assert objetivo.fecha_inicio == "2026-10-01"
    assert objetivo.fecha_fin == "2026-12-31"
    assert objetivo.frecuencia == "mensual"

    mock_objetivo.obtener_por_id.assert_called_once_with("1")
    mock_objetivo.actualizar.assert_called_once_with(objetivo)


@patch("routes.objetivos.Objetivo")
def test_editar_objetivo_completado(mock_objetivo):
    app = crear_app()

    objetivo = MagicMock()

    objetivo.progreso_actual = 10
    objetivo.meta = 5
    objetivo.to_dict.return_value = {
        "id_objetivo": 1,
        "estado": "completado",
        "completado": True
    }

    mock_objetivo.obtener_por_id.return_value = objetivo

    with app.test_client() as client:
        iniciar_sesion(client)

        respuesta = client.put(
            "/api/objetivos/1",
            json={
                "titulo": "Leer libros",
                "tipo": "libros",
                "meta": 5
            }
        )

    assert respuesta.status_code == 200

    assert objetivo.progreso_actual == 5
    assert objetivo.estado == "completado"
    assert objetivo.completado is True

    mock_objetivo.actualizar.assert_called_once_with(objetivo)


@patch("routes.objetivos.Objetivo")
def test_editar_objetivo_sin_datos(mock_objetivo):
    app = crear_app()

    with app.test_client() as client:
        iniciar_sesion(client)

        respuesta = client.put(
            "/api/objetivos/1",
            json={}
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == {
        "error": "No se recibieron datos."
    }

    mock_objetivo.obtener_por_id.assert_not_called()


@patch("routes.objetivos.Objetivo")
def test_editar_objetivo_no_encontrado(mock_objetivo):
    app = crear_app()

    mock_objetivo.obtener_por_id.return_value = None

    with app.test_client() as client:
        iniciar_sesion(client)

        respuesta = client.put(
            "/api/objetivos/99",
            json={
                "titulo": "Leer libros",
                "tipo": "libros",
                "meta": 10
            }
        )

    assert respuesta.status_code == 404

    assert respuesta.get_json() == {
        "error": "Objetivo no encontrado."
    }

    mock_objetivo.obtener_por_id.assert_called_once_with("99")


@patch("routes.objetivos.Objetivo")
def test_editar_objetivo_sin_titulo(mock_objetivo):
    app = crear_app()

    objetivo = MagicMock()

    mock_objetivo.obtener_por_id.return_value = objetivo

    with app.test_client() as client:
        iniciar_sesion(client)

        respuesta = client.put(
            "/api/objetivos/1",
            json={
                "tipo": "libros",
                "meta": 10
            }
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == {
        "error": "El título es obligatorio."
    }

    mock_objetivo.actualizar.assert_not_called()


@patch("routes.objetivos.Objetivo")
def test_editar_objetivo_sin_tipo(mock_objetivo):
    app = crear_app()

    objetivo = MagicMock()

    mock_objetivo.obtener_por_id.return_value = objetivo

    with app.test_client() as client:
        iniciar_sesion(client)

        respuesta = client.put(
            "/api/objetivos/1",
            json={
                "titulo": "Leer libros",
                "meta": 10
            }
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == {
        "error": "El tipo de objetivo es obligatorio."
    }

    mock_objetivo.actualizar.assert_not_called()


@patch("routes.objetivos.Objetivo")
def test_editar_objetivo_meta_no_numerica(mock_objetivo):
    app = crear_app()

    objetivo = MagicMock()

    mock_objetivo.obtener_por_id.return_value = objetivo

    with app.test_client() as client:
        iniciar_sesion(client)

        respuesta = client.put(
            "/api/objetivos/1",
            json={
                "titulo": "Leer libros",
                "tipo": "libros",
                "meta": "abc"
            }
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == {
        "error": "La meta debe ser numérica."
    }

    mock_objetivo.actualizar.assert_not_called()


@patch("routes.objetivos.Objetivo")
def test_editar_objetivo_meta_menor_o_igual_a_cero(mock_objetivo):
    app = crear_app()

    objetivo = MagicMock()

    mock_objetivo.obtener_por_id.return_value = objetivo

    with app.test_client() as client:
        iniciar_sesion(client)
        respuesta = client.put(
            "/api/objetivos/1",
            json={
                "titulo": "Leer libros",
                "tipo": "libros",
                "meta": 0
            }
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == {
        "error": "La meta debe ser mayor que cero."
    }

    mock_objetivo.actualizar.assert_not_called()


# =============================================================
# DELETE /api/objetivos/<id_objetivo>
# =============================================================

@patch("routes.objetivos.Objetivo")
def test_eliminar_objetivo_correctamente(mock_objetivo):
    app = crear_app()

    mock_objetivo.eliminar.return_value = True

    with app.test_client() as client:
        iniciar_sesion(client)

        respuesta = client.delete(
            "/api/objetivos/1"
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "mensaje": "Objetivo eliminado correctamente."
    }

    mock_objetivo.eliminar.assert_called_once_with("1")


@patch("routes.objetivos.Objetivo")
def test_eliminar_objetivo_no_encontrado(mock_objetivo):
    app = crear_app()

    mock_objetivo.eliminar.return_value = False

    with app.test_client() as client:
        iniciar_sesion(client)

        respuesta = client.delete(
            "/api/objetivos/99"
        )

    assert respuesta.status_code == 404

    assert respuesta.get_json() == {
        "error": "Objetivo no encontrado."
    }

    mock_objetivo.eliminar.assert_called_once_with("99")