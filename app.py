from flask import Flask
from flask_cors import CORS

# Importar las rutas
from routes.home import registrar_rutas as home_routes
from routes.libros import registrar_rutas as libros_routes
from routes.usuarios import registrar_rutas as usuarios_routes
from routes.lectura import registrar_rutas as lectura_routes
from routes.seguimiento import registrar_rutas as seguimiento_routes
from routes.objetivos import objetivos_bp

# Importar Blueprints
from IA.recomendador import recomendador_bp
from IA.asistente import ia_bp
from models.notificaciones import notificaciones_bp
from models.recuperacion import recuperacion_bp

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

# Registrar Blueprints
app.register_blueprint(ia_bp)
app.register_blueprint(recomendador_bp)
app.register_blueprint(notificaciones_bp)
app.register_blueprint(objetivos_bp) 
app.register_blueprint(recuperacion_bp)

CORS(app)

# Registrar todas las rutas
home_routes(app)
libros_routes(app)
usuarios_routes(app)
lectura_routes(app)
seguimiento_routes(app)

if __name__ == "__main__":
    app.run(
        debug=True,
        port=5000
    )
    
