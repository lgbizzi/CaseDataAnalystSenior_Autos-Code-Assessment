from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

from repositories.dashboard_preditivo_repository import DashboardPreditivoRepository


def _make_daily_series(rows: list[dict], dt_ini: date, dt_fim: date) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame({"DIA": pd.date_range(dt_ini, dt_fim, freq="D"), "Y": 0.0})

    df["DIA"] = pd.to_datetime(df["DIA"])
    df["Y"] = df["Y"].astype(float)

    full = pd.DataFrame({"DIA": pd.date_range(dt_ini, dt_fim, freq="D")})
    df = full.merge(df, on="DIA", how="left").fillna({"Y": 0.0})
    return df


def _forecast_ma_with_ci(df: pd.DataFrame, horizon: int, ma_window: int, seed: int = 42) -> pd.DataFrame:
    """
    Forecast simples:
    - ponto = média móvel dos últimos 'ma_window' dias
    - IC via bootstrap dos resíduos do ajuste in-sample usando MA
    """
    y = df["Y"].values.astype(float)
    if len(y) < max(10, ma_window + 2):
        # pouco histórico: repete média global
        base = float(np.mean(y)) if len(y) else 0.0
        future = pd.DataFrame({"t": np.arange(1, horizon + 1), "yhat": base})
        future["yhat_80_lo"] = future["yhat"]
        future["yhat_80_hi"] = future["yhat"]
        future["yhat_95_lo"] = future["yhat"]
        future["yhat_95_hi"] = future["yhat"]
        return future

    # fitted MA (in-sample)
    fitted = pd.Series(y).rolling(ma_window).mean().shift(1).fillna(np.mean(y[:ma_window]))
    resid = y - fitted.values

    # forecast point = last rolling mean
    last_ma = float(pd.Series(y).tail(ma_window).mean())
    yhat = np.full(horizon, last_ma, dtype=float)

    # bootstrap residuals -> simula trajetória
    rng = np.random.default_rng(seed)
    n_sim = 1000
    sims = np.zeros((n_sim, horizon))
    for i in range(n_sim):
        noise = rng.choice(resid, size=horizon, replace=True)
        sims[i, :] = np.clip(yhat + noise, a_min=0.0, a_max=None)

    # intervalos por percentil
    lo80, hi80 = np.percentile(sims, [10, 90], axis=0)
    lo95, hi95 = np.percentile(sims, [2.5, 97.5], axis=0)

    out = pd.DataFrame({
        "t": np.arange(1, horizon + 1),
        "yhat": yhat,
        "yhat_80_lo": lo80,
        "yhat_80_hi": hi80,
        "yhat_95_lo": lo95,
        "yhat_95_hi": hi95,
    })
    return out


def _plot_forecast(title: str, hist: pd.DataFrame, forecast: pd.DataFrame) -> None:
    last_day = hist["DIA"].max()
    future_days = pd.date_range(last_day + pd.Timedelta(days=1), periods=len(forecast), freq="D")

    fc = forecast.copy()
    fc["DIA"] = future_days

    # junta para plot
    hist_plot = hist.copy()
    hist_plot["TIPO"] = "Histórico"
    hist_plot = hist_plot.rename(columns={"Y": "VALOR"})

    fc_plot = fc[["DIA", "yhat"]].copy()
    fc_plot["TIPO"] = "Forecast"
    fc_plot = fc_plot.rename(columns={"yhat": "VALOR"})

    df_plot = pd.concat([hist_plot[["DIA", "VALOR", "TIPO"]], fc_plot], ignore_index=True)
    fig = px.line(df_plot, x="DIA", y="VALOR", color="TIPO", title=title)
    st.plotly_chart(fig, use_container_width=True)

    # intervalos como tabela (MVP)
    ci = fc[["DIA", "yhat", "yhat_80_lo", "yhat_80_hi", "yhat_95_lo", "yhat_95_hi"]].tail(15)
    st.caption("Intervalos de confiança (últimos 15 pontos previstos)")
    st.dataframe(ci, use_container_width=True, hide_index=True)


def render() -> None:
    st.subheader("Dashboard Preditivo")
    st.caption("Forecasts e alertas por heurísticas (MVP).")

    with st.sidebar:
        st.subheader("Configuração")
        dt_ini = st.date_input("Início histórico", value=date(2025, 1, 1))
        dt_fim = st.date_input("Fim histórico", value=date(2025, 12, 31))
        ma_window = st.slider("Janela média móvel (dias)", 3, 30, 7, 1)
        horizon = st.selectbox("Horizonte", options=[30, 60, 90], index=0)
        dias_media_peca = st.selectbox("Janela consumo peças (dias)", options=[14, 30, 60], index=1)

    repo = DashboardPreditivoRepository()
    tab1, tab2, tab3 = st.tabs(["Forecast Vendas", "Forecast Estoque", "Alertas & Recomendações"])

    # ---------- Forecast Vendas ----------
    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.metric("Horizonte (dias)", str(horizon), border=True)
        c2.metric("IC 80%", "P10–P90", border=True)
        c3.metric("IC 95%", "P2.5–P97.5", border=True)

        # Veículos (unidades)
        st.markdown("### Veículos — unidades/dia")
        s1 = _make_daily_series(repo.serie_diaria_veiculos_unidades(dt_ini, dt_fim), dt_ini, dt_fim)
        fc1 = _forecast_ma_with_ci(s1, horizon=horizon, ma_window=ma_window)
        _plot_forecast("Forecast veículos (unidades/dia)", s1.rename(columns={"Y": "Y"}), fc1)

        # Peças (receita)
        st.markdown("### Peças — receita/dia")
        s2 = _make_daily_series(repo.serie_diaria_pecas_receita(dt_ini, dt_fim), dt_ini, dt_fim)
        fc2 = _forecast_ma_with_ci(s2, horizon=horizon, ma_window=ma_window)
        _plot_forecast("Forecast peças (receita/dia)", s2.rename(columns={"Y": "Y"}), fc2)

        # Serviços (receita)
        st.markdown("### Serviços — receita/dia")
        s3 = _make_daily_series(repo.serie_diaria_servicos_receita(dt_ini, dt_fim), dt_ini, dt_fim)
        fc3 = _forecast_ma_with_ci(s3, horizon=horizon, ma_window=ma_window)
        _plot_forecast("Forecast serviços (receita/dia)", s3.rename(columns={"Y": "Y"}), fc3)

    # ---------- Forecast Estoque ----------
    with tab2:
        st.markdown("### Peças com risco de falta (próx. 30 dias)")
        risk = pd.DataFrame(repo.risco_falta_pecas_30d(dias_media=int(dias_media_peca), top_n=30))
        if risk.empty:
            st.info("Nenhuma peça com risco de falta pelo critério atual.")
        else:
            fig = px.bar(
                risk.sort_values("DIAS_COBERTURA", ascending=False),
                x="DIAS_COBERTURA",
                y="DESCRICAO_PECA",
                orientation="h",
                title="Dias de cobertura estimados (quanto menor, pior)",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(risk, use_container_width=True, hide_index=True)

        st.markdown("### Peças obsoletas / paradas")
        obs = pd.DataFrame(repo.pecas_obsoletas(top_n=50))
        if obs.empty:
            st.info("Nenhuma peça marcada como obsoleta (flag) ou com tempo obsoleto alto.")
        else:
            st.dataframe(obs, use_container_width=True, hide_index=True)

    # ---------- Alertas & Recomendações ----------
    with tab3:
        st.markdown("### Alertas inteligentes (heurísticos)")
        st.write("- Peça pode faltar em X dias: baseado em dias de cobertura (estoque / consumo recente).")
        st.write("- Peça obsoleta: baseado em flag/tempo obsoleto/dias sem venda.")
        st.write("- Meta de modelo/filial/vendedor: precisa de metas (não existem no banco), pode ser input manual.")

        st.markdown("### Recomendações (MVP)")
        if 'risk' in locals() and not risk.empty:
            st.write("Aumentar/Manter/Reduzir (heurística):")
            rec = risk.copy()
            rec["RECOMENDACAO"] = rec["DIAS_COBERTURA"].apply(
                lambda d: "Aumentar" if d <= 10 else ("Manter" if d <= 30 else "Reduzir")
            )
            st.dataframe(rec[["CATEGORIA_PECA", "DESCRICAO_PECA", "ESTOQUE_ATUAL", "CONSUMO_MEDIO_DIA", "DIAS_COBERTURA", "RECOMENDACAO"]],
                         use_container_width=True, hide_index=True)
        else:
            st.info("Sem recomendações de reposição no momento (nenhum risco detectado).")
