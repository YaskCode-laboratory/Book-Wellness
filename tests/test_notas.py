from unittest.mock import MagicMock, patch

import pytest

from models.Notas import Nota


# ============================================================
# CONSTRUCTOR
# ============================================================

def test_crear_objeto_nota():
    nota = Nota(
        id_nota=1,
        id_usuario=2,
        id_libro=3,
        titulo="Mi nota",
        contenido="Contenido de prueba",
        categoria="Reflexión",
        fecha_creacion="2026-10-05",
        tipo="manual"
    )

    assert nota.id_nota == 1
    assert nota.id_usuario == 2
    assert nota.id_libro == 3
    assert nota.titulo == "Mi nota"
    assert nota.contenido == "Contenido de prueba"
    assert nota.categoria == "Reflexión"
    assert nota.fecha_creacion == "2026-10-05"
    assert nota.tipo == "manual"


def test_constructor_valores_por_defecto():
    nota = Nota()

    assert nota.id_nota is None
    assert nota.id_usuario is None
    assert nota.id_libro is None
    assert nota.titulo is None
    assert nota.contenido is None
    assert nota.categoria is None
    assert nota.fecha_creacion is None
    assert nota.tipo == "manual"


# ============================================================
# OBTENER TODAS
# ============================================================

@patch("models.Notas.obtener_conexion")
def test_obtener_todas(mock_obtener_conexion):
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()

    mock_obtener_conexion.return_value = mock_conexion
    mock_conexion.cursor.return_value = mock_cursor

    notas_manuales = [
        {
            "id_nota": 1,
            "id_libro": 10,
            "titulo": "Nota manual",
            "contenido": "Contenido",
            "categoria": "Reflexión"
        }
    ]

    notas_sesion = [
        {
            "id_nota": 2,
            "como_te_sientes": "Feliz",
            "que_aprendiste": "Aprendí mucho",
            "tipo": "sesion"
        }
    ]

    mock_cursor.fetchall.side_effect = [
        notas_manuales,
        notas_sesion
    ]

    resultado_manuales, resultado_sesion = Nota.obtener_todas(5)

    assert resultado_manuales == notas_manuales
    assert resultado_sesion == notas_sesion

    assert mock_cursor.execute.call_count == 2

    mock_cursor.close.assert_called_once()
    mock_conexion.close.assert_called_once()


# ============================================================
# CREAR
# ============================================================

@patch("models.Notas.obtener_conexion")
def test_crear_nota(mock_obtener_conexion):
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()

    mock_obtener_conexion.return_value = mock_conexion
    mock_conexion.cursor.return_value = mock_cursor

    mock_cursor.lastrowid = 25

    nota = Nota.crear(
        id_usuario=1,
        id_libro=10,
        titulo="Nueva nota",
        contenido="Contenido de la nota",
        categoria="Opinión"
    )

    assert isinstance(nota, Nota)

    assert nota.id_nota == 25
    assert nota.id_usuario == 1
    assert nota.id_libro == 10
    assert nota.titulo == "Nueva nota"
    assert nota.contenido == "Contenido de la nota"
    assert nota.categoria == "Opinión"
    assert nota.tipo == "manual"

    mock_cursor.execute.assert_called_once()
    mock_conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conexion.close.assert_called_once()


# ============================================================
# EDITAR NOTA MANUAL
# ============================================================

@patch("models.Notas.obtener_conexion")
def test_editar_nota_manual(mock_obtener_conexion):
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()

    mock_obtener_conexion.return_value = mock_conexion
    mock_conexion.cursor.return_value = mock_cursor

    nota = Nota(
        id_nota=5,
        id_usuario=1,
        id_libro=10,
        titulo="Título original",
        contenido="Contenido original",
        categoria="Original",
        tipo="manual"
    )
    nota.editar(
        titulo="Título nuevo",
        contenido="Contenido nuevo",
        categoria="Nueva"
    )

    assert nota.titulo == "Título nuevo"
    assert nota.contenido == "Contenido nuevo"
    assert nota.categoria == "Nueva"

    mock_cursor.execute.assert_called_once()
    mock_conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conexion.close.assert_called_once()


def test_editar_nota_con_valores_none():
    nota = Nota(
        id_nota=5,
        titulo="Título original",
        contenido="Contenido original",
        categoria="Original",
        tipo="manual"
    )

    with patch("models.Notas.obtener_conexion") as mock_obtener_conexion:
        mock_conexion = MagicMock()
        mock_cursor = MagicMock()

        mock_obtener_conexion.return_value = mock_conexion
        mock_conexion.cursor.return_value = mock_cursor

        nota.editar()

        assert nota.titulo == "Título original"
        assert nota.contenido == "Contenido original"
        assert nota.categoria == "Original"


def test_editar_nota_sesion_lanza_error():
    nota = Nota(
        id_nota=1,
        tipo="sesion"
    )

    with pytest.raises(
        Exception,
        match="Solo notas manuales son editables completas"
    ):
        nota.editar(
            titulo="Nuevo título",
            contenido="Nuevo contenido",
            categoria="Nueva"
        )


# ============================================================
# EDITAR CAMPO DE SESIÓN
# ============================================================

@patch("models.Notas.obtener_conexion")
def test_editar_campo_sesion(mock_obtener_conexion):
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()

    mock_obtener_conexion.return_value = mock_conexion
    mock_conexion.cursor.return_value = mock_cursor

    nota = Nota(
        id_nota=15,
        tipo="sesion"
    )

    nota.editar_campo_sesion(
        "como_te_sientes",
        "Feliz"
    )

    mock_cursor.execute.assert_called_once_with(
        "UPDATE notas_lectura SET como_te_sientes=%s WHERE id_nota=%s",
        ("Feliz", 15)
    )

    mock_conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conexion.close.assert_called_once()


def test_editar_campo_sesion_campo_no_permitido():
    nota = Nota(
        id_nota=15,
        tipo="sesion"
    )

    with pytest.raises(
        Exception,
        match="Campo no permitido"
    ):
        nota.editar_campo_sesion(
            "campo_inventado",
            "Valor"
        )


@pytest.mark.parametrize(
    "campo",
    [
        "como_te_sientes",
        "que_aprendiste",
        "palabras_nuevas",
        "personaje_destacado",
        "escena_impacto",
        "parecer_sesion",
        "recuerdo_vida",
        "notas_observaciones",
        "respuesta_reflexion"
    ]
)
@patch("models.Notas.obtener_conexion")
def test_editar_todos_los_campos_permitidos(
    mock_obtener_conexion,
    campo
):
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()

    mock_obtener_conexion.return_value = mock_conexion
    mock_conexion.cursor.return_value = mock_cursor

    nota = Nota(
        id_nota=20,
        tipo="sesion"
    )

    nota.editar_campo_sesion(
        campo,
        "Valor de prueba"
    )

    mock_cursor.execute.assert_called_once_with(
        f"UPDATE notas_lectura SET {campo}=%s WHERE id_nota=%s",
        ("Valor de prueba", 20)
    )

    mock_conexion.commit.assert_called_once()


# ============================================================
# ELIMINAR
# ============================================================

@patch("models.Notas.obtener_conexion")
def test_eliminar_nota_manual(mock_obtener_conexion):
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()

    mock_obtener_conexion.return_value = mock_conexion
    mock_conexion.cursor.return_value = mock_cursor

    nota = Nota(
        id_nota=10,
        tipo="manual"
    )

    nota.eliminar()
    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM notas_usuario WHERE id_nota=%s",
        (10,)
    )

    mock_conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conexion.close.assert_called_once()


def test_eliminar_nota_sesion_lanza_error():
    nota = Nota(
        id_nota=10,
        tipo="sesion"
    )

    with pytest.raises(
        Exception,
        match="Las notas de sesión no se pueden eliminar"
    ):
        nota.eliminar()


# ============================================================
# TO_DICT
# ============================================================

def test_to_dict():
    nota = Nota(
        id_nota=1,
        id_usuario=2,
        id_libro=3,
        titulo="Mi nota",
        contenido="Contenido",
        categoria="Reflexión",
        fecha_creacion="2026-10-05",
        tipo="manual"
    )

    resultado = nota.to_dict()

    assert resultado == {
        "id_nota": 1,
        "id_libro": 3,
        "titulo": "Mi nota",
        "contenido": "Contenido",
        "categoria": "Reflexión",
        "fecha_creacion": "2026-10-05",
        "tipo": "manual"
    }


def test_to_dict_sin_fecha():
    nota = Nota(
        id_nota=1,
        id_libro=3,
        titulo="Nota",
        contenido="Contenido",
        categoria="General",
        fecha_creacion=None,
        tipo="manual"
    )

    resultado = nota.to_dict()

    assert resultado["fecha_creacion"] is None


# ============================================================
# FILTRAR
# ============================================================

@patch("models.Notas.obtener_conexion")
def test_filtrar_solo_por_usuario(mock_obtener_conexion):
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()

    mock_obtener_conexion.return_value = mock_conexion
    mock_conexion.cursor.return_value = mock_cursor

    notas = [
        {
            "id_nota": 1,
            "id_libro": 10,
            "titulo": "Nota 1",
            "contenido": "Contenido",
            "categoria": "General"
        }
    ]

    mock_cursor.fetchall.return_value = notas

    resultado = Nota.filtrar(5)

    assert resultado == notas

    query, valores = mock_cursor.execute.call_args[0]

    assert "WHERE n.id_usuario = %s" in query
    assert "ORDER BY n.fecha_creacion DESC" in query
    assert valores == [5]

    mock_cursor.close.assert_called_once()
    mock_conexion.close.assert_called_once()


@patch("models.Notas.obtener_conexion")
def test_filtrar_por_libro(mock_obtener_conexion):
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()

    mock_obtener_conexion.return_value = mock_conexion
    mock_conexion.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = []

    resultado = Nota.filtrar(
        id_usuario=5,
        id_libro=20
    )

    assert resultado == []

    query, valores = mock_cursor.execute.call_args[0]

    assert "n.id_libro = %s" in query
    assert valores == [5, 20]


@patch("models.Notas.obtener_conexion")
def test_filtrar_por_categoria(mock_obtener_conexion):
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()

    mock_obtener_conexion.return_value = mock_conexion
    mock_conexion.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = []

    resultado = Nota.filtrar(
        id_usuario=5,
        categoria="Reflexión"
    )

    assert resultado == []

    query, valores = mock_cursor.execute.call_args[0]

    assert "n.categoria = %s" in query
    assert valores == [5, "Reflexión"]


@patch("models.Notas.obtener_conexion")
def test_filtrar_por_libro_y_categoria(mock_obtener_conexion):
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()

    mock_obtener_conexion.return_value = mock_conexion
    mock_conexion.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = []

    resultado = Nota.filtrar(
        id_usuario=5,
        id_libro=20,
        categoria="Reflexión"
    )

    assert resultado == []

    query, valores = mock_cursor.execute.call_args[0]
    assert "n.id_libro = %s" in query
    assert "n.categoria = %s" in query
    assert valores == [5, 20, "Reflexión"]


@patch("models.Notas.obtener_conexion")
def test_filtrar_categoria_todos_no_aplica_filtro(
    mock_obtener_conexion
):
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()

    mock_obtener_conexion.return_value = mock_conexion
    mock_conexion.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = []

    resultado = Nota.filtrar(
        id_usuario=5,
        categoria="Todos"
    )

    assert resultado == []

    query, valores = mock_cursor.execute.call_args[0]

    assert "n.categoria = %s" not in query
    assert valores == [5]


# ============================================================
# GUARDAR NOTAS DE LECTURA
# ============================================================

@patch("models.Notas.obtener_conexion")
def test_guardar_notas_lectura(mock_obtener_conexion):
    mock_conexion = MagicMock()
    mock_cursor = MagicMock()

    mock_obtener_conexion.return_value = mock_conexion
    mock_conexion.cursor.return_value = mock_cursor

    Nota.guardar_notas_lectura(
        id_lectura=100,
        como_te_sientes="Feliz",
        continuara="Sí",
        notas="Me gustó mucho el capítulo.",
        tipo_reflexion="Personal",
        respuesta_reflexion="Me hizo reflexionar."
    )

    mock_cursor.execute.assert_called_once_with(
        """
            INSERT INTO notas_lectura
            (id_lectura, como_te_sientes, continuara, notas_observaciones, tipo_reflexion, respuesta_reflexion)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            100,
            "Feliz",
            "Sí",
            "Me gustó mucho el capítulo.",
            "Personal",
            "Me hizo reflexionar."
        )
    )

    mock_conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conexion.close.assert_called_once()