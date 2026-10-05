from unittest.mock import MagicMock, patch

import db


# ============================================================
# obtener_conexion
# ============================================================

@patch("db.mysql.connector.connect")
def test_obtener_conexion(mock_connect):
    conexion = MagicMock()

    mock_connect.return_value = conexion

    resultado = db.obtener_conexion()

    assert resultado == conexion

    mock_connect.assert_called_once_with(
        user="root",
        password="",
        host="localhost",
        database="proyectowellness",
        port=3306
    )


# ============================================================
# guardar_recomendaciones
# ============================================================

@patch("db.obtener_conexion")
def test_guardar_recomendaciones(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    libros = [
        {
            "titulo": "El Principito",
            "autor": "Antoine de Saint-Exupéry",
            "descripcion": "Un clásico",
            "portada": "portada.jpg",
            "paginas": 96,
            "generos": "Fantasía",
            "anio": 1943,
            "id_google": "google123",
            "key": "clave123"
        }
    ]

    db.guardar_recomendaciones(
        5,
        libros
    )

    assert cursor.execute.call_count == 2

    primera_consulta = cursor.execute.call_args_list[0]

    assert primera_consulta.args[1] == (5,)

    segunda_consulta = cursor.execute.call_args_list[1]

    assert segunda_consulta.args[1] == (
        5,
        "El Principito",
        "Antoine de Saint-Exupéry",
        "Un clásico",
        "portada.jpg",
        96,
        "Fantasía",
        1943,
        "google123",
        "clave123"
    )

    conexion.commit.assert_called_once()

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("db.obtener_conexion")
def test_guardar_recomendaciones_sin_libros(
    mock_obtener_conexion
):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    db.guardar_recomendaciones(
        5,
        []
    )

    cursor.execute.assert_called_once()

    conexion.commit.assert_called_once()

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


# ============================================================
# obtener_recomendaciones_cache
# ============================================================

@patch("db.obtener_conexion")
def test_obtener_recomendaciones_cache(
    mock_obtener_conexion
):
    conexion = MagicMock()
    cursor = MagicMock()

    recomendaciones = [
        {
            "titulo": "El Principito",
            "autor": "Antoine de Saint-Exupéry"
        },
        {
            "titulo": "1984",
            "autor": "George Orwell"
        }
    ]

    cursor.fetchall.return_value = recomendaciones

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    resultado = db.obtener_recomendaciones_cache(5)

    assert resultado == recomendaciones

    cursor.execute.assert_called_once_with(
        """
        SELECT * FROM recomendaciones_cache 
        WHERE id_usuario = %s
        ORDER BY fecha_generacion DESC
    """,
        (5,)
    )

    cursor.fetchall.assert_called_once()

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


# ============================================================
# invalidar_cache_recomendaciones
# ============================================================

@patch("db.obtener_conexion")
def test_invalidar_cache_recomendaciones(
    mock_obtener_conexion
):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    db.invalidar_cache_recomendaciones(5)
    cursor.execute.assert_called_once_with(
        "DELETE FROM recomendaciones_cache WHERE id_usuario = %s",
        (5,)
    )

    conexion.commit.assert_called_once()

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


# ============================================================
# guardar_mensaje
# ============================================================

@patch("db.obtener_conexion")
def test_guardar_mensaje(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    db.guardar_mensaje(
        5,
        "usuario",
        "Hola, necesito una recomendación."
    )

    cursor.execute.assert_called_once()

    parametros = cursor.execute.call_args.args[1]

    assert parametros == (
        5,
        "usuario",
        "Hola, necesito una recomendación."
    )

    conexion.commit.assert_called_once()

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


# ============================================================
# obtener_estado_recomendacion_inicial
# ============================================================

@patch("db.obtener_conexion")
def test_obtener_estado_recomendacion_inicial_true(
    mock_obtener_conexion
):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = (1,)

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    resultado = db.obtener_estado_recomendacion_inicial(5)

    assert resultado is True

    cursor.execute.assert_called_once()

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("db.obtener_conexion")
def test_obtener_estado_recomendacion_inicial_false(
    mock_obtener_conexion
):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = (0,)

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    resultado = db.obtener_estado_recomendacion_inicial(5)

    assert resultado is False

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("db.obtener_conexion")
def test_obtener_estado_recomendacion_inicial_usuario_no_existe(
    mock_obtener_conexion
):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = None

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    resultado = db.obtener_estado_recomendacion_inicial(999)

    assert resultado is False

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


# ============================================================
# obtener_historial
# ============================================================

@patch("db.obtener_conexion")
def test_obtener_historial(
    mock_obtener_conexion
):
    conexion = MagicMock()
    cursor = MagicMock()

    historial = [
        {
            "rol": "usuario",
            "mensaje": "Hola"
        },
        {
            "rol": "asistente",
            "mensaje": "¡Hola! ¿En qué puedo ayudarte?"
        }
    ]

    cursor.fetchall.return_value = historial.copy()

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    resultado = db.obtener_historial(5)

    assert resultado == [
        {
            "rol": "asistente",
            "mensaje": "¡Hola! ¿En qué puedo ayudarte?"
        },
        {
            "rol": "usuario",
            "mensaje": "Hola"
        }
    ]

    cursor.execute.assert_called_once_with(
        """
        SELECT
            rol,
            mensaje
        FROM conversaciones
        WHERE id_usuario = %s
        ORDER BY fecha DESC
        LIMIT %s
        """,
        (
            5,
            20
        )
    )

    cursor.fetchall.assert_called_once()

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()

@patch("db.obtener_conexion")
def test_obtener_historial_con_limite_personalizado(
    mock_obtener_conexion
):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = []

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    resultado = db.obtener_historial(
        5,
        limite=10
    )

    assert resultado == []

    cursor.execute.assert_called_once_with(
        """
        SELECT
            rol,
            mensaje
        FROM conversaciones
        WHERE id_usuario = %s
        ORDER BY fecha DESC
        LIMIT %s
        """,
        (
            5,
            10
        )
    )

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()