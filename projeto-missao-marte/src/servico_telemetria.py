class ServicoTelemetriaEspacial:
    """Serviço externo de comunicação com a estação terrestre."""

    def enviar_relatorio_status(self, dados: dict) -> dict:
        raise ConnectionError("Conexão real com a Terra indisponível durante testes.")

    def disparar_alerta_crise(self, mensagem: str, nivel_severidade: str) -> bool:
        raise ConnectionError("Conexão real com a Terra indisponível durante testes.")