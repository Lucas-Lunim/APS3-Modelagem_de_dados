# APS 3 — PoliticaMatching

**Aluno:** Lucas Gabriel de Carvalho de Oliveira  
**Projeto:** Sistema de Gestão de Aprendizagem e Estágios da UniSenai.

## Funcionalidade

Calcular a compatibilidade entre o perfil do estudante e os requisitos de uma vaga industrial. A análise orienta as recomendações de vagas.

A aplicação Python recebe o pedido, inicia uma tarefa assíncrona e permite consultar seu estado. Perfil e vaga são buscados em paralelo no Supabase. Com dados válidos, PoliticaMatching calcula a compatibilidade e o resultado é salvo.

`dadosValidos = perfil.encontrado && demanda.encontrada && demanda.publicada && demanda.convenioValido`

O serviço inicia o processamento somente no estado Recebida. Cada solicitação possui uma única tarefa; os estados Concluida, Rejeitada e Falha não aceitam novas alterações. Erros técnicos são capturados pela tarefa e levam ao estado Falha. Falhas reportadas pelo cálculo ou pela gravação também levam a Falha.

Os critérios de comparação e seus pesos ainda serão definidos pela equipe. Os diagramas representam o fluxo do cálculo, sem atribuir pesos ou uma fórmula como regra aprovada.

## Tecnologias

- Python: API, tarefa assíncrona com asyncio e regra de matching.
- Supabase: consulta de perfis e vagas e armazenamento de resultados.
- Robot Framework: tecnologia prevista para testes; esta atividade entrega a modelagem.

## Operações públicas

Assinaturas das classes utilizadas no diagrama de sequência:

```python
class MatchingAPI:
    def solicitar(self, pedido: PedidoMatchingDTO) -> SolicitacaoDTO: ...
    def consultar(self, id: str) -> ConsultaMatchingDTO: ...

class ServicoMatching:
    def criar(self, pedido: PedidoMatchingDTO) -> SolicitacaoDTO: ...
    async def processar(self, id: str) -> None: ...
    def consultar(self, id: str) -> ConsultaMatchingDTO: ...

class RepositorioDados:
    async def buscarPerfil(self, perfilId: str) -> PerfilDTO: ...
    async def buscarDemanda(self, demandaId: str) -> DemandaDTO: ...
    async def salvarResultado(self, id: str, resultado: ResultadoMatchingDTO) -> GravacaoDTO: ...

class PoliticaMatching:
    def calcular(self, perfil: PerfilDTO, demanda: DemandaDTO) -> ResultadoMatchingDTO: ...
```

## Dados retornados

| DTO | Conteúdo |
| --- | --- |
| PedidoMatchingDTO | perfilId e demandaId |
| SolicitacaoDTO | id e estado |
| PerfilDTO | encontrado e dados de competências, formação, disponibilidade e localização |
| DemandaDTO | encontrada, publicada, convenioValido e requisitos da vaga |
| ResultadoMatchingDTO | sucesso, grau de compatibilidade e motivo de falha, quando houver |
| GravacaoDTO | sucesso |
| ConsultaMatchingDTO | id, estado, resultado e motivo, quando houver |

## Diagrama de sequência

```mermaid
sequenceDiagram
    actor Estudante
    participant API as MatchingAPI
    participant Servico as ServicoMatching
    participant Dados as RepositorioDados
    participant Politica as PoliticaMatching

    Estudante->>API: solicitar(PedidoMatchingDTO)
    API->>Servico: criar(pedido)
    Servico-->>API: SolicitacaoDTO
    API-)Servico: processar(id)
    API-->>Estudante: SolicitacaoDTO / HTTP 202

    par Buscar perfil
        Servico->>Dados: buscarPerfil(perfilId)
        Dados-->>Servico: PerfilDTO
    and Buscar vaga
        Servico->>Dados: buscarDemanda(demandaId)
        Dados-->>Servico: DemandaDTO
    end

    alt dadosValidos
        Servico->>Politica: calcular(perfil, demanda)
        Politica-->>Servico: ResultadoMatchingDTO
        alt resultado.sucesso
            Servico->>Dados: salvarResultado(id, resultado)
            Dados-->>Servico: GravacaoDTO
            Note over Servico: Concluida se gravacao.sucesso. Caso contrário, Falha.
        else falha no cálculo
            Note over Servico: Registrar estado Falha e motivo
        end
    else dados inválidos
        Note over Servico: Registrar estado Rejeitada e motivo
    end

    Estudante->>API: consultar(id)
    API->>Servico: consultar(id)
    Servico-->>API: ConsultaMatchingDTO
    API-->>Estudante: ConsultaMatchingDTO
```

## Diagrama de atividades com raias

```mermaid
flowchart TB
    subgraph ALUNO["Raia 1 - Estudante"]
        I(( ))
        PEDIR("Solicitar matching")
        VER("Consultar estado e resultado")
        F((("●")))
    end
    subgraph SISTEMA["Raia 2 - Aplicação Python"]
        CRIAR("Criar solicitação Recebida e retornar identificador")
        INICIAR("Iniciar tarefa assíncrona - EmAnalise")
        FORK["<span style='display:block;width:140px;height:1px'></span>"]
        JOIN["<span style='display:block;width:140px;height:1px'></span>"]
        VALIDAR{"Dados válidos?"}
        CALCULAR("PoliticaMatching.calcular")
        OK{"Cálculo bem-sucedido?"}
        SALVOU{"Resultado salvo?"}
        CONCLUIR("Marcar Concluida")
        REJEITAR("Marcar Rejeitada e motivo")
        MERGE_FALHA{" "}
        FALHAR("Marcar Falha e motivo")
        MERGE_FINAL{" "}
        DISPONIVEL("Disponibilizar estado e resultado")
    end
    subgraph BANCO["Raia 3 - Supabase"]
        PERFIL("Buscar perfil")
        VAGA("Buscar vaga e convênio")
        SALVAR("Salvar resultado")
    end
    I --> PEDIR --> CRIAR --> INICIAR --> FORK
    FORK --> PERFIL --> JOIN
    FORK --> VAGA --> JOIN
    JOIN --> VALIDAR
    VALIDAR -- "[dadosValidos]" --> CALCULAR --> OK
    VALIDAR -- "[!dadosValidos]" --> REJEITAR --> MERGE_FINAL
    OK -- "[resultado.sucesso]" --> SALVAR --> SALVOU
    OK -- "[!resultado.sucesso]" --> MERGE_FALHA
    SALVOU -- "[gravacao.sucesso]" --> CONCLUIR --> MERGE_FINAL
    SALVOU -- "[!gravacao.sucesso]" --> MERGE_FALHA
    MERGE_FALHA --> FALHAR --> MERGE_FINAL
    MERGE_FINAL --> DISPONIVEL
    DISPONIVEL --> VER --> F

    classDef barra fill:#243B53,stroke:#243B53,color:#243B53;
    class FORK,JOIN,I barra;
    style ALUNO fill:#F5F7FA,stroke:#829AB1
    style SISTEMA fill:#EDF4FC,stroke:#6285AA
    style BANCO fill:#EAF5EF,stroke:#658F7C
```

## Diagrama de estados

```mermaid
stateDiagram-v2
    state "Recebida" as Recebida
    state "EmAnalise" as EmAnalise {
        state "BuscandoDados" as BuscandoDados
        state "Calculando" as Calculando
        [*] --> BuscandoDados
        BuscandoDados : do / buscarDadosEValidar()
        BuscandoDados --> Calculando : dadosCarregados<br/>[dadosValidos]<br/>/ iniciarCalculo()
        Calculando : do / calcularESalvarResultado()
    }
    state "Concluida" as Concluida
    state "Rejeitada" as Rejeitada
    state "Falha" as Falha
    [*] --> Recebida
    Recebida --> EmAnalise : iniciarProcessamento<br/>[estado == Recebida]<br/>/ iniciarTarefa()
    Calculando --> Concluida : resultadoGravado<br/>[resultado.sucesso && gravacao.sucesso]<br/>/ registrarResultado()
    BuscandoDados --> Rejeitada : dadosCarregados<br/>[!dadosValidos]<br/>/ registrarMotivo()
    EmAnalise --> Falha : processamentoFalhou<br/>[houveFalha]<br/>/ registrarErro()
    Concluida --> [*]
    Rejeitada --> [*]
    Falha --> [*]
```

## C4 nível 3 de componentes

```mermaid
flowchart TB
    CLIENTE["Interface do estudante<br/>[Contêiner: Web]"]
    subgraph APP["Aplicação Python - C4 nível 3"]
        API["MatchingAPI<br/>[Componente: Python]<br/>Recebe pedidos e consultas"]
        SERVICO["ServicoMatching<br/>[Componente: Python / asyncio]<br/>Executa a análise e controla o estado"]
        POLITICA["PoliticaMatching<br/>[Componente: Python]<br/>Calcula a compatibilidade"]
        DADOS["RepositorioDados<br/>[Componente: Python / supabase-py]<br/>Consulta dados e salva resultados"]
        API -->|"Criar e consultar<br/>Chamada Python"| SERVICO
        API -. "Processar em segundo plano<br/>Tarefa asyncio" .-> SERVICO
        SERVICO -->|"calcular<br/>Chamada Python"| POLITICA
        SERVICO -->|"buscar e salvar<br/>Chamadas Python"| DADOS
    end
    SUPABASE["Supabase<br/>[Sistema externo: PostgreSQL / PostgREST]<br/>Perfis, vagas, convênios e resultados"]
    CLIENTE -->|"Solicitar e consultar<br/>HTTPS / JSON"| API
    DADOS -->|"Ler e gravar<br/>REST / HTTPS / JSON"| SUPABASE

    classDef componente fill:#E7EFF9,stroke:#5D7FA1,color:#17324D;
    class API,SERVICO,POLITICA,DADOS componente;
    style APP fill:#F7FAFC,stroke:#829AB1
```

## ADR0001

### ADR 0001 — Separar o cálculo de matching das consultas aos dados

#### Status

Proposto.

#### Contexto

O sistema precisa comparar o perfil do estudante com os requisitos da vaga. A regra de cálculo deve poder mudar sem alterar as consultas ao Supabase. A equipe ainda não definiu os critérios quantitativos nem seus pesos.

#### Decisão

Manter o cálculo em um componente Python chamado PoliticaMatching. O ServicoMatching busca perfil e vaga em paralelo, valida os dados e chama a política.

A API inicia uma tarefa em segundo plano com asyncio e retorna o identificador da solicitação. O estado é acompanhado em memória pelo serviço. O RepositorioDados usa a API REST do Supabase por HTTPS/JSON para consultar as entradas e salvar o resultado.

O processamento só começa no estado Recebida. Somente uma tarefa é responsável por cada solicitação, e estados terminais não podem ser alterados.

#### Consequências

- A regra de cálculo fica separada do acesso ao banco.
- A interface pode consultar o estado enquanto o processamento ocorre.
- A solução utiliza uma aplicação Python e Supabase.
- Uma reinicialização da aplicação pode perder as tarefas e os estados em memória; nesse caso, o estudante precisa solicitar uma nova análise.
- Os critérios e pesos ainda precisam ser definidos pela equipe.
