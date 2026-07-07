import pandas as pd
import streamlit as st

from db import DB, get_db


def fornecedores():
    st.title("🏭 Fornecedores")

    db = DB(get_db())

    if 'edit_fornecedor' not in st.session_state:
        st.session_state.edit_fornecedor = None
    if 'del_fornecedor' not in st.session_state:
        st.session_state.del_fornecedor = None

    col1, col2 = st.columns([3, 1], vertical_alignment="center")
    with col1:
        st.subheader("Novo Fornecedor")
    with col2:
        if st.button("🔄 Atualizar"):
            st.rerun()

    with st.form("novo_fornecedor"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome / Razão social *")
        with col2:
            contato = st.text_input("Contato")

        submitted = st.form_submit_button("➕ Salvar Fornecedor", use_container_width=True)

        if submitted:
            if not nome:
                st.error("Nome é obrigatório!")
            else:
                try:
                    db.run("INSERT INTO Fornecedor(nome, contato) VALUES(%s, %s)", (nome, contato))
                    st.success(f"✅ Fornecedor '{nome}' cadastrado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

    st.divider()
    st.subheader("Vincular Produtos ao Fornecedor")

    fornecedores_rows = db.q("SELECT id_fornecedor, nome FROM Fornecedor ORDER BY nome")
    produtos_rows = db.q("SELECT id_produto, nome FROM Produto ORDER BY nome")
    forn_map = {f["nome"]: f["id_fornecedor"] for f in fornecedores_rows}
    prod_map = {p["nome"]: p["id_produto"] for p in produtos_rows}

    with st.form("vincular_produtos_fornecedor"):
        col1, col2 = st.columns(2)
        with col1:
            fornecedor_sel = st.selectbox("Fornecedor *", list(forn_map.keys()) if forn_map else [""])
        with col2:
            produtos_sel = st.multiselect("Produtos fornecidos *", list(prod_map.keys()))

        if st.form_submit_button("🔗 Vincular Produtos", use_container_width=True):
            if not fornecedor_sel or not produtos_sel:
                st.error("Selecione fornecedor e pelo menos um produto.")
            else:
                try:
                    for produto_nome in produtos_sel:
                        db.run(
                            """INSERT INTO Fornece(id_fornecedor, id_produto)
                               VALUES(%s, %s)
                               ON CONFLICT(id_fornecedor, id_produto) DO NOTHING""",
                            (forn_map[fornecedor_sel], prod_map[produto_nome])
                        )
                    st.success("✅ Produtos vinculados ao fornecedor.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao vincular produtos: {e}")

    st.divider()
    st.subheader("Fornecedores Cadastrados")

    rows = db.q("""
        SELECT f.id_fornecedor, f.nome, f.contato,
               COUNT(fr.id_produto) AS produtos_fornecidos,
               COALESCE(STRING_AGG(p.nome, ', ' ORDER BY p.nome), 'Nenhum produto vinculado') AS produtos
        FROM Fornecedor f
        LEFT JOIN Fornece fr ON fr.id_fornecedor = f.id_fornecedor
        LEFT JOIN Produto p ON p.id_produto = fr.id_produto
        GROUP BY f.id_fornecedor, f.nome, f.contato
        ORDER BY f.nome
    """)

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum fornecedor cadastrado")

    if st.session_state.edit_fornecedor:
        with st.expander("✏️ Editando Fornecedor", expanded=True):
            fornecedor_id = st.session_state.edit_fornecedor
            dados = db.q("SELECT nome, contato FROM Fornecedor WHERE id_fornecedor=%s", (fornecedor_id,))[0]

            with st.form("edit_fornecedor_form"):
                col1, col2 = st.columns(2)
                with col1:
                    nome_edit = st.text_input("Nome / Razão social *", value=dados["nome"])
                with col2:
                    contato_edit = st.text_input("Contato", value=dados["contato"] or "")

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                        if not nome_edit:
                            st.error("Nome é obrigatório!")
                        else:
                            try:
                                db.run(
                                    "UPDATE Fornecedor SET nome=%s, contato=%s WHERE id_fornecedor=%s",
                                    (nome_edit, contato_edit, fornecedor_id)
                                )
                                st.success("✅ Fornecedor atualizado com sucesso!")
                                st.session_state.edit_fornecedor = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar: {e}")
                with col2:
                    if st.form_submit_button("❌ Cancelar Edição", use_container_width=True):
                        st.session_state.edit_fornecedor = None
                        st.rerun()

    if st.session_state.del_fornecedor:
        fornecedor_id = st.session_state.del_fornecedor
        nome_fornecedor = db.q("SELECT nome FROM Fornecedor WHERE id_fornecedor=%s", (fornecedor_id,))[0]["nome"]

        st.warning(f"""
        ### ⚠️ Confirmar Exclusão

        Tem certeza que deseja excluir o fornecedor **{nome_fornecedor}**?

        Os vínculos com produtos serão removidos automaticamente.
        """)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sim, Excluir", use_container_width=True):
                try:
                    db.run("DELETE FROM Fornecedor WHERE id_fornecedor=%s", (fornecedor_id,))
                    st.success(f"✅ Fornecedor '{nome_fornecedor}' excluído com sucesso!")
                    st.session_state.del_fornecedor = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Não foi possível excluir: {e}")
        with col2:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.del_fornecedor = None
                st.rerun()

    if rows:
        st.write("### Lista de Fornecedores")
        for row in rows:
            col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 1, 1])
            with col1:
                st.write(f"**{row['nome']}**")
            with col2:
                st.write(row["contato"] or "—")
            with col3:
                st.write(f"{row['produtos_fornecidos']} produto(s)")
            with col4:
                if st.button("✏️", key=f"edit_forn_{row['id_fornecedor']}", help="Editar fornecedor"):
                    st.session_state.edit_fornecedor = row["id_fornecedor"]
                    st.rerun()
            with col5:
                if st.button("🗑️", key=f"del_forn_{row['id_fornecedor']}", help="Excluir fornecedor"):
                    st.session_state.del_fornecedor = row["id_fornecedor"]
                    st.rerun()
            st.caption(row["produtos"])
            st.divider()

