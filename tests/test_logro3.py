from unittest.mock import patch, MagicMock

from models.Ob_Logros.logros3 import Logros3


# ============================================================
# obtener_logros
# ============================================================

def test_obtener_logros():
    with patch.object(Logros3, "mente_sana", return_value={"id": 15}) as mente, \
         patch.object(Logros3, "gran_volumen", return_value={"id": 16}) as volumen, \
         patch.object(Logros3, "lector_versatil", return_value={"id": 17}) as versatil, \
         patch.object(Logros3, "vision_del_futuro", return_value={"id": 18}) as futuro, \
         patch.object(Logros3, "mitad_de_camino", return_value={"id": 19}) as mitad, \
         patch.object(Logros3, "cronicas_reales", return_value={"id": 20}) as cronicas, \
         patch.object(Logros3, "lexic_enriquecido", return_value={"id": 21}) as lexic:

        resultado = Logros3.obtener_logros(5)

    assert resultado == [
        {"id": 15},
        {"id": 16},
        {"id": 17},
        {"id": 18},
        {"id": 19},
        {"id": 20},
        {"id": 21}
    ]

    mente.assert_called_once_with(5)
    volumen.assert_called_once_with(5)
    versatil.assert_called_once_with(5)
    futuro.assert_called_once_with(5)
    mitad.assert_called_once_with(5)
    cronicas.assert_called_once_with(5)
    lexic.assert_called_once_with(5)


# ============================================================
# 15. MENTE SANA
# ============================================================

@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_mente_sana_progreso(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = [
        {"paginas_leidas": 50, "genero": "Salud"},
        {"paginas_leidas": 30, "genero": "Psicología"},
        {"paginas_leidas": 20, "genero": "Fantasía"},
    ]

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.mente_sana(1)

    assert resultado["id"] == 15
    assert resultado["nombre"] == "Mente Sana"
    assert resultado["progreso"] == 80
    assert resultado["objetivo"] == 150
    assert resultado["porcentaje"] == 53
    assert resultado["completado"] is False

    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_mente_sana_completado(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = [
        {"paginas_leidas": 100, "genero": "Salud"},
        {"paginas_leidas": 80, "genero": "Wellness"},
    ]

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.mente_sana(1)

    assert resultado["progreso"] == 150
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_mente_sana_limita_progreso(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = [
        {"paginas_leidas": 500, "genero": "Salud"},
    ]

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.mente_sana(1)

    assert resultado["progreso"] == 150
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_mente_sana_sin_lecturas(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = []

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.mente_sana(1)

    assert resultado["progreso"] == 0
    assert resultado["porcentaje"] == 0
    assert resultado["completado"] is False


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_mente_sana_ignora_generos_no_validos(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()
    cursor.fetchall.return_value = [
        {"paginas_leidas": 100, "genero": "Fantasía"},
        {"paginas_leidas": 50, "genero": None},
        {"paginas_leidas": 30, "genero": ""},
        {"paginas_leidas": 20, "genero": "Historia"},
    ]

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.mente_sana(1)

    assert resultado["progreso"] == 0
    assert resultado["porcentaje"] == 0
    assert resultado["completado"] is False


# ============================================================
# 16. GRAN VOLUMEN
# ============================================================

@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_gran_volumen_progreso(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"paginas": 200}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.gran_volumen(1)

    assert resultado["id"] == 16
    assert resultado["nombre"] == "Gran Volumen"
    assert resultado["progreso"] == 200
    assert resultado["objetivo"] == 400
    assert resultado["porcentaje"] == 50
    assert resultado["completado"] is False


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_gran_volumen_completado(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"paginas": 400}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.gran_volumen(1)

    assert resultado["progreso"] == 400
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_gran_volumen_limita_progreso(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"paginas": 900}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.gran_volumen(1)

    assert resultado["progreso"] == 400
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_gran_volumen_sin_paginas(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"paginas": 0}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.gran_volumen(1)

    assert resultado["progreso"] == 0
    assert resultado["porcentaje"] == 0
    assert resultado["completado"] is False


# ============================================================
# 17. LECTOR VERSÁTIL
# ============================================================

@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_lector_versatil_progreso(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"libros": 1}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.lector_versatil(1)

    assert resultado["id"] == 17
    assert resultado["nombre"] == "Lector Versátil"
    assert resultado["progreso"] == 1
    assert resultado["objetivo"] == 2
    assert resultado["porcentaje"] == 50
    assert resultado["completado"] is False


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_lector_versatil_completado(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"libros": 2}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.lector_versatil(1)

    assert resultado["progreso"] == 2
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_lector_versatil_limita_progreso(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"libros": 10}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion
    resultado = Logros3.lector_versatil(1)

    assert resultado["progreso"] == 2
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_lector_versatil_sin_libros(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"libros": 0}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.lector_versatil(1)

    assert resultado["progreso"] == 0
    assert resultado["porcentaje"] == 0
    assert resultado["completado"] is False


# ============================================================
# 18. VISIÓN DEL FUTURO
# ============================================================

@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_vision_del_futuro_progreso(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"libros": 1}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.vision_del_futuro(1)

    assert resultado["id"] == 18
    assert resultado["nombre"] == "Visión del Futuro"
    assert resultado["progreso"] == 1
    assert resultado["objetivo"] == 2
    assert resultado["porcentaje"] == 50
    assert resultado["completado"] is False


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_vision_del_futuro_completado(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"libros": 2}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.vision_del_futuro(1)

    assert resultado["progreso"] == 2
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_vision_del_futuro_limita_progreso(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"libros": 8}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.vision_del_futuro(1)

    assert resultado["progreso"] == 2
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_vision_del_futuro_sin_libros(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"libros": 0}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.vision_del_futuro(1)

    assert resultado["progreso"] == 0
    assert resultado["porcentaje"] == 0
    assert resultado["completado"] is False


# ============================================================
# 19. MITAD DE CAMINO
# ============================================================

@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_mitad_de_camino_progreso(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"libros": 6}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.mitad_de_camino(1)

    assert resultado["id"] == 19
    assert resultado["nombre"] == "Mitad de Camino"
    assert resultado["progreso"] == 6
    assert resultado["objetivo"] == 12
    assert resultado["porcentaje"] == 50
    assert resultado["completado"] is False


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_mitad_de_camino_completado(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"libros": 12}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.mitad_de_camino(1)

    assert resultado["progreso"] == 12
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True

@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_mitad_de_camino_limita_progreso(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"libros": 30}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.mitad_de_camino(1)

    assert resultado["progreso"] == 12
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_mitad_de_camino_sin_libros(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"libros": 0}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.mitad_de_camino(1)

    assert resultado["progreso"] == 0
    assert resultado["porcentaje"] == 0
    assert resultado["completado"] is False


# ============================================================
# 20. CRÓNICAS REALES
# ============================================================

@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_cronicas_reales_sin_libros(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"libros": 0}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.cronicas_reales(1)

    assert resultado["id"] == 20
    assert resultado["nombre"] == "Crónicas Reales"
    assert resultado["progreso"] == 0
    assert resultado["objetivo"] == 1
    assert resultado["porcentaje"] == 0
    assert resultado["completado"] is False


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_cronicas_reales_completado(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"libros": 1}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.cronicas_reales(1)

    assert resultado["progreso"] == 1
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_cronicas_reales_limita_progreso(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {"libros": 5}

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.cronicas_reales(1)

    assert resultado["progreso"] == 1
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


# ============================================================
# 21. LÉXICO ENRIQUECIDO
# ============================================================

@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_lexic_enriquecido_progreso(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = [
        {"contenido": "Una dos tres cuatro cinco"},
        {"contenido": "seis siete ocho nueve diez"},
    ]

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.lexic_enriquecido(1)

    assert resultado["id"] == 21
    assert resultado["nombre"] == "Léxico Enriquecido"
    assert resultado["progreso"] == 10
    assert resultado["objetivo"] == 20
    assert resultado["porcentaje"] == 50
    assert resultado["completado"] is False


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_lexic_enriquecido_completado(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = [
        {"contenido": "uno dos tres cuatro cinco seis siete ocho nueve diez"},
        {"contenido": "once doce trece catorce quince dieciseis diecisiete dieciocho diecinueve veinte"},
    ]

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.lexic_enriquecido(1)

    assert resultado["progreso"] == 20
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True

@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_lexic_enriquecido_limita_progreso(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = [
        {
            "contenido": (
                "uno dos tres cuatro cinco seis siete ocho nueve diez "
                "once doce trece catorce quince dieciseis diecisiete "
                "dieciocho diecinueve veinte veintiuno veintidos"
            )
        }
    ]

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.lexic_enriquecido(1)

    assert resultado["progreso"] == 20
    assert resultado["porcentaje"] == 100
    assert resultado["completado"] is True


@patch("models.Ob_Logros.logros3.obtener_conexion")
def test_lexic_enriquecido_ignora_notas_vacias(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = [
        {"contenido": ""},
        {"contenido": "   "},
    ]

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    resultado = Logros3.lexic_enriquecido(1)

    assert resultado["progreso"] == 0
    assert resultado["porcentaje"] == 0
    assert resultado["completado"] is False
