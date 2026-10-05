from unittest.mock import MagicMock, patch

from IA.RecomendadorInicial import RecomendacionInicial


# ============================================================
# OBTENER DATOS DE ENCUESTA
# ============================================================

@patch("IA.RecomendadorInicial.db.obtener_conexion")
def test_obtener_datos_encuesta(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    datos = [
        {
            "nivel_actual": "intermedio",
            "id_pregunta": 1,
            "texto_pregunta": "¿Qué género te gusta?",
            "nombre_campo": "genero",
            "respuesta": "Fantasía"
        }
    ]

    cursor.fetchall.return_value = datos

    resultado = RecomendacionInicial.obtener_datos_encuesta(1)

    assert resultado == datos

    conexion.cursor.assert_called_once_with(dictionary=True)

    cursor.execute.assert_called_once()

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("IA.RecomendadorInicial.db.obtener_conexion")
def test_obtener_datos_encuesta_sin_resultados(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor
    cursor.fetchall.return_value = []

    resultado = RecomendacionInicial.obtener_datos_encuesta(1)

    assert resultado == []

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


# ============================================================
# YA GENERADA
# ============================================================

@patch("IA.RecomendadorInicial.db.obtener_conexion")
def test_ya_generada_true(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = (1,)

    resultado = RecomendacionInicial.ya_generada(1)

    assert resultado is True

    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("IA.RecomendadorInicial.db.obtener_conexion")
def test_ya_generada_false_cero(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = (0,)

    resultado = RecomendacionInicial.ya_generada(1)

    assert resultado is False


@patch("IA.RecomendadorInicial.db.obtener_conexion")
def test_ya_generada_sin_usuario(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = None

    resultado = RecomendacionInicial.ya_generada(1)

    assert resultado is False


# ============================================================
# GENERAR - SIN ENCUESTA
# ============================================================

@patch.object(
    RecomendacionInicial,
    "obtener_datos_encuesta"
)
def test_generar_sin_datos_encuesta(mock_encuesta):
    mock_encuesta.return_value = []

    resultado = RecomendacionInicial.generar(1)

    assert resultado is False


# ============================================================
# GENERAR - ERROR DE GEMINI
# ============================================================

@patch("IA.RecomendadorInicial.OrquestadorIA")
@patch.object(
    RecomendacionInicial,
    "obtener_datos_encuesta"
)
def test_generar_error_gemini(
    mock_encuesta,
    mock_orquestador
):
    mock_encuesta.return_value = [
        {
            "nivel_actual": "principiante",
            "id_pregunta": 1,
            "texto_pregunta": "¿Qué género te gusta?",
            "nombre_campo": "genero",
            "respuesta": "Fantasía"
        }
    ]

    ia = MagicMock()
    ia.generar_json.side_effect = Exception("Error Gemini")

    mock_orquestador.return_value = ia
    resultado = RecomendacionInicial.generar(1)

    assert resultado is False

    ia.generar_json.assert_called_once()


# ============================================================
# GENERAR - JSON NO ES DICCIONARIO
# ============================================================

@patch("IA.RecomendadorInicial.OrquestadorIA")
@patch.object(
    RecomendacionInicial,
    "obtener_datos_encuesta"
)
def test_generar_resultado_no_es_diccionario(
    mock_encuesta,
    mock_orquestador
):
    mock_encuesta.return_value = [
        {
            "nivel_actual": "principiante",
            "id_pregunta": 1,
            "texto_pregunta": "¿Qué género te gusta?",
            "nombre_campo": "genero",
            "respuesta": "Fantasía"
        }
    ]

    ia = MagicMock()
    ia.generar_json.return_value = ["esto", "no", "es", "un", "dict"]

    mock_orquestador.return_value = ia

    resultado = RecomendacionInicial.generar(1)

    assert resultado is False


# ============================================================
# GENERAR - NO EXISTE LA CLAVE LIBROS
# ============================================================

@patch("IA.RecomendadorInicial.OrquestadorIA")
@patch.object(
    RecomendacionInicial,
    "obtener_datos_encuesta"
)
def test_generar_sin_clave_libros(
    mock_encuesta,
    mock_orquestador
):
    mock_encuesta.return_value = [
        {
            "nivel_actual": "principiante",
            "id_pregunta": 1,
            "texto_pregunta": "¿Qué género te gusta?",
            "nombre_campo": "genero",
            "respuesta": "Fantasía"
        }
    ]

    ia = MagicMock()
    ia.generar_json.return_value = {}

    mock_orquestador.return_value = ia

    resultado = RecomendacionInicial.generar(1)

    assert resultado is False


# ============================================================
# GENERAR - LIBROS NO ES LISTA
# ============================================================

@patch("IA.RecomendadorInicial.OrquestadorIA")
@patch.object(
    RecomendacionInicial,
    "obtener_datos_encuesta"
)
def test_generar_libros_no_es_lista(
    mock_encuesta,
    mock_orquestador
):
    mock_encuesta.return_value = [
        {
            "nivel_actual": "intermedio",
            "id_pregunta": 1,
            "texto_pregunta": "¿Qué género te gusta?",
            "nombre_campo": "genero",
            "respuesta": "Fantasía"
        }
    ]

    ia = MagicMock()
    ia.generar_json.return_value = {
        "libros": "no es una lista"
    }

    mock_orquestador.return_value = ia

    resultado = RecomendacionInicial.generar(1)

    assert resultado is False


# ============================================================
# GENERAR - NO SON EXACTAMENTE 5 LIBROS
# ============================================================

@patch("IA.RecomendadorInicial.OrquestadorIA")
@patch.object(
    RecomendacionInicial,
    "obtener_datos_encuesta"
)
def test_generar_cinco_libros_no_exactos(
    mock_encuesta,
    mock_orquestador
):
    mock_encuesta.return_value = [
        {
            "nivel_actual": "intermedio",
            "id_pregunta": 1,
            "texto_pregunta": "¿Qué género te gusta?",
            "nombre_campo": "genero",
            "respuesta": "Fantasía"
        }
    ]

    ia = MagicMock()

    ia.generar_json.return_value = {
        "libros": [
            {
                "titulo": "Libro 1",
                "autor": "Autor 1"
            },
            {
                "titulo": "Libro 2",
                "autor": "Autor 2"
            }
        ]
    }

    mock_orquestador.return_value = ia

    resultado = RecomendacionInicial.generar(1)

    assert resultado is False


# ============================================================
# GENERAR - ERROR BUSCANDO LIBROS
# ============================================================
@patch("IA.RecomendadorInicial.motor.buscar_libros")
@patch("IA.RecomendadorInicial.OrquestadorIA")
@patch.object(
    RecomendacionInicial,
    "obtener_datos_encuesta"
)
def test_generar_error_buscar_libros(
    mock_encuesta,
    mock_orquestador,
    mock_buscar
):
    mock_encuesta.return_value = [
        {
            "nivel_actual": "intermedio",
            "id_pregunta": 1,
            "texto_pregunta": "¿Qué género te gusta?",
            "nombre_campo": "genero",
            "respuesta": "Fantasía"
        }
    ]

    libros_ia = [
        {"titulo": "Libro 1", "autor": "Autor 1"},
        {"titulo": "Libro 2", "autor": "Autor 2"},
        {"titulo": "Libro 3", "autor": "Autor 3"},
        {"titulo": "Libro 4", "autor": "Autor 4"},
        {"titulo": "Libro 5", "autor": "Autor 5"},
    ]

    ia = MagicMock()
    ia.generar_json.return_value = {
        "libros": libros_ia
    }

    mock_orquestador.return_value = ia

    mock_buscar.side_effect = Exception(
        "Error Google Books"
    )

    resultado = RecomendacionInicial.generar(1)

    assert resultado is False


# ============================================================
# GENERAR - NO ENCUENTRA LIBROS
# ============================================================

@patch("IA.RecomendadorInicial.motor.buscar_libros")
@patch("IA.RecomendadorInicial.OrquestadorIA")
@patch.object(
    RecomendacionInicial,
    "obtener_datos_encuesta"
)
def test_generar_sin_libros_encontrados(
    mock_encuesta,
    mock_orquestador,
    mock_buscar
):
    mock_encuesta.return_value = [
        {
            "nivel_actual": "intermedio",
            "id_pregunta": 1,
            "texto_pregunta": "¿Qué género te gusta?",
            "nombre_campo": "genero",
            "respuesta": "Fantasía"
        }
    ]

    libros_ia = [
        {"titulo": "Libro 1", "autor": "Autor 1"},
        {"titulo": "Libro 2", "autor": "Autor 2"},
        {"titulo": "Libro 3", "autor": "Autor 3"},
        {"titulo": "Libro 4", "autor": "Autor 4"},
        {"titulo": "Libro 5", "autor": "Autor 5"},
    ]

    ia = MagicMock()
    ia.generar_json.return_value = {
        "libros": libros_ia
    }

    mock_orquestador.return_value = ia
    mock_buscar.return_value = []

    resultado = RecomendacionInicial.generar(1)

    assert resultado is False


# ============================================================
# GENERAR - LIBRO CON ESTRUCTURA INVÁLIDA
# ============================================================

@patch("IA.RecomendadorInicial.motor.buscar_libros")
@patch("IA.RecomendadorInicial.OrquestadorIA")
@patch.object(
    RecomendacionInicial,
    "obtener_datos_encuesta"
)
def test_generar_libro_no_es_diccionario(
    mock_encuesta,
    mock_orquestador,
    mock_buscar
):
    mock_encuesta.return_value = [
        {
            "nivel_actual": "intermedio",
            "id_pregunta": 1,
            "texto_pregunta": "¿Qué género te gusta?",
            "nombre_campo": "genero",
            "respuesta": "Fantasía"
        }
    ]

    libros_ia = [
        {"titulo": "Libro 1", "autor": "Autor 1"},
        {"titulo": "Libro 2", "autor": "Autor 2"},
        {"titulo": "Libro 3", "autor": "Autor 3"},
        {"titulo": "Libro 4", "autor": "Autor 4"},
        {"titulo": "Libro 5", "autor": "Autor 5"},
    ]

    ia = MagicMock()
    ia.generar_json.return_value = {
        "libros": libros_ia
    }

    mock_orquestador.return_value = ia

    mock_buscar.return_value = [
        "esto no es un diccionario"
    ]

    resultado = RecomendacionInicial.generar(1)

    assert resultado is False


# ============================================================
# GENERAR - FALTA TÍTULO
# ============================================================

@patch("IA.RecomendadorInicial.motor.buscar_libros")
@patch("IA.RecomendadorInicial.OrquestadorIA")
@patch.object(
    RecomendacionInicial,
    "obtener_datos_encuesta"
)
def test_generar_libro_sin_titulo(
    mock_encuesta,
    mock_orquestador,
    mock_buscar
):
    mock_encuesta.return_value = [
        {
            "nivel_actual": "intermedio",
            "id_pregunta": 1,
            "texto_pregunta": "¿Qué género te gusta?",
            "nombre_campo": "genero",
            "respuesta": "Fantasía"
        }
    ]

    libros_ia = [
        {"titulo": "Libro 1", "autor": "Autor 1"},
        {"titulo": "Libro 2", "autor": "Autor 2"},
        {"titulo": "Libro 3", "autor": "Autor 3"},
        {"titulo": "Libro 4", "autor": "Autor 4"},
        {"titulo": "Libro 5", "autor": "Autor 5"},
    ]

    ia = MagicMock()
    ia.generar_json.return_value = {
        "libros": libros_ia
    }

    mock_orquestador.return_value = ia

    mock_buscar.return_value = [
        {
            "titulo": "",
            "autor": "Autor"
        }
    ]

    resultado = RecomendacionInicial.generar(1)

    assert resultado is False


# ============================================================
# GENERAR - FALTA AUTOR
# ============================================================

@patch("IA.RecomendadorInicial.motor.buscar_libros")
@patch("IA.RecomendadorInicial.OrquestadorIA")
@patch.object(
    RecomendacionInicial,
    "obtener_datos_encuesta"
)
def test_generar_libro_sin_autor(
    mock_encuesta,
    mock_orquestador,
    mock_buscar
):
    mock_encuesta.return_value = [
        {
            "nivel_actual": "intermedio",
            "id_pregunta": 1,
            "texto_pregunta": "¿Qué género te gusta?",
            "nombre_campo": "genero",
            "respuesta": "Fantasía"
        }
    ]

    libros_ia = [
        {"titulo": "Libro 1", "autor": "Autor 1"},
        {"titulo": "Libro 2", "autor": "Autor 2"},
        {"titulo": "Libro 3", "autor": "Autor 3"},
        {"titulo": "Libro 4", "autor": "Autor 4"},
        {"titulo": "Libro 5", "autor": "Autor 5"},
    ]

    ia = MagicMock()
    ia.generar_json.return_value = {
        "libros": libros_ia
    }

    mock_orquestador.return_value = ia

    mock_buscar.return_value = [
        {
            "titulo": "Libro",
            "autor": ""
        }
    ]

    resultado = RecomendacionInicial.generar(1)

    assert resultado is False


# ============================================================
# GENERAR - GUARDAR RECOMENDACIONES FALLA
# ============================================================

@patch("IA.RecomendadorInicial.db.guardar_recomendaciones")
@patch("IA.RecomendadorInicial.motor.buscar_libros")
@patch("IA.RecomendadorInicial.OrquestadorIA")
@patch.object(
    RecomendacionInicial,
    "obtener_datos_encuesta"
)
def test_generar_error_guardando_recomendaciones(
    mock_encuesta,
    mock_orquestador,
    mock_buscar,
    mock_guardar
):
    mock_encuesta.return_value = [
        {
            "nivel_actual": "intermedio",
            "id_pregunta": 1,
            "texto_pregunta": "¿Qué género te gusta?",
            "nombre_campo": "genero",
            "respuesta": "Fantasía"
        }
    ]

    libros_ia = [
        {"titulo": "Libro 1", "autor": "Autor 1"},
        {"titulo": "Libro 2", "autor": "Autor 2"},
        {"titulo": "Libro 3", "autor": "Autor 3"},
        {"titulo": "Libro 4", "autor": "Autor 4"},
        {"titulo": "Libro 5", "autor": "Autor 5"},
    ]

    libros_completos = [
        {
            "titulo": "Libro 1",
            "autor": "Autor 1"
        },
        {
            "titulo": "Libro 2",
            "autor": "Autor 2"
        },
        {
            "titulo": "Libro 3",
            "autor": "Autor 3"
        },
        {
            "titulo": "Libro 4",
            "autor": "Autor 4"
        },
        {
            "titulo": "Libro 5",
            "autor": "Autor 5"
        }
    ]

    ia = MagicMock()
    ia.generar_json.return_value = {
        "libros": libros_ia
    }

    mock_orquestador.return_value = ia
    mock_buscar.return_value = libros_completos
    mock_guardar.side_effect = Exception(
        "Error de base de datos"
    )

    resultado = RecomendacionInicial.generar(1)

    assert resultado is False


# ============================================================
# GENERAR - ÉXITO
# ============================================================

@patch.object(
    RecomendacionInicial,
    "marcar_generada"
)
@patch("IA.RecomendadorInicial.db.guardar_recomendaciones")
@patch("IA.RecomendadorInicial.motor.buscar_libros")
@patch("IA.RecomendadorInicial.OrquestadorIA")
@patch.object(
    RecomendacionInicial,
    "obtener_datos_encuesta"
)
def test_generar_exitosamente(
    mock_encuesta,
    mock_orquestador,
    mock_buscar,
    mock_guardar,
    mock_marcar
):
    datos_encuesta = [
        {
            "nivel_actual": "intermedio",
            "id_pregunta": 1,
            "texto_pregunta": "¿Qué género te gusta?",
            "nombre_campo": "genero",
            "respuesta": "Fantasía"
        },
        {
            "nivel_actual": "intermedio",
            "id_pregunta": 2,
            "texto_pregunta": "¿Qué formato prefieres?",
            "nombre_campo": "formato",
            "respuesta": "Físico"
        }
    ]

    libros_ia = [
        {"titulo": "Libro 1", "autor": "Autor 1"},
        {"titulo": "Libro 2", "autor": "Autor 2"},
        {"titulo": "Libro 3", "autor": "Autor 3"},
        {"titulo": "Libro 4", "autor": "Autor 4"},
        {"titulo": "Libro 5", "autor": "Autor 5"},
    ]

    libros_completos = [
        {
            "titulo": "Libro 1",
            "autor": "Autor 1"
        },
        {
            "titulo": "Libro 2",
            "autor": "Autor 2"
        },
        {
            "titulo": "Libro 3",
            "autor": "Autor 3"
        },
        {
            "titulo": "Libro 4",
            "autor": "Autor 4"
        },
        {
            "titulo": "Libro 5",
            "autor": "Autor 5"
        }
    ]

    mock_encuesta.return_value = datos_encuesta

    ia = MagicMock()
    ia.generar_json.return_value = {
        "libros": libros_ia
    }

    mock_orquestador.return_value = ia
    mock_buscar.return_value = libros_completos

    resultado = RecomendacionInicial.generar(1)

    assert resultado is True

    mock_encuesta.assert_called_once_with(1)

    ia.generar_json.assert_called_once()

    mock_buscar.assert_called_once_with(libros_ia)

    mock_guardar.assert_called_once_with(
        1,
        libros_completos
    )

    mock_marcar.assert_called_once_with(1)


# ============================================================
# MARCAR COMO GENERADA
# ============================================================

@patch("IA.RecomendadorInicial.db.obtener_conexion")
def test_marcar_generada(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    RecomendacionInicial.marcar_generada(1)

    cursor.execute.assert_called_once()
    conexion.commit.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()