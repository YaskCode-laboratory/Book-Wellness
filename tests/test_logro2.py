from unittest.mock import MagicMock, patch

from models.Ob_Logros.logros2 import Logros2


# ============================================================
# explorador_de_misterio - Logro 8
# ============================================================

@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_explorador_de_misterio_progreso(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 1}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.explorador_de_misterio(1)

    assert resultado == {
        "id": 8,
        "nombre": "Explorador de Misterio",
        "progreso": 1,
        "objetivo": 2,
        "porcentaje": 50,
        "completado": False
    }

    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_explorador_de_misterio_completado(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 2}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.explorador_de_misterio(1)

    assert resultado["progreso"] == 2
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_explorador_de_misterio_supera_objetivo(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 10}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.explorador_de_misterio(1)

    assert resultado["progreso"] == 2
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_explorador_de_misterio_sin_libros(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": None}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.explorador_de_misterio(1)

    assert resultado["progreso"] == 0
    assert resultado["porcentaje"] == 0
    assert resultado["completado"] is False


# ============================================================
# viaje_fantastico - Logro 9
# ============================================================

@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_viaje_fantastico_progreso(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 2}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.viaje_fantastico(1)

    assert resultado == {
        "id": 9,
        "nombre": "Viaje Fantástico",
        "progreso": 2,
        "objetivo": 3,
        "porcentaje": 66,
        "completado": False
    }


@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_viaje_fantastico_completado(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 3}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.viaje_fantastico(1)

    assert resultado["progreso"] == 3
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_viaje_fantastico_supera_objetivo(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 8}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.viaje_fantastico(1)

    assert resultado["progreso"] == 3
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True
@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_viaje_fantastico_sin_libros(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": None}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.viaje_fantastico(1)

    assert resultado["progreso"] == 0
    assert resultado["porcentaje"] == 0
    assert resultado["completado"] is False


# ============================================================
# paso_a_paso - Logro 10
# ============================================================

@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_paso_a_paso_progreso(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"capitulos": 10}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.paso_a_paso(1)

    assert resultado == {
        "id": 10,
        "nombre": "Paso a Paso",
        "progreso": 10,
        "objetivo": 25,
        "porcentaje": 40,
        "completado": False
    }


@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_paso_a_paso_completado(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"capitulos": 25}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.paso_a_paso(1)

    assert resultado["progreso"] == 25
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_paso_a_paso_supera_objetivo(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"capitulos": 50}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.paso_a_paso(1)

    assert resultado["progreso"] == 25
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_paso_a_paso_sin_capitulos(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"capitulos": None}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.paso_a_paso(1)

    assert resultado["progreso"] == 0
    assert resultado["porcentaje"] == 0
    assert resultado["completado"] is False


# ============================================================
# erudito - Logro 12
# ============================================================

@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_erudito_progreso(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 3}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.erudito(1)

    assert resultado == {
        "id": 12,
        "nombre": "Erudito",
        "progreso": 3,
        "objetivo": 5,
        "porcentaje": 60,
        "completado": False
    }


@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_erudito_completado(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 5}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.erudito(1)

    assert resultado["progreso"] == 5
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_erudito_supera_objetivo(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 12}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.erudito(1)
    assert resultado["progreso"] == 5
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_erudito_sin_libros(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": None}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.erudito(1)

    assert resultado["progreso"] == 0
    assert resultado["porcentaje"] == 0
    assert resultado["completado"] is False


# ============================================================
# lector_veloz - Logro 13
# ============================================================

@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_lector_veloz_no_completado(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 0}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.lector_veloz(1)

    assert resultado == {
        "id": 13,
        "nombre": "Lector Veloz",
        "progreso": 0,
        "objetivo": 1,
        "porcentaje": 0,
        "completado": False
    }


@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_lector_veloz_completado(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 1}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.lector_veloz(1)

    assert resultado["progreso"] == 1
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_lector_veloz_muchos_libros(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 5}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.lector_veloz(1)

    assert resultado["progreso"] == 1
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


# ============================================================
# amor_por_los_clasicos - Logro 14
# ============================================================

@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_amor_por_los_clasicos_no_completado(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 0}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.amor_por_los_clasicos(1)

    assert resultado == {
        "id": 14,
        "nombre": "Amor por los Clásicos",
        "progreso": 0,
        "objetivo": 1,
        "porcentaje": 0,
        "completado": False
    }


@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_amor_por_los_clasicos_completado(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 1}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.amor_por_los_clasicos(1)

    assert resultado["progreso"] == 1
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros2.obtener_conexion")
def test_amor_por_los_clasicos_supera_objetivo(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 5}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros2.amor_por_los_clasicos(1)

    assert resultado["progreso"] == 1
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


# ============================================================
# obtener_logros
# ============================================================
@patch("models.Ob_Logros.logros2.Logros2.amor_por_los_clasicos")
@patch("models.Ob_Logros.logros2.Logros2.lector_veloz")
@patch("models.Ob_Logros.logros2.Logros2.erudito")
@patch("models.Ob_Logros.logros2.Logros2.paso_a_paso")
@patch("models.Ob_Logros.logros2.Logros2.viaje_fantastico")
@patch("models.Ob_Logros.logros2.Logros2.explorador_de_misterio")
def test_obtener_logros(
    mock_misterio,
    mock_fantastico,
    mock_paso,
    mock_erudito,
    mock_veloz,
    mock_clasicos
):
    mock_misterio.return_value = {"id": 8}
    mock_fantastico.return_value = {"id": 9}
    mock_paso.return_value = {"id": 10}
    mock_erudito.return_value = {"id": 12}
    mock_veloz.return_value = {"id": 13}
    mock_clasicos.return_value = {"id": 14}

    resultado = Logros2.obtener_logros(50)

    assert resultado == [
        {"id": 8},
        {"id": 9},
        {"id": 10},
        {"id": 12},
        {"id": 13},
        {"id": 14}
    ]

    mock_misterio.assert_called_once_with(50)
    mock_fantastico.assert_called_once_with(50)
    mock_paso.assert_called_once_with(50)
    mock_erudito.assert_called_once_with(50)
    mock_veloz.assert_called_once_with(50)
    mock_clasicos.assert_called_once_with(50)