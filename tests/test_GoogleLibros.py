import sys
import os

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from unittest.mock import patch

from GoogleLibros import GoogleBooksAPI



# ============================================================
# CONFIGURACIÓN
# ============================================================

def crear_api():
    return GoogleBooksAPI()


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


@patch("GoogleLibros.obtener_json")
def test_buscar_libros_correctamente(mock_obtener_json):

    api = crear_api()

    mock_obtener_json.return_value = {
        "items": [
            {
                "id": "abc123",
                "volumeInfo": {
                    "title": "El Principito",
                    "subtitle": "Una historia",
                    "authors": [
                        "Antoine de Saint-Exupéry"
                    ],
                    "description": "Un pequeño príncipe viaja por distintos planetas.",
                    "pageCount": 96,
                    "categories": [
                        "Ficción"
                    ],
                    "publishedDate": "1943",
                    "imageLinks": {
                        "thumbnail": "portada.jpg"
                    }
                }
            }
        ]
    }

    resultado = api.buscar_libros("El Principito")

    assert len(resultado) == 1

    assert resultado[0] == {
        "titulo": "El Principito",
        "subtitulo": "Una historia",
        "autor": "Antoine de Saint-Exupéry",
        "descripcion": "Un pequeño príncipe viaja por distintos planetas.",
        "paginas": 96,
        "generos": "Ficción",
        "anio": "1943",
        "pais": "Desconocido",
        "formato": "BOOK",
        "portada": "portada.jpg",
        "id_google": "abc123"
    }


@patch("GoogleLibros.obtener_json")
def test_buscar_libros_sin_resultados(mock_obtener_json):

    api = crear_api()

    mock_obtener_json.return_value = {
        "items": []
    }

    resultado = api.buscar_libros("Libro inexistente")

    assert resultado == []


@patch("GoogleLibros.obtener_json")
def test_buscar_libros_sin_datos(mock_obtener_json):

    api = crear_api()

    mock_obtener_json.return_value = None

    resultado = api.buscar_libros("El Principito")

    assert resultado == []


@patch("GoogleLibros.obtener_json")
def test_buscar_libros_error(mock_obtener_json):

    api = crear_api()

    mock_obtener_json.side_effect = Exception(
        "Error de conexión"
    )

    resultado = api.buscar_libros("El Principito")

    assert resultado == []


@patch("GoogleLibros.obtener_json")
def test_buscar_libros_datos_incompletos(mock_obtener_json):

    api = crear_api()

    mock_obtener_json.return_value = {
        "items": [
            {
                "id": "abc123",
                "volumeInfo": {}
            }
        ]
    }

    resultado = api.buscar_libros("Libro")

    assert len(resultado) == 1

    assert resultado[0]["titulo"] == "Sin título"
    assert resultado[0]["subtitulo"] == ""
    assert resultado[0]["autor"] == "Autor desconocido"
    assert resultado[0]["descripcion"] == "Descripción no disponible"
    assert resultado[0]["paginas"] == "Desconocido"
    assert resultado[0]["generos"] == ""
    assert resultado[0]["anio"] == "Desconocido"
    assert resultado[0]["pais"] == "Desconocido"
    assert resultado[0]["formato"] == "BOOK"
    assert resultado[0]["id_google"] == "abc123"


# ============================================================
# obtener_libro()
# ============================================================

@patch("GoogleLibros.obtener_json")
def test_obtener_libro_correctamente(mock_obtener_json):

    api = crear_api()
    mock_obtener_json.return_value = {
        "volumeInfo": {
            "title": "1984",
            "subtitle": "Una novela",
            "authors": [
                "George Orwell"
            ],
            "description": "Una novela distópica.",
            "pageCount": 328,
            "categories": [
                "Ficción",
                "Distopía"
            ],
            "publishedDate": "1949",
            "printType": "BOOK",
            "imageLinks": {
                "thumbnail": "portada.jpg"
            }
        }
    }

    resultado = api.obtener_libro("google123")

    assert resultado == {
        "titulo": "1984",
        "subtitulo": "Una novela",
        "autor": "George Orwell",
        "descripcion": "Una novela distópica.",
        "paginas": 328,
        "generos": "Ficción, Distopía",
        "anio": "1949",
        "formato": "BOOK",
        "portada": "portada.jpg"
    }

    mock_obtener_json.assert_called_once()


@patch("GoogleLibros.obtener_json")
def test_obtener_libro_sin_datos(mock_obtener_json):

    api = crear_api()

    mock_obtener_json.return_value = None

    try:
        api.obtener_libro("google123")
        assert False
    except Exception as e:
        assert str(e) == "Google Books no respondió."


@patch("GoogleLibros.obtener_json")
def test_obtener_libro_datos_incompletos(mock_obtener_json):

    api = crear_api()

    mock_obtener_json.return_value = {
        "volumeInfo": {}
    }

    resultado = api.obtener_libro("google123")

    assert resultado["titulo"] == "Sin título"
    assert resultado["subtitulo"] == ""
    assert resultado["autor"] == "Autor desconocido"
    assert resultado["descripcion"] == "Descripción no disponible"
    assert resultado["paginas"] == "Desconocido"
    assert resultado["generos"] == ""
    assert resultado["anio"] == "Desconocido"
    assert resultado["formato"] == "BOOK"


@patch("GoogleLibros.obtener_json")
def test_obtener_libro_sin_portada(mock_obtener_json):

    api = crear_api()

    mock_obtener_json.return_value = {
        "volumeInfo": {
            "title": "Libro sin portada"
        }
    }

    resultado = api.obtener_libro("google123")

    assert resultado["titulo"] == "Libro sin portada"

    assert (
        resultado["portada"]
        == "https://via.placeholder.com/200x300?text=Sin+Portada"
    )


# ============================================================
# API KEY
# ============================================================

@patch("GoogleLibros.os.getenv")
def test_api_key(mock_getenv):

    mock_getenv.return_value = "clave-de-prueba"

    api = GoogleBooksAPI()

    mock_getenv.assert_called_once_with(
        "GOOGLE_BOOKS_API_KEY"
    )

    assert api.api_key == "clave-de-prueba"