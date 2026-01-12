from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st
import plotly.express as px

from repositories.pos_vendas_repository import PosVendaRepository


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
    st.subheader("Pós-venda")
    st.caption("Análises de serviços (com proxies quando não há OS/itens de peça por serviço).")

    with st.sidebar:
        st.subheader("Filtros")
        dt_ini = st.date_input("Data inicial", value=date(2025, 1, 1))
        dt_fim = st.date_input("Data final", value=date(2025, 12, 31))
        top_n = st.slider("Top N", min_value=5, max_value=30, value=15, step=1)

    repo = PosVendaRepository()

    tab1, tab2, tab3 = st.tabs(["Ticket médio", "Departamento", "Tipo de serviço"])  # [web:148]

    # -------- Ticket médio --------
    with tab1:
        k = repo.kpis_servicos(dt_ini, dt_fim)

        a, b, c, d = st.columns(4)
        a.metric("Receita serviços", _fmt_money(k.get("RECEITA_SERVICOS", 0)), border=True)
        b.metric("Lucro serviços", _fmt_money(k.get("LUCRO_SERVICOS", 0)), border=True)
        c.metric("Margem serviços", _fmt_pct(k.get("MARGEM_SERVICOS")), border=True)
        d.metric("Ticket médio (por registro)", _fmt_money(k.get("TICKET_MEDIO_POR_REGISTRO", 0)), border=True)

        st.info(
            "Limitação: não há número de OS nem itens de peça por OS; portanto métricas 'por OS' e 'peças por OS' não são calculáveis com o BRZ atual."
        )

    # -------- Departamento --------
    with tab2:
        rows = repo.por_departamento(dt_ini, dt_fim, top_n=top_n)
        df = pd.DataFrame(rows)

        if df.empty:
            st.info("Sem dados para os filtros atuais.")
        else:
            # Ranking -> barras horizontais
            fig = px.bar(
                df.sort_values("RECEITA", ascending=True),
                x="RECEITA",
                y="DEPARTAMENTO_SERVICO",
                orientation="h",
                title="Receita por departamento (Top N)",
            )  # [web:144]
            st.plotly_chart(fig, use_container_width=True)  # [web:87]

            # Tabela com margem/volume
            st.dataframe(
                df[["DEPARTAMENTO_SERVICO", "QTDE_SERVICOS", "RECEITA", "LUCRO", "MARGEM"]],
                use_container_width=True,
                hide_index=True,
            )

            st.info("Limitação: 'dias de espera' não existe nas colunas do BRZ_HIST_SERVICOS (sem agendamento/conclusão).")

    # -------- Tipo de serviço --------
    with tab3:
        rows = repo.por_categoria_servico(dt_ini, dt_fim, top_n=top_n)
        df = pd.DataFrame(rows)

        if df.empty:
            st.info("Sem dados para os filtros atuais.")
        else:
            fig = px.bar(
                df.sort_values("LUCRO", ascending=True),
                x="LUCRO",
                y="CATEGORIA_SERVICO",
                orientation="h",
                title="Serviços mais lucrativos por categoria (Top N)",
            )  # [web:144]
            st.plotly_chart(fig, use_container_width=True)  # [web:87]

            st.dataframe(
                df[["CATEGORIA_SERVICO", "QTDE_SERVICOS", "RECEITA", "LUCRO", "MARGEM"]],
                use_container_width=True,
                hide_index=True,
            )

            st.info(
                "Limitação: 'Receita x Peças Utilizadas' não é calculável pois não há relacionamento explícito de peças usadas em cada serviço no BRZ atual."
            )
