from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from models.Ob_Logros.logros1 import Logros1


# ============================================================
# _racha_maxima
# ============================================================

@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_racha_maxima_sin_sesiones(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchall.return_value = []

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1._racha_maxima(1)

    assert resultado == 0

    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_racha_maxima_una_sesion(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    cursor.fetchall.return_value = [
        {"dia": date(2026, 10, 1)}
    ]

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1._racha_maxima(1)

    assert resultado == 1


@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_racha_maxima_dias_consecutivos(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    cursor.fetchall.return_value = [
        {"dia": date(2026, 10, 1)},
        {"dia": date(2026, 10, 2)},
        {"dia": date(2026, 10, 3)},
        {"dia": date(2026, 10, 4)},
        {"dia": date(2026, 10, 5)}
    ]

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1._racha_maxima(1)

    assert resultado == 5


@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_racha_maxima_con_dias_separados(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    cursor.fetchall.return_value = [
        {"dia": date(2026, 10, 1)},
        {"dia": date(2026, 10, 2)},
        {"dia": date(2026, 10, 3)},
        {"dia": date(2026, 10, 8)},
        {"dia": date(2026, 10, 9)}
    ]

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1._racha_maxima(1)

    assert resultado == 3


@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_racha_maxima_varias_rachas(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    cursor.fetchall.return_value = [
        {"dia": date(2026, 10, 1)},
        {"dia": date(2026, 10, 2)},
        {"dia": date(2026, 10, 5)},
        {"dia": date(2026, 10, 6)},
        {"dia": date(2026, 10, 7)},
        {"dia": date(2026, 10, 8)},
        {"dia": date(2026, 10, 15)}
    ]

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1._racha_maxima(1)

    assert resultado == 4


# ============================================================
# devorador_de_paginas
# ============================================================

@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_devorador_de_paginas_progreso(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"paginas": 250}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1.devorador_de_paginas(1)

    assert resultado == {
        "id": 1,
        "nombre": "Devorador de Páginas",
        "progreso": 250,
        "objetivo": 500,
        "porcentaje": 50,
        "completado": False
    }


@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_devorador_de_paginas_completado(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"paginas": 500}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1.devorador_de_paginas(1)
    assert resultado["progreso"] == 500
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_devorador_de_paginas_no_supera_objetivo(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"paginas": 800}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1.devorador_de_paginas(1)

    assert resultado["progreso"] == 500
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_devorador_de_paginas_sin_paginas(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"paginas": None}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1.devorador_de_paginas(1)

    assert resultado["progreso"] == 0
    assert resultado["porcentaje"] == 0
    assert resultado["completado"] is False


# ============================================================
# habito_nocturno
# ============================================================

@patch("models.Ob_Logros.logros1.Logros1._racha_maxima")
def test_habito_nocturno_progreso(mock_racha):
    mock_racha.return_value = 10

    resultado = Logros1.habito_nocturno(1)

    assert resultado == {
        "id": 2,
        "nombre": "Hábito Nocturno",
        "progreso": 10,
        "objetivo": 15,
        "porcentaje": 66,
        "completado": False
    }

    mock_racha.assert_called_once_with(1)


@patch("models.Ob_Logros.logros1.Logros1._racha_maxima")
def test_habito_nocturno_completado(mock_racha):
    mock_racha.return_value = 15

    resultado = Logros1.habito_nocturno(1)

    assert resultado["progreso"] == 15
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros1.Logros1._racha_maxima")
def test_habito_nocturno_supera_objetivo(mock_racha):
    mock_racha.return_value = 30

    resultado = Logros1.habito_nocturno(1)

    assert resultado["progreso"] == 15
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


# ============================================================
# lector_critico
# ============================================================

@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_lector_critico_progreso(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"total": 5}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1.lector_critico(1)

    assert resultado == {
        "id": 3,
        "nombre": "Lector Crítico",
        "progreso": 5,
        "objetivo": 10,
        "porcentaje": 50,
        "completado": False
    }


@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_lector_critico_completado(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"total": 10}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1.lector_critico(1)

    assert resultado["progreso"] == 10
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_lector_critico_sin_notas(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"total": None}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1.lector_critico(1)

    assert resultado["progreso"] == 0
    assert resultado["porcentaje"] == 0
    assert resultado["completado"] is False


# ============================================================
# primeros_pasos
# ============================================================
@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_primeros_pasos_sin_libros(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 0}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1.primeros_pasos(1)

    assert resultado == {
        "id": 4,
        "nombre": "Primeros Pasos",
        "progreso": 0,
        "objetivo": 1,
        "porcentaje": 0,
        "completado": False
    }


@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_primeros_pasos_completado(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 1}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1.primeros_pasos(1)

    assert resultado["progreso"] == 1
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_primeros_pasos_muchos_libros(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"libros": 10}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1.primeros_pasos(1)

    assert resultado["progreso"] == 1
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


# ============================================================
# enfoque_de_hierro
# ============================================================

@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_enfoque_de_hierro_progreso(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"max_tiempo": 60}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1.enfoque_de_hierro(1)

    assert resultado == {
        "id": 5,
        "nombre": "Enfoque de Hierro",
        "progreso": 60,
        "objetivo": 120,
        "porcentaje": 50,
        "completado": False
    }


@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_enfoque_de_hierro_completado(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"max_tiempo": 120}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1.enfoque_de_hierro(1)

    assert resultado["progreso"] == 120
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_enfoque_de_hierro_supera_objetivo(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"max_tiempo": 200}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1.enfoque_de_hierro(1)

    assert resultado["progreso"] == 120
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


# ============================================================
# maraton_dominical
# ============================================================

@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_maraton_dominical_progreso(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"mejor_dia": 50}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1.maraton_dominical(1)

    assert resultado == {
        "id": 6,
        "nombre": "Maratón Dominical",
        "progreso": 50,
        "objetivo": 100,
        "porcentaje": 50,
        "completado": False
    }


@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_maraton_dominical_completado(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()
    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"mejor_dia": 100}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1.maraton_dominical(1)

    assert resultado["progreso"] == 100
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros1.obtener_conexion")
def test_maraton_dominical_supera_objetivo(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {"mejor_dia": 250}

    mock_obtener_conexion.return_value = conexion

    resultado = Logros1.maraton_dominical(1)

    assert resultado["progreso"] == 100
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


# ============================================================
# racha_imbatible
# ============================================================

@patch("models.Ob_Logros.logros1.Logros1._racha_maxima")
def test_racha_imbatible_progreso(mock_racha):
    mock_racha.return_value = 15

    resultado = Logros1.racha_imbatible(1)

    assert resultado == {
        "id": 7,
        "nombre": "Racha Imbatible",
        "progreso": 15,
        "objetivo": 30,
        "porcentaje": 50,
        "completado": False
    }

    mock_racha.assert_called_once_with(1)


@patch("models.Ob_Logros.logros1.Logros1._racha_maxima")
def test_racha_imbatible_completado(mock_racha):
    mock_racha.return_value = 30

    resultado = Logros1.racha_imbatible(1)

    assert resultado["progreso"] == 30
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros1.Logros1._racha_maxima")
def test_racha_imbatible_supera_objetivo(mock_racha):
    mock_racha.return_value = 50

    resultado = Logros1.racha_imbatible(1)

    assert resultado["progreso"] == 30
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


# ============================================================
# obtener_logros
# ============================================================

@patch("models.Ob_Logros.logros1.Logros1.racha_imbatible")
@patch("models.Ob_Logros.logros1.Logros1.maraton_dominical")
@patch("models.Ob_Logros.logros1.Logros1.enfoque_de_hierro")
@patch("models.Ob_Logros.logros1.Logros1.primeros_pasos")
@patch("models.Ob_Logros.logros1.Logros1.lector_critico")
@patch("models.Ob_Logros.logros1.Logros1.habito_nocturno")
@patch("models.Ob_Logros.logros1.Logros1.devorador_de_paginas")
def test_obtener_logros(
    mock_devorador,
    mock_habito,
    mock_lector,
    mock_primeros,
    mock_enfoque,
    mock_maraton,
    mock_racha
):
    mock_devorador.return_value = {"id": 1}
    mock_habito.return_value = {"id": 2}
    mock_lector.return_value = {"id": 3}
    mock_primeros.return_value = {"id": 4}
    mock_enfoque.return_value = {"id": 5}
    mock_maraton.return_value = {"id": 6}
    mock_racha.return_value = {"id": 7}

    resultado = Logros1.obtener_logros(99)

    assert resultado == [
        {"id": 1},
        {"id": 2},
        {"id": 3},
        {"id": 4},
        {"id": 5},
        {"id": 6},
        {"id": 7}
    ]

    mock_devorador.assert_called_once_with(99)
    mock_habito.assert_called_once_with(99)
    mock_lector.assert_called_once_with(99)
    mock_primeros.assert_called_once_with(99)
    mock_enfoque.assert_called_once_with(99)
    mock_maraton.assert_called_once_with(99)
    mock_racha.assert_called_once_with(99)