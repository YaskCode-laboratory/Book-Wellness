from unittest.mock import MagicMock, patch

from IA.IAOBjetivo import IAObjetivo, PROMPT_OBJETIVOS


def test_iaobjetivo_inicializa_motor():
    with patch("IA.IAOBjetivo.OrquestadorIA") as mock_orquestador:
        ia = IAObjetivo()

        mock_orquestador.assert_called_once()
        assert ia.motor == mock_orquestador.return_value


def test_conversar():
    with patch("IA.IAOBjetivo.OrquestadorIA") as mock_orquestador:
        motor = MagicMock()
        motor.generar_texto.return_value = "Respuesta del asistente"

        mock_orquestador.return_value = motor

        ia = IAObjetivo()

        resultado = ia.conversar(
            1,
            "Quiero crear un objetivo de lectura."
        )

        assert resultado == "Respuesta del asistente"

        motor.generar_texto.assert_called_once_with(
            1,
            PROMPT_OBJETIVOS,
            "Quiero crear un objetivo de lectura."
        )