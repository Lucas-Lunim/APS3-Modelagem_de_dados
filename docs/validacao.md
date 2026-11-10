# Verificação da APS 3 e cenários para Robot Framework

## Critérios de entrega

| Exigência | Evidência |
| --- | --- |
| Sequência em código textual | docs/diagrams/sequencia.mmd |
| Chamadas síncronas | Invocações com seta ->> |
| Mensagem assíncrona | Entrega lógica de MensagemMatchingDTO com seta -) |
| Fragmentos combinados | alt/else, par e loop |
| Retornos DTO | Tipos nomeados na sequência e definidos em contratos.md |
| Operações públicas correspondentes | interfaces.mmd e tabela de contratos.md |
| Pelo menos três raias | Quatro partições nomeadas no diagrama de atividades |
| Guardas booleanas exclusivas | Expressão e negação em cada par de saídas de decisão |
| Fork e Join | Duas barras e três consultas independentes |
| Inicial, subestados e terminais | SolicitacaoMatching com Processando composto e três desfechos |
| Transições formais | evento [guarda] / efeito() em mais de duas transições |
| Ações internas | entry e do nos estados |
| C4 nível 3 | Um worker Python detalhado; API e Supabase como elementos de apoio |
| Tecnologias e protocolos | Tipos nos blocos e chamadas Python, HTTPS/JSON, REST/RPC e PostgreSQL nos conectores |
| ADR no formato Nygard | Título, status, contexto, decisão e consequências em adr-0001.md |
| README integrado | Os quatro diagramas, a ADR e as interfaces estão incorporados ao README |
| Entrega individual | Recorte PoliticaMatching; modelos redesenhados para esse fluxo |

## Conferências de consistência

- A mesma operação calcular recebe perfil, demanda e configuração em sequência, interfaces, README e ADR.
- O mesmo comando assíncrono inicia a solicitação vista nos diagramas de sequência, atividades e estados.
- Perfil, demanda e política são consultados em paralelo; o cálculo ocorre somente depois do Join e da validação.
- Rejeitada, FalhaTecnica e Concluida têm os mesmos significados em todos os artefatos.
- O C4 detalha somente o contêiner worker; seus componentes não são apresentados como microserviços independentes.
- A nota de matching não substitui elegibilidade acadêmica nem a autorização para candidatura.
- Os pesos não foram inventados como decisão da equipe; configuração incompleta bloqueia a nota.

## Cenários de aceitação propostos

| Cenário | Resultado esperado |
| --- | --- |
| Perfil, demanda e política válidos | Concluida, com nota entre 0 e 100 e versões das entradas |
| Perfil não encontrado | Rejeitada, com motivo PERFIL_AUSENTE |
| Demanda não encontrada ou não publicada | Rejeitada, sem nota |
| Convênio inválido | Rejeitada, sem nota |
| Política ausente ou incompleta | Rejeitada, sem nota |
| Falha técnica em uma consulta | Os três ramos terminam; FalhaTecnica persistida |
| Exceção do cálculo capturada | FalhaTecnica, sem resultado parcial |
| Publicação falha na transação inicial | Nenhuma solicitação aceita sem mensagem durável |
| Mesmo pedido e chave repetidos | Mesmo identificador; não duplicar cálculo |
| Mesma chave e pedido diferente | Rejeitar conflito de idempotência |
| Mensagem repetida após conclusão | Confirmar sem calcular novamente |
| Concessão ainda vigente em outro consumidor | Não adquirir nem confirmar prematuramente a mensagem |
| Consumidor trava e concessão expira | Outra tentativa pode prosseguir com novo token |
| Consumidor antigo tenta finalizar | Escrita recusada; resultado da tentativa atual preservado |
| Gravação terminal ou confirmação falha | Mensagem permanece recuperável; resultado persistido não é sobrescrito |
| Usuário tenta consultar pedido de outro | Acesso negado conforme permissões |

Robot Framework é a tecnologia escolhida para automatizar esses cenários na implementação futura. Os testes de aplicação não foram implementados nem executados nesta entrega. A verificação atual é de sintaxe, renderização e consistência dos modelos.

## Versionamento e entrega

Os arquivos devem ser publicados no repositório individual e o link enviado no AVA. Não há URL de repositório fornecida nesta conversa. O pacote não simula commits antigos; o histórico deve refletir alterações reais.
