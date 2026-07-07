import pandas as pd
import streamlit as st

from db import DB, get_db


def produtos():
    st.title("📦 Produtos")
    
    db = DB(get_db())

    if 'edit_produto' not in st.session_state:
        st.session_state.edit_produto = None
    if 'del_produto' not in st.session_state:
        st.session_state.del_produto = None
    
    col1, col2 = st.columns([3, 1], vertical_alignment="center")
    with col1:
        st.subheader("Novo Produto")
    with col2:
        if st.button("🔄 Atualizar"):
            st.rerun()
    
    # Categorias
    cats = db.q("SELECT id_categoria, nome FROM Categoria_Produto ORDER BY nome")
    cat_map = {c["nome"]: c["id_categoria"] for c in cats}
    
    with st.form("novo_produto"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nome = st.text_input("Nome do produto *")
        with col2:
            preco = st.number_input("Preço (R$) *", min_value=0.01, step=0.01)
        with col3:
            categoria = st.selectbox("Categoria *", list(cat_map.keys()) if cat_map else [""])
        
        descricao = st.text_area("Descrição", height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            nova_cat = st.text_input("Criar nova categoria")
        with col2:
            if st.form_submit_button("➕ Adicionar Categoria"):
                if nova_cat:
                    try:
                        db.run("INSERT INTO Categoria_Produto(nome) VALUES(%s)", (nova_cat,))
                        st.success("Categoria criada!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
        
        submitted = st.form_submit_button("➕ Salvar Produto", use_container_width=True)
        
        if submitted:
            if not nome or not categoria:
                st.error("Nome e categoria são obrigatórios!")
            else:
                try:
                    db.run("INSERT INTO Produto(nome,descricao,preco,id_categoria) VALUES(%s,%s,%s,%s)",
                          (nome, descricao, preco, cat_map[categoria]))
                    st.success(f"✅ Produto '{nome}' cadastrado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
    
    st.divider()
    
    st.subheader("Produtos em Catálogo")
    rows = db.q("""
        SELECT p.id_produto, p.nome, p.preco, cp.nome AS categoria, p.descricao
        FROM Produto p JOIN Categoria_Produto cp ON cp.id_categoria=p.id_categoria
        ORDER BY p.nome
    """)
    
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum produto cadastrado")

    # ================ SEÇÃO DE EDIÇÃO ================
    if st.session_state.edit_produto:
        with st.expander("✏️ Editando Produto", expanded=True):
            produto_id = st.session_state.edit_produto
            # Buscar dados atuais
            dados = db.q("""
                SELECT p.id_produto, p.nome, p.descricao, p.preco, p.id_categoria, cp.nome AS categoria_nome
                FROM Produto p 
                JOIN Categoria_Produto cp ON cp.id_categoria = p.id_categoria
                WHERE p.id_produto=%s
            """, (produto_id,))[0]
            
            # Recarregar categorias para o selectbox
            cats_edit = db.q("SELECT id_categoria, nome FROM Categoria_Produto ORDER BY nome")
            cat_edit_map = {c["nome"]: c["id_categoria"] for c in cats_edit}
            
            with st.form("edit_produto_form"):
                st.info(f"Editando produto ID: {produto_id}")
                
                col1, col2 = st.columns(2)
                with col1:
                    nome_edit = st.text_input("Nome *", value=dados['nome'])
                with col2:
                    preco_edit = st.number_input("Preço (R$) *", min_value=0.01, step=0.01, value=float(dados['preco']))
                
                col1, col2 = st.columns(2)
                with col1:
                    categoria_edit = st.selectbox(
                        "Categoria *", 
                        list(cat_edit_map.keys()),
                        index=list(cat_edit_map.keys()).index(dados['categoria_nome']) if dados['categoria_nome'] in cat_edit_map else 0
                    )
                with col2:
                    # Campo para criar nova categoria durante a edição
                    nova_cat_edit = st.text_input("Ou crie uma nova categoria")
                    if nova_cat_edit and st.form_submit_button("➕ Adicionar Categoria (edição)"):
                        try:
                            db.run("INSERT INTO Categoria_Produto(nome) VALUES(%s)", (nova_cat_edit,))
                            st.success("Categoria criada! Recarregue a página.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
                
                descricao_edit = st.text_area("Descrição", value=dados['descricao'] or '', height=100)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                        if not nome_edit or not preco_edit:
                            st.error("Nome e preço são obrigatórios!")
                        else:
                            try:
                                # Atualizar dados do produto
                                db.run("""
                                    UPDATE Produto 
                                    SET nome=%s, descricao=%s, preco=%s, id_categoria=%s 
                                    WHERE id_produto=%s
                                """, (nome_edit, descricao_edit, preco_edit, cat_edit_map[categoria_edit], produto_id))
                                st.success("✅ Produto atualizado com sucesso!")
                                st.session_state.edit_produto = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar: {e}")
                with col2:
                    if st.form_submit_button("❌ Cancelar Edição", use_container_width=True):
                        st.session_state.edit_produto = None
                        st.rerun()
    
    # ================ SEÇÃO DE EXCLUSÃO ================
    if st.session_state.del_produto:
        produto_id = st.session_state.del_produto
        nome_produto = db.q("SELECT nome FROM Produto WHERE id_produto=%s", (produto_id,))[0]['nome']
        
        st.warning(f"""
        ### ⚠️ Confirmar Exclusão
        
        Tem certeza que deseja excluir o produto **{nome_produto}**?
        
        **ATENÇÃO:** Esta ação pode ser bloqueada se o produto estiver vinculado a:
        - Pedidos (itens de pedido)
        - Estoque
        - Fornecedores
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sim, Excluir", use_container_width=True):
                try:
                    db.run("DELETE FROM Produto WHERE id_produto=%s", (produto_id,))
                    st.success(f"✅ Produto '{nome_produto}' excluído com sucesso!")
                    st.session_state.del_produto = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Não foi possível excluir: {e}")
        with col2:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.del_produto = None
                st.rerun()
    
    # ================ TABELA DE PRODUTOS COM BOTÕES ================
    if rows:
        df = pd.DataFrame(rows)
        df['preco'] = df['preco'].apply(lambda x: f"R$ {x:,.2f}")
        
        st.write("### Lista de Produtos")
        
        for idx, row in df.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 1, 1])
            
            with col1:
                st.write(f"**{row['nome']}**")
            with col2:
                st.write(row['categoria'])
            with col3:
                st.write(row['preco'])
            with col4:
                st.write(row['descricao'][:50] + '...' if len(str(row['descricao'])) > 50 else row['descricao'])
            with col5:
                if st.button("✏️", key=f"edit_prod_{row['id_produto']}", help="Editar produto"):
                    st.session_state.edit_produto = row['id_produto']
                    st.rerun()
            with col6:
                if st.button("🗑️", key=f"del_prod_{row['id_produto']}", help="Excluir produto"):
                    st.session_state.del_produto = row['id_produto']
                    st.rerun()
            
            st.divider()

