Feature: Solicitação de Suprimentos de Oxigênio no Habitat de Marte
  Como engenheiro de suporte à vida do Habitat de Marte
  Quero controlar as solicitações de oxigênio em condições normais e de crise
  Para garantir a segurança da tripulação e o envio correto de telemetria à Terra

  Scenario: Solicitação de oxigênio dentro do limite normal de operação
    Given que o habitat possui 1000 kg de oxigênio em estoque
    When um astronauta solicita 120 kg de oxigênio para "Atividade extraveicular"
    Then o estoque restante deve ser de 880 kg
    And um relatório de status deve ser enviado para a estação na Terra

  Scenario: Solicitação de oxigênio em condição de crise por falta de estoque
    Given que o habitat possui 100 kg de oxigênio em estoque
    When um astronauta solicita 250 kg de oxigênio para "Reparo emergencial"
    Then a solicitação deve ser bloqueada por insuficiência de oxigênio
    And um alerta de crise deve ser disparado para a estação na Terra