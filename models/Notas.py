

import mysql.connector
from db import obtener_conexion

class Nota:
    def __init__(self, id_nota=None, id_usuario=None, id_libro=None,
                 titulo=None, contenido=None, categoria=None,
                 fecha_creacion=None, tipo='manual'):

        self.id_nota = id_nota
        self.id_usuario = id_usuario
        self.id_libro = id_libro
        self.titulo = titulo
        self.contenido = contenido
        self.categoria = categoria
        self.fecha_creacion = fecha_creacion
        self.tipo = tipo

    @staticmethod
    def obtener_todas(id_usuario):

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        
        cursor.execute("""
            SELECT n.id_nota, n.id_libro, n.titulo, n.contenido, n.categoria, n.fecha_creacion,
                   l.titulo as libro_titulo, l.autor as libro_autor, l.portada,
                   'manual' as tipo
            FROM notas_usuario n
            LEFT JOIN libros l ON n.id_libro = l.id_libro
            WHERE n.id_usuario = %s
            ORDER BY n.fecha_creacion DESC
        """, (id_usuario,))
        notas_manuales = cursor.fetchall()


        cursor.execute("""
            SELECT nl.id_nota, nl.como_te_sientes, nl.que_aprendiste, nl.palabras_nuevas,
                   nl.personaje_destacado, nl.escena_impacto, nl.parecer_sesion,
                   nl.recuerdo_vida, nl.notas_observaciones, nl.buscaba_al_leer,
                   nl.encontro_lo_buscado, nl.tipo_reflexion, nl.respuesta_reflexion,
                   lec.fecha_fin as fecha_creacion,
                   l.id_libro, l.titulo as libro_titulo, l.autor as libro_autor, l.portada,
                   'sesion' as tipo
            FROM notas_lectura nl
            JOIN lecturas lec ON nl.id_lectura = lec.id_lectura
            JOIN libros l ON lec.id_libro = l.id_libro
            WHERE lec.id_usuario = %s AND lec.fecha_fin IS NOT NULL
            ORDER BY lec.fecha_fin DESC
        """, (id_usuario,))
        notas_sesion = cursor.fetchall()

        cursor.close()
        conexion.close()
        return notas_manuales, notas_sesion

    @staticmethod
    def crear(id_usuario, id_libro, titulo, contenido, categoria):
        """Crea una nota manual nueva (siempre tipo='manual') y devuelve el objeto Nota resultante."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO notas_usuario (id_usuario, id_libro, titulo, contenido, categoria, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, CURDATE())
        """, (id_usuario, id_libro, titulo, contenido, categoria))
        conexion.commit()
        id_nueva = cursor.lastrowid  
        cursor.close()
        conexion.close()
        return Nota(
            id_nota=id_nueva,
            id_usuario=id_usuario,
            id_libro=id_libro,
            titulo=titulo,
            contenido=contenido,
            categoria=categoria,
            tipo='manual'
        )

    def editar(self, titulo=None, contenido=None, categoria=None):
        """Edita una nota manual completa. Las notas de sesión no pueden editarse por este método."""
        if self.tipo != 'manual':
            raise Exception("Solo notas manuales son editables completas")
        
        self.titulo = titulo or self.titulo
        self.contenido = contenido or self.contenido
        self.categoria = categoria or self.categoria
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE notas_usuario SET titulo=%s, contenido=%s, categoria=%s
            WHERE id_nota=%s
        """, (self.titulo, self.contenido, self.categoria, self.id_nota))
        conexion.commit()
        cursor.close()
        conexion.close()

    def editar_campo_sesion(self, campo, valor):

        campos_permitidos = [
            'como_te_sientes', 'que_aprendiste', 'palabras_nuevas',
            'personaje_destacado', 'escena_impacto', 'parecer_sesion',
            'recuerdo_vida', 'notas_observaciones', 'respuesta_reflexion'
        ]
        if campo not in campos_permitidos:
            raise Exception("Campo no permitido")
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            f"UPDATE notas_lectura SET {campo}=%s WHERE id_nota=%s",
            (valor, self.id_nota)
        )
        conexion.commit()
        cursor.close()
        conexion.close()

    def eliminar(self):

        if self.tipo != 'manual':
            raise Exception("Las notas de sesión no se pueden eliminar")
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM notas_usuario WHERE id_nota=%s", (self.id_nota,))
        conexion.commit()
        cursor.close()
        conexion.close()

    def to_dict(self):

        return {
            'id_nota': self.id_nota,
            'id_libro': self.id_libro,
            'titulo': self.titulo,
            'contenido': self.contenido,
            'categoria': self.categoria,
            'fecha_creacion': str(self.fecha_creacion) if self.fecha_creacion else None,
            'tipo': self.tipo
        }

    @staticmethod
    def filtrar(id_usuario, id_libro=None, categoria=None):

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        query = """
            SELECT n.id_nota, n.id_libro, n.titulo, n.contenido, n.categoria, n.fecha_creacion
            FROM notas_usuario n
            WHERE n.id_usuario = %s
        """
        valores = [id_usuario]

        if id_libro:
            query += " AND n.id_libro = %s"
            valores.append(id_libro)

        if categoria and categoria != 'Todos':
            query += " AND n.categoria = %s"
            valores.append(categoria)

        query += " ORDER BY n.fecha_creacion DESC"
        cursor.execute(query, valores)
        notas = cursor.fetchall()
        cursor.close()
        conexion.close()
        return notas
    @staticmethod
    def guardar_notas_lectura(id_lectura, como_te_sientes, continuara, notas, tipo_reflexion, respuesta_reflexion):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO notas_lectura
            (id_lectura, como_te_sientes, continuara, notas_observaciones, tipo_reflexion, respuesta_reflexion)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id_lectura, como_te_sientes, continuara, notas, tipo_reflexion, respuesta_reflexion))
        conexion.commit()
        cursor.close()
        conexion.close()
