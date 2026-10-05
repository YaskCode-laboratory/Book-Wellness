from unittest.mock import MagicMock, patch

from flask import session
from app import app

from models.notificaciones import (
    estado_notificaciones,
    toggle_notificaciones,
    enviar_correo,
    _construir_y_enviar_correo_usuario,
    procesar_notificaciones_al_iniciar_sesion
)


# ============================================================
# ESTADO DE NOTIFICACIONES
# ============================================================

def test_estado_notificaciones_sin_usuario():
    with app.test_request_context():
        session.clear()

        respuesta, codigo = estado_notificaciones()

        assert codigo == 200
        assert respuesta.get_json() == {
            "activadas": True
        }


@patch("models.notificaciones.Usuario.obtener_estado_notificaciones")
def test_estado_notificaciones_usuario_activado(mock_obtener_estado):
    mock_obtener_estado.return_value = True

    with app.test_request_context():
        session["usuario_id"] = 1

        respuesta, codigo = estado_notificaciones()

        assert codigo == 200
        assert respuesta.get_json() == {
            "activadas": True
        }

        mock_obtener_estado.assert_called_once_with(1)


@patch("models.notificaciones.Usuario.obtener_estado_notificaciones")
def test_estado_notificaciones_usuario_desactivado(mock_obtener_estado):
    mock_obtener_estado.return_value = False

    with app.test_request_context():
        session["usuario_id"] = 1

        respuesta, codigo = estado_notificaciones()

        assert codigo == 200
        assert respuesta.get_json() == {
            "activadas": False
        }

        mock_obtener_estado.assert_called_once_with(1)


# ============================================================
# TOGGLE DE NOTIFICACIONES
# ============================================================

def test_toggle_sin_usuario():
    with app.test_request_context():
        session.clear()

        respuesta, codigo = toggle_notificaciones()

        assert codigo == 401
        assert respuesta.get_json() == {
            "error": "Usuario no autenticado"
        }


@patch("models.notificaciones.Usuario.cambiar_estado_notificaciones")
@patch("models.notificaciones.Usuario.obtener_estado_notificaciones")
def test_toggle_activa_notificaciones(
    mock_obtener_estado,
    mock_cambiar_estado
):
    mock_obtener_estado.return_value = False

    with app.test_request_context():
        session["usuario_id"] = 1

        respuesta, codigo = toggle_notificaciones()

        assert codigo == 200
        assert respuesta.get_json() == {
            "activadas": True
        }

        mock_obtener_estado.assert_called_once_with(1)
        mock_cambiar_estado.assert_called_once_with(1, True)

        assert session["notificaciones_activas"] is True


@patch("models.notificaciones.Usuario.cambiar_estado_notificaciones")
@patch("models.notificaciones.Usuario.obtener_estado_notificaciones")
def test_toggle_desactiva_notificaciones(
    mock_obtener_estado,
    mock_cambiar_estado
):
    mock_obtener_estado.return_value = True

    with app.test_request_context():
        session["usuario_id"] = 1

        respuesta, codigo = toggle_notificaciones()

        assert codigo == 200
        assert respuesta.get_json() == {
            "activadas": False
        }

        mock_obtener_estado.assert_called_once_with(1)
        mock_cambiar_estado.assert_called_once_with(1, False)

        assert session["notificaciones_activas"] is False


# ============================================================
# ENVÍO DE CORREOS
# ============================================================

@patch("models.notificaciones.smtplib.SMTP")
def test_enviar_correo_exitoso(mock_smtp):
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server

    resultado = enviar_correo(
        "usuario@gmail.com",
        "Prueba",
        "Este es un correo de prueba."
    )

    assert resultado is True

    mock_smtp.assert_called_once_with(
        "smtp.gmail.com",
        587
    )
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once()
    mock_server.send_message.assert_called_once()
    mock_server.quit.assert_called_once()


@patch("models.notificaciones.smtplib.SMTP")
def test_enviar_correo_error(mock_smtp):
    mock_smtp.side_effect = Exception("Error de conexión")

    resultado = enviar_correo(
        "usuario@gmail.com",
        "Prueba",
        "Este es un correo de prueba."
    )

    assert resultado is False


# ============================================================
# CONSTRUCCIÓN DE CORREOS
# ============================================================

@patch("models.notificaciones.enviar_correo")
def test_construir_correo_calendario(mock_enviar):
    mock_enviar.return_value = True

    usuario = {
        "nombre": "Ricardo",
        "correo": "ricardo@gmail.com",
        "eventos": [
            {
                "tipo": "fin_libro",
                "titulo": "El Principito"
            },
            {
                "tipo": "sesion",
                "titulo": "Sesión de lectura"
            }
        ]
    }

    resultado = _construir_y_enviar_correo_usuario(
        usuario,
        "2026-10-05"
    )

    assert resultado is True

    mock_enviar.assert_called_once()

    argumentos = mock_enviar.call_args[0]

    assert argumentos[0] == "ricardo@gmail.com"
    assert "2026-10-05" in argumentos[1]
    assert "El Principito" in argumentos[2]
    assert "Sesión de lectura" in argumentos[2]


@patch("models.notificaciones.enviar_correo")
def test_construir_correo_sin_eventos(mock_enviar):
    mock_enviar.return_value = True

    usuario = {
        "nombre": "Ricardo",
        "correo": "ricardo@gmail.com",
        "eventos": []
    }

    resultado = _construir_y_enviar_correo_usuario(
        usuario,
        "2026-10-05"
    )

    assert resultado is True

    mock_enviar.assert_called_once()

    argumentos = mock_enviar.call_args[0]

    assert argumentos[0] == "ricardo@gmail.com"
    assert "2026-10-05" in argumentos[1]


# ============================================================
# PROCESAMIENTO DE NOTIFICACIONES AL INICIAR SESIÓN
# ============================================================

@patch("models.notificaciones._construir_y_enviar_correo_usuario")
@patch("models.notificaciones.Calendario.obtener_actividades_usuarios_por_fecha")
@patch("models.notificaciones.Objetivo.obtener_usuarios_con_objetivos_por_vencer")
@patch("models.notificaciones.Usuario.obtener_estado_notificaciones")
def test_procesar_notificaciones_desactivadas(
    mock_estado,
    mock_objetivos,
    mock_calendario,
    mock_construir
):
    mock_estado.return_value = False

    procesar_notificaciones_al_iniciar_sesion(1)

    mock_estado.assert_called_once_with(1)

    mock_calendario.assert_not_called()
    mock_objetivos.assert_not_called()
    mock_construir.assert_not_called()


@patch("models.notificaciones._construir_y_enviar_correo_usuario")
@patch("models.notificaciones.Calendario.obtener_actividades_usuarios_por_fecha")
@patch("models.notificaciones.Objetivo.obtener_usuarios_con_objetivos_por_vencer")
@patch("models.notificaciones.Usuario.obtener_estado_notificaciones")
def test_procesar_notificaciones_sin_actividades(
    mock_estado,
    mock_objetivos,
    mock_calendario,
    mock_construir
):
    mock_estado.return_value = True
    mock_calendario.return_value = []
    mock_objetivos.return_value = []

    procesar_notificaciones_al_iniciar_sesion(1)

    mock_estado.assert_called_once_with(1)
    mock_calendario.assert_called_once()
    mock_objetivos.assert_called_once()

    mock_construir.assert_not_called()


@patch("models.notificaciones._construir_y_enviar_correo_usuario")
@patch("models.notificaciones.Calendario.obtener_actividades_usuarios_por_fecha")
@patch("models.notificaciones.Objetivo.obtener_usuarios_con_objetivos_por_vencer")
@patch("models.notificaciones.Usuario.obtener_estado_notificaciones")
def test_procesar_notificaciones_calendario(
    mock_estado,
    mock_objetivos,
    mock_calendario,
    mock_construir
):
    mock_estado.return_value = True

    mock_calendario.return_value = [
        {
            "id_usuario": 1,
            "nombre": "Ricardo",
            "correo": "ricardo@gmail.com",
            "eventos": [
                {
                    "tipo": "sesion",
                    "titulo": "Leer 20 páginas"
                }
            ]
        }
    ]

    mock_objetivos.return_value = []

    procesar_notificaciones_al_iniciar_sesion(1)

    mock_construir.assert_called_once()

    usuario_recibido = mock_construir.call_args[0][0]

    assert usuario_recibido["id_usuario"] == 1
    assert usuario_recibido["nombre"] == "Ricardo"


@patch("models.notificaciones.enviar_correo")
@patch("models.notificaciones.Calendario.obtener_actividades_usuarios_por_fecha")
@patch("models.notificaciones.Objetivo.obtener_usuarios_con_objetivos_por_vencer")
@patch("models.notificaciones.Usuario.obtener_estado_notificaciones")
def test_procesar_notificaciones_objetivos(
    mock_estado,
    mock_objetivos,
    mock_calendario,
    mock_enviar
):
    mock_estado.return_value = True

    mock_calendario.return_value = []

    mock_objetivos.return_value = [
        {
            "id_usuario": 1,
            "nombre": "Ricardo",
            "correo": "ricardo@gmail.com",
            "objetivos": [
                "Leer 3 libros",
                "Leer 500 páginas"
            ]
        }
    ]

    procesar_notificaciones_al_iniciar_sesion(1)

    mock_enviar.assert_called_once()

    argumentos = mock_enviar.call_args[0]

    assert argumentos[0] == "ricardo@gmail.com"
    assert "vence" in argumentos[1]
    assert "Leer 3 libros" in argumentos[2]
    assert "Leer 500 páginas" in argumentos[2]


@patch("models.notificaciones.enviar_correo")
@patch("models.notificaciones._construir_y_enviar_correo_usuario")
@patch("models.notificaciones.Calendario.obtener_actividades_usuarios_por_fecha")
@patch("models.notificaciones.Objetivo.obtener_usuarios_con_objetivos_por_vencer")
@patch("models.notificaciones.Usuario.obtener_estado_notificaciones")
def test_procesar_notificaciones_calendario_y_objetivos(
    mock_estado,
    mock_objetivos,
    mock_calendario,
    mock_construir,
    mock_enviar
):
    mock_estado.return_value = True

    mock_calendario.return_value = [
        {
            "id_usuario": 1,
            "nombre": "Ricardo",
            "correo": "ricardo@gmail.com",
            "eventos": [
                {
                    "tipo": "fin_libro",
                    "titulo": "El Principito"
                }
            ]
        }
    ]

    mock_objetivos.return_value = [
        {
            "id_usuario": 1,
            "nombre": "Ricardo",
            "correo": "ricardo@gmail.com",
            "objetivos": [
                "Leer 5 libros"
            ]
        }
    ]

    procesar_notificaciones_al_iniciar_sesion(1)

    mock_construir.assert_called_once()
    mock_enviar.assert_called_once()

    usuario_calendario = mock_construir.call_args[0][0]

    assert usuario_calendario["id_usuario"] == 1
    assert usuario_calendario["nombre"] == "Ricardo"

    argumentos = mock_enviar.call_args[0]

    assert argumentos[0] == "ricardo@gmail.com"
    assert "Leer 5 libros" in argumentos[2]