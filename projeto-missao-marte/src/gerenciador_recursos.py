from src.servico_telemetria import ServicoTelemetriaEspacial


class OxigenioInsuficienteError(Exception):
    """Exceção lançada quando não há estoque suficiente de oxigênio."""


class NivelEmergenciaInvalidoError(Exception):
    """Exceção lançada quando o nível de emergência está fora da faixa permitida (1 a 5)."""


class GerenciadorRecursosMarte:
    """Controla os recursos vitais (ECLSS) do Habitat de Marte."""

    CONSUMO_BASE_O2_POR_ASTRONAUTA = 2.0  # kg/dia
    LIMIAR_CRISE_PERCENTUAL = 0.20

    def __init__(
        self,
        estoque_oxigenio: float,
        estoque_agua: float,
        telemetria: ServicoTelemetriaEspacial | None = None,
    ):
        self.estoque_oxigenio = estoque_oxigenio
        self.oxigenio_inicial = estoque_oxigenio
        self.estoque_agua = estoque_agua
        self.telemetria = telemetria or ServicoTelemetriaEspacial()
        self.fator_racionamento = 1.0

    def calcular_taxa_emergencia(self, nivel_emergencia: int) -> float:
        if nivel_emergencia < 1 or nivel_emergencia > 5:
            raise NivelEmergenciaInvalidoError(
                f"Nível de emergência inválido: {nivel_emergencia}. Deve estar entre 1 e 5."
            )
        return 1.0 + (nivel_emergencia - 1) * 0.25

    def calcular_consumo_diario(
        self, num_astronautas: int, nivel_emergencia: int = 1
    ) -> float:
        taxa = self.calcular_taxa_emergencia(nivel_emergencia)
        consumo = (
            num_astronautas
            * self.CONSUMO_BASE_O2_POR_ASTRONAUTA
            * taxa
            * self.fator_racionamento
        )
        return round(consumo, 2)

    def aplicar_cota_racionamento(self, percentual_reducao: float) -> float:
        if not 0 < percentual_reducao <= 0.5:
            raise ValueError("A redução de racionamento deve estar entre 0% e 50%.")
        self.fator_racionamento = round(1.0 - percentual_reducao, 2)
        return self.fator_racionamento

    def solicitar_oxigenio(self, quantidade: float, motivo: str = "Operação padrão") -> float:
        if quantidade <= 0:
            raise ValueError("A quantidade solicitada deve ser maior que zero.")

        if quantidade > self.estoque_oxigenio:
            self.telemetria.disparar_alerta_crise(
                f"Tentativa de retirada acima do estoque ({quantidade} kg). Motivo: {motivo}",
                "CRITICO",
            )
            raise OxigenioInsuficienteError(
                f"Estoque insuficiente: solicitado {quantidade} kg, disponível {self.estoque_oxigenio} kg."
            )

        self.estoque_oxigenio = round(self.estoque_oxigenio - quantidade, 2)

        if self.estoque_oxigenio <= self.oxigenio_inicial * self.LIMIAR_CRISE_PERCENTUAL:
            self.telemetria.disparar_alerta_crise(
                f"Reserva crítica de oxigênio atingida: {self.estoque_oxigenio} kg restantes.",
                "ALTO",
            )
        else:
            self.telemetria.enviar_relatorio_status(
                {
                    "evento": "consumo_oxigenio",
                    "quantidade_retirada": quantidade,
                    "estoque_restante": self.estoque_oxigenio,
                    "motivo": motivo,
                }
            )

        return self.estoque_oxigenio