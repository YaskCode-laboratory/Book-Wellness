import pytest
from unittest.mock import MagicMock, patch

from models.Libro import Libro


# ============================================================
# CONSTRUCTOR
# ============================================================

def test_constructor():
    libro = Libro(
        id_usuario=1,
        titulo="Harry Potter",
        autor="J.K. Rowling",
        descripcion="Un libro de magia",
        portada="http://imagen.com/libro.jpg",
        categoria="Fantasía",
        key_libro="/works/OL123W",
        paginas=300,
        id_google="abc123",
        genero="Fantasía",
        anio=1997,
        es_manual=True,
        formato="Físico"
    )

    assert libro.id_usuario == 1
    assert libro.titulo == "Harry Potter"
    assert libro.autor == "J.K. Rowling"
    assert libro.descripcion == "Un libro de magia"
    assert libro.portada == "http://imagen.com/libro.jpg"
    assert libro.categoria == "Fantasía"
    assert libro.key_libro == "/works/OL123W"
    assert libro.paginas == 300
    assert libro.id_google == "abc123"
    assert libro.genero == "Fantasía"
    assert libro.anio == 1997
    assert libro.es_manual is True
    assert libro.formato == "Físico"


def test_constructor_valores_por_defecto():
    libro = Libro()

    assert libro.id_usuario is None
    assert libro.titulo is None
    assert libro.autor is None
    assert libro.descripcion is None
    assert libro.portada is None
    assert libro.categoria is None
    assert libro.key_libro is None
    assert libro.paginas is None
    assert libro.id_google is None
    assert libro.genero is None
    assert libro.anio is None
    assert libro.es_manual is False
    assert libro.formato is None


# ============================================================
# GUARDAR
# ============================================================

@patch("models.Libro.obtener_conexion")
def test_guardar(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = None
    cursor.lastrowid = 15

    libro = Libro(
        id_usuario=1,
        titulo="Harry Potter",
        autor="J.K. Rowling",
        portada="http://imagen.com/libro.jpg"
    )

    resultado = libro.guardar()

    assert resultado == 15

    # La portada http debe convertirse en https
    parametros = cursor.execute.call_args_list[1].args[1]

    assert "https://imagen.com/libro.jpg" in parametros

    conexion.commit.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.Libro.obtener_conexion")
def test_guardar_libro_duplicado(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = {
        "id_libro": 10
    }

    libro = Libro(
        id_usuario=1,
        titulo="Harry Potter"
    )

    resultado = libro.guardar()

    assert resultado is False
    conexion.commit.assert_not_called()


# ============================================================
# OBTENER
# ============================================================

@patch("models.Libro.obtener_conexion")
def test_obtener(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    datos = {
        "id_libro": 5,
        "titulo": "1984",
        "autor": "George Orwell"
    }

    cursor.fetchone.return_value = datos

    resultado = Libro.obtener(5)

    assert resultado == datos
    cursor.execute.assert_called_once()


@patch("models.Libro.obtener_conexion")
def test_obtener_no_encontrado(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = None

    resultado = Libro.obtener(999)

    assert resultado is None
# ============================================================
# LIBROS DEL USUARIO
# ============================================================

@pytest.mark.parametrize(
    "orden",
    [None, "recientes", "antiguos", "az", "za"]
)
@patch("models.Libro.obtener_conexion")
def test_obtener_libros_usuario(mock_conexion, orden):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    libros = [
        {"id_libro": 1, "titulo": "A"},
        {"id_libro": 2, "titulo": "B"}
    ]

    cursor.fetchall.return_value = libros

    resultado = Libro.obtener_libros_usuario(
        id_usuario=1,
        categoria="Fantasía",
        orden=orden
    )

    assert resultado == libros
    cursor.execute.assert_called_once()


@patch("models.Libro.obtener_conexion")
def test_eliminar_libro(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    resultado = Libro.eliminar(10, 1)

    assert resultado is None

    assert cursor.execute.call_count == 2
    conexion.commit.assert_called_once()

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


# ============================================================
# ACTUALIZAR DATOS
# ============================================================

@patch("models.Libro.obtener_conexion")
def test_actualizar_datos_todos(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    Libro.actualizar_datos(
        id_libro=10,
        paginas_totales=300,
        num_caps=20,
        formato="Ebook"
    )

    cursor.execute.assert_called_once()
    conexion.commit.assert_called_once()


@patch("models.Libro.obtener_conexion")
def test_actualizar_datos_solo_paginas(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    Libro.actualizar_datos(
        id_libro=10,
        paginas_totales=500
    )

    cursor.execute.assert_called_once()
    conexion.commit.assert_called_once()


@patch("models.Libro.obtener_conexion")
def test_actualizar_datos_solo_capitulos(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    Libro.actualizar_datos(
        id_libro=10,
        num_caps=25
    )

    cursor.execute.assert_called_once()


@patch("models.Libro.obtener_conexion")
def test_actualizar_datos_solo_formato(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    Libro.actualizar_datos(
        id_libro=10,
        formato="Audiolibro"
    )

    cursor.execute.assert_called_once()


@patch("models.Libro.obtener_conexion")
def test_actualizar_datos_sin_cambios(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    Libro.actualizar_datos(id_libro=10)

    cursor.execute.assert_not_called()
    conexion.commit.assert_not_called()


# ============================================================
# OBTENER COMPLETO
# ============================================================

@patch("models.Libro.obtener_conexion")
def test_obtener_completo_por_google(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    datos = {
        "id_libro": 1,
        "titulo": "1984"
    }

    cursor.fetchone.return_value = datos

    resultado = Libro.obtener_completo(
        id_google="abc123"
    )

    assert resultado == datos


@patch("models.Libro.obtener_conexion")
def test_obtener_completo_por_key(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()
    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    datos = {
        "id_libro": 1,
        "titulo": "1984"
    }

    cursor.fetchone.return_value = datos

    resultado = Libro.obtener_completo(
        key_libro="/works/OL123W"
    )

    assert resultado == datos


@patch("models.Libro.obtener_conexion")
def test_obtener_completo_sin_identificador(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = None

    resultado = Libro.obtener_completo()

    assert resultado is None


# ============================================================
# FORMATEAR RESPUESTA
# ============================================================

def test_formatear_respuesta_completa():
    datos = {
        "id_libro": 1,
        "titulo": "1984",
        "autor": "George Orwell",
        "descripcion": "Distopía",
        "portada": "imagen.jpg",
        "categoria": "Ficción",
        "key_libro": "/works/OL123W",
        "paginas": 300,
        "id_google": "abc123",
        "genero": "Distopía",
        "anio": 1949,
        "formato": "Físico"
    }

    resultado = Libro.formatear_respuesta(datos)

    assert isinstance(resultado, dict)
    assert resultado["titulo"] == "1984"
    assert resultado["autor"] == "George Orwell"
    assert resultado["descripcion"] == "Distopía"


def test_formatear_respuesta_valores_vacios():
    resultado = Libro.formatear_respuesta({})

    assert resultado["titulo"] == "Sin título"
    assert resultado["autor"] == "Autor desconocido"


# ============================================================
# GOOGLE BOOKS - API REAL
# ============================================================

def test_buscar_google_api_real():
    resultado = Libro.buscar_google("Harry Potter")

    assert resultado is not None
    assert isinstance(resultado, (dict, list))


def test_obtener_google_api_real():
    resultado = Libro.obtener_google("KZvHBAAAQBAJ")

    assert resultado is not None
    assert isinstance(resultado, dict)


# ============================================================
# OPENLIBRARY - API REAL
# ============================================================

def test_buscar_openlibrary_api_real():
    resultado = Libro.buscar_openlibrary("Harry Potter")

    assert resultado is not None
    assert isinstance(resultado, (dict, list))


def test_obtener_openlibrary_api_real():
    resultado = Libro.obtener_openlibrary(
        "/works/OL82563W"
    )

    assert isinstance(resultado, dict)

    assert "titulo" in resultado or "error" in resultado


def test_obtener_openlibrary_clave_invalida():
    resultado = Libro.obtener_openlibrary("")

    assert resultado == {
        "error": "Clave inválida"
    }


# ============================================================
# BD -> GOOGLE BOOKS
# ============================================================

@patch("models.Libro.obtener_conexion")
def test_obtener_desde_bd_por_google(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = {
        "id_libro": 1,
        "titulo": "1984"
    }

    resultado = Libro.obtener_desde_bd_o_google(
        id_google="abc123"
    )

    assert resultado["titulo"] == "1984"


@patch("models.Libro.obtener_conexion")
def test_obtener_desde_bd_por_clave(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = {
        "id_libro": 1,
        "titulo": "1984"
    }

    resultado = Libro.obtener_desde_bd_o_google(
        clave="/works/OL123W"
    )

    assert resultado["titulo"] == "1984"


@patch("models.Libro.obtener_conexion")
def test_obtener_desde_bd_por_id_libro(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()
    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = {
        "id_libro": 20,
        "titulo": "El Hobbit"
    }

    resultado = Libro.obtener_desde_bd_o_google(
        id_libro=20
    )

    assert resultado["titulo"] == "El Hobbit"


@patch("models.Libro.obtener_conexion")
def test_obtener_desde_google_si_no_existe_bd(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    # La base de datos no encuentra el libro.
    cursor.fetchone.return_value = None

    # Se consulta Google Books REALMENTE.
    resultado = Libro.obtener_desde_bd_o_google(
        id_google="KZvHBAAAQBAJ"
    )

    assert resultado is not None
    assert isinstance(resultado, dict)


@patch("models.Libro.obtener_conexion")
def test_obtener_desde_bd_o_google_sin_datos(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = None

    resultado = Libro.obtener_desde_bd_o_google()

    assert resultado is None


# ============================================================
# CATEGORÍA
# ============================================================

@patch("models.Libro.obtener_conexion")
def test_actualizar_categoria(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    resultado = Libro.actualizar_categoria(
        id_libro=10,
        categoria="Fantasía"
    )

    assert resultado is None

    cursor.execute.assert_called_once()
    conexion.commit.assert_called_once()


# ============================================================
# FORMATO
# ============================================================

@patch("models.Libro.obtener_conexion")
def test_obtener_libros_usuario_formato(mock_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    datos = [
        {
            "id_libro": 1,
            "titulo": "Harry Potter",
            "formato": "Ebook"
        }
    ]

    cursor.fetchall.return_value = datos

    resultado = Libro.obtener_libros_usuario_formato(
        id_usuario=1,
        formato="Ebook"
    )

    assert resultado == datos
    cursor.execute.assert_called_once()