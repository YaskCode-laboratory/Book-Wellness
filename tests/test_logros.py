from unittest.mock import patch

from models.Ob_Logros.logros import Logros


# ============================================================
# obtener_logros
# ============================================================

@patch("models.Ob_Logros.logros.Logros3.obtener_logros")
@patch("models.Ob_Logros.logros.Logros2.obtener_logros")
@patch("models.Ob_Logros.logros.Logros1.obtener_logros")
def test_obtener_logros(
    mock_logros1,
    mock_logros2,
    mock_logros3
):
    mock_logros1.return_value = [
        {"id": 1, "nombre": "Primer logro"}
    ]

    mock_logros2.return_value = [
        {"id": 8, "nombre": "Segundo logro"}
    ]

    mock_logros3.return_value = [
        {"id": 15, "nombre": "Mente Sana"}
    ]

    resultado = Logros.obtener_logros(10)

    assert resultado == {
        "logros1": [
            {"id": 1, "nombre": "Primer logro"}
        ],
        "logros2": [
            {"id": 8, "nombre": "Segundo logro"}
        ],
        "logros3": [
            {"id": 15, "nombre": "Mente Sana"}
        ]
    }

    mock_logros1.assert_called_once_with(10)
    mock_logros2.assert_called_once_with(10)
    mock_logros3.assert_called_once_with(10)


# ============================================================
# Verificar que utiliza el mismo usuario
# ============================================================

@patch("models.Ob_Logros.logros.Logros3.obtener_logros")
@patch("models.Ob_Logros.logros.Logros2.obtener_logros")
@patch("models.Ob_Logros.logros.Logros1.obtener_logros")
def test_obtener_logros_pasa_correctamente_el_usuario(
    mock_logros1,
    mock_logros2,
    mock_logros3
):
    usuario_id = 25

    mock_logros1.return_value = []
    mock_logros2.return_value = []
    mock_logros3.return_value = []

    Logros.obtener_logros(usuario_id)

    mock_logros1.assert_called_once_with(usuario_id)
    mock_logros2.assert_called_once_with(usuario_id)
    mock_logros3.assert_called_once_with(usuario_id)


# ============================================================
# Cuando los tres módulos no tienen logros
# ============================================================

@patch("models.Ob_Logros.logros.Logros3.obtener_logros")
@patch("models.Ob_Logros.logros.Logros2.obtener_logros")
@patch("models.Ob_Logros.logros.Logros1.obtener_logros")
def test_obtener_logros_sin_resultados(
    mock_logros1,
    mock_logros2,
    mock_logros3
):
    mock_logros1.return_value = []
    mock_logros2.return_value = []
    mock_logros3.return_value = []

    resultado = Logros.obtener_logros(1)

    assert resultado == {
        "logros1": [],
        "logros2": [],
        "logros3": []
    }


# ============================================================
# Conserva exactamente las respuestas de cada módulo
# ============================================================

@patch("models.Ob_Logros.logros.Logros3.obtener_logros")
@patch("models.Ob_Logros.logros.Logros2.obtener_logros")
@patch("models.Ob_Logros.logros.Logros1.obtener_logros")
def test_obtener_logros_conserva_resultados(
    mock_logros1,
    mock_logros2,
    mock_logros3
):
    resultado1 = {"completados": 2, "total": 7}
    resultado2 = {"completados": 4, "total": 7}
    resultado3 = {"completados": 6, "total": 7}

    mock_logros1.return_value = resultado1
    mock_logros2.return_value = resultado2
    mock_logros3.return_value = resultado3

    resultado = Logros.obtener_logros(50)

    assert resultado["logros1"] is resultado1
    assert resultado["logros2"] is resultado2
    assert resultado["logros3"] is resultado3
