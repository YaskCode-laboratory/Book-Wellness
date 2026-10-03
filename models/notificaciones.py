import sys
import os
from datetime import date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, jsonify, session

# Importación flexible de módulos usando la ruta relativa del paquete
try:
    from .calendario import Calendario
    from .Objetivo import Objetivo
    from .Usuario import Usuario
except (ImportError, ModuleNotFoundError):
    try:
        from models.calendario import Calendario
        from models.Objetivo import Objetivo
        from models.Usuario import Usuario
    except (ImportError, ModuleNotFoundError):
        DIR_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if DIR_RAIZ not in sys.path:
            sys.path.insert(0, DIR_RAIZ)
        from calendario import Calendario
        from Objetivo import Objetivo
        from Usuario import Usuario

# ==========================================
# BLUEPRINT DE FLASK PARA NOTIFICACIONES
# ==========================================
notificaciones_bp = Blueprint('notificaciones', __name__)

@notificaciones_bp.route('/notificaciones/estado', methods=['GET'])
def estado_notificaciones():
    """Consulta el estado de las notificaciones desde MySQL."""
    id_usuario = session.get('usuario_id') or session.get('id_usuario')
    
    if not id_usuario:
        return jsonify({'activadas': True}), 200

    activadas = Usuario.obtener_estado_notificaciones(id_usuario)
    return jsonify({'activadas': activadas}), 200


@notificaciones_bp.route('/notificaciones/toggle', methods=['POST'])
def toggle_notificaciones():
    """Alterna el estado de las notificaciones y lo guarda en MySQL."""
    id_usuario = session.get('usuario_id') or session.get('id_usuario')
    
    if not id_usuario:
        return jsonify({'error': 'Usuario no autenticado'}), 401

    estado_actual = Usuario.obtener_estado_notificaciones(id_usuario)
    nuevo_estado = not estado_actual

    Usuario.cambiar_estado_notificaciones(id_usuario, nuevo_estado)
    session['notificaciones_activas'] = nuevo_estado

    print(f"[NOTIFICACIONES] Estado actualizado a {nuevo_estado} para el usuario ID {id_usuario}")

    return jsonify({'activadas': nuevo_estado}), 200


# ==========================================
# CONFIGURACIÓN DE GMAIL Y ENVÍO DE CORREOS
# ==========================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
CORREO_EMISOR = "bookwellnesscontacto@gmail.com"
PASSWORD_EMISOR = os.getenv("PASSWORD_EMISOR")


def enviar_correo(destinatario, asunto, cuerpo):
    """Envía un correo electrónico mediante smtplib."""
    msg = MIMEMultipart()
    msg['From'] = f"Book Wellness <{CORREO_EMISOR}>"
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(CORREO_EMISOR, PASSWORD_EMISOR)
        server.send_message(msg)
        server.quit()
        print(f"[NOTIFICACIÓN] Correo enviado exitosamente a: {destinatario}")
        return True
    except Exception as e:
        print(f"[ERROR NOTIFICACIÓN] No se pudo enviar el correo a {destinatario}: {e}")
        return False


def _construir_y_enviar_correo_usuario(usuario, fecha_str):
    """Arma la plantilla del calendario y envía el correo."""
    nombre = usuario['nombre']
    correo = usuario['correo']
    eventos = usuario['eventos']

    cuerpo = f"Hola {nombre},\n\nTienes actividades o metas marcadas en tu calendario de Book Wellness para hoy ({fecha_str}):\n\n"
    for ev in eventos:
        if ev['tipo'] == 'fin_libro':
            cuerpo += f"  • ⏰ Fecha límite para terminar: {ev['titulo']}\n"
        elif ev['tipo'] == 'sesion':
            cuerpo += f"  • 📖 Sesión de lectura programada: {ev['titulo']}\n"

    cuerpo += "\n¡Te deseamos una excelente sesión de lectura hoy!\n\nAtentamente,\nEl equipo de Book Wellness"
    asunto = f"📚 Book Wellness - Tus actividades de hoy ({fecha_str})"

    return enviar_correo(correo, asunto, cuerpo)


# ==========================================
# DISPARADOR AL INICIAR SESIÓN
# ==========================================
def procesar_notificaciones_al_iniciar_sesion(id_usuario):
    """Consulta MySQL y envía notificaciones únicamente si están activadas en BD."""
    
    # Comprobar el estado en la base de datos
    if not Usuario.obtener_estado_notificaciones(id_usuario):
        print(f"[NOTIFICACIÓN] El usuario ID {id_usuario} tiene notificaciones desactivadas. Omitiendo envío.")
        return

    hoy = date.today().strftime('%Y-%m-%d')
    print(f"\n[LOGIN] Procesando notificaciones para el usuario ID {id_usuario} ({hoy})...")

    # 1. Notificaciones del Calendario
    usuarios_cal = Calendario.obtener_actividades_usuarios_por_fecha(hoy)
    usuario_cal = next((u for u in usuarios_cal if u.get('id_usuario') == id_usuario), None)

    if usuario_cal:
        _construir_y_enviar_correo_usuario(usuario_cal, hoy)

    # 2. Notificaciones de Objetivos por Vencer
    usuarios_obj = Objetivo.obtener_usuarios_con_objetivos_por_vencer(hoy)
    usuario_obj = next((u for u in usuarios_obj if u.get('id_usuario') == id_usuario), None)

    if usuario_obj:
        cuerpo = f"Hola {usuario_obj['nombre']},\n\nTe recordamos que hoy ({hoy}) vence la fecha límite de tus siguientes objetivos personales de lectura:\n\n"
        for obj_titulo in usuario_obj['objetivos']:
            cuerpo += f"  • 🎯 Objetivo: {obj_titulo}\n"

        cuerpo += "\n¡Da el último esfuerzo para alcanzar tus metas de lectura!\n\nAtentamente,\nEl equipo de Book Wellness"
        asunto = f"🎯 Book Wellness - ¡Hoy vence tu objetivo de lectura! ({hoy})"

        enviar_correo(usuario_obj['correo'], asunto, cuerpo)
