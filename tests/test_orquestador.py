import json
from unittest.mock import MagicMock, patch

from IA.orquestador import OrquestadorIA


# ============================================================
# CONFIGURACIÓN
# ============================================================

def crear_orquestador():
    return OrquestadorIA(
        api_key="test-api-key",
        modelo="gemini-test",
        timeout=10
    )


# ============================================================
# init
# ============================================================

def test_orquestador_inicializacion():

    orquestador = crear_orquestador()

    assert orquestador.api_key == "test-api-key"
    assert orquestador.timeout == 10
    assert "gemini-test:generateContent" in orquestador.url


def test_orquestador_usa_api_key_global():

    with patch(
        "IA.orquestador.API_KEY",
        "api-key-global"
    ):
        orquestador = OrquestadorIA()

    assert orquestador.api_key == "api-key-global"


# ============================================================
# construir_historial
# ============================================================

@patch("IA.orquestador.db.obtener_historial")
def test_construir_historial(mock_historial):

    mock_historial.return_value = [
        {
            "rol": "usuario",
            "mensaje": "Quiero leer fantasía"
        },
        {
            "rol": "asistente",
            "mensaje": "Puedes probar con El Hobbit"
        },
        {
            "rol": "usuario",
            "mensaje": "Gracias"
        }
    ]

    orquestador = crear_orquestador()

    resultado = orquestador.construir_historial(5)

    assert resultado == (
        "Usuario: Quiero leer fantasía\n\n"
        "Asistente: Puedes probar con El Hobbit\n\n"
        "Usuario: Gracias\n\n"
    )

    mock_historial.assert_called_once_with(5)


@patch("IA.orquestador.db.obtener_historial")
def test_construir_historial_vacio(mock_historial):

    mock_historial.return_value = []

    orquestador = crear_orquestador()

    resultado = orquestador.construir_historial(10)

    assert resultado == ""

    mock_historial.assert_called_once_with(10)


# ============================================================
# _consultar
# ============================================================

@patch("IA.orquestador.requests.post")
def test_consultar_correctamente(mock_post):

    mock_respuesta = MagicMock()

    mock_respuesta.status_code = 200

    mock_respuesta.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "Hola, soy AM."
                        }
                    ]
                }
            }
        ]
    }

    mock_post.return_value = mock_respuesta

    orquestador = crear_orquestador()

    resultado = orquestador._consultar("Hola")

    assert resultado == "Hola, soy AM."

    mock_post.assert_called_once_with(
        orquestador.url,
        params={
            "key": "test-api-key"
        },
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": "Hola"
                        }
                    ]
                }
            ]
        },
        timeout=10
    )

    mock_respuesta.raise_for_status.assert_called_once()


@patch("IA.orquestador.requests.post")
def test_consultar_reintenta_si_gemini_responde_503(
    mock_post
):

    respuesta_503 = MagicMock()
    respuesta_503.status_code = 503

    respuesta_ok = MagicMock()
    respuesta_ok.status_code = 200

    respuesta_ok.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "Respuesta correcta"
                        }
                    ]
                }
            }
        ]
    }

    mock_post.side_effect = [
        respuesta_503,
        respuesta_ok
    ]

    orquestador = crear_orquestador()
    with patch("IA.orquestador.time.sleep") as mock_sleep:

        resultado = orquestador._consultar("Hola")

    assert resultado == "Respuesta correcta"

    assert mock_post.call_count == 2

    mock_sleep.assert_called_once_with(1)


@patch("IA.orquestador.requests.post")
def test_consultar_503_tres_veces(
    mock_post
):

    respuesta_503 = MagicMock()
    respuesta_503.status_code = 503

    mock_post.return_value = respuesta_503

    orquestador = crear_orquestador()

    with patch("IA.orquestador.time.sleep") as mock_sleep:

        resultado = orquestador._consultar("Hola")

    assert resultado is None

    assert mock_post.call_count == 3

    assert mock_sleep.call_count == 2


# ============================================================
# generar_texto
# ============================================================

@patch("IA.orquestador.db.guardar_mensaje")
@patch("IA.orquestador.db.obtener_historial")
@patch.object(
    OrquestadorIA,
    "_consultar"
)
def test_generar_texto(
    mock_consultar,
    mock_historial,
    mock_guardar
):

    mock_historial.return_value = [
        {
            "rol": "usuario",
            "mensaje": "Hola"
        },
        {
            "rol": "asistente",
            "mensaje": "Hola, ¿cómo estás?"
        }
    ]

    mock_consultar.return_value = "Asistente: Estoy muy bien."

    orquestador = crear_orquestador()

    resultado = orquestador.generar_texto(
        7,
        "Eres un asistente de lectura.",
        "Recomiéndame un libro."
    )

    assert resultado == "Estoy muy bien."

    mock_consultar.assert_called_once_with(
        "Eres un asistente de lectura.\n\n"
        "Usuario: Hola\n\n"
        "Asistente: Hola, ¿cómo estás?\n\n"
        "Usuario: Recomiéndame un libro."
    )

    assert mock_guardar.call_count == 2

    mock_guardar.assert_any_call(
        7,
        "usuario",
        "Recomiéndame un libro."
    )

    mock_guardar.assert_any_call(
        7,
        "asistente",
        "Estoy muy bien."
    )


@patch("IA.orquestador.db.guardar_mensaje")
@patch("IA.orquestador.db.obtener_historial")
@patch.object(
    OrquestadorIA,
    "_consultar"
)
def test_generar_texto_sin_prefijo_asistente(
    mock_consultar,
    mock_historial,
    mock_guardar
):

    mock_historial.return_value = []

    mock_consultar.return_value = "Respuesta directa"

    orquestador = crear_orquestador()

    resultado = orquestador.generar_texto(
        1,
        "Prompt",
        "Mensaje"
    )

    assert resultado == "Respuesta directa"


# ============================================================
# generar_respuesta
# ============================================================

@patch("IA.orquestador.db.guardar_mensaje")
@patch("IA.orquestador.db.obtener_historial")
@patch.object(
    OrquestadorIA,
    "_consultar"
)
def test_generar_respuesta(
    mock_consultar,
    mock_historial,
    mock_guardar
):

    mock_historial.return_value = [
        {
            "rol": "usuario",
            "mensaje": "Hola"
        }
    ]

    mock_consultar.return_value = (
        "Asistente: Esta es mi respuesta."
    )

    orquestador = crear_orquestador()

    resultado = orquestador.generar_respuesta(
        3,
        "Ayúdame a elegir un libro."
    )

    assert resultado == "Esta es mi respuesta."

    mock_consultar.assert_called_once_with(
        "Usuario: Hola\n\n"
        "\n"
        "Ayúdame a elegir un libro."
    )

    mock_guardar.assert_called_once_with(
        3,
        "asistente",
        "Esta es mi respuesta."
    )


# ============================================================
# generar_json
# ============================================================

@patch.object(
    OrquestadorIA,
    "_consultar"
)
def test_generar_json_correctamente(mock_consultar):

    mock_consultar.return_value = (
        '{"titulo": "El Principito", "paginas": 96}'
    )

    orquestador = crear_orquestador()

    resultado = orquestador.generar_json(
        "Genera un libro en JSON."
    )
    assert resultado == {
        "titulo": "El Principito",
        "paginas": 96
    }


@patch.object(
    OrquestadorIA,
    "_consultar"
)
def test_generar_json_elimina_bloque_markdown(
    mock_consultar
):

    mock_consultar.return_value = (
        '`json\n{"titulo": "1984"}\n```'
    )

    orquestador = crear_orquestador()

    resultado = orquestador.generar_json(
        "Genera JSON."
    )

    assert resultado == {
        "titulo": "1984"
    }

    orquestador = crear_orquestador()

    resultado = orquestador.generar_json(
        "Genera JSON."
    )

    assert resultado == {
        "titulo": "1984"
    }


@patch.object(
    OrquestadorIA,
    "_consultar"
)
def test_generar_json_restablece_timeout(
    mock_consultar
):

    mock_consultar.return_value = (
        '{"ok": true}'
    )

    orquestador = crear_orquestador()

    timeout_original = orquestador.timeout

    resultado = orquestador.generar_json(
        "Genera JSON.",
        timeout=50
    )

    assert resultado == {
        "ok": True
    }

    assert orquestador.timeout == timeout_original


@patch.object(
    OrquestadorIA,
    "_consultar"
)
def test_generar_json_restablece_timeout_si_hay_error(
    mock_consultar
):

    mock_consultar.side_effect = ValueError(
        "JSON inválido"
    )

    orquestador = crear_orquestador()

    timeout_original = orquestador.timeout

    try:
        orquestador.generar_json(
            "Genera JSON.",
            timeout=50
        )
    except ValueError:
        pass

    assert orquestador.timeout == timeout_original