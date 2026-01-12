---
title: "Case Técnico – Data Analyst Senior"
author: "Luís Guilherme Ferreira Bizzi"
description: "AI-Powered Insights for Automotive Dealership Operations"
paginate: true
---

# Case Técnico – Data Analyst Senior

AI-Powered Insights for Automotive Dealership Operations  
Luís Guilherme Ferreira Bizzi  

<!-- TODO: inserir logotipo da empresa / sua foto aqui -->
![Foto profissional](images/Eu_2025.png)

---

## Sobre mim

- **Formação:** Bacharel em Engenharia de Software, com foco em dados, BI e IA aplicada a negócios.
- **Atual:** IT Business Analyst no Sicoob São Paulo, liderando criação da divisão de Dados, RPA e arquitetura de Data Pipeline corporativo.
- **Experiência prévia:** Tech Lead Power BI e SQL em consultoria SAP Business One, desenvolvendo dashboards, integrações e treinando equipes.
- **Stack principal:** Python, SQL, Power BI, Oracle, PostgreSQL, LangChain, Streamlit, metodologias ágeis.

<!-- TODO: inserir foto profissional ou avatar -->

---

## Contexto do case

- Desenvolvimento de um sistema de IA para analisar dados de **veículos, peças, serviços e inventário** de uma rede de concessionárias.
- Objetivo: gerar insights para entender tendências, otimizar estoque e apoiar a gestão na tomada de decisão.
- Entregáveis sugeridos: identificação de padrões, previsão de necessidades de estoque e relatórios em linguagem natural usando APIs OpenAI.

---

## Objetivos de negócio

- Identificar **padrões de vendas e tendências de serviços** ao longo do tempo.
- Prever **necessidades de estoque** para reduzir rupturas e excesso de inventário.
- Apoiar a gestão com **insights acionáveis**, conectando indicadores a decisões práticas.
- Automatizar **relatórios em linguagem natural**, aproximando dados da linguagem do negócio.

---

## Visão da solução

- Arquitetura pensada no modelo **medalhão**:
  - Bronze: armazenamento dos dados brutos em Oracle, espelhando os arquivos CSV.
  - Silver: dados limpos, padronizados e prontos para análise.
  - Gold: dados enriquecidos, consolidados e orientados a métricas de negócio.
- Três frentes principais:
  - ETL automatizado em Python.
  - Agente de IA (LLM) conectado ao banco Oracle.
  - Visualizações interativas em Streamlit.
- Projeto disponibilizado no Github: https://github.com/lgbizzi/CaseDataAnalystSenior_Autos-Code-Assessment

<!-- TODO: inserir diagrama de arquitetura (medalhão + Oracle + LLM + Streamlit) -->
<!-- ![Arquitetura da solução](caminho/para/arquitetura.png) -->

---

## Recorte do MVP

- Limitação de tempo → foco em um **MVP funcional ponta a ponta**:
  1. Entendimento do dicionário de dados e avaliação de qualidade das bases.
  2. Provisionamento de banco Oracle via Docker e criação de tabelas Bronze.
  3. Implementação de ETL em Python com tratamentos de inconsistências.
  4. Criação de um agente de IA (LLM) com LangChain + OpenAI conectado ao Oracle.
  5. Desenvolvimento de aplicação Streamlit com visuais para stakeholders.

---

## Entendimento dos dados (1/2)

- **Estoque de Veículos:**
  - Valores nulos e colunas repetidas (ex.: múltiplas `Data_de_Entrada`).
  - Ações: limpeza de nulos críticos, remoção de duplicatas e ajuste de estrutura.
- **Histórico de Vendas de Veículos:**
  - Coluna vazia com dezenas de milhares de nulos e registros duplicados.
  - Ações: remoção de coluna inútil, deduplicação e validação de margens.

---

## Entendimento dos dados (2/2)

- **Histórico de Serviços:**
  - Margens anômalas (lucro > receita), indicando possíveis problemas de semântica.
  - Ações: investigação do conceito de lucro/receita e uso com cautela em análises.
- **Estoque e Vendas de Peças:**
  - Lucros negativos, margens > 100%, custos zerados e transações negativas.
  - Ações: padronização de margens por canal, revisão de custos e tratamento de devoluções.

<!-- TODO: inserir print de notebook/relatório de data profiling ou tabelas de exemplo -->
<!-- ![Data profiling](caminho/para/profiling.png) -->

### Qualidade dos Dados

| Base | Registros | Colunas | Status | Observações |
|------|-----------|---------|--------|------------|
| Estoque de Veículos | 255 | 16 | ⚠️ Com Problemas | 10 valores nulos, 3 duplicatas, colunas repetidas |
| Estoque de Peças | 5.332 | 15 | ✅ Limpo | Sem valores nulos, sem duplicatas |
| Histórico de Serviços Realizados | 35.803 | 22 | ✅ Limpo | Sem valores nulos, sem duplicatas |
| Histórico de Vendas de Veículos | 41.666 | 28 | ⚠️ Com Problemas | 41.772 valores nulos, 1.417 duplicatas |
| Histórico de Vendas de Peças | ~250k+ | 19 | ⚠️ Com Problemas | Acentuações nos Nomes |
| **TOTAL** | **~333k+** | **100** | - | Dados integrados de ciclo completo |

---

## Banco Oracle em Docker

- Criação de container Oracle para ambiente isolado de desenvolvimento:
  - Definição de senha, volume de dados e mapeamento de porta.
  - Exemplo: `docker run` parametrizado para subir o Oracle Free.
- Passos principais:
  - Conexão via SQLPlus dentro do container.
  - Seleção do PDB (`FREEPDB1`).
  - Criação de usuário dedicado ao projeto com permissões adequadas.

<!-- TODO: inserir captura de tela do terminal com container Oracle rodando -->
<!-- ![Docker Oracle](caminho/para/docker_oracle.png) -->

### Comandos
```bash
docker run --name oracle_db_container \
  -p 1521:1521 \
  -e ORACLE_PWD=123@Troca \
  container-registry.oracle.com/database/free:latest
```

---

## Modelagem – Camada Bronze

- Criação de tabelas espelhando o dicionário de dados:
  - `BRZ_ESTOQUE_PECAS`, `BRZ_ESTOQUE_VEICULOS`,
    `BRZ_HIST_SERVICOS`, `BRZ_HIST_VENDAS_PECAS`,
    `BRZ_HIST_VENDAS_VEICULOS`.
- Decisões de modelagem:
  - Chaves técnicas (ID identity) para cada tabela.
  - Índices em colunas de alto volume de consultas (filial, datas, peça/veículo, vendedor).
  - FKs lógicas planejadas para futura evolução Silver/Gold.

<!-- TODO: inserir trecho ilustrativo de DDL (print ou imagem) -->
<!-- ![DDL das tabelas Bronze](caminho/para/ddl.png) -->

### Queries
```sql
-- BRZ_ESTOQUE_PECAS
CREATE TABLE BRZ_ESTOQUE_PECAS (
    ID_ESTOQUE_PECA          NUMBER GENERATED BY DEFAULT AS IDENTITY,
    COD_CONCESSIONARIA       VARCHAR2(10)   NOT NULL,
    COD_FILIAL               VARCHAR2(10)   NOT NULL,
    NOME_CONCESSIONARIA      VARCHAR2(100),
    NOME_FILIAL              VARCHAR2(100),
    MARCA_FILIAL             VARCHAR2(50),
    VALOR_PECA_ESTOQUE       NUMBER(18,2),
    QTDE_PECA_ESTOQUE        NUMBER(18,2),
    DESCRICAO_PECA           VARCHAR2(200),
    CATEGORIA_PECA           VARCHAR2(100),
    DT_ULTIMA_VENDA_PECA     DATE,
    DT_ULTIMA_ENTRADA_PECA   DATE,
    PECA_OBSOLETA_FLAG       VARCHAR2(3),
    TEMPO_OBSOLETA_DIAS      NUMBER(10),
    MARCA_PECA               VARCHAR2(100),
    CODIGO_PECA_ESTOQUE      VARCHAR2(50),
    CONSTRAINT PK_BRZ_ESTOQUE_PECAS
        PRIMARY KEY (ID_ESTOQUE_PECA)
);

-- Índices recomendados
CREATE INDEX IX_BRZ_EST_PECAS_FILIAL
    ON BRZ_ESTOQUE_PECAS (COD_CONCESSIONARIA, COD_FILIAL);

CREATE INDEX IX_BRZ_EST_PECAS_CODIGO
    ON BRZ_ESTOQUE_PECAS (CODIGO_PECA_ESTOQUE);



-- BRZ_ESTOQUE_VEICULOS
CREATE TABLE BRZ_ESTOQUE_VEICULOS (
    ID_ESTOQUE_VEICULO        NUMBER GENERATED BY DEFAULT AS IDENTITY,
    COD_CONCESSIONARIA        VARCHAR2(10)   NOT NULL,
    COD_FILIAL                VARCHAR2(10)   NOT NULL,
    NOME_CONCESSIONARIA       VARCHAR2(100),
    NOME_FILIAL               VARCHAR2(100),
    MARCA_FILIAL              VARCHAR2(50),
    CUSTO_VEICULO             NUMBER(18,2),
    MARCA_VEICULO             VARCHAR2(50),
    MODELO_VEICULO            VARCHAR2(100),
    COR_VEICULO               VARCHAR2(50),
    VEICULO_NOVO_SEMINOVO     VARCHAR2(20),
    TIPO_COMBUSTIVEL          VARCHAR2(30),
    ANO_MODELO                NUMBER(4),
    ANO_FABRICACAO            NUMBER(4),
    CHASSI_VEICULO            VARCHAR2(50),
    TEMPO_TOTAL_ESTOQUE_DIAS  NUMBER(10),
    KM_ATUAL                  NUMBER(10),
    PLACA_VEICULO             VARCHAR2(20),
    DT_ENTRADA_ESTOQUE        DATE,
    CONSTRAINT PK_BRZ_ESTOQUE_VEICULOS
        PRIMARY KEY (ID_ESTOQUE_VEICULO),
    CONSTRAINT UQ_BRZ_EST_VEICULOS_CHASSI
        UNIQUE (CHASSI_VEICULO)
);

-- Índices
CREATE INDEX IX_BRZ_EST_VEIC_FILIAL
    ON BRZ_ESTOQUE_VEICULOS (COD_CONCESSIONARIA, COD_FILIAL);

CREATE INDEX IX_BRZ_EST_VEIC_MODELO
    ON BRZ_ESTOQUE_VEICULOS (MARCA_VEICULO, MODELO_VEICULO);




-- BRZ_HIST_SERVICOS
CREATE TABLE BRZ_HIST_SERVICOS (
    ID_SERVICO                 NUMBER GENERATED BY DEFAULT AS IDENTITY,
    COD_CONCESSIONARIA         VARCHAR2(10)   NOT NULL,
    COD_FILIAL                 VARCHAR2(10)   NOT NULL,
    NOME_CONCESSIONARIA        VARCHAR2(100),
    NOME_FILIAL                VARCHAR2(100),
    DT_REALIZACAO_SERVICO      DATE           NOT NULL,
    QTDE_SERVICOS              NUMBER(10),
    VALOR_TOTAL_SERVICO        NUMBER(18,2),
    LUCRO_SERVICO              NUMBER(18,2),
    DESCRICAO_SERVICO          VARCHAR2(200),
    SECAO_SERVICO              VARCHAR2(100),
    DEPARTAMENTO_SERVICO       VARCHAR2(100),
    CATEGORIA_SERVICO          VARCHAR2(100),
    NOME_VENDEDOR_SERVICO      VARCHAR2(100),
    NOME_MECANICO              VARCHAR2(100),
    NOME_CLIENTE               VARCHAR2(150),
    CONSTRAINT PK_BRZ_HIST_SERVICOS
        PRIMARY KEY (ID_SERVICO)
);

-- Índices (alto volume de linhas)
CREATE INDEX IX_BRZ_SERV_FILIAL_DATA
    ON BRZ_HIST_SERVICOS (COD_CONCESSIONARIA, COD_FILIAL, DT_REALIZACAO_SERVICO);

CREATE INDEX IX_BRZ_SERV_DEPARTAMENTO
    ON BRZ_HIST_SERVICOS (DEPARTAMENTO_SERVICO);

CREATE INDEX IX_BRZ_SERV_VENDEDOR
    ON BRZ_HIST_SERVICOS (NOME_VENDEDOR_SERVICO);



-- BRZ_HIST_VENDAS_PECAS
CREATE TABLE BRZ_HIST_VENDAS_PECAS (
    ID_VENDA_PECA              NUMBER GENERATED BY DEFAULT AS IDENTITY,
    COD_CONCESSIONARIA         VARCHAR2(10)   NOT NULL,
    COD_FILIAL                 VARCHAR2(10)   NOT NULL,
    NOME_CONCESSIONARIA        VARCHAR2(100),
    NOME_FILIAL                VARCHAR2(100),
    MARCA_FILIAL               VARCHAR2(50),
    DT_VENDA                   DATE           NOT NULL,
    QTDE_VENDIDA               NUMBER(18,2),
    TIPO_TRANSACAO             VARCHAR2(50),
    VALOR_VENDA                NUMBER(18,2),
    CUSTO_PECA                 NUMBER(18,2),
    LUCRO_VENDA                NUMBER(18,2),
    MARGEM_VENDA               NUMBER(9,4),
    DESCRICAO_PECA             VARCHAR2(200),
    CATEGORIA_PECA             VARCHAR2(100),
    DEPARTAMENTO_VENDA         VARCHAR2(100),
    TIPO_VENDA_PECA            VARCHAR2(100),
    NOME_VENDEDOR              VARCHAR2(100),
    NOME_COMPRADOR             VARCHAR2(150),
    CIDADE_VENDA               VARCHAR2(100),
    ESTADO_VENDA               VARCHAR2(50),
    MACROREGIAO_VENDA          VARCHAR2(50),
    CONSTRAINT PK_BRZ_HIST_VENDAS_PECAS
        PRIMARY KEY (ID_VENDA_PECA)
);

-- FKs lógicas (mesmo que Bronze não valide fisicamente, já deixa pronto)
-- Ex.: para futura Dim_Peca (SILVER/GOLD), o join será por DESCRICAO/CATEGORIA
-- e para filial por COD_CONCESSIONARIA/COD_FILIAL. [file:2]

-- Índices (tabela de maior volume)
CREATE INDEX IX_BRZ_VP_FILIAL_DATA
    ON BRZ_HIST_VENDAS_PECAS (COD_CONCESSIONARIA, COD_FILIAL, DT_VENDA);

CREATE INDEX IX_BRZ_VP_PECA
    ON BRZ_HIST_VENDAS_PECAS (DESCRICAO_PECA, CATEGORIA_PECA);

CREATE INDEX IX_BRZ_VP_VENDEDOR
    ON BRZ_HIST_VENDAS_PECAS (NOME_VENDEDOR);

CREATE INDEX IX_BRZ_VP_CIDADE_ESTADO
    ON BRZ_HIST_VENDAS_PECAS (ESTADO_VENDA, CIDADE_VENDA);



-- BRZ_HIST_VENDAS_VEICULOS
CREATE TABLE BRZ_HIST_VENDAS_VEICULOS (
    ID_VENDA_VEICULO           NUMBER GENERATED BY DEFAULT AS IDENTITY,
    COD_CONCESSIONARIA         VARCHAR2(10)   NOT NULL,
    COD_FILIAL                 VARCHAR2(10)   NOT NULL,
    NOME_CONCESSIONARIA        VARCHAR2(100),
    NOME_FILIAL                VARCHAR2(100),
    MARCA_FILIAL               VARCHAR2(50),
    DT_VENDA                   DATE           NOT NULL,
    QTDE_VENDIDA               NUMBER(10),
    TIPO_TRANSACAO             VARCHAR2(50),
    VALOR_VENDA                NUMBER(18,2),
    CUSTO_VEICULO              NUMBER(18,2),
    LUCRO_VENDA                NUMBER(18,2),
    MARGEM_VENDA               NUMBER(9,4),
    MARCA_VEICULO              VARCHAR2(50),
    MODELO_VEICULO             VARCHAR2(100),
    FAMILIA_VEICULO            VARCHAR2(100),
    CATEGORIA_VEICULO          VARCHAR2(100),
    COR_VEICULO                VARCHAR2(50),
    VEICULO_NOVO_SEMINOVO      VARCHAR2(20),
    TIPO_COMBUSTIVEL           VARCHAR2(30),
    ANO_MODELO                 NUMBER(4),
    ANO_FABRICACAO             NUMBER(4),
    CHASSI_VEICULO             VARCHAR2(50),
    DIAS_EM_ESTOQUE            NUMBER(10),
    TIPO_VENDA_VEICULO         VARCHAR2(100),
    NOME_VENDEDOR              VARCHAR2(100),
    NOME_COMPRADOR             VARCHAR2(150),
    CIDADE_VENDA               VARCHAR2(100),
    ESTADO_VENDA               VARCHAR2(50),
    MACROREGIAO_VENDA          VARCHAR2(50),
    CONSTRAINT PK_BRZ_HIST_VENDAS_VEIC
        PRIMARY KEY (ID_VENDA_VEICULO)
);

-- Índices
CREATE INDEX IX_BRZ_VV_FILIAL_DATA
    ON BRZ_HIST_VENDAS_VEICULOS (COD_CONCESSIONARIA, COD_FILIAL, DT_VENDA);

CREATE INDEX IX_BRZ_VV_MARCA_MODELO
    ON BRZ_HIST_VENDAS_VEICULOS (MARCA_VEICULO, MODELO_VEICULO);

CREATE INDEX IX_BRZ_VV_CHASSI
    ON BRZ_HIST_VENDAS_VEICULOS (CHASSI_VEICULO);

CREATE INDEX IX_BRZ_VV_VENDEDOR
    ON BRZ_HIST_VENDAS_VEICULOS (NOME_VENDEDOR);
```

---

## ETL em Python

- Organização do projeto:
  - `controllers/`: ETL por domínio (estoque, vendas, serviços).
  - `mains/`: scripts de execução para cargas individuais.
  - `utils/`: `csv_handler` para padronizar leitura de CSV e `logger_controller` para logging centralizado.
- Principais tratamentos:
  - Correção de acentuação, tipos incorretos (ex.: código de filial como data).
  - Preenchimento/ajuste de códigos ausentes de concessionária/filial.
  - Remoção de duplicatas e colunas vazias antes da carga em Oracle.

<!-- TODO: inserir print de código Python do ETL -->
<!-- ![Código ETL](caminho/para/etl.png) -->

---

## Agente de IA (LLM)

- Implementação de Data Analyst Agent:
  - Desenvolvido em Python com LangChain.
  - Conectado ao Oracle via oracle_connector dedicado.
- Funcionalidades:
  - Recebe perguntas em linguagem natural sobre vendas, serviços e estoque.
  - Traduz para consultas SQL adequadas, executa no banco e retorna respostas explicadas.
  - Uso de API OpenAI com configuração via arquivo de ambiente seguro.

![Funcionamento do Agente](images/OpenAI_Agent/01.png)
![Funcionamento do Agente](images/OpenAI_Agent/02.png)
![Funcionamento do Agente](images/OpenAI_Agent/03.png)
![Funcionamento do Agente](images/OpenAI_Agent/04.png)
![Funcionamento do Agente](images/OpenAI_Agent/05.png)
![Funcionamento do Agente](images/OpenAI_Agent/06.png)
![Funcionamento do Agente](images/OpenAI_Agent/07.png)
![Funcionamento do Agente](images/OpenAI_Agent/08.png)


## Aplicação Streamlit
- App em light theme, com navegação por áreas de negócio:
  - Home e KPIs gerais.
  - Rentabilidade Integrada.
  - Pós-vendas.
  - Performance por filial.
  - Clientes.
  - Dashboards Operacional, Analítico e Preditivo.
  - Arquitetura interna:
    - `repositories/`: consultas ao Oracle.
    - `views/`: construção dos visuais.
    - `app.py`: orquestração de páginas e navegação.


### Execução Streamlit:
```markdown
```bash
streamlit run streamlit_app/app.py
```

![Streamlit](images/Streamlit/01.png)
![Streamlit](images/Streamlit/02.png)
![Streamlit](images/Streamlit/03.png)
![Streamlit](images/Streamlit/04.png)
![Streamlit](images/Streamlit/05.png)
![Streamlit](images/Streamlit/06.png)
![Streamlit](images/Streamlit/07.png)
![Streamlit](images/Streamlit/08.png)
![Streamlit](images/Streamlit/09.png)
![Streamlit](images/Streamlit/10.png)
![Streamlit](images/Streamlit/11.png)
![Streamlit](images/Streamlit/12.png)
![Streamlit](images/Streamlit/13.png)
![Streamlit](images/Streamlit/14.png)
![Streamlit](images/Streamlit/15.png)
![Streamlit](images/Streamlit/16.png)
![Streamlit](images/Streamlit/17.png)
![Streamlit](images/Streamlit/18.png)
![Streamlit](images/Streamlit/19.png)
![Streamlit](images/Streamlit/20.png)
![Streamlit](images/Streamlit/21.png)
![Streamlit](images/Streamlit/22.png)
![Streamlit](images/Streamlit/23.png)
![Streamlit](images/Streamlit/24.png)
![Streamlit](images/Streamlit/25.png)
![Streamlit](images/Streamlit/26.png)



## Estrutura do repositório

```text
etl_autos_code/
│
├── 📁 agents/
│   ├── data_analyst_agent.py											# Definição do agente de IA, utilizando Langchain e API OpenAI
│   └── sql_oracle_tool.py												# Conector ao Banco de Dados, através da oracle_connector, para o acesso do Agente
│
├── 📁 bases/																# Pasta com as bases, para consumo das automações ETL
│   ├── estoque-atual-de-pecas.csv										# Current Parts Inventory (estoque-atual-de-pecas.csv)
│   ├── estoque-atual-de-veículos.csv									# Current Vehicle Inventory (estoque-atual-de-veiculos.csv)
│   ├── historico-de-servicos-realizados.csv							# Service History (historico-de-servicos-realizados.csv)
│   ├── historico-de-vendas-de-pecas.csv								# Sales History of Parts (historico-de-vendas-de-peças.csv)
│   └── historico-de-vendas-de-veiculos.csv							# Sales History of Vehicles (historico-de-vendas-de-veiculos.csv)
│
├── 📁 config/
│   ├── database.ini													# IP, banco, usuário, senha, schema							
│   ├── load_oai_env.py												# Código para leitura do arquivo de ambiente, com API-key da OpenAI
│   └── oai.env														# Arquivo de ambiente, com API-key da OpenAI
│
├── 📁 connector/
│   ├── __init__.py.py   	   											# Vazia														
│   └── oracle_connector.py  											# Classe OracleConnector (conexão única)						
│
├── 📁 models/
│   └── models.py             											# Estruturas de tabelas das bases, como Dicionário de Dados para o Banco
│
├── 📁 controllers/
│   ├── estoque_pecas_controller.py									# ETL das bases Current Parts Inventory (estoque-atual-de-pecas.csv)
│   ├── estoque_veiculos_controller.py									# ETL das bases Current Vehicle Inventory (estoque-atual-de-veiculos.csv)
│   ├── hist_servicos_controller.py									# ETL das bases Service History (historico-de-servicos-realizados.csv)
│   ├── hist_vendas_pecas_controller.py								# ETL das bases Sales History of Parts (historico-de-vendas-de-peças.csv)
│   └── hist_vendas_veiculos_controller.py								# ETL das bases Sales History of Vehicles (historico-de-vendas-de-veiculos.csv)
│
├── 📁 views/
│   ├── estoque_pecas_view.py											# View das bases Current Parts Inventory (estoque-atual-de-pecas.csv)
│   ├── estoque_veiculos_view.py										# View das bases Current Vehicle Inventory (estoque-atual-de-veiculos.csv)
│   ├── hist_servicos_view.py											# View das bases Service History (historico-de-servicos-realizados.csv)
│   ├── hist_vendas_pecas_view.py										# View das bases Sales History of Parts (historico-de-vendas-de-peças.csv)
│   └── hist_vendas_veiculos_view.py									# View das bases Sales History of Vehicles (historico-de-vendas-de-veiculos.csv)
│
├── 📁 mains/
│   ├── main_estoque_pecas.py											# Main para executar carga das bases Current Parts Inventory (estoque-atual-de-pecas.csv)
│   ├── main_estoque_veiculos.py										# Main para executar carga das bases Current Vehicle Inventory (estoque-atual-de-veiculos.csv)
│   ├── main_hist_servicos.py											# Main para executar carga das bases Service History (historico-de-servicos-realizados.csv)
│   ├── main_hist_vendas_pecas.py										# Main para executar carga das bases Sales History of Parts (historico-de-vendas-de-peças.csv)
│   ├── main_hist_vendas_veiculos.py									# Main para executar carga das bases Sales History of Vehicles (historico-de-vendas-de-veiculos.csv)
│   └── main_llm_agent.py												# Main para executar o agente LLM
│
├── 📁 logs/
│   ├── csv_handler.txt												# Log de csv_handler
│   ├── EstoquePecasController.txt										# Log de EstoquePecas
│   ├── EstoqueVeiculosController.txt									# Log de EstoqueVeiculos
│   ├── HistServicosController.txt										# Log de HistServicos
│   ├── HistVendasPecas.txt											# Log de HistVendasPecas
│   ├── HistVendasVeiculos.txt											# Log de HistVendasVeiculos
│   └── OracleConnector.py	 	            							# Log de OracleConnector
│
├── 📁 sql/
│   ├── BRONZE - CREATE TABLE BRZ_ESTOQUE_PECAS.sql					# Query para criação da tabela BRZ_ESTOQUE_PECAS
│   ├── BRONZE - CREATE TABLE BRZ_ESTOQUE_VEICULOS.sql					# Query para criação da tabela BRZ_ESTOQUE_VEICULOS
│   ├── BRONZE - CREATE TABLE BRZ_HIST_SERVICOS.sql					# Query para criação da tabela BRZ_HIST_SERVICOS
│   ├── BRONZE - CREATE TABLE BRZ_HIST_VENDAS_PECAS.sql				# Query para criação da tabela BRZ_HIST_VENDAS_PECAS
│   └── BRONZE - CREATE TABLE BRZ_HIST_VENDAS_VEICULOS.sql				# Query para criação da tabela BRZ_HIST_VENDAS_VEICULOS
│
├── 📁 streamlit_app/
│   ├── app.py															# Raiz do Projeto, funciona como Main
│
│   ├── 📁 auth/
│			├── __init__.py.py   	   									# Vazia		
│		   	└── auth_services.py										# Implementar, futuramente, Autenticação por Login e Senha
│
│   ├── 📁 config/
│		   	└── config.ini												# Implementar, futuramente, Autenticação por Login e Senha
│
│   ├── 📁 repositories/
│   		├── __init__.py.py   	   # Vazia		
│   		├── base_repo.py											# Repositório para as consultas Base para todas as demais
│   		├── kpi_repository.py										# Repositório para as consultas dos KPIs da página inicial
│   		├── rentabilidade_integrada_repository.py					# Repositório para as consultas da página Rentabilidade Integrada
│   		├── pos_vendas_repository.py								# Repositório para as consultas da página Pós-Vendas
│   		├── performance_filial_repository.py						# Repositório para as consultas da página Performance Filial
│   		├── clientes_repository.py									# Repositório para as consultas da página Clientes
│   		├── dashboard_operacional_repository.py					# Repositório para as consultas da página DASHBOARD - Operacional
│   		├── dashboard_analitico_repository.py						# Repositório para as consultas da página DASHBOARD - Analítico
│		   	└── dashboard_preditivo_repository.py						# Repositório para as consultas da página DASHBOARD - Preditivo
│
│   ├── 📁 views/
│   		├── home_view.py											# Criação dos visuais da Página Inicial (Home)
│   		├── rentabilidade_integrada_view.py						# Criação dos visuais da página Rentabilidade Integrada
│   		├── pos_vendas_view.py										# Criação dos visuais da página Pós-Vendas
│   		├── performance_filial_view.py								# Criação dos visuais da página Performance Filial
│   		├── clientes_view.py										# Criação dos visuais da página Clientes
│   		├── dashboard_operacional_view.py							# Criação dos visuais da página DASHBOARD - Operacional
│   		├── dashboard_analitico_view.py							# Criação dos visuais da página DASHBOARD - Analítico
│		   	└── dashboard_preditivo_view.py							# Criação dos visuais da página DASHBOARD - Preditivo
│
├── 📁 utils/
│   └── __init__.py.py   	   											# Vazia														
│   ├── csv_handler.py        											# Tratamento de Arquivos .CSV. Detecta "," e ";" automaticamente							
│   └── logger_controller.py             								# Logging centralizado							
│
├── requirements.txt
└── README.md
```


## Fluxo ponta a ponta

- 1: Arquivos CSV são carregados e validados pelo ETL em Python.
- 2: Dados tratados são gravados em tabelas Bronze no Oracle.
- 3: Agente de IA consulta o Oracle para responder perguntas do negócio.
- 4: Streamlit consome o mesmo banco, exibindo KPIs e dashboards interativos.


## Próximos passos
- MVP valida a viabilidade de uma solução completa:
  - Governança mínima de dados.
  - Camada analítica acessível via dashboards e via IA conversacional.

- Próximos passos sugeridos:
  - Evoluir para camadas Silver/Gold com métricas consolidadas e dimensões bem definidas.
  - Adicionar modelos preditivos (demanda, churn, rentabilidade futura).
  - Ampliar o uso do LLM para geração automática de relatórios executivos.


## Encerramento
- O case demonstra:
  - Capacidade técnica em dados, IA e engenharia.
  - Foco em valor de negócio, não apenas em código.
  - Visão de arquitetura escalável e orientada a time.

- Obrigado!
Contato:
  - E-mail: lg_bizzi@hotmail.com
  - LinkedIn: linkedin.com/in/luis-guilherme-ferreira-bizzi