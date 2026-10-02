# 🤖 Inteligencia Artificial — Book Wellness

La carpeta `IA` contiene los módulos relacionados con las funcionalidades de Inteligencia Artificial de **Book Wellness**.

El sistema utiliza **Google Gemini** para generar respuestas, recomendaciones y contenido personalizado de acuerdo con la información del usuario, sus hábitos de lectura, objetivos y estado de ánimo.

---

# 🧠 Modelo utilizado

Actualmente, Book Wellness utiliza el modelo:

```text
gemini-2.5-flash
```

Se utiliza esta versión para mantener una mayor estabilidad en las solicitudes y evitar problemas relacionados con respuestas **HTTP 503 (Service Unavailable)** que pueden presentarse con otros modelos o configuraciones.

Está previsto continuar mejorando y ampliando las capacidades de la Inteligencia Artificial de Book Wellness conforme evolucione el proyecto.

---

# 🔑 API Key

Para que las funciones de Inteligencia Artificial funcionen correctamente es necesario introducir una **API Key válida y funcional de Google Gemini**.

La clave es utilizada por el archivo:

```text
orquestador.py
```

La API Key **no debe hacerse pública ni subirse directamente a GitHub**, ya que se trata de una credencial privada.

Durante el desarrollo, la clave se encuentra configurada de manera local. Para el despliegue del proyecto, debe proporcionarse mediante las variables de entorno correspondientes en el servicio de hosting.

> ⚠️ No publicar una API Key real dentro del código fuente, repositorios públicos, capturas de pantalla o documentación.

---

# 📂 Archivos de la carpeta IA

## 🎭 EstadoAnimo.py

Este módulo se encarga de las funcionalidades de Inteligencia Artificial relacionadas con el **estado de ánimo del usuario**.

Utiliza la información emocional seleccionada por el lector para generar respuestas relacionadas con su situación y con su experiencia de lectura.

Entre sus funciones se encuentran los flujos relacionados con estados como:

- 😊 Feliz
- 🤔 Reflexivo
- 😮 Sorprendido
- 😰 Ansioso
- 😢 Triste

El módulo utiliza el `OrquestadorIA` para comunicarse con Gemini y generar las respuestas correspondientes.

---

## 🎯 IAObjetivo.py

Este módulo está relacionado con la Inteligencia Artificial aplicada a los **objetivos y rutinas de lectura**.

Contiene el prompt específico utilizado para orientar a la IA en tareas relacionadas con:

- Creación de objetivos.
- Rutinas de lectura.
- Condiciones y características de los objetivos.
- Personalización de los objetivos según la información del usuario.

`IAObjetivo.py` utiliza el `OrquestadorIA` para enviar las solicitudes a Gemini y obtener las respuestas generadas.

---

## 📚 recomendadorInicial.py

Este módulo se encarga de generar las **recomendaciones iniciales de libros** para un usuario.

Utiliza información obtenida durante el proceso inicial del usuario, como:

- Nivel actual del lector.
- Respuestas de la encuesta.
- Preferencias obtenidas durante el registro.

A partir de esta información, la IA genera una selección inicial de libros.

Después, el sistema utiliza información bibliográfica de servicios como **Google Books** y **Open Library** para complementar las recomendaciones y almacenarlas en el sistema.

La recomendación inicial se genera una vez para cada usuario y queda registrada en la base de datos.

---

## 💬 asistente.py

Este archivo gestiona el **asistente de Inteligencia Artificial** de Book Wellness.

Expone el endpoint:

```text
/api/ia
```

Su función principal es recibir las solicitudes realizadas por el usuario, determinar el contexto correspondiente y enviar la información al módulo de IA adecuado.

Dependiendo de la sección desde la que se realice la solicitud, puede utilizar diferentes instrucciones o prompts, incluyendo las relacionadas con los objetivos.

También mantiene el contexto de la conversación mediante el sistema gestionado por `orquestador.py`.

---

## ⚙️ orquestador.py

Este es uno de los componentes principales de la carpeta `IA`.

El **OrquestadorIA** funciona como intermediario entre Book Wellness y la API de Google Gemini.

Su función es centralizar la comunicación con el modelo para evitar que cada módulo tenga que implementar por separado la conexión con Gemini.

Entre sus responsabilidades se encuentran:

- Gestionar la API Key.
- Seleccionar el modelo `gemini-2.5-flash`.
- Enviar solicitudes a Gemini.
- Gestionar las respuestas de la API.
- Generar respuestas de texto.
- Generar respuestas en formato JSON.
- Procesar las respuestas recibidas.
- Mantener el historial de conversación cuando corresponde.
- Guardar las interacciones necesarias en la base de datos.

Los demás módulos pueden utilizar el orquestador para comunicarse con Gemini sin tener que repetir toda la lógica de conexión.

---

## 📖 recomendado.py

Este módulo está relacionado con el sistema de **recomendaciones de lectura** de Book Wellness.

Su función es trabajar con las recomendaciones generadas por la Inteligencia Artificial y con la información bibliográfica disponible para proporcionar libros adecuados al usuario.

El sistema tiene en cuenta información del lector y utiliza servicios bibliográficos para obtener datos de los libros recomendados.

Las recomendaciones se integran con el resto de las funcionalidades de Book Wellness para que puedan ser mostradas al usuario dentro de la plataforma.
