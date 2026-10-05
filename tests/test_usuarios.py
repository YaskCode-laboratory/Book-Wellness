from unittest.mock import patch, MagicMock

from flask import Flask

from routes.usuarios import registrar_rutas


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
# /api/registrar_usuario
# ============================================================

@patch("routes.usuarios.Usuario")
def test_registrar_usuario_correctamente(mock_usuario):
    app = crear_app()

    usuario = MagicMock()
    usuario.registrar.return_value = 10

    mock_usuario.return_value = usuario

    datos = {
        "nombre": "Ricardo",
        "correo": "ricardo@test.com",
        "password": "123456",
        "nivel": "principiante"
    }

    with app.test_client() as client:
        respuesta = client.post(
            "/api/registrar_usuario",
            json=datos
        )

    assert respuesta.status_code == 201

    assert respuesta.get_json() == {
        "mensaje": "¡Usuario Ricardo registrado con éxito!",
        "id_asignado": 10
    }

    mock_usuario.assert_called_once_with(
        nombre="Ricardo",
        correo="ricardo@test.com",
        password="123456",
        nivel_actual="principiante"
    )

    usuario.registrar.assert_called_once()


@patch("routes.usuarios.Usuario")
def test_registrar_usuario_faltan_campos(mock_usuario):
    app = crear_app()

    datos = {
        "nombre": "Ricardo",
        "correo": "ricardo@test.com",
        "password": "123456"
    }

    with app.test_client() as client:
        respuesta = client.post(
            "/api/registrar_usuario",
            json=datos
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == {
        "error": "Todos los campos son obligatorios"
    }

    mock_usuario.assert_not_called()


@patch("routes.usuarios.Usuario")
def test_registrar_usuario_correo_duplicado(mock_usuario):
    app = crear_app()

    import mysql.connector

    usuario = MagicMock()

    error = mysql.connector.errors.IntegrityError(
        msg="Duplicate entry"
    )

    usuario.registrar.side_effect = error

    mock_usuario.return_value = usuario

    datos = {
        "nombre": "Ricardo",
        "correo": "ricardo@test.com",
        "password": "123456",
        "nivel": "principiante"
    }

    with app.test_client() as client:
        respuesta = client.post(
            "/api/registrar_usuario",
            json=datos
        )

    assert respuesta.status_code == 409

    assert respuesta.get_json() == {
        "error": "Este correo ya está registrado"
    }


@patch("routes.usuarios.Usuario")
def test_registrar_usuario_error_mysql(mock_usuario):
    app = crear_app()

    import mysql.connector

    usuario = MagicMock()

    error = mysql.connector.Error(
        msg="Error de conexión"
    )

    usuario.registrar.side_effect = error

    mock_usuario.return_value = usuario

    datos = {
        "nombre": "Ricardo",
        "correo": "ricardo@test.com",
        "password": "123456",
        "nivel": "principiante"
    }

    with app.test_client() as client:
        respuesta = client.post(
            "/api/registrar_usuario",
            json=datos
        )

    assert respuesta.status_code == 500

    assert respuesta.get_json() == {
        "error": "Error en MySQL: Error de conexión"
    }


@patch("routes.usuarios.Usuario")
def test_registrar_usuario_error_inesperado(mock_usuario):
    app = crear_app()

    usuario = MagicMock()

    usuario.registrar.side_effect = Exception(
        "Error inesperado"
    )

    mock_usuario.return_value = usuario

    datos = {
        "nombre": "Ricardo",
        "correo": "ricardo@test.com",
        "password": "123456",
        "nivel": "principiante"
    }
    with app.test_client() as client:
        respuesta = client.post(
            "/api/registrar_usuario",
            json=datos
        )

    assert respuesta.status_code == 500

    assert respuesta.get_json() == {
        "error": "Error inesperado: Error inesperado"
    }


# ============================================================
# /api/login
# ============================================================

@patch("routes.usuarios.Usuario")
def test_login_correctamente(mock_usuario):
    app = crear_app()

    usuario = MagicMock()

    usuario.id_usuario = 5
    usuario.nombre = "Ricardo"
    usuario.correo = "ricardo@test.com"

    mock_usuario.iniciar_sesion.return_value = usuario

    datos = {
        "correo": "ricardo@test.com",
        "password": "123456"
    }

    with app.test_client() as client:
        respuesta = client.post(
            "/api/login",
            json=datos
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "mensaje": "¡Bienvenido, Ricardo!",
        "usuario": {
            "id_usuario": 5,
            "nombre": "Ricardo",
            "correo": "ricardo@test.com"
        }
    }

    mock_usuario.iniciar_sesion.assert_called_once_with(
        "ricardo@test.com",
        "123456"
    )

    with client.session_transaction() as sesion:
        assert sesion["id_usuario"] == 5
        assert sesion["nombre"] == "Ricardo"


@patch("routes.usuarios.Usuario")
def test_login_faltan_campos(mock_usuario):
    app = crear_app()

    datos = {
        "correo": "ricardo@test.com"
    }

    with app.test_client() as client:
        respuesta = client.post(
            "/api/login",
            json=datos
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == {
        "error": "Rellena todos los campos"
    }

    mock_usuario.iniciar_sesion.assert_not_called()


@patch("routes.usuarios.Usuario")
def test_login_credenciales_incorrectas(mock_usuario):
    app = crear_app()

    mock_usuario.iniciar_sesion.return_value = None

    datos = {
        "correo": "ricardo@test.com",
        "password": "incorrecta"
    }

    with app.test_client() as client:
        respuesta = client.post(
            "/api/login",
            json=datos
        )

    assert respuesta.status_code == 401

    assert respuesta.get_json() == {
        "error": "Credenciales incorrectas"
    }

    mock_usuario.iniciar_sesion.assert_called_once_with(
        "ricardo@test.com",
        "incorrecta"
    )


# ============================================================
# /api/recomendacion-inicial
# ============================================================

@patch("routes.usuarios.RecomendacionInicial")
def test_recomendacion_inicial_usuario_no_autenticado(
    mock_recomendacion
):
    app = crear_app()

    with app.test_client() as client:
        respuesta = client.post(
            "/api/recomendacion-inicial"
        )

    assert respuesta.status_code == 401

    assert respuesta.get_json() == {
        "error": "Usuario no autenticado"
    }

    mock_recomendacion.ya_generada.assert_not_called()
    mock_recomendacion.generar.assert_not_called()


@patch("routes.usuarios.RecomendacionInicial")
def test_recomendacion_inicial_ya_generada(
    mock_recomendacion
):
    app = crear_app()

    mock_recomendacion.ya_generada.return_value = True

    with app.test_client() as client:

        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 5

        respuesta = client.post(
            "/api/recomendacion-inicial"
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "mensaje": "La recomendación inicial ya fue generada."
    }

    mock_recomendacion.ya_generada.assert_called_once_with(5)

    mock_recomendacion.generar.assert_not_called()


@patch("routes.usuarios.RecomendacionInicial")
def test_recomendacion_inicial_generada_correctamente(
    mock_recomendacion
):
    app = crear_app()
    mock_recomendacion.ya_generada.return_value = False
    mock_recomendacion.generar.return_value = True

    with app.test_client() as client:

        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 5

        respuesta = client.post(
            "/api/recomendacion-inicial"
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "mensaje": "Recomendación inicial generada correctamente."
    }

    mock_recomendacion.ya_generada.assert_called_once_with(5)

    mock_recomendacion.generar.assert_called_once_with(5)


@patch("routes.usuarios.RecomendacionInicial")
def test_recomendacion_inicial_error_generando(
    mock_recomendacion
):
    app = crear_app()

    mock_recomendacion.ya_generada.return_value = False
    mock_recomendacion.generar.return_value = False

    with app.test_client() as client:

        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 5

        respuesta = client.post(
            "/api/recomendacion-inicial"
        )

    assert respuesta.status_code == 500

    assert respuesta.get_json() == {
        "error": "No se pudo generar la recomendación inicial."
    }

    mock_recomendacion.generar.assert_called_once_with(5)


# ============================================================
# /api/logout
# ============================================================

def test_logout():
    app = crear_app()

    with app.test_client() as client:

        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 5
            sesion["nombre"] = "Ricardo"

        respuesta = client.post("/api/logout")

        assert respuesta.status_code == 200

        assert respuesta.get_json() == {
            "mensaje": "Sesión cerrada"
        }

        with client.session_transaction() as sesion:
            assert "id_usuario" not in sesion
            assert "nombre" not in sesion