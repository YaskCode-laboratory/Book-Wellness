import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta

from models.estadistica import Estadistica


# ============================================================
# _FORMATEAR_TIEMPO
# ============================================================

def test_formatear_tiempo_cero():
    resultado = Estadistica._formatear_tiempo(0)

    assert resultado == "0 s"


def test_formatear_tiempo_menor_a_un_minuto():
    resultado = Estadistica._formatear_tiempo(0.5)

    assert resultado == "30 s"


def test_formatear_tiempo_menor_a_un_minuto_decimal():
    resultado = Estadistica._formatear_tiempo(0.25)

    assert resultado == "15 s"


def test_formatear_tiempo_un_minuto():
    resultado = Estadistica._formatear_tiempo(1)

    assert resultado == "1.0 Min"


def test_formatear_tiempo_minutos():
    resultado = Estadistica._formatear_tiempo(30)

    assert resultado == "30.0 Min"


def test_formatear_tiempo_minutos_decimales():
    resultado = Estadistica._formatear_tiempo(45.5)

    assert resultado == "45.5 Min"


def test_formatear_tiempo_una_hora():
    resultado = Estadistica._formatear_tiempo(60)

    assert resultado == "1.0 h"


def test_formatear_tiempo_horas():
    resultado = Estadistica._formatear_tiempo(120)

    assert resultado == "2.0 h"


def test_formatear_tiempo_horas_decimales():
    resultado = Estadistica._formatear_tiempo(90)

    assert resultado == "1.5 h"


def test_formatear_tiempo_none():
    resultado = Estadistica._formatear_tiempo(None)

    assert resultado == "0 s"


# ============================================================
# _CALCULAR_RACHAS
# ============================================================

def test_calcular_rachas_sin_dias():
    resultado = Estadistica._calcular_rachas([])

    assert resultado == (0, 0)


def test_calcular_rachas_un_solo_dia():
    hoy = date.today()

    resultado = Estadistica._calcular_rachas([hoy])

    assert resultado == (1, 1)


def test_calcular_rachas_dias_consecutivos():
    hoy = date.today()

    dias = [
        hoy - timedelta(days=2),
        hoy - timedelta(days=1),
        hoy
    ]

    resultado = Estadistica._calcular_rachas(dias)

    assert resultado == (3, 3)


def test_calcular_rachas_dias_no_consecutivos():
    hoy = date.today()

    dias = [
        hoy - timedelta(days=4),
        hoy - timedelta(days=2),
        hoy
    ]

    resultado = Estadistica._calcular_rachas(dias)

    assert resultado == (1, 1)


def test_calcular_rachas_maxima_mayor_que_actual():
    hoy = date.today()

    dias = [
        hoy - timedelta(days=10),
        hoy - timedelta(days=9),
        hoy - timedelta(days=8),
        hoy - timedelta(days=5),
        hoy - timedelta(days=4),
        hoy - timedelta(days=3),
        hoy
    ]

    resultado = Estadistica._calcular_rachas(dias)

    assert resultado[0] == 1
    assert resultado[1] == 3


def test_calcular_rachas_termina_ayer():
    hoy = date.today()

    dias = [
        hoy - timedelta(days=3),
        hoy - timedelta(days=2),
        hoy - timedelta(days=1)
    ]

    resultado = Estadistica._calcular_rachas(dias)

    assert resultado == (3, 3)


def test_calcular_rachas_termina_anteayer():
    hoy = date.today()

    dias = [
        hoy - timedelta(days=2)
    ]

    resultado = Estadistica._calcular_rachas(dias)

    assert resultado == (0, 1)


def test_calcular_rachas_termina_en_fecha_antigua():
    hoy = date.today()

    dias = [
        hoy - timedelta(days=10),
        hoy - timedelta(days=9)
    ]

    resultado = Estadistica._calcular_rachas(dias)

    assert resultado[0] == 0
    assert resultado[1] == 2


def test_calcular_rachas_rompe_racha_y_crea_otra():
    hoy = date.today()

    dias = [
        hoy - timedelta(days=8),
        hoy - timedelta(days=7),
        hoy - timedelta(days=6),
        hoy - timedelta(days=3),
        hoy - timedelta(days=2),
        hoy - timedelta(days=1),
        hoy
    ]

    resultado = Estadistica._calcular_rachas(dias)

    assert resultado[0] == 4
    assert resultado[1] == 4
def test_calcular_rachas_varias_rachas():
    hoy = date.today()

    dias = [
        hoy - timedelta(days=10),
        hoy - timedelta(days=9),
        hoy - timedelta(days=5),
        hoy - timedelta(days=4),
        hoy - timedelta(days=3),
        hoy
    ]

    resultado = Estadistica._calcular_rachas(dias)

    assert resultado[0] == 1
    assert resultado[1] == 3


# ============================================================
# CONSULTAR
# ============================================================

@patch("models.estadistica.obtener_conexion")
def test_consultar(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    hoy = date.today()

    cursor.fetchone.side_effect = [
        {
            "total_paginas": 500,
            "total_minutos": 180,
            "tiempo_promedio": 30
        },
        {
            "libros_leidos": 4
        },
        {
            "como_te_sientes": "feliz",
            "freq": 3
        }
    ]

    cursor.fetchall.side_effect = [
        [
            {"contenido": "palabra1, palabra2, palabra3"},
            {"contenido": "palabra4, palabra5"}
        ],
        [
            {"genero": "Fantasía, Aventura"},
            {"genero": "Fantasía, Romance"},
            {"genero": "Aventura"}
        ],
        [
            {"dia": hoy - timedelta(days=1)},
            {"dia": hoy}
        ]
    ]

    resultado = Estadistica.consultar(1)

    assert resultado["total_paginas"] == 500
    assert resultado["total_minutos"] == 180
    assert resultado["tiempo_promedio"] == "30.0 Min"
    assert resultado["tiempo_total_formateado"] == "3.0 h"

    assert resultado["palabras_nuevas"] == 5
    assert resultado["libros_leidos"] == 4

    assert resultado["animo"] == "feliz"

    assert resultado["generos_top"] == [
        "Fantasía",
        "Aventura",
        "Romance"
    ]

    assert resultado["racha_actual"] == 2
    assert resultado["racha_maxima"] == 2

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.estadistica.obtener_conexion")
def test_consultar_sin_datos(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.side_effect = [
        {
            "total_paginas": 0,
            "total_minutos": 0,
            "tiempo_promedio": 0
        },
        {
            "libros_leidos": 0
        },
        None
    ]

    cursor.fetchall.side_effect = [
        [],
        [],
        []
    ]

    resultado = Estadistica.consultar(1)

    assert resultado["total_paginas"] == 0
    assert resultado["total_minutos"] == 0
    assert resultado["tiempo_promedio"] == "0 s"
    assert resultado["tiempo_total_formateado"] == "0 s"

    assert resultado["palabras_nuevas"] == 0
    assert resultado["libros_leidos"] == 0

    assert resultado["animo"] == "Sin datos"
    assert resultado["generos_top"] == []

    assert resultado["racha_actual"] == 0
    assert resultado["racha_maxima"] == 0


@patch("models.estadistica.obtener_conexion")
def test_consultar_palabras_con_contenido_vacio(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.side_effect = [
        {
            "total_paginas": 100,
            "total_minutos": 30,
            "tiempo_promedio": 15
        },
        {
            "libros_leidos": 1
        },
        None
    ]

    cursor.fetchall.side_effect = [
        [
            {"contenido": ""},
            {"contenido": None},
            {"contenido": "   "},
            {"contenido": "palabra1, palabra2"}
        ],
        [],
        []
    ]

    resultado = Estadistica.consultar(1)

    assert resultado["palabras_nuevas"] == 2
@patch("models.estadistica.obtener_conexion")
def test_consultar_palabras_con_espacios(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.side_effect = [
        {
            "total_paginas": 100,
            "total_minutos": 30,
            "tiempo_promedio": 15
        },
        {
            "libros_leidos": 1
        },
        None
    ]

    cursor.fetchall.side_effect = [
        [
            {
                "contenido":
                    " palabra1 , palabra2 ,   , palabra3 "
            }
        ],
        [],
        []
    ]

    resultado = Estadistica.consultar(1)

    assert resultado["palabras_nuevas"] == 3


@patch("models.estadistica.obtener_conexion")
def test_consultar_generos_repetidos(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.side_effect = [
        {
            "total_paginas": 100,
            "total_minutos": 60,
            "tiempo_promedio": 20
        },
        {
            "libros_leidos": 3
        },
        None
    ]

    cursor.fetchall.side_effect = [
        [],
        [
            {"genero": "Fantasía"},
            {"genero": "Fantasía"},
            {"genero": "Fantasía"},
            {"genero": "Romance"},
            {"genero": "Romance"},
            {"genero": "Misterio"},
            {"genero": "Ciencia ficción"}
        ],
        []
    ]

    resultado = Estadistica.consultar(1)

    assert resultado["generos_top"] == [
        "Fantasía",
        "Romance",
        "Misterio"
    ]


@patch("models.estadistica.obtener_conexion")
def test_consultar_generos_separados_por_comas(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.side_effect = [
        {
            "total_paginas": 100,
            "total_minutos": 60,
            "tiempo_promedio": 20
        },
        {
            "libros_leidos": 3
        },
        None
    ]

    cursor.fetchall.side_effect = [
        [],
        [
            {
                "genero":
                    "Fantasía, Aventura, Romance"
            },
            {
                "genero":
                    "Fantasía, Misterio"
            }
        ],
        []
    ]

    resultado = Estadistica.consultar(1)

    assert resultado["generos_top"][0] == "Fantasía"
    assert "Aventura" in resultado["generos_top"]
    assert "Romance" in resultado["generos_top"]


@patch("models.estadistica.obtener_conexion")
def test_consultar_maximo_tres_generos(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.side_effect = [
        {
            "total_paginas": 100,
            "total_minutos": 60,
            "tiempo_promedio": 20
        },
        {
            "libros_leidos": 5
        },
        None
    ]

    cursor.fetchall.side_effect = [
        [],
        [
            {"genero": "Fantasía"},
            {"genero": "Romance"},
            {"genero": "Misterio"},
            {"genero": "Terror"},
            {"genero": "Historia"},
        ],
        []
    ]

    resultado = Estadistica.consultar(1)

    assert len(resultado["generos_top"]) == 3


@patch("models.estadistica.obtener_conexion")
def test_consultar_animo_mas_frecuente(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor
    cursor.fetchone.side_effect = [
        {
            "total_paginas": 200,
            "total_minutos": 100,
            "tiempo_promedio": 25
        },
        {
            "libros_leidos": 2
        },
        {
            "como_te_sientes": "reflexivo",
            "freq": 10
        }
    ]

    cursor.fetchall.side_effect = [
        [],
        [],
        []
    ]

    resultado = Estadistica.consultar(1)

    assert resultado["animo"] == "reflexivo"


@patch("models.estadistica.obtener_conexion")
def test_consultar_animo_sin_registro(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.side_effect = [
        {
            "total_paginas": 0,
            "total_minutos": 0,
            "tiempo_promedio": 0
        },
        {
            "libros_leidos": 0
        },
        None
    ]

    cursor.fetchall.side_effect = [
        [],
        [],
        []
    ]

    resultado = Estadistica.consultar(1)

    assert resultado["animo"] == "Sin datos"


@patch("models.estadistica.obtener_conexion")
def test_consultar_fechas_no_consecutivas(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    hoy = date.today()

    cursor.fetchone.side_effect = [
        {
            "total_paginas": 300,
            "total_minutos": 120,
            "tiempo_promedio": 40
        },
        {
            "libros_leidos": 3
        },
        {
            "como_te_sientes": "feliz",
            "freq": 1
        }
    ]

    cursor.fetchall.side_effect = [
        [],
        [],
        [
            {"dia": hoy - timedelta(days=5)},
            {"dia": hoy - timedelta(days=2)},
            {"dia": hoy}
        ]
    ]

    resultado = Estadistica.consultar(1)

    assert resultado["racha_actual"] == 1
    assert resultado["racha_maxima"] == 1


@patch("models.estadistica.obtener_conexion")
def test_consultar_tiempo_en_segundos(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.side_effect = [
        {
            "total_paginas": 10,
            "total_minutos": 0.5,
            "tiempo_promedio": 0.25
        },
        {
            "libros_leidos": 1
        },
        None
    ]

    cursor.fetchall.side_effect = [
        [],
        [],
        []
    ]

    resultado = Estadistica.consultar(1)

    assert resultado["tiempo_promedio"] == "15 s"
    assert resultado["tiempo_total_formateado"] == "30 s"


@patch("models.estadistica.obtener_conexion")
def test_consultar_tiempo_en_horas(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.side_effect = [
        {
            "total_paginas": 1000,
            "total_minutos": 180,
            "tiempo_promedio": 90
        },
        {
            "libros_leidos": 10
        },
        None
    ]

    cursor.fetchall.side_effect = [
        [],
        [],
        []
    ]

    resultado = Estadistica.consultar(1)

    assert resultado["tiempo_promedio"] == "1.5 h"
    assert resultado["tiempo_total_formateado"] == "3.0 h"


# ============================================================
# COMPROBACIONES DE CONEXIÓN
# ============================================================

@patch("models.estadistica.obtener_conexion")
def test_consultar_cierra_conexion(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor
    cursor.fetchone.side_effect = [
        {
            "total_paginas": 0,
            "total_minutos": 0,
            "tiempo_promedio": 0
        },
        {
            "libros_leidos": 0
        },
        None
    ]

    cursor.fetchall.side_effect = [
        [],
        [],
        []
    ]

    Estadistica.consultar(1)

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()