import requests

from routes.utilidades import obtener_json

class GoogleBooksAPI:

    def __init__(self):
        self.url_base = "https://www.googleapis.com/books/v1/volumes"
        self.api_key = os.getenv("GOOGLE_BOOKS_API_KEY")


    def buscar_libros(self, texto):

        if not texto:
            return []

        try:

            print("=" * 60)
            print("GOOGLE BOOKS - NUEVA BÚSQUEDA")
            print("Texto:", texto)

            parametros = {
                "q": texto,
                "maxResults": 20,
                "key": self.api_key
            }

            datos = obtener_json(
                self.url_base,
                params=parametros,
                timeout=5
            )

            if not datos:
                return []
    
            print("Claves recibidas:", datos.keys())
            print("Cantidad de resultados:", len(datos.get("items", [])))


            resultados = []

            for item in datos.get("items", []):

                info = item.get("volumeInfo", {})

                imagen = (
                    info.get("imageLinks", {})
                    .get("thumbnail",
                         "https://via.placeholder.com/200x300?text=Sin+Portada")
                )

                resultados.append({

                    "titulo": info.get(
                        "title",
                        "Sin título"
                    ),

                    "subtitulo": info.get(
                        "subtitle",
                        ""
                    ),

                    "autor": ", ".join(
                        info.get(
                            "authors",
                            ["Autor desconocido"]
                        )
                    ),

                    "descripcion": info.get(
                        "description",
                        "Descripción no disponible"
                    ),

                    "paginas": info.get(
                        "pageCount",
                        "Desconocido"
                    ),

                    "generos": ", ".join(
                        info.get(
                            "categories",
                            []
                        )
                    ),

                    "anio": info.get(
                        "publishedDate",
                        "Desconocido"
                    ),

                    "pais": info.get(
                        "country",
                        "Desconocido"
                    ),

                    "formato": info.get(
                        "printType",
                        "BOOK"
                    ),

                    "portada": imagen,

                    "id_google": item.get(
                        "id",
                        ""
                    )

                })

            print("Resultados procesados:", len(resultados))

            return resultados

        except Exception as e:

            import traceback

            print("=" * 60)
            print("ERROR GOOGLE BOOKS")
            print("Tipo:", type(e).__name__)
            print("Mensaje:", e)
            traceback.print_exc()
            print("=" * 60)

            return []



    def obtener_libro(self, id_google):

        print("=" * 60)
        print("OBTENIENDO LIBRO")
        print("ID:", id_google)


        datos = obtener_json(
            f"{self.url_base}/{id_google}",
            params={
                "key": self.api_key
            },
            timeout=5
        )

        if not datos:
            raise Exception("Google Books no respondió.")


        print("Claves:", datos.keys())

        info = datos["volumeInfo"]


        imagen = info.get(
            "imageLinks",
            {}
        ).get(
            "thumbnail",
            "https://via.placeholder.com/200x300?text=Sin+Portada"
        )

        return {

            "titulo": info.get("title", "Sin título"),

            "subtitulo": info.get("subtitle", ""),

            "autor": ", ".join(
                info.get(
                    "authors",
                    ["Autor desconocido"]
                )
            ),

            "descripcion": info.get(
                "description",
                "Descripción no disponible"
            ),

            "paginas": info.get(
                "pageCount",
                "Desconocido"
            ),

            "generos": ", ".join(
                info.get(
                    "categories",
                    []
                )
            ),

            "anio": info.get(
                "publishedDate",
                "Desconocido"
            ),

            "formato": info.get(
                "printType",
                "BOOK"
            ),

            "portada": imagen
        }

            

