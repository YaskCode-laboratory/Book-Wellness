from unittest.mock import patch, MagicMock
import requests
from Libros import LibroAPI


# ============================================================
# CONFIGURACIÓN
# ============================================================

def crear_api():
    return LibroAPI()


# ============================================================
# obtener_portada()
# ============================================================

def test_obtener_portada_por_edition_key():

    api = crear_api()

    libro = {
        "edition_key": ["OL123M"]
    }

    resultado = api.obtener_portada(libro)

    assert resultado == (
        "https://covers.openlibrary.org/b/olid/"
        "OL123M-L.jpg"
    )


def test_obtener_portada_por_isbn():

    api = crear_api()

    libro = {
        "isbn": ["9781234567890"]
    }

    resultado = api.obtener_portada(libro)

    assert resultado == (
        "https://covers.openlibrary.org/b/isbn/"
        "9781234567890-L.jpg"
    )


def test_obtener_portada_por_cover_id():

    api = crear_api()

    libro = {
        "cover_i": 123456
    }

    resultado = api.obtener_portada(libro)

    assert resultado == (
        "https://covers.openlibrary.org/b/id/"
        "123456-L.jpg"
    )


def test_obtener_portada_sin_portada():

    api = crear_api()

    libro = {}

    resultado = api.obtener_portada(libro)

    assert resultado == (
        "https://via.placeholder.com/"
        "200x300?text=Sin+Portada"
    )


def test_obtener_portada_prioriza_edition_key():

    api = crear_api()

    libro = {
        "edition_key": ["OL123M"],
        "isbn": ["9781234567890"],
        "cover_i": 123456
    }

    resultado = api.obtener_portada(libro)

    assert resultado == (
        "https://covers.openlibrary.org/b/olid/"
        "OL123M-L.jpg"
    )


# ============================================================
# buscar_libros()
# ============================================================

def test_buscar_libros_sin_texto():

    api = crear_api()

    resultado = api.buscar_libros("")

    assert resultado == []


def test_buscar_libros_sin_texto_none():

    api = crear_api()

    resultado = api.buscar_libros(None)

    assert resultado == []


@patch("Libros.requests.get")
def test_buscar_libros_correctamente(mock_get):

    api = crear_api()

    respuesta = MagicMock()

    respuesta.json.return_value = {
        "docs": [
            {
                "title": "El Principito",
                "author_name": [
                    "Antoine de Saint-Exupéry"
                ],
                "first_publish_year": 1943,
                "edition_key": ["OL123M"],
                "language": ["spa"],
                "key": "/works/OL123W"
            }
        ]
    }

    mock_get.return_value = respuesta

    resultado = api.buscar_libros("El Principito")

    assert len(resultado) == 1

    assert resultado[0] == {
        "titulo": "El Principito",
        "autor": "Antoine de Saint-Exupéry",
        "anio": 1943,
        "portada": (
            "https://covers.openlibrary.org/b/olid/"
            "OL123M-L.jpg"
        ),
        "idiomas": ["spa"],
        "key": "/works/OL123W"
    }

    mock_get.assert_called_once_with(
        api.url_base,
        params={"q": "El Principito"},
        timeout=10
    )

    respuesta.raise_for_status.assert_called_once()


@patch("Libros.requests.get")
def test_buscar_libros_sin_resultados(mock_get):

    api = crear_api()

    respuesta = MagicMock()

    respuesta.json.return_value = {
        "docs": []
    }

    mock_get.return_value = respuesta

    resultado = api.buscar_libros("Libro inexistente")

    assert resultado == []


@patch("Libros.requests.get")
def test_buscar_libros_maximo_20(mock_get):

    api = crear_api()

    libros = []

    for i in range(30):
        libros.append({
            "title": f"Libro {i}",
            "author_name": [f"Autor {i}"],
            "first_publish_year": 2000 + i,
            "edition_key": [f"OL{i}M"],
            "language": ["spa"],
            "key": f"/works/OL{i}W"
        })

    respuesta = MagicMock()
    respuesta.json.return_value = {
        "docs": libros
    }

    mock_get.return_value = respuesta

    with patch("Libros.random.sample") as mock_sample:

        mock_sample.return_value = libros[:20]

        resultado = api.buscar_libros("Libros")

    assert len(resultado) == 20

    mock_sample.assert_called_once_with(
        libros,
        20
    )


@patch("Libros.requests.get")
def test_buscar_libros_20_o_menos_no_usa_sample(mock_get):

    api = crear_api()

    libros = [
        {
            "title": "Libro 1",
            "author_name": ["Autor 1"],
            "first_publish_year": 2020,
            "edition_key": ["OL123M"],
            "language": ["spa"],
            "key": "/works/OL123W"
        }
    ]

    respuesta = MagicMock()

    respuesta.json.return_value = {
        "docs": libros
    }

    mock_get.return_value = respuesta

    with patch("Libros.random.sample") as mock_sample:

        resultado = api.buscar_libros("Libro")

    assert len(resultado) == 1

    mock_sample.assert_not_called()


@patch("Libros.requests.get")
def test_buscar_libros_error_request(mock_get):

    api = crear_api()

    mock_get.side_effect = (
        requests.exceptions.RequestException(
            "Error de conexión"
        )
    )

    resultado = api.buscar_libros("El Principito")

    assert resultado == []


@patch("Libros.requests.get")
def test_buscar_libros_datos_incompletos(mock_get):

    api = crear_api()

    respuesta = MagicMock()

    respuesta.json.return_value = {
        "docs": [
            {}
        ]
    }

    mock_get.return_value = respuesta

    resultado = api.buscar_libros("Libro")

    assert len(resultado) == 1

    assert resultado[0]["titulo"] == "Sin título"
    assert resultado[0]["autor"] == "Autor desconocido"
    assert resultado[0]["anio"] == "Desconocido"
    assert resultado[0]["portada"] == (
        "https://via.placeholder.com/"
        "200x300?text=Sin+Portada"
    )
    assert resultado[0]["idiomas"] == []
    assert resultado[0]["key"] == ""