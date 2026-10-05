import db

from IA.orquestador import OrquestadorIA
from IA.recomendador import motor

class RecomendacionInicial:

    # =====================================================
    # OBTENER ENCUESTA DEL USUARIO
    # =====================================================

    @staticmethod
    def obtener_datos_encuesta(id_usuario):

        conexion = db.obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                u.nivel_actual,
                p.id_pregunta,
                p.texto_pregunta,
                p.nombre_campo,
                r.respuesta
            FROM usuarios u

            INNER JOIN preguntas_encuesta p
                ON p.nivel = u.nivel_actual

            LEFT JOIN respuestas_encuesta r
                ON r.id_pregunta = p.id_pregunta
                AND r.id_usuario = u.id_usuario

            WHERE u.id_usuario = %s

            ORDER BY p.id_pregunta
        """, (id_usuario,))

        datos = cursor.fetchall()

        cursor.close()
        conexion.close()

        return datos


    # =====================================================
    # VERIFICAR SI YA SE GENERÓ
    # =====================================================

    @staticmethod
    def ya_generada(id_usuario):

        conexion = db.obtener_conexion()
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


    # =====================================================
    # GENERAR RECOMENDACIONES INICIALES
    # =====================================================

    @staticmethod
    def generar(id_usuario):

        datos = RecomendacionInicial.obtener_datos_encuesta(
            id_usuario
        )

        print("=" * 60)
        print("RECOMENDACION INICIAL RECIBIÓ:")
        print(f"Usuario: {id_usuario}")
        print("Datos de encuesta:")

        for dato in datos:
            print(
                f"- Nivel: {dato['nivel_actual']} | "
                f"Pregunta: {dato['texto_pregunta']} | "
                f"Campo: {dato['nombre_campo']} | "
                f"Respuesta: {dato['respuesta']}"
            )

        print("=" * 60)


        if not datos:
            print(
                "No se encontraron datos de encuesta "
                f"para el usuario {id_usuario}"
            )
            return False


        nivel = datos[0]["nivel_actual"]


        # -------------------------------------------------
        # CONSTRUIR ENCUESTA PARA EL PROMPT
        # -------------------------------------------------

        encuesta = []

        for dato in datos:

            encuesta.append({
                "pregunta": dato["texto_pregunta"],
                "respuesta": dato["respuesta"]
            })


        # -------------------------------------------------
        # PROMPT DE RECOMENDACIÓN INICIAL
        # -------------------------------------------------

        prompt = f"""
la información obtenida de su encuesta de preferencias.

Debes analizar cuidadosamente:

- Su nivel de lectura.
- Sus respuestas personales.
- Sus gustos literarios.
- Sus preferencias de formato.
- Sus hábitos de lectura.
- Los tipos de autores que prefiere.
- Qué espera de Book Wellness.
- Cualquier otra preferencia expresada en la encuesta.

No debes recomendar libros al azar.

Las recomendaciones deben sentirse personalizadas
para ESTA persona.

NIVEL DE LECTURA DEL USUARIO:
{nivel}

RESPUESTAS DE LA ENCUESTA:

{encuesta}


REGLAS:

- Recomienda exactamente 5 libros.
- Los 5 libros deben existir realmente.
- No repitas libros.
- Las recomendaciones deben estar relacionadas
  directamente con las respuestas de la encuesta.
- Respeta el nivel de lectura del usuario.
- Prioriza los gustos expresados por el usuario.
- Puedes recomendar autores nuevos si las respuestas
  indican que el usuario desea descubrir nuevos autores.
- Si el usuario indica preferencias de formato,
  tenlas en cuenta cuando sea relevante.
- No inventes títulos.
- No inventes autores.
- No escribas explicaciones.
- No escribas texto antes del JSON.
- No escribas texto después del JSON.

Devuelve ÚNICAMENTE un JSON válido con esta estructura:

{{
    "libros": [
        {{
            "titulo": "...",
            "autor": "..."
        }},
        {{
            "titulo": "...",
            "autor": "..."
        }},
        {{
            "titulo": "...",
            "autor": "..."
        }},
        {{
            "titulo": "...",
            "autor": "..."
        }},
        {{
            "titulo": "...",
            "autor": "..."
        }}
    ]
}}
"""



        # -------------------------------------------------
        # LLAMAR A GEMINI
        # -------------------------------------------------

        try:

            ia = OrquestadorIA()

            resultado = ia.generar_json(
                prompt,
                timeout=120
            )

            print("=" * 60)
            print("RESPUESTA DE GEMINI - RECOMENDACION INICIAL")
            print(resultado)
            print("=" * 60)


        except Exception as e:

            print(
                "ERROR GENERANDO RECOMENDACIÓN INICIAL:",
                e
            )

            return False


        # -------------------------------------------------
        # OBTENER LIBROS
        # -------------------------------------------------

        if not isinstance(resultado, dict):

            print(
                "La IA no devolvió un objeto JSON válido."
            )

            return False


        libros = resultado.get(
            "libros",
            []
        )


        if not isinstance(libros, list):

            print(
                "La IA no devolvió una lista de libros."
            )

            return False


        if len(libros) != 5:

            print(
                "La IA no devolvió exactamente 5 libros."
            )

            return False
        
        # =====================================================
        # BUSCAR INFORMACIÓN COMPLETA DE LOS LIBROS
        # =====================================================

        try:

            libros_completos = motor.buscar_libros(libros)

        except Exception as e:

            print(
                "ERROR BUSCANDO LIBROS EN GOOGLE BOOKS:",
                e
            )

            return False


        if len(libros_completos) == 0:

            print(
                "No se pudieron encontrar los libros "
                "en Google Books/OpenLibrary."
            )

            return False

        libros = libros_completos



        # -------------------------------------------------
        # VALIDAR ESTRUCTURA
        # -------------------------------------------------

        for libro in libros:

            if not isinstance(libro, dict):
                return False

            if not libro.get("titulo"):
                return False

            if not libro.get("autor"):
                return False


        # -------------------------------------------------
        # GUARDAR RECOMENDACIONES
        # -------------------------------------------------

        try:

            db.guardar_recomendaciones(
                id_usuario,
                libros
            )

        except Exception as e:

            print(
                "ERROR GUARDANDO RECOMENDACIONES INICIALES:",
                e
            )

            return False


        # -------------------------------------------------
        # MARCAR COMO GENERADA
        # -------------------------------------------------

        RecomendacionInicial.marcar_generada(
            id_usuario
        )


        print(
            f"Recomendaciones iniciales generadas "
            f"para usuario {id_usuario}"
        )

        return True


    # =====================================================
    # MARCAR COMO GENERADA
    # =====================================================

    @staticmethod
    def marcar_generada(id_usuario):

        conexion = db.obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE usuarios
            SET recomendacion_inicial_generada = 1
            WHERE id_usuario = %s
        """, (id_usuario,))

        conexion.commit()

        cursor.close()
        conexion.close()

