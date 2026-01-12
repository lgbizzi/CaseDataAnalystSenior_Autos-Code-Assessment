from __future__ import annotations

import pandas as pd
import streamlit as st

from repositories.dashboard_operacional_repository import DashboardOperacionalRepository


def _fmt_money(v) -> str:
    try:
        x = float(v or 0)
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def _fmt_int(v) -> str:
    try:
        return f"{int(v or 0)}"
    except Exception:
        return "0"


def _fmt_pct(v) -> str:
    if v is None:
        return "-"
    try:
        return f"{float(v)*100:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "-"


def render() -> None:
    st.subheader("Dashboard Operacional (Diário)")
    st.caption("Hoje vs Ontem vs Média 30 dias (quando aplicável).")

    repo = DashboardOperacionalRepository()

    # --- Vendas Veículos ---
    st.markdown("### Vendas Veículos")
    kv = repo.kpis_vendas_veiculos_diario()

    c1, c2, c3 = st.columns(3)
    c1.metric("Vendas hoje", _fmt_int(kv.get("QTD_HOJE")), delta=_fmt_int((kv.get("QTD_HOJE") or 0) - (kv.get("QTD_ONTEM") or 0)), border=True)
    c2.metric("Receita hoje", _fmt_money(kv.get("RECEITA_HOJE")), delta=_fmt_money((kv.get("RECEITA_HOJE") or 0) - (kv.get("RECEITA_ONTEM") or 0)), border=True)
    c3.metric("Média 30d (receita)", _fmt_money(kv.get("RECEITA_MEDIA_30D")), border=True)

    # Estoque vs meta / dias médio estoque -> só se você tiver colunas e meta definida
    st.info("Estoque vs meta e dias médio em estoque dependem de colunas/metas que podem não existir no BRZ atual.")

    # --- Vendas Peças ---
    st.markdown("### Vendas Peças")
    kp = repo.kpis_vendas_pecas_diario()
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Receita hoje", _fmt_money(kp.get("RECEITA_HOJE")), delta=_fmt_money((kp.get("RECEITA_HOJE") or 0) - (kp.get("RECEITA_MEDIA_30D") or 0)), border=True)
    p2.metric("Volume hoje", _fmt_int(kp.get("QTD_HOJE")), delta=_fmt_int((kp.get("QTD_HOJE") or 0) - (kp.get("QTD_MEDIA_30D") or 0)), border=True)
    p3.metric("Margem hoje", _fmt_pct(kp.get("MARGEM_HOJE")), border=True)
    p4.metric("Margem média 30d", _fmt_pct(kp.get("MARGEM_MEDIA_30D")), border=True)

    top10 = pd.DataFrame(repo.top10_pecas_hoje())
    st.markdown("#### Top 10 peças vendidas hoje")
    if top10.empty:
        st.info("Sem vendas de peças hoje.")
    else:
        st.dataframe(top10, use_container_width=True, hide_index=True)

    # --- Serviços ---
    st.markdown("### Serviços")
    ks = repo.kpis_servicos_diario()
    s1, s2, s3 = st.columns(3)
    s1.metric("Serviços hoje (proxy OS)", _fmt_int(ks.get("QTD_HOJE")), delta=_fmt_int((ks.get("QTD_HOJE") or 0) - (ks.get("QTD_MEDIA_30D") or 0)), border=True)
    s2.metric("Receita serviços hoje", _fmt_money(ks.get("RECEITA_HOJE")), delta=_fmt_money((ks.get("RECEITA_HOJE") or 0) - (ks.get("RECEITA_MEDIA_30D") or 0)), border=True)
    s3.metric("Média 30d (serviços)", _fmt_int(ks.get("QTD_MEDIA_30D")), border=True)

    st.info("Dias de espera, OS atrasadas e gargalos de capacidade exigem dados de agendamento/status que não constam no dataset BRZ do case.")

    # --- Alertas (os que são possíveis) ---
    st.markdown("### Alertas")
    st.write("- Peças em falta (estoque zerado): possível se BRZ_ESTOQUE_PECAS tiver quantidade em estoque.")
    st.write("- Veículos com 60+ dias em estoque: possível se BRZ_ESTOQUE_VEICULOS tiver dias/tempo em estoque.")
    st.write("- Margem abaixo do limite: possível (peças/serviços/veículos), basta definir limiares.")
