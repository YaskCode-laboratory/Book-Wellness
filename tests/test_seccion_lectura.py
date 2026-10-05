from unittest.mock import MagicMock, patch

from models.SeccionLectura import SeccionLectura


def test_crear_seccion_lectura():
    lectura = SeccionLectura(
        id_lectura=1,
        id_usuario=2,
        id_libro=3,
        tiempo_minutos=30,
        estado="en progreso",
        paginas_leidas=20,
        pagina_actual=20,
        capitulos_leidos=2
    )

    assert lectura.id_lectura == 1
    assert lectura.id_usuario == 2
    assert lectura.id_libro == 3
    assert lectura.tiempo_minutos == 30
    assert lectura.estado == "en progreso"
    assert lectura.paginas_leidas == 20
    assert lectura.pagina_actual == 20
    assert lectura.capitulos_leidos == 2


@patch("models.SeccionLectura.obtener_conexion")
def test_obtener_lectura(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    lectura = {
        "id_lectura": 1,
        "id_usuario": 2,
        "id_libro": 3,
        "pagina_actual": 20
    }

    cursor.fetchone.return_value = lectura

    mock_obtener_conexion.return_value = conexion

    resultado = SeccionLectura.obtener(2, 3)

    assert resultado == lectura

    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.SeccionLectura.obtener_conexion")
def test_obtener_lectura_inexistente(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = None

    mock_obtener_conexion.return_value = conexion

    resultado = SeccionLectura.obtener(2, 999)

    assert resultado is None


@patch("models.SeccionLectura.obtener_conexion")
def test_actualizar_progreso_lectura_existente(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = {
        "id_lectura": 10
    }

    mock_obtener_conexion.return_value = conexion

    lectura = SeccionLectura(
        id_usuario=2,
        id_libro=3,
        pagina_actual=50,
        capitulos_leidos=5,
        fecha_inicio="2026-10-05"
    )

    lectura.actualizar_progreso()

    assert cursor.execute.call_count == 2
    conexion.commit.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.SeccionLectura.obtener_conexion")
def test_actualizar_progreso_lectura_nueva(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    # No existe una lectura previa
    cursor.fetchone.return_value = None
    cursor.lastrowid = 25

    mock_obtener_conexion.return_value = conexion

    lectura = SeccionLectura(
        id_usuario=2,
        id_libro=3,
        pagina_actual=10,
        capitulos_leidos=1,
        fecha_inicio="2026-10-05"
    )

    lectura.actualizar_progreso()

    assert lectura.id_lectura == 25
    assert cursor.execute.call_count == 2
    conexion.commit.assert_called_once()


@patch("models.SeccionLectura.obtener_conexion")
def test_guardar_lectura_existente(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = {
        "id_lectura": 10,
        "tiempo_minutos": 30,
        "paginas_leidas": 20,
        "capitulos_leidos": 2
    }

    mock_obtener_conexion.return_value = conexion

    lectura = SeccionLectura(
        id_usuario=2,
        id_libro=3,
        tiempo_minutos=15,
        paginas_leidas=10,
        capitulos_leidos=1,
        pagina_actual=30,
        estado="en progreso",
        fecha_fin=None
    )

    resultado = lectura.guardar()

    assert resultado == 10
    assert lectura.id_lectura == 10

    conexion.commit.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.SeccionLectura.obtener_conexion")
def test_guardar_lectura_nueva(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = None
    cursor.lastrowid = 50

    mock_obtener_conexion.return_value = conexion

    lectura = SeccionLectura(
        id_usuario=2,
        id_libro=3,
        tiempo_minutos=20,
        paginas_leidas=15,
        capitulos_leidos=2,
        pagina_actual=15,
        estado="en progreso"
    )

    resultado = lectura.guardar()

    assert resultado == 50
    assert lectura.id_lectura == 50

    conexion.commit.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.SeccionLectura.obtener_conexion")
def test_guardar_sesion(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    lectura = SeccionLectura(
        id_lectura=10,
        id_usuario=2,
        id_libro=3,
        paginas_leidas=20,
        tiempo_minutos=30,
        capitulos_leidos=2,
        fecha_fin="2026-10-05 15:00:00"
    )

    lectura.guardar_sesion("feliz")

    cursor.execute.assert_called_once()
    conexion.commit.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()