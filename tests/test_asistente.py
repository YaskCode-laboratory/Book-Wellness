from unittest.mock import patch

from flask import Flask, session

from IA.asistente import ia_bp


# ============================================================
# CONFIGURACIÓN
# ============================================================

def crear_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test-secret-key"

    app.register_blueprint(ia_bp)

    return app


# ============================================================
# /api/ia
# ============================================================

def test_preguntar_ia_sin_sesion():

    app = crear_app()

    with app.test_client() as client:

        respuesta = client.post(
            "/api/ia",
            json={
                "mensaje": "¿Qué libro me recomiendas?"
            }
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "respuesta": "Debes iniciar sesión."
    }


def test_preguntar_ia_sin_mensaje():

    app = crear_app()

    with app.test_client() as client:

        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 1

        respuesta = client.post(
            "/api/ia",
            json={
                "mensaje": ""
            }
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "respuesta": "Escribe una pregunta."
    }


def test_preguntar_ia_mensaje_con_espacios():

    app = crear_app()

    with app.test_client() as client:

        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 1

        respuesta = client.post(
            "/api/ia",
            json={
                "mensaje": "   "
            }
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "respuesta": "Escribe una pregunta."
    }


@patch("IA.asistente.motor")
def test_preguntar_ia_general(
    mock_motor
):

    app = crear_app()

    mock_motor.generar_texto.return_value = (
        "Te recomiendo leer El Principito."
    )

    with app.test_client() as client:

        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 5

        respuesta = client.post(
            "/api/ia",
            json={
                "mensaje": "Recomiéndame un libro.",
                "seccion": "general"
            }
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "respuesta": "Te recomiendo leer El Principito."
    }

    mock_motor.generar_texto.assert_called_once_with(
        5,
        # PROMPT_SISTEMA se comprueba después
        mock_motor.generar_texto.call_args.args[1],
        "Recomiéndame un libro."
    )


@patch("IA.asistente.motor")
def test_preguntar_ia_sin_seccion(
    mock_motor
):

    app = crear_app()

    mock_motor.generar_texto.return_value = "Respuesta de AM."

    with app.test_client() as client:

        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 10

        respuesta = client.post(
            "/api/ia",
            json={
                "mensaje": "¿Qué puedo leer?"
            }
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "respuesta": "Respuesta de AM."
    }

    mock_motor.generar_texto.assert_called_once()

    argumentos = mock_motor.generar_texto.call_args.args

    assert argumentos[0] == 10
    assert argumentos[2] == "¿Qué puedo leer?"


@patch("IA.asistente.motor_objetivos")
def test_preguntar_ia_seccion_objetivos(
    mock_motor_objetivos
):

    app = crear_app()

    mock_motor_objetivos.conversar.return_value = (
        "Tu objetivo de lectura va muy bien."
    )

    with app.test_client() as client:

        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 7

        respuesta = client.post(
            "/api/ia",
            json={
                "mensaje": "¿Cómo voy con mi objetivo?",
                "seccion": "objetivos"
            }
        )

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {
        "respuesta": "Tu objetivo de lectura va muy bien."
    }

    mock_motor_objetivos.conversar.assert_called_once_with(
        7,
        "¿Cómo voy con mi objetivo?"
    )


@patch("IA.asistente.motor")
def test_preguntar_ia_error_motor(
    mock_motor
):

    app = crear_app()

    mock_motor.generar_texto.side_effect = Exception(
        "Error de conexión"
    )

    with app.test_client() as client:

        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 3

        respuesta = client.post(
            "/api/ia",
            json={
                "mensaje": "Hola AM"
            }
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "respuesta": "Error: Error de conexión"
    }


@patch("IA.asistente.motor_objetivos")
def test_preguntar_ia_error_objetivos(
    mock_motor_objetivos
):

    app = crear_app()

    mock_motor_objetivos.conversar.side_effect = Exception(
        "Error en objetivos"
    )

    with app.test_client() as client:

        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 8

        respuesta = client.post(
            "/api/ia",
            json={
                "mensaje": "Ayúdame con mi objetivo.",
                "seccion": "objetivos"
            }
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "respuesta": "Error: Error en objetivos"
    }


@patch("IA.asistente.motor")
def test_preguntar_ia_usa_id_usuario_de_sesion(
    mock_motor
):

    app = crear_app()

    mock_motor.generar_texto.return_value = "Respuesta."

    with app.test_client() as client:

        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 123

        respuesta = client.post(
            "/api/ia",
            json={
                "mensaje": "Hola"
            }
        )

    assert respuesta.status_code == 200

    argumentos = mock_motor.generar_texto.call_args.args

    assert argumentos[0] == 123
    assert argumentos[2] == "Hola"


@patch("IA.asistente.motor")
def test_preguntar_ia_mensaje_se_recorta(
    mock_motor
):

    app = crear_app()

    mock_motor.generar_texto.return_value = "Respuesta."

    with app.test_client() as client:

        with client.session_transaction() as sesion:
            sesion["id_usuario"] = 15

        respuesta = client.post(
            "/api/ia",
            json={
                "mensaje": "   Hola AM   "
            }
        )

    assert respuesta.status_code == 200

    argumentos = mock_motor.generar_texto.call_args.args

    assert argumentos[2] == "Hola AM"