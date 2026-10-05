import pytest
from unittest.mock import MagicMock, patch

from models.calendario import Calendario


# ============================================================
# obtener_fechas_calendario
# ============================================================

@patch("models.calendario.obtener_conexion")
def test_obtener_fechas_calendario(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    cursor.fetchall.return_value = [
        {"fecha": "2026-10-01", "tipo": "sesion"},
        {"fecha": "2026-10-01", "tipo": "primera_sesion"},
        {"fecha": "2026-10-02", "tipo": "fecha_limite"},
        {"fecha": "2026-10-03", "tipo": "concluido"},
    ]

    mock_obtener_conexion.return_value = conexion

    resultado = Calendario.obtener_fechas_calendario(1)

    assert resultado == {
        "2026-10-01": "primera_sesion",
        "2026-10-02": "fecha_limite",
        "2026-10-03": "concluido"
    }

    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.calendario.obtener_conexion")
def test_obtener_fechas_calendario_prioridad_concluido(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    cursor.fetchall.return_value = [
        {"fecha": "2026-10-05", "tipo": "sesion"},
        {"fecha": "2026-10-05", "tipo": "primera_sesion"},
        {"fecha": "2026-10-05", "tipo": "fecha_limite"},
        {"fecha": "2026-10-05", "tipo": "concluido"},
    ]

    mock_obtener_conexion.return_value = conexion

    resultado = Calendario.obtener_fechas_calendario(1)

    assert resultado["2026-10-05"] == "concluido"


@patch("models.calendario.obtener_conexion")
def test_obtener_fechas_calendario_sin_datos(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchall.return_value = []

    mock_obtener_conexion.return_value = conexion

    resultado = Calendario.obtener_fechas_calendario(1)

    assert resultado == {}

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.calendario.obtener_conexion")
def test_obtener_fechas_calendario_prioridad_fecha_limite(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    cursor.fetchall.return_value = [
        {"fecha": "2026-10-10", "tipo": "sesion"},
        {"fecha": "2026-10-10", "tipo": "fecha_limite"},
    ]

    mock_obtener_conexion.return_value = conexion

    resultado = Calendario.obtener_fechas_calendario(1)

    assert resultado["2026-10-10"] == "fecha_limite"


# ============================================================
# obtener_libros_por_fecha
# ============================================================

@patch("models.calendario.obtener_conexion")
def test_obtener_libros_por_fecha(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    libros = [
        {
            "titulo": "Harry Potter",
            "autor": "J.K. Rowling",
            "portada": "portada.jpg",
            "id_libro": 1,
            "tipo": "sesion"
        },
        {
            "titulo": "El Principito",
            "autor": "Antoine de Saint-Exupéry",
            "portada": "principito.jpg",
            "id_libro": 2,
            "tipo": "fecha_limite"
        }
    ]

    cursor.fetchall.return_value = libros
    mock_obtener_conexion.return_value = conexion

    resultado = Calendario.obtener_libros_por_fecha(
        1,
        "2026-10-05"
    )

    assert resultado == libros
    assert len(resultado) == 2

    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.calendario.obtener_conexion")
def test_obtener_libros_por_fecha_sin_resultados(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()
    conexion.cursor.return_value = cursor
    cursor.fetchall.return_value = []

    mock_obtener_conexion.return_value = conexion

    resultado = Calendario.obtener_libros_por_fecha(
        1,
        "2026-10-05"
    )

    assert resultado == []

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


# ============================================================
# guardar_fecha_limite
# ============================================================

@patch("models.calendario.obtener_conexion")
def test_guardar_fecha_limite(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    Calendario.guardar_fecha_limite(
        1,
        25,
        "2026-10-30"
    )

    cursor.execute.assert_called_once()
    conexion.commit.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.calendario.obtener_conexion")
def test_guardar_fecha_limite_verifica_parametros(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    Calendario.guardar_fecha_limite(
        10,
        50,
        "2026-12-15"
    )

    argumentos = cursor.execute.call_args

    parametros = argumentos[0][1]

    assert parametros == (
        "2026-12-15",
        10,
        50
    )


# ============================================================
# obtener_actividades_usuarios_por_fecha
# ============================================================

@patch("models.calendario.obtener_conexion")
def test_obtener_actividades_usuarios_por_fecha(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    cursor.fetchall.return_value = [
        {
            "id_usuario": 1,
            "nombre": "Juan",
            "correo": "juan@gmail.com",
            "titulo": "Harry Potter",
            "tipo": "sesion"
        },
        {
            "id_usuario": 1,
            "nombre": "Juan",
            "correo": "juan@gmail.com",
            "titulo": "El Principito",
            "tipo": "fin_libro"
        },
        {
            "id_usuario": 2,
            "nombre": "Maria",
            "correo": "maria@gmail.com",
            "titulo": "1984",
            "tipo": "sesion"
        }
    ]

    mock_obtener_conexion.return_value = conexion

    resultado = Calendario.obtener_actividades_usuarios_por_fecha(
        "2026-10-05"
    )

    assert len(resultado) == 2

    assert resultado[0]["id_usuario"] == 1
    assert resultado[0]["nombre"] == "Juan"
    assert resultado[0]["correo"] == "juan@gmail.com"

    assert len(resultado[0]["eventos"]) == 2

    assert resultado[0]["eventos"][0] == {
        "titulo": "Harry Potter",
        "tipo": "sesion"
    }

    assert resultado[0]["eventos"][1] == {
        "titulo": "El Principito",
        "tipo": "fin_libro"
    }

    assert resultado[1]["id_usuario"] == 2
    assert len(resultado[1]["eventos"]) == 1

    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.calendario.obtener_conexion")
def test_obtener_actividades_usuarios_por_fecha_sin_datos(
    mock_obtener_conexion
):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchall.return_value = []

    mock_obtener_conexion.return_value = conexion

    resultado = Calendario.obtener_actividades_usuarios_por_fecha(
        "2026-10-05"
    )

    assert resultado == []

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.calendario.obtener_conexion")
def test_obtener_actividades_agrupa_varios_eventos_del_mismo_usuario(
    mock_obtener_conexion
):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchall.return_value = [
        {
            "id_usuario": 5,
            "nombre": "Carlos",
            "correo": "carlos@gmail.com",
            "titulo": "Libro 1",
            "tipo": "sesion"
        },
        {
            "id_usuario": 5,
            "nombre": "Carlos",
            "correo": "carlos@gmail.com",
            "titulo": "Libro 2",
            "tipo": "sesion"
        },
        {
            "id_usuario": 5,
            "nombre": "Carlos",
            "correo": "carlos@gmail.com",
            "titulo": "Libro 3",
            "tipo": "fin_libro"
        }
    ]

    mock_obtener_conexion.return_value = conexion

    resultado = Calendario.obtener_actividades_usuarios_por_fecha(
        "2026-10-05"
    )

    assert len(resultado) == 1
    assert resultado[0]["id_usuario"] == 5
    assert len(resultado[0]["eventos"]) == 3

    titulos = [
        evento["titulo"]
        for evento in resultado[0]["eventos"]
    ]

    assert titulos == [
        "Libro 1",
        "Libro 2",
        "Libro 3"
    ]


@patch("models.calendario.obtener_conexion")
def test_obtener_actividades_usuarios_conserva_datos_usuario(
    mock_obtener_conexion
):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    cursor.fetchall.return_value = [
        {
            "id_usuario": 20,
            "nombre": "Ana",
            "correo": "ana@example.com",
            "titulo": "Cien años de soledad",
            "tipo": "sesion"
        }
    ]

    mock_obtener_conexion.return_value = conexion

    resultado = Calendario.obtener_actividades_usuarios_por_fecha(
        "2026-10-05"
    )

    assert resultado[0]["id_usuario"] == 20
    assert resultado[0]["nombre"] == "Ana"
    assert resultado[0]["correo"] == "ana@example.com"
    assert resultado[0]["eventos"][0]["titulo"] == (
        "Cien años de soledad"
    )
    assert resultado[0]["eventos"][0]["tipo"] == "sesion"