import mysql.connector
from db import obtener_conexion
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario:

    def __init__(
        self,
        id_usuario=None,
        nombre=None,
        correo=None,
        password=None,
        nivel_actual=None
    ):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.correo = correo
        self.password = password
        self.nivel_actual = nivel_actual

    def registrar(self):
        """Registra el usuario en la base de datos."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        password_hash = generate_password_hash(self.password)

        cursor.execute("""
            INSERT INTO usuarios
            (
                nombre,
                correo,
                password,
                nivel_actual
            )
            VALUES (%s, %s, %s, %s)
        """, (
            self.nombre,
            self.correo,
            password_hash,
            self.nivel_actual
        ))

        conexion.commit()
        self.id_usuario = cursor.lastrowid

        cursor.execute("DELETE FROM usuario_encuesta_temporal")

        cursor.execute("""
            INSERT INTO usuario_encuesta_temporal (id_usuario)
            VALUES (%s)
        """, (self.id_usuario,))

        conexion.commit()

        cursor.close()
        conexion.close()

        return self.id_usuario



    @classmethod
    def iniciar_sesion(cls, correo, password):
        """Valida credenciales y dispara las notificaciones pendientes."""
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_usuario,
                nombre,
                correo,
                password,
                recomendacion_inicial_generada
            FROM usuarios
            WHERE correo = %s
        """, (
            correo,
        ))


        datos = cursor.fetchone()

        cursor.close()
        conexion.close()

        if not datos:
            return None

        if not check_password_hash(datos["password"], password):
            return None


        usuario_logeado = cls(
            id_usuario=datos["id_usuario"],
            nombre=datos["nombre"],
            correo=datos["correo"]
        )

        # Import local para evitar el import circular
        try:
            try:
                from .notificaciones import procesar_notificaciones_al_iniciar_sesion
            except (ImportError, ModuleNotFoundError):
                from models.notificaciones import procesar_notificaciones_al_iniciar_sesion

            procesar_notificaciones_al_iniciar_sesion(usuario_logeado.id_usuario)
        except Exception as e:
            print(f"[ADVERTENCIA] No se pudieron enviar las notificaciones en login: {e}")

        return usuario_logeado

    @staticmethod
    def obtener_estado_notificaciones(id_usuario):
        """Devuelve True si el usuario tiene notificaciones activas en BD, False si no."""
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT notificaciones_activadas 
            FROM usuarios 
            WHERE id_usuario = %s
        """, (id_usuario,))

        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()

        if resultado and resultado.get("notificaciones_activadas") is not None:
            return bool(resultado["notificaciones_activadas"])
        return True

    @staticmethod
    def cambiar_estado_notificaciones(id_usuario, nuevo_estado):
        """Actualiza la preferencia de notificaciones en la base de datos."""
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE usuarios 
            SET notificaciones_activadas = %s 
            WHERE id_usuario = %s
        """, (1 if nuevo_estado else 0, id_usuario))

        conexion.commit()
        cursor.close()
        conexion.close()

    def cerrar_sesion(self):
        pass
