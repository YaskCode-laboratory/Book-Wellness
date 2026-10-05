import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app import app


@pytest.fixture
def cliente():
    app.config["TESTING"] = True

    with app.test_client() as cliente:
        yield cliente


# ============================================================
# RUTAS DE PÁGINAS
# ============================================================

def test_home_sin_usuario(cliente):
    respuesta = cliente.get("/")

    assert respuesta.status_code == 200


@patch("routes.home.Libro.obtener_libros_usuario")
@patch("routes.home.Estadistica.consultar")
def test_home_con_usuario(mock_estadistica, mock_libros, cliente):

    mock_libros.return_value = []
    mock_estadistica.return_value = {
        "racha_actual": 5
    }

    with cliente.session_transaction() as sesion:
        sesion["id_usuario"] = 1

    respuesta = cliente.get("/")

    assert respuesta.status_code == 200
    mock_estadistica.assert_called_once_with(1)


def test_sesion(cliente):
    respuesta = cliente.get("/sesion")

    assert respuesta.status_code == 200


def test_registro(cliente):
    respuesta = cliente.get("/registro")

    assert respuesta.status_code == 200


def test_recuperar_password(cliente):
    respuesta = cliente.get("/recuperar-password")

    assert respuesta.status_code == 200


def test_seccion_lectura(cliente):
    respuesta = cliente.get("/seccion-lectura")

    assert respuesta.status_code == 200


@patch("routes.home.Estadistica.consultar")
def test_estadisticas_sin_usuario(mock_estadistica, cliente):

    respuesta = cliente.get("/estadisticas")

    assert respuesta.status_code == 200
    mock_estadistica.assert_not_called()


@patch("routes.home.EstadoAnimo.obtener_actual")
@patch("routes.home.Estadistica.consultar")
def test_estadisticas_con_usuario(
    mock_estadistica,
    mock_estado,
    cliente
):

    mock_estadistica.return_value = {
        "racha_actual": 3
    }

    mock_estado.return_value = {
        "estado": "feliz"
    }

    with cliente.session_transaction() as sesion:
        sesion["id_usuario"] = 1

    respuesta = cliente.get("/estadisticas")

    assert respuesta.status_code == 200

    mock_estadistica.assert_called_once_with(1)
    mock_estado.assert_called_once_with(1)


def test_objetivo(cliente):
    respuesta = cliente.get("/objetivo")

    assert respuesta.status_code == 200


@patch("routes.home.Libro.obtener_libros_usuario_formato")
@patch("routes.home.Libro.obtener_libros_usuario")
def test_leidos_con_usuario(
    mock_libros,
    mock_formato,
    cliente
):

    mock_libros.return_value = []
    mock_formato.return_value = []

    with cliente.session_transaction() as sesion:
        sesion["id_usuario"] = 1

    respuesta = cliente.get("/leidos")

    assert respuesta.status_code == 200

    mock_formato.assert_called_once_with(
        1,
        "Audiolibro"
    )


def test_leidos_sin_usuario(cliente):
    respuesta = cliente.get("/leidos")

    assert respuesta.status_code == 200


def test_seguimiento(cliente):
    respuesta = cliente.get("/seguimiento")

    assert respuesta.status_code == 200


def test_agregar(cliente):
    respuesta = cliente.get("/agregar")

    assert respuesta.status_code == 200


def test_formulario_principiante(cliente):
    respuesta = cliente.get("/formulario-principiante")

    assert respuesta.status_code == 200


def test_formulario_intermedio(cliente):
    respuesta = cliente.get("/formulario-intermedio")

    assert respuesta.status_code == 200


def test_formulario_experto(cliente):
    respuesta = cliente.get("/formulario-experto")

    assert respuesta.status_code == 200


# ============================================================
# LOGROS
# ============================================================

@patch("routes.home.Logros.obtener_logros")
def test_logros_sin_usuario(mock_logros, cliente):

    respuesta = cliente.get("/api/logros")

    assert respuesta.status_code == 401
    mock_logros.assert_not_called()


@patch("routes.home.Logros.obtener_logros")
def test_logros_con_usuario(mock_logros, cliente):
    mock_logros.return_value = {
        "logros1": [
            {"id": 1, "nombre": "Devorador de Páginas"}
        ],
        "logros2": [
            {"id": 8, "nombre": "Explorador de Misterio"}
        ],
        "logros3": [
            {"id": 15, "nombre": "Mente Sana"}
        ]
    }

    with cliente.session_transaction() as sesion:
        sesion["id_usuario"] = 1

    respuesta = cliente.get("/api/logros")

    assert respuesta.status_code == 200

    datos = respuesta.get_json()

    assert len(datos) == 3
    assert datos[0]["id"] == 1
    assert datos[1]["id"] == 8
    assert datos[2]["id"] == 15

    mock_logros.assert_called_once_with(1)


# ============================================================
# REANUDAR LIBRO
# ============================================================

def test_reanudar_libro_sin_usuario(cliente):

    respuesta = cliente.post(
        "/api/reanudar_libro",
        json={"id_libro": 10}
    )

    assert respuesta.status_code == 401


@patch("routes.home.Libro.actualizar_categoria")
def test_reanudar_libro(mock_actualizar, cliente):

    with cliente.session_transaction() as sesion:
        sesion["id_usuario"] = 1

    respuesta = cliente.post(
        "/api/reanudar_libro",
        json={"id_libro": 10}
    )

    assert respuesta.status_code == 200

    datos = respuesta.get_json()

    assert datos["mensaje"] == "Libro reanudado"

    mock_actualizar.assert_called_once_with(
        10,
        "leyendo"
    )


# ============================================================
# GUARDAR ENCUESTA
# ============================================================

@patch("routes.home.Preferencias.obtener_usuario_pendiente")
def test_guardar_encuesta_sin_usuario_pendiente(
    mock_pendiente,
    cliente
):

    mock_pendiente.return_value = None

    respuesta = cliente.post(
        "/api/guardar_encuesta",
        json={
            "nivel": "principiante",
            "respuestas": {}
        }
    )

    assert respuesta.status_code == 400

    datos = respuesta.get_json()

    assert datos["error"] == "No existe un usuario pendiente."


@patch("routes.home.Preferencias.limpiar_usuario_pendiente")
@patch("routes.home.Preferencias.guardar")
@patch("routes.home.Preferencias.obtener_usuario_pendiente")
def test_guardar_encuesta(
    mock_pendiente,
    mock_guardar,
    mock_limpiar,
    cliente
):

    mock_pendiente.return_value = 1

    respuesta = cliente.post(
        "/api/guardar_encuesta",
        json={
            "nivel": "principiante",
            "respuestas": {
                "genero": "fantasia"
            }
        }
    )

    assert respuesta.status_code == 200

    datos = respuesta.get_json()

    assert datos["mensaje"] == "Encuesta guardada correctamente."

    mock_guardar.assert_called_once()
    mock_limpiar.assert_called_once_with(1)


# ============================================================
# ESTADO DE ÁNIMO - GET
# ============================================================

def test_estado_animo_get_sin_usuario(cliente):

    respuesta = cliente.get("/api/estado_animo_actual")

    assert respuesta.status_code == 401

    datos = respuesta.get_json()

    assert datos["estado"] is None


@patch("routes.home.db.obtener_conexion")
def test_estado_animo_get_sin_registro(
    mock_conexion,
    cliente
):

    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = None

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    with cliente.session_transaction() as sesion:
        sesion["id_usuario"] = 1

    respuesta = cliente.get("/api/estado_animo_actual")

    assert respuesta.status_code == 200

    datos = respuesta.get_json()

    assert datos["estado"] is None

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


# ============================================================
# ESTADO DE ÁNIMO - POST
# ============================================================

def test_estado_animo_post_sin_usuario(cliente):
    respuesta = cliente.post(
        "/api/estado_animo_actual",
        json={"estado": "feliz"}
    )

    assert respuesta.status_code == 401


def test_estado_animo_post_sin_estado(cliente):

    with cliente.session_transaction() as sesion:
        sesion["id_usuario"] = 1

    respuesta = cliente.post(
        "/api/estado_animo_actual",
        json={}
    )

    assert respuesta.status_code == 400

    datos = respuesta.get_json()

    assert "No se recibió ningún estado" in datos["error"]


# ============================================================
# ANALIZAR TRISTE
# ============================================================

def test_analizar_triste_sin_usuario(cliente):

    respuesta = cliente.post(
        "/api/triste/analizar",
        json={
            "respuesta": "Estoy triste"
        }
    )

    assert respuesta.status_code == 401


def test_analizar_triste_respuesta_vacia(cliente):

    with cliente.session_transaction() as sesion:
        sesion["id_usuario"] = 1

    respuesta = cliente.post(
        "/api/triste/analizar",
        json={
            "respuesta": "   "
        }
    )

    assert respuesta.status_code == 400

    datos = respuesta.get_json()

    assert datos["error"] == "La respuesta está vacía."


@patch("routes.home.EstadoAnimo.procesar_triste")
def test_analizar_triste(mock_procesar, cliente):

    mock_procesar.return_value = {
        "respuesta": "Te entiendo.",
        "recomendaciones": [
            {"titulo": "Libro recomendado"}
        ],
        "estado_triste": True
    }

    with cliente.session_transaction() as sesion:
        sesion["id_usuario"] = 1

    respuesta = cliente.post(
        "/api/triste/analizar",
        json={
            "respuesta": "Hoy tuve un día difícil."
        }
    )

    assert respuesta.status_code == 200

    datos = respuesta.get_json()

    assert datos["respuesta_ia"] == "Te entiendo."
    assert len(datos["recomendaciones"]) == 1
    assert datos["estado_triste"] is True

    mock_procesar.assert_called_once_with(
        1,
        "Hoy tuve un día difícil."
    )


# ============================================================
# HISTORIAL DE ÁNIMO
# ============================================================

@patch("routes.home.db.obtener_conexion")
def test_historial_animo_sin_usuario(
    mock_conexion,
    cliente
):

    respuesta = cliente.get("/historial-animo")

    assert respuesta.status_code == 200

    mock_conexion.assert_not_called()


@patch("routes.home.db.obtener_conexion")
def test_historial_animo_con_usuario(
    mock_conexion,
    cliente
):

    conexion = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = [
        {
            "estado_animo": "feliz",
            "fecha_hora": datetime(2026, 10, 1, 10, 0, 0)
        }
    ]

    conexion.cursor.return_value = cursor
    mock_conexion.return_value = conexion

    with cliente.session_transaction() as sesion:
        sesion["id_usuario"] = 1

    respuesta = cliente.get("/historial-animo")

    assert respuesta.status_code == 200

    cursor.execute.assert_called_once()

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()