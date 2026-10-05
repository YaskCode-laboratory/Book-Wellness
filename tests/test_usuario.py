from unittest.mock import MagicMock, patch

from werkzeug.security import generate_password_hash

from models.Usuario import Usuario


def test_crear_usuario():
    usuario = Usuario(
        id_usuario=1,
        nombre="Usuario Prueba",
        correo="prueba@test.com",
        password="123456",
        nivel_actual="principiante"
    )

    assert usuario.id_usuario == 1
    assert usuario.nombre == "Usuario Prueba"
    assert usuario.correo == "prueba@test.com"
    assert usuario.password == "123456"
    assert usuario.nivel_actual == "principiante"


@patch("models.Usuario.obtener_conexion")
def test_registrar_usuario(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.lastrowid = 10

    mock_obtener_conexion.return_value = conexion

    usuario = Usuario(
        nombre="Usuario Prueba",
        correo="prueba@test.com",
        password="123456",
        nivel_actual="principiante"
    )

    resultado = usuario.registrar()

    assert resultado == 10
    assert usuario.id_usuario == 10

    # Comprueba que se utilizó una contraseña protegida
    primera_consulta = cursor.execute.call_args_list[0]
    parametros = primera_consulta.args[1]

    password_guardada = parametros[2]

    assert password_guardada != "123456"

    # Comprueba que realmente es un hash válido
    from werkzeug.security import check_password_hash

    assert check_password_hash(password_guardada, "123456")


@patch("models.Usuario.obtener_conexion")
@patch("models.notificaciones.procesar_notificaciones_al_iniciar_sesion")
def test_iniciar_sesion_correcta(
    mock_notificaciones,
    mock_obtener_conexion
):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    password_hash = generate_password_hash("123456")

    cursor.fetchone.return_value = {
        "id_usuario": 1,
        "nombre": "Usuario Prueba",
        "correo": "prueba@test.com",
        "password": password_hash,
        "recomendacion_inicial_generada": 0
    }

    mock_obtener_conexion.return_value = conexion

    usuario = Usuario.iniciar_sesion(
        "prueba@test.com",
        "123456"
    )

    assert usuario is not None
    assert usuario.id_usuario == 1
    assert usuario.nombre == "Usuario Prueba"
    assert usuario.correo == "prueba@test.com"

    mock_notificaciones.assert_called_once_with(1)


@patch("models.Usuario.obtener_conexion")
def test_iniciar_sesion_password_incorrecta(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    password_hash = generate_password_hash("123456")

    cursor.fetchone.return_value = {
        "id_usuario": 1,
        "nombre": "Usuario Prueba",
        "correo": "prueba@test.com",
        "password": password_hash,
        "recomendacion_inicial_generada": 0
    }

    mock_obtener_conexion.return_value = conexion

    usuario = Usuario.iniciar_sesion(
        "prueba@test.com",
        "password_incorrecta"
    )

    assert usuario is None


@patch("models.Usuario.obtener_conexion")
def test_iniciar_sesion_usuario_inexistente(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = None

    mock_obtener_conexion.return_value = conexion

    usuario = Usuario.iniciar_sesion(
        "noexiste@test.com",
        "123456"
    )

    assert usuario is None


@patch("models.Usuario.obtener_conexion")
def test_obtener_estado_notificaciones(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {
        "notificaciones_activadas": 1
    }

    mock_obtener_conexion.return_value = conexion

    resultado = Usuario.obtener_estado_notificaciones(1)

    assert resultado is True


@patch("models.Usuario.obtener_conexion")
def test_cambiar_estado_notificaciones(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()
    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    Usuario.cambiar_estado_notificaciones(1, False)

    assert cursor.execute.called
    conexion.commit.assert_called_once()