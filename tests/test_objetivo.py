import pytest
from unittest.mock import MagicMock, patch

from models.Objetivo import Objetivo


# ============================================================
# PRUEBAS DE actualizar_progreso()
# ============================================================

def test_actualizar_progreso_suma_cantidad():
    objetivo = Objetivo(
        id_usuario=1,
        titulo="Leer",
        descripcion="Leer libros",
        tipo="paginas",
        meta=100,
        progreso_actual=20
    )

    objetivo.actualizar_progreso(30)

    assert objetivo.progreso_actual == 50
    assert objetivo.completado is False
    assert objetivo.estado == "activo"


def test_actualizar_progreso_completa_objetivo():
    objetivo = Objetivo(
        id_usuario=1,
        titulo="Leer",
        descripcion="Leer libros",
        tipo="paginas",
        meta=100,
        progreso_actual=80
    )

    objetivo.actualizar_progreso(20)

    assert objetivo.progreso_actual == 100
    assert objetivo.completado is True
    assert objetivo.estado == "completado"


def test_actualizar_progreso_no_supera_meta():
    objetivo = Objetivo(
        id_usuario=1,
        titulo="Leer",
        descripcion="Leer libros",
        tipo="paginas",
        meta=100,
        progreso_actual=80
    )

    objetivo.actualizar_progreso(50)

    assert objetivo.progreso_actual == 100
    assert objetivo.completado is True
    assert objetivo.estado == "completado"


# ============================================================
# PRUEBAS DE obtener_porcentaje()
# ============================================================

def test_obtener_porcentaje_correcto():
    objetivo = Objetivo(
        id_usuario=1,
        titulo="Leer",
        descripcion="",
        tipo="paginas",
        meta=200,
        progreso_actual=50
    )

    assert objetivo.obtener_porcentaje() == 25


def test_obtener_porcentaje_cero():
    objetivo = Objetivo(
        id_usuario=1,
        titulo="Leer",
        descripcion="",
        tipo="paginas",
        meta=200,
        progreso_actual=0
    )

    assert objetivo.obtener_porcentaje() == 0


def test_obtener_porcentaje_no_supera_100():
    objetivo = Objetivo(
        id_usuario=1,
        titulo="Leer",
        descripcion="",
        tipo="paginas",
        meta=100,
        progreso_actual=150
    )

    assert objetivo.obtener_porcentaje() == 100


def test_obtener_porcentaje_meta_cero():
    objetivo = Objetivo(
        id_usuario=1,
        titulo="Leer",
        descripcion="",
        tipo="paginas",
        meta=0,
        progreso_actual=0
    )

    assert objetivo.obtener_porcentaje() == 0


# ============================================================
# PRUEBAS DE esta_completado()
# ============================================================

def test_esta_completado_false():
    objetivo = Objetivo(
        id_usuario=1,
        titulo="Leer",
        descripcion="",
        tipo="paginas",
        meta=100,
        progreso_actual=50
    )

    assert objetivo.esta_completado() is False


def test_esta_completado_true():
    objetivo = Objetivo(
        id_usuario=1,
        titulo="Leer",
        descripcion="",
        tipo="paginas",
        meta=100,
        progreso_actual=100
    )

    assert objetivo.esta_completado() is True


def test_esta_completado_supera_meta():
    objetivo = Objetivo(
        id_usuario=1,
        titulo="Leer",
        descripcion="",
        tipo="paginas",
        meta=100,
        progreso_actual=120
    )

    assert objetivo.esta_completado() is True


# ============================================================
# PRUEBAS DE _aplicar_condicion()
# ============================================================

def crear_objetivo_con_condicion(condicion_tipo, condicion_valor):
    return Objetivo(
        id_usuario=1,
        titulo="Objetivo",
        descripcion="",
        tipo="libros",
        meta=5,
        condicion_tipo=condicion_tipo,
        condicion_valor=condicion_valor
    )
def test_aplicar_condicion_ninguna():
    objetivo = crear_objetivo_con_condicion("ninguna", None)

    sql = "SELECT * FROM libros WHERE 1=1"
    valores = []

    nuevo_sql, nuevos_valores = objetivo._aplicar_condicion(
        sql,
        valores
    )

    assert nuevo_sql == sql
    assert nuevos_valores == []


def test_aplicar_condicion_genero():
    objetivo = crear_objetivo_con_condicion(
        "genero",
        "Fantasía"
    )

    sql = "SELECT * FROM libros WHERE 1=1"
    valores = []

    nuevo_sql, nuevos_valores = objetivo._aplicar_condicion(
        sql,
        valores
    )

    assert "b.genero LIKE %s" in nuevo_sql
    assert nuevos_valores == ["%Fantasía%"]


def test_aplicar_condicion_autor():
    objetivo = crear_objetivo_con_condicion(
        "autor",
        "J.K. Rowling"
    )

    sql = "SELECT * FROM libros WHERE 1=1"
    valores = []

    nuevo_sql, nuevos_valores = objetivo._aplicar_condicion(
        sql,
        valores
    )

    assert "b.autor LIKE %s" in nuevo_sql
    assert nuevos_valores == ["%J.K. Rowling%"]


def test_aplicar_condicion_formato():
    objetivo = crear_objetivo_con_condicion(
        "formato",
        "Ebook"
    )

    sql = "SELECT * FROM libros WHERE 1=1"
    valores = []

    nuevo_sql, nuevos_valores = objetivo._aplicar_condicion(
        sql,
        valores
    )

    assert "b.formato LIKE %s" in nuevo_sql
    assert nuevos_valores == ["%Ebook%"]


def test_aplicar_condicion_libro():
    objetivo = crear_objetivo_con_condicion(
        "libro",
        "Harry Potter"
    )

    sql = "SELECT * FROM libros WHERE 1=1"
    valores = []

    nuevo_sql, nuevos_valores = objetivo._aplicar_condicion(
        sql,
        valores
    )

    assert "b.titulo LIKE %s" in nuevo_sql
    assert nuevos_valores == ["%Harry Potter%"]


# ============================================================
# PRUEBA DE to_dict()
# ============================================================

def test_to_dict():
    objetivo = Objetivo(
        id_objetivo=10,
        id_usuario=1,
        titulo="Leer 100 páginas",
        descripcion="Leer durante la semana",
        tipo="paginas",
        meta=100,
        unidad="páginas",
        progreso_actual=50,
        fecha_inicio="2026-10-01",
        fecha_fin="2026-10-07",
        condicion_tipo="genero",
        condicion_valor="Fantasía",
        frecuencia="semanal",
        estado="activo"
    )

    resultado = objetivo.to_dict()

    assert resultado["id_objetivo"] == 10
    assert resultado["id_usuario"] == 1
    assert resultado["titulo"] == "Leer 100 páginas"
    assert resultado["tipo"] == "paginas"
    assert resultado["meta"] == 100
    assert resultado["unidad"] == "páginas"
    assert resultado["progreso_actual"] == 50
    assert resultado["porcentaje"] == 50
    assert resultado["fecha_inicio"] == "2026-10-01"
    assert resultado["fecha_fin"] == "2026-10-07"
    assert resultado["condicion_tipo"] == "genero"
    assert resultado["condicion_valor"] == "Fantasía"
    assert resultado["frecuencia"] == "semanal"
    assert resultado["estado"] == "activo"


# ============================================================
# PRUEBAS DE calcular_progreso()
# ============================================================

@patch("models.Objetivo.obtener_conexion")
def test_calcular_progreso_paginas(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = {
        "total": 75
    }

    objetivo = Objetivo(
        id_usuario=1,
        titulo="Leer páginas",
        descripcion="",
        tipo="paginas",
        meta=100,
        fecha_inicio="2026-10-01"
    )

    resultado = objetivo.calcular_progreso()

    assert resultado == 75
    assert objetivo.progreso_actual == 75
    assert objetivo.completado is False
    assert objetivo.estado == "activo"

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()

@patch("models.Objetivo.obtener_conexion")
def test_calcular_progreso_paginas_completado(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = {
        "total": 150
    }

    objetivo = Objetivo(
        id_usuario=1,
        titulo="Leer páginas",
        descripcion="",
        tipo="paginas",
        meta=100,
        fecha_inicio="2026-10-01"
    )

    resultado = objetivo.calcular_progreso()

    assert resultado == 100
    assert objetivo.progreso_actual == 100
    assert objetivo.completado is True
    assert objetivo.estado == "completado"


@patch("models.Objetivo.obtener_conexion")
def test_calcular_progreso_tiempo(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = {
        "total": 120
    }

    objetivo = Objetivo(
        id_usuario=1,
        titulo="Leer durante 120 minutos",
        descripcion="",
        tipo="tiempo",
        meta=180,
        fecha_inicio="2026-10-01"
    )

    resultado = objetivo.calcular_progreso()

    assert resultado == 120
    assert objetivo.progreso_actual == 120
    assert objetivo.completado is False


@patch("models.Objetivo.obtener_conexion")
def test_calcular_progreso_libros(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = {
        "total": 3
    }

    objetivo = Objetivo(
        id_usuario=1,
        titulo="Terminar libros",
        descripcion="",
        tipo="libros",
        meta=5,
        fecha_inicio="2026-10-01"
    )

    resultado = objetivo.calcular_progreso()

    assert resultado == 3
    assert objetivo.progreso_actual == 3
    assert objetivo.completado is False


@patch("models.Objetivo.obtener_conexion")
def test_calcular_progreso_rutina(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = {
        "total_dias": 4
    }

    objetivo = Objetivo(
        id_usuario=1,
        titulo="Leer 7 días",
        descripcion="",
        tipo="rutina",
        meta=7,
        fecha_inicio="2026-10-01"
    )

    resultado = objetivo.calcular_progreso()

    assert resultado == 4
    assert objetivo.progreso_actual == 4
    assert objetivo.completado is False


# ============================================================
# PRUEBA DE crear()
# ============================================================

@patch("models.Objetivo.obtener_conexion")
def test_crear_objetivo(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor
    cursor.lastrowid = 25

    objetivo = Objetivo(
        id_usuario=1,
        titulo="Leer 5 libros",
        descripcion="Terminar cinco libros",
        tipo="libros",
        meta=5,
        unidad="libros"
    )

    resultado = Objetivo.crear(objetivo)

    assert resultado is objetivo
    assert objetivo.id_objetivo == 25

    cursor.execute.assert_called_once()
    conexion.commit.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


# ============================================================
# PRUEBA DE obtener_por_id()
# ============================================================

@patch("models.Objetivo.obtener_conexion")
def test_obtener_por_id(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor
    cursor.fetchone.return_value = {
        "id_objetivo": 10,
        "id_usuario": 1,
        "titulo": "Leer 5 libros",
        "descripcion": "Terminar cinco libros",
        "tipo": "libros",
        "meta": 5,
        "unidad": "libros",
        "fecha_inicio": None,
        "fecha_fin": None,
        "condicion_tipo": None,
        "condicion_valor": None,
        "frecuencia": None,
        "progreso_actual": 2,
        "completado": 0,
        "estado": "activo"
    }

    objetivo = Objetivo.obtener_por_id(10)

    assert objetivo is not None
    assert objetivo.id_objetivo == 10
    assert objetivo.id_usuario == 1
    assert objetivo.titulo == "Leer 5 libros"
    assert objetivo.tipo == "libros"
    assert objetivo.meta == 5
    assert objetivo.progreso_actual == 2

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.Objetivo.obtener_conexion")
def test_obtener_por_id_no_existente(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchone.return_value = None

    resultado = Objetivo.obtener_por_id(999)

    assert resultado is None


# ============================================================
# PRUEBA DE eliminar()
# ============================================================

@patch("models.Objetivo.obtener_conexion")
def test_eliminar_objetivo(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.rowcount = 1

    resultado = Objetivo.eliminar(10)

    assert resultado is True

    cursor.execute.assert_called_once()
    conexion.commit.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


@patch("models.Objetivo.obtener_conexion")
def test_eliminar_objetivo_no_existente(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.rowcount = 0

    resultado = Objetivo.eliminar(999)

    assert resultado is False


# ============================================================
# PRUEBA DE obtener_usuarios_con_objetivos_por_vencer()
# ============================================================

@patch("models.Objetivo.obtener_conexion")
def test_obtener_usuarios_con_objetivos_por_vencer(mock_obtener_conexion):
    conexion = MagicMock()
    cursor = MagicMock()

    mock_obtener_conexion.return_value = conexion
    conexion.cursor.return_value = cursor

    cursor.fetchall.return_value = [
        {
            "id_usuario": 1,
            "nombre": "Juan",
            "correo": "juan@email.com",
            "notificaciones_activadas": 1,
            "titulo": "Leer 5 libros"
        },
        {
            "id_usuario": 1,
            "nombre": "Juan",
            "correo": "juan@email.com",
            "notificaciones_activadas": 1,
            "titulo": "Leer 100 páginas"
        },
        {
            "id_usuario": 2,
            "nombre": "Ana",
            "correo": "ana@email.com",
            "notificaciones_activadas": 0,
            "titulo": "Leer 3 libros"
        }
    ]

    resultado = Objetivo.obtener_usuarios_con_objetivos_por_vencer(
        "2026-10-05"
    )

    assert len(resultado) == 2

    assert resultado[0]["id_usuario"] == 1
    assert resultado[0]["nombre"] == "Juan"
    assert len(resultado[0]["objetivos"]) == 2

    assert "Leer 5 libros" in resultado[0]["objetivos"]
    assert "Leer 100 páginas" in resultado[0]["objetivos"]

    assert resultado[1]["id_usuario"] == 2
    assert resultado[1]["objetivos"] == ["Leer 3 libros"]

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()