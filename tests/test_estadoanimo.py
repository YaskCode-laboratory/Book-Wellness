import pytest
from unittest.mock import MagicMock, patch

from IA.EstadoAnimo import EstadoAnimo


# ==========================================================
# guardar
# ==========================================================

@patch("IA.EstadoAnimo.obtener_conexion")
def test_guardar(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    EstadoAnimo.guardar(1, "feliz")

    cursor.execute.assert_called_once()
    conexion.commit.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


# ==========================================================
# obtener_actual
# ==========================================================

@patch("IA.EstadoAnimo.obtener_conexion")
def test_obtener_actual(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = {
        "estado_animo": "feliz",
        "fecha_hora": "2026-10-05"
    }

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    resultado = EstadoAnimo.obtener_actual(1)

    assert resultado["estado_animo"] == "feliz"
    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


# ==========================================================
# obtener_libro_leyendo
# ==========================================================

@patch("IA.EstadoAnimo.random.choice")
@patch("IA.EstadoAnimo.Libro.obtener_libros_usuario")
def test_obtener_libro_leyendo_con_libros(mock_obtener, mock_choice):
    libros = [
        {"titulo": "Libro 1"},
        {"titulo": "Libro 2"}
    ]

    mock_obtener.return_value = libros
    mock_choice.return_value = libros[0]

    resultado = EstadoAnimo.obtener_libro_leyendo(1)

    mock_obtener.assert_called_once_with(1, "leyendo")
    mock_choice.assert_called_once_with(libros)
    assert resultado == libros[0]


@patch("IA.EstadoAnimo.Libro.obtener_libros_usuario")
def test_obtener_libro_leyendo_sin_libros(mock_obtener):
    mock_obtener.return_value = []

    resultado = EstadoAnimo.obtener_libro_leyendo(1)

    assert resultado is None


# ==========================================================
# obtener_libro_pendiente
# ==========================================================

@patch("IA.EstadoAnimo.random.choice")
@patch("IA.EstadoAnimo.Libro.obtener_libros_usuario")
def test_obtener_libro_pendiente_con_libros(mock_obtener, mock_choice):
    libros = [
        {"titulo": "Pendiente 1"},
        {"titulo": "Pendiente 2"}
    ]

    mock_obtener.return_value = libros
    mock_choice.return_value = libros[0]

    resultado = EstadoAnimo.obtener_libro_pendiente(1)

    mock_obtener.assert_called_once_with(1, "pendiente")
    mock_choice.assert_called_once_with(libros)
    assert resultado == libros[0]


@patch("IA.EstadoAnimo.Libro.obtener_libros_usuario")
def test_obtener_libro_pendiente_sin_libros(mock_obtener):
    mock_obtener.return_value = []

    resultado = EstadoAnimo.obtener_libro_pendiente(1)

    assert resultado is None


# ==========================================================
# obtener_libro_reflexivo
# ==========================================================

@patch("IA.EstadoAnimo.obtener_conexion")
def test_obtener_libro_reflexivo_encuentra_libro(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = [
        {
            "titulo": "Introducción a la filosofía",
            "genero": "Filosofía"
        }
    ]

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    resultado = EstadoAnimo.obtener_libro_reflexivo(1)

    assert resultado["titulo"] == "Introducción a la filosofía"
    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()

@patch("IA.EstadoAnimo.obtener_conexion")
def test_obtener_libro_reflexivo_no_encuentra(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = [
        {
            "titulo": "Romance juvenil",
            "genero": "Romance"
        }
    ]

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    resultado = EstadoAnimo.obtener_libro_reflexivo(1)

    assert resultado is None


# ==========================================================
# obtener_libro_sorprendido
# ==========================================================

@patch("IA.EstadoAnimo.obtener_conexion")
def test_obtener_libro_sorprendido_encuentra_libro(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = [
        {
            "titulo": "El mundo fantástico",
            "genero": "Fantasía"
        }
    ]

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    resultado = EstadoAnimo.obtener_libro_sorprendido(1)

    assert resultado["titulo"] == "El mundo fantástico"


@patch("IA.EstadoAnimo.obtener_conexion")
def test_obtener_libro_sorprendido_no_encuentra(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = [
        {
            "titulo": "Libro romántico",
            "genero": "Romance"
        }
    ]

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    resultado = EstadoAnimo.obtener_libro_sorprendido(1)

    assert resultado is None


# ==========================================================
# obtener_libro_ansioso
# ==========================================================

@patch("IA.EstadoAnimo.obtener_conexion")
def test_obtener_libro_ansioso_encuentra_libro(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = [
        {
            "titulo": "Una historia de fantasía",
            "genero": "Fantasía"
        }
    ]

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    resultado = EstadoAnimo.obtener_libro_ansioso(1)

    assert resultado["titulo"] == "Una historia de fantasía"


@patch("IA.EstadoAnimo.obtener_conexion")
def test_obtener_libro_ansioso_excluye_terror(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = [
        {
            "titulo": "La casa del terror",
            "genero": "Terror"
        }
    ]

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    resultado = EstadoAnimo.obtener_libro_ansioso(1)

    assert resultado is None


@patch("IA.EstadoAnimo.obtener_conexion")
def test_obtener_libro_ansioso_no_encuentra(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = [
        {
            "titulo": "Libro histórico",
            "genero": "Historia"
        }
    ]

    conexion.cursor.return_value = cursor
    mock_obtener_conexion.return_value = conexion

    resultado = EstadoAnimo.obtener_libro_ansioso(1)

    assert resultado is None


# ==========================================================
# responder_feliz
# ==========================================================

@patch("IA.EstadoAnimo.guardar_mensaje")
@patch("IA.EstadoAnimo.random.choice")
@patch.object(
    EstadoAnimo,
    "obtener_libro_leyendo"
)
def test_responder_feliz_con_libro(
    mock_libro,
    mock_choice,
    mock_guardar
):
    mock_libro.return_value = {
        "titulo": "Harry Potter"
    }

    mock_choice.return_value = "¡Qué bien que estás leyendo {libro}!"

    resultado = EstadoAnimo.responder_feliz(1)

    assert resultado == "¡Qué bien que estás leyendo Harry Potter!"

    mock_guardar.assert_called_once_with(
        1,
        "ia",
        "¡Qué bien que estás leyendo Harry Potter!"
    )

@patch("IA.EstadoAnimo.guardar_mensaje")
@patch("IA.EstadoAnimo.random.choice")
@patch.object(
    EstadoAnimo,
    "obtener_libro_leyendo"
)
def test_responder_feliz_sin_libro(
    mock_libro,
    mock_choice,
    mock_guardar
):
    mock_libro.return_value = None
    mock_choice.return_value = "¡Qué bueno verte feliz!"

    resultado = EstadoAnimo.responder_feliz(1)

    assert resultado == "¡Qué bueno verte feliz!"

    mock_guardar.assert_called_once_with(
        1,
        "ia",
        "¡Qué bueno verte feliz!"
    )


# ==========================================================
# responder_tranquilo
# ==========================================================

@patch("IA.EstadoAnimo.OrquestadorIA")
@patch.object(EstadoAnimo, "obtener_libro_pendiente")
@patch.object(EstadoAnimo, "obtener_libro_leyendo")
def test_responder_tranquilo_con_libro_leyendo(
    mock_leyendo,
    mock_pendiente,
    mock_ia
):
    mock_leyendo.return_value = {
        "titulo": "El Principito"
    }

    mock_pendiente.return_value = None

    instancia_ia = MagicMock()
    instancia_ia.generar_respuesta.return_value = "Disfruta tu lectura."
    mock_ia.return_value = instancia_ia

    resultado = EstadoAnimo.responder_tranquilo(1)

    assert resultado == "Disfruta tu lectura."

    instancia_ia.generar_respuesta.assert_called_once()


@patch("IA.EstadoAnimo.OrquestadorIA")
@patch.object(EstadoAnimo, "obtener_libro_pendiente")
@patch.object(EstadoAnimo, "obtener_libro_leyendo")
def test_responder_tranquilo_con_libro_pendiente(
    mock_leyendo,
    mock_pendiente,
    mock_ia
):
    mock_leyendo.return_value = None
    mock_pendiente.return_value = {
        "titulo": "1984"
    }

    instancia_ia = MagicMock()
    instancia_ia.generar_respuesta.return_value = "Lee con calma."
    mock_ia.return_value = instancia_ia

    resultado = EstadoAnimo.responder_tranquilo(1)

    assert resultado == "Lee con calma."


@patch("IA.EstadoAnimo.OrquestadorIA")
@patch.object(EstadoAnimo, "obtener_libro_pendiente")
@patch.object(EstadoAnimo, "obtener_libro_leyendo")
def test_responder_tranquilo_sin_libros(
    mock_leyendo,
    mock_pendiente,
    mock_ia
):
    mock_leyendo.return_value = None
    mock_pendiente.return_value = None

    instancia_ia = MagicMock()
    instancia_ia.generar_respuesta.return_value = "Tómate un momento para descansar."
    mock_ia.return_value = instancia_ia

    resultado = EstadoAnimo.responder_tranquilo(1)

    assert resultado == "Tómate un momento para descansar."


# ==========================================================
# responder_reflexivo
# ==========================================================

@patch("IA.EstadoAnimo.OrquestadorIA")
@patch.object(EstadoAnimo, "obtener_libro_reflexivo")
def test_responder_reflexivo_con_libro(
    mock_libro,
    mock_ia
):
    mock_libro.return_value = {
        "titulo": "El mundo de Sofía"
    }

    instancia_ia = MagicMock()
    instancia_ia.generar_respuesta.return_value = "Continúa descubriendo nuevas ideas."
    mock_ia.return_value = instancia_ia

    resultado = EstadoAnimo.responder_reflexivo(1)

    assert resultado == {
        "respuesta": "Continúa descubriendo nuevas ideas.",
        "recomendaciones": []
    }

    instancia_ia.generar_respuesta.assert_called_once()


@patch("IA.EstadoAnimo.db.guardar_mensaje")
@patch("IA.EstadoAnimo.db.guardar_recomendaciones")
@patch("IA.EstadoAnimo.motor.recomendar")
@patch.object(EstadoAnimo, "obtener_libro_reflexivo")
def test_responder_reflexivo_sin_libro(
    mock_libro,
    mock_recomendar,
    mock_guardar_recomendaciones,
    mock_guardar_mensaje
):
    mock_libro.return_value = None

    recomendaciones = [
        {"titulo": "Libro 1"},
        {"titulo": "Libro 2"}
    ]

    mock_recomendar.return_value = {
        "mensaje": "Aquí tienes algunas recomendaciones.",
        "libros": recomendaciones
    }

    resultado = EstadoAnimo.responder_reflexivo(1)

    assert resultado["respuesta"] == "Aquí tienes algunas recomendaciones."
    assert resultado["recomendaciones"] == recomendaciones
    mock_recomendar.assert_called_once_with(
        1,
        devolver_mensaje=True,
        tipo="reflexivo"
    )

    mock_guardar_recomendaciones.assert_called_once_with(
        1,
        recomendaciones
    )

    mock_guardar_mensaje.assert_called_once_with(
        1,
        "ia",
        "Aquí tienes algunas recomendaciones."
    )


# ==========================================================
# responder_sorprendido
# ==========================================================

@patch("IA.EstadoAnimo.OrquestadorIA")
@patch.object(EstadoAnimo, "obtener_libro_sorprendido")
def test_responder_sorprendido_con_libro(
    mock_libro,
    mock_ia
):
    mock_libro.return_value = {
        "titulo": "Alicia en el país de las maravillas"
    }

    instancia_ia = MagicMock()
    instancia_ia.generar_respuesta.return_value = "Déjate sorprender."
    mock_ia.return_value = instancia_ia

    resultado = EstadoAnimo.responder_sorprendido(1)

    assert resultado == {
        "respuesta": "Déjate sorprender.",
        "recomendaciones": []
    }


@patch("IA.EstadoAnimo.db.guardar_mensaje")
@patch("IA.EstadoAnimo.db.guardar_recomendaciones")
@patch("IA.EstadoAnimo.motor.recomendar")
@patch.object(EstadoAnimo, "obtener_libro_sorprendido")
def test_responder_sorprendido_sin_libro(
    mock_libro,
    mock_recomendar,
    mock_guardar_recomendaciones,
    mock_guardar_mensaje
):
    mock_libro.return_value = None

    recomendaciones = [
        {"titulo": "Libro sorpresa"}
    ]

    mock_recomendar.return_value = {
        "mensaje": "Tengo algo que podría sorprenderte.",
        "libros": recomendaciones
    }

    resultado = EstadoAnimo.responder_sorprendido(1)

    assert resultado["respuesta"] == "Tengo algo que podría sorprenderte."
    assert resultado["recomendaciones"] == recomendaciones

    mock_recomendar.assert_called_once_with(
        1,
        devolver_mensaje=True,
        tipo="sorprendido"
    )

    mock_guardar_recomendaciones.assert_called_once_with(
        1,
        recomendaciones
    )

    mock_guardar_mensaje.assert_called_once_with(
        1,
        "ia",
        "Tengo algo que podría sorprenderte."
    )


# ==========================================================
# responder_ansioso
# ==========================================================

@patch("IA.EstadoAnimo.OrquestadorIA")
@patch.object(EstadoAnimo, "obtener_libro_ansioso")
def test_responder_ansioso_con_libro(
    mock_libro,
    mock_ia
):
    mock_libro.return_value = {
        "titulo": "Un libro tranquilo"
    }

    instancia_ia = MagicMock()
    instancia_ia.generar_respuesta.return_value = "Lee a tu propio ritmo."
    mock_ia.return_value = instancia_ia

    resultado = EstadoAnimo.responder_ansioso(1)

    assert resultado == {
        "respuesta": "Lee a tu propio ritmo.",
        "recomendaciones": []
    }


@patch("IA.EstadoAnimo.db.guardar_recomendaciones")
@patch("IA.EstadoAnimo.motor.recomendar")
@patch.object(EstadoAnimo, "obtener_libro_ansioso")
def test_responder_ansioso_sin_libro(
    mock_libro,
    mock_recomendar,
    mock_guardar_recomendaciones
):
    mock_libro.return_value = None

    recomendaciones = [
        {"titulo": "Libro relajante"}
    ]

    mock_recomendar.return_value = {
        "mensaje": "Aquí tienes algo ligero para leer.",
        "libros": recomendaciones
    }

    resultado = EstadoAnimo.responder_ansioso(1)

    assert resultado["respuesta"] == "Aquí tienes algo ligero para leer."
    assert resultado["recomendaciones"] == recomendaciones

    mock_recomendar.assert_called_once_with(
        1,
        devolver_mensaje=True,
        tipo="ansioso"
    )

    mock_guardar_recomendaciones.assert_called_once_with(
        1,
        recomendaciones
    )


# ==========================================================
# responder_triste
# ==========================================================

@patch("IA.EstadoAnimo.db.guardar_mensaje")
@patch("IA.EstadoAnimo.random.choice")
def test_responder_triste(mock_choice, mock_guardar):
    mock_choice.return_value = "Todo estará bien."
    resultado = EstadoAnimo.responder_triste(1)

    assert resultado == {
        "respuesta": "Todo estará bien.",
        "recomendaciones": []
    }

    mock_guardar.assert_called_once_with(
        1,
        "asistente",
        "Todo estará bien."
    )


# ==========================================================
# procesar_triste
# ==========================================================

@patch("IA.EstadoAnimo.motor.recomendar_triste")
@patch("IA.EstadoAnimo.db.guardar_mensaje")
def test_procesar_triste_estado_valido(
    mock_guardar,
    mock_recomendar
):
    mock_recomendar.return_value = {
        "estado": 3,
        "motivo": "El usuario se siente decaído.",
        "mensaje": "Te recomiendo algo que pueda acompañarte.",
        "libros": [
            {"titulo": "Libro 1"}
        ]
    }

    resultado = EstadoAnimo.procesar_triste(
        1,
        "Me siento mal."
    )

    assert resultado == {
        "respuesta": "Te recomiendo algo que pueda acompañarte.",
        "recomendaciones": [
            {"titulo": "Libro 1"}
        ],
        "estado_triste": 3
    }

    mock_guardar.assert_called_once_with(
        1,
        "usuario",
        "Me siento mal."
    )

    mock_recomendar.assert_called_once_with(
        1,
        "Me siento mal."
    )


@patch("IA.EstadoAnimo.motor.recomendar_triste")
@patch("IA.EstadoAnimo.db.guardar_mensaje")
def test_procesar_triste_estado_invalido(
    mock_guardar,
    mock_recomendar
):
    mock_recomendar.return_value = {
        "estado": 99,
        "motivo": "Motivo",
        "mensaje": "Respuesta",
        "libros": []
    }

    resultado = EstadoAnimo.procesar_triste(
        1,
        "Estoy triste."
    )

    assert resultado["estado_triste"] == 5


@patch("IA.EstadoAnimo.motor.recomendar_triste")
@patch("IA.EstadoAnimo.db.guardar_mensaje")
def test_procesar_triste_estado_no_numerico(
    mock_guardar,
    mock_recomendar
):
    mock_recomendar.return_value = {
        "estado": "abc",
        "motivo": "Motivo",
        "mensaje": "Respuesta",
        "libros": []
    }

    resultado = EstadoAnimo.procesar_triste(
        1,
        "Estoy triste."
    )

    assert resultado["estado_triste"] == 5


@patch("IA.EstadoAnimo.motor.recomendar_triste")
@patch("IA.EstadoAnimo.db.guardar_mensaje")
def test_procesar_triste_estado_none(
    mock_guardar,
    mock_recomendar
):
    mock_recomendar.return_value = {
        "estado": None,
        "motivo": "Motivo",
        "mensaje": "Respuesta",
        "libros": []
    }

    resultado = EstadoAnimo.procesar_triste(
        1,
        "Estoy triste."
    )

    assert resultado["estado_triste"] == 5