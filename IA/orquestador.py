import json
import requests
import time

import db

API_KEY = os.getenv("GEMINI_API_KEY")

class OrquestadorIA:

    def __init__(
        self,
        api_key=None,
        modelo="gemini-2.5-flash",
        timeout=120
    ):

        self.api_key = api_key or API_KEY
        self.timeout = timeout

        self.url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{modelo}:generateContent"
        )

    ##########################################################
    # CONSTRUIR HISTORIAL
    ##########################################################

    def construir_historial(self, id_usuario):

        historial = db.obtener_historial(id_usuario)

        texto = ""

        for mensaje in historial:

            if mensaje["rol"] == "usuario":

                texto += (
                    "Usuario: "
                    + mensaje["mensaje"]
                    + "\n\n"
                )

            else:

                texto += (
                    "Asistente: "
                    + mensaje["mensaje"]
                    + "\n\n"
                )

        return texto

    ##########################################################
    # CONSULTAR GEMINI
    ##########################################################

    def _consultar(self, prompt):

        body = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        MAX_REINTENTOS = 3

        for intento in range(MAX_REINTENTOS):

            respuesta = requests.post(
                self.url,
                params={
                    "key": self.api_key
                },
                json=body,
                timeout=self.timeout
            )

            # Si Gemini responde 503, reintentar
            if respuesta.status_code == 503:

                # Si todavía quedan intentos
                if intento < MAX_REINTENTOS - 1:

                    espera = 2 ** intento

                    print(
                        f"Gemini respondió 503. "
                        f"Reintentando en {espera} segundos..."
                    )

                    time.sleep(espera)

                    continue

                # Ya no quedan intentos
                print("Gemini continúa respondiendo 503 después de 3 intentos.")

            # Cualquier respuesta que NO sea 503
            # se procesa normalmente.
            respuesta.raise_for_status()

            datos = respuesta.json()

            return (
                datos["candidates"][0]
                ["content"]["parts"][0]["text"]
            )


    ##########################################################
    # GENERAR TEXTO (CON MEMORIA)
    ##########################################################

    def generar_texto(
        self,
        id_usuario,
        prompt_sistema,
        mensaje_usuario
    ):

        historial = self.construir_historial(id_usuario)

        prompt = (
            prompt_sistema
            + "\n\n"
            + historial
            + "Usuario: "
            + mensaje_usuario
        )

        respuesta = self._consultar(prompt).strip()

        if respuesta.startswith("Asistente:"):
            respuesta = respuesta[len("Asistente:"):].strip()


        db.guardar_mensaje(
            id_usuario,
            "usuario",
            mensaje_usuario
        )

        db.guardar_mensaje(
            id_usuario,
            "asistente",
            respuesta
        )

        return respuesta

    ##########################################################
    # GENERAR RESPUESTA DEL SISTEMA
    ##########################################################

    def generar_respuesta(
        self,
        id_usuario,
        prompt
    ):

        historial = self.construir_historial(
            id_usuario
        )

        prompt_final = (
            historial
            + "\n"
            + prompt
        )

        respuesta = self._consultar(
            prompt_final
        ).strip()

        if respuesta.startswith("Asistente:"):

            respuesta = respuesta[len("Asistente:"):].strip()

        db.guardar_mensaje(
            id_usuario,
            "asistente",
            respuesta
        )

        return respuesta

    ##########################################################
    # GENERAR JSON
    ##########################################################

    def generar_json(self, prompt, timeout=None):

        timeout_original = self.timeout

        if timeout is not None:
            self.timeout = timeout

        try:

            texto = self._consultar(prompt)

            texto = texto.replace("`json", "")
            texto = texto.replace("`", "")
            texto = texto.strip()

            return json.loads(texto)

        finally:

            self.timeout = timeout_original

