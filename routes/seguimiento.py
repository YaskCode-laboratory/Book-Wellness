from flask import render_template, request, jsonify, session
import db
from models.Libro import Libro
import os
import cloudinary
import cloudinary.uploader

from models.seguimiento import Seguimiento

cloudinary.config(
    cloud_name = "jklaybsr",
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET")  
)

# -------------------------
# ELIMINAR LIBRO
# -------------------------
def registrar_rutas(app):

    @app.route('/api/agregar_libro_manual', methods=['POST'])
    def agregar_libro_manual():
        id_usuario = session.get('id_usuario')
        
        if not id_usuario:
            return jsonify({"error": "No hay sesión activa"}), 401

        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        descripcion = request.form.get('descripcion', '')
        paginas = request.form.get('paginas')
        capitulos = request.form.get('capitulos')
        anio = request.form.get('anio')
        genero = request.form.get('genero')
        formato = request.form.get('formato')
        categoria = request.form.get('categoria', 'pendiente')

        if not titulo or not autor:
            return jsonify({"error": "Título y autor son obligatorios"}), 400

        portada = None
        if 'portada' in request.files:
            archivo = request.files['portada']
            if archivo.filename != '':
                try:
                    resultado_cloud = cloudinary.uploader.upload(archivo)
                    portada = resultado_cloud.get('secure_url')
                except Exception as e:
                    print("ERROR CLOUDINARY:", e)

        try:
            # 1. Crear la instancia con todos los datos
            libro = Libro(
                id_usuario=id_usuario,
                titulo=titulo,
                autor=autor,
                descripcion=descripcion,
                portada=portada,
                categoria=categoria,
                key_libro=None,       # manual no tiene key_libro
                paginas=paginas,
                id_google=None,       # manual no tiene id_google
                genero=genero,
                anio=anio,
                es_manual=True,       # ← True porque es agregado manual
                formato=formato
            )
            
            # 2. Guardar (0 argumentos)
            resultado = libro.guardar()  # Devuelve id_nuevo o False

            if resultado:
                if capitulos:
                    # .actualizar_datos SÍ es estático, así que está bien
                    Libro.actualizar_datos(resultado, num_caps=int(capitulos))
                    
                db.invalidar_cache_recomendaciones(id_usuario)
                return jsonify({"mensaje": "Libro agregado correctamente"}), 201
            
            return jsonify({"error": "Este libro ya está en tu lista"}), 409

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    
    
    @app.route('/api/eliminar_libro', methods=['DELETE'])
    def eliminar_libro():

        datos = request.json
        print("DATOS RECIBIDOS:", datos)

        id_libro = datos.get('id_libro')
        id_usuario = datos.get('id_usuario')

        print("ID_LIBRO:", id_libro, "ID_USUARIO:", id_usuario)

        if not id_libro or not id_usuario:
            return jsonify({
                "error": "Datos incompletos"
            }), 400

        try:
            Libro.eliminar(
                int(id_libro),
                int(id_usuario)
            )
            db.invalidar_cache_recomendaciones(id_usuario)

            return jsonify({
                "mensaje": "Libro eliminado"
            }), 200

        except Exception as e:
            print("ERROR ELIMINAR:", str(e))
            return jsonify({
                "error": str(e)
            }), 500
        

    @app.route('/api/eventos_seguimiento')
    def eventos_seguimiento():
        id_usuario = session.get('id_usuario')
        fecha = request.args.get('fecha')
        if not id_usuario or not fecha:
            return jsonify([]), 400
        eventos = Seguimiento.obtener_eventos_por_fecha(id_usuario, fecha)
        return jsonify(eventos)
