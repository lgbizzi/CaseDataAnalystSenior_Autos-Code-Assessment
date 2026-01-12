from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st
import plotly.express as px

from repositories.rentabilidade_integrada_repository import RentabilidadeIntegradaRepository


def _fmt_money(x) -> str:
    try:
        v = float(x or 0)
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def _fmt_pct(x) -> str:
    if x is None:
        return "-"
    try:
        return f"{float(x)*100:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "-"


def render() -> None:
    st.subheader("Rentabilidade Integrada")
    st.caption("Vendas de veículos + pós-venda (serviços e peças) no mesmo cliente dentro de uma janela em dias.")

    with st.sidebar:
        st.subheader("Filtros")
        dt_ini = st.date_input("Data inicial (venda veículo)", value=date(2025, 1, 1))
        dt_fim = st.date_input("Data final (venda veículo)", value=date(2025, 12, 31))
        janela = st.number_input("Janela pós-venda (dias)", min_value=0, max_value=180, value=30, step=5)
        limit = st.number_input("Limite de registros", min_value=50, max_value=2000, value=200, step=50)

    repo = RentabilidadeIntegradaRepository()
    rows = repo.margem_integrada_por_venda_veiculo(dt_ini, dt_fim, janela_dias=int(janela), limit=int(limit))
    df = pd.DataFrame(rows)

    if df.empty:
        st.info("Sem dados para o período/filtros selecionados.")
        return

    # KPIs do recorte exibido
    receita_int = df["RECEITA_INTEGRADA"].sum()
    lucro_int = df["LUCRO_INTEGRADO"].sum()
    margem_int = (lucro_int / receita_int) if receita_int else None

    a, b, c = st.columns(3)
    a.metric("Receita integrada (amostra)", _fmt_money(receita_int), border=True)
    b.metric("Lucro integrado (amostra)", _fmt_money(lucro_int), border=True)
    c.metric("Margem integrada (amostra)", _fmt_pct(margem_int), border=True)

    st.divider()

    # Ordenação para “insight”: veículos com baixa margem na venda mas alta margem integrada
    df_insight = df.copy()
    df_insight["DELTA_MARGEM"] = (df_insight["MARGEM_INTEGRADA"].fillna(0) - df_insight["MARGEM_VEICULO"].fillna(0))
    df_insight = df_insight.sort_values(["DELTA_MARGEM", "RECEITA_VEICULO"], ascending=[False, False])

    st.caption("Top casos onde pós-venda melhora a margem (Δ = integrada - venda veículo)")
    show_cols = [
        "DT_VENDA", "NOME_FILIAL", "NOME_COMPRADOR", "MARCA_VEICULO", "MODELO_VEICULO",
        "RECEITA_VEICULO", "MARGEM_VEICULO",
        "RECEITA_SERVICOS", "RECEITA_PECAS",
        "RECEITA_INTEGRADA", "MARGEM_INTEGRADA",
        "DELTA_MARGEM"
    ]

    st.dataframe(
        df_insight[show_cols],
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.subheader("Análise 2 — Ranking de modelos (rentabilidade integrada)")

    top_n = st.slider("Top N modelos", min_value=5, max_value=30, value=15, step=1)
    min_receita = st.number_input("Receita mínima (veículo) para entrar no ranking", min_value=0.0, value=0.0, step=10000.0)

    rank_rows = repo.ranking_modelos_rentabilidade_integrada(
        dt_ini, dt_fim,
        janela_dias=int(janela),
        top_n=int(top_n),
        min_receita_veiculo=float(min_receita),
    )
    df_rank = pd.DataFrame(rank_rows)

    if df_rank.empty:
        st.info("Sem dados para ranking com os filtros atuais.")
    else:
        df_rank["MODELO_LABEL"] = df_rank["MARCA_VEICULO"].astype(str) + " - " + df_rank["MODELO_VEICULO"].astype(str)

        fig = px.bar(
            df_rank.sort_values("MARGEM_INTEGRADA", ascending=True),
            x="MARGEM_INTEGRADA",
            y="MODELO_LABEL",
            orientation="h",
            title="Top modelos por margem integrada",
        )
        st.plotly_chart(fig, use_container_width=True)  # [web:87]

        st.dataframe(
            df_rank[["MARCA_VEICULO","MODELO_VEICULO","QTD_VENDAS","RECEITA_INTEGRADA","LUCRO_INTEGRADO","MARGEM_INTEGRADA"]],
            use_container_width=True,
            hide_index=True
        )

"""
    st.divider()
    st.subheader("Análise 3 — Fluxo de caixa (proxy)")
    st.caption("Comparação entre capital imobilizado em estoque e entradas de receita no período (proxy).")

    fc_rows = repo.fluxo_caixa_proxy(dt_ini, dt_fim)
    df_fc = pd.DataFrame(fc_rows)

    if df_fc.empty:
        st.info("Sem dados para fluxo de caixa (proxy).")
    else:
        fig2 = px.bar(
            df_fc,
            x="ITEM",
            y="VALOR",
            color="TIPO",
            barmode="group",
            title="Capital imobilizado vs entradas no período",
        )
        st.plotly_chart(fig2, use_container_width=True)  # [web:87]

        st.dataframe(df_fc, use_container_width=True, hide_index=True)
"""