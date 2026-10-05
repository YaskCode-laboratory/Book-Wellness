import sys
import os
from flask import Blueprint, render_template, request, redirect, url_for
from itsdangerous import (
    URLSafeTimedSerializer,
    SignatureExpired,
    BadTimeSignature,
    BadSignature
)
from db import obtener_conexion
from werkzeug.security import generate_password_hash

# Importación flexible de enviar_correo según la ubicación del ejecutor
try:
    from .notificaciones import enviar_correo
except (ImportError, ModuleNotFoundError):
    try:
        from models.notificaciones import enviar_correo
    except (ImportError, ModuleNotFoundError):
        from notificaciones import enviar_correo

recuperacion_bp = Blueprint('recuperacion', __name__)

# Clave secreta para firmar el token
SECRET_KEY = os.getenv("SECRET_KEY")
serializer = URLSafeTimedSerializer(SECRET_KEY)


@recuperacion_bp.route('/recuperar', methods=['GET', 'POST'])
def solicitar_recuperacion():
    if request.method == 'POST':
        correo = request.form.get('correo')

        # 1. Verificar si el usuario existe en MySQL
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()

        if usuario:
            # 2. Generar token firmado con el correo del usuario
            token = serializer.dumps(correo, salt='recuperar-contrasena')

            # 3. Crear enlace absoluto de confirmación
            link_recuperacion = url_for('recuperacion.restablecer_contrasena', token=token, _external=True)

            # 4. Enviar correo electrónico
            asunto = "🔐 Book Wellness - Restablecer Contraseña"
            cuerpo = (
                f"Hola {usuario['nombre']},\n\n"
                f"Hemos recibido una solicitud para cambiar tu contraseña en Book Wellness.\n"
                f"Haz clic en el siguiente enlace para restablecerla (válido por 15 minutos):\n\n"
                f"{link_recuperacion}\n\n"
                f"Si no solicitaste este cambio, puedes ignorar este mensaje de forma segura.\n\n"
                f"Atentamente,\nEl equipo de Book Wellness"
            )

            enviar_correo(correo, asunto, cuerpo)

        # Renderizar la vista dentro de la carpeta HTML SESION
        return render_template('HTML SESION/CodigoEnviado.html')

    return render_template('HTML SESION/¿OlvidasteContrasena.html')


@recuperacion_bp.route('/restablecer/<token>', methods=['GET', 'POST'])
def restablecer_contrasena(token):
    try:
        # Validar token (expira en 900 segundos / 15 minutos)
        correo = serializer.loads(token, salt='recuperar-contrasena', max_age=900)
    except (SignatureExpired, BadTimeSignature, BadSignature):
        return "<h3>El enlace de recuperación es inválido o ha expirado. Por favor, solicita uno nuevo.</h3>", 400

    if request.method == 'POST':
        nueva_password = request.form.get('password')

        if not nueva_password:
            return "La contraseña no puede estar vacía", 400

        # Actualizar contraseña en MySQL
        password_hash = generate_password_hash(nueva_password)

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            "UPDATE usuarios SET password = %s WHERE correo = %s",
            (password_hash, correo)
        )

        print("Correo recibido:", correo)
        print("Filas modificadas:", cursor.rowcount)

        conexion.commit()

        cursor.close()
        conexion.close()



        # Ajusta 'usuarios.iniciar_sesion' o la ruta correspondiente a tu vista de login
        return redirect('/sesion')
    
    return render_template('HTML SESION/nuevacontraseña.html', token=token)
