from unittest.mock import MagicMock, patch

from flask import Flask

from routes.lectura import registrar_rutas


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
# /api/agregar_libro
# ============================================================

@patch("routes.lectura.db")
@patch("routes.lectura.Libro")
def test_agregar_libro_exitoso(mock_libro, mock_db):
    app = crear_app()

    libro = MagicMock()
    libro.guardar.return_value = 10
    mock_libro.return_value = libro

    with app.test_client() as client:
        respuesta = client.post(
            "/api/agregar_libro",
            json={
                "id_usuario": 1,
                "titulo": "El Principito",
                "autor": "Antoine de Saint-Exupéry",
                "descripcion": "Un clásico",
                "portada": "portada.jpg",
                "categoria": "pendiente",
                "key_libro": "abc123",
                "paginas": 100,
                "id_google": "google123",
                "genero": "Fantasía",
                "anio": 1943,
                "formato": "Físico"
            }
        )

    assert respuesta.status_code == 201

    datos = respuesta.get_json()

    assert datos["mensaje"] == "Libro agregado correctamente"

    libro.guardar.assert_called_once()
    mock_db.invalidar_cache_recomendaciones.assert_called_once_with(1)


@patch("routes.lectura.Libro")
def test_agregar_libro_sin_usuario(mock_libro):
    app = crear_app()

    with app.test_client() as client:
        respuesta = client.post(
            "/api/agregar_libro",
            json={
                "titulo": "El Principito"
            }
        )

    assert respuesta.status_code == 400

    datos = respuesta.get_json()

    assert datos["error"] == "Usuario no identificado"

    mock_libro.assert_not_called()


@patch("routes.lectura.Libro")
def test_agregar_libro_duplicado(mock_libro):
    app = crear_app()

    libro = MagicMock()
    libro.guardar.return_value = False

    mock_libro.return_value = libro

    with app.test_client() as client:
        respuesta = client.post(
            "/api/agregar_libro",
            json={
                "id_usuario": 1,
                "titulo": "El Principito"
            }
        )

    assert respuesta.status_code == 409

    datos = respuesta.get_json()

    assert datos["error"] == "Este libro ya está en tu lista"


@patch("routes.lectura.Libro")
def test_agregar_libro_error(mock_libro):
    app = crear_app()

    libro = MagicMock()
    libro.guardar.side_effect = Exception("Error de base de datos")

    mock_libro.return_value = libro

    with app.test_client() as client:
        respuesta = client.post(
            "/api/agregar_libro",
            json={
                "id_usuario": 1,
                "titulo": "El Principito"
            }
        )

    assert respuesta.status_code == 500

    datos = respuesta.get_json()

    assert datos["error"] == "Error de base de datos"


# ============================================================
# /sesion-lectura
# ============================================================

@patch("routes.lectura.render_template")
@patch("routes.lectura.SeccionLectura")
@patch("routes.lectura.Libro")
def test_sesion_lectura_con_libro_y_lectura(
    mock_libro,
    mock_seccion,
    mock_render
):
    mock_render.return_value = "OK"

    app = crear_app()

    mock_libro.obtener.return_value = {
        "id_libro": 1,
        "titulo": "El Principito",
        "paginas_totales": 100,
        "num_caps": 10
    }

    fecha_inicio = MagicMock()
    fecha_inicio.date.return_value = "2026-10-01"

    mock_seccion.obtener.return_value = {
        "pagina_actual": 25,
        "capitulos_leidos": 3,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": None,
        "fecha_limite": None
    }

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.get(
            "/sesion-lectura?id_libro=1"
        )

    assert respuesta.status_code == 200

    mock_libro.obtener.assert_called_once_with("1")

    mock_seccion.obtener.assert_called_once_with(
        1,
        "1"
    )


@patch("routes.lectura.render_template")
@patch("routes.lectura.SeccionLectura")
@patch("routes.lectura.Libro")
def test_sesion_lectura_sin_usuario(
    mock_libro,
    mock_seccion,
    mock_render
):
    mock_render.return_value = "OK"

    app = crear_app()

    mock_libro.obtener.return_value = {
        "id_libro": 1,
        "titulo": "Libro",
        "paginas_totales": 100,
        "num_caps": 10
    }

    with app.test_client() as client:
        respuesta = client.get(
            "/sesion-lectura?id_libro=1"
        )

    assert respuesta.status_code == 200

    mock_libro.obtener.assert_called_once_with("1")
    mock_seccion.obtener.assert_not_called()


@patch("routes.lectura.render_template")
@patch("routes.lectura.Libro")
def test_sesion_lectura_sin_libro(
    mock_libro,
    mock_render
):
    mock_render.return_value = "OK"

    app = crear_app()

    with app.test_client() as client:
        respuesta = client.get("/sesion-lectura")

    assert respuesta.status_code == 200

    mock_libro.obtener.assert_not_called()


# ============================================================
# /api/actualizar_progreso
# ============================================================

@patch("routes.lectura.SeccionLectura")
def test_actualizar_progreso_sin_sesion(mock_seccion):
    app = crear_app()

    with app.test_client() as client:
        respuesta = client.post(
            "/api/actualizar_progreso",
            json={
                "id_libro": 1,
                "pagina_actual": 20,
                "capitulos_leidos": 2
            }
        )

    assert respuesta.status_code == 401

    datos = respuesta.get_json()

    assert datos["error"] == "No hay sesión activa"

    mock_seccion.assert_not_called()


@patch("routes.lectura.SeccionLectura")
def test_actualizar_progreso_exitoso(mock_seccion):
    app = crear_app()

    lectura = MagicMock()
    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/actualizar_progreso",
            json={
                "id_libro": 5,
                "pagina_actual": 30,
                "capitulos_leidos": 3,
                "fecha_inicio": "2026-10-01"
            }
        )

    assert respuesta.status_code == 200

    datos = respuesta.get_json()

    assert datos["mensaje"] == "Progreso actualizado"

    mock_seccion.assert_called_once_with(
        id_usuario=1,
        id_libro=5,
        pagina_actual=30,
        capitulos_leidos=3,
        fecha_inicio="2026-10-01"
    )

    lectura.actualizar_progreso.assert_called_once()


@patch("routes.lectura.SeccionLectura")
def test_actualizar_progreso_error(mock_seccion):
    app = crear_app()

    lectura = MagicMock()
    lectura.actualizar_progreso.side_effect = Exception("Error")

    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/actualizar_progreso",
            json={
                "id_libro": 5,
                "pagina_actual": 30,
                "capitulos_leidos": 3
            }
        )

    assert respuesta.status_code == 500

    datos = respuesta.get_json()

    assert datos["error"] == "Error"


# ============================================================
# /api/iniciar_lectura
# ============================================================

@patch("routes.lectura.Libro")
def test_iniciar_lectura_exitoso(mock_libro):
    app = crear_app()

    with app.test_client() as client:
        respuesta = client.post(
            "/api/iniciar_lectura",
            json={
                "id_libro": 5,
                "paginas_totales": 300,
                "num_caps": 20,
                "formato": "Físico"
            }
        )

    assert respuesta.status_code == 200

    datos = respuesta.get_json()

    assert datos["mensaje"] == "Datos guardados"

    mock_libro.actualizar_datos.assert_called_once_with(
        5,
        300,
        20,
        "Físico"
    )


@patch("routes.lectura.Libro")
def test_iniciar_lectura_error(mock_libro):
    app = crear_app()

    mock_libro.actualizar_datos.side_effect = Exception(
        "Error guardando datos"
    )

    with app.test_client() as client:

        respuesta = client.post(
            "/api/iniciar_lectura",
            json={
                "id_libro": 5,
                "paginas_totales": 300,
                "num_caps": 20,
                "formato": "Físico"
            }
        )

    assert respuesta.status_code == 500

    datos = respuesta.get_json()

    assert datos["error"] == "Error guardando datos"


# ============================================================
# /api/guardar_fecha_limite
# ============================================================

@patch("routes.lectura.Calendario")
def test_guardar_fecha_limite_sin_sesion(mock_calendario):
    app = crear_app()

    with app.test_client() as client:

        respuesta = client.post(
            "/api/guardar_fecha_limite",
            json={
                "id_libro": 1,
                "fecha_limite": "2026-12-31"
            }
        )

    assert respuesta.status_code == 401

    datos = respuesta.get_json()

    assert datos["error"] == "No hay sesión activa"

    mock_calendario.guardar_fecha_limite.assert_not_called()


@patch("routes.lectura.Calendario")
def test_guardar_fecha_limite_exitoso(mock_calendario):
    app = crear_app()

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_fecha_limite",
            json={
                "id_libro": 5,
                "fecha_limite": "2026-12-31"
            }
        )

    assert respuesta.status_code == 200

    datos = respuesta.get_json()

    assert datos["mensaje"] == "Fecha límite guardada"

    mock_calendario.guardar_fecha_limite.assert_called_once_with(
        1,
        5,
        "2026-12-31"
    )


@patch("routes.lectura.Calendario")
def test_guardar_fecha_limite_error(mock_calendario):
    app = crear_app()

    mock_calendario.guardar_fecha_limite.side_effect = Exception(
        "Error calendario"
    )

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_fecha_limite",
            json={
                "id_libro": 5,
                "fecha_limite": "2026-12-31"
            }
        )

    assert respuesta.status_code == 500

    datos = respuesta.get_json()

    assert datos["error"] == "Error calendario"


# ============================================================
# /api/fechas_calendario
# ============================================================

@patch("routes.lectura.Calendario")
def test_fechas_calendario_sin_sesion(mock_calendario):
    app = crear_app()

    with app.test_client() as client:
        respuesta = client.get(
            "/api/fechas_calendario"
        )

    assert respuesta.status_code == 401

    assert respuesta.get_json() == {}

    mock_calendario.obtener_fechas_calendario.assert_not_called()


@patch("routes.lectura.Calendario")
def test_fechas_calendario_exitoso(mock_calendario):
    app = crear_app()

    mock_calendario.obtener_fechas_calendario.return_value = [
        {
            "fecha": "2026-10-05",
            "id_libro": 1
        }
    ]

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1
    respuesta = client.get(
            "/api/fechas_calendario"
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == [
        {
            "fecha": "2026-10-05",
            "id_libro": 1
        }
    ]

    mock_calendario.obtener_fechas_calendario.assert_called_once_with(1)


# ============================================================
# /api/libros_por_fecha
# ============================================================

@patch("routes.lectura.Calendario")
def test_libros_por_fecha_sin_sesion(mock_calendario):
    app = crear_app()

    with app.test_client() as client:

        respuesta = client.get(
            "/api/libros_por_fecha?fecha=2026-10-05"
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == []

    mock_calendario.obtener_libros_por_fecha.assert_not_called()


@patch("routes.lectura.Calendario")
def test_libros_por_fecha_sin_fecha(mock_calendario):
    app = crear_app()

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.get(
            "/api/libros_por_fecha"
        )

    assert respuesta.status_code == 400

    assert respuesta.get_json() == []

    mock_calendario.obtener_libros_por_fecha.assert_not_called()


@patch("routes.lectura.Calendario")
def test_libros_por_fecha_exitoso(mock_calendario):
    app = crear_app()

    mock_calendario.obtener_libros_por_fecha.return_value = [
        {
            "id_libro": 5,
            "titulo": "Libro"
        }
    ]

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.get(
            "/api/libros_por_fecha?fecha=2026-10-05"
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == [
        {
            "id_libro": 5,
            "titulo": "Libro"
        }
    ]

    mock_calendario.obtener_libros_por_fecha.assert_called_once_with(
        1,
        "2026-10-05"
    )


# ============================================================
# /seccion2-lectura
# ============================================================

@patch("routes.lectura.render_template")
@patch("routes.lectura.Libro")
def test_seccion2_lectura_con_libro(
    mock_libro,
    mock_render
):
    mock_render.return_value = "OK"

    app = crear_app()

    mock_libro.obtener.return_value = {
        "id_libro": 5,
        "titulo": "El Principito"
    }

    with app.test_client() as client:

        respuesta = client.get(
            "/seccion2-lectura?id_libro=5"
        )

    assert respuesta.status_code == 200

    mock_libro.obtener.assert_called_once_with("5")


@patch("routes.lectura.render_template")
@patch("routes.lectura.Libro")
def test_seccion2_lectura_sin_libro(
    mock_libro,
    mock_render
):
    mock_render.return_value = "OK"

    app = crear_app()

    with app.test_client() as client:

        respuesta = client.get(
            "/seccion2-lectura"
        )

    assert respuesta.status_code == 200

    mock_libro.obtener.assert_not_called()


# ============================================================
# /seccion3-lectura
# ============================================================

@patch("routes.lectura.render_template")
@patch("routes.lectura.SeccionLectura")
def test_seccion3_lectura_con_lectura(
    mock_seccion,
    mock_render
):
    mock_render.return_value = "OK"

    app = crear_app()

    mock_seccion.obtener.return_value = {
        "pagina_actual": 75
    }

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.get(
            "/seccion3-lectura?id_libro=5"
        )

    assert respuesta.status_code == 200

    mock_seccion.obtener.assert_called_once_with(
        1,
        "5"
    )


@patch("routes.lectura.render_template")
@patch("routes.lectura.SeccionLectura")
def test_seccion3_lectura_sin_lectura(
    mock_seccion,
    mock_render
):
    mock_render.return_value = "OK"

    app = crear_app()

    mock_seccion.obtener.return_value = None

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.get(
            "/seccion3-lectura?id_libro=5"
        )

    assert respuesta.status_code == 200
    mock_seccion.obtener.assert_called_once_with(
        1,
        "5"
    )


@patch("routes.lectura.render_template")
@patch("routes.lectura.SeccionLectura")
def test_seccion3_lectura_sin_usuario(
    mock_seccion,
    mock_render
):
    mock_render.return_value = "OK"

    app = crear_app()

    with app.test_client() as client:

        respuesta = client.get(
            "/seccion3-lectura?id_libro=5"
        )

    assert respuesta.status_code == 200

    mock_seccion.obtener.assert_not_called()


# ============================================================
# /api/guardar_lectura
# ============================================================

@patch("routes.lectura.Nota")
@patch("routes.lectura.Libro")
@patch("routes.lectura.SeccionLectura")
def test_guardar_lectura_sin_sesion(
    mock_seccion,
    mock_libro,
    mock_nota
):
    app = crear_app()

    with app.test_client() as client:

        respuesta = client.post(
            "/api/guardar_lectura",
            json={
                "id_libro": 5
            }
        )

    assert respuesta.status_code == 401

    datos = respuesta.get_json()

    assert datos["error"] == "No hay sesión activa"

    mock_seccion.assert_not_called()
    mock_libro.actualizar_categoria.assert_not_called()
    mock_nota.guardar_notas_lectura.assert_not_called()


@patch("routes.lectura.Nota")
@patch("routes.lectura.Libro")
@patch("routes.lectura.SeccionLectura")
def test_guardar_lectura_en_progreso(
    mock_seccion,
    mock_libro,
    mock_nota
):
    app = crear_app()

    lectura = MagicMock()
    lectura.guardar.return_value = 25

    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_lectura",
            json={
                "id_libro": 5,
                "tiempo_minutos": 30,
                "estado": "en progreso",
                "paginas_leidas": 20,
                "pagina_actual": 20,
                "capitulos_leidos": 2
            }
        )

    assert respuesta.status_code == 201

    datos = respuesta.get_json()

    assert datos["mensaje"] == "Lectura guardada"

    lectura.guardar.assert_called_once()
    lectura.guardar_sesion.assert_called_once_with(
        como_te_sientes=None
    )

    mock_libro.actualizar_categoria.assert_not_called()


@patch("routes.lectura.Nota")
@patch("routes.lectura.Libro")
@patch("routes.lectura.SeccionLectura")
def test_guardar_lectura_terminada(
    mock_seccion,
    mock_libro,
    mock_nota
):
    app = crear_app()

    lectura = MagicMock()
    lectura.guardar.return_value = 25

    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_lectura",
            json={
                "id_libro": 5,
                "tiempo_minutos": 30,
                "estado": "He terminado el libro",
                "paginas_leidas": 100,
                "pagina_actual": 100,
                "capitulos_leidos": 10
            }
        )

    assert respuesta.status_code == 201

    mock_libro.actualizar_categoria.assert_called_once_with(
        5,
        "leido"
    )


@patch("routes.lectura.Nota")
@patch("routes.lectura.Libro")
@patch("routes.lectura.SeccionLectura")
def test_guardar_lectura_inconclusa(
    mock_seccion,
    mock_libro,
    mock_nota
):
    app = crear_app()

    lectura = MagicMock()
    lectura.guardar.return_value = 25

    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_lectura",
            json={
                "id_libro": 5,
                "estado": "No por ahora",
                "paginas_leidas": 50,
                "pagina_actual": 50,
                "capitulos_leidos": 5
            }
        )

    assert respuesta.status_code == 201
    mock_libro.actualizar_categoria.assert_called_once_with(
        5,
        "inconcluso"
    )


@patch("routes.lectura.Nota")
@patch("routes.lectura.Libro")
@patch("routes.lectura.SeccionLectura")
def test_guardar_lectura_guarda_reflexion(
    mock_seccion,
    mock_libro,
    mock_nota
):
    app = crear_app()

    lectura = MagicMock()
    lectura.guardar.return_value = 30

    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_lectura",
            json={
                "id_libro": 5,
                "estado": "en progreso",
                "estado_animo": "Feliz",
                "notas": "Me gustó mucho.",
                "tipo_reflexion": "aprendiste",
                "respuesta_reflexion": "Aprendí algo nuevo."
            }
        )

    assert respuesta.status_code == 201

    mock_nota.guardar_notas_lectura.assert_called_once_with(
        id_lectura=30,
        como_te_sientes="Feliz",
        continuara="en progreso",
        notas="Me gustó mucho.",
        tipo_reflexion="aprendiste",
        respuesta_reflexion="Aprendí algo nuevo."
    )


@patch("routes.lectura.Nota")
@patch("routes.lectura.Libro")
@patch("routes.lectura.SeccionLectura")
def test_guardar_lectura_guarda_nota_manual(
    mock_seccion,
    mock_libro,
    mock_nota
):
    app = crear_app()

    lectura = MagicMock()
    lectura.guardar.return_value = 40

    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_lectura",
            json={
                "id_libro": 5,
                "estado": "en progreso",
                "notas": "Esta es mi nota.",
                "nota_titulo": "Reflexión personal",
                "nota_categoria": "Reflexiones"
            }
        )

    assert respuesta.status_code == 201

    mock_nota.crear.assert_called_once_with(
        id_usuario=1,
        id_libro=5,
        titulo="Reflexión personal",
        contenido="Esta es mi nota.",
        categoria="Reflexiones"
    )


@patch("routes.lectura.Nota")
@patch("routes.lectura.Libro")
@patch("routes.lectura.SeccionLectura")
def test_guardar_lectura_nota_manual_categoria_default(
    mock_seccion,
    mock_libro,
    mock_nota
):
    app = crear_app()

    lectura = MagicMock()
    lectura.guardar.return_value = 41

    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_lectura",
            json={
                "id_libro": 5,
                "estado": "en progreso",
                "notas": "Una reflexión.",
                "nota_titulo": "Mi nota"
            }
        )

    assert respuesta.status_code == 201

    mock_nota.crear.assert_called_once_with(
        id_usuario=1,
        id_libro=5,
        titulo="Mi nota",
        contenido="Una reflexión.",
        categoria="Reflexiones"
    )


@patch("routes.lectura.Nota")
@patch("routes.lectura.Libro")
@patch("routes.lectura.SeccionLectura")
def test_guardar_lectura_pregunta_aprendiste(
    mock_seccion,
    mock_libro,
    mock_nota
):
    app = crear_app()

    lectura = MagicMock()
    lectura.guardar.return_value = 50

    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_lectura",
            json={
                "id_libro": 5,
                "estado": "en progreso",
                "tipo_reflexion": "aprendiste",
                "respuesta_reflexion": "Aprendí sobre historia."
            }
        )

    assert respuesta.status_code == 201
    llamadas = mock_nota.crear.call_args_list

    assert len(llamadas) == 1

    assert llamadas[0].kwargs == {
        "id_usuario": 1,
        "id_libro": 5,
        "titulo": "¿Qué aprendiste hoy?",
        "contenido": "Aprendí sobre historia.",
        "categoria": "Aprendizaje"
    }


@patch("routes.lectura.Nota")
@patch("routes.lectura.Libro")
@patch("routes.lectura.SeccionLectura")
def test_guardar_lectura_pregunta_palabras(
    mock_seccion,
    mock_libro,
    mock_nota
):
    app = crear_app()

    lectura = MagicMock()
    lectura.guardar.return_value = 51

    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_lectura",
            json={
                "id_libro": 5,
                "estado": "en progreso",
                "tipo_reflexion": "palabras",
                "respuesta_reflexion": "Una palabra nueva."
            }
        )

    assert respuesta.status_code == 201

    llamada = mock_nota.crear.call_args

    assert llamada.kwargs["titulo"] == "¿Palabras nuevas?"
    assert llamada.kwargs["categoria"] == "Vocabulario"


@patch("routes.lectura.Nota")
@patch("routes.lectura.Libro")
@patch("routes.lectura.SeccionLectura")
def test_guardar_lectura_pregunta_personaje(
    mock_seccion,
    mock_libro,
    mock_nota
):
    app = crear_app()

    lectura = MagicMock()
    lectura.guardar.return_value = 52

    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_lectura",
            json={
                "id_libro": 5,
                "estado": "en progreso",
                "tipo_reflexion": "personaje",
                "respuesta_reflexion": "El personaje principal."
            }
        )

    assert respuesta.status_code == 201

    llamada = mock_nota.crear.call_args

    assert llamada.kwargs["titulo"] == "Personaje destacado"
    assert llamada.kwargs["categoria"] == "Personajes"


@patch("routes.lectura.Nota")
@patch("routes.lectura.Libro")
@patch("routes.lectura.SeccionLectura")
def test_guardar_lectura_pregunta_escena(
    mock_seccion,
    mock_libro,
    mock_nota
):
    app = crear_app()

    lectura = MagicMock()
    lectura.guardar.return_value = 53

    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_lectura",
            json={
                "id_libro": 5,
                "estado": "en progreso",
                "tipo_reflexion": "escena",
                "respuesta_reflexion": "La escena final."
            }
        )

    assert respuesta.status_code == 201

    llamada = mock_nota.crear.call_args

    assert llamada.kwargs["titulo"] == "Escena que más impactó"
    assert llamada.kwargs["categoria"] == "Escenas"


@patch("routes.lectura.Nota")
@patch("routes.lectura.Libro")
@patch("routes.lectura.SeccionLectura")
def test_guardar_lectura_pregunta_sesion(
    mock_seccion,
    mock_libro,
    mock_nota
):
    app = crear_app()

    lectura = MagicMock()
    lectura.guardar.return_value = 54

    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_lectura",
            json={
                "id_libro": 5,
                "estado": "en progreso",
                "tipo_reflexion": "sesion",
                "respuesta_reflexion": "Fue una buena sesión."
            }
        )

    assert respuesta.status_code == 201

    llamada = mock_nota.crear.call_args
    assert llamada.kwargs["titulo"] == "¿Qué te pareció esta sesión?"
    assert llamada.kwargs["categoria"] == "Sesión de Lectura"


@patch("routes.lectura.Nota")
@patch("routes.lectura.Libro")
@patch("routes.lectura.SeccionLectura")
def test_guardar_lectura_pregunta_vida(
    mock_seccion,
    mock_libro,
    mock_nota
):
    app = crear_app()

    lectura = MagicMock()
    lectura.guardar.return_value = 55

    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_lectura",
            json={
                "id_libro": 5,
                "estado": "en progreso",
                "tipo_reflexion": "vida",
                "respuesta_reflexion": "Me recordó mi infancia."
            }
        )

    assert respuesta.status_code == 201

    llamada = mock_nota.crear.call_args

    assert llamada.kwargs["titulo"] == "¿Te recordó algo de tu vida?"
    assert llamada.kwargs["categoria"] == "Mi Vida"


@patch("routes.lectura.Nota")
@patch("routes.lectura.Libro")
@patch("routes.lectura.SeccionLectura")
def test_guardar_lectura_pregunta_objetivo(
    mock_seccion,
    mock_libro,
    mock_nota
):
    app = crear_app()

    lectura = MagicMock()
    lectura.guardar.return_value = 56

    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_lectura",
            json={
                "id_libro": 5,
                "estado": "en progreso",
                "tipo_reflexion": "objetivo",
                "respuesta_reflexion": "Quería aprender."
            }
        )

    assert respuesta.status_code == 201

    llamada = mock_nota.crear.call_args

    assert llamada.kwargs["titulo"] == "¿Qué buscabas al leer?"
    assert llamada.kwargs["categoria"] == "Reflexiones"


@patch("routes.lectura.Nota")
@patch("routes.lectura.Libro")
@patch("routes.lectura.SeccionLectura")
def test_guardar_lectura_pregunta_encontraste(
    mock_seccion,
    mock_libro,
    mock_nota
):
    app = crear_app()

    lectura = MagicMock()
    lectura.guardar.return_value = 57

    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_lectura",
            json={
                "id_libro": 5,
                "estado": "en progreso",
                "tipo_reflexion": "encontraste",
                "respuesta_reflexion": "Sí, encontré lo que buscaba."
            }
        )

    assert respuesta.status_code == 201

    llamada = mock_nota.crear.call_args

    assert llamada.kwargs["titulo"] == "¿Encontraste lo que buscabas?"
    assert llamada.kwargs["categoria"] == "Reflexiones"


@patch("routes.lectura.Nota")
@patch("routes.lectura.Libro")
@patch("routes.lectura.SeccionLectura")
def test_guardar_lectura_tipo_reflexion_desconocido(
    mock_seccion,
    mock_libro,
    mock_nota
):
    app = crear_app()

    lectura = MagicMock()
    lectura.guardar.return_value = 58

    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_lectura",
            json={
                "id_libro": 5,
                "estado": "en progreso",
                "tipo_reflexion": "otro",
                "respuesta_reflexion": "Respuesta."
            }
        )

    assert respuesta.status_code == 201

    llamada = mock_nota.crear.call_args

    assert llamada.kwargs["titulo"] == "Reflexión"
    assert llamada.kwargs["categoria"] == "Reflexiones"
@patch("routes.lectura.Nota")
@patch("routes.lectura.Libro")
@patch("routes.lectura.SeccionLectura")
def test_guardar_lectura_error(
    mock_seccion,
    mock_libro,
    mock_nota
):
    app = crear_app()

    lectura = MagicMock()
    lectura.guardar.side_effect = Exception(
        "Error guardando lectura"
    )

    mock_seccion.return_value = lectura

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/guardar_lectura",
            json={
                "id_libro": 5,
                "estado": "en progreso"
            }
        )

    assert respuesta.status_code == 500

    datos = respuesta.get_json()

    assert datos["error"] == "Error guardando lectura"


# ============================================================
# /notas
# ============================================================

@patch("routes.lectura.render_template")
@patch("routes.lectura.Libro")
@patch("routes.lectura.Nota")
def test_notas_sin_usuario(
    mock_nota,
    mock_libro,
    mock_render
):
    mock_render.return_value = "OK"

    app = crear_app()

    with app.test_client() as client:

        respuesta = client.get("/notas")

    assert respuesta.status_code == 200

    mock_nota.obtener_todas.assert_not_called()

    mock_libro.obtener_libros_usuario.assert_not_called()


@patch("routes.lectura.render_template")
@patch("routes.lectura.Libro")
@patch("routes.lectura.Nota")
def test_notas_con_usuario(
    mock_nota,
    mock_libro,
    mock_render
):
    mock_render.return_value = "OK"

    app = crear_app()

    mock_nota.obtener_todas.return_value = (
        [{"id_nota": 1}],
        [{"id_nota": 2}]
    )

    mock_libro.obtener_libros_usuario.side_effect = [
        [{"id_libro": 1}],
        [{"id_libro": 2}],
        [{"id_libro": 3}]
    ]

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.get(
            "/notas?id_libro=5"
        )

    assert respuesta.status_code == 200

    mock_nota.obtener_todas.assert_called_once_with(1)

    assert mock_libro.obtener_libros_usuario.call_count == 3

    llamadas = mock_libro.obtener_libros_usuario.call_args_list

    assert llamadas[0].args == (1, "leyendo")
    assert llamadas[1].args == (1, "leido")
    assert llamadas[2].args == (1, "inconcluso")


# ============================================================
# /api/agregar_nota
# ============================================================

@patch("routes.lectura.Nota")
def test_agregar_nota_sin_sesion(mock_nota):
    app = crear_app()

    with app.test_client() as client:

        respuesta = client.post(
            "/api/agregar_nota",
            json={
                "id_libro": 1,
                "titulo": "Nota",
                "contenido": "Contenido",
                "categoria": "Reflexiones"
            }
        )

    assert respuesta.status_code == 401

    datos = respuesta.get_json()

    assert datos["error"] == "No hay sesión"

    mock_nota.crear.assert_not_called()


@patch("routes.lectura.Nota")
def test_agregar_nota_exitoso(mock_nota):
    app = crear_app()

    nota = MagicMock()
    nota.id_nota = 15

    mock_nota.crear.return_value = nota

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.post(
            "/api/agregar_nota",
            json={
                "id_libro": 5,
                "titulo": "Mi nota",
                "contenido": "Contenido",
                "categoria": "Reflexiones"
            }
        )

    assert respuesta.status_code == 201

    datos = respuesta.get_json()

    assert datos["id_nota"] == 15

    mock_nota.crear.assert_called_once_with(
        1,
        5,
        "Mi nota",
        "Contenido",
        "Reflexiones"
    )


# ============================================================
# /api/editar_nota
# ============================================================

@patch("routes.lectura.Nota")
def test_editar_nota_manual(mock_nota):
    app = crear_app()
    nota = MagicMock()
    mock_nota.return_value = nota

    with app.test_client() as client:

        respuesta = client.post(
            "/api/editar_nota",
            json={
                "id_nota": 5,
                "tipo": "manual",
                "titulo": "Nuevo título",
                "contenido": "Nuevo contenido",
                "categoria": "Aprendizaje"
            }
        )

    assert respuesta.status_code == 200

    datos = respuesta.get_json()

    assert datos["mensaje"] == "Nota actualizada"

    mock_nota.assert_called_once_with(
        id_nota=5,
        tipo="manual"
    )

    nota.editar.assert_called_once_with(
        "Nuevo título",
        "Nuevo contenido",
        "Aprendizaje"
    )


@patch("routes.lectura.Nota")
def test_editar_nota_sesion(mock_nota):
    app = crear_app()

    nota = MagicMock()
    mock_nota.return_value = nota

    with app.test_client() as client:

        respuesta = client.post(
            "/api/editar_nota",
            json={
                "id_nota": 5,
                "tipo": "sesion",
                "campo": "notas",
                "valor": "Texto actualizado"
            }
        )

    assert respuesta.status_code == 200

    datos = respuesta.get_json()

    assert datos["mensaje"] == "Nota actualizada"

    nota.editar_campo_sesion.assert_called_once_with(
        "notas",
        "Texto actualizado"
    )


@patch("routes.lectura.Nota")
def test_editar_nota_tipo_desconocido(mock_nota):
    app = crear_app()

    nota = MagicMock()
    mock_nota.return_value = nota

    with app.test_client() as client:

        respuesta = client.post(
            "/api/editar_nota",
            json={
                "id_nota": 5,
                "tipo": "otro"
            }
        )

    assert respuesta.status_code == 200

    datos = respuesta.get_json()

    assert datos["mensaje"] == "Nota actualizada"

    nota.editar.assert_not_called()
    nota.editar_campo_sesion.assert_not_called()


# ============================================================
# /api/eliminar_nota
# ============================================================

@patch("routes.lectura.Nota")
def test_eliminar_nota(mock_nota):
    app = crear_app()

    nota = MagicMock()
    mock_nota.return_value = nota

    with app.test_client() as client:

        respuesta = client.delete(
            "/api/eliminar_nota",
            json={
                "id_nota": 5,
                "tipo": "manual"
            }
        )

    assert respuesta.status_code == 200

    datos = respuesta.get_json()

    assert datos["mensaje"] == "Nota eliminada"

    mock_nota.assert_called_once_with(
        id_nota=5,
        tipo="manual"
    )

    nota.eliminar.assert_called_once()


# ============================================================
# /api/notas
# ============================================================

@patch("routes.lectura.Nota")
def test_api_notas_sin_sesion(mock_nota):
    app = crear_app()

    with app.test_client() as client:

        respuesta = client.get("/api/notas")

    assert respuesta.status_code == 401

    assert respuesta.get_json() == []

    mock_nota.filtrar.assert_not_called()


@patch("routes.lectura.Nota")
def test_api_notas_exitoso(mock_nota):
    app = crear_app()

    mock_nota.filtrar.return_value = [
        {
            "id_nota": 1,
            "titulo": "Mi nota"
        }
    ]

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.get(
            "/api/notas?id_libro=5&categoria=Reflexiones"
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == [
        {
            "id_nota": 1,
            "titulo": "Mi nota"
        }
    ]

    mock_nota.filtrar.assert_called_once_with(
        1,
        "5",
        "Reflexiones"
    )


@patch("routes.lectura.Nota")
def test_api_notas_solo_libro(mock_nota):
    app = crear_app()

    mock_nota.filtrar.return_value = []

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.get(
            "/api/notas?id_libro=10"
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == []

    mock_nota.filtrar.assert_called_once_with(
        1,
        "10",
        None
    )


@patch("routes.lectura.Nota")
def test_api_notas_solo_categoria(mock_nota):
    app = crear_app()

    mock_nota.filtrar.return_value = []

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["id_usuario"] = 1

        respuesta = client.get(
            "/api/notas?categoria=Vocabulario"
        )

    assert respuesta.status_code == 200

    assert respuesta.get_json() == []

    mock_nota.filtrar.assert_called_once_with(
        1,
        None,
        "Vocabulario"
    )