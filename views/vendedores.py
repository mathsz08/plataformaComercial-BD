import pandas as pd
import streamlit as st

from db import DB, get_db


def vendedores():
    st.title("🧑‍💼 Vendedores")
    
    db = DB(get_db())

    if 'edit_vendedor' not in st.session_state:
        st.session_state.edit_vendedor = None
    if 'del_vendedor' not in st.session_state:
        st.session_state.del_vendedor = None
    
    col1, col2 = st.columns([3, 1], vertical_alignment="center")
    with col1:
        st.subheader("Novo Vendedor")
    with col2:
        if st.button("🔄 Atualizar"):
            st.rerun()
    
    with st.form("novo_vendedor"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nome = st.text_input("Nome completo *")
        with col2:
            telefone = st.text_input("Telefone")
        with col3:
            matricula = st.text_input("Matrícula *")
        
        submitted = st.form_submit_button("➕ Salvar Vendedor", use_container_width=True)
        
        if submitted:
            if not nome or not matricula:
                st.error("Nome e matrícula são obrigatórios!")
            else:
                try:
                    r = db.q("INSERT INTO Pessoa(nome,telefone) VALUES(%s,%s) RETURNING id",
                            (nome, telefone))
                    db.run("INSERT INTO Vendedor(id,matricula) VALUES(%s,%s)",
                          (r[0]["id"], matricula))
                    st.success(f"✅ Vendedor '{nome}' cadastrado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
    
    st.divider()
    
    st.subheader("Vendedores Cadastrados")
    rows = db.q("""
        SELECT v.id, p.nome, p.telefone, v.matricula
        FROM Vendedor v JOIN Pessoa p ON p.id=v.id
        ORDER BY p.nome
    """)
    
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum vendedor cadastrado")

    # ================ SEÇÃO DE EDIÇÃO ================
    if st.session_state.edit_vendedor:
        with st.expander("✏️ Editando Vendedor", expanded=True):
            vendedor_id = st.session_state.edit_vendedor
            # Buscar dados atuais
            dados = db.q("""
                SELECT p.nome, p.telefone, v.matricula 
                FROM Vendedor v JOIN Pessoa p ON p.id=v.id 
                WHERE v.id=%s
            """, (vendedor_id,))[0]
            
            with st.form("edit_vendedor_form"):
                st.info(f"Editando vendedor ID: {vendedor_id}")
                
                col1, col2 = st.columns(2)
                with col1:
                    nome_edit = st.text_input("Nome *", value=dados['nome'])
                with col2:
                    matricula_edit = st.text_input("Matrícula *", value=dados['matricula'])
                
                telefone_edit = st.text_input("Telefone", value=dados['telefone'] or '')
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                        if not nome_edit or not matricula_edit:
                            st.error("Nome e matrícula são obrigatórios!")
                        else:
                            try:
                                db.run("UPDATE Pessoa SET nome=%s, telefone=%s WHERE id=%s", 
                                      (nome_edit, telefone_edit, vendedor_id))
                                db.run("UPDATE Vendedor SET matricula=%s WHERE id=%s", 
                                      (matricula_edit, vendedor_id))
                                st.success("✅ Vendedor atualizado com sucesso!")
                                st.session_state.edit_vendedor = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar: {e}")
                with col2:
                    if st.form_submit_button("❌ Cancelar Edição", use_container_width=True):
                        st.session_state.edit_vendedor = None
                        st.rerun()
    
    # ================ SEÇÃO DE EXCLUSÃO ================
    if st.session_state.del_vendedor:
        vendedor_id = st.session_state.del_vendedor
        nome_vendedor = db.q("""
            SELECT p.nome FROM Vendedor v JOIN Pessoa p ON p.id=v.id WHERE v.id=%s
        """, (vendedor_id,))[0]['nome']
        
        st.warning(f"""
        ### ⚠️ Confirmar Exclusão
        
        Tem certeza que deseja excluir o vendedor **{nome_vendedor}**?
        
        **ATENÇÃO:** Esta ação pode ser bloqueada se o vendedor tiver pedidos vinculados.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sim, Excluir", use_container_width=True):
                try:
                    db.run("DELETE FROM Vendedor WHERE id=%s", (vendedor_id,))
                    st.success(f"✅ Vendedor '{nome_vendedor}' excluído com sucesso!")
                    st.session_state.del_vendedor = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Não foi possível excluir: {e}")
        with col2:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.del_vendedor = None
                st.rerun()
    
    # ================ TABELA DE VENDEDORES COM BOTÕES ================
    df = pd.DataFrame(rows)
    
    st.write("### Lista de Vendedores")
    
    for idx, row in df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
        
        with col1:
            st.write(f"**{row['nome']}**")
        with col2:
            st.write(row['matricula'])
        with col3:
            st.write(row['telefone'] or '—')
        with col4:
            if st.button("✏️", key=f"edit_vend_{row['id']}", help="Editar vendedor"):
                st.session_state.edit_vendedor = row['id']
                st.rerun()
        with col5:
            if st.button("🗑️", key=f"del_vend_{row['id']}", help="Excluir vendedor"):
                st.session_state.del_vendedor = row['id']
                st.rerun()
        
        st.divider()

