from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st
import plotly.express as px

from repositories.dashboard_analitico_repository import DashboardAnaliticoRepository
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
    st.subheader("Dashboard Analítico (Semanal/Mensal)")

    with st.sidebar:
        st.subheader("Filtros")
        dt_ini = st.date_input("Data inicial", value=date(2025, 1, 1))
        dt_fim = st.date_input("Data final", value=date(2025, 12, 31))
        top_n = st.slider("Top N", min_value=10, max_value=50, value=20, step=5)

        # Metas (MVP: input manual)
        meta_lucro = st.number_input("Meta lucro (período)", min_value=0.0, value=500000.0, step=50000.0)
        meta_est_veic = st.number_input("Meta estoque veículos (valor)", min_value=0.0, value=5000000.0, step=100000.0)
        meta_est_pec = st.number_input("Meta estoque peças (valor)", min_value=0.0, value=1000000.0, step=50000.0)

    repo = DashboardAnaliticoRepository()
    tab1, tab2, tab3, tab4 = st.tabs(["Rentabilidade", "Estoque", "Performance Filial", "Sazonalidade"])  # [web:148]

    # ---------------- Rentabilidade ----------------
    with tab1:
        pnl = pd.DataFrame(repo.pnl_mensal(dt_ini, dt_fim))
        if pnl.empty:
            st.info("Sem dados no período.")
        else:
            lucro_total = pnl["LUCRO_TOTAL"].sum()
            a, b = st.columns(2)
            a.metric("Lucro total", _fmt_money(lucro_total), delta=_fmt_money(lucro_total - meta_lucro), border=True)
            b.metric("Meta lucro", _fmt_money(meta_lucro), border=True)

            veic_m = (pnl["VEIC_LUCRO"].sum() / pnl["VEIC_RECEITA"].sum()) if pnl["VEIC_RECEITA"].sum() else None
            pec_m = (pnl["PEC_LUCRO"].sum() / pnl["PEC_RECEITA"].sum()) if pnl["PEC_RECEITA"].sum() else None
            srv_m = (pnl["SRV_LUCRO"].sum() / pnl["SRV_RECEITA"].sum()) if pnl["SRV_RECEITA"].sum() else None

            c1, c2, c3 = st.columns(3)
            c1.metric("Margem Veículos", _fmt_pct(veic_m), border=True)
            c2.metric("Margem Peças", _fmt_pct(pec_m), border=True)
            c3.metric("Margem Serviços", _fmt_pct(srv_m), border=True)

            roi = pd.DataFrame(repo.roi_por_filial_periodo(dt_ini, dt_fim))
            if not roi.empty:
                fig = px.bar(
                    roi.sort_values("ROI_ESTOQUE", ascending=True).tail(top_n),
                    x="ROI_ESTOQUE",
                    y="NOME_FILIAL",
                    orientation="h",
                    title="ROI por filial (lucro período / capital em estoque atual) - Top",
                )
                st.plotly_chart(fig, use_container_width=True)

            vend = pd.DataFrame(repo.lucro_por_vendedor(dt_ini, dt_fim, top_n=top_n))
            if not vend.empty:
                fig2 = px.bar(
                    vend.sort_values("LUCRO_TOTAL", ascending=True),
                    x="LUCRO_TOTAL",
                    y="VENDEDOR",
                    orientation="h",
                    title="Lucro por vendedor (veículos + peças + serviços) - Top",
                )
                st.plotly_chart(fig2, use_container_width=True)

    # ---------------- Estoque ----------------
    with tab2:
        k = repo.estoque_kpis()

        a, b, c = st.columns(3)
        a.metric(
            "Estoque veículos (valor)",
            _fmt_money(k.get("ESTOQUE_VEIC_VALOR")),
            delta=_fmt_money((k.get("ESTOQUE_VEIC_VALOR") or 0) - meta_est_veic),
            border=True,
        )
        b.metric(
            "Estoque peças (valor)",
            _fmt_money(k.get("ESTOQUE_PEC_VALOR")),
            delta=_fmt_money((k.get("ESTOQUE_PEC_VALOR") or 0) - meta_est_pec),
            border=True,
        )
        c.metric(
            "Dias médios estoque veículos (atual)",
            f'{float(k.get("ESTOQUE_VEIC_DIAS_MEDIO_ATUAL") or 0):.1f}',
            border=True,
        )

        # Top 20 peças em valor estocado
        toppec = pd.DataFrame(repo.top_pecas_valor_estoque(top_n=20))
        if not toppec.empty:
            fig = px.bar(
                toppec.sort_values("VALOR_ESTOQUE", ascending=True),
                x="VALOR_ESTOQUE",
                y="DESCRICAO_PECA",
                orientation="h",
                title="Top 20 peças por valor estocado",
            )
            st.plotly_chart(fig, use_container_width=True)

        # Giro (proxy) por categoria
        giro = pd.DataFrame(repo.rotatividade_pecas_categoria_proxy(dt_ini, dt_fim))
        if not giro.empty:
            fig2 = px.bar(
                giro.sort_values("GIRO_PROXY", ascending=True).tail(top_n),
                x="GIRO_PROXY",
                y="CATEGORIA_PECA",
                orientation="h",
                title="Rotatividade de peças por categoria (proxy)",
            )
            st.plotly_chart(fig2, use_container_width=True)

        # --- NOVO: Atual vs Histórico (dias em estoque) ---
        st.divider()
        st.subheader("Dias em estoque: Atual vs Histórico")

        dias_atual = float(k.get("ESTOQUE_VEIC_DIAS_MEDIO_ATUAL") or 0)
        hist = pd.DataFrame(repo.dias_estoque_historico_venda_mensal(dt_ini, dt_fim))

        if hist.empty:
            st.info("Sem histórico de DIAS_EM_ESTOQUE no período selecionado.")
        else:
            hist["MES"] = pd.to_datetime(hist["MES"])
            hist = hist.sort_values("MES")

            # Construir dataframe em formato longo para 2 linhas no mesmo gráfico
            df_plot = pd.concat([
                hist[["MES", "DIAS_MEDIO_VENDA"]].rename(columns={"DIAS_MEDIO_VENDA": "DIAS"}).assign(SERIE="Histórico (vendidos)"),
                hist[["MES"]].assign(DIAS=dias_atual, SERIE="Atual (estoque)"),
            ], ignore_index=True)

            fig3 = px.line(
                df_plot,
                x="MES",
                y="DIAS",
                color="SERIE",
                title="Dias médios em estoque — atual (snapshot) vs histórico (veículos vendidos)",
            )
            st.plotly_chart(fig3, use_container_width=True)

    # ---------------- Performance Filial ----------------
    with tab3:
        st.caption("Rankings principais por filial (reuso da tela Performance por Filial).")

        perf_repo = PerformanceFilialRepository()
        perf_rows = perf_repo.performance_por_filial(dt_ini, dt_fim, top_n=200)
        dfp = pd.DataFrame(perf_rows)

        if dfp.empty:
            st.info("Sem dados para performance por filial no período.")
        else:
            # Top ROI
            df_roi = dfp.dropna(subset=["ROI_ESTOQUE"]).sort_values("ROI_ESTOQUE", ascending=False).head(top_n)
            if not df_roi.empty:
                fig_roi = px.bar(
                    df_roi.sort_values("ROI_ESTOQUE", ascending=True),
                    x="ROI_ESTOQUE",
                    y="NOME_FILIAL",
                    orientation="h",
                    title="Top filiais por ROI (lucro/estoque)",
                )
                st.plotly_chart(fig_roi, use_container_width=True)

            # Top Lucro
            df_lucro = dfp.sort_values("LUCRO_TOTAL", ascending=False).head(top_n)
            if not df_lucro.empty:
                fig_lucro = px.bar(
                    df_lucro.sort_values("LUCRO_TOTAL", ascending=True),
                    x="LUCRO_TOTAL",
                    y="NOME_FILIAL",
                    orientation="h",
                    title="Top filiais por lucro total (período)",
                )
                st.plotly_chart(fig_lucro, use_container_width=True)

            # Tabela enxuta (benchmark)
            st.dataframe(
                dfp[["NOME_FILIAL", "RECEITA_TOTAL", "LUCRO_TOTAL", "CAPITAL_ESTOQUE", "ROI_ESTOQUE"]]
                .sort_values("ROI_ESTOQUE", ascending=False)
                .head(50),
                use_container_width=True,
                hide_index=True,
            )

    # ---------------- Sazonalidade ----------------
    with tab4:
        pnl = pd.DataFrame(repo.pnl_mensal(dt_ini, dt_fim))
        if pnl.empty:
            st.info("Sem dados no período.")
        else:
            pnl["MES"] = pd.to_datetime(pnl["MES"])
            pnl = pnl.sort_values("MES")

            last12 = pnl.tail(12)
            fig = px.line(last12, x="MES", y="RECEITA_TOTAL", title="Vendas - últimos 12 meses (receita total)")
            st.plotly_chart(fig, use_container_width=True)

            pnl["ANO"] = pnl["MES"].dt.year
            pnl["MESNUM"] = pnl["MES"].dt.month
            if pnl["ANO"].nunique() >= 2:
                yoy = pnl.groupby(["ANO", "MESNUM"], as_index=False)["RECEITA_TOTAL"].sum()
                fig2 = px.line(yoy, x="MESNUM", y="RECEITA_TOTAL", color="ANO", title="Comparação vs ano anterior (receita por mês)")
                st.plotly_chart(fig2, use_container_width=True)

            st.info("Previsão próximo mês: pode ser feita com regressão linear simples na série mensal (próximo passo), mas não há modelo pronto no dataset.")
