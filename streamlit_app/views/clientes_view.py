from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st
import plotly.express as px

from repositories.clientes_repository import ClientesRepository


def _fmt_money(v) -> str:
    try:
        x = float(v or 0)
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def render() -> None:
    st.subheader("Clientes")
    st.caption("Funil de clientes, LTV (proxy) e segmentação RFM.")

    with st.sidebar:
        st.subheader("Filtros")
        dt_ini = st.date_input("Data inicial", value=date(2025, 1, 1))
        dt_fim = st.date_input("Data final", value=date(2025, 12, 31))
        top_n = st.slider("Top N (LTV)", min_value=10, max_value=200, value=50, step=10)

    repo = ClientesRepository()

    # --- Funil 2023 ---
    st.markdown("### Funil Período")
    funil = repo.funil_clientes()

    a, b, c = st.columns(3)
    a.metric("Compraram veículo no período", int(funil.get("CLIENTES_VEIC_2023", 0) or 0), border=True)
    b.metric("Desses, fizeram serviço (período)", int(funil.get("COM_SERVICO_POSTERIOR", 0) or 0), border=True)
    c.metric("Desses, compraram peças (período)", int(funil.get("COM_COMPRA_PECAS", 0) or 0), border=True)

    st.divider()

    # --- LTV (proxy) ---
    st.markdown("### Lifetime Value (proxy)")
    ltv = pd.DataFrame(repo.ltv_por_cliente(dt_ini, dt_fim, top_n=top_n))
    if ltv.empty:
        st.info("Sem dados para o período selecionado.")
        return

    fig = px.bar(
        ltv.sort_values("RECEITA_TOTAL", ascending=True),
        x="RECEITA_TOTAL",
        y="CLIENTE",
        orientation="h",
        title="Top clientes por receita total (ciclo completo - proxy)",
    )
    st.plotly_chart(fig, use_container_width=True)  # ranking -> barras

    st.dataframe(
        ltv[["CLIENTE", "TRANSACOES", "PRIMEIRA_DATA", "ULTIMA_DATA", "RECEITA_TOTAL", "LUCRO_TOTAL"]],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # --- RFM ---
    st.markdown("### RFM e Segmentos")
    rfm = pd.DataFrame(repo.rfm_base(dt_ini, dt_fim))
    if rfm.empty:
        st.info("Sem dados para RFM.")
        return

    # Scores por quantis (simples e robusto)
    # Recency: menor é melhor; Frequency/Monetary: maior é melhor
    rfm["R_SCORE"] = pd.qcut(rfm["RECENCY_DIAS"].rank(method="first"), 5, labels=[5,4,3,2,1]).astype(int)
    rfm["F_SCORE"] = pd.qcut(rfm["FREQUENCY"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    rfm["M_SCORE"] = pd.qcut(rfm["MONETARY"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)

    # Segmentação (heurística alinhada ao seu texto)
    def segment(row):
        recent = row["R_SCORE"] >= 4
        freq_high = row["F_SCORE"] >= 4
        money_high = row["M_SCORE"] >= 4

        if recent and freq_high and money_high:
            return "VIP"
        if recent and freq_high and not money_high:
            return "Crescimento"
        if (not recent) and (freq_high or money_high):
            return "Risco"
        return "Dorminte"

    rfm["SEGMENTO"] = rfm.apply(segment, axis=1)

    seg = rfm.groupby("SEGMENTO", as_index=False).agg(
        CLIENTES=("CLIENTE", "count"),
        RECEITA=("MONETARY", "sum"),
        FREQ_MEDIA=("FREQUENCY", "mean"),
        RECENCY_MEDIA=("RECENCY_DIAS", "mean"),
    )

    fig2 = px.bar(
        seg.sort_values("CLIENTES", ascending=True),
        x="CLIENTES",
        y="SEGMENTO",
        orientation="h",
        title="Distribuição de clientes por segmento RFM",
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(seg, use_container_width=True, hide_index=True)

    st.caption("Observação: RFM usa transações agregadas (veículo + peça + serviço) e Recency/Frequency/Monetary do período selecionado.")
