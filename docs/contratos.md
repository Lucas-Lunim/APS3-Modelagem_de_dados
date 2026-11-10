# Contratos públicos e dados de matching

## Regra de leitura

O diagrama de interfaces declara todas as operações chamadas na sequência. Uma seta síncrona `->>` é uma invocação; `-->>` devolve o DTO da operação anterior; `-)` representa a entrega lógica assíncrona do comando. Retornos não são novas operações no destinatário. O estudante é ator, não uma classe de serviço.

O comando `FilaMatching -> ExecutorMatching.processar` é uma abstração do transporte: Supabase Queues é uma fila de consumo ativo (pull). No nível de implementação, o Consumidor da Fila lê com `pgmq_public.read` e despacha o comando ao executor Python. A API não chama diretamente o worker nem depende da duração do cálculo.

## Correspondência das chamadas

| Destinatário | Operação pública | Retorno |
| --- | --- | --- |
| MatchingAPI | solicitar(SolicitarMatchingDTO) | SolicitacaoDTO |
| MatchingAPI | consultar(id) | ConsultaMatchingDTO |
| FilaMatching | publicarSolicitacao(PedidoMatchingDTO) | SolicitacaoDTO |
| FilaMatching | confirmar(mensagemId) | ConfirmacaoDTO |
| ExecutorMatching | processar(MensagemMatchingDTO) | void |
| ExecutorMatching | validarEntradas(ConsultaPerfilDTO, ConsultaDemandaDTO, ConsultaPoliticaDTO) | ValidacaoDTO |
| RepositorioDados | buscarPerfil(idEstudante) | ConsultaPerfilDTO |
| RepositorioDados | buscarDemanda(idDemanda) | ConsultaDemandaDTO |
| RepositorioDados | buscarPolitica(versao) | ConsultaPoliticaDTO |
| PoliticaMatching | calcular(PerfilCompetencias, DemandaTecnica, ConfiguracaoPolitica) | ResultadoMatchingDTO |
| RepositorioMatching | iniciarTentativa(id, mensagemId) | TentativaDTO |
| RepositorioMatching | registrarEtapa(id, token, etapa) | PersistenciaDTO |
| RepositorioMatching | concluir(id, token, resultado) | PersistenciaDTO |
| RepositorioMatching | rejeitar(id, token, motivos) | PersistenciaDTO |
| RepositorioMatching | registrarFalha(id, token, motivo) | PersistenciaDTO |
| RepositorioMatching | consultar(id) | ConsultaMatchingDTO |

Todas essas operações são públicas, representadas por `+` em `interfaces.mmd`. Funções de entrada/saída da máquina de estados descrevem comportamentos internos, não endpoints HTTP adicionais.

## DTOs

| Tipo | Campos essenciais e significado |
| --- | --- |
| SolicitarMatchingDTO | idDemanda: UUID; chaveIdempotencia: string. O estudante é obtido da identidade autenticada. |
| PedidoMatchingDTO | idEstudante: UUID; idDemanda: UUID; chaveIdempotencia: string; versaoPolitica: string ou null, fixada no recebimento. |
| SolicitacaoDTO | solicitacaoId: UUID; estado: Pendente ou estado já existente em pedido repetido; recebidaEm: timestamp; versaoPolitica: string ou null. |
| MensagemMatchingDTO | mensagemId: inteiro; solicitacaoId: UUID; idEstudante: UUID; idDemanda: UUID; versaoPolitica: string ou null. |
| TentativaDTO | adquirida: bool; token: UUID ou null; concessaoAte: timestamp ou null; estadoAtual: estado da solicitação. |
| ConsultaPerfilDTO | falhaTecnica: bool; encontrado: bool; perfil: PerfilCompetencias ou null; versaoPerfil: string ou null; motivo: string ou null. |
| ConsultaDemandaDTO | falhaTecnica: bool; encontrada: bool; publicada: bool; convenioValido: bool; demanda: DemandaTecnica ou null; versaoDemanda: string ou null; motivo: string ou null. |
| ConsultaPoliticaDTO | falhaTecnica: bool; encontrada: bool; publicada: bool; configuracao: ConfiguracaoPolitica ou null; versaoPolitica: string ou null; motivo: string ou null. |
| ValidacaoDTO | valida: bool; motivos: lista de códigos de domínio. |
| ResultadoMatchingDTO | ok: bool; grau: decimal de 0 a 100 ou null; versaoPolitica: string; evidencias: contribuições por critério; motivo: string ou null. |
| PersistenciaDTO | aplicada: bool; estadoAtual: estado; tokenVigente: bool. Uma gravação recusada não autoriza sobrescrever o estado. |
| ConsultaMatchingDTO | solicitacaoId; estado; etapa; estadoTerminal: bool; resultado: ResultadoMatchingDTO ou null; motivos; versaoPerfil; versaoDemanda; versaoPolitica; concluidaEm: timestamp ou null. |
| ConfirmacaoDTO | mensagemId; arquivada: bool. Confirmação repetida é tratada de forma idempotente. |

## Projeções de domínio

`PerfilCompetencias` reúne as informações necessárias do perfil e do aluno: competências, formação, horas disponíveis e localização, quando exigidas pela configuração. `DemandaTecnica` reúne competências e formação requeridas, carga horária e localização da vaga. A origem e a forma de comparar esses campos ainda precisam de definição de negócio.

`ConfiguracaoPolitica` contém versão imutável, situação de publicação, critérios habilitados, pesos e regras de comparação por critério. Configuração incompleta ou ausente não deve gerar nota.

A operação conceitual da Sprint 2 `calcular(perfil, demanda): double` foi refinada nesta proposta: recebe configuração explicitamente e retorna DTO com nota, versão e evidências. Esse refinamento está aplicado de forma uniforme aos artefatos da APS 3; não altera os arquivos de referência.

## Pré-condições, invariantes e erros

- O estudante acessa somente solicitações permitidas pelo seu perfil de acesso; identificação do dono é aplicada no backend.
- Pedido com identificadores malformados ou acesso não autorizado é recusado pela API antes do fluxo mostrado. O diagrama principal parte de pedido autenticado e estruturalmente válido.
- Perfil existente, demanda publicada, convênio válido e configuração publicada/completa são requisitos para calcular.
- Somente o token vigente pode registrar etapa ou estado terminal. Estado terminal é imutável.
- `iniciarTentativa` adquire concessão atomicamente. Em recuperação, invalida o token expirado e inicia uma nova tentativa. Consumidor obsoleto abandona o processamento quando uma mudança de etapa é recusada.
- Cada consulta paralela termina com DTO de dados ou erro, inclusive em timeout; nenhum ramo pode deixar o Join aguardando indefinidamente.
- Falha de leitura ou do cálculo produz FalhaTecnica; ausência de dados ou política inválida produz Rejeitada.
- Em falha ao persistir, o consumidor não confirma a mensagem. Uma nova leitura da fila permite recuperar a execução.
- A confirmação ocorre somente após consulta do estado terminal persistido. Se ela falhar, a reentrega encontra o estado terminal e confirma sem recalcular.
- Um novo cálculo após desfecho terminal é outra solicitação, com outra chave. Repetir a mesma chave com conteúdo diferente é conflito; repetir a mesma chave e conteúdo retorna o identificador original.

## Implementação proposta no Supabase

`FilaMatching.publicarSolicitacao` é uma fachada para uma RPC PostgreSQL proposta: inserir a solicitação Pendente e executar `pgmq.send` na mesma transação. A restrição única da chave por estudante deve impedir solicitações duplicadas. A API só retorna aceitação após sucesso dessa operação; rollback não deixa pedido aceito sem mensagem.

As mudanças de estado também são RPCs propostas, com comparação do estado esperado, token e prazo da concessão em uma única operação transacional. Elas não são sequências de requisições REST independentes.

O Consumidor da Fila usa `read` com tempo de visibilidade e `archive` após conclusão persistida. Não usa `pop`, que removeria o comando antes do processamento. A concessão deve cobrir o prazo de processamento configurado; se expirar, a tentativa antiga perde o direito de gravar.

Essas RPCs, as tabelas e os workers são especificações arquiteturais. Não foram criados em nenhuma conta Supabase.

## Estados persistidos

Os efeitos prepararFalha(), prepararRejeicao() e prepararDesfecho() selecionam um desfecho local da tentativa. Na máquina de estados, persistirDesfecho() delega para registrarFalha(), rejeitar() ou concluir(), conforme esse desfecho. A escolha não é um novo estado persistido. Falha na RPC impede a efetivação da transição, preservando a possibilidade de recuperação.

Na chamada de calcular(), perfil.perfil e demanda.demanda extraem as projeções dos DTOs de consulta; politica.configuracao contém a configuração. Não se passa o envelope de transporte como entidade de domínio.

`estado` assume Pendente, Processando, Concluida, Rejeitada ou FalhaTecnica. Em Processando, `etapa` assume CarregandoDados, ValidandoDados ou Calculando. A notação composta da máquina de estados corresponde a esses dois campos.

A recuperação de concessão expirada, representada por Processando -> Pendente -> Processando, ocorre dentro da operação atômica `iniciarTentativa`. Os estados intermediários dessa recuperação são lógicos; não há janela para o token antigo gravar após a aquisição do novo.
