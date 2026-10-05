from unittest.mock import MagicMock, patch

import requests

from routes.utilidades import obtener_json


# ============================================================
# obtener_json
# ============================================================

@patch("routes.utilidades.requests.get")
def test_obtener_json_correctamente(mock_get):
    respuesta = MagicMock()

    respuesta.json.return_value = {
        "titulo": "El Principito"
    }

    mock_get.return_value = respuesta

    resultado = obtener_json(
        "https://ejemplo.com/libros"
    )

    assert resultado == {
        "titulo": "El Principito"
    }

    mock_get.assert_called_once_with(
        "https://ejemplo.com/libros",
        params=None,
        timeout=(10, 20)
    )

    respuesta.raise_for_status.assert_called_once()
    respuesta.json.assert_called_once()


@patch("routes.utilidades.requests.get")
def test_obtener_json_con_parametros(mock_get):
    respuesta = MagicMock()

    respuesta.json.return_value = {
        "resultados": []
    }

    mock_get.return_value = respuesta

    parametros = {
        "q": "El Principito"
    }

    resultado = obtener_json(
        "https://ejemplo.com/libros",
        params=parametros,
        timeout=(5, 10)
    )

    assert resultado == {
        "resultados": []
    }

    mock_get.assert_called_once_with(
        "https://ejemplo.com/libros",
        params=parametros,
        timeout=(5, 10)
    )


@patch("routes.utilidades.time.sleep")
@patch("routes.utilidades.requests.get")
def test_obtener_json_reintenta_si_falla(
    mock_get,
    mock_sleep
):
    respuesta = MagicMock()

    respuesta.json.return_value = {
        "ok": True
    }

    mock_get.side_effect = [
        requests.exceptions.RequestException(
            "Error de conexión"
        ),
        respuesta
    ]

    resultado = obtener_json(
        "https://ejemplo.com"
    )

    assert resultado == {
        "ok": True
    }

    assert mock_get.call_count == 2

    mock_sleep.assert_called_once_with(1)

    respuesta.raise_for_status.assert_called_once()
    respuesta.json.assert_called_once()


@patch("routes.utilidades.time.sleep")
@patch("routes.utilidades.requests.get")
def test_obtener_json_agota_intentos(
    mock_get,
    mock_sleep
):
    mock_get.side_effect = requests.exceptions.RequestException(
        "Error de conexión"
    )

    resultado = obtener_json(
        "https://ejemplo.com",
        intentos=3
    )

    assert resultado is None

    assert mock_get.call_count == 3

    assert mock_sleep.call_count == 2


@patch("routes.utilidades.time.sleep")
@patch("routes.utilidades.requests.get")
def test_obtener_json_no_reintenta_si_intentos_es_uno(
    mock_get,
    mock_sleep
):
    mock_get.side_effect = requests.exceptions.RequestException(
        "Error de conexión"
    )

    resultado = obtener_json(
        "https://ejemplo.com",
        intentos=1
    )

    assert resultado is None

    mock_get.assert_called_once()

    mock_sleep.assert_not_called()


@patch("routes.utilidades.requests.get")
def test_obtener_json_usa_timeout_personalizado(mock_get):
    respuesta = MagicMock()

    respuesta.json.return_value = {
        "ok": True
    }

    mock_get.return_value = respuesta

    resultado = obtener_json(
        "https://ejemplo.com",
        timeout=(3, 7)
    )

    assert resultado == {
        "ok": True
    }

    mock_get.assert_called_once_with(
        "https://ejemplo.com",
        params=None,
        timeout=(3, 7)
    )


@patch("routes.utilidades.time.sleep")
@patch("routes.utilidades.requests.get")
def test_obtener_json_falla_varias_veces_y_luego_funciona(
    mock_get,
    mock_sleep
):
    respuesta = MagicMock()

    respuesta.json.return_value = {
        "mensaje": "Conexión recuperada"
    }
    mock_get.side_effect = [
        requests.exceptions.Timeout(
            "Tiempo agotado"
        ),
        requests.exceptions.ConnectionError(
            "Sin conexión"
        ),
        requests.exceptions.RequestException(
            "Error temporal"
        ),
        respuesta
    ]

    resultado = obtener_json(
        "https://ejemplo.com",
        intentos=5
    )

    assert resultado == {
        "mensaje": "Conexión recuperada"
    }

    assert mock_get.call_count == 4

    assert mock_sleep.call_count == 3