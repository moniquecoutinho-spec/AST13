import os
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def obter_url_painel() -> str:
    caminho_html = Path(__file__).resolve().parent.parent / "web" / "painel.html"
    return caminho_html.as_uri()


def test_solicitacao_cota_extra_oxigenio_sucesso(driver):
    driver.get(obter_url_painel())
    wait = WebDriverWait(driver, 5)

    campo_qtd = wait.until(EC.visibility_of_element_located((By.ID, "qtd-oxigenio")))
    campo_qtd.clear()
    campo_qtd.send_keys("200")

    botao = driver.find_element(By.ID, "btn-solicitar")
    botao.click()

    wait.until(
        EC.text_to_be_present_in_element(
            (By.ID, "mensagem-status"), "Solicitação aprovada: 200 kg liberados."
        )
    )
    nivel_atualizado = driver.find_element(By.ID, "nivel-oxigenio").text
    assert nivel_atualizado == "800"


def test_solicitacao_acima_estoque_exibe_alerta_e_salva_evidencia(driver):
    driver.get(obter_url_painel())
    wait = WebDriverWait(driver, 5)

    campo_qtd = wait.until(EC.visibility_of_element_located((By.ID, "qtd-oxigenio")))
    campo_qtd.clear()
    campo_qtd.send_keys("1500")

    driver.find_element(By.ID, "btn-solicitar").click()

    wait.until(
        EC.text_to_be_present_in_element(
            (By.ID, "mensagem-status"), "Alerta de Crise: Estoque de oxigênio insuficiente!"
        )
    )

    os.makedirs("evidencias", exist_ok=True)
    screenshot_salvo = driver.save_screenshot("evidencias/alerta_crise_painel.png")
    assert screenshot_salvo is True