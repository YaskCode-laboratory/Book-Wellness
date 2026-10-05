from unittest.mock import patch
from io import BytesIO
from flask import Flask

from routes.seguimiento import registrar_rutas


# ============================================================
# CONFIGURACIÓN
# ============================================================

def crear_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test-secret-key"

    registrar_rutas(app)

    return app


# ============================================================
# /api/agregar_libro_manual
# ============================================================

def test_agregar_libro_manual_sin_sesion():
    app = crear_app()

    with app.test_client() as client:
        respuesta = client.post(
            "/api/agregar_libro_manual",
            data={
                "titulo": "El Principito",
                "autor": "Antoine de Saint-Exupéry"
            }
        )

    assert respuesta.status_code == 401

    assert respuesta.get_json() == {
        "error": "No hay sesión activa"
    }


def test_agregar_libro_manual_sin_titulo():
    app = crear_app()

    with app.test_client() as client:
        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 1

        respuesta = client.post(
            "/api/agregar_libro_manual",
            data={
                "autor": "Antoine de Saint-Exupéry"
            }
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == {
        "error": "Título y autor son obligatorios"
    }


def test_agregar_libro_manual_sin_autor():
    app = crear_app()

    with app.test_client() as client:
        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 1

        respuesta = client.post(
            "/api/agregar_libro_manual",
            data={
                "titulo": "El Principito"
            }
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == {
        "error": "Título y autor son obligatorios"
    }


@patch("routes.seguimiento.db.invalidar_cache_recomendaciones")
@patch("routes.seguimiento.cloudinary.uploader.upload")
@patch("routes.seguimiento.Libro")
def test_agregar_libro_manual_correctamente(
    mock_libro,
    mock_upload,
    mock_cache
):
    app = crear_app()

    mock_upload.return_value = {
        "secure_url": "https://cloudinary.com/portada.jpg"
    }

    instancia_libro = mock_libro.return_value
    instancia_libro.guardar.return_value = 10

    with app.test_client() as client:
        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 1

        respuesta = client.post(
            "/api/agregar_libro_manual",
            data={
                "titulo": "El Principito",
                "autor": "Antoine de Saint-Exupéry",
                "descripcion": "Un clásico",
                "paginas": "100",
                "capitulos": "10",
                "anio": "1943",
                "genero": "Fantasía",
                "formato": "Físico",
                "categoria": "pendiente",
                "portada": (
                    BytesIO(b"imagen de prueba"),
                    "portada.jpg"
                )

            },
            content_type="multipart/form-data"
        )

    assert respuesta.status_code == 201

    assert respuesta.get_json() == {
        "mensaje": "Libro agregado correctamente"
    }

    mock_upload.assert_called_once()

    mock_libro.assert_called_once_with(
        id_usuario=1,
        titulo="El Principito",
        autor="Antoine de Saint-Exupéry",
        descripcion="Un clásico",
        portada="https://cloudinary.com/portada.jpg",
        categoria="pendiente",
        key_libro=None,
        paginas="100",
        id_google=None,
        genero="Fantasía",
        anio="1943",
        es_manual=True,
        formato="Físico"
    )

    instancia_libro.guardar.assert_called_once_with()

    mock_libro.actualizar_datos.assert_called_once_with(
        10,
        num_caps=10
    )

    mock_cache.assert_called_once_with(1)

@patch("routes.seguimiento.db.invalidar_cache_recomendaciones")
@patch("routes.seguimiento.Libro")
def test_agregar_libro_manual_sin_capitulos(
    mock_libro,
    mock_cache
):
    app = crear_app()

    instancia_libro = mock_libro.return_value
    instancia_libro.guardar.return_value = 15

    with app.test_client() as client:
        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 2

        respuesta = client.post(
            "/api/agregar_libro_manual",
            data={
                "titulo": "1984",
                "autor": "George Orwell"
            }
        )

    assert respuesta.status_code == 201

    assert respuesta.get_json() == {
        "mensaje": "Libro agregado correctamente"
    }

    instancia_libro.guardar.assert_called_once_with()

    mock_libro.actualizar_datos.assert_not_called()

    mock_cache.assert_called_once_with(2)


@patch("routes.seguimiento.db.invalidar_cache_recomendaciones")
@patch("routes.seguimiento.Libro")
def test_agregar_libro_manual_libro_duplicado(
    mock_libro,
    mock_cache
):
    app = crear_app()

    instancia_libro = mock_libro.return_value
    instancia_libro.guardar.return_value = False

    with app.test_client() as client:
        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 1

        respuesta = client.post(
            "/api/agregar_libro_manual",
            data={
                "titulo": "1984",
                "autor": "George Orwell"
            }
        )

    assert respuesta.status_code == 409

    assert respuesta.get_json() == {
        "error": "Este libro ya está en tu lista"
    }

    instancia_libro.guardar.assert_called_once_with()

    mock_cache.assert_not_called()


@patch("routes.seguimiento.Libro")
def test_agregar_libro_manual_error(mock_libro):
    app = crear_app()

    instancia_libro = mock_libro.return_value
    instancia_libro.guardar.side_effect = Exception(
        "Error de base de datos"
    )

    with app.test_client() as client:
        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 1

        respuesta = client.post(
            "/api/agregar_libro_manual",
            data={
                "titulo": "1984",
                "autor": "George Orwell"
            }
        )

    assert respuesta.status_code == 500

    assert respuesta.get_json() == {
        "error": "Error de base de datos"
    }


# ============================================================
# /api/eliminar_libro
# ============================================================

def test_eliminar_libro_datos_incompletos():
    app = crear_app()

    with app.test_client() as client:
        respuesta = client.delete(
            "/api/eliminar_libro",
            json={}
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == {
        "error": "Datos incompletos"
    }


def test_eliminar_libro_sin_id_libro():
    app = crear_app()

    with app.test_client() as client:
        respuesta = client.delete(
            "/api/eliminar_libro",
            json={
                "id_usuario": 1
            }
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == {
        "error": "Datos incompletos"
    }


def test_eliminar_libro_sin_id_usuario():
    app = crear_app()

    with app.test_client() as client:
        respuesta = client.delete(
            "/api/eliminar_libro",
            json={
                "id_libro": 5
            }
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == {
        "error": "Datos incompletos"
    }


@patch("routes.seguimiento.db.invalidar_cache_recomendaciones")
@patch("routes.seguimiento.Libro")
def test_eliminar_libro_correctamente(
    mock_libro,
    mock_cache
):
    app = crear_app()

    with app.test_client() as client:
        respuesta = client.delete(
            "/api/eliminar_libro",
            json={
                "id_libro": "5",
                "id_usuario": "2"
            }
        )
    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "mensaje": "Libro eliminado"
    }

    mock_libro.eliminar.assert_called_once_with(
        5,
        2
    )

    mock_cache.assert_called_once_with("2")


@patch("routes.seguimiento.Libro")
def test_eliminar_libro_error(mock_libro):
    app = crear_app()

    mock_libro.eliminar.side_effect = Exception(
        "Error al eliminar"
    )

    with app.test_client() as client:
        respuesta = client.delete(
            "/api/eliminar_libro",
            json={
                "id_libro": 5,
                "id_usuario": 2
            }
        )

    assert respuesta.status_code == 500

    assert respuesta.get_json() == {
        "error": "Error al eliminar"
    }


# ============================================================
# /api/eventos_seguimiento
# ============================================================

def test_eventos_seguimiento_sin_usuario():
    app = crear_app()

    with app.test_client() as client:
        respuesta = client.get(
            "/api/eventos_seguimiento?fecha=2026-10-05"
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == []


def test_eventos_seguimiento_sin_fecha():
    app = crear_app()

    with app.test_client() as client:
        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 1

        respuesta = client.get(
            "/api/eventos_seguimiento"
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == []


def test_eventos_seguimiento_sin_usuario_ni_fecha():
    app = crear_app()

    with app.test_client() as client:
        respuesta = client.get(
            "/api/eventos_seguimiento"
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == []


@patch("routes.seguimiento.Seguimiento.obtener_eventos_por_fecha")
def test_eventos_seguimiento_correctamente(
    mock_eventos
):
    app = crear_app()

    eventos = [
        {
            "id": 1,
            "tipo": "lectura",
            "fecha": "2026-10-05"
        },
        {
            "id": 2,
            "tipo": "nota",
            "fecha": "2026-10-05"
        }
    ]

    mock_eventos.return_value = eventos

    with app.test_client() as client:
        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 7

        respuesta = client.get(
            "/api/eventos_seguimiento?fecha=2026-10-05"
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == eventos

    mock_eventos.assert_called_once_with(
        7,
        "2026-10-05"
    )


@patch("routes.seguimiento.Seguimiento.obtener_eventos_por_fecha")
def test_eventos_seguimiento_sin_eventos(
    mock_eventos
):
    app = crear_app()

    mock_eventos.return_value = []

    with app.test_client() as client:
        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 7

        respuesta = client.get(
            "/api/eventos_seguimiento?fecha=2026-10-05"
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == []

    mock_eventos.assert_called_once_with(
        7,
        "2026-10-05"
    )