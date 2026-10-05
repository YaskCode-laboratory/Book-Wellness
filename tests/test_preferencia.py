from unittest.mock import MagicMock, patch

from models.Preferencias import Preferencias


def test_crear_preferencias():
    preferencias = Preferencias(
        id_usuario=1,
        nivel="principiante",
        respuestas={
            "genero": "Fantasía"
        }
    )

    assert preferencias.id_usuario == 1
    assert preferencias.nivel == "principiante"
    assert preferencias.respuestas["genero"] == "Fantasía"


@patch("models.Preferencias.obtener_conexion")
def test_obtener_usuario_pendiente(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = (15,)

    mock_obtener_conexion.return_value = conexion

    resultado = Preferencias.obtener_usuario_pendiente()

    assert resultado == 15

    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.Preferencias.obtener_conexion")
def test_obtener_usuario_pendiente_inexistente(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = None

    mock_obtener_conexion.return_value = conexion

    resultado = Preferencias.obtener_usuario_pendiente()

    assert resultado is None


@patch("models.Preferencias.obtener_conexion")
def test_obtener_preguntas(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    preguntas = [
        {
            "id_pregunta": 1,
            "nombre_campo": "genero"
        },
        {
            "id_pregunta": 2,
            "nombre_campo": "formato"
        }
    ]

    cursor.fetchall.return_value = preguntas

    mock_obtener_conexion.return_value = conexion

    resultado = Preferencias.obtener_preguntas("principiante")

    assert resultado == preguntas
    assert len(resultado) == 2

    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.Preferencias.Preferencias.obtener_preguntas")
@patch("models.Preferencias.obtener_conexion")
def test_guardar_respuestas(
    mock_obtener_conexion,
    mock_obtener_preguntas
):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    mock_obtener_conexion.return_value = conexion

    mock_obtener_preguntas.return_value = [
        {
            "id_pregunta": 1,
            "nombre_campo": "genero"
        },
        {
            "id_pregunta": 2,
            "nombre_campo": "autores"
        }
    ]

    preferencias = Preferencias(
        id_usuario=10,
        nivel="principiante",
        respuestas={
            "genero": "Fantasía",
            "autores": ["Autor 1", "Autor 2"]
        }
    )

    preferencias.guardar()

    assert cursor.execute.call_count == 2

    # Verifica que la lista se convierta en texto
    segunda_consulta = cursor.execute.call_args_list[1]
    parametros = segunda_consulta.args[1]

    assert parametros[0] == 10
    assert parametros[1] == 2
    assert parametros[2] == "Autor 1, Autor 2"

    conexion.commit.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.Preferencias.obtener_conexion")
def test_limpiar_usuario_pendiente(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    conexion.cursor.return_value = cursor

    mock_obtener_conexion.return_value = conexion

    Preferencias.limpiar_usuario_pendiente(10)

    cursor.execute.assert_called_once()
    conexion.commit.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()
