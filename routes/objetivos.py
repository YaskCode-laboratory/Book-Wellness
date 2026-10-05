from flask import Blueprint, jsonify, request, session

from models.Objetivo import Objetivo


objetivos_bp = Blueprint(
    "objetivos",
    __name__
)


# =====================================================
# OBTENER OBJETIVOS
# =====================================================

@objetivos_bp.route("/api/objetivos", methods=["GET"])
def obtener_objetivos():

    id_usuario = session["id_usuario"]

    objetivos = Objetivo.obtener_por_usuario(id_usuario)

    return jsonify(objetivos)


# =====================================================
# CREAR OBJETIVO
# =====================================================

@objetivos_bp.route("/api/objetivos", methods=["POST"])
def crear_objetivo():

    datos = request.json

    print("DATOS RECIBIDOS: ", datos)

    titulo = datos.get("titulo")
    tipo = datos.get("tipo")
    meta = datos.get("meta")

    if not titulo:
        return jsonify({
            "error": "El título es obligatorio."
        }), 400


    if not tipo:
        return jsonify({
            "error": "El tipo de objetivo es obligatorio."
        }), 400


    if meta is None or meta == "":
        return jsonify({
            "error": "La meta es obligatoria."
        }), 400



    try:
        meta = int(meta)

    except ValueError:

        return jsonify({
            "error": "La meta debe ser numérica."
        }), 400


    if meta <= 0:

        return jsonify({
            "error": "La meta debe ser mayor que cero."
        }), 400


    objetivo = Objetivo(

        id_usuario=session["id_usuario"],

        titulo=titulo,

        descripcion=datos.get("descripcion"),

        tipo=tipo,

        meta=meta,

        unidad=datos.get("unidad"),

        fecha_inicio=datos.get("fecha_inicio"),

        fecha_fin=datos.get("fecha_fin"),

        condicion_tipo=datos.get("condicion_tipo"),

        condicion_valor=datos.get("condicion_valor"),

        frecuencia=datos.get("frecuencia")

    )

    print("TIPO ANTES DE CREAR:", objetivo.tipo)

    Objetivo.crear(objetivo)


    return jsonify({

        "mensaje": "Objetivo creado correctamente.",

        "objetivo": objetivo.to_dict()

    }), 201



# =====================================================
# EDITAR OBJETIVO
# =====================================================

@objetivos_bp.route("/api/objetivos/<id_objetivo>", methods=["PUT"])
def editar_objetivo(id_objetivo):

    datos = request.get_json()


    if not datos:

        return jsonify({

            "error": "No se recibieron datos."

        }), 400



    objetivo = Objetivo.obtener_por_id(id_objetivo)


    if objetivo is None:

        return jsonify({

            "error": "Objetivo no encontrado."

        }), 404



    titulo = datos.get("titulo")

    descripcion = datos.get("descripcion")

    tipo = datos.get("tipo")

    meta = datos.get("meta")

    unidad = datos.get("unidad")

    fecha_inicio = datos.get("fecha_inicio")

    fecha_fin = datos.get("fecha_fin")

    condicion_tipo = datos.get("condicion_tipo")

    condicion_valor = datos.get("condicion_valor")

    frecuencia = datos.get("frecuencia")



    if not titulo:

        return jsonify({

            "error": "El título es obligatorio."

        }), 400



    if not tipo:

        return jsonify({

            "error": "El tipo de objetivo es obligatorio."

        }), 400



    try:

        meta = int(meta)


    except (TypeError, ValueError):

        return jsonify({

            "error": "La meta debe ser numérica."

        }), 400



    if meta <= 0:

        return jsonify({

            "error": "La meta debe ser mayor que cero."

        }), 400



    objetivo.titulo = titulo

    objetivo.descripcion = descripcion

    objetivo.tipo = tipo

    objetivo.meta = meta

    objetivo.unidad = unidad

    objetivo.fecha_inicio = fecha_inicio

    objetivo.fecha_fin = fecha_fin

    objetivo.condicion_tipo = condicion_tipo

    objetivo.condicion_valor = condicion_valor

    objetivo.frecuencia = frecuencia



    if objetivo.progreso_actual >= objetivo.meta:

        objetivo.progreso_actual = objetivo.meta

        objetivo.estado = "completado"

        objetivo.completado = True
    else:

        objetivo.estado = "activo"

        objetivo.completado = False



    Objetivo.actualizar(objetivo)



    return jsonify({

        "mensaje": "Objetivo actualizado correctamente.",

        "objetivo": objetivo.to_dict()

    })



# =====================================================
# ELIMINAR OBJETIVO
# =====================================================

@objetivos_bp.route("/api/objetivos/<id_objetivo>", methods=["DELETE"])
def eliminar_objetivo(id_objetivo):

    eliminado = Objetivo.eliminar(id_objetivo)


    if not eliminado:

        return jsonify({

            "error": "Objetivo no encontrado."

        }), 404



    return jsonify({

        "mensaje": "Objetivo eliminado correctamente."

    })
