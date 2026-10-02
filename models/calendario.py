
from db import obtener_conexion

class Calendario:

    @staticmethod
    def obtener_fechas_calendario(id_usuario):

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT DATE(fecha_inicio) as fecha, 'primera_sesion' as tipo
            FROM lecturas
            WHERE id_usuario = %s AND fecha_inicio IS NOT NULL

            UNION

            SELECT DATE(fecha_limite) as fecha,
                CASE WHEN fecha_limite < CURDATE() THEN 'expirada' ELSE 'fecha_limite' END as tipo
            FROM lecturas
            WHERE id_usuario = %s AND fecha_limite IS NOT NULL
            AND estado != 'He terminado el libro'

            UNION

            SELECT DATE(fecha_fin) as fecha, 'concluido' as tipo
            FROM lecturas
            WHERE id_usuario = %s AND fecha_fin IS NOT NULL
            AND estado = 'He terminado el libro'

            UNION

            SELECT DATE(fecha) as fecha, 'sesion' as tipo
            FROM sesiones
            WHERE id_usuario = %s AND fecha IS NOT NULL
        """, (id_usuario, id_usuario, id_usuario, id_usuario))

        filas = cursor.fetchall()
        cursor.close()
        conexion.close()

        fechas = {}
        for fila in filas:
            fecha_str = str(fila['fecha'])
            if fecha_str not in fechas:
                fechas[fecha_str] = fila['tipo']
            else:
                prioridad = {'concluido': 4, 'fecha_limite': 3, 'primera_sesion': 2, 'sesion': 1}
                if prioridad.get(fila['tipo'], 0) > prioridad.get(fechas[fecha_str], 0):
                    fechas[fecha_str] = fila['tipo']

        return fechas

    @staticmethod
    def obtener_libros_por_fecha(id_usuario, fecha):
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT l.titulo, l.autor, l.portada, l.id_libro,
                   'sesion' as tipo
            FROM lecturas lec
            JOIN libros l ON lec.id_libro = l.id_libro
            WHERE lec.id_usuario = %s AND DATE(lec.fecha_inicio) = %s
            UNION
            SELECT l.titulo, l.autor, l.portada, l.id_libro,
                   'fecha_limite' as tipo
            FROM lecturas lec
            JOIN libros l ON lec.id_libro = l.id_libro
            WHERE lec.id_usuario = %s AND DATE(lec.fecha_limite) = %s
        """, (id_usuario, fecha, id_usuario, fecha))
        libros = cursor.fetchall()
        cursor.close()
        conexion.close()
        return libros

    @staticmethod
    def guardar_fecha_limite(id_usuario, id_libro, fecha_limite):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE lecturas SET fecha_limite = %s
            WHERE id_usuario = %s AND id_libro = %s
        """, (fecha_limite, id_usuario, id_libro))
        conexion.commit()
        cursor.close()
        conexion.close()

    @staticmethod
    def obtener_actividades_usuarios_por_fecha(fecha):
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT u.id_usuario, u.nombre, u.correo, l.titulo, 'sesion' AS tipo
            FROM lecturas lec
            JOIN usuarios u ON lec.id_usuario = u.id_usuario
            JOIN libros l ON lec.id_libro = l.id_libro
            WHERE DATE(lec.fecha_inicio) = %s AND lec.fecha_inicio IS NOT NULL
            
            UNION ALL
            
            SELECT u.id_usuario, u.nombre, u.correo, l.titulo, 'fin_libro' AS tipo
            FROM lecturas lec
            JOIN usuarios u ON lec.id_usuario = u.id_usuario
            JOIN libros l ON lec.id_libro = l.id_libro
            WHERE DATE(lec.fecha_limite) = %s AND lec.fecha_limite IS NOT NULL
        """, (fecha, fecha))

        filas = cursor.fetchall()
        cursor.close()
        conexion.close()

        usuarios = {}
        for fila in filas:
            uid = fila['id_usuario']
            if uid not in usuarios:
                usuarios[uid] = {
                    'id_usuario': uid,
                    'nombre': fila['nombre'],
                    'correo': fila['correo'],
                    'eventos': []
                }
            usuarios[uid]['eventos'].append({
                'titulo': fila['titulo'],
                'tipo': fila['tipo']
            })

        return list(usuarios.values())
