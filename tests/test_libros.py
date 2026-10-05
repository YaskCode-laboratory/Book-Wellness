from unittest.mock import MagicMock, patch

from flask import Flask

from routes.libros import registrar_rutas


# ============================================================
# CONFIGURACIÓN
# ============================================================

def crear_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test-secret-key"

    registrar_rutas(app)

    return app


# ============================================================
# /buscar
# ============================================================

@patch("routes.libros.render_template")
def test_buscar_con_consulta(mock_render):
    app = crear_app()

    mock_render.return_value = "OK"

    with app.test_client() as client:
        respuesta = client.get(
            "/buscar?q=El+Principito"
        )

    assert respuesta.status_code == 200

    mock_render.assert_called_once_with(
        "BusquedaDeLibros.html",
        consulta="El Principito"
    )


@patch("routes.libros.render_template")
def test_buscar_sin_consulta(mock_render):
    app = crear_app()

    mock_render.return_value = "OK"

    with app.test_client() as client:
        respuesta = client.get("/buscar")

    assert respuesta.status_code == 200

    mock_render.assert_called_once_with(
        "BusquedaDeLibros.html",
        consulta=""
    )


# ============================================================
# /api/buscar
# ============================================================

@patch("routes.libros.Libro")
def test_api_buscar_google_con_resultados(mock_libro):
    app = crear_app()

    mock_libro.buscar_google.return_value = [
        {
            "titulo": "El Principito",
            "autor": "Antoine de Saint-Exupéry"
        }
    ]

    with app.test_client() as client:
        respuesta = client.get(
            "/api/buscar?q=El+Principito"
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == [
        {
            "titulo": "El Principito",
            "autor": "Antoine de Saint-Exupéry"
        }
    ]

    mock_libro.buscar_google.assert_called_once_with(
        "El Principito"
    )

    mock_libro.buscar_openlibrary.assert_not_called()


@patch("routes.libros.Libro")
def test_api_buscar_google_sin_resultados_usa_openlibrary(
    mock_libro
):
    app = crear_app()

    mock_libro.buscar_google.return_value = []

    mock_libro.buscar_openlibrary.return_value = [
        {
            "titulo": "El Principito",
            "autor": "Antoine de Saint-Exupéry"
        }
    ]

    with app.test_client() as client:
        respuesta = client.get(
            "/api/buscar?q=El+Principito"
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == [
        {
            "titulo": "El Principito",
            "autor": "Antoine de Saint-Exupéry"
        }
    ]

    mock_libro.buscar_google.assert_called_once_with(
        "El Principito"
    )

    mock_libro.buscar_openlibrary.assert_called_once_with(
        "El Principito"
    )


@patch("routes.libros.Libro")
def test_api_buscar_sin_consulta(mock_libro):
    app = crear_app()

    mock_libro.buscar_google.return_value = []

    mock_libro.buscar_openlibrary.return_value = []

    with app.test_client() as client:
        respuesta = client.get("/api/buscar")

    assert respuesta.status_code == 200

    assert respuesta.get_json() == []

    mock_libro.buscar_google.assert_called_once_with("")

    mock_libro.buscar_openlibrary.assert_called_once_with("")


@patch("routes.libros.Libro")
def test_api_buscar_error(mock_libro):
    app = crear_app()

    mock_libro.buscar_google.side_effect = Exception(
        "Error de búsqueda"
    )

    with app.test_client() as client:
        respuesta = client.get(
            "/api/buscar?q=Libro"
        )

    assert respuesta.status_code == 500

    datos = respuesta.get_json()

    assert datos["error"] == "Error de búsqueda"


# ============================================================
# /libro
# ============================================================
@patch("routes.libros.render_template")
def test_libro_con_datos(mock_render):
    app = crear_app()

    mock_render.return_value = "OK"

    with app.test_client() as client:
        respuesta = client.get(
            "/libro"
            "?clave=abc123"
            "&portada=portada.jpg"
            "&id_google=google123"
        )

    assert respuesta.status_code == 200

    mock_render.assert_called_once_with(
        "libros.html",
        clave="abc123",
        portada="portada.jpg",
        id_google="google123"
    )


@patch("routes.libros.render_template")
def test_libro_sin_datos(mock_render):
    app = crear_app()

    mock_render.return_value = "OK"

    with app.test_client() as client:
        respuesta = client.get("/libro")

    assert respuesta.status_code == 200

    mock_render.assert_called_once_with(
        "libros.html",
        clave=None,
        portada=None,
        id_google=None
    )


# ============================================================
# /api/libro
# ============================================================

@patch("routes.libros.Libro")
def test_api_libro_por_id_google_en_bd(mock_libro):
    app = crear_app()

    libro_bd = {
        "id_libro": 1,
        "titulo": "El Principito"
    }

    mock_libro.obtener_completo.return_value = libro_bd

    mock_libro.formatear_respuesta.return_value = {
        "id_libro": 1,
        "titulo": "El Principito"
    }

    with app.test_client() as client:
        respuesta = client.get(
            "/api/libro?id=google123"
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "id_libro": 1,
        "titulo": "El Principito"
    }

    mock_libro.obtener_completo.assert_called_once_with(
        id_google="google123"
    )

    mock_libro.formatear_respuesta.assert_called_once_with(
        libro_bd
    )


@patch("routes.libros.Libro")
def test_api_libro_por_clave_en_bd(mock_libro):
    app = crear_app()

    libro_bd = {
        "id_libro": 2,
        "titulo": "1984"
    }

    mock_libro.obtener_completo.return_value = libro_bd

    mock_libro.formatear_respuesta.return_value = {
        "id_libro": 2,
        "titulo": "1984"
    }

    with app.test_client() as client:
        respuesta = client.get(
            "/api/libro?clave=clave123"
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "id_libro": 2,
        "titulo": "1984"
    }

    mock_libro.obtener_completo.assert_called_once_with(
        key_libro="clave123"
    )

    mock_libro.formatear_respuesta.assert_called_once_with(
        libro_bd
    )


@patch("routes.libros.Libro")
def test_api_libro_por_id_libro(mock_libro):
    app = crear_app()

    libro_bd = {
        "id_libro": 5,
        "titulo": "Libro guardado"
    }

    mock_libro.obtener.return_value = libro_bd

    mock_libro.formatear_respuesta.return_value = {
        "id_libro": 5,
        "titulo": "Libro guardado"
    }

    with app.test_client() as client:
        respuesta = client.get(
            "/api/libro?id_libro=5"
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "id_libro": 5,
        "titulo": "Libro guardado"
    }

    mock_libro.obtener.assert_called_once_with("5")

    mock_libro.formatear_respuesta.assert_called_once_with(
        libro_bd
    )


@patch("routes.libros.Libro")
def test_api_libro_google_fallback_openlibrary(
    mock_libro
):
    app = crear_app()

    mock_libro.obtener_completo.return_value = None

    mock_libro.obtener_google.side_effect = Exception(
        "Google Books no disponible"
    )

    mock_libro.obtener_openlibrary.return_value = {
        "titulo": "El Principito"
    }

    with app.test_client() as client:
        respuesta = client.get(
            "/api/libro"
            "?id=google123"
            "&portada=portada.jpg"
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "titulo": "El Principito"
    }
    mock_libro.obtener_completo.assert_called_once_with(
        id_google="google123"
    )

    mock_libro.obtener_google.assert_called_once_with(
        "google123"
    )

    # IMPORTANTE:
    # routes/libros.py conserva "clave" como None
    # porque la búsqueda se hizo mediante id_google.
    mock_libro.obtener_openlibrary.assert_called_once_with(
        None,
        "portada.jpg"
    )


@patch("routes.libros.Libro")
def test_api_libro_openlibrary_por_defecto(mock_libro):
    app = crear_app()

    mock_libro.obtener_openlibrary.return_value = {
        "titulo": "Libro OpenLibrary"
    }

    with app.test_client() as client:
        respuesta = client.get("/api/libro")

    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "titulo": "Libro OpenLibrary"
    }

    mock_libro.obtener_openlibrary.assert_called_once_with(
        None,
        ""
    )


@patch("routes.libros.Libro")
def test_api_libro_id_libro_no_encontrado(
    mock_libro
):
    app = crear_app()

    mock_libro.obtener.return_value = None

    mock_libro.obtener_openlibrary.return_value = {
        "titulo": "Libro encontrado en OpenLibrary"
    }

    with app.test_client() as client:
        respuesta = client.get(
            "/api/libro?id_libro=99"
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == {
        "titulo": "Libro encontrado en OpenLibrary"
    }

    mock_libro.obtener.assert_called_once_with("99")

    mock_libro.obtener_openlibrary.assert_called_once_with(
        None,
        ""
    )


# ============================================================
# /libro-manual
# ============================================================

@patch("routes.libros.render_template")
@patch("routes.libros.Libro")
def test_libro_manual_con_libro(
    mock_libro,
    mock_render
):
    app = crear_app()

    libro = {
        "id_libro": 5,
        "titulo": "El Principito",
        "portada": "portada.jpg"
    }

    mock_libro.obtener.return_value = libro

    mock_render.return_value = "OK"

    with app.test_client() as client:
        respuesta = client.get(
            "/libro-manual?id_libro=5"
        )

    assert respuesta.status_code == 200

    mock_libro.obtener.assert_called_once_with("5")

    mock_render.assert_called_once_with(
        "libros.html",
        clave=None,
        portada="portada.jpg",
        id_google=None,
        id_libro="5",
        libro_manual=libro
    )


@patch("routes.libros.render_template")
@patch("routes.libros.Libro")
def test_libro_manual_sin_libro(
    mock_libro,
    mock_render
):
    app = crear_app()

    mock_render.return_value = "OK"

    with app.test_client() as client:
        respuesta = client.get("/libro-manual")

    assert respuesta.status_code == 200

    mock_libro.obtener.assert_not_called()

    mock_render.assert_called_once_with(
        "libros.html",
        clave=None,
        portada=None,
        id_google=None,
        id_libro=None,
        libro_manual=None
    )


@patch("routes.libros.render_template")
@patch("routes.libros.Libro")
def test_libro_manual_libro_no_encontrado(
    mock_libro,
    mock_render
):
    app = crear_app()

    mock_libro.obtener.return_value = None

    mock_render.return_value = "OK"

    with app.test_client() as client:
        respuesta = client.get(
            "/libro-manual?id_libro=99"
        )

    assert respuesta.status_code == 200

    mock_libro.obtener.assert_called_once_with("99")

    mock_render.assert_called_once_with(
        "libros.html",
        clave=None,
        portada=None,
        id_google=None,
        id_libro="99",
        libro_manual=None
    )


# ============================================================
# /filtrar
# ============================================================

@patch("routes.libros.render_template")
def test_filtrar_con_genero(mock_render):
    app = crear_app()

    mock_render.return_value = "OK"
    with app.test_client() as client:
        respuesta = client.get(
            "/filtrar?genero=Fantasía"
        )

    assert respuesta.status_code == 200

    mock_render.assert_called_once_with(
        "BusquedaDeLibros.html",
        consulta="Fantasía"
    )


@patch("routes.libros.render_template")
def test_filtrar_sin_genero(mock_render):
    app = crear_app()

    mock_render.return_value = "OK"

    with app.test_client() as client:
        respuesta = client.get("/filtrar")

    assert respuesta.status_code == 200

    mock_render.assert_called_once_with(
        "BusquedaDeLibros.html",
        consulta=""
    )