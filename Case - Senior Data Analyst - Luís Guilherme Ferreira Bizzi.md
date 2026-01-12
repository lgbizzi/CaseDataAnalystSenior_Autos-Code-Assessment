# PLANO DE AÇÃO - AUTOS CODE ASSESSMENT
## Sistema de IA para Insights Acionáveis em Operações de Concessionária Automóvel

**Data de Criação:** Janeiro 2026  
**Status:** Planejamento Estratégico  
**Objetivo Principal:** Desenvolver um sistema integrado de IA que fornece insights acionáveis para operações de concessionária automóvel, unificando dados de veículos, peças e serviços

---

## 📊 RESUMO EXECUTIVO DOS DADOS

### Bases de Dados Disponíveis (5 Bases Integradas)

| Base | Registros | Colunas | Status | Observações |
|------|-----------|---------|--------|------------|
| Estoque de Veículos | 255 | 16 | ⚠️ Com Problemas | 10 valores nulos, 3 duplicatas, colunas repetidas |
| Estoque de Peças | 5.332 | 15 | ✅ Limpo | Sem valores nulos, sem duplicatas |
| Histórico de Serviços Realizados | 35.803 | 22 | ✅ Limpo | Sem valores nulos, sem duplicatas |
| Histórico de Vendas de Veículos | 41.666 | 28 | ⚠️ Com Problemas | 41.772 valores nulos, 1.417 duplicatas |
| Histórico de Vendas de Peças | ~250k+ | 19 | ⚠️ Com Problemas | Acentuações nos Nomes |
| **TOTAL** | **~333k+** | **100** | - | Dados integrados de ciclo completo |

### Métricas Financeiras Consolidadas (4 Bases Anteriores)

- **Estoque Veículos:** 255 unidades | R$ 27.552.796,65
- **Estoque Peças:** ~5.332 registros | Valor variável
- **Receita Serviços:** R$ 8.301.606,42 | Lucro: R$ 9.484.135,25 (⚠️ Anômalia: 114% margem)
- **Receita Vendas Veículos:** R$ 4.466.426.322,23 | Lucro: R$ 50.734.895,13 (1,14% margem)

### Dimensão: Vendas de Peças (Histórico 2023)
- **Período:** 2023 (com picos em maio/2023 e períodos variáveis)
- **Tipos de Venda:** Oficina, Peças Atacado, Peças Varejo, Funilaria, Acessórios
- **Categorias:** Peças Originais, Peças Não-Originais, Acessórios, Lubrificantes
- **Estrutura:** CodConcessionaria, CodFilial, DataVenda, QuantidadeVendida, ValorVenda, CustoPeca, LucroVenda, MargemVenda, DescricaoPeca, CategoriaPeca, DepartamentoVenda, TipoVenda, NomeVendedor, NomeComprador, Localização (Cidade, Estado, Macrorregião)

---

## 🎯 PROBLEMAS IDENTIFICADOS (5 BASES)

### CAMADA 1: Qualidade de Dados

#### 1.1 Estoque de Veículos
- **Valores nulos:** 10 registros em colunas críticas
- **Duplicatas:** 3 registros duplicados
- **Estrutura:** Colunas repetidas (Data_de_Entrada aparece 3 vezes)
- **Ação:** Limpeza, remoção de duplicatas, deduplicate colunas

#### 1.2 Histórico de Vendas de Veículos
- **Valores nulos:** 41.772 nulos (coluna "Unnamed: 27" - vazia)
- **Duplicatas:** 1.417 registros duplicados
- **Margem anômala:** 1,14% muito baixa (investigar cálculos)
- **Ação:** Remover coluna vazia, deduplicar, validar fórmulas

#### 1.3 Histórico de Serviços
- **Lucro > Receita:** 114% de margem CRÍTICO
- **Possível causa:** Lucro acumulado ou estrutura diferente
- **Ação:** Investigação urgente da semântica dos dados

#### 1.4 Estoque de Peças
- **Status:** Limpo (sem problemas aparentes)
- **Validação necessária:** Datas, campos de obsolescência
- **Ação:** Confirmar campos críticos, validar ranges

#### 1.5 Histórico de Vendas de Peças
- **Margens anômalas:** Peças com lucro negativo ou margem >100%
- **Zeros:** Custo da peça zerado em registros (verificar se correto)
- **Negativas:** Transações negativas (devoluções/cancelamentos não claramente marcadas)
- **Incoerências:** Mesmo item com custos diferentes por filial/período
- **Vendedor/Comprador:** Alguns registros com mesmo nome (venda interna?)
- **Ação:** Padronizar margens por canal, investigar negativas, validar custo

---

### CAMADA 2: Padrões de Negócio Não Explicados

#### 2.1 Pós-Venda Desconectado
- **Problema:** Vendas de peças não ligadas claramente a serviços realizados
- **Impacto:** Impossível medir rentabilidade integrada (veículo + serviço + peça)
- **Ação:** Criar chave de ligação: cliente + data/período para análise integrada

#### 2.2 Rentabilidade por Canal
- **Problema:** Margens diferentes entre Oficina, Atacado, Varejo, Funilaria não justificadas
- **Impacto:** Impossível otimizar mix e pricing por canal
- **Ação:** Analisar distribuição de margem por canal, definir faixas aceitáveis

#### 2.3 Obsolescência de Estoque
- **Problema:** Sem informação clara de tempo em estoque vs. saída
- **Impacto:** Peças paradas/mortas imobilizam capital
- **Ação:** Cruzar estoque atual com histórico de vendas, calcular giro por peça

#### 2.4 Sazonalidade e Demanda
- **Problema:** Picos de venda em maio/2023 (vendas de peças) não explicados
- **Impacto:** Impossível planejar compras e estoque
- **Ação:** Investigar eventos, campanhas, sazonalidade de serviços

---

### CAMADA 3: Oportunidades de Otimização

#### 3.1 Produtividade de Vendedores
- **Problema:** Vendedor mesmo em múltiplos registros (repetição de venda?)
- **Impacto:** Impossível medir performance real
- **Ação:** Validar se vendedor = responsável pela venda ou por etapa

#### 3.2 Foco de Estoque
- **Problema:** Sem análise ABC de peças
- **Impacto:** Capital distribuído em itens de baixo giro
- **Ação:** Classificar peças por volume×valor, propor realocação

#### 3.3 Margem Integrada (Veículo + Serviço + Peça)
- **Problema:** Margens analisadas isoladamente
- **Impacto:** Decisões de pricing não otimizadas
- **Ação:** Criar modelo de margem integrada por cliente/marca/filial

---

## 📈 PLANO DE AÇÃO INTEGRADO (5 BASES)

### FASE 1: ORGANIZAR E PADRONIZAR DADOS (Semanas 1-2)

#### 1.1 Mapear e Validar Chaves Primárias
```
□ CodConcessionaria + CodFilial = identificador único de filial
□ Histórico de Vendas: Cada transação tem data + vendedor + cliente
□ Estoque: Cada SKU (peça/veículo) tem código único
□ Serviços: Cada OS tem número único + data + mecânico
□ Validar referencias cruzadas entre bases
```

#### 1.2 Padronizar Categorias e Tipos
```
PEÇAS:
□ CategoriaPeca: Originais, Não-Originais, Acessórios, Lubrificantes (VALIDAR)
□ DepartamentoVenda: Oficina, Peças Atacado, Peças Varejo, Funilaria (MAPEAR)
□ TipoVenda: Normal, Promoção, Desconto (INFERIR de margem)

VEÍCULOS:
□ Marca x Modelo x Versão (consistência entre bases)
□ Tipo de Venda: Novo, Semi-novo, Trade-in, Leilão
□ Condição Estoque: Ativo, Vendido, Parado

SERVIÇOS:
□ Tipo de Serviço: Manutenção, Reparo, Revisão, Diagnóstico
□ Departamento: Oficina, Funilaria, Elétrica, Lataria
□ Status: Agendado, Em Execução, Concluído, Cancelado
```

#### 1.3 Tratamento de Nulos e Duplicatas
```
□ Estoque Veículos: Remover 10 registros nulos ou imputar valores
□ Vendas Veículos: Remover coluna "Unnamed: 27" vazia
□ Vendas Veículos: Investigar e remover/validar 1.417 duplicatas
□ Peças: Verificar se custo zerado = erro ou promoção
□ Serviços: Confirmar se lucro > receita é acumulação ou erro
```

#### 1.4 Criar Campos Derivados Essenciais
```
TEMPORAL:
□ Data: Ano, Mês, Trimestre, Dia da Semana, Semana do Ano
□ Estoque Veículos: Dias em Estoque = hoje - Data de Entrada
□ Estoque Peças: Dias em Estoque = hoje - Data de Entrada (inferir)
□ Serviços: Período entre agendamento e conclusão

FINANCEIRO:
□ Margem % = (Receita - Custo) / Receita × 100
□ Markup = Preço / Custo
□ ROI por Filial = Lucro / Capital Investido
□ Custo de Estoque = Valor × Taxa de Manutenção Anual

OPERACIONAL:
□ Giro de Estoque = Saídas no Período / Estoque Médio
□ Ticket Médio = Receita Total / Número de Transações
□ Produtividade Vendedor = Vendas / Dias Trabalhados
□ Taxa de Retenção = Clientes que repetem / Total de Clientes
```

#### 1.5 Validar Ranges e Outliers
```
□ Preço de Venda: Deve estar acima do custo (exceto promoções)
□ Margem: Range esperado por categoria/canal (definir limites)
□ Estoque Dias: Alertar se > 180 dias (obsolescência)
□ Volume Vendas: Identificar transações anormalmente grandes (possíveis erros)
□ Custo Peça: Mesmo código deve ter custo similar (validar duplicados)
```

---

### FASE 2: MODELO DE DADOS UNIFICADO (Semanas 2-3)

#### 2.1 Dimensões Comuns (Star Schema)
```
Dim_Concessionaria
  ├─ CodConcessionaria (PK)
  ├─ NomeConcessionaria
  ├─ Filiais (1:N)
  └─ Macrorregião

Dim_Filial
  ├─ CodFilial (PK)
  ├─ CodConcessionaria (FK)
  ├─ NomeFilial
  ├─ Cidade
  ├─ Estado
  └─ Macrorregião

Dim_Tempo
  ├─ Data (PK)
  ├─ Ano, Mês, Trimestre
  ├─ Dia da Semana
  ├─ Semana do Ano
  └─ EhFeriadoOuPromocao

Dim_Marca_Modelo (para Veículos)
  ├─ CodMarca_Modelo (PK)
  ├─ Marca
  ├─ Modelo
  ├─ Versão
  ├─ Categoria (Sedan, SUV, etc)
  └─ Segmento (Luxo, Popular, etc)

Dim_Peca
  ├─ CodPeca (PK)
  ├─ DescricaoPeca
  ├─ CategoriaPeca (Original, Não-Original, Acessório, Lubrificante)
  ├─ Departamento Padrão
  ├─ UnidadeMedida
  ├─ FamiliaComercial (Freios, Filtros, Óleo, etc)
  └─ CustoMedio

Dim_Pessoa (Vendedor/Mecânico/Cliente)
  ├─ CodPessoa (PK)
  ├─ Nome
  ├─ Tipo (Vendedor, Mecânico, Cliente)
  ├─ Filial
  ├─ DataAdmissao
  └─ Ativo (S/N)

Dim_Departamento
  ├─ CodDepartamento (PK)
  ├─ NomeDepartamento (Oficina, Peças Atacado, Peças Varejo, Funilaria)
  └─ TipoOperacao (Venda Peça, Prestação Serviço)
```

#### 2.2 Fatos Principais
```
Fato_Vendas_Veiculos
  ├─ ID (PK)
  ├─ CodConcessionaria (FK)
  ├─ CodFilial (FK)
  ├─ CodMarca_Modelo (FK)
  ├─ DataVenda (FK)
  ├─ CodVendedor (FK)
  ├─ CodComprador (FK)
  ├─ ValorVenda
  ├─ CustoVeiculo
  ├─ LucroVenda
  ├─ MargemVenda %
  ├─ TipoVenda (Novo, Semi-novo, Trade-in)
  ├─ DiaEmEstoque
  └─ Flags: duplicata, ajuste, erro

Fato_Vendas_Pecas
  ├─ ID (PK)
  ├─ CodConcessionaria (FK)
  ├─ CodFilial (FK)
  ├─ CodPeca (FK)
  ├─ DataVenda (FK)
  ├─ CodVendedor (FK)
  ├─ CodComprador (FK)
  ├─ CodDepartamento (FK)
  ├─ QuantidadeVendida
  ├─ ValorUnitario
  ├─ ValorTotal
  ├─ CustoTotal
  ├─ LucroVenda
  ├─ MargemVenda %
  ├─ TipoVenda (Normal, Promoção, Desconto)
  └─ Flags: venda interna, devolução, ajuste

Fato_Servicos_Realizados
  ├─ NumeroOS (PK)
  ├─ CodConcessionaria (FK)
  ├─ CodFilial (FK)
  ├─ DataAgendamento (FK)
  ├─ DataConclusao (FK)
  ├─ CodMecanico (FK)
  ├─ CodCliente (FK)
  ├─ CodDepartamento (FK)
  ├─ TipoServico (Manutenção, Reparo, Revisão)
  ├─ HorasGastas
  ├─ ReceitaServico
  ├─ CustoServico
  ├─ LucroServico
  ├─ MargemServico %
  ├─ PecasUtilizadas (array de CodPeca)
  ├─ Status (Agendado, Em Execução, Concluído, Cancelado)
  └─ Flags: retrabalho, atraso, anomalia

Fato_Estoque_Veiculos (SNAPSHOT)
  ├─ ID (PK)
  ├─ DataSnapshot (FK)
  ├─ CodConcessionaria (FK)
  ├─ CodFilial (FK)
  ├─ CodMarca_Modelo (FK)
  ├─ QuantidadeEstoque
  ├─ ValorEstoque
  ├─ CustoMedioUnitario
  ├─ DiasEstoque
  ├─ RotatividadeAnual
  ├─ Status (Ativo, Parado, Obsoleto)
  └─ Recomendacao (Manter, Promover, Liquidar)

Fato_Estoque_Pecas (SNAPSHOT)
  ├─ ID (PK)
  ├─ DataSnapshot (FK)
  ├─ CodConcessionaria (FK)
  ├─ CodFilial (FK)
  ├─ CodPeca (FK)
  ├─ QuantidadeEstoque
  ├─ ValorEstoque
  ├─ CustoMedioUnitario
  ├─ DiasEstoque
  ├─ RotatividadeAnual
  ├─ ReorderPoint
  ├─ EOQ (Economic Order Quantity)
  ├─ Status (Ativo, Lento, Parado, Obsoleto)
  └─ Recomendacao (Manter, Aumentar, Reduzir, Liquidar)
```

#### 2.3 Integrações e Chaves de Ligação
```
LIGAÇÃO PÓS-VENDA (Veículo → Serviço → Peça):
□ Cliente + Data: Identificar se cliente que comprou veículo depois faz serviço
□ Veículo + Serviço: Se número VIN disponível, ligar serviço ao veículo
□ Serviço + Peças: Peças usadas no serviço (descrito em Fato_Servicos)
□ Análise: Margem Integrada = Margem Venda Veiculo + Margem Serviços + Margem Peças

LIGAÇÃO ESTOQUE × VENDAS:
□ Peça vendida hoje deve estar em estoque naquele dia/período
□ Validar: Quantidade saída <= Quantidade em estoque (não vender do nada)
□ Rastreabilidade: Peça X saiu do estoque na data Y com custo Z

LIGAÇÃO FILIAL × DEPARTAMENTO:
□ Mesmo departamento em diferentes filiais deve ter políticas similares
□ Mas margens podem variar por região
□ Flag para análise: Outliers de margem por departamento/filial
```

---

### FASE 3: REVISÃO DE PROBLEMAS COM AS 5 BASES (Semanas 3-4)

#### 3.1 Margens Anômalas
```
INVESTIGAÇÃO:
□ Peças com lucro NEGATIVO:
  - São devoluções/cancelamentos? (devem estar marcadas como tipo diferente)
  - São erros de custo cadastrado? (comparar com histórico)
  - São promoções com desconto > custo? (deve estar justificado)
  
□ Peças com margem >100%:
  - São acessórios com alto markup? (validar se padrão)
  - Erro de custo zerado? (re-verificar)
  - Transação interna ou teste? (investigar vendedor/comprador)

□ Serviços com lucro > receita (114% anômalo):
  - Lucro é acumulado ou por serviço?
  - Há desconto de custo duplicado?
  - Erro na fórmula de cálculo?

PADRONIZAÇÃO:
□ Definir margem mínima por canal:
  - Oficina: 40-50%
  - Peças Atacado: 20-30%
  - Peças Varejo: 35-45%
  - Funilaria: 35-45%
  - Acessórios: 40-60%
□ Criar alertas para desvios > 10% do padrão
```

#### 3.2 Coerência Estoque × Vendas
```
ANÁLISE:
□ Peças com ALTO VOLUME de vendas em 2023 + BAIXO estoque atual:
  - Risco de ruptura
  - Precisa aumentar reorder point
  
□ Peças com BAIXO VOLUME de vendas + ALTO valor em estoque:
  - Capital parado
  - Candidata a liquidação/devolução
  
□ Veículos com TEMPO > 180 DIAS em estoque:
  - Custo financeiro elevado
  - Possível desconto necessário
  - Pode sinalizar marca/modelo com demanda fraca

VALIDAÇÃO:
□ Nenhuma venda de peça deve ser feita sem que ela exista em estoque
□ Estoque zerado de peça que vendia 10 unidades/mês = problema
□ Saldo de estoque deve bater: Estoque Inicial + Compras - Vendas = Estoque Final
```

#### 3.3 Análise ABC de Peças
```
CLASSIFICAÇÃO:
□ A (80% da receita):
  - Peças de alta saída × alto valor
  - Prioridade: Nunca faltar em estoque
  - Reorder point: 2-3 meses de estoque
  
□ B (15% da receita):
  - Peças de saída média × valor médio
  - Prioridade: Gerenciar com atenção
  - Reorder point: 1,5 meses de estoque
  
□ C (5% da receita):
  - Peças de baixa saída ou baixo valor
  - Prioridade: Minimizar estoque / Liquidar
  - Recomendação: Considerar devolução ao fornecedor

IMPACTO:
□ % de estoque gasto em A, B e C
□ % de capital parado em C
□ Oportunidade de liberação de caixa
```

#### 3.4 Sazonalidade e Demanda
```
PADRÕES OBSERVADOS:
□ Pico de vendas de peças em mai/2023 (investigar evento)
□ Variação por período do ano (fim de ano, férias, inverno/verão)
□ Correlação entre vendas de veículos e demanda de peças/serviços
□ Diferença sazonal por tipo de serviço (manutenção vs reparo)

AÇÕES:
□ Criar calendário sazonal
□ Ajustar níveis de estoque conforme sazonalidade
□ Planejar compras 2-3 meses à frente
□ Identificar oportunidades de promoção em períodos de baixa
```

---

### FASE 4: ANÁLISES PRIORITÁRIAS (Semanas 4-6)

#### 4.1 Rentabilidade Integrada
```
OBJETIVO: Medir lucro de forma holística (carro + serviço + peça)

ANÁLISE 1: Margem por Veículo
□ Cliente compra Veículo X em data Y com margem Z
□ Mesmo cliente faz serviço em data Y+30 com margem W
□ Mesmo cliente compra peças em data Y+30 com margem V
□ Margem Integrada = (Z + W + V) / (Preço Veiculo + Valor Servicos + Valor Pecas)
□ Resultado: Alguns veículos que vendem com margem baixa compensam em pós-venda

ANÁLISE 2: Ranking de Modelos por Rentabilidade Integrada
□ Qual modelo tem melhor ROI considerando ciclo completo?
□ Modelo A: Margem baixa mas alto serviço/peça vs Modelo B: Margem alta mas baixo pós-venda
□ Decisão: Qual modelo priorizar?

ANÁLISE 3: Fluxo de Caixa
□ Veículo: Capital parado durante dias em estoque
□ Serviço: Receita rápida mas custo imediato
□ Peça: Recebimento rápido vs pagamento a fornecedor (prazo)
□ Otimizar: Acelerar venda de veículos + maximizar serviço + otimizar giro de peças
```

#### 4.2 Pós-Venda (Serviços × Peças)
```
TICKET MÉDIO:
□ Valor médio de serviço por OS
□ Quantidade média de peças por OS
□ Valor médio de peça por OS
□ Margem média por OS

DEPARTAMENTO:
□ Oficina: Qual margem média?
□ Funilaria: Qual margem média?
□ Por cada departamento: volume, receita, lucro, margem, dias de espera

TIPO DE SERVIÇO:
□ Manutenção: Receita x Peças Utilizadas
□ Reparo: Receita x Peças Utilizadas
□ Revisão: Receita x Peças Utilizadas
□ Qual tipo é mais lucrativo?

PEÇAS CORE:
□ Identificar peças que entram em > 50% dos serviços
□ Garantir estoque sempre disponível
□ Negociar desconto com fornecedor para essas peças
```

#### 4.3 Performance por Filial
```
MÉTRICAS POR FILIAL:
□ Vendas Veículos: Volume, Receita, Lucro, Dias Médio Estoque, Margem
□ Vendas Peças: Volume, Receita, Lucro, Margem, Giro
□ Serviços: Volume (OS), Receita, Lucro, Margem, Dias Espera
□ ROI: Lucro Total / Capital Investido em Estoque
□ Produtividade Vendedor: Vendas por Vendedor

BENCHMARKING:
□ Filial X tem melhor ROI que Filial Y: Por quê?
□ Replicar boas práticas
□ Investigar deficiências

OPORTUNIDADES:
□ Realocação de estoque entre filiais
□ Compartilhamento de mecânicos/conhecimento
□ Centralizacao de compras vs descentralização
```

#### 4.4 Segmentação de Clientes
```
ANÁLISE:
□ Quantos clientes únicos compraram veículos em 2023?
□ Desses, quantos fizeram serviço posterior?
□ Desses, quantos compraram peças?
□ Lifetime Value: Quanto cada cliente "rendeu" em ciclo completo?

MATRIZ RFM (Recency, Frequency, Monetary):
□ Clientes recentes que compram frequentemente = VIPs
□ Clientes que desapareceram = churn risk
□ Clientes high-value mas low-frequency = oportunidade de retenção

SEGMENTAÇÃO:
□ VIP: Compra frequente + alto valor + recente
□ Crescimento: Compra frequente + valor médio + recente
□ Risco: Compra frequente + alto valor + não recente
□ Dorminte: Sem atividade recente
```

---

### FASE 5: MODELO DE NEGÓCIO APRIMORADO (Semanas 6-8)

#### 5.1 Política de Preços e Margens
```
OBJETIVOS:
□ Definir margem mínima e máxima por canal/categoria
□ Garantir competitividade e consistência
□ Maximizar volume onde margem está baixa
□ Maximizar margem onde volume está alto (80/20)

POR CANAL - PEÇAS:
□ Oficina: 45-55% (peças usadas em serviço, cliente cativo)
□ Atacado: 15-25% (volume, margens menores)
□ Varejo: 35-45% (cliente walk-in, preço mais sensível)
□ Funilaria: 40-50% (peças + serviço integrado)

MARKUP MÍNIMO:
□ Peça Original: Markup 1.8x-2.5x custo
□ Peça Não-Original: Markup 1.5x-2.0x custo
□ Acessórios: Markup 2.0x-3.0x custo (maior elasticidade)
□ Lubrificantes: Markup 1.5x-2.0x custo (commodities)

REGRA DE NEGÓCIO:
□ Nunca vender abaixo de markup mínimo (exceto promoção aprovada)
□ Promoção máx 15% abaixo de preço de tabela
□ Descontos progressivos por volume

MONITORAMENTO:
□ Alert semanal: Vendas abaixo de margem mínima
□ Revisão mensal de mix de preços
□ Análise trimestral de elasticidade preço
```

#### 5.2 Plano de Compras e Reabastecimento
```
MATRIZ ABC PARA DEFINIR POLÍTICA:
□ Peças CLASSE A:
  - Reorder Point: 2 meses de estoque
  - EOQ: Compra mensal
  - Fornecedor: Sempre ativa segunda opção (risco de ruptura)
  
□ Peças CLASSE B:
  - Reorder Point: 1,5 meses de estoque
  - EOQ: Compra a cada 6 semanas
  - Fornecedor: Uma opção é suficiente
  
□ Peças CLASSE C:
  - Reorder Point: 1 mês de estoque
  - EOQ: Compra por demanda (just-in-time)
  - Fornecedor: Avaliar devolução vs estoque

DESOVA PROGRAMADA:
□ Peças com 0 saídas nos últimos 6 meses:
  - Gerar nota de crédito com fornecedor (se possível)
  - Promover em "Liquida Estoque"
  - Doação/descarte se não há saída
  
□ Impacto esperado: Liberar 15-25% do capital investido em estoque

SAZONALIDADE:
□ Aumentar estoque antes de períodos de pico
□ Reduzir antes de períodos de baixa
□ Negociar prazo estendido com fornecedor em períodos baixos
```

#### 5.3 Estratégia de Veículos
```
OBJETIVO: Reduzir dias em estoque + maximizar margem

ANÁLISE POR TIPO:
□ Novos: Dias em estoque médio + Margem
□ Semi-novos/Trade-in: Dias em estoque médio + Margem
□ Leilão: Dias em estoque médio + Margem
□ Qual tipo tem melhor ROI?

POLÍTICA DE DESCONTO:
□ Veículo com 60+ dias em estoque: Avaliação de desconto
□ Veículo com 120+ dias em estoque: Desconto obrigatório (custo financeiro alto)
□ Modelo com baixa demanda: Considerar reduzir compra

COMPRA INTELIGENTE:
□ Analisar qual marca/modelo tem menor dias em estoque + maior margem
□ Focar compras nesses modelos
□ Reduzir compra de modelos com ciclo longo

PROMOÇÃO:
□ Meses com baixa vendita: Lançar campanha direcionada
□ Veículos com 90+ dias: Campanha agressiva
□ Teste A/B: Desconto vs Financing vs Trade-in
```

#### 5.4 Estratégia de Serviços
```
OBJETIVO: Aumentar throughput + maximizar margem

CAPACIDADE:
□ Oficina: Quantas OS/dia?
□ Dias espera médio por departamento
□ Gargalho: Qual departamento está no limite?

PRICING:
□ Revisão regular de tabela de mão-de-obra
□ Benchmark com concorrência
□ Aumentar margem onde demanda > capacidade

RETENÇÃO:
□ Lembrete de manutenção preventiva
□ Planos de manutenção anual
□ Fidelização: Cliente que comprou veículo deve fazer serviço em sua concessionária

PEÇAS:
□ Garantir disponibilidade de peças core (filtros, óleo, freios)
□ Negociar desconto com fornecedor (compra conjunta de múltiplas filiais)
□ Buscar peça alternativa de boa qualidade para aumentar margem (não-original)

AGENDAMENTO:
□ Sistema de agendamento online
□ Reduzir dias de espera (custo indireto para cliente)
□ Rastrear tempo de espera por departamento e tipo de serviço
```

---

### FASE 6: DASHBOARDS E KPIs (Semanas 7-10)

#### 6.1 Dashboard Operacional (Diário)
```
VENDAS VEÍCULOS:
□ Vendas Hoje vs Ontem vs Média 30 dias
□ Receita Hoje vs Ontem vs Média 30 dias
□ Unidades em Estoque vs Meta
□ Dias Médio Estoque Atual vs Histórico

VENDAS PEÇAS:
□ Receita Hoje vs Ontem vs Média 30 dias
□ Volume Peças Vendidas Hoje vs Média
□ Margem % Hoje vs Média
□ Top 10 Peças Vendidas Hoje

SERVIÇOS:
□ OSs Concluídas Hoje vs Meta
□ Receita Serviços Hoje vs Média
□ Dias Espera Médio Atual
□ Gargalos de Capacidade

ALERTAS:
□ Peças em Falta (estoque zerado)
□ Veículos com 60+ dias em estoque
□ OS Atrasadas
□ Margem Abaixo do Limite
```

#### 6.2 Dashboard Analítico (Semanal/Mensal)
```
RENTABILIDADE:
□ Lucro Total vs Meta
□ Margem Veículos vs Peças vs Serviços
□ ROI por Filial
□ Lucro por Vendedor

ESTOQUE:
□ Valor Total Estoque Veículos vs Meta
□ Valor Total Estoque Peças vs Meta
□ Dias Médio Estoque Veículos vs Histórico
□ Rotatividade Peças por Categoria
□ Top 20 Peças em Valor Estocado

PERFORMANCE FILIAL:
□ Vendas Filial A vs Filial B vs Meta
□ Lucro Filial A vs Filial B
□ Produtividade Vendedor (vendas/pessoa)
□ Eficiência Serviço (OS/mês por mecânico)

SAZONALIDADE:
□ Vendas Última 12 Meses (série temporal)
□ Padrão Sazonal Identificado
□ Previsão Próximo Mês
□ Comparação vs Ano Anterior
```

#### 6.3 Dashboard Preditivo (Forecasting)
```
PREVISÃO DE VENDAS:
□ Forecast 30/60/90 dias de vendas veículos
□ Forecast 30/60/90 dias de receita peças
□ Forecast 30/60/90 dias de receita serviços
□ Intervalo de confiança (80%, 95%)

PREVISÃO DE ESTOQUE:
□ Peças que podem faltar nos próximos 30 dias
□ Peças que podem ficar obsoletas (estoque parado)
□ Recomendação: Aumentar/Manter/Reduzir estoque
□ Oportunidade de desova

ALERTAS INTELIGENTES:
□ Modelo de carro provavelmente vai vencer a meta em 20 dias (ajustar compra)
□ Peça X vai faltar em 10 dias se padrão de venda continuar
□ Vendedor Y está fora de pista vs pares (investigar)
□ Filial Z pode não atingir margem mínima este mês (ação corretiva)

RECOMENDAÇÕES:
□ Aumentar compra de Peça A (demanda crescente)
□ Liquidar Peça B (obsoleta)
□ Promover Modelo C (margem alta, baixa saída)
□ Aumentar estoque Modelo D (falta frequente)
```

---

### FASE 7: AUTOMAÇÃO E IA (Semanas 10-14)

#### 7.1 Pipeline de Dados
```
ARQUITETURA:
□ Extraction: Dados das 5 bases (CSV, BD, APIs) → Data Lake
□ Transformation: Limpeza, validação, cálculo de métricas → Warehouse
□ Loading: Dados prontos para BI e ML → Dashboards, APIs
□ Orquestração: Apache Airflow ou Prefect (DAGs diários/semanais)

FREQUÊNCIA:
□ Dados de Vendas: Atualizar a cada 1 hora (tempo real)
□ Dados de Serviços: Atualizar a cada 4 horas
□ Dados de Estoque: Atualizar 1x/dia (final do dia)
□ Cálculo de Métricas: Atualizar 1x/dia
□ Forecasting: Atualizar 1x/semana (modelo retraining)
```

#### 7.2 Modelos de ML
```
FORECASTING DE DEMANDA:
□ Modelo: Prophet ou ARIMA para séries sazonais
□ Dados: Série de vendas últimos 24 meses
□ Saída: Previsão 30/60/90 dias
□ Acurácia esperada: MAPE < 15%

DETECÇÃO DE ANOMALIAS:
□ Modelo: Isolation Forest ou Local Outlier Factor
□ Dados: Histórico de margens por categoria/canal/filial
□ Saída: Alert quando margem sai do esperado
□ Acurácia esperada: Precision > 90%

SEGMENTAÇÃO DE CLIENTES:
□ Modelo: K-means clustering
□ Dados: RFM (Recency, Frequency, Monetary)
□ Saída: Grupos VIP, Regular, Churn Risk
□ Validação: Silhueta score > 0.5

RECOMENDAÇÃO DE PREÇO:
□ Modelo: Regression (XGBoost ou Gradual Boosting)
□ Dados: Histórico preço × demanda × margem
□ Saída: Preço ótimo para novo item
□ Acurácia esperada: R² > 0.7
```

#### 7.3 Integração com LLM (GPT-4)
```
CASO 1: Geração de Relatórios Automáticos
□ Extrai métricas do data warehouse
□ Agrupa insights principais (top 5 padrões)
□ Envia para GPT-4 com template de prompt
□ GPT-4 gera narrativa em linguagem natural
□ Relatório enviado por email automaticamente

CASO 2: Alertas Inteligentes
□ Sistema detecta anomalia (ex: margem caiu 20%)
□ Extrai contexto: qual peça, qual filial, qual período
□ Envia para GPT-4 com prompt: "Analise por que a margem de [peça] caiu [X%] e recomende ação"
□ GPT-4 retorna recomendação estruturada
□ Alert enviado a gestor com recomendação

CASO 3: Chatbot Q&A
□ Usuário faz pergunta: "Qual foi o lucro de outubro por filial?"
□ Sistema extrai informação do BD
□ GPT-4 formata resposta em linguagem natural
□ Usuário recebe resposta clara e contextualizada

TEMPLATES DE PROMPTS:
□ Análise de Margem: "Descreva por que margem de [categoria] está em [X%] vs esperado [Y%]"
□ Recomendação de Estoque: "A peça [nome] está obsoleta com [dias] sem saída. Recomende ação."
□ Análise de Performance: "Filial [nome] teve margem [X%] vs [Y%] da concorrência interna. Qual é o problema?"
□ Previsão de Demanda: "Baseado em histórico, a demanda de [produto] para [período] será [valor]. Recomende estoque."
```

#### 7.4 Interface de Usuário
```
STREAMLIT APP:
□ Login + Permissões por Filial/Rol
□ Dashboard principal com KPIs principais
□ Drilldown: Clique em métrica para explorar detalhes
□ Filtros: Data, Filial, Categoria, Tipo de Venda, etc

CHATBOT:
□ "Qual foi a margem de peças em maio?"
□ "Top 10 clientes por value"
□ "Por que a receita de serviços caiu?"
□ Sistema extrai dados + LLM formata resposta

```

---

## 📊 MATRIZ DE PROBLEMAS × SOLUÇÕES

| Problema | Causa Raiz | Solução | Impacto Esperado |
|----------|-----------|--------|------------------|
| Margem 1,14% veículos (baixa) | Competição / Modelo de negócio | Aumentar volume pós-venda (serviços+peças) | Margem integrada +5-8% |
| Lucro 114% serviços (anômalo) | Erro de cálculo ou estrutura diferente | Investigar fórmula e validar dados | Confiabilidade nos KPIs |
| Duplicatas em vendas (1.417) | Erros de entry ou sincronização | Remover duplicatas / implementar validação | Dados 100% confiáveis |
| Nulos em estoque veículos (10) | Dados incompletos | Imputação ou remoção conforme contexto | Dataset limpo |
| Peças com margem negativa | Devolução/cancelamento não marcado ou erro | Separar movimentos por tipo / validar custo | Margens consistentes |
| Capital parado em peças obsoletas | Sem política de desova | Implementar análise ABC + liquidação periódica | Liberar 15-25% capital |
| Dias estoque veículos elevados | Modelo/marca com baixa demanda | Reduzir compra + promoção direcionada | Reduzir dias em 20-30% |
| Sazonalidade não planejada | Sem forecasting | Implementar modelo de previsão | Planejar 90 dias à frente |
| Pós-venda desconectado de vendas | Sem chave de ligação cliente/tempo | Criar model relacional integrado | Medir margem integrada |
| Margem por canal inconsistente | Sem política de pricing | Definir matriz margem × canal × categoria | Consistência 95%+ |

---

## ✅ CRONOGRAMA EXECUTIVO (14 Semanas)

```
SEMANA 1-2      FASE 1: PADRONIZAÇÃO DE DADOS
                □ Exploração das 5 bases
                □ Limpeza (nulos, duplicatas)
                □ Validação ranges e outliers
                □ Entregável: Dataset limpo + Relatório Qualidade

SEMANA 2-3      FASE 2: MODELO DE DADOS
                □ Design Star Schema
                □ Dimensões e Fatos
                □ Chaves de ligação
                □ Entregável: Modelo de Dados Documentado

SEMANA 3-4      FASE 3: ANÁLISE DE PROBLEMAS
                □ Investigação: Margens, Estoque, Sazonalidade
                □ Análise ABC de peças
                □ Pós-venda (serviço × peça)
                □ Entregável: Documento de Achados + Recomendações

SEMANA 4-6      FASE 4: ANÁLISES PRIORITÁRIAS
                □ Rentabilidade integrada
                □ Performance por filial
                □ Segmentação de clientes
                □ Entregável: 10-15 Insights Acionáveis

SEMANA 6-8      FASE 5: MODELO DE NEGÓCIO APRIMORADO
                □ Política de preços/margens
                □ Plano de compras (ABC)
                □ Estratégia veículos/peças/serviços
                □ Entregável: Documento de Política (30-40p)

SEMANA 7-10     FASE 6: DASHBOARDS
                □ Dashboard Operacional (diário)
                □ Dashboard Analítico (semanal)
                □ Dashboard Preditivo (forecasting)
                □ Entregável: 3 Dashboards Interativos + Documentação

SEMANA 10-14    FASE 7: AUTOMAÇÃO & IA
                □ Pipeline ETL
                □ Modelos ML (forecasting, anomalias, recomendação)
                □ Integração GPT-4 + LangChain
                □ Chatbot + API REST
                □ Entregável: Sistema Completo Automático

SEMANA 14       TESTES, VALIDAÇÃO & APROVAÇÃO
                □ QA de dados e modelos
                □ Testes de acurácia (forecasting, detecção)
                □ Feedback stakeholders
                □ Documentação final
```

---

## 🎯 MÉTRICAS DE SUCESSO

### Qualidade de Dados
- [x] 100% de dados limpos e validados
- [x] Sem duplicatas não explicadas
- [x] Concordância Estoque = Inicial + Compras - Vendas
- [x] Nenhuma transação com custo > preço (exceto promoções)

### Insights de Negócio
- [x] Mínimo 15 padrões significativos identificados
- [x] 5+ recomendações acionáveis por stakeholder
- [x] Rentabilidade integrada calculada
- [x] Margem mínima por canal/categoria definida e aceita

### Modelos Preditivos
- [x] Forecast vendas: MAPE < 15%
- [x] Detecção anomalias: Precision > 90%
- [x] Segmentação clientes: Silhueta > 0.5
- [x] Modelos validados em holdout test

### Automação e IA
- [x] 85%+ das análises rotineiras automatizadas
- [x] Relatório automático gerado em < 5 minutos
- [x] Taxa de precisão de alertas > 90%
- [x] Chatbot responde 80%+ de perguntas corretamente

### Adoção
- [x] Dashboards utilizados por 80%+ dos usuários
- [x] Feedback positivo de 90%+ de stakeholders
- [x] Decisões de negócio documentadas baseadas em insights
- [x] Melhoria de 10%+ em KPIs principais (ROI, margem, giro)

---

## 📞 PRÓXIMOS PASSOS IMEDIATOS

1. **Aprovação do Plano** - Revisar escopo, cronograma e recursos com stakeholders
2. **Setup de Ambiente** - Configurar infraestrutura (BD, Data Lake, BI, Python)
3. **Ingestão de Dados** - Carregar as 5 bases no ambiente analítico
4. **Kick-off Formal** - Reunião de alinhamento com equipes
5. **Início Fase 1** - Exploração e limpeza das primeiras bases

---

**Preparado por:** Luís Guilherme Ferreira Bizzi  
**Data:** Janeiro 2026  
**Status:** Pronto para Aprovação e Implementação  
**Escopo:** 5 Bases de Dados Integradas (Veículos + Peças + Serviços)