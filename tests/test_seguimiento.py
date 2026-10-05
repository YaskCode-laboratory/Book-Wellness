from datetime import datetime
from unittest.mock import MagicMock, patch

from models.seguimiento import Seguimiento


def test_clave_orden_con_fecha():
    evento = {
        "fecha": "2026-10-05 14:30:00"
    }

    resultado = Seguimiento._clave_orden(evento)

    assert resultado == datetime(2026, 10, 5, 14, 30, 0)


def test_clave_orden_con_fecha_limite():
    evento = {
        "fecha_limite": "2026-10-10"
    }

    resultado = Seguimiento._clave_orden(evento)

    assert resultado == datetime(2026, 10, 10)


def test_clave_orden_con_fecha_fin():
    evento = {
        "fecha_fin": "2026-10-15"
    }

    resultado = Seguimiento._clave_orden(evento)

    assert resultado == datetime(2026, 10, 15)


def test_clave_orden_sin_fecha():
    evento = {}

    resultado = Seguimiento._clave_orden(evento)

    assert resultado == datetime.min


def test_clave_orden_fecha_invalida():
    evento = {
        "fecha": "fecha-invalida"
    }

    resultado = Seguimiento._clave_orden(evento)

    assert resultado == datetime.min


@patch("models.seguimiento.obtener_conexion")
def test_obtener_eventos_por_fecha(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    # Las cuatro consultas de la función devolverán listas vacías.
    cursor.fetchall.side_effect = [
        [],  # fechas límite
        [],  # sesiones
        [],  # primeras sesiones
        []   # concluidos
    ]

    mock_obtener_conexion.return_value = conexion

    resultado = Seguimiento.obtener_eventos_por_fecha(
        1,
        "2026-10-05"
    )

    assert resultado == []

    assert cursor.execute.call_count == 4

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()