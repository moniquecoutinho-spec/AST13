import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.gerenciador_recursos import GerenciadorRecursosMarte
from src.servico_telemetria import ServicoTelemetriaEspacial


@pytest.fixture(scope="module")
def parametros_habitat():
    """Carrega os parâmetros iniciais do habitat para todo o módulo de testes."""
    config = {
        "oxigenio_inicial": 1000.0,
        "agua_inicial": 2000.0,
        "num_astronautas": 4,
    }
    yield config
    config.clear()


@pytest.fixture(scope="function")
def telemetria_mock(mocker):
    """Isola chamadas de rede do ServicoTelemetriaEspacial."""
    mock = mocker.MagicMock(spec=ServicoTelemetriaEspacial)
    mock.enviar_relatorio_status.return_value = {"status": "OK"}
    mock.disparar_alerta_crise.return_value = True
    return mock


@pytest.fixture(scope="function")
def gerenciador(parametros_habitat, telemetria_mock):
    """Fornece uma instância limpa do GerenciadorRecursosMarte por teste."""
    instancia = GerenciadorRecursosMarte(
        estoque_oxigenio=parametros_habitat["oxigenio_inicial"],
        estoque_agua=parametros_habitat["agua_inicial"],
        telemetria=telemetria_mock,
    )
    yield instancia
    del instancia


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook para registrar se o teste falhou e permitir captura de screenshot."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(scope="function")
def driver(request):
    """Inicializa e encerra o navegador Chrome em modo headless."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,800")

    web_driver = webdriver.Chrome(options=chrome_options)
    yield web_driver

    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        os.makedirs("evidencias", exist_ok=True)
        web_driver.save_screenshot(f"evidencias/falha_{request.node.name}.png")

    web_driver.quit()