from unittest.mock import MagicMock, patch

from flask import Flask

from models.recuperacion import (
    serializer,
    solicitar_recuperacion,
    restablecer_contrasena,
    recuperacion_bp
)


def crear_app():
    app = Flask(__name__)
    app.register_blueprint(recuperacion_bp)
    return app


def test_generar_token_recuperacion():
    correo = "prueba@test.com"

    token = serializer.dumps(
        correo,
        salt="recuperar-contrasena"
    )

    resultado = serializer.loads(
        token,
        salt="recuperar-contrasena",
        max_age=900
    )

    assert resultado == correo


def test_token_invalido():
    token = "token_invalido"

    try:
        serializer.loads(
            token,
            salt="recuperar-contrasena",
            max_age=900
        )
        valido = True
    except Exception:
        valido = False

    assert valido is False


@patch("models.recuperacion.render_template")
@patch("models.recuperacion.obtener_conexion")
def test_solicitar_recuperacion_usuario_no_existe(
    mock_obtener_conexion,
    mock_render_template
):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = None

    mock_obtener_conexion.return_value = conexion
    mock_render_template.return_value = "CodigoEnviado"

    app = crear_app()

    with app.test_request_context(
        "/recuperar",
        method="POST",
        data={"correo": "noexiste@test.com"}
    ):
        resultado = solicitar_recuperacion()

    assert resultado == "CodigoEnviado"

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.recuperacion.enviar_correo")
@patch("models.recuperacion.render_template")
@patch("models.recuperacion.obtener_conexion")
def test_solicitar_recuperacion_usuario_existente(
    mock_obtener_conexion,
    mock_render_template,
    mock_enviar_correo
):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = {
        "id_usuario": 1,
        "nombre": "Usuario Prueba",
        "correo": "prueba@test.com"
    }

    mock_obtener_conexion.return_value = conexion
    mock_render_template.return_value = "CodigoEnviado"

    app = crear_app()

    with app.test_request_context(
        "/recuperar",
        method="POST",
        data={"correo": "prueba@test.com"}
    ):
        resultado = solicitar_recuperacion()

    assert resultado == "CodigoEnviado"

    mock_enviar_correo.assert_called_once()

    argumentos = mock_enviar_correo.call_args.args

    assert argumentos[0] == "prueba@test.com"
    assert "Restablecer" in argumentos[1]


@patch("models.recuperacion.render_template")
def test_restablecer_token_valido_get(mock_render_template):
    correo = "prueba@test.com"

    token = serializer.dumps(
        correo,
        salt="recuperar-contrasena"
    )

    mock_render_template.return_value = "NuevaContraseña"

    app = crear_app()

    with app.test_request_context(
        f"/restablecer/{token}",
        method="GET"
    ):
        resultado = restablecer_contrasena(token)

    assert resultado == "NuevaContraseña"

    mock_render_template.assert_called_once()


def test_restablecer_token_invalido():
    app = crear_app()

    with app.test_request_context(
        "/restablecer/token-invalido",
        method="GET"
    ):
        resultado = restablecer_contrasena("token-invalido")

    assert isinstance(resultado, tuple)
    assert resultado[1] == 400


def test_restablecer_password_vacia():
    correo = "prueba@test.com"

    token = serializer.dumps(
        correo,
        salt="recuperar-contrasena"
    )

    app = crear_app()

    with app.test_request_context(
        f"/restablecer/{token}",
        method="POST",
        data={"password": ""}
    ):
        resultado = restablecer_contrasena(token)

    assert resultado == (
        "La contraseña no puede estar vacía",
        400
    )
