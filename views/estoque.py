import pandas as pd
import streamlit as st

from db import DB, get_db


def estoque():
    st.title("🗃️ Estoque")
    
    db = DB(get_db())
    
    col1, col2 = st.columns([3, 1], vertical_alignment="center")
    with col1:
        st.subheader("Gerenciar Estoque")
    with col2:
        if st.button("🔄 Atualizar"):
            st.rerun()
    
    estoques = db.q("SELECT id_estoque, descricao FROM Estoque ORDER BY id_estoque")
    est_map = {e["descricao"]: e["id_estoque"] for e in estoques}
    
    produtos = db.q("SELECT id_produto, nome FROM Produto ORDER BY nome")
    prod_map = {p["nome"]: p["id_produto"] for p in produtos}
    
    with st.form("adicionar_estoque"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            estoque_sel = st.selectbox("Estoque *", list(est_map.keys()) if est_map else [""])
        with col2:
            produto_sel = st.selectbox("Produto *", list(prod_map.keys()) if prod_map else [""])
        with col3:
            quantidade = st.number_input("Quantidade *", min_value=1, step=1)
        
        submitted = st.form_submit_button("➕ Adicionar ao Estoque", use_container_width=True)
        
        if submitted:
            if not estoque_sel or not produto_sel:
                st.error("Selecione estoque e produto!")
            else:
                try:
                    db.run("""INSERT INTO Estoque_Produto(id_estoque,id_produto,quantidade)
                             VALUES(%s,%s,%s)
                             ON CONFLICT(id_estoque,id_produto)
                             DO UPDATE SET quantidade=Estoque_Produto.quantidade+EXCLUDED.quantidade""",
                          (est_map[estoque_sel], prod_map[produto_sel], quantidade))
                    st.success(f"✅ {quantidade} un. de {produto_sel} adicionadas!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
    
    st.divider()
    
    st.subheader("Situação do Estoque")
    rows = db.q("""
        SELECT e.descricao AS estoque, p.nome AS produto, ep.quantidade, p.preco,
               (ep.quantidade * p.preco) as valor_total
        FROM Estoque_Produto ep
        JOIN Estoque e ON e.id_estoque=ep.id_estoque
        JOIN Produto p ON p.id_produto=ep.id_produto
        ORDER BY e.descricao, p.nome
    """)
    
    if rows:
        df = pd.DataFrame(rows)
        df["valor_total"] = df["valor_total"].apply(lambda x: f"R$ {x:,.2f}")
        df["preco"] = df["preco"].apply(lambda x: f"R$ {x:,.2f}")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Resumo
        total_items = sum([r["quantidade"] for r in rows])
        st.metric("📦 Total de itens em estoque", total_items)
    else:
        st.info("Estoque vazio")

