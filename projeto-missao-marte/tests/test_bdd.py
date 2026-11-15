import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from src.gerenciador_recursos import (
    GerenciadorRecursosMarte,
    OxigenioInsuficienteError,
)
from src.servico_telemetria import ServicoTelemetriaEspacial

scenarios("../features/solicitacao_oxigenio.feature")


@pytest.fixture
def contexto_bdd(mocker):
    telemetria = mocker.MagicMock(spec=ServicoTelemetriaEspacial)
    return {"telemetria": telemetria, "erro": None}


@given(parsers.parse("que o habitat possui {estoque:d} kg de oxigênio em estoque"))
def definir_estoque_inicial(contexto_bdd, estoque):
    contexto_bdd["gerenciador"] = GerenciadorRecursosMarte(
        estoque_oxigenio=float(estoque),
        estoque_agua=2000.0,
        telemetria=contexto_bdd["telemetria"],
    )


@when(
    parsers.parse(
        'um astronauta solicita {quantidade:d} kg de oxigênio para "{motivo}"'
    )
)
def solicitar_suprimento(contexto_bdd, quantidade, motivo):
    try:
        contexto_bdd["estoque_final"] = contexto_bdd["gerenciador"].solicitar_oxigenio(
            float(quantidade), motivo=motivo
        )
    except OxigenioInsuficienteError as exc:
        contexto_bdd["erro"] = exc


@then(parsers.parse("o estoque restante deve ser de {esperado:d} kg"))
def validar_estoque_restante(contexto_bdd, esperado):
    assert contexto_bdd["erro"] is None
    assert contexto_bdd["estoque_final"] == float(esperado)


@then("um relatório de status deve ser enviado para a estação na Terra")
def validar_envio_relatorio(contexto_bdd):
    contexto_bdd["telemetria"].enviar_relatorio_status.assert_called_once()


@then("a solicitação deve ser bloqueada por insuficiência de oxigênio")
def validar_bloqueio_crise(contexto_bdd):
    assert isinstance(contexto_bdd["erro"], OxigenioInsuficienteError)


@then("um alerta de crise deve ser disparado para a estação na Terra")
def validar_alerta_crise(contexto_bdd):
    contexto_bdd["telemetria"].disparar_alerta_crise.assert_called_once()