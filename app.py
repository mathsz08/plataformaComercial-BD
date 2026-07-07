import streamlit as st

from style import inject_custom_css
from views.dashboard import dashboard
from views.clientes import clientes
from views.produtos import produtos
from views.vendedores import vendedores
from views.fornecedores import fornecedores
from views.pedidos import pedidos
from views.estoque import estoque
from views.consultas import consultas

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Plataforma Comercial",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Sistema de Gestão Comercial v1.0"}
)

inject_custom_css()

# ─────────────────────────── SIDEBAR ──────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">🏪</div>
        <div>
            <div class="sidebar-brand-title">Plataforma Comercial</div>
            <div class="sidebar-brand-sub">Gestão Comercial</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navegação",
        ["📊 Dashboard", "👤 Clientes", "📦 Produtos", "🧑‍💼 Vendedores",
         "🏭 Fornecedores", "🛒 Pedidos", "🗃️ Estoque", "🔎 Consultas"],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("v1.0 — PostgreSQL")

# ─────────────────────────── MAIN ────────────────────────────────────────────
if page == "📊 Dashboard":
    dashboard()
elif page == "👤 Clientes":
    clientes()
elif page == "📦 Produtos":
    produtos()
elif page == "🧑‍💼 Vendedores":
    vendedores()
elif page == "🏭 Fornecedores":
    fornecedores()
elif page == "🛒 Pedidos":
    pedidos()
elif page == "🗃️ Estoque":
    estoque()
elif page == "🔎 Consultas":
    consultas()
