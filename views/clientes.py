import pandas as pd
import streamlit as st

from db import DB, get_db


def clientes():
    st.title("👤 Clientes")
    
    db = DB(get_db())

    if 'edit_cliente' not in st.session_state:
        st.session_state.edit_cliente = None
    if 'del_cliente' not in st.session_state:
        st.session_state.del_cliente = None
    
    col1, col2 = st.columns([3, 1], vertical_alignment="center")
    
    with col1:
        st.subheader("Novo Cliente")
    with col2:
        if st.button("🔄 Atualizar"):
            st.rerun()
    
    # Form
    with st.form("novo_cliente"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nome = st.text_input("Nome completo *")
        with col2:
            telefone = st.text_input("Telefone")
        with col3:
            email = st.text_input("Email")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cpf_cnpj = st.text_input("CPF / CNPJ *")
        with col2:
            tipo = st.selectbox("Tipo *", ["PESSOA_FISICA", "PESSOA_JURIDICA"])
        
        submitted = st.form_submit_button("➕ Salvar Cliente", use_container_width=True)
        
        if submitted:
            if not nome or not cpf_cnpj:
                st.error("Nome e CPF/CNPJ são obrigatórios!")
            else:
                try:
                    rows = db.q("INSERT INTO Pessoa(nome,telefone,email) VALUES(%s,%s,%s) RETURNING id",
                               (nome, telefone, email))
                    db.run("INSERT INTO Cliente(id,cpf_cnpj,tipo) VALUES(%s,%s,%s)",
                          (rows[0]["id"], cpf_cnpj, tipo))
                    st.success(f"✅ Cliente '{nome}' cadastrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
    
    st.divider()
    
    # Lista de clientes
    st.subheader("Clientes Cadastrados")
    rows = db.q("""
        SELECT p.id, p.nome, p.telefone, p.email, c.cpf_cnpj, c.tipo
        FROM Cliente c JOIN Pessoa p ON p.id=c.id
        ORDER BY p.nome
    """)
    
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum cliente cadastrado ainda")

     # ================ SEÇÃO DE EDIÇÃO ================
    if st.session_state.edit_cliente:
        with st.expander("✏️ Editando Cliente", expanded=True):
            cliente_id = st.session_state.edit_cliente
            # Buscar dados atuais
            dados = db.q("""
                SELECT p.nome, p.telefone, p.email, c.cpf_cnpj, c.tipo 
                FROM Cliente c JOIN Pessoa p ON p.id=c.id 
                WHERE c.id=%s
            """, (cliente_id,))[0]
            
            with st.form("edit_cliente_form"):
                st.info(f"Editando cliente ID: {cliente_id}")
                
                col1, col2 = st.columns(2)
                with col1:
                    nome_edit = st.text_input("Nome *", value=dados['nome'])
                with col2:
                    cpf_edit = st.text_input("CPF/CNPJ *", value=dados['cpf_cnpj'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    telefone_edit = st.text_input("Telefone", value=dados['telefone'] or '')
                with col2:
                    email_edit = st.text_input("Email", value=dados['email'] or '')
                with col3:
                    tipo_edit = st.selectbox(
                        "Tipo *", 
                        ["PESSOA_FISICA", "PESSOA_JURIDICA"],
                        index=0 if dados['tipo'] == 'PESSOA_FISICA' else 1
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                        if not nome_edit or not cpf_edit:
                            st.error("Nome e CPF/CNPJ são obrigatórios!")
                        else:
                            try:
                                db.run("UPDATE Pessoa SET nome=%s, telefone=%s, email=%s WHERE id=%s", 
                                      (nome_edit, telefone_edit, email_edit, cliente_id))
                                db.run("UPDATE Cliente SET cpf_cnpj=%s, tipo=%s WHERE id=%s", 
                                      (cpf_edit, tipo_edit, cliente_id))
                                st.success("✅ Cliente atualizado com sucesso!")
                                st.session_state.edit_cliente = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar: {e}")
                with col2:
                    if st.form_submit_button("❌ Cancelar Edição", use_container_width=True):
                        st.session_state.edit_cliente = None
                        st.rerun()
    
    # ================ SEÇÃO DE EXCLUSÃO ================
    if st.session_state.del_cliente:
        cliente_id = st.session_state.del_cliente
        nome_cliente = db.q("""
            SELECT p.nome FROM Cliente c JOIN Pessoa p ON p.id=c.id WHERE c.id=%s
        """, (cliente_id,))[0]['nome']
        
        st.warning(f"""
        ### ⚠️ Confirmar Exclusão
        
        Tem certeza que deseja excluir o cliente **{nome_cliente}**?
        
        **ATENÇÃO:** Esta ação pode ser bloqueada se o cliente tiver pedidos vinculados.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sim, Excluir", use_container_width=True):
                try:
                    db.run("DELETE FROM Cliente WHERE id=%s", (cliente_id,))
                    st.success(f"✅ Cliente '{nome_cliente}' excluído com sucesso!")
                    st.session_state.del_cliente = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Não foi possível excluir: {e}")
        with col2:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.del_cliente = None
                st.rerun()
    
    # ================ TABELA DE CLIENTES COM BOTÕES ================
    # Converter para DataFrame
    df = pd.DataFrame(rows)
    
    # Exibir tabela com botões usando colunas
    st.write("### Lista de Clientes")
    
    for idx, row in df.iterrows():
        col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 1, 1])
        
        with col1:
            st.write(f"**{row['nome']}**")
        with col2:
            st.write(row['cpf_cnpj'])
        with col3:
            st.write(row['telefone'] or '—')
        with col4:
            st.write(row['email'] or '—')
        with col5:
            if st.button("✏️", key=f"edit_{row['id']}", help="Editar cliente"):
                st.session_state.edit_cliente = row['id']
                st.rerun()
        with col6:
            if st.button("🗑️", key=f"del_{row['id']}", help="Excluir cliente"):
                st.session_state.del_cliente = row['id']
                st.rerun()
        
        st.divider()

