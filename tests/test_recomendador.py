from unittest.mock import MagicMock, patch

from flask import Flask

from IA.recomendador import RecomendadorLibros, recomendador_bp


def crear_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test-secret-key"
    app.register_blueprint(recomendador_bp)
    return app


def crear_recomendador():
    with patch("IA.recomendador.OrquestadorIA"), \
         patch("IA.recomendador.GoogleBooksAPI"), \
         patch("IA.recomendador.libros_api.LibroAPI"):

        recomendador = RecomendadorLibros()

    return recomendador


# ============================================================
# INICIALIZACIÓN
# ============================================================

def test_inicializar_recomendador():
    with patch("IA.recomendador.OrquestadorIA") as mock_ia, \
         patch("IA.recomendador.GoogleBooksAPI") as mock_google, \
         patch("IA.recomendador.libros_api.LibroAPI") as mock_openlibrary:

        recomendador = RecomendadorLibros()

        mock_ia.assert_called_once()
        mock_google.assert_called_once()
        mock_openlibrary.assert_called_once()

        assert recomendador.ia == mock_ia.return_value
        assert recomendador.google == mock_google.return_value
        assert recomendador.openlibrary == mock_openlibrary.return_value


# ============================================================
# OBTENER GÉNEROS
# ============================================================

@patch("IA.recomendador.db.obtener_conexion")
def test_obtener_generos(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchall.return_value = [
        ("Fantasía, Aventura",),
        ("Fantasía",),
        ("Aventura, Romance",),
        (None,),
        ("",),
    ]

    recomendador = crear_recomendador()

    resultado = recomendador.obtener_generos(1)

    assert resultado == {
        "Fantasía": 2,
        "Aventura": 2,
        "Romance": 1
    }

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("IA.recomendador.db.obtener_conexion")
def test_obtener_generos_sin_libros(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor
    cursor.fetchall.return_value = []

    recomendador = crear_recomendador()

    resultado = recomendador.obtener_generos(1)

    assert resultado == {}

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


# ============================================================
# OBTENER TÍTULOS
# ============================================================

@patch("IA.recomendador.db.obtener_conexion")
def test_obtener_titulos(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchall.return_value = [
        ("1984",),
        ("El Hobbit ",),
        (None,),
        ("",),
    ]

    recomendador = crear_recomendador()

    resultado = recomendador.obtener_titulos(1)

    assert resultado == [
        "1984",
        "El Hobbit"
    ]

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("IA.recomendador.db.obtener_conexion")
def test_obtener_titulos_sin_libros(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor
    cursor.fetchall.return_value = []

    recomendador = crear_recomendador()

    resultado = recomendador.obtener_titulos(1)

    assert resultado == []


# ============================================================
# CONSTRUIR PROMPT
# ============================================================

def test_construir_prompt():
    recomendador = crear_recomendador()

    generos = {
        "Fantasía": 3,
        "Romance": 1
    }

    titulos = [
        "El Hobbit",
        "1984"
    ]
    resultado = recomendador.construir_prompt(
        generos,
        titulos,
        "PROMPT BASE"
    )

    assert "PROMPT BASE" in resultado
    assert "Libros que ya posee o ha leído el usuario:" in resultado
    assert "- El Hobbit" in resultado
    assert "- 1984" in resultado
    assert "Géneros favoritos del usuario:" in resultado
    assert "- Fantasía: 3 libros" in resultado
    assert "- Romance: 1 libros" in resultado


def test_construir_prompt_sin_datos():
    recomendador = crear_recomendador()

    resultado = recomendador.construir_prompt(
        {},
        [],
        "PROMPT BASE"
    )

    assert "PROMPT BASE" in resultado
    assert "Libros que ya posee o ha leído el usuario:" in resultado
    assert "Géneros favoritos del usuario:" in resultado


# ============================================================
# BUSCAR LIBROS
# ============================================================

def test_buscar_libros_google_books():
    recomendador = crear_recomendador()

    recomendador.google.buscar_libros.return_value = [
        {
            "titulo": "1984",
            "autor": "George Orwell",
            "descripcion": "Una novela distópica.",
            "portada": "portada.jpg",
            "paginas": 300,
            "generos": "Distopía",
            "anio": "1949",
            "id_google": "abc123",
            "key": ""
        }
    ]

    resultado = recomendador.buscar_libros([
        {
            "titulo": "1984",
            "autor": "George Orwell"
        }
    ])

    assert len(resultado) == 1
    assert resultado[0]["titulo"] == "1984"
    assert resultado[0]["autor"] == "George Orwell"
    assert resultado[0]["id_google"] == "abc123"

    recomendador.google.buscar_libros.assert_called_once_with(
        "1984 George Orwell"
    )


def test_buscar_libros_fallback_openlibrary():
    recomendador = crear_recomendador()

    recomendador.google.buscar_libros.return_value = []

    recomendador.openlibrary.buscar_libros.return_value = [
        {
            "titulo": "1984",
            "autor": "George Orwell",
            "descripcion": "Una novela distópica.",
            "portada": "portada.jpg",
            "paginas": 300,
            "generos": "Distopía",
            "anio": "1949",
            "id_google": "",
            "key": "/works/OL123"
        }
    ]

    resultado = recomendador.buscar_libros([
        {
            "titulo": "1984",
            "autor": "George Orwell"
        }
    ])

    assert len(resultado) == 1
    assert resultado[0]["titulo"] == "1984"
    assert resultado[0]["key"] == "/works/OL123"

    recomendador.openlibrary.buscar_libros.assert_called_once_with(
        "1984 George Orwell"
    )


def test_buscar_libros_sin_resultados():
    recomendador = crear_recomendador()

    recomendador.google.buscar_libros.return_value = []
    recomendador.openlibrary.buscar_libros.return_value = []

    resultado = recomendador.buscar_libros([
        {
            "titulo": "Libro inexistente",
            "autor": "Autor"
        }
    ])

    assert resultado == []


def test_buscar_libros_elige_mejor_resultado():
    recomendador = crear_recomendador()

    recomendador.google.buscar_libros.return_value = [
        {
            "titulo": "Resultado 1",
            "autor": "",
            "descripcion": "",
            "portada": "",
            "anio": "2000",
            "id_google": "",
            "key": ""
        },
        {
            "titulo": "Resultado 2",
            "autor": "Autor",
            "descripcion": "Descripción",
            "portada": "portada.jpg",
            "anio": "2001",
            "id_google": "abc",
            "key": "/works/123"
        }
    ]

    resultado = recomendador.buscar_libros([
        {
            "titulo": "Libro",
            "autor": "Autor"
        }
    ])

    assert len(resultado) == 1
    assert resultado[0]["titulo"] == "Resultado 2"

# ============================================================
# RECOMENDACIONES POR DEFECTO
# ============================================================

@patch.object(RecomendadorLibros, "buscar_libros")
def test_recomendaciones_defecto(mock_buscar):
    mock_buscar.return_value = [
        {"titulo": "El Hobbit"}
    ]

    recomendador = crear_recomendador()

    resultado = recomendador.recomendaciones_defecto()

    assert resultado == [{"titulo": "El Hobbit"}]

    recomendaciones = mock_buscar.call_args[0][0]

    assert len(recomendaciones) == 5
    assert recomendaciones[0]["titulo"] == "El Hobbit"


@patch.object(RecomendadorLibros, "buscar_libros")
def test_recomendaciones_defecto_reflexivo(mock_buscar):
    mock_buscar.return_value = [{"titulo": "Crimen y castigo"}]

    recomendador = crear_recomendador()

    resultado = recomendador.recomendaciones_defecto_reflexivo()

    assert resultado == [{"titulo": "Crimen y castigo"}]

    recomendaciones = mock_buscar.call_args[0][0]

    assert len(recomendaciones) == 5
    assert recomendaciones[0]["titulo"] == "Crimen y castigo"


@patch.object(RecomendadorLibros, "buscar_libros")
def test_recomendaciones_defecto_sorprendido(mock_buscar):
    mock_buscar.return_value = [{"titulo": "El Hobbit"}]

    recomendador = crear_recomendador()

    resultado = recomendador.recomendaciones_defecto_sorprendido()

    assert resultado == [{"titulo": "El Hobbit"}]

    recomendaciones = mock_buscar.call_args[0][0]

    assert len(recomendaciones) == 5


@patch.object(RecomendadorLibros, "buscar_libros")
def test_recomendaciones_defecto_ansioso(mock_buscar):
    mock_buscar.return_value = [{"titulo": "Stardust"}]

    recomendador = crear_recomendador()

    resultado = recomendador.recomendaciones_defecto_ansioso()

    assert resultado == [{"titulo": "Stardust"}]

    recomendaciones = mock_buscar.call_args[0][0]

    assert len(recomendaciones) == 5


# ============================================================
# RECOMENDAR TRISTE
# ============================================================

@patch("IA.recomendador.db.guardar_mensaje")
@patch("IA.recomendador.db.guardar_recomendaciones")
@patch.object(RecomendadorLibros, "buscar_libros")
@patch.object(RecomendadorLibros, "obtener_titulos")
@patch.object(RecomendadorLibros, "obtener_generos")
def test_recomendar_triste(
    mock_generos,
    mock_titulos,
    mock_buscar,
    mock_guardar_recomendaciones,
    mock_guardar_mensaje
):
    recomendador = crear_recomendador()

    mock_generos.return_value = {
        "Fantasía": 2,
        "Romance": 1
    }

    mock_titulos.return_value = [
        "El Hobbit",
        "1984"
    ]

    recomendador.ia.generar_json.return_value = {
        "estado": 2,
        "motivo": "El usuario está atravesando un cambio.",
        "mensaje": "Estas lecturas pueden acompañarte en este momento.",
        "libros": [
            {
                "titulo": "La sombra del viento",
                "autor": "Carlos Ruiz Zafón"
            },
            {
                "titulo": "El principito",
                "autor": "Antoine de Saint-Exupéry"
            }
        ]
    }

    mock_buscar.return_value = [
        {
            "titulo": "La sombra del viento",
            "autor": "Carlos Ruiz Zafón",
            "descripcion": "Descripción",
            "portada": "portada.jpg",
            "paginas": 500,
            "generos": "Misterio",
            "anio": "2001",
            "id_google": "abc123",
            "key": ""
        },
        {
            "titulo": "El principito",
            "autor": "Antoine de Saint-Exupéry",
            "descripcion": "Descripción",
            "portada": "portada2.jpg",
            "paginas": 100,
            "generos": "Fantasía",
            "anio": "1943",
            "id_google": "def456",
            "key": ""
        }
    ]

    resultado = recomendador.recomendar_triste(
        1,
        "Estoy triste porque estoy atravesando un cambio importante."
    )

    assert resultado["estado"] == 2
    assert resultado["motivo"] == "El usuario está atravesando un cambio."
    assert resultado["mensaje"] == "Estas lecturas pueden acompañarte en este momento."

    assert len(resultado["libros"]) == 2

    mock_generos.assert_called_once_with(1)
    mock_titulos.assert_called_once_with(1)

    recomendador.ia.generar_json.assert_called_once()

    mock_buscar.assert_called_once()

    mock_guardar_recomendaciones.assert_called_once_with(
        1,
        resultado["libros"]
    )

    mock_guardar_mensaje.assert_called_once_with(
        1,
        "asistente",
        "Estas lecturas pueden acompañarte en este momento."
    )

    pass