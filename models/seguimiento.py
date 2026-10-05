from datetime import datetime

from db import obtener_conexion

class Seguimiento:


    @staticmethod
    def _clave_orden(ev):
        valor = ev.get('fecha') or ev.get('fecha_limite') or ev.get('fecha_fin')

        if not valor:
            return datetime.min

        try:
            if ' ' in valor:
                return datetime.strptime(valor, '%Y-%m-%d %H:%M:%S')
            else:
                return datetime.strptime(valor, '%Y-%m-%d')
        except (ValueError, TypeError):
            return datetime.min



    @staticmethod
    def obtener_eventos_por_fecha(id_usuario, fecha):
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)


        

        # Fechas límite
        cursor.execute("""
            SELECT l.titulo, l.autor, l.portada, l.id_libro,
                lec.fecha_limite, lec.fecha_fin, lec.estado,
                CASE WHEN lec.fecha_limite < CURDATE() AND lec.estado != 'He terminado el libro'
                     THEN 'expirada' ELSE 'fecha_limite' END as tipo
            FROM lecturas lec
            JOIN libros l ON lec.id_libro = l.id_libro
            WHERE lec.id_usuario = %s AND DATE(lec.fecha_limite) = %s
        """, (id_usuario, fecha))
        limites = cursor.fetchall()

        # Sesiones individuales

        cursor.execute("""
            SELECT l.titulo, l.autor, l.portada, l.id_libro,
                s.paginas_leidas_sesion as paginas_leidas,
                s.tiempo_minutos, s.fecha, s.capitulos_leidos,
                s.como_te_sientes, 'sesion' as tipo
            FROM sesiones s
            JOIN lecturas lec ON s.id_lectura = lec.id_lectura
            JOIN libros l ON lec.id_libro = l.id_libro
            WHERE s.id_usuario = %s AND DATE(s.fecha) = %s
            AND s.id_sesion != (
                SELECT MIN(s2.id_sesion)
                FROM sesiones s2
                WHERE s2.id_lectura = lec.id_lectura
            )
        """, (id_usuario, fecha))
        sesiones = cursor.fetchall()
        
        for ev in sesiones:
            if ev.get('fecha'):
                ev['fecha'] = str(ev['fecha'])

        # Primera sesión de cada libro 
        cursor.execute("""
            SELECT l.titulo, l.autor, l.portada, l.id_libro,
                s.paginas_leidas_sesion as paginas_leidas,
                s.tiempo_minutos, s.fecha, s.capitulos_leidos,
                s.como_te_sientes,
                'primera_sesion' as tipo
            FROM sesiones s
            JOIN lecturas lec ON s.id_lectura = lec.id_lectura
            JOIN libros l ON lec.id_libro = l.id_libro
            WHERE s.id_usuario = %s
            AND s.id_sesion = (
                SELECT MIN(s2.id_sesion)
                FROM sesiones s2
                WHERE s2.id_lectura = lec.id_lectura
            )
            AND DATE(s.fecha) = %s
        """, (id_usuario, fecha))
        primeras_sesiones = cursor.fetchall()

        for ev in primeras_sesiones:
            if ev.get('fecha'):
                ev['fecha'] = str(ev['fecha'])

        # Concluidos
        cursor.execute("""
            SELECT l.titulo, l.autor, l.portada, l.id_libro,
                lec.fecha_fin, lec.paginas_leidas, lec.tiempo_minutos,
                'concluido' as tipo
            FROM lecturas lec
            JOIN libros l ON lec.id_libro = l.id_libro
            WHERE lec.id_usuario = %s AND DATE(lec.fecha_fin) = %s
            AND lec.estado = 'He terminado el libro'
        """, (id_usuario, fecha))
        concluidos = cursor.fetchall()

        cursor.close()
        conexion.close()

        for ev in sesiones:
            if ev.get('fecha'):
                ev['fecha'] = str(ev['fecha'])

        for ev in limites:
            if ev.get('fecha_limite'):
                ev['fecha_limite'] = str(ev['fecha_limite'])

        for ev in concluidos:
            if ev.get('fecha_fin'):
                ev['fecha_fin'] = str(ev['fecha_fin'])

        todos_eventos = primeras_sesiones + sesiones + limites + concluidos
        todos_eventos.sort(key=Seguimiento._clave_orden)

        return todos_eventos

