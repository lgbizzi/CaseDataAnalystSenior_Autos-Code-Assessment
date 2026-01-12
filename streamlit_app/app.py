import sys
from pathlib import Path

# Adiciona a raiz do projeto (pai de streamlit_app) no PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

# ----------------------------
# (AUTH) Mantido, porém desativado para o case
# ----------------------------
# from auth.auth_service import AuthService
# auth = AuthService()

APP_TITLE = "Autos Code - Dashboard"

# IMPORTANTE: set_page_config deve ser chamado 1x e como primeiro comando Streamlit. [web:64]
st.set_page_config(page_title=APP_TITLE, layout="wide")


def init_session_state() -> None:
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "auth_user" not in st.session_state:
        st.session_state["auth_user"] = None


def do_logout() -> None:
    # (AUTH) Mantido, mas não usado
    st.session_state["authenticated"] = False
    st.session_state["auth_user"] = None
    st.rerun()


# def render_login(auth: AuthService) -> None:
def render_login() -> None:
    # (AUTH) Mantido, porém desativado para o case
    st.title(APP_TITLE)
    st.caption("Acesso restrito. (Desativado no case)")

    # with st.form("login_form", clear_on_submit=False):
    #     username = st.text_input("Usuário", placeholder="autos_code")
    #     password = st.text_input("Senha", type="password", placeholder="••••••••")
    #     submitted = st.form_submit_button("Entrar")
    #
    # if submitted:
    #     ok = auth.authenticate(username, password)
    #     if ok:
    #         st.session_state["authenticated"] = True
    #         st.session_state["auth_user"] = username
    #         st.rerun()
    #     else:
    #         st.error("Usuário ou senha inválidos.")

    st.info("Login desativado para este case. Indo direto para o dashboard.")


def render_app_shell() -> None:
    # Sidebar base
    with st.sidebar:
        st.subheader("Navegação")

        # (AUTH) Mantido, mas opcional no case
        # st.write(f"Usuário: {st.session_state.get('auth_user')}")
        # st.button("Sair", on_click=do_logout)

        page = st.radio(
            "Página",
            options=["Home", 
                     "DASHBOARD - Operacional", 
                     "DASHBOARD - Analítico",
                     "DASHBOARD - Preditivo",
                     "Rentabilidade Integrada", 
                     "Pós-Vendas", 
                     "Performance Filial", 
                     "Clientes"
                     ],
            index=0,
        )

    # Conteúdo
    st.title(APP_TITLE)

    
    if page == "Home":
        from views.home_view import render as render_home
        render_home()
    elif page == "DASHBOARD - Operacional":
        from views.dashboard_operacional_view import render as render_ops
        render_ops()
    elif page == "DASHBOARD - Analítico":
        from views.dashboard_analitico_view import render as render_ops
        render_ops()
    elif page == "DASHBOARD - Preditivo":
        from views.dashboard_preditivo_view import render as render_ops
        render_ops()
    elif page == "Rentabilidade Integrada":
        from views.rentabilidade_integrada_view import render as render_ri
        render_ri()
    elif page == "Pós-Vendas":
        from views.pos_vendas_view import render as render_pos
        render_pos()
    elif page == "Performance Filial":
        from views.performance_filial_view import render as render_perf
        render_perf()
    elif page == "Clientes":
        from views.clientes_view import render as render_clientes
        render_clientes()


def main() -> None:
    init_session_state()

    # ----------------------------
    # (AUTH) DESATIVADO
    # ----------------------------
    # auth = AuthService(config_file="streamlit_app/config/config.ini")
    # if not st.session_state["authenticated"]:
    #     render_login(auth)
    #     st.stop()

    # Vai direto para a tela inicial
    render_app_shell()


if __name__ == "__main__":
    main()
