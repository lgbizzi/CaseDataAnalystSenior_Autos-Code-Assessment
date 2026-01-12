# models/models.py

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class BaseBronzeModel(BaseModel):
    """
    Base para modelos BRONZE:
    - Validações e tratamentos específicos serão adicionados depois (por dataset).
    - Aqui é apenas o contrato de campos alinhado ao Oracle.
    """
    model_config = ConfigDict(
        extra="ignore",          # ignora colunas extras do CSV (ex.: "Unnamed: 27")
        populate_by_name=True,   # permite alias em campos quando quisermos mapear CSV -> BRZ
        str_strip_whitespace=True
    )


# ============================================================
# BRZ_ESTOQUE_PECAS
# ============================================================

class BRZEstoquePecas(BaseBronzeModel):
    #id_estoque_peca: Optional[int] = Field(default=None, alias="ID_ESTOQUE_PECA")

    cod_concessionaria: str = Field(alias="COD_CONCESSIONARIA")
    cod_filial: str = Field(alias="COD_FILIAL")

    nome_concessionaria: Optional[str] = Field(default=None, alias="NOME_CONCESSIONARIA")
    nome_filial: Optional[str] = Field(default=None, alias="NOME_FILIAL")
    marca_filial: Optional[str] = Field(default=None, alias="MARCA_FILIAL")

    valor_peca_estoque: Optional[float] = Field(default=None, alias="VALOR_PECA_ESTOQUE")
    qtde_peca_estoque: Optional[float] = Field(default=None, alias="QTDE_PECA_ESTOQUE")

    descricao_peca: Optional[str] = Field(default=None, alias="DESCRICAO_PECA")
    categoria_peca: Optional[str] = Field(default=None, alias="CATEGORIA_PECA")

    dt_ultima_venda_peca: Optional[date] = Field(default=None, alias="DT_ULTIMA_VENDA_PECA")
    dt_ultima_entrada_peca: Optional[date] = Field(default=None, alias="DT_ULTIMA_ENTRADA_PECA")

    peca_obsoleta_flag: Optional[str] = Field(default=None, alias="PECA_OBSOLETA_FLAG")  # "SIM"/"NAO" ou "YES"/"NO"
    tempo_obsoleta_dias: Optional[int] = Field(default=None, alias="TEMPO_OBSOLETA_DIAS")

    marca_peca: Optional[str] = Field(default=None, alias="MARCA_PECA")
    codigo_peca_estoque: Optional[str] = Field(default=None, alias="CODIGO_PECA_ESTOQUE")


# ============================================================
# BRZ_ESTOQUE_VEICULOS
# ============================================================

class BRZEstoqueVeiculos(BaseBronzeModel):
    #id_estoque_veiculo: Optional[int] = Field(default=None, alias="ID_ESTOQUE_VEICULO")

    cod_concessionaria: str = Field(alias="COD_CONCESSIONARIA")
    cod_filial: str = Field(alias="COD_FILIAL")

    nome_concessionaria: Optional[str] = Field(default=None, alias="NOME_CONCESSIONARIA")
    nome_filial: Optional[str] = Field(default=None, alias="NOME_FILIAL")
    marca_filial: Optional[str] = Field(default=None, alias="MARCA_FILIAL")

    custo_veiculo: Optional[float] = Field(default=None, alias="CUSTO_VEICULO")

    marca_veiculo: Optional[str] = Field(default=None, alias="MARCA_VEICULO")
    modelo_veiculo: Optional[str] = Field(default=None, alias="MODELO_VEICULO")
    cor_veiculo: Optional[str] = Field(default=None, alias="COR_VEICULO")

    veiculo_novo_seminovo: Optional[str] = Field(default=None, alias="VEICULO_NOVO_SEMINOVO")
    tipo_combustivel: Optional[str] = Field(default=None, alias="TIPO_COMBUSTIVEL")

    ano_modelo: Optional[int] = Field(default=None, alias="ANO_MODELO")
    ano_fabricacao: Optional[int] = Field(default=None, alias="ANO_FABRICACAO")

    chassi_veiculo: Optional[str] = Field(default=None, alias="CHASSI_VEICULO")
    tempo_total_estoque_dias: Optional[int] = Field(default=None, alias="TEMPO_TOTAL_ESTOQUE_DIAS")
    km_atual: Optional[int] = Field(default=None, alias="KM_ATUAL")
    placa_veiculo: Optional[str] = Field(default=None, alias="PLACA_VEICULO")

    dt_entrada_estoque: Optional[date] = Field(default=None, alias="DT_ENTRADA_ESTOQUE")


# ============================================================
# BRZ_HIST_SERVICOS
# ============================================================

class BRZHistServicos(BaseBronzeModel):
    #id_servico: Optional[int] = Field(default=None, alias="ID_SERVICO")

    cod_concessionaria: str = Field(alias="COD_CONCESSIONARIA")
    cod_filial: str = Field(alias="COD_FILIAL")

    nome_concessionaria: Optional[str] = Field(default=None, alias="NOME_CONCESSIONARIA")
    nome_filial: Optional[str] = Field(default=None, alias="NOME_FILIAL")

    dt_realizacao_servico: date = Field(alias="DT_REALIZACAO_SERVICO")

    qtde_servicos: Optional[int] = Field(default=None, alias="QTDE_SERVICOS")
    valor_total_servico: Optional[float] = Field(default=None, alias="VALOR_TOTAL_SERVICO")
    lucro_servico: Optional[float] = Field(default=None, alias="LUCRO_SERVICO")

    descricao_servico: Optional[str] = Field(default=None, alias="DESCRICAO_SERVICO")
    secao_servico: Optional[str] = Field(default=None, alias="SECAO_SERVICO")
    departamento_servico: Optional[str] = Field(default=None, alias="DEPARTAMENTO_SERVICO")
    categoria_servico: Optional[str] = Field(default=None, alias="CATEGORIA_SERVICO")

    nome_vendedor_servico: Optional[str] = Field(default=None, alias="NOME_VENDEDOR_SERVICO")
    nome_mecanico: Optional[str] = Field(default=None, alias="NOME_MECANICO")
    nome_cliente: Optional[str] = Field(default=None, alias="NOME_CLIENTE")


# ============================================================
# BRZ_HIST_VENDAS_PECAS
# ============================================================

class BRZHistVendasPecas(BaseBronzeModel):
    #id_venda_peca: Optional[int] = Field(default=None, alias="ID_VENDA_PECA")

    cod_concessionaria: str = Field(alias="COD_CONCESSIONARIA")
    cod_filial: str = Field(alias="COD_FILIAL")

    nome_concessionaria: Optional[str] = Field(default=None, alias="NOME_CONCESSIONARIA")
    nome_filial: Optional[str] = Field(default=None, alias="NOME_FILIAL")
    marca_filial: Optional[str] = Field(default=None, alias="MARCA_FILIAL")

    dt_venda: date = Field(alias="DT_VENDA")

    qtde_vendida: Optional[float] = Field(default=None, alias="QTDE_VENDIDA")
    tipo_transacao: Optional[str] = Field(default=None, alias="TIPO_TRANSACAO")

    valor_venda: Optional[float] = Field(default=None, alias="VALOR_VENDA")
    custo_peca: Optional[float] = Field(default=None, alias="CUSTO_PECA")
    lucro_venda: Optional[float] = Field(default=None, alias="LUCRO_VENDA")
    margem_venda: Optional[float] = Field(default=None, alias="MARGEM_VENDA")

    descricao_peca: Optional[str] = Field(default=None, alias="DESCRICAO_PECA")
    categoria_peca: Optional[str] = Field(default=None, alias="CATEGORIA_PECA")

    departamento_venda: Optional[str] = Field(default=None, alias="DEPARTAMENTO_VENDA")
    tipo_venda_peca: Optional[str] = Field(default=None, alias="TIPO_VENDA_PECA")

    nome_vendedor: Optional[str] = Field(default=None, alias="NOME_VENDEDOR")
    nome_comprador: Optional[str] = Field(default=None, alias="NOME_COMPRADOR")

    cidade_venda: Optional[str] = Field(default=None, alias="CIDADE_VENDA")
    estado_venda: Optional[str] = Field(default=None, alias="ESTADO_VENDA")
    macroregiao_venda: Optional[str] = Field(default=None, alias="MACROREGIAO_VENDA")


# ============================================================
# BRZ_HIST_VENDAS_VEICULOS
# ============================================================

class BRZHistVendasVeiculos(BaseBronzeModel):
    #id_venda_veiculo: Optional[int] = Field(default=None, alias="ID_VENDA_VEICULO")

    cod_concessionaria: str = Field(alias="COD_CONCESSIONARIA")
    cod_filial: str = Field(alias="COD_FILIAL")

    nome_concessionaria: Optional[str] = Field(default=None, alias="NOME_CONCESSIONARIA")
    nome_filial: Optional[str] = Field(default=None, alias="NOME_FILIAL")
    marca_filial: Optional[str] = Field(default=None, alias="MARCA_FILIAL")

    dt_venda: date = Field(alias="DT_VENDA")

    qtde_vendida: Optional[int] = Field(default=None, alias="QTDE_VENDIDA")
    tipo_transacao: Optional[str] = Field(default=None, alias="TIPO_TRANSACAO")

    valor_venda: Optional[float] = Field(default=None, alias="VALOR_VENDA")
    custo_veiculo: Optional[float] = Field(default=None, alias="CUSTO_VEICULO")
    lucro_venda: Optional[float] = Field(default=None, alias="LUCRO_VENDA")
    margem_venda: Optional[float] = Field(default=None, alias="MARGEM_VENDA")

    marca_veiculo: Optional[str] = Field(default=None, alias="MARCA_VEICULO")
    modelo_veiculo: Optional[str] = Field(default=None, alias="MODELO_VEICULO")
    familia_veiculo: Optional[str] = Field(default=None, alias="FAMILIA_VEICULO")
    categoria_veiculo: Optional[str] = Field(default=None, alias="CATEGORIA_VEICULO")
    cor_veiculo: Optional[str] = Field(default=None, alias="COR_VEICULO")

    veiculo_novo_seminovo: Optional[str] = Field(default=None, alias="VEICULO_NOVO_SEMINOVO")
    tipo_combustivel: Optional[str] = Field(default=None, alias="TIPO_COMBUSTIVEL")

    ano_modelo: Optional[int] = Field(default=None, alias="ANO_MODELO")
    ano_fabricacao: Optional[int] = Field(default=None, alias="ANO_FABRICACAO")

    chassi_veiculo: Optional[str] = Field(default=None, alias="CHASSI_VEICULO")
    dias_em_estoque: Optional[int] = Field(default=None, alias="DIAS_EM_ESTOQUE")

    tipo_venda_veiculo: Optional[str] = Field(default=None, alias="TIPO_VENDA_VEICULO")
    nome_vendedor: Optional[str] = Field(default=None, alias="NOME_VENDEDOR")
    nome_comprador: Optional[str] = Field(default=None, alias="NOME_COMPRADOR")

    cidade_venda: Optional[str] = Field(default=None, alias="CIDADE_VENDA")
    estado_venda: Optional[str] = Field(default=None, alias="ESTADO_VENDA")
    macroregiao_venda: Optional[str] = Field(default=None, alias="MACROREGIAO_VENDA")
