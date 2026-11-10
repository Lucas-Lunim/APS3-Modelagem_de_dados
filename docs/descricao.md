# APS 3 — PoliticaMatching

**Autor:** Lucas Gabriel de Carvalho de Oliveira  
**Projeto da equipe:** Sistema de Gestão de Aprendizagem e Estágios da UniSenai  
**Funcionalidade individual:** calcular a compatibilidade entre o perfil de competências do estudante e os requisitos de uma demanda industrial.  
**Status:** proposta de arquitetura e modelagem; não descreve uma aplicação já implementada.

## Objetivo e importância

O componente PoliticaMatching transforma informações do perfil e da vaga em uma análise rastreável de compatibilidade. Isso orienta as recomendações e reduz o cruzamento manual de dados. Esta entrega individual usa as sprints do grupo como referência de domínio e redesenha os modelos para esse recorte.

O componente recebe perfil, demanda e configuração versionada e retorna ResultadoMatchingDTO. Consultas, controle das solicitações e publicação de mensagens pertencem aos componentes de apoio. Elegibilidade acadêmica para candidatura e assinatura de contratos permanecem em outros fluxos do sistema.

## Premissas confirmadas e decisões propostas

| Tipo | Conteúdo |
| --- | --- |
| Confirmado nesta conversa | Domínio UniSenai; responsabilidade individual PoliticaMatching; Python, Supabase e Robot Framework; a equipe ainda não definiu fórmula nem pesos. |
| Herdado das sprints | Perfil de competências, demanda técnica, política de compatibilidade e convênio válido como requisito de publicação. |
| Proposto neste dossiê | SolicitacaoMatching, API e worker Python, fila durável Supabase Queues, tentativas com concessão, RPCs atômicas, DTOs e política quantitativa configurável. |
| Ainda depende de definição de negócio | Critérios exatos de similaridade, seus pesos e sua validação/aprovação. Nenhum valor foi atribuído como regra aprovada. |

## Fluxo escolhido

1. O estudante autenticado solicita uma análise para uma demanda. A API inclui a identidade autorizada no pedido.
2. Uma RPC proposta cria a solicitação Pendente e publica o comando na fila na mesma transação. A API responde HTTP 202 com SolicitacaoDTO.
3. O consumidor Python faz polling da fila e encaminha o comando ao ExecutorMatching.
4. O executor adquire uma tentativa exclusiva e consulta perfil, demanda e versão da política em paralelo, sincronizando as três respostas.
5. Dados ausentes, demanda não publicada, convênio inválido ou política incompleta produzem Rejeitada, com motivos. Falhas técnicas produzem FalhaTecnica.
6. Com entradas válidas, PoliticaMatching calcula a nota e devolve ResultadoMatchingDTO; a tentativa persiste Concluida com as versões usadas.
7. A mensagem é arquivada somente depois de confirmar um estado terminal persistido. O estudante consulta o estado e o resultado pelo identificador.

A fila transporta um comando assíncrono, embora as chamadas de leitura e confirmação usem HTTPS. Não se representa retorno HTTP como se fosse evento de conclusão. Duplicatas e consumidores atrasados não podem sobrescrever desfechos terminais.

## Regra de cálculo proposta

Como não há fórmula aprovada, o modelo exige uma política publicada contendo critérios, comparadores, pesos não negativos e versão imutável. A soma dos pesos deve ser positiva e todos os critérios habilitados devem poder ser avaliados. Dados necessários ausentes geram rejeição, sem atribuição silenciosa de zero.

Uma formulação candidata é a média ponderada normalizada:

`grau = 100 × soma(peso_i × aderencia_i) / soma(peso_i)`

Cada `aderencia_i` pertence ao intervalo de 0 a 1 e depende de um comparador definido na política. As referências de domínio são competências/área de formação, disponibilidade de carga horária e localização. A definição desses comparadores, a seleção de critérios e seus pesos continuam pendentes de decisão da equipe. A expressão é uma proposta de organização do cálculo, não uma decisão quantitativa aprovada.

A nota pertence ao intervalo de 0 a 100, acompanha a versão da política e as contribuições por critério. Ela não constitui aprovação acadêmica, autorização de candidatura ou seleção pela empresa.

## Arquitetura e responsabilidades

O C4 nível 3 detalha um único contêiner: o Worker de Matching. Consumidor, executor, política e repositórios são componentes Python internos ao worker. A API é outro contêiner Python; Supabase Data API e a fila são serviços de apoio. O PostgreSQL persiste dados e também hospeda pgmq; a fila é mostrada como abstração lógica de mensageria, não como outro fornecedor.

A seta lógica da fila para processar() na sequência resume o Consumidor da Fila. Ele lê mensagens com polling e chama o executor localmente. MatchingAPI, FilaMatching, ExecutorMatching, RepositorioDados, RepositorioMatching e PoliticaMatching possuem contratos públicos declarados nas interfaces de apoio.

## Leitura dos diagramas

- Sequência: chamadas, DTOs, entrega assíncrona, consultas paralelas, repetição e consulta do resultado.
- Atividades: quatro raias de responsabilidade; Fork/Join sincronizam perfil, demanda e política. Os pares de guardas usam expressão e negação.
- Estados: o ciclo de vida é da SolicitacaoMatching. O estado Processando tem os subestados CarregandoDados, ValidandoDados e Calculando.
- C4: responsabilidades, unidades de implantação e protocolos do fluxo.
- Interfaces: apoio para comprovar a correspondência entre mensagens e operações públicas.

O final interno de Processando representa o fim da preparação de uma tentativa, não o encerramento da solicitação inteira. Desfecho é um nó de escolha, sem persistência própria. persistirDesfecho() seleciona concluir(), rejeitar() ou registrarFalha() conforme o resultado preparado. A transição só é efetivada se sua gravação transacional tiver sucesso; falha de persistência deixa a solicitação recuperável. Os estados Concluida, Rejeitada e FalhaTecnica são terminais e imutáveis.

Na implementação proposta, estado e etapa são dois campos persistidos. A recuperação de concessão expirada é uma operação atômica que invalida o token anterior e inicia uma nova tentativa. Detalhes estão em [Contratos e DTOs](docs/contratos.md).

## Organização da entrega

Os quatro diagramas também estão disponíveis no [Mermaid Chart](docs/mermaid-links.md).

- `docs/diagrams/`: sequência, atividades, estados e interfaces em Mermaid.
- `docs/architecture/`: C4 de componentes e ADR0001.
- `docs/rendered/`: imagens PNG, SVG e relatório de renderização.
- `docs/contratos.md`: DTOs, operações, idempotência e transições condicionais.
- `docs/validacao.md`: atendimento ao enunciado e cenários de aceitação.
- `scripts/gerar_readme.py`: incorpora os códigos e a ADR neste README.
- `scripts/verificar_modelos.py`: confere operações, fontes incorporadas e correspondência dos renders.

As imagens permitem leitura imediata; os blocos Mermaid incorporados em cada seção são as fontes editáveis. Os SVGs permitem ampliar sem perder definição.

## Verificação e manutenção

Os cinco diagramas (quatro exigidos e um de interfaces de apoio) foram analisados e renderizados com Mermaid 10.9.3. A versão foi fixada para a conferência local; as imagens no README também atendem a leitores sem suporte Mermaid.

Depois de alterar uma fonte, regenere sua imagem, atualize o registro de hash no relatório de renderização e execute `python scripts/gerar_readme.py` e `python scripts/verificar_modelos.py`. Nunca atualize só a imagem: a fonte é a referência para revisão e versionamento.

Robot Framework fica reservado à automação futura dos cenários de [validação](docs/validacao.md). Não há testes de aplicação executados, API publicada ou recursos criados no Supabase por este trabalho.

## Versionamento, autoria e entrega

Esta modelagem individual adapta as abstrações do grupo ao recorte escolhido, com elaboração e revisão assistidas pelo Codex. As RPCs, interfaces e o cálculo paramétrico são especificações propostas. Os commits devem refletir mudanças reais, sem reconstrução artificial de datas ou histórico.

A entrega final requer publicar este diretório no repositório individual e enviar o link no AVA. Nenhum repositório remoto nem envio ao AVA foi realizado nesta conversa.

## Referências

- Sprint1_Grupo6.pdf: abstrações de domínio, atores e requisitos do projeto.
- sprint2.docx: escopo, fronteiras e classes conceituais. A assinatura original do cálculo foi refinada para receber configuração e devolver um DTO.
- Enunciado APS 3: Dossiê de Arquitetura Viva e Modelagem Comportamental as-Code.
- [Mermaid — sequência e setas assíncronas](https://mermaid.js.org/syntax/sequenceDiagram.html)
- [Mermaid — estados compostos](https://mermaid.js.org/syntax/stateDiagram.html)
- [Mermaid — flowcharts](https://mermaid.js.org/syntax/flowchart.html)
- [C4 Model — componentes](https://c4model.com/diagrams/component)
- [Supabase Queues](https://supabase.com/docs/guides/queues)
- [Supabase — consumo ativo da fila](https://supabase.com/docs/guides/queues/quickstart)
- [Supabase — operações de mensagens](https://supabase.com/docs/guides/queues/api)
- [Supabase Data API](https://supabase.com/docs/guides/api)
