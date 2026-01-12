from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st
import plotly.express as px

from repositories.performance_filial_repository import PerformanceFilialRepository


def _fmt_money(v) -> str:
    try:
        x = float(v or 0)
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def _fmt_pct(v) -> str:
    if v is None:
        return "-"
    try:
        return f"{float(v)*100:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "-"


def render() -> None:
    st.subheader("Performance por Filial")
    st.caption("Comparativo por filial: vendas, serviços, estoques e ROI (proxy).")

    with st.sidebar:
        st.subheader("Filtros")
        dt_ini = st.date_input("Data inicial", value=date(2025, 1, 1))
        dt_fim = st.date_input("Data final", value=date(2025, 12, 31))
        top_n = st.slider("Top N filiais", min_value=5, max_value=100, value=30, step=5)

    repo = PerformanceFilialRepository()
    rows = repo.performance_por_filial(dt_ini, dt_fim, top_n=top_n)
    df = pd.DataFrame(rows)

    if df.empty:
        st.info("Sem dados para os filtros atuais.")
        return

    # --- KPIs gerais (somatório das filiais exibidas) ---
    lucro_total = df["LUCRO_TOTAL"].sum()
    capital = df["CAPITAL_ESTOQUE"].sum()
    roi = (lucro_total / capital) if capital else None

    a, b, c = st.columns(3)
    a.metric("Lucro total (amostra)", _fmt_money(lucro_total), border=True)
    b.metric("Capital em estoque (amostra)", _fmt_money(capital), border=True)
    c.metric("ROI (lucro/estoque) amostra", _fmt_pct(roi), border=True)

    # --- Ranking (barras) ---
    st.divider()
    st.subheader("Ranking (ROI)")

    df_rank = df.sort_values("ROI_ESTOQUE", ascending=True)
    fig = px.bar(
        df_rank,
        x="ROI_ESTOQUE",
        y="NOME_FILIAL",
        orientation="h",
        title="ROI por filial (lucro total / capital em estoque)",
    )
    st.plotly_chart(fig, use_container_width=True)  # [web:144]

    # --- Benchmarking: comparar duas filiais ---
    st.divider()
    st.subheader("Benchmarking (2 filiais)")

    filiais = df["NOME_FILIAL"].dropna().unique().tolist()
    col1, col2 = st.columns(2)
    with col1:
        f1 = st.selectbox("Filial A", options=filiais, index=0)
    with col2:
        f2 = st.selectbox("Filial B", options=filiais, index=min(1, len(filiais)-1))

    a_df = df[df["NOME_FILIAL"] == f1].iloc[0]
    b_df = df[df["NOME_FILIAL"] == f2].iloc[0]

    comp = pd.DataFrame([
        {"Métrica": "ROI (lucro/estoque)", "Filial A": a_df["ROI_ESTOQUE"], "Filial B": b_df["ROI_ESTOQUE"]},
        {"Métrica": "Lucro total", "Filial A": a_df["LUCRO_TOTAL"], "Filial B": b_df["LUCRO_TOTAL"]},
        {"Métrica": "Capital em estoque", "Filial A": a_df["CAPITAL_ESTOQUE"], "Filial B": b_df["CAPITAL_ESTOQUE"]},
        {"Métrica": "Margem veículos", "Filial A": a_df["VEIC_MARGEM"], "Filial B": b_df["VEIC_MARGEM"]},
        {"Métrica": "Margem peças", "Filial A": a_df["PEC_MARGEM"], "Filial B": b_df["PEC_MARGEM"]},
        {"Métrica": "Margem serviços", "Filial A": a_df["SRV_MARGEM"], "Filial B": b_df["SRV_MARGEM"]},
        {"Métrica": "Receita total", "Filial A": a_df["RECEITA_TOTAL"], "Filial B": b_df["RECEITA_TOTAL"]},
    ])

    # formatação simples
    def fmt_row(row):
        if "Margem" in row["Métrica"] or "ROI" in row["Métrica"]:
            row["Filial A"] = _fmt_pct(row["Filial A"])
            row["Filial B"] = _fmt_pct(row["Filial B"])
        else:
            row["Filial A"] = _fmt_money(row["Filial A"])
            row["Filial B"] = _fmt_money(row["Filial B"])
        return row

    comp = comp.apply(fmt_row, axis=1)
    st.dataframe(comp, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Oportunidades (heurísticas)")
    st.write(
        "- Realocar estoque: filiais com alto capital em estoque e baixo ROI são candidatas a reduzir/redistribuir estoque.\n"
        "- Compartilhar conhecimento: filiais com margem de serviços acima da média podem servir de referência operacional.\n"
        "- Centralizar compras: filiais com margem de peças muito abaixo podem indicar custo alto ou pricing inconsistente."
    )
