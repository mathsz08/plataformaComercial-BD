import pandas as pd
import streamlit as st

from db import DB, get_db


def dashboard():
    st.title("📊 Visão Geral do Sistema")
    st.markdown("Resumo das operações comerciais")
    
    db = DB(get_db())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        n_clientes = db.q("SELECT COUNT(*) as n FROM Cliente")[0]["n"]
        st.metric("👥 Clientes", n_clientes, "registrados", delta_color="off")
    
    with col2:
        n_produtos = db.q("SELECT COUNT(*) as n FROM Produto")[0]["n"]
        st.metric("📦 Produtos", n_produtos, "no catálogo", delta_color="off")
    
    with col3:
        n_pedidos = db.q("""SELECT COUNT(*) as n FROM Pedido 
                            WHERE status NOT IN ('CANCELADO','CONCLUIDO')""")[0]["n"]
        st.metric("🛒 Pedidos Ativos", n_pedidos, "em processamento", delta_color="off")
    
    with col4:
        n_vendedores = db.q("SELECT COUNT(*) as n FROM Vendedor")[0]["n"]
        st.metric("💼 Vendedores", n_vendedores, "ativos", delta_color="off")
    
    st.divider()
    
    # Gráfico de pedidos recentes
    st.subheader("📈 Pedidos Recentes")
    rows = db.q("""
        SELECT p.id_pedido, p.data, p.status, pc.nome, COUNT(ip.id_item) as itens
        FROM Pedido p
        JOIN Cliente c ON c.id=p.id_cliente
        JOIN Pessoa pc ON pc.id=c.id
        LEFT JOIN Item_Pedido ip ON ip.id_pedido=p.id_pedido
        GROUP BY p.id_pedido, p.data, p.status, pc.nome
        ORDER BY p.id_pedido DESC LIMIT 10
    """)
    
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum pedido registrado ainda")
    
    # Produtos mais cadastrados
    st.subheader("🏆 Produtos em Catálogo")
    prods = db.q("""
        SELECT nome, preco, 
               (SELECT COUNT(*) FROM Estoque_Produto WHERE id_produto=Produto.id_produto) as em_estoque
        FROM Produto
        LIMIT 10
    """)
    
    if prods:
        df_prods = pd.DataFrame(prods)
        st.dataframe(df_prods, use_container_width=True, hide_index=True)

