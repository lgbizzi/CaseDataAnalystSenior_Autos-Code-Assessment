from __future__ import annotations

from datetime import date
import streamlit as st
import pandas as pd
import plotly.express as px

from repositories.kpi_repository import KpiRepository


def _fmt_money(x) -> str:
    try:
        v = float(x or 0)
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def _fmt_pct(x) -> str:
    try:
        return f"{float(x)*100:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "-"


def render() -> None:
    st.subheader("Visão geral")

    c1, c2 = st.columns(2)
    with c1:
        dt_ini = st.date_input("Data inicial", value=date(2025, 1, 1))
    with c2:
        dt_fim = st.date_input("Data final", value=date(2025, 12, 31))

    repo = KpiRepository()
    kpis = repo.kpis_gerais_periodo(dt_ini, dt_fim)

    receita_total = kpis.get("RECEITA_TOTAL", 0) or 0
    lucro_total = kpis.get("LUCRO_TOTAL", 0) or 0
    margem_total = (lucro_total / receita_total) if receita_total else None

    a, b, c, d = st.columns(4)
    a.metric("Receita total", _fmt_money(receita_total), border=True)
    b.metric("Lucro total", _fmt_money(lucro_total), border=True)
    c.metric("Margem total", _fmt_pct(margem_total) if margem_total is not None else "-", border=True)
    d.metric("Estoque peças (valor)", _fmt_money(kpis.get("VALOR_ESTOQUE_PEC", 0) or 0), border=True)

    st.divider()
    st.caption("Quebra por linha de negócio")

    v1, v2, v3 = st.columns(3)

    rv = kpis.get("RECEITA_VEIC", 0) or 0
    lv = kpis.get("LUCRO_VEIC", 0) or 0
    v1.metric("Veículos - Receita", _fmt_money(rv), border=True)
    v1.metric("Veículos - Margem", _fmt_pct((lv / rv)) if rv else "-", border=True)

    rp = kpis.get("RECEITA_PEC", 0) or 0
    lp = kpis.get("LUCRO_PEC", 0) or 0
    v2.metric("Peças - Receita", _fmt_money(rp), border=True)
    v2.metric("Peças - Margem", _fmt_pct((lp / rp)) if rp else "-", border=True)

    rs = kpis.get("RECEITA_SRV", 0) or 0
    ls = kpis.get("LUCRO_SRV", 0) or 0
    v3.metric("Serviços - Receita", _fmt_money(rs), border=True)
    v3.metric("Serviços - Margem", _fmt_pct((ls / rs)) if rs else "-", border=True)

    df = pd.DataFrame(repo.receita_mensal_total(dt_ini, dt_fim))
    if not df.empty:
        fig = px.line(df, x="MES", y="RECEITA_TOTAL", title="Receita total por mês")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados no período selecionado.")
