# database.py
import mysql.connector
import os

def obtener_conexion():
    return mysql.connector.connect(
        user='root',
        password='',
        host='localhost',
        database='proyectowellness',
        port=3306
    )


def guardar_recomendaciones(id_usuario, libros):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    # Borrar recomendaciones anteriores
    cursor.execute("DELETE FROM recomendaciones_cache WHERE id_usuario = %s", (id_usuario,))
    
    # Insertar nuevas
    for libro in libros:
        cursor.execute("""
            INSERT INTO recomendaciones_cache
            (
                id_usuario,
                titulo,
                autor,
                descripcion,
                portada,
                paginas,
                generos,
                anio,
                id_google,
                `key`
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            id_usuario,
            libro.get('titulo'),
            libro.get('autor'),
            libro.get('descripcion'),
            libro.get('portada'),
            libro.get('paginas'),
            libro.get('generos'),
            libro.get('anio'),
            libro.get('id_google'),
            libro.get('key')
        ))

    
    conexion.commit()
    cursor.close()
    conexion.close()

def obtener_recomendaciones_cache(id_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM recomendaciones_cache 
        WHERE id_usuario = %s
        ORDER BY fecha_generacion DESC
    """, (id_usuario,))
    libros = cursor.fetchall()
    cursor.close()
    conexion.close()
    return libros


def invalidar_cache_recomendaciones(id_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "DELETE FROM recomendaciones_cache WHERE id_usuario = %s",
        (id_usuario,)
    )
    conexion.commit()
    cursor.close()
    conexion.close()

##########################################################
# GUARDAR MENSAJE DE IA
##########################################################

def guardar_mensaje(id_usuario, rol, mensaje):

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute(
        """
        INSERT INTO conversaciones
        (
            id_usuario,
            rol,
            mensaje
        )
        VALUES
        (
            %s,
            %s,
            %s
        )
        """,
        (
            id_usuario,
            rol,
            mensaje
        )
    )

    conexion.commit()

    cursor.close()
    conexion.close()

def obtener_estado_recomendacion_inicial(id_usuario):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT recomendacion_inicial_generada
        FROM usuarios
        WHERE id_usuario = %s
    """, (id_usuario,))

    resultado = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not resultado:
        return False

    return resultado[0] == 1


##########################################################
# OBTENER HISTORIAL IA
##########################################################

def obtener_historial(id_usuario, limite=20):

    conexion = obtener_conexion()

    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            rol,
            mensaje
        FROM conversaciones
        WHERE id_usuario = %s
        ORDER BY fecha DESC
        LIMIT %s
        """,
        (
            id_usuario,
            limite
        )
    )

    historial = cursor.fetchall()

    cursor.close()
    conexion.close()

    historial.reverse()

    return historial

