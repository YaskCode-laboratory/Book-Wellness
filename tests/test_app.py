import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


def test_app_inicia():
    app.config["TESTING"] = True

    with app.test_client() as cliente:
        respuesta = cliente.get("/")

    assert respuesta.status_code == 200

