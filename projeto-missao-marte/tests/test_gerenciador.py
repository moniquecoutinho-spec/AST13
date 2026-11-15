import pytest
from src.gerenciador_recursos import (
    GerenciadorRecursosMarte,
    NivelEmergenciaInvalidoError,
    OxigenioInsuficienteError,
)


@pytest.mark.parametrize(
    "num_astronautas, nivel_emergencia, consumo_esperado",
    [
        (4, 1, 8.0),    # 4 * 2.0 * 1.00
        (4, 2, 10.0),   # 4 * 2.0 * 1.25
        (6, 3, 18.0),   # 6 * 2.0 * 1.50
        (2, 5, 8.0),    # 2 * 2.0 * 2.00
    ],
)
def test_calculo_consumo_diario_parametrizado(
    gerenciador, num_astronautas, nivel_emergencia, consumo_esperado
):
    consumo = gerenciador.calcular_consumo_diario(num_astronautas, nivel_emergencia)
    assert consumo == consumo_esperado


@pytest.mark.parametrize("nivel_invalido", [0, -1, 6, 10])
def test_nivel_emergencia_invalido_lanca_excecao(gerenciador, nivel_invalido):
    with pytest.raises(NivelEmergenciaInvalidoError):
        gerenciador.calcular_consumo_diario(num_astronautas=4, nivel_emergencia=nivel_invalido)


def test_aplicar_cota_racionamento_reduz_consumo(gerenciador):
    fator = gerenciador.aplicar_cota_racionamento(0.25)
    assert fator == 0.75
    assert gerenciador.calcular_consumo_diario(num_astronautas=4, nivel_emergencia=1) == 6.0


def test_solicitacao_normal_envia_relatorio_telemetria(gerenciador, telemetria_mock):
    restante = gerenciador.solicitar_oxigenio(150.0, motivo="Manutenção externa")

    assert restante == 850.0
    telemetria_mock.enviar_relatorio_status.assert_called_once_with(
        {
            "evento": "consumo_oxigenio",
            "quantidade_retirada": 150.0,
            "estoque_restante": 850.0,
            "motivo": "Manutenção externa",
        }
    )


def test_solicitacao_acima_estoque_dispara_alerta_e_lanca_excecao(
    gerenciador, telemetria_mock
):
    with pytest.raises(OxigenioInsuficienteError):
        gerenciador.solicitar_oxigenio(1200.0, motivo="Expansão estufa")

    telemetria_mock.disparar_alerta_crise.assert_called_once_with(
        "Tentativa de retirada acima do estoque (1200.0 kg). Motivo: Expansão estufa",
        "CRITICO",
    )


def test_reserva_critica_atingida_dispara_alerta_crise(mocker):
    mock_envio = mocker.patch(
        "src.servico_telemetria.ServicoTelemetriaEspacial.disparar_alerta_crise",
        return_value=True,
    )
    gerenciador_local = GerenciadorRecursosMarte(estoque_oxigenio=1000.0, estoque_agua=2000.0)

    restante = gerenciador_local.solicitar_oxigenio(850.0, motivo="Pressurização módulo B")

    assert restante == 150.0
    mock_envio.assert_called_once_with(
        "Reserva crítica de oxigênio atingida: 150.0 kg restantes.",
        "ALTO",
    )